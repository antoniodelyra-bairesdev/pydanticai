import asyncio
from contextlib import asynccontextmanager
from decimal import Decimal
from io import BytesIO
import logging
from pathlib import Path
from re import sub
from shutil import rmtree
import traceback
from typing import Any, Callable, Coroutine, TypeVar
import config.database as db

from dataclasses import dataclass
from datetime import date, datetime
from uuid import uuid4
import playwright
import playwright.driver
from sqlalchemy.ext.asyncio import AsyncSession
from playwright.async_api import Page, async_playwright


from modules.arquivos.repository import ArquivosDatabaseRepository
from modules.auth.model import Usuario
from modules.queue.service import QueueService
from modules.websockets.service import WebSocketService

from .repository import CobrancaRepository
from .schema import CNAB400Remessa, CriacaoDadosExecucaoDaycovalSchema, BodyCriacaoDadosExecucaoDaycovalSchema, DadosExecucaoDaycovalSchema, ExecucaoDaycovalSchema, PassoExecucaoDaycovalSchema, TipoExecucaoDaycovalSchema, TipoMultaDaycovalEnum


class CobrancaServiceFactory:
    @staticmethod
    def criarService(db: AsyncSession):
        return CobrancaService(cobranca_repository=CobrancaRepository(db))

T = TypeVar('T')

