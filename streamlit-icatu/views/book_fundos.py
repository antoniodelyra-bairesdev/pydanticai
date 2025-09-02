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

def book_fundos(barra, db):
    st.title('Book de Fundos')

    st.subheader('Gerar Book de Fundos')

    with st.form('we'):
        col1, _ =  st.columns([1, 4])
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

        data = date(date.today().year, date.today().month, 1) - relativedelta(days=1)
        data_d5 = mutil.somar_dia_util(data, 2)
        ok = True
        senha = ''
        if data_d5 > date.today():
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
                with st.spinner('Aguarde...'):
                    if not new_df['selected_rows'] is None:
                        fundos = [row['isin'].strip() for row in new_df['selected_rows']]
                        cwd = os.getcwd()
                        caminho_personalizados = os.path.join(cwd, 
                                                            'assets', 
                                                            'Relatórios', 
                                                            'book_fundos')
                        shutil.rmtree(caminho_personalizados, ignore_errors=True)
                        os.makedirs(caminho_personalizados)

                        r = requests.get(f'http://{env.IP}:{env.API_PORT}/gerar_book_fundos/data={data}', 
                                            json={'lista': fundos})

                        if r.status_code == 200:
                            arquivo = f"{'book_fundos_'}{data.strftime('%Y-%m')}.pdf"
                            with open(os.path.join(caminho_personalizados, arquivo), 'wb') as f:
                                f.write(r.content)

                        with open(os.path.join(caminho_personalizados, arquivo), 'rb') as f:
                            data = f.read()
                            btn = st.download_button(
                                label="Download",
                                data=data,
                                file_name=arquivo,
                                mime="pdf"
                            )

            except Exception as erro:
                print(erro)
                st.caption('Houve um erro')
