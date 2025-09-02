import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode
import pandas as pd
from datetime import datetime, date
import requests
from environment import *
import os 
from os import listdir
from dateutil.relativedelta import relativedelta
import zipfile


def laminas(barra, db, notion_controller):
    st.title('Lâminas Mensais')
    consultar, gerar = st.tabs(["Consultar", "Gerar"])

    caminho_rede = os.path.join(r"\\ISMTZVANGUARDA", 
                                'Dir-GestaodeAtivos$', 
                                'Mesa Renda Fixa', 
                                '1. Gestão Crédito', 
                                'Banco de Dados', 
                                'Lâminas Mensais')

    with consultar:
        meses = listdir(caminho_rede)
        meses = [i.replace('-', '/') for i in meses] if meses else [(date.today() + relativedelta(months=-1)).strftime('%Y/%m')]
        meses = sorted(meses, reverse=True)
        col1, col2 =  st.columns([1, 4])
        mes = col1.selectbox('Mês', meses)
        atualizar = st.button('Atualizar')
        form = st.empty()
        with form.form('sdf'):
            st.subheader('Consultar Lâminas')
            new_df = None
            if listdir(os.path.join(caminho_rede)):
                if [i for i in listdir(os.path.join(caminho_rede, mes.replace('/', '-'))) if i.startswith('lamina')]:
                    st.write('Escolha os fundos')
                    fundos = [ i[14:26] for i in listdir(os.path.join(caminho_rede, mes.replace('/', '-')))]
                    fundos = ','.join([f"'{cnpj}'" for cnpj in fundos])
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
                    st.write('Não há lâminas para o mês selecionado')
            else:
                st.write('Não há lâminas para o mês selecionado')
            download =st.form_submit_button('Gerar ZIP das lâminas')
        
        if download:
            if new_df:
                with st.spinner('Aguarde...'):
                    arquivos = [f"{'lamina-'+mes.replace('/', '')}-{i['isin']}-{i['nome']}.pdf" for i in new_df['selected_rows']]
                    with zipfile.ZipFile("laminas.zip", 'w') as zipMe:
                        for arquivo in arquivos:
                            zipMe.write(os.path.join(caminho_rede, mes.replace('/', '-'), arquivo), arquivo)

                    with open("laminas.zip", 'rb') as f:
                        data = f.read()
                        btn = st.download_button(
                            label="Download",
                            data=data,
                            file_name="laminas.zip",
                            mime="zip"
                        )
                    os.remove("laminas.zip")

    with gerar:
        with st.form('we'):
            st.subheader('Gerar Lâminas')
            col1, _ =  st.columns([1, 4])
            mes_atual = (date.today() + relativedelta(months=-1)).strftime('%Y/%m')
            mes_anterior = (date.today() + relativedelta(months=-2)).strftime('%Y/%m')
            dois_meses_atras = (date.today() + relativedelta(months=-3)).strftime('%Y/%m')
            mes = col1.selectbox('Mês', [mes_atual, mes_anterior, dois_meses_atras])
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
                                       where tipo_lamina is not null
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

            gerar =st.form_submit_button('Gerar lâminas')
            
        if gerar:
            try:
                i =1
                info_progresso = st.empty()
                progress_bar = st.empty()
                progress_bar.progress(0)
                data = (datetime(int(mes[:4]), int(mes[5:7]), 1) + relativedelta(months=1) - relativedelta(days=1)).strftime('%Y-%m-%d')
                fundos = [i for i in new_df['selected_rows']]
                erros, sucessos = 0, 0
                fundos_erro = []
                for fundo in fundos:
                    info_progresso.write(f"({i} de {len(fundos)}) Gerando lâmina do {fundo['nome']}. Aguarde...")
                    isin = fundo['isin']
                    r = requests.get(f'http://{env.IP}:{env.API_PORT}/gerar_lamina/isin={isin}/data={data}')
                    progress_bar.progress(i / len(fundos))
                    pasta = os.path.join(caminho_rede, mes.replace('/', '-'))
                    if not os.path.exists(pasta):
                        os.makedirs(pasta)
                    if r.status_code == 200:
                        sucessos +=1
                        caminho = os.path.join(pasta, f"{'lamina-'+mes.replace('/', '')}-{isin}-{fundo['nome']}.pdf")
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
                    col1.warning(f'{sucessos} de {len(fundos)} lâminas foram geradas.')
                    col1.write('Houve erro nos seguintes fundos:')
                    for fundo in fundos_erro:
                        st.markdown(f'- {fundo}')
                if erros == 0 and sucessos > 0:
                    col1.success('Lâminas geradas com sucesso!')
                if erros > 0 and sucessos == 0:
                    col1.error('Houve um erro na geração das lâminas!')

            except Exception as erro:
                print(erro)
                st.caption('Houve um erro')