@dataclass
class CobrancaService:
    cobranca_repository: CobrancaRepository

    @staticmethod
    async def notificar_execucao_daycoval(execucao: ExecucaoDaycovalSchema):
        await WebSocketService.send_json({
            "canal": 'locacoes.boletos',
            "tipo": 'execucoes_daycoval.atualizacao',
            "dados": execucao.model_dump(mode='json')
        })

    @staticmethod
    async def notificar_passo_execucao_daycoval(passo: PassoExecucaoDaycovalSchema):
        await WebSocketService.send_json({
            "canal": 'locacoes.boletos',
            "tipo": 'execucoes_daycoval.passos.atualizacao',
            "dados": passo.model_dump(mode='json')
        })

    @staticmethod
    async def notificar_dados_execucao_daycoval(dados: list[DadosExecucaoDaycovalSchema]):
        await WebSocketService.send_json({
            "canal": 'locacoes.boletos',
            "tipo": 'execucoes_daycoval.dados.atualizacao',
            "dados": [dado.model_dump(mode='json') for dado in dados]
        })

    @staticmethod
    def tentativa_acesso_execucao_daycoval(
        dados: list[BodyCriacaoDadosExecucaoDaycovalSchema] | int,
        tipo_execucao_id: int,
        solicitante: Usuario
    ):
        async def executar(
            dados: list[BodyCriacaoDadosExecucaoDaycovalSchema] | int,
            tipo_execucao_id: int,
            solicitante: Usuario
        ):
            async with db.get_session(db.engine) as session, session.begin():
                svc = CobrancaServiceFactory.criarService(session)
                execucoes = await svc.execucoes_daycoval()
                if any([execucao.fim == None for execucao in execucoes]):
                    return await WebSocketService.notify(
                        [solicitante.id],
                        text=f"Já existe uma execução em andamento.",
                        level="ERROR",
                    )
            CobrancaService.execucao_daycoval(
                dados, tipo_execucao_id, solicitante
            )
        qs = QueueService()
        qs.enqueue(executar(dados, tipo_execucao_id, solicitante), 'recursos.acesso')

    @staticmethod
    def execucao_daycoval(
        dados: list[BodyCriacaoDadosExecucaoDaycovalSchema] | int,
        tipo_execucao_id: int,
        solicitante: Usuario
    ):
        async def executar():
            execucao: ExecucaoDaycovalSchema | None = None
            erro: str | None = None
            try:
                async with db.get_session(db.engine) as session:
                    svc = CobrancaServiceFactory.criarService(session)
                    execucao = await svc.criar_execucao_daycoval(dados, tipo_execucao_id, solicitante)
            except Exception as exc:
                erro = f'Falha na execução: {exc}'
            finally:
                if execucao:
                    CobrancaService.liberacao_acesso_execucao_daycoval(execucao, erro)
        qs = QueueService()
        qs.enqueue(executar(), 'execucoes.daycoval')
    
    @staticmethod
    def liberacao_acesso_execucao_daycoval(execucao: ExecucaoDaycovalSchema, erro: str | None = None):
        async def executar(execucao: ExecucaoDaycovalSchema, erro: str | None = None):
            async with db.get_session(db.engine) as session, session.begin():
                svc = CobrancaServiceFactory.criarService(session)
                if execucao.fim != None:
                    return
                fim = datetime.now()
                await svc.cobranca_repository.finalizar_execucoes_daycoval([execucao.id], fim, erro)
                execucao.fim = fim
                await CobrancaService.notificar_execucao_daycoval(execucao)
        qs = QueueService()
        qs.enqueue(executar(execucao, erro), 'recursos.acesso')

    async def inquilinos_fundo(self, fundo_id: int):
        return await self.cobranca_repository.inquilinos_fundo(fundo_id)

    async def dados_execucao(self, ids_boletos: list[int] | None = None):
        return await self.cobranca_repository.boletos(ids_boletos)
    
    async def execucoes_daycoval(self, ids_execucoes: list[int] | None = None):
        return await self.cobranca_repository.execucoes_daycoval(ids_execucoes)
    
    def wrapper_passo(self, execucao: ExecucaoDaycovalSchema, nome_passo: str):
        def decorator(callback: Callable[..., Coroutine[Any, Any, T]]):
            async def wrapper(*args, **kwargs):
                passos = { passo.nome: passo for passo in execucao.passos }
                passo: PassoExecucaoDaycovalSchema
                if nome_passo not in passos:
                    passo = await self.cobranca_repository.criar_passo_execucao_daycoval(
                        execucao.id, nome_passo
                    )
                else:
                    passo = passos[nome_passo]
                    agora = datetime.now()
                    passo.inicio = agora
                    passo.fim = None
                    passo.erro = None
                    await self.cobranca_repository.reiniciar_passo_execucao_daycoval(passo.id, agora)
                await self.cobranca_repository.db.commit()
                await CobrancaService.notificar_passo_execucao_daycoval(passo)
                erro: str | None = None
                try:
                    return await callback(*args, **kwargs)
                except Exception as exc:
                    erro = f'Falha na execução: {exc}'
                    raise exc
                finally:
                    fim = datetime.now()
                    passo.fim = fim
                    passo.erro = erro
                    await CobrancaService.notificar_passo_execucao_daycoval(passo)
                    await self.cobranca_repository.finalizar_passos_execucao_daycoval([passo.id], fim, erro)
                    await self.cobranca_repository.db.commit()
                    execucao.passos.append(passo)
            return wrapper
        return decorator
    
    def wrapper_execucao(
        self,
        callback: Callable[
            [ExecucaoDaycovalSchema, dict[int, DadosExecucaoDaycovalSchema]],
            Coroutine[Any, Any, T]
        ]
    ):
        """
        Recebe uma função que recebe como parâmetros os detalhes de uma execução do Daycoval
        e um dicionário relacionando o ID do contrato com os dados da execução.

        Retorna uma função que recebe os dados para criação de uma nova execução ou o ID de
        uma execução existente. Esses dados serão transformados para alimentar a callback
        fornecida.
        """

        async def wrapper(
            dados: list[BodyCriacaoDadosExecucaoDaycovalSchema] | int,
            tipo_execucao_id: int,
            usuario: Usuario
        ):
            tipo_execucao = await self.cobranca_repository.buscar_tipo_execucao(tipo_execucao_id)
            criacao_dados_execucao: list[CriacaoDadosExecucaoDaycovalSchema] = []
            
            execucao: ExecucaoDaycovalSchema
            mapa_id_contrato_dados_execucao: dict[int, DadosExecucaoDaycovalSchema]
            if type(dados) == int:
                execucoes = await self.cobranca_repository.execucoes_daycoval([dados])
                if len(execucoes) == 0:
                    raise Exception('Execução não encontrada.')
                [exec] = execucoes
                execucao = ExecucaoDaycovalSchema.from_model(exec)
                agora = datetime.now()
                execucao.inicio = agora
                execucao.fim = None
                execucao.erro = None
                execucao.passos = []
                await self.cobranca_repository.reiniciar_execucao_daycoval(execucao.id)
                await self.cobranca_repository.db.commit()
                mapa_id_contrato_dados_execucao = {
                    dado.contrato_id: dado
                    for dado in execucao.dados
                }
            elif type(dados) == list:
                criacao_dados_execucao = [
                    CriacaoDadosExecucaoDaycovalSchema(
                        identificador_documento_cobranca=uuid4().hex[:10],
                        identificador_titulo=uuid4().hex[:25],
                        contrato_id=dado.contrato_id,
                        percentual_juros_mora_ao_mes=dado.percentual_juros_mora_ao_mes,
                        percentual_sobre_valor_multa_mora=dado.percentual_sobre_valor_multa_mora,
                        valor=dado.valor,
                        vencimento=dado.vencimento
                    )
                    for dado in dados
                ]
                agora = datetime.now()
                resultados = await self.cobranca_repository.criar_execucao_daycoval(
                    criacao_dados_execucao, tipo_execucao_id, usuario.id, agora
                )
                await self.cobranca_repository.db.commit()
                mapa_id_contrato_dados_execucao = {
                    criacao_dados_execucao[i].contrato_id: DadosExecucaoDaycovalSchema(
                        id=id_dado,
                        execucao_daycoval_id=resultados.id_execucao,
                        identificador_titulo=criacao_dados_execucao[i].identificador_titulo,
                        identificador_documento_cobranca=criacao_dados_execucao[i].identificador_documento_cobranca,
                        vencimento=criacao_dados_execucao[i].vencimento,
                        valor=criacao_dados_execucao[i].valor,
                        percentual_juros_mora_ao_mes=criacao_dados_execucao[i].percentual_juros_mora_ao_mes,
                        percentual_sobre_valor_multa_mora=criacao_dados_execucao[i].percentual_sobre_valor_multa_mora,
                        contrato_id=criacao_dados_execucao[i].contrato_id,
                    )
                    for i, id_dado in enumerate(resultados.ids_dados_execucao)
                }
                execucao = ExecucaoDaycovalSchema(
                    id=resultados.id_execucao,
                    tipo_execucao=TipoExecucaoDaycovalSchema(
                        id=tipo_execucao.id,
                        nome=tipo_execucao.nome
                    ),
                    inicio=agora,
                    passos=[],
                    dados=[*mapa_id_contrato_dados_execucao.values()],
                    usuario=ExecucaoDaycovalSchema.Usuario(
                        id=usuario.id,
                        nome=usuario.nome,
                        email=usuario.email
                    ),
                )
            else:
                raise TypeError('Dados de execução devem ser só o ID da execução existente ou os dados para nova execução')

            await CobrancaService.notificar_execucao_daycoval(execucao)
            erro: str | None = None
            try:
                return await callback(execucao, mapa_id_contrato_dados_execucao)
            except Exception as exc:
                erro = f'Falha na execução: {exc}'
                raise exc
            finally:
                fim = datetime.now()
                execucao.fim = fim
                execucao.erro = erro
                await CobrancaService.notificar_execucao_daycoval(execucao)
                await self.cobranca_repository.finalizar_execucoes_daycoval([execucao.id], fim, erro)
                await self.cobranca_repository.db.commit()
        return wrapper
    
    @dataclass
    class CtxNavegador:
        exec_id: str
        download_dir: str
        page: Page

    @asynccontextmanager
    async def pagina(self):
        exec_id = uuid4().hex
        download_dir = f"/home/host_user/app/files/temp/downloads/{exec_id}"
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, downloads_path=download_dir)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
                )
                page = await context.new_page()
                await page.emulate_media(media='screen')
                yield self.CtxNavegador(
                    exec_id=exec_id,
                    download_dir=download_dir,
                    page=page
                )
        finally:
            rmtree(download_dir, ignore_errors=True)
    
    async def acesso_site_daycoval(self, execucao: ExecucaoDaycovalSchema, ctx: CtxNavegador):
        page = ctx.page
        download_dir = ctx.download_dir

        @self.wrapper_passo(execucao, 'locacoes.boletos.arquivos.webdriver.credenciais.id')
        async def inserir_id():
            await page.goto("https://ecode.daycoval.com.br")
            await page.locator('#tabSuaEmpresa').click()
            await page.locator('#ctl00_cphLogin_txtCodigoUsuario').fill("00881738303")
            await page.locator('#ctl00_cphLogin_btnPesquisaCodigoUsuarioPessoaJuridica').click()
        await inserir_id()

        @self.wrapper_passo(execucao, 'locacoes.boletos.arquivos.webdriver.credenciais.leitura')
        async def leitura():
            from easyocr import Reader
            reader = Reader(
                ["pt"],
                gpu=False,
                download_enabled=False,
                model_storage_directory="/home/host_user/app/files/models",
                user_network_directory="/home/host_user/app/files/models"
            )
            for i in range(1, 6):
                tecla = page.locator(f'#ctl00_cphLogin_btnTecla{i}')
                b64 = await tecla.get_attribute("src")
                async with page.expect_download() as download_info:
                    await page.evaluate(
                        f"""
                        console.log('Início captura de tecla {i}');
                        const link{i} = document.createElement('a');
                        link{i}.href = '{b64}';
                        link{i}.target = '_blank';
                        link{i}.rel = 'noopener noreferrer';
                        link{i}.download = 'tecla_{i}.png';
                        link{i}.click();
                        console.log('Fim captura de tecla {i}');
                        """
                    )
                download = await download_info.value
                await download.save_as(f"{download_dir}/tecla_{i}.png")
            numero_para_tecla: dict[int, int] = {}
            for i in range(1, 6):
                _txt: Any = reader.readtext(f"{download_dir}/tecla_{i}.png", detail=0)
                txt: list[str] = _txt
                algarismos = [int(c) for c in sub("[^0-9]", "", "".join(txt))]
                for algarismo in algarismos:
                    numero_para_tecla[algarismo] = i
            return numero_para_tecla
        numero_para_tecla = await leitura()

        @self.wrapper_passo(execucao, 'locacoes.boletos.arquivos.webdriver.credenciais.envio')
        async def login(numero_para_tecla: dict[int, int]):
            for c in "29042003":
                algarismo = int(c)
                tecla = page.locator(f'#ctl00_cphLogin_btnTecla{numero_para_tecla[algarismo]}')
                logging.info(f"Tecla {algarismo}")
                await tecla.click()
                await page.wait_for_timeout(1000)
            await page.locator('#ctl00_cphLogin_btnAcessoConta').click()
        await login(numero_para_tecla)
    
    async def execucao_criacao_cobranca(self, execucao: ExecucaoDaycovalSchema, mapa_id_contrato_dados_execucao: dict[int, DadosExecucaoDaycovalSchema]):
        @self.wrapper_passo(execucao, 'locacoes.boletos.arquivos.remessa.validacao')
        async def validacao():
            contratos = {
                c.id: c
                for c in await self.cobranca_repository.contratos([dado.contrato_id for dado in execucao.dados])
            }
            if not contratos or len(execucao.dados) != len(contratos):
                raise Exception('Alguns IDs de contratos informados não existem.')
            return contratos
        
        mapa_id_contratos = await validacao()

        @self.wrapper_passo(execucao, 'locacoes.boletos.arquivos.remessa.criacao')
        async def criacao_remessa():
            mapa_dado_execucao_id_conteudo_remessa: dict[int, str] = {}
            for dado_execucao in mapa_id_contrato_dados_execucao.values():
                contrato = mapa_id_contratos[dado_execucao.contrato_id]
                juros_1_dia = (
                    dado_execucao.percentual_sobre_valor_multa_mora / 100 * dado_execucao.valor
                ) / 30
                conteudo_remessa = (
                    dado_execucao.conteudo_arquivo_remessa if dado_execucao.conteudo_arquivo_remessa else
                    CNAB400Remessa(
                        bairro_empresa_cobrada=contrato.inquilino.bairro,
                        cep_empresa_cobrada=contrato.inquilino.cep,
                        cidade_empresa_cobrada=contrato.inquilino.cidade,
                        cnpj_empresa_cobrada=contrato.inquilino.cnpj,
                        data_emissao=date.today(),
                        dias_apos_vencimento_para_aplicar_multa=1,
                        logradouro_empresa_cobrada=contrato.inquilino.logradouro,
                        nome_empresa_cobrada=contrato.inquilino.razao_social,
                        tipo_multa=TipoMultaDaycovalEnum.PERCENTUAL,
                        uf_empresa_cobrada=contrato.inquilino.estado,
                        valor=Decimal(dado_execucao.valor),
                        valor_mora_por_dia_de_atraso=Decimal(juros_1_dia),
                        valor_ou_taxa_multa=Decimal(dado_execucao.percentual_sobre_valor_multa_mora),
                        vencimento=dado_execucao.vencimento,
                    ).gerar(
                        dado_execucao.identificador_titulo,
                        dado_execucao.identificador_documento_cobranca,
                    )
                )
                mapa_dado_execucao_id_conteudo_remessa[dado_execucao.id] = conteudo_remessa
                dado_execucao.conteudo_arquivo_remessa = conteudo_remessa
            return mapa_dado_execucao_id_conteudo_remessa
        
        mapa_dado_execucao_id_conteudo_remessa = await criacao_remessa()
        
        @self.wrapper_passo(execucao, 'locacoes.boletos.arquivos.remessa.armazenamento')
        async def armazenamento_remessa():
            await self.cobranca_repository.salvar_informacoes_remessa(mapa_dado_execucao_id_conteudo_remessa)
            await self.cobranca_repository.db.commit()
            for dado in execucao.dados:
                remessa = mapa_dado_execucao_id_conteudo_remessa[dado.id]
                dado.conteudo_arquivo_remessa = remessa
            await CobrancaService.notificar_dados_execucao_daycoval([*mapa_id_contrato_dados_execucao.values()])
        await armazenamento_remessa()

        this = self
        @this.wrapper_passo(execucao, 'locacoes.boletos.arquivos.webdriver.boleto.armazenamento')
        async def envio_arquivos_remessa_daycoval():
            async with this.pagina() as ctx:
                await this.acesso_site_daycoval(execucao, ctx)
                @this.wrapper_passo(execucao, 'locacoes.boletos.arquivos.webdriver.remessa.upload')
                async def upload():
                    await ctx.page.locator('#ctl00_ucBarraMenu_MenuRepeater_ctl05_divMenuNaoClicavel').click()
                    await ctx.page.locator('#ctl00_ucBarraMenu_MenuRepeater_ctl05_SubMenuRepeaterColuna1_ctl00_ItensSubMenuRepeaterColuna1_ctl14_lnkButtonIrPaginaSelecionada1').click()
                    for dado in execucao.dados:
                        if dado.nome_arquivo_remessa:
                            continue
                        nome_arquivo = f"YVG{date.today().strftime('%d%m')}{dado.id}.txt"
                        remessa = mapa_dado_execucao_id_conteudo_remessa[dado.id]
                        await ctx.page.locator('#ctl00_cphPrincipal_fuUpload').set_input_files(
                            files=[{
                                "name": nome_arquivo,
                                "mimeType": "text/plain",
                                "buffer": remessa.encode()
                            }]
                        )
                        await ctx.page.locator('#ctl00_cphPrincipal_btnEnviar').click()
                        resultado = await ctx.page.locator('#ctl00_cphPrincipal_lblMensagemUpload').text_content()
                        if resultado != f'O arquivo "{nome_arquivo}" foi enviado com sucesso!':
                            raise Exception('Falha no envio do arquivo.')
                        await self.cobranca_repository.salvar_nome_arquivo_remessa(dado.id, nome_arquivo)
                        await self.cobranca_repository.db.commit()
                await upload()
        
        tentativas_restantes = 3
        while tentativas_restantes > 0:
            try:
                await envio_arquivos_remessa_daycoval()
                break
            except Exception as exc:
                logging.info(f"{'='*80}")
                logging.info(f"Falha ao inserir informações no site do Daycoval.")
                logging.info(f"\t{exc}")
                logging.info(f"{'='*80}")
            tentativas_restantes = tentativas_restantes - 1
            if tentativas_restantes == 0:
                raise Exception("Número de tentativas excedido ao tentar acessar o site do Daycoval")

        @self.wrapper_passo(execucao, 'locacoes.boletos.arquivos.parcial.criacao')
        async def criacao_boletos_parciais():
            async with this.pagina() as ctx:
                for dado in execucao.dados:
                    contrato = mapa_id_contratos[dado.contrato_id]
                    inquilino = contrato.inquilino
                    hoje = date.today()
                    vencimento = dado.vencimento
                    qparams = [
                        f"vencimento={vencimento.strftime('%d/%m/%Y')}",
                        f"data_documento={hoje.strftime('%d/%m/%Y')}",
                        f"numero_documento={dado.identificador_documento_cobranca}",
                        f"valor_documento={dado.valor}",
                        f"instrucoes={dado.html_cobranca()}",
                        f"pagador={inquilino.razao_social}<br>{inquilino.logradouro}<br>{inquilino.bairro} - {inquilino.cidade}/{inquilino.estado} - CEP: {inquilino.cep}",
                        f"cnpj_pagador={inquilino.cnpj}"
                    ]
                    await ctx.page.goto(f'file:///home/host_user/app/modules/cobranca/views/boleto/view.html?{"&".join(qparams)}')
                    buf = await ctx.page.pdf(
                        display_header_footer=False,
                        width='1077px',
                        height='762px',
                        margin={
                            'top': '0px',
                            'bottom': '0px',
                            'left': '0px',
                            'right': '0px'
                        },
                        print_background=True
                    )
                    arq_svc = ArquivosDatabaseRepository(self.cobranca_repository.db)
                    id_arq = await arq_svc.criar(BytesIO(buf), "boleto.pdf", "application/pdf")
                    dado.arquivo_id_boleto_parcial_pdf = id_arq
                    await self.cobranca_repository.salvar_informacoes_boleto_parcial(dado.id, dado.arquivo_id_boleto_parcial_pdf)
                    await self.cobranca_repository.db.commit()
                    await CobrancaService.notificar_dados_execucao_daycoval([dado])
        
        await criacao_boletos_parciais()

        return execucao
    
    async def execucao_coleta_boletos(self, execucao: ExecucaoDaycovalSchema, *_):
        execucoes = await self.cobranca_repository.execucoes_daycoval()
        retornos_ja_processados = {
            dado.nome_arquivo_retorno
            for execucao in execucoes
            for dado in execucao.dados
            if dado.nome_arquivo_retorno
        }
        dados_sem_retorno = [
            DadosExecucaoDaycovalSchema.from_model(dado)
            for execucao in execucoes
            for dado in execucao.dados
            if dado.conteudo_arquivo_retorno == None
        ]
        
        @self.wrapper_passo(execucao, 'locacoes.boletos.arquivos.webdriver.boleto.armazenamento')
        async def download():
            async with self.pagina() as ctx:
                await self.acesso_site_daycoval(execucao, ctx)
                await ctx.page.locator('#ctl00_ucBarraMenu_MenuRepeater_ctl05_divMenuNaoClicavel').click()
                await ctx.page.locator('#ctl00_ucBarraMenu_MenuRepeater_ctl05_SubMenuRepeaterColuna1_ctl00_ItensSubMenuRepeaterColuna1_ctl14_lnkButtonIrPaginaSelecionada1').click()
                await ctx.page.locator('#ctl00_cphPrincipal_tabDownload').click()
                linhas_arquivos = await ctx.page.locator('#ctl00_cphPrincipal_gvArquivo_wrapper > .table-responsive > table > tbody > tr').all()

                @self.wrapper_passo(execucao, 'locacoes.boletos.arquivos.webdriver.retorno.download')
                async def clicar_e_baixar():
                    for linha in linhas_arquivos:
                        link = linha.locator('a')
                        nome_arquivo = await link.text_content()
                        if not nome_arquivo or nome_arquivo in retornos_ja_processados:
                            continue
                        caminho = f"{ctx.download_dir}/{nome_arquivo}"
                        async with ctx.page.expect_download() as download_info:
                            await link.click()
                        download = await download_info.value
                        await download.save_as(caminho)
                        linhas: list[str] = []
                        with open(caminho, 'r') as arquivo:
                            linhas = arquivo.readlines()
                        for dado in dados_sem_retorno:
                            linhas_associadas = [
                                linha
                                for linha in linhas
                                if linha[116:126].upper() == dado.identificador_documento_cobranca.upper()
                            ]
                            if len(linhas_associadas) == 0:
                                continue
                            conteudo_retorno = '\n'.join(linhas)
                            await self.cobranca_repository.salvar_informacoes_retorno({
                                dado.id: {
                                    'nome_arquivo': nome_arquivo,
                                    'conteudo': conteudo_retorno
                                }
                            })
                            await self.cobranca_repository.db.commit()
                await clicar_e_baixar()
        await download()

        @self.wrapper_passo(execucao, 'locacoes.boletos.arquivos.completo.criacao')
        async def gerar_boletos_completos():
            dados_sem_boleto_completo = [
                DadosExecucaoDaycovalSchema.from_model(dado)
                for exec in await self.cobranca_repository.execucoes_daycoval()
                for dado in exec.dados
                if dado.arquivo_id_boleto_completo_pdf == None
                and dado.conteudo_arquivo_retorno
            ]
            contratos = {
                c.id: c
                for c in await self.cobranca_repository.contratos([dado.contrato_id for dado in dados_sem_boleto_completo])
            }

            for dado in dados_sem_boleto_completo:
                linhas = [
                    linha
                    for linha in (dado.conteudo_arquivo_retorno or '').split('\n')
                    if linha[116:126].upper() == dado.identificador_documento_cobranca.upper()
                ]
                if len(linhas) == 0:
                    continue
                linha = linhas[0]
                uso_do_banco = linha[30:37]
                nosso_numero = linha[62:73]
                fator_vencimento = 1000 + (dado.vencimento - date(2000, 7, 3)).days % 9000
                async with self.pagina() as ctx:
                    contrato = contratos[dado.contrato_id]
                    inquilino = contrato.inquilino
                    hoje = date.today()
                    vencimento = dado.vencimento
                    qparams = [
                        f"vencimento={vencimento.strftime('%d/%m/%Y')}",
                        f"data_documento={hoje.strftime('%d/%m/%Y')}",
                        f"numero_documento={dado.identificador_documento_cobranca}",
                        f"valor_documento={dado.valor}",
                        f"instrucoes={dado.html_cobranca()}",
                        f"pagador={inquilino.razao_social}<br>{inquilino.logradouro}<br>{inquilino.bairro} - {inquilino.cidade}/{inquilino.estado} - CEP: {inquilino.cep}",
                        f"cnpj_pagador={inquilino.cnpj}",
                        f"uso_banco={uso_do_banco}",
                        f"nosso_numero={nosso_numero}",
                        f"fator_vencimento={fator_vencimento}"
                    ]
                    await ctx.page.goto(f'file:///home/host_user/app/modules/cobranca/views/boleto/view.html?{"&".join(qparams)}')
                    buf = await ctx.page.pdf(
                        display_header_footer=False,
                        width='1077px',
                        height='762px',
                        margin={
                            'top': '0px',
                            'bottom': '0px',
                            'left': '0px',
                            'right': '0px'
                        },
                        print_background=True
                    )
                    arq_svc = ArquivosDatabaseRepository(self.cobranca_repository.db)
                    id_arq = await arq_svc.criar(BytesIO(buf), "boleto.pdf", "application/pdf")
                    dado.arquivo_id_boleto_completo_pdf = id_arq
                    await self.cobranca_repository.salvar_informacoes_boleto_completo(dado.id, dado.arquivo_id_boleto_completo_pdf)
                    await self.cobranca_repository.db.commit()
                    await CobrancaService.notificar_dados_execucao_daycoval([dado])
        await gerar_boletos_completos()

    async def criar_execucao_daycoval(
        self,
        dados: list[BodyCriacaoDadosExecucaoDaycovalSchema] | int,
        tipo_execucao_id: int,
        usuario: Usuario
    ):
        if tipo_execucao_id == 1:
            executar = self.wrapper_execucao(self.execucao_criacao_cobranca)
            return await executar(dados, tipo_execucao_id, usuario)
        elif tipo_execucao_id == 2:
            executar = self.wrapper_execucao(self.execucao_coleta_boletos)
            return await executar([] if type(dados) == list else dados, tipo_execucao_id, usuario)
        return None