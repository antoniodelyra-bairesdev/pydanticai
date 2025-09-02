import streamlit as st
from os import listdir
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
import os
import base64
import zipfile
import io 
import xlsxwriter


def try_error(func):
    def wrapper(barra, database, notion_controller):
        try:
            return func(barra, database, notion_controller)
        except Exception as erro:
            print(erro)
            st.caption('Houve um erro.')
    return wrapper

@try_error
def assembleias(barra, db, notion_controller):
    st.title('Assembleias')

    caminho_rede = os.path.join(r'\\ISMTZVANGUARDA', 
                                'Dir-GestaodeAtivos$', 
                                'Mesa Renda Fixa', 
                                '1. Gestão Crédito', 
                                'Banco de Dados', 
                                'Assembleias')
    caminho_rede = caminho_rede.lstrip('\\')
    caminho_rede = r'\\?\UNC\{}'.format(caminho_rede)

    meses = [f"{i[11:15]}/{i[16:18]}" for i in listdir(caminho_rede) if i.startswith('Assembleia_')]
    meses = list(set(meses))
    meses.sort(reverse=True)

    col1, _ = st.columns([1, 5])
    mes = col1.selectbox('Mês', meses)
    consolidado, por_fundo = st.tabs(['Consolidado', 'Por Fundo'])
    with por_fundo:
        with st.spinner('Aguarde...'):
            dados_fundos= db.query('''select 
                                    nome, codigo_brit, cnpj 
                                   from icatu.fundos 
                                   where id_risco is not null
                                   order by nome''')
            fundos = {i['nome'] : {
                            'cnpj': i['cnpj'], 
                            'codigo_brit' : i['codigo_brit']} 
                    for i in dados_fundos}
            col1, _ = st.columns([1, 2])
            fundo = col1.selectbox('Selecione o fundo:', [i for i in fundos])
            fundo_escolhido = fundos[fundo]['cnpj']
            arquivo_zip = os.path.join(caminho_rede, f"Assembleias_{mes.replace('/', '-')}.zip")
            archive = zipfile.ZipFile(arquivo_zip, 'r')
            excel = archive.open('Assembleias_Período.xlsx') 
            df = pd.read_excel(excel, sheet_name='Fundos', dtype={'CNPJ': str})
            df = df[df['CNPJ']==fundo_escolhido].reset_index()
            df = df[['CNPJ', 
                    'Data', 
                    'Emissor', 
                    'Código', 
                    'Emissão', 
                    'Série', 
                    'Representante', 
                    '% Fundo',
                    'Agente Fiduciário',	
                    'Quórum',	
                    'Ordem do Dia',	
                    'Contrapartida',	
                    'Voto Vanguarda',	
                    'Decisão'
                    ]]
            
            excel_buffer = io.BytesIO()
            workbook = xlsxwriter.Workbook(excel_buffer, {'nan_inf_to_errors': True})
            worksheet = workbook.add_worksheet('Controle')
            date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'align': 'center'})
            percent_format = workbook.add_format({'num_format': '0.00%', 'align': 'center'})
            cell_format = workbook.add_format({'align': 'left'})

            for col_idx, col_name in enumerate(df.columns):
                worksheet.write(0, col_idx, col_name)

            for col_idx, column in enumerate(df.columns):
                for row_idx, row in df[column].items():
                    row = '' if pd.isna(row) else row
                    excel_row = row_idx + 1  
                    if column == 'Data':
                        worksheet.set_column(col_idx, col_idx, 13)
                        worksheet.write_datetime(excel_row, col_idx, row, date_format) 
                    elif column == '% Fundo':
                         worksheet.set_column(col_idx, col_idx, 13)
                         worksheet.write(excel_row, col_idx, row, percent_format) 
                    elif column == 'CNPJ':
                         worksheet.set_column(col_idx, col_idx, 16)
                         worksheet.write(excel_row, col_idx, row, cell_format) 
                    elif column in ['Emissão', 'Série']:
                         worksheet.set_column(col_idx, col_idx, 8)
                         worksheet.write(excel_row, col_idx, row, cell_format) 
                    else:
                        worksheet.set_column(col_idx, col_idx, 20)
                        worksheet.write(excel_row, col_idx, row, cell_format) 

            workbook.close()
            excel_buffer.seek(0)

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for ind, row in df.iterrows():
                    emissor = row['Emissor'].replace(' ', '-')
                    pasta = f"Assembleia_{row.Data.strftime('%Y-%m-%d')}_{emissor}{f'({row.Código})'}"
                    caminho = os.path.join(caminho_rede, pasta)
                    arquivos = [i for i in listdir(caminho) if pasta not in i and i != 'Fundos']
                    arquivo_assembleia = f'{pasta}_Fundo_{row.CNPJ}.pdf'
                    zip_file.write(os.path.join(caminho, 'Fundos', arquivo_assembleia), 
                                   os.path.join(pasta, arquivo_assembleia))
                    for arquivo in arquivos:
                        zip_file.write(os.path.join(caminho, arquivo), os.path.join(pasta, arquivo))
                zip_file.writestr("Assembleias_Período.xlsx", excel_buffer.read())

            zip_buffer.seek(0)

            btn = st.download_button(
                label="Download ZIP",
                data=zip_buffer,
                file_name=f"Assembleias_{mes.replace('/', '-')}_Fundo_{fundo_escolhido}.zip",
                mime="application/zip"
            )

            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_grid_options(enableRangeSelection=True)
            gb.configure_grid_options(enableCellTextSelection=True)
            gb.configure_selection('single', use_checkbox=True)

            gb = gb.build()
            gb['columnDefs'] = [
                {'field': 'CNPJ', 
                 'minWidth': 190,
                 'maxWidth': 190,
                  "checkboxSelection": True
                },
                {
                    'field': 'Data', 
                    'minWidth': 120,
                    'maxWidth': 120,
                    'type': ["dateColumnFilter", "customDateTimeFormat"], 
                    'custom_format_string': 'dd/MM/yyyy'
                },
               {'field': 'Emissor','minWidth': 200, },
               {'field': 'Código','minWidth': 100, },
               {'field': 'Emissão','minWidth': 100, 'maxWidth': 100, },
               {'field': 'Série','minWidth': 100, 'maxWidth': 100, },
               {'field': 'Representante','minWidth': 200, },
                {
                    'field': '% Fundo',
                    'minWidth': 110,
                    'maxWidth': 110,
                    'valueFormatter': "(value*100).toLocaleString('pt-BR',{minimumFractionDigits: 2}) + '%'", 'suppressMenu': True,
                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                }
                ]


            
            custom_css = {
                ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                ".ag-header-cell":{"background-color": "#0D6696 !important","color": "white"},
                ".ag-row":  {  "font-size": "16px !important;"}
                }
            new_df = AgGrid(
                df,
                gridOptions=gb,
                update_mode='MODEL_CHANGED',
                allow_unsafe_jscode=True,
                enableRangeSelection=True,
                custom_css=custom_css,
                height=min(30 + 45 * len(df.index), 400),
                enable_enterprise_modules=True)

            with st.spinner('Aguarde...'):
                if new_df['selected_rows']:
                    linha = new_df['selected_rows']
                    nome = linha[0]['Emissor'].replace(' ', '-') + "("  + linha[0]['Código']+')'
                    nome_pasta = f"Assembleia_{linha[0]['Data'][:10]}_{nome}"
                    if nome_pasta[-1] == ".":
                        nome_pasta = nome_pasta[:-1]
                    caminho_fundos = os.path.join(caminho_rede, nome_pasta,  'Fundos')
                    with open(os.path.join(caminho_fundos, f"{nome_pasta}_Fundo_{fundo_escolhido}.pdf"), 'rb') as pdf_file:
                        base64_pdf = base64.b64encode(
                            pdf_file.read()).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000px" height="800px" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)


    with consolidado:
        with st.spinner('Aguarde...'):
            arquivo_zip = os.path.join(caminho_rede, f"Assembleias_{mes.replace('/', '-')}.zip")
            with open(arquivo_zip, "rb") as fp:
                btn = st.download_button(
                    label="Download ZIP",
                    data=fp,
                    file_name=f"Assembleias_{mes.replace('/', '-')}.zip",
                    mime="application/zip"
                )
            df = pd.read_excel(os.path.join(caminho_rede, 'Assembleias Controle.xlsx'))
            df['mes'] = df.apply(lambda x: x['Data'].strftime('%Y/%m'), axis=1)
            df = df[df['mes'] == mes]
            df['Emissor'] = df['Emissor'].apply(lambda x: x.split('(')[0])

            gb = GridOptionsBuilder.from_dataframe(
                df[['Data', 
                    'Emissor', 
                    'Código', 
                    'Emissão', 
                    'Série', 
                    'Representante', 
                    '% Vanguarda', 
                    'Agente Fiduciário']])
            gb.configure_grid_options(enableRangeSelection=True)
            gb.configure_grid_options(enableCellTextSelection=True)
            gb.configure_selection('single', use_checkbox=True)
            gb = gb.build()
            gb['columnDefs'] = [
                {
                    'field': 'Data',
                    'minWidth': 140,
                    'maxWidth': 140, 
                    'type': ["dateColumnFilter", "customDateTimeFormat"], 
                    'custom_format_string': 'dd/MM/yyyy',
                    "checkboxSelection": True
                },
               {'field': 'Emissor','minWidth': 200 },
               {'field': 'Código' ,'minWidth': 100 },
               {'field': 'Emissão','minWidth': 100, 'maxWidth': 100, },
               {'field': 'Série','minWidth': 100, 'maxWidth': 100, },
               {'field': 'Representante','minWidth': 200 },
                {
                    'field': '% Vanguarda',
                    'minWidth': 130,
                    'maxWidth': 130,
                    'valueFormatter': "(value*100).toLocaleString('pt-BR',{minimumFractionDigits: 2}) + '%'", 'suppressMenu': True,
                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                },
                {'field': 'Agente Fiduciário','minWidth': 200 }
                ]
            custom_css = {
                ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                ".ag-header-cell":{"background-color": "#0D6696 !important","color": "white"},
                ".ag-row":  {  "font-size": "16px !important;"}
                }
            new_df = AgGrid(
                df,
                gridOptions=gb,
                update_mode='SELECTION_CHANGED',
                fit_columns_on_grid_load=False,
                allow_unsafe_jscode=True,
                enableRangeSelection=True,
                custom_css=custom_css,
                height=min(30 + 45 * len(df.index), 400),
                enable_enterprise_modules=True)

            with st.spinner('Aguarde...'):
                if new_df['selected_rows']:
                    linha = new_df['selected_rows']
                    nome = linha[0]['Emissor'].replace(' ', '-') + "("  + linha[0]['Código']+')'
                    arquivo = f"Assembleia_{linha[0]['Data'][:10]}_{nome}"
                    if arquivo[-1] == ".":
                        arquivo = arquivo[:-1]
                    with open(os.path.join(caminho_rede, arquivo, f"{arquivo}.pdf"), 'rb') as pdf_file:
                        base64_pdf = base64.b64encode(
                            pdf_file.read()).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000px" height="800px" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
