import uuid

from config.swagger import token_field
from datetime import date
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.routing import APIRouter
from http import HTTPStatus
from io import BytesIO
from requests_toolbelt import MultipartEncoder

from modules.util.mediatypes import ZIP
from modules.util.parallel import Parallel
from modules.util.temp_file import TempFileHelper
from modules.posicao.xml_anbima_401.service import XMLAnbima401Service

from .aluguel_acoes.service import AluguelAcoesService
from .bolsa.service import BolsaService
from .bonds_offshore.service import BondsOffshoreService
from .renda_fixa.service import RendaFixaService
from .compromissadas.service import CompromissadasService
from .movimentacoes_pgbl.service import MovimentacoesPGBLService
from .taxa_performance.service import TaxaPerformanceService
from .cotas.service import CotasService
from .batimentos.estoque.service import BatimentoEstoqueService
from .batimentos.estoque.schema import ResponseSchema as BatimentoEstoqueResponseSchema
from .batimentos.precos.service import BatimentoPrecosCreditoPrivado
from .batimentos.precos.schema import (
    ResponseSchema as BatimentoPrecosDestoantesResponseSchema,
)
from .batimentos.xmls.service import BatimentoXmlsService
from .batimentos.xmls.schema import ResponseSchema as BatimentoXmlsResponseSchema
from .batimentos.patrimonio_liquido.service import BatimentoPatrimonioLiquidoService
from .batimentos.patrimonio_liquido.schema import (
    ResponseSchema as BatimentoPatrimonioLiquidoResponseSchema,
)


router = APIRouter(
    prefix="/liberacao-cotas", tags=["Liberação de cotas"], dependencies=[token_field]
)


