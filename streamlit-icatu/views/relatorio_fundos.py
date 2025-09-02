import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode
import pandas as pd
from datetime import datetime, date
import requests
from environment import *
import os 
from os import listdir
from models import util as mutil
from dateutil.relativedelta import relativedelta
import zipfile
import shutil

def relatorio_fundos(barra, db, notion_controller):
    st.title('Relatório de Fundos')
    consultar, gerar_relatorio = st.tabs(["Consultar", "Gerar"])

    caminho_rede = os.path.join(r"\\ISMTZVANGUARDA", 
                                'Dir-GestaodeAtivos$', 
                                'Mesa Renda Fixa', 
                                '1. Gestão Crédito', 
                                'Banco de Dados', 
                                'Relatório Fundos')

    with consultar:
        meses = listdir(caminho_rede)
        meses = [i.replace('-', '/') for i in meses] if meses else [(date.today() + relativedelta(months=-1)).strftime('%Y/%m')]
        meses = sorted(meses, reverse=True)
        col1, col2 =  st.columns([1, 4])
        mes = col1.selectbox('Mês', meses)
        atualizar = st.button('Atualizar')
        form = st.empty()
        with form.form('sdf'):
            st.subheader('Consultar Relatório de Fundos')
            new_df = None
            if listdir(os.path.join(caminho_rede)):
                if [i for i in listdir(os.path.join(caminho_rede, mes.replace('/', '-'))) if i.startswith('relatorio')]:
                    st.write('Escolha os fundos')
                    fundos = [ i[17:29] for i in listdir(os.path.join(caminho_rede, mes.replace('/', '-')))]
                    fundos = ','.join([f"'{isin}'" for isin in fundos])
                    df = pd.DataFrame(db.query(f'''select 
                                               isin, 
                                               nome, 
                                               codigo_brit, 
                                               cnpj_classe as cnpj, 
                                               mesa, 
                                               nome_xml, 
                                               benchmark,
                                               case when subclasse = true then 'Sim' else 'Não' end as subclasse
                                            from icatu.fundos
                                            where isin in ({fundos})
                                            order by mesa, nome'''))
                    gb = GridOptionsBuilder.from_dataframe(df)
                    gb.configure_grid_options(enableRangeSelection=True)
                    gb.configure_grid_options(enableCellTextSelection=True)
                    gb.configure_selection('multiple', use_checkbox=True)
                    gb = gb.build()
                    gb['columnDefs'] = [
                            {'field': 'mesa', 'headerName': 'Mesa', 'minWidth': 180, 'filter': True},
                            {'field': 'subclasse', 'headerName': 'Subclasse','maxWidth': 100, 'minWidth': 100,'filter': True},
                            {'field': 'nome', 
                             'headerName': 'Nome', 
                             "checkboxSelection": True, 
                             'minWidth': 280,
                             'filter': True},
                            {'field': 'codigo_brit', 'headerName': 'BRIT', 'maxWidth': 100, 'filter': True},
                            {'field': 'benchmark', 'headerName': 'Benchmark', 'maxWidth': 130, 'filter': True},
                            {'field': 'isin', 'headerName': 'ISIN', 'maxWidth': 150, 'filter': True},
                            {'field': 'cnpj', 'headerName': 'CNPJ', 'minWidth': 150, 'maxWidth': 150, 'filter': True},
                            {'field': 'nome_xml', 'headerName': 'Nome Completo', 'minWidth': 500, 'filter': True}
                        ]

                    custom_css = {
                    ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                    ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                    ".ag-row":  {  "font-size": "16px !important;"}
                    }

                    new_df = AgGrid(
                    df,
                    gridOptions=gb,
                    update_mode='MODEL_CHANGED',
                    # fit_columns_on_grid_load=True,
                    allow_unsafe_jscode=True,
                    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                    enableRangeSelection=True,
                    custom_css=custom_css,
                    height=400,
                    enable_enterprise_modules=True)
                else:
                    st.write('Não há relatórios para o mês selecionado')
            else:
                st.write('Não há relatórios para o mês selecionado')
            download =st.form_submit_button('Gerar ZIP dos Relatórios')
        
        if download:
            if new_df:
                with st.spinner('Aguarde...'):
                    arquivos = [f"{'relatorio-'+mes.replace('/', '')}-{i['isin']}-{i['nome']}.pdf" for i in new_df['selected_rows']]
                    with zipfile.ZipFile("relatorio.zip", 'w') as zipMe:
                        for arquivo in arquivos:
                            zipMe.write(os.path.join(caminho_rede, mes.replace('/', '-'), arquivo), arquivo)

                    with open("relatorio.zip", 'rb') as f:
                        data = f.read()
                        btn = st.download_button(
                            label="Download",
                            data=data,
                            file_name="relatorio.zip",
                            mime="zip"
                        )
                    os.remove("relatorio.zip")

    with gerar_relatorio:
        st.subheader('Gerar Relatório de Fundos')
        mes_atual = (date.today() + relativedelta(months=-1)).strftime('%Y/%m')
        mes_anterior = (date.today() + relativedelta(months=-2)).strftime('%Y/%m')
        dois_meses_atras = (date.today() + relativedelta(months=-3)).strftime('%Y/%m')
        col1, _ =  st.columns([1, 4])
        mes = col1.selectbox('Mês', [mes_atual, mes_anterior, dois_meses_atras])
        with st.form('we'):
            col1, _ =  st.columns([1, 4])
            secoes_completa = ['Carta Mensal', 
                               'Secundário',
                               'Rentabilidade', 
                               'Composição da Carteira', 
                               'Compras e Vendas', 
                               'Ratings',
                               'Composição da Equipe',
                               'Carteira Detalhada',
                               'Fatos Relevantes']
            secoes = st.multiselect('Escolha as seções', secoes_completa,secoes_completa)
            marca_dagua = st.text_input("Escreva o texto da marca d'água (Opcional)")
            lista_secoes = {
                'Carta Mensal': 'carta_mensal', 
                'Rentabilidade': 'rentabilidade', 
                'Composição da Carteira': 'composicao_carteira', 
                'Compras e Vendas': 'compras_vendas', 
                'Ratings': 'ratings', 
                'Composição da Equipe': 'composicao_equipe',
                'Carteira Detalhada': 'carteira_detalhada',
                'Fatos Relevantes': 'fatos_relevantes',
                'Secundário': 'secundario'
            }
            lista_secoes = [lista_secoes[secao] for secao in secoes]
            st.write('Escolha os fundos')
            df = pd.DataFrame(db.query('''select 
                                        isin, 
                                        nome, 
                                        codigo_brit, 
                                        cnpj_classe as cnpj, 
                                        nome_xml, 
                                        mesa, 
                                        benchmark,
                                        case when subclasse = true then 'Sim' else 'Não' end as subclasse
                                       from icatu.fundos 
                                       where tipo_relatorio is not null
                                       order by mesa, nome'''))
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_grid_options(enableRangeSelection=True)
            gb.configure_grid_options(enableCellTextSelection=True)
            gb.configure_selection('multiple', use_checkbox=True)
            gb = gb.build()
            gb['columnDefs'] = [
                {'field': 'mesa', 'headerName': 'Mesa','minWidth': 150, 'maxWidth': 180, 'filter': True},
                {'field': 'subclasse', 'headerName': 'Subclasse','maxWidth': 100, 'minWidth': 100,'filter': True},
                {'field': 'nome', 
                 'headerName': 'Nome', 
                 "checkboxSelection": True, 
                 'minWidth': 280,
                 'filter': True},
                {'field': 'codigo_brit', 'headerName': 'BRIT', 'maxWidth': 100, 'filter': True},
                {'field': 'benchmark', 'headerName': 'Benchmark', 'maxWidth': 130, 'filter': True},
                {'field': 'isin', 'headerName': 'ISIN', 'maxWidth': 150, 'filter': True},
                {'field': 'cnpj', 'headerName': 'CNPJ', 'minWidth': 150, 'maxWidth': 150, 'filter': True},
                {'field': 'nome_xml', 'headerName': 'Nome Completo', 'minWidth': 500, 'filter': True},
                ]

            custom_css = {
                ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                ".ag-row":  {  "font-size": "16px !important;"}
                }

            new_df = AgGrid(
            df,
            gridOptions=gb,
            update_mode='MODEL_CHANGED',
            # fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            enableRangeSelection=True,
            custom_css=custom_css,
            height=400,
            enable_enterprise_modules=True)

            data = (datetime(int(mes[:4]), int(mes[5:7]), 1) + relativedelta(months=1) - relativedelta(days=1)).date()
            data_d5 = mutil.somar_dia_util(data, 5)
            ok = True
            senha = ''
            if mes == mes_atual and data_d5 > date.today():
                col1, _ = st.columns([1, 2])
                col1.error('Data inferior ao quinto dia útil')
                senha = col1.text_input('Informe a senha:')
                ok = False
            gerar = st.form_submit_button('Gerar Relatórios')
        
        if gerar:
            if ok == False and senha != 'vanguarda':
                col1, _ = st.columns([1, 3])
                col1.error('Senha incorreta!')
            if ok == True or senha == 'vanguarda':
                try:
                    if not new_df['selected_rows'] is None:
                        i =1
                        info_progresso = st.empty()
                        progress_bar = st.empty()
                        progress_bar.progress(0)
                        fundos = [{'nome': row['nome'].strip(), 'isin': row['isin'].strip()} for row in new_df['selected_rows']]
                        data = (datetime(int(mes[:4]), int(mes[5:7]), 1) + relativedelta(months=1) - relativedelta(days=1)).strftime('%Y-%m-%d')
                        erros, sucessos = 0, 0
                        fundos_erro = []
                        cwd = os.getcwd()
                        caminho_personalizados = os.path.join(cwd, 'assets', 'Relatórios', 'relatorios_personalizados')
                        shutil.rmtree(caminho_personalizados, ignore_errors=True)
                        os.makedirs(caminho_personalizados)

                        for fundo in fundos:
                            personalizado = False
                            for secao in secoes_completa:
                                if secao not in secoes:
                                    personalizado = True 
                            if marca_dagua:
                                personalizado = True
                            info_progresso.write(f"({i} de {len(fundos)}) Gerando Relatório do {fundo['nome']}. Aguarde...")
                            isin = fundo['isin']
                            r = requests.get(f'http://{env.IP}:{env.API_PORT}/gerar_relatorio_fundo/isin={isin}/data={data}', 
                                                json={'lista': lista_secoes, 
                                                    'marca_dagua': marca_dagua})
                            progress_bar.progress(i / len(fundos))
                            pasta = os.path.join(caminho_rede, mes.replace('/', '-'))
                            if not os.path.exists(pasta):
                                os.makedirs(pasta)
                            if r.status_code == 200:
                                sucessos +=1
                                arquivo = f"{'relatorio-'+mes.replace('/', '')}-{isin}-{fundo['nome']}.pdf"
                                with open(os.path.join(caminho_personalizados, arquivo), 'wb') as f:
                                    f.write(r.content)
                                if not personalizado:
                                    caminho = os.path.join(pasta, arquivo)
                                    with open(caminho, 'wb') as f:
                                        f.write(r.content)
                            else:
                                erros+=1
                                fundos_erro.append(fundo["nome"])
                            info_progresso.empty()
                            i+=1
                        progress_bar.empty()
                        col1, _ = st.columns([1, 4])
                        if erros > 0 and sucessos > 0:
                            col1.warning(f'{sucessos} de {len(fundos)} relatórios foram gerados.')
                            col1.write('Houve erro nos seguintes fundos:')
                            for fundo in fundos_erro:
                                st.markdown(f'- {fundo}')
                        if erros == 0 and sucessos > 0:
                            col1.success('Relatórios gerados com sucesso!')
                        if erros > 0 and sucessos == 0:
                            col1.error('Houve um erro na geração dos relatórios!')

                        arquivos = listdir(caminho_personalizados)
                        with zipfile.ZipFile("relatorio.zip", 'w') as zipMe:
                            for arquivo in arquivos:
                                zipMe.write(os.path.join(caminho_personalizados, arquivo), arquivo)

                        with open("relatorio.zip", 'rb') as f:
                            data = f.read()
                            btn = st.download_button(
                                label="Download",
                                data=data,
                                file_name="relatorio.zip",
                                mime="zip"
                            )
                        os.remove("relatorio.zip")

                except Exception as erro:
                    print(erro)
                    st.caption('Houve um erro')