@router.post("/aluguel-acoes/renovacoes")
async def alugel_acoes_renovacoes(
    data_referente: date,
    xls_caracteristicas_fundos: UploadFile = File(...),
    csv_relatorio_bip: UploadFile = File(...),
):
    identificador_arqs_temp = f"aluguelacoesrenovacoes-{str(uuid.uuid4())}"
    service = AluguelAcoesService(identificador_arqs_temp=identificador_arqs_temp)

    valida_arquivos_xls(
        arquivos=[xls_caracteristicas_fundos],
        mensagem_erro="Input planilha de característica de fundos inválida. O arquivo deve ser um .xls.",
    )
    valida_arquivos_csv(
        arquivos=[csv_relatorio_bip],
        mensagem_erro="Input relatório BIP inválido. O arquivo deve ser um .csv.",
    )

    identificador_arqs_temp: str = "aluguelacoesrenovacoes"

    try:
        [
            nome_arq_xls_caracteristicas_fundos,
            nome_arq_csv_relatorio_bip,
        ] = await service.cria_arqs_temporarios(
            [xls_caracteristicas_fundos, csv_relatorio_bip]
        )

        (zip_buffer, avisos_json) = await Parallel.execute(
            1,
            service.get_zip_buffer_renovacoes,
            data_referente,
            nome_arq_xls_caracteristicas_fundos,
            nome_arq_csv_relatorio_bip,
        )
        zip_buffer.seek(0)

        nome_arquivo: str = (
            f"{data_referente.strftime('%Y%m%d')}_aluguel_acoes_liquidacao.zip"
        )
        multipart = MultipartEncoder(
            fields={"avisos": avisos_json, "arquivo": (nome_arquivo, zip_buffer, ZIP)}
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return Response(multipart.to_string(), media_type=multipart.content_type)


@router.post("/aluguel-acoes/novos_contratos")
async def aluguel_acoes_novos_contratos(
    data_referente: date,
    xls_caracteristicas_fundos: UploadFile = File(...),
    csv_relatorio_bip: UploadFile = File(...),
):
    identificador_arqs_temp = f"aluguelacoesnovoscontratos-{str(uuid.uuid4())}"
    service = AluguelAcoesService(identificador_arqs_temp=identificador_arqs_temp)

    valida_arquivos_xls(
        arquivos=[xls_caracteristicas_fundos],
        mensagem_erro="Input planilha de característica de fundos inválida. O arquivo deve ser um .xls.",
    )
    valida_arquivos_csv(
        arquivos=[csv_relatorio_bip],
        mensagem_erro="Input relatório BIP inválido. O arquivo deve ser um .csv.",
    )

    try:
        [
            nome_arq_xls_caracteristicas_fundos,
            nome_arq_csv_relatorio_bip,
        ] = await service.cria_arqs_temporarios(
            [xls_caracteristicas_fundos, csv_relatorio_bip]
        )

        (zip_buffer, avisos_json) = await Parallel.execute(
            1,
            service.get_zip_buffer_novos_contratos,
            data_referente,
            nome_arq_xls_caracteristicas_fundos,
            nome_arq_csv_relatorio_bip,
        )
        zip_buffer.seek(0)

        nome_arquivo: str = (
            f"{data_referente.strftime('%Y%m%d')}_aluguel_acoes_novos_contratos.zip"
        )
        multipart = MultipartEncoder(
            fields={"avisos": avisos_json, "arquivo": (nome_arquivo, zip_buffer, ZIP)}
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return Response(multipart.to_string(), media_type=multipart.content_type)


@router.post("/aluguel-acoes/antecipacoes")
async def aluguel_acoes_antecipacoes(
    data_referente: date,
    xls_caracteristicas_fundos: UploadFile = File(...),
    xlsx_relatorio_antecipacao: UploadFile = File(...),
):
    identificador_arqs_temp = f"aluguelacoesantecipacoes-{str(uuid.uuid4())}"
    service = AluguelAcoesService(identificador_arqs_temp=identificador_arqs_temp)

    valida_arquivos_xls(
        arquivos=[xls_caracteristicas_fundos],
        mensagem_erro="Input planilha de característica de fundos inválida. O arquivo deve ser um .xls.",
    )
    valida_arquivos_xlsx(
        arquivos=[xlsx_relatorio_antecipacao],
        mensagem_erro="Input relatório BIP inválido. O arquivo deve ser um .csv.",
    )

    try:
        [
            nome_arq_xls_caracteristicas_fundos,
            nome_arq_xlsx_relatorio_antecipacao,
        ] = await service.cria_arqs_temporarios(
            [xls_caracteristicas_fundos, xlsx_relatorio_antecipacao]
        )

        (zip_buffer, avisos_json) = await Parallel.execute(
            1,
            service.get_zip_buffer_antecipacoes,
            data_referente,
            nome_arq_xls_caracteristicas_fundos,
            nome_arq_xlsx_relatorio_antecipacao,
        )
        zip_buffer.seek(0)

        nome_arquivo: str = (
            f"{data_referente.strftime('%Y%m%d')}_aluguel_acoes_renovacoes.zip"
        )
        multipart = MultipartEncoder(
            fields={"avisos": avisos_json, "arquivo": (nome_arquivo, zip_buffer, ZIP)}
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return Response(multipart.to_string(), media_type=multipart.content_type)


@router.post("/movimentacoes-pgbl")
async def aluguel_acoes_movimentacoes_pbgl(
    data_referente: date,
    zips_arqs_xml_anbima_401: list[UploadFile] = File(...),
    xls_caracteristicas_fundos: UploadFile = File(...),
    xlsxs_relatorios_movimentacoes_pgbl: list[UploadFile] = File(...),
):
    identificador_arqs_temp = f"movimentacoespgbl-{str(uuid.uuid4())}"
    movimentacoes_pgbl_service = MovimentacoesPGBLService(
        identificador_arqs_temp=identificador_arqs_temp
    )
    xml_anbima_401_service = XMLAnbima401Service()

    valida_arquivos_zip(
        arquivos=zips_arqs_xml_anbima_401,
        mensagem_erro="Input de xmls anbima inválido. O arquivo deve ser um .zip",
    )
    valida_arquivos_xls(
        arquivos=[xls_caracteristicas_fundos],
        mensagem_erro="Input característica de fundos inválida. O arquivo deve ser um .xls",
    )
    valida_arquivos_xlsx(
        arquivos=xlsxs_relatorios_movimentacoes_pgbl,
        mensagem_erro="Input de movimentações PGBL inválido. O arquivo deve ser um .xlsx",
    )

    try:
        buffers_zips_arqs_xml_anbima_401: list[BytesIO] = []
        for zip in zips_arqs_xml_anbima_401:
            buffers_zips_arqs_xml_anbima_401.append(BytesIO(await zip.read()))

        nomes_arqs_xmls_anbima_401: list[tuple[str, str]] = await Parallel.execute(
            1,
            xml_anbima_401_service.cria_arquivos_xml_fundos_from_zips,
            buffers_zips_arqs_xml_anbima_401,
            identificador_arqs_temp,
        )

        nomes_arqs_temporarios: list[str] = (
            await movimentacoes_pgbl_service.cria_arqs_temporarios(
                [xls_caracteristicas_fundos, *xlsxs_relatorios_movimentacoes_pgbl]
            )
        )
        nome_arq_xls_caracteristicas_fundos: str = nomes_arqs_temporarios[0]
        nomes_arqs_xlsxs_relatorios_movimentacoes_pgbl: list[str] = (
            nomes_arqs_temporarios[1:]
        )

        (zip_buffer, avisos_json) = await Parallel.execute(
            1,
            movimentacoes_pgbl_service.get_zip_buffer_movimentacoes_pgbl,
            data_referente,
            nomes_arqs_xmls_anbima_401,
            nome_arq_xls_caracteristicas_fundos,
            nomes_arqs_xlsxs_relatorios_movimentacoes_pgbl,
        )
        zip_buffer.seek(0)

        nome_arquivo: str = (
            f"{data_referente.strftime('%Y%m%d')}_movimentacoes_pgbl.zip"
        )
        multipart = MultipartEncoder(
            fields={"avisos": avisos_json, "arquivo": (nome_arquivo, zip_buffer, ZIP)}
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return Response(multipart.to_string(), media_type=multipart.content_type)


@router.post("/precos/bolsa-bmf")
async def bolsa_bmf(
    usdbrl: float,
    zips_arqs_xml_anbima_401: list[UploadFile] = File(...),
    xlsm_depara_derivativos: UploadFile = File(...),
):
    identificador_arqs_temp = f"bolsabmf-{str(uuid.uuid4())}"
    bolsa_service = BolsaService(identificador_arqs_temp=identificador_arqs_temp)
    xml_anbima_401_service = XMLAnbima401Service()

    valida_arquivos_zip(
        arquivos=zips_arqs_xml_anbima_401,
        mensagem_erro="Input de xmls anbima inválido. O arquivo deve ser um .zip",
    )
    valida_arquivos_xlsm(
        arquivos=[xlsm_depara_derivativos],
        mensagem_erro="Input DE/PARA derivativos inválido. O arquivo deve ser um .xlsm",
    )

    try:
        buffers_zips_arqs_xml_anbima_401: list[BytesIO] = []
        for zip in zips_arqs_xml_anbima_401:
            buffers_zips_arqs_xml_anbima_401.append(BytesIO(await zip.read()))

        nomes_arqs_xmls_anbima_401: list[tuple[str, str]] = await Parallel.execute(
            1,
            xml_anbima_401_service.cria_arquivos_xml_fundos_from_zips,
            buffers_zips_arqs_xml_anbima_401,
            identificador_arqs_temp,
        )

        [nome_arq_xlsm_depara_derivativos] = await bolsa_service.cria_arqs_temporarios(
            [xlsm_depara_derivativos]
        )

        (zip_buffer, avisos_json) = await Parallel.execute(
            1,
            bolsa_service.get_zip_buffer_bolsa_e_bmf,
            nomes_arqs_xmls_anbima_401,
            nome_arq_xlsm_depara_derivativos,
            usdbrl,
        )
        zip_buffer.seek(0)

        nome_arquivo: str = "bolsa_bmf.zip"
        multipart = MultipartEncoder(
            fields={"avisos": avisos_json, "arquivo": (nome_arquivo, zip_buffer, ZIP)}
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return Response(multipart.to_string(), media_type=multipart.content_type)


@router.post("/precos/bonds-offshore")
async def offshore_bonds(
    usdbrl: float,
    zips_arqs_xml_anbima_401: list[UploadFile] = File(...),
    xlsx_depara_bonds_offshore: UploadFile = File(...),
):
    identificador_arqs_temp = f"offshorebonds-{str(uuid.uuid4())}"
    bonds_offshore_service = BondsOffshoreService(
        identificador_arqs_temp=identificador_arqs_temp
    )
    xml_anbima_401_service = XMLAnbima401Service()

    valida_arquivos_zip(
        arquivos=zips_arqs_xml_anbima_401,
        mensagem_erro="Input de xmls anbima inválido. O arquivo deve ser um .zip",
    )
    valida_arquivos_xlsx(
        arquivos=[xlsx_depara_bonds_offshore],
        mensagem_erro="Input de DE/PARA bonds inválido. O arquivo deve ser um .xlsx",
    )

    try:
        buffers_zips_arqs_xml_anbima_401: list[BytesIO] = []
        for zip in zips_arqs_xml_anbima_401:
            buffers_zips_arqs_xml_anbima_401.append(BytesIO(await zip.read()))

        nomes_arqs_xmls_anbima_401: list[tuple[str, str]] = await Parallel.execute(
            1,
            xml_anbima_401_service.cria_arquivos_xml_fundos_from_zips,
            buffers_zips_arqs_xml_anbima_401,
            identificador_arqs_temp,
        )

        [nome_arq_xlsx_depara_bonds] = (
            await bonds_offshore_service.cria_arqs_temporarios(
                [xlsx_depara_bonds_offshore]
            )
        )

        (zip_buffer, avisos_json) = await Parallel.execute(
            1,
            bonds_offshore_service.get_zip_buffer_offshore_bonds_offshore,
            nomes_arqs_xmls_anbima_401,
            nome_arq_xlsx_depara_bonds,
            usdbrl,
        )
        zip_buffer.seek(0)

        nome_arquivo: str = "bonds_offshore.zip"
        multipart = MultipartEncoder(
            fields={"avisos": avisos_json, "arquivo": (nome_arquivo, zip_buffer, ZIP)}
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return Response(multipart.to_string(), media_type=multipart.content_type)


@router.post("/precos/renda-fixa/nao-precificados-anbima-fundos-bradesco")
async def credito_privado_nao_precificado_anbima(
    zips_arqs_xml_anbima_401: list[UploadFile] = File(...),
    xls_caracteristicas_fundos: UploadFile = File(...),
    xlsx_depara_ativos_credito_privado: UploadFile = File(...),
    xlsx_depara_ativos_marcados_na_curva: UploadFile = File(...),
):
    identificador_arqs_temp = f"creditoprivadonaoprecificadosanbima-{str(uuid.uuid4())}"
    renda_fixa_service = RendaFixaService(
        identificador_arqs_temp=identificador_arqs_temp
    )
    xml_anbima_401_service = XMLAnbima401Service()

    valida_arquivos_zip(
        arquivos=zips_arqs_xml_anbima_401,
        mensagem_erro="Input de xmls anbima inválido. O arquivo deve ser um .zip",
    )
    valida_arquivos_xls(
        arquivos=[xls_caracteristicas_fundos],
        mensagem_erro="Input característica de fundos inválida. O arquivo deve ser um .xls",
    )
    valida_arquivos_xlsx(
        arquivos=[xlsx_depara_ativos_credito_privado],
        mensagem_erro="Input de DE/PARA ativos crédito privado não precificados pela ABNIMA inválido. O arquivo deve ser um .xlsx",
    )
    valida_arquivos_xlsx(
        arquivos=[xlsx_depara_ativos_marcados_na_curva],
        mensagem_erro="Input de DE/PARA ativos marcados na curva inválido. O arquivo deve ser um .xlsx",
    )

    try:
        buffers_zips_arqs_xml_anbima_401: list[BytesIO] = []
        for zip in zips_arqs_xml_anbima_401:
            buffers_zips_arqs_xml_anbima_401.append(BytesIO(await zip.read()))

        nomes_arqs_xmls_anbima_401: list[tuple[str, str]] = await Parallel.execute(
            1,
            xml_anbima_401_service.cria_arquivos_xml_fundos_from_zips,
            buffers_zips_arqs_xml_anbima_401,
            identificador_arqs_temp,
        )

        [
            nome_arq_xls_caracteristicas_fundos,
            nome_arq_xlsx_depara_ativos_credito_privado,
            nome_arq_xlsx_depara_ativos_marcados_na_curva,
        ] = await renda_fixa_service.cria_arqs_temporarios(
            [
                xls_caracteristicas_fundos,
                xlsx_depara_ativos_credito_privado,
                xlsx_depara_ativos_marcados_na_curva,
            ]
        )

        (zip_buffer, avisos_json) = await Parallel.execute(
            1,
            renda_fixa_service.get_zip_buffer_ativos_renda_fixa_nao_precificados_anbima_fundos_bradesco,
            nomes_arqs_xmls_anbima_401,
            nome_arq_xls_caracteristicas_fundos,
            nome_arq_xlsx_depara_ativos_credito_privado,
            nome_arq_xlsx_depara_ativos_marcados_na_curva,
        )
        zip_buffer.seek(0)

        nome_arquivo: str = "ativos_nao_precificados_anbima.zip"
        multipart = MultipartEncoder(
            fields={
                "avisos": avisos_json,
                "arquivo": (nome_arquivo, zip_buffer, ZIP),
            }
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return Response(multipart.to_string(), media_type=multipart.content_type)


@router.post("/precos/credito-privado/marcacao-mercado-em-fundos-nao-bradesco")
async def credito_privado_marcacao_mercado_em_fundos_nao_bradesco(
    zips_arqs_xml_anbima_401: list[UploadFile] = File(...),
    xls_caracteristicas_fundos: UploadFile = File(...),
    xlsx_depara_ativos_credito_privado: UploadFile = File(...),
):
    identificador_arqs_temp = (
        f"creditoprivadomarcacaomercadoemfundosnaobradesco-{str(uuid.uuid4())}"
    )
    renda_fixa_service = RendaFixaService(
        identificador_arqs_temp=identificador_arqs_temp
    )
    xml_anbima_401_service = XMLAnbima401Service()

    valida_arquivos_zip(
        arquivos=zips_arqs_xml_anbima_401,
        mensagem_erro="Input de xmls anbima inválido. O arquivo deve ser um .zip",
    )
    valida_arquivos_xls(
        arquivos=[xls_caracteristicas_fundos],
        mensagem_erro="Input característica de fundos inválida. O arquivo deve ser um .xls",
    )

    try:
        buffers_zips_arqs_xml_anbima_401: list[BytesIO] = []
        for zip in zips_arqs_xml_anbima_401:
            buffers_zips_arqs_xml_anbima_401.append(BytesIO(await zip.read()))

        nomes_arqs_xmls_anbima_401: list[tuple[str, str]] = await Parallel.execute(
            1,
            xml_anbima_401_service.cria_arquivos_xml_fundos_from_zips,
            buffers_zips_arqs_xml_anbima_401,
            identificador_arqs_temp,
        )

        [
            nome_arq_xls_caracteristicas_fundos,
            nome_arq_xlsx_depara_ativos_credito_privado,
        ] = await renda_fixa_service.cria_arqs_temporarios(
            [xls_caracteristicas_fundos, xlsx_depara_ativos_credito_privado]
        )

        (zip_buffer, avisos_json) = await Parallel.execute(
            1,
            renda_fixa_service.get_zip_buffer_marcacao_mercado_ativos_em_fundos_nao_bradesco,
            nomes_arqs_xmls_anbima_401,
            nome_arq_xls_caracteristicas_fundos,
            nome_arq_xlsx_depara_ativos_credito_privado,
        )
        zip_buffer.seek(0)

        nome_arquivo: str = "marcacao_mercado_manual_fundos_nao_bradesco.zip"
        multipart = MultipartEncoder(
            fields={"avisos": avisos_json, "arquivo": (nome_arquivo, zip_buffer, ZIP)}
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return Response(multipart.to_string(), media_type=multipart.content_type)


@router.post("/precos/cotas-fundos")
async def cotas_fundos(
    zips_arqs_xml_anbima_401: list[UploadFile] = File(...),
    xlsx_depara_cotas_fundos: UploadFile = File(...),
    xls_caracteristicas_fundos: UploadFile = File(...),
):
    identificador_arqs_temp = f"cotasfundos-{str(uuid.uuid4())}"
    cotas_service = CotasService(identificador_arqs_temp=identificador_arqs_temp)
    xml_anbima_401_service = XMLAnbima401Service()

    valida_arquivos_zip(
        arquivos=zips_arqs_xml_anbima_401,
        mensagem_erro="Input de xmls anbima inválido. O arquivo deve ser um .zip",
    )
    valida_arquivos_xlsx(
        arquivos=[xlsx_depara_cotas_fundos],
        mensagem_erro="Input de DE/PARA cotas fundos inválido. O arquivo deve ser um .xlsx",
    )
    valida_arquivos_xls(
        arquivos=[xls_caracteristicas_fundos],
        mensagem_erro="Input característica de fundos inválida. O arquivo deve ser um .xls",
    )

    try:
        buffers_zips_arqs_xml_anbima_401: list[BytesIO] = []
        for zip in zips_arqs_xml_anbima_401:
            buffers_zips_arqs_xml_anbima_401.append(BytesIO(await zip.read()))

        nomes_arqs_xmls_anbima_401: list[tuple[str, str]] = await Parallel.execute(
            1,
            xml_anbima_401_service.cria_arquivos_xml_fundos_from_zips,
            buffers_zips_arqs_xml_anbima_401,
            identificador_arqs_temp,
        )

        [nome_arq_xlsx_depara_cotas_fundos, nome_arq_xls_caracteristicas_fundos] = (
            await cotas_service.cria_arqs_temporarios(
                [xlsx_depara_cotas_fundos, xls_caracteristicas_fundos]
            )
        )

        (zip_buffer, avisos_json) = await Parallel.execute(
            1,
            cotas_service.get_zip_buffer_cotas_fundos,
            nomes_arqs_xmls_anbima_401,
            nome_arq_xlsx_depara_cotas_fundos,
            nome_arq_xls_caracteristicas_fundos,
        )
        zip_buffer.seek(0)

        nome_arquivo: str = "historico_cotas_fundos.zip"
        multipart = MultipartEncoder(
            fields={
                "avisos": avisos_json,
                "arquivo": (nome_arquivo, zip_buffer, ZIP),
            }
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return Response(multipart.to_string(), media_type=multipart.content_type)


@router.post("/compromissadas")
async def compromissadas(
    zips_arqs_xml_anbima_401: list[UploadFile] = File(...),
    xls_caracteristicas_fundos: UploadFile = File(...),
):
    identificador_arqs_temp = f"compromissadas-{str(uuid.uuid4())}"
    compromissadas_service = CompromissadasService(
        identificador_arqs_temp=identificador_arqs_temp
    )
    xml_anbima_401_service = XMLAnbima401Service()

    valida_arquivos_zip(
        arquivos=zips_arqs_xml_anbima_401,
        mensagem_erro="Input de xmls anbima inválido. O arquivo deve ser um .zip",
    )
    valida_arquivos_xls(
        arquivos=[xls_caracteristicas_fundos],
        mensagem_erro="Input característica de fundos inválida. O arquivo deve ser um .xls",
    )

    try:
        buffers_zips_arqs_xml_anbima_401: list[BytesIO] = []
        for zip in zips_arqs_xml_anbima_401:
            buffers_zips_arqs_xml_anbima_401.append(BytesIO(await zip.read()))

        nomes_arqs_xmls_anbima_401: list[tuple[str, str]] = await Parallel.execute(
            1,
            xml_anbima_401_service.cria_arquivos_xml_fundos_from_zips,
            buffers_zips_arqs_xml_anbima_401,
            identificador_arqs_temp,
        )
        [nome_arq_xls_caracteristicas_fundos] = (
            await compromissadas_service.cria_arqs_temporarios(
                [xls_caracteristicas_fundos]
            )
        )

        (zip_buffer, avisos_json) = await Parallel.execute(
            1,
            compromissadas_service.get_zip_buffer_compromissadas,
            nomes_arqs_xmls_anbima_401,
            nome_arq_xls_caracteristicas_fundos,
        )
        zip_buffer.seek(0)

        nome_arquivo: str = "compromissadas.zip"
        multipart = MultipartEncoder(
            fields={"avisos": avisos_json, "arquivo": (nome_arquivo, zip_buffer, ZIP)}
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return Response(multipart.to_string(), media_type=multipart.content_type)


@router.post("/taxa-performance")
async def taxa_performance(
    zips_arqs_xml_anbima_401: list[UploadFile] = File(...),
    xlsx_relatorio_despesas_britech: UploadFile = File(...),
    xls_caracteristicas_fundos: UploadFile = File(...),
):
    identificador_arqs_temp = f"taxaperformance-{str(uuid.uuid4())}"
    taxa_performance_service = TaxaPerformanceService(
        identificador_arqs_temp=identificador_arqs_temp
    )
    xml_anbima_401_service = XMLAnbima401Service()

    valida_arquivos_zip(
        arquivos=zips_arqs_xml_anbima_401,
        mensagem_erro="Input xmls anbima inválido. O arquivo deve ser um .zip",
    )
    valida_arquivos_xlsx(
        arquivos=[xlsx_relatorio_despesas_britech],
        mensagem_erro="Input xlsx relatório despesas britech inválido. O arquivo deve ser um .xlsx",
    )
    valida_arquivos_xls(
        arquivos=[xls_caracteristicas_fundos],
        mensagem_erro="Input característica de fundos inválida. O arquivo deve ser um .xls",
    )

    try:
        buffers_zips_arqs_xml_anbima_401: list[BytesIO] = []
        for zip in zips_arqs_xml_anbima_401:
            buffers_zips_arqs_xml_anbima_401.append(BytesIO(await zip.read()))

        nomes_arqs_xmls_anbima_401: list[tuple[str, str]] = await Parallel.execute(
            1,
            xml_anbima_401_service.cria_arquivos_xml_fundos_from_zips,
            buffers_zips_arqs_xml_anbima_401,
            identificador_arqs_temp,
        )

        [
            nome_arq_xlsx_relatorio_despesas_britech,
            nome_arq_xls_caracteristicas_fundos,
        ] = await taxa_performance_service.cria_arqs_temporarios(
            [xlsx_relatorio_despesas_britech, xls_caracteristicas_fundos]
        )

        (zip_buffer, avisos_json) = await Parallel.execute(
            1,
            taxa_performance_service.get_zip_buffer_taxas_performance,
            nomes_arqs_xmls_anbima_401,
            nome_arq_xlsx_relatorio_despesas_britech,
            nome_arq_xls_caracteristicas_fundos,
        )
        zip_buffer.seek(0)

        nome_arquivo: str = "taxa_performance.zip"
        multipart = MultipartEncoder(
            fields={"avisos": avisos_json, "arquivo": (nome_arquivo, zip_buffer, ZIP)}
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return Response(multipart.to_string(), media_type=multipart.content_type)


@router.post("/batimento/estoque")
async def batimento_estoque(
    usdbrl: float,
    zips_arqs_xml_anbima_401: list[UploadFile] = File(...),
    xls_caracteristicas_fundos: UploadFile = File(...),
    xlsx_depara_cotas_fundos: UploadFile = File(...),
    xlsm_depara_derivativos: UploadFile = File(...),
    xlsx_estoque_renda_fixa: UploadFile = File(...),
    xlsx_estoque_renda_variavel: UploadFile = File(...),
    xlsx_estoque_futuro: UploadFile = File(...),
    xlsx_estoque_cota: UploadFile = File(...),
):
    identificador_arqs_temp = f"batimentoestoque-{str(uuid.uuid4())}"
    batimento_estoque_service: BatimentoEstoqueService = BatimentoEstoqueService()
    xml_anbima_401_service: XMLAnbima401Service = XMLAnbima401Service()

    valida_arquivos_zip(
        arquivos=zips_arqs_xml_anbima_401,
        mensagem_erro="Input xmls anbima inválido. O arquivo deve ser um .zip",
    )
    valida_arquivos_xls(
        arquivos=[xls_caracteristicas_fundos],
        mensagem_erro="Input característica de fundos inválida. O arquivo deve ser um .xls",
    )
    valida_arquivos_xlsx(
        arquivos=[xlsx_depara_cotas_fundos],
        mensagem_erro="Input de DE/PARA cotas fundos inválido. O arquivo deve ser um .xlsx",
    )
    valida_arquivos_xlsm(
        arquivos=[xlsm_depara_derivativos],
        mensagem_erro="Input DE/PARA derivativos inválido. O arquivo deve ser um .xlsm",
    )
    valida_arquivos_xlsx(
        arquivos=[xlsx_estoque_renda_fixa],
        mensagem_erro="Input xlsx_estoque_renda_fixa inválido. O arquivo deve ser um .xlsx",
    )
    valida_arquivos_xlsx(
        arquivos=[xlsx_estoque_renda_variavel],
        mensagem_erro="Input xlsx_estoque_renda_variavel inválido. O arquivo deve ser um .xlsx",
    )
    valida_arquivos_xlsx(
        arquivos=[xlsx_estoque_futuro],
        mensagem_erro="Input xlsx_estoque_futuro inválido. O arquivo deve ser um .xlsx",
    )
    valida_arquivos_xlsx(
        arquivos=[xlsx_estoque_cota],
        mensagem_erro="Input xlsx_estoque_cota inválido. O arquivo deve ser um .xlsx",
    )

    try:
        buffers_zips_arqs_xml_anbima_401: list[BytesIO] = []
        for zip in zips_arqs_xml_anbima_401:
            buffers_zips_arqs_xml_anbima_401.append(BytesIO(await zip.read()))

        nomes_arqs_xmls_anbima_401: list[tuple[str, str]] = await Parallel.execute(
            1,
            xml_anbima_401_service.cria_arquivos_xml_fundos_from_zips,
            buffers_zips_arqs_xml_anbima_401,
            identificador_arqs_temp,
        )

        [
            nome_arq_xls_caracteristicas_fundos,
            nome_arq_xlsx_depara_cotas_fundos,
            nome_arq_xlsm_depara_derivativos,
            nome_arq_xlsx_estoque_renda_fixa,
            nome_arq_xlsx_estoque_renda_variavel,
            nome_arq_xlsx_estoque_futuro,
            nome_arq_xlsx_estoque_cota,
        ] = await TempFileHelper.cria_arqs_temporarios(
            [
                xls_caracteristicas_fundos,
                xlsx_depara_cotas_fundos,
                xlsm_depara_derivativos,
                xlsx_estoque_renda_fixa,
                xlsx_estoque_renda_variavel,
                xlsx_estoque_futuro,
                xlsx_estoque_cota,
            ],
            identificador_arqs_temp,
        )

        estoque_e_avisos: BatimentoEstoqueResponseSchema = await Parallel.execute(
            1,
            batimento_estoque_service.get_batimento_estoque,
            usdbrl,
            nomes_arqs_xmls_anbima_401,
            nome_arq_xls_caracteristicas_fundos,
            nome_arq_xlsx_depara_cotas_fundos,
            nome_arq_xlsm_depara_derivativos,
            nome_arq_xlsx_estoque_renda_fixa,
            nome_arq_xlsx_estoque_renda_variavel,
            nome_arq_xlsx_estoque_futuro,
            nome_arq_xlsx_estoque_cota,
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return estoque_e_avisos


@router.post("/batimento/xmls-faltantes")
async def batimento_xmls_faltantes(
    zips_arqs_xml_anbima_401: list[UploadFile] = File(...),
    xls_caracteristicas_fundos: UploadFile = File(...),
):
    """
    Lista os XMLs não encontrados dos fundos existentes em xls_caracteristicas_fundos
    """

    identificador_arqs_temp = f"batimentoxmls-{str(uuid.uuid4())}"
    batimento_xmls_service: BatimentoXmlsService = BatimentoXmlsService()
    xml_anbima_401_service: XMLAnbima401Service = XMLAnbima401Service()

    valida_arquivos_zip(
        arquivos=zips_arqs_xml_anbima_401,
        mensagem_erro="Input xmls anbima inválido. O arquivo deve ser um .zip",
    )
    valida_arquivos_xls(
        arquivos=[xls_caracteristicas_fundos],
        mensagem_erro="Input característica de fundos inválida. O arquivo deve ser um .xls",
    )

    try:
        buffers_zips_arqs_xml_anbima_401: list[BytesIO] = []
        for zip in zips_arqs_xml_anbima_401:
            buffers_zips_arqs_xml_anbima_401.append(BytesIO(await zip.read()))

        nomes_arqs_xmls_anbima_401: list[tuple[str, str]] = await Parallel.execute(
            1,
            xml_anbima_401_service.cria_arquivos_xml_fundos_from_zips,
            buffers_zips_arqs_xml_anbima_401,
            identificador_arqs_temp,
        )

        [nome_arq_xls_caracteristicas_fundos] = (
            await TempFileHelper.cria_arqs_temporarios(
                [xls_caracteristicas_fundos], identificador_arqs_temp
            )
        )

        response: BatimentoXmlsResponseSchema = await Parallel.execute(
            1,
            batimento_xmls_service.get_batimento_xmls,
            nomes_arqs_xmls_anbima_401,
            nome_arq_xls_caracteristicas_fundos,
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return response


@router.post("/batimento/patrimonio-liquido")
async def batimento_patrimonio_liquido(
    zips_arqs_xml_anbima_401: list[UploadFile] = File(...),
    xls_caracteristicas_fundos: UploadFile = File(...),
):
    identificador_arqs_temp = f"batimentopatrimonioliquido-{str(uuid.uuid4())}"
    batimento_patrimonio_liquido_service: BatimentoPatrimonioLiquidoService = (
        BatimentoPatrimonioLiquidoService()
    )
    xml_anbima_401_service: XMLAnbima401Service = XMLAnbima401Service()

    valida_arquivos_zip(
        arquivos=zips_arqs_xml_anbima_401,
        mensagem_erro="Input xmls anbima inválido. O arquivo deve ser um .zip",
    )
    valida_arquivos_xls(
        arquivos=[xls_caracteristicas_fundos],
        mensagem_erro="Input característica de fundos inválida. O arquivo deve ser um .xls",
    )

    try:
        buffers_zips_arqs_xml_anbima_401: list[BytesIO] = []
        for zip in zips_arqs_xml_anbima_401:
            buffers_zips_arqs_xml_anbima_401.append(BytesIO(await zip.read()))

        nomes_arqs_xmls_anbima_401: list[tuple[str, str]] = await Parallel.execute(
            1,
            xml_anbima_401_service.cria_arquivos_xml_fundos_from_zips,
            buffers_zips_arqs_xml_anbima_401,
            identificador_arqs_temp,
        )

        [nome_arq_xls_caracteristicas_fundos] = (
            await TempFileHelper.cria_arqs_temporarios(
                [xls_caracteristicas_fundos], identificador_arqs_temp
            )
        )

        response: BatimentoPatrimonioLiquidoResponseSchema = await Parallel.execute(
            1,
            batimento_patrimonio_liquido_service.get_batimento_patrimonio_liquido,
            nomes_arqs_xmls_anbima_401,
            nome_arq_xls_caracteristicas_fundos,
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return response


@router.post(
    "/batimento/precos/credito-privado",
    response_model=BatimentoPrecosDestoantesResponseSchema,
    summary="Identifica Ocorrências de Preços para Ativos com Destoâncias",  # Título ajustado
    description="""**Realiza o batimento de preços para ativos de crédito privado.**

Este endpoint processa arquivos XML ANBIMA 401 (contidos em arquivos ZIP) e
um arquivo XLS com características dos fundos.

Seu objetivo é identificar ativos que apresentam **preços unitários (PU) diferentes
para a mesma data de posição**, mesmo que esses preços venham de fundos diferentes.

A resposta contém uma lista (`ativos`) com **todas as ocorrências de preço encontradas**
para os ativos que foram sinalizados como tendo potenciais destoâncias.

OBS.: Só será comparado ativos de fundos que tenham o mesmo custodiante

**Exemplo de Destoância que Levaria um Ativo a ser Incluído:**
Se o ativo 'ABCDE11' possui um PU de R$ 100,50 no Fundo X na data D, e o
mesmo ativo 'ABCDE11' possui um PU de R$ 100,60 no Fundo Y na mesma data D,
*ambas* as ocorrências de preço para 'ABCDE11' na data D (uma do Fundo X e
outra do Fundo Y) serão incluídas na lista `ativos` da resposta.

**Estrutura da Resposta:**
A resposta é um objeto JSON contendo a chave `ativos`. O valor de `ativos` é
uma lista (`[]`) onde cada item representa uma ocorrência de preço para um
ativo em uma data específica e contém os seguintes campos:
*   `codigo`: Código do ativo (string)
*   `isin`: Código ISIN do ativo (string, pode ser nulo/opcional)
*   `preco_unitario_posicao`: Preço unitário na data (string, representando o valor Decimal)
*   `data_referente`: Data da posição (string, formato YYYY-MM-DD)
*   `fundo_info`: Objeto com informações do fundo de origem, contendo:
    *   `codigo_britech` (string)
    *   `codigo_administrador` (string)
    *   `cnpj` (string)
    *   `nome` (string)
    *   `tipo_cota` (string)
    *   `nome_arq_xml_anbima_401` (string): Nome do arquivo XML de onde a info foi extraída.

Os arquivos devem ser enviados via `multipart/form-data`.
""",
    responses={
        200: {
            "description": "Sucesso - Retorna um objeto contendo a lista (`ativos`) com as ocorrências de preço para os ativos identificados com potenciais destoâncias.",
        },
        422: {
            "description": "Erro de validação nos arquivos de entrada (formato incorreto ou dados inválidos).",
        },
        500: {"description": "Erro interno no servidor durante o processamento."},
    },
)
async def batimento_precos_credito_privado(
    zips_arqs_xml_anbima_401: list[UploadFile] = File(...),
    xls_caracteristicas_fundos: UploadFile = File(...),
):
    identificador_arqs_temp = f"batimentoprecosdestoantes-{str(uuid.uuid4())}"
    batimento_precos_destoantes_service: BatimentoPrecosCreditoPrivado = (
        BatimentoPrecosCreditoPrivado()
    )
    xml_anbima_401_service: XMLAnbima401Service = XMLAnbima401Service()

    valida_arquivos_zip(
        arquivos=zips_arqs_xml_anbima_401,
        mensagem_erro="Input xmls anbima inválido. O arquivo deve ser um .zip",
    )
    valida_arquivos_xls(
        arquivos=[xls_caracteristicas_fundos],
        mensagem_erro="Input característica de fundos inválida. O arquivo deve ser um .xls",
    )

    try:
        buffers_zips_arqs_xml_anbima_401: list[BytesIO] = []
        for zip in zips_arqs_xml_anbima_401:
            buffers_zips_arqs_xml_anbima_401.append(BytesIO(await zip.read()))

        nomes_arqs_xmls_anbima_401: list[tuple[str, str]] = await Parallel.execute(
            1,
            xml_anbima_401_service.cria_arquivos_xml_fundos_from_zips,
            buffers_zips_arqs_xml_anbima_401,
            identificador_arqs_temp,
        )

        [nome_arq_xls_caracteristicas_fundos] = (
            await TempFileHelper.cria_arqs_temporarios(
                [xls_caracteristicas_fundos], identificador_arqs_temp
            )
        )

        response: BatimentoPrecosDestoantesResponseSchema = await Parallel.execute(
            1,
            batimento_precos_destoantes_service.get_batimento_precos_credito_privado,
            nomes_arqs_xmls_anbima_401,
            nome_arq_xls_caracteristicas_fundos,
        )
    except Exception as e:
        TempFileHelper.deleta_arquivos_temp_relacionados(identificador_arqs_temp)
        raise e

    return response


def valida_arquivos_xls(arquivos: list[UploadFile], mensagem_erro: str) -> None:
    for arquivo in arquivos:
        if arquivo.content_type != "application/vnd.ms-excel":
            raise HTTPException(
                status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, detail=mensagem_erro
            )


def valida_arquivos_xlsx(arquivos: list[UploadFile], mensagem_erro: str) -> None:
    for arquivo in arquivos:
        if (
            arquivo.content_type
            != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            raise HTTPException(
                status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, detail=mensagem_erro
            )


def valida_arquivos_xlsm(arquivos: list[UploadFile], mensagem_erro: str) -> None:
    for arquivo in arquivos:
        if arquivo.content_type != "application/vnd.ms-excel.sheet.macroEnabled.12":
            raise HTTPException(
                status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, detail=mensagem_erro
            )


def valida_arquivos_csv(arquivos: list[UploadFile], mensagem_erro: str) -> None:
    for arquivo in arquivos:
        if arquivo.content_type != "text/csv":
            raise HTTPException(
                status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, detail=mensagem_erro
            )


def valida_arquivos_zip(arquivos: list[UploadFile], mensagem_erro: str) -> None:
    for arquivo in arquivos:
        if (
            arquivo.content_type != "application/zip"
            and arquivo.content_type != "application/x-zip-compressed"
        ):
            raise HTTPException(
                status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, detail=mensagem_erro
            )
