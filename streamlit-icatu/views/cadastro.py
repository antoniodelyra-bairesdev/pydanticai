from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit as st
import pandas as pd
import unidecode
import views.util as util
import models.util as mutil
import models.automacao as automacao
import unidecode
import math
import re
import zipfile
import shutil
import os
import base64
from os import listdir
from environment import *


def banco_dados(database, barra):
    with barra:
        opcao = st.radio('Selecione uma ferramenta', [
            'Ativos',
            'Fundos',
            'PL de Emissores/Grupos',
            'Ratings',
            'Arquivos'
        ])

    if opcao == 'Fundos':
        st.title("Cadastro de fundos")
        cadastrar_fundo(database, barra)
        tabela_fundos(database, barra)

    if opcao == 'Ativos':
        st.title("Cadastro de ativos")
        tab1, tab2, tab3 = st.tabs(
            ["Cadastrar ativo", 'Importar Excel', "Lista de ativos"])

        with tab1:
            incluir_ativo(database, barra)
        with tab2:
            importar_excel(database, barra)
        with tab3:
            if st.button("Carregar listas"):
                tabela_ativos(database, barra)
                tabela_fluxo(database, barra)

    if opcao == 'PL de Emissores/Grupos':
        pl_grupos_emissores(database, barra)

    if opcao == 'Ratings':
        ratings(database, barra)

    if opcao == 'Arquivos':
        upload_arquivos(database, barra)


@st.cache_resource(show_spinner=False)
def query_db(_database, query):
    return _database.query(query)



def try_error(func):
    def wrapper(database, barra):
        try:
            return func(database, barra)
        except Exception as erro:
            print(erro)
            st.caption('Houve um erro.')
    return wrapper

@try_error
def upload_arquivos(database, barra):
    st.title('Arquivos')
    tab1, tab2, tab3 = st.tabs(
        ["Consulta", "Upload de Arquivos", 'Excluir Arquivos'])
    caminho_rede = os.path.join(r"\\ISMTZVANGUARDA", 'Dir-GestaodeAtivos$', 'Mesa Renda Fixa', '1. Gestão Crédito', 'Banco de Dados', 'Arquivos Emissões')

    custom_css = {
        ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
        ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
        '.ag-header-group-cell': {"background-color": "#2E96BF","color": "white"},
        ".ag-row":  {  "font-size": "16px !important;"}
        }


    with tab1:
        st.subheader('Consultar Arquivos')
        with st.form('lkdfg'):
            col1, col2, _ = st.columns([1, 1, 2])
            emissao = col1.selectbox('Emissão', [i['codigo'] for i in query_db(
                database, 'select codigo from icatu.info_papeis order by codigo')])
            consulta = st.form_submit_button('Consultar')

        if consulta or ('consulta' in st.session_state and st.session_state['consulta'] == True):
            st.session_state['consulta'] = True
            pasta = os.path.join(caminho_rede, emissao)
            arquivos = []
            for dirpath, dirnames, files in os.walk(pasta):
                arquivos += files

            if not arquivos:
                col1, _ = st.columns([1, 2])
                col1.info('Não há documentos para a emissão selecionada')
            else:
                dados = []
                for tipo in listdir(pasta):
                    for arquivo in listdir(os.path.join(pasta, tipo)):
                        dados.append(
                            {'Emissão': emissao, 'Tipo': tipo, 'Nome do Arquivo': arquivo})
                df = pd.DataFrame(dados)
                with st.form('pgh'):
                    gb = GridOptionsBuilder.from_dataframe(df)
                    gb.configure_grid_options(
                        enableRangeSelection=True, tooltipShowDelay=0)
                    gb.configure_grid_options(enableCellTextSelection=True)
                    gb.configure_selection('multiple', use_checkbox=True)
                    gb = gb.build()

                    gb['columnDefs'] = [
                        {'field': 'Emissão', 'maxWidth': 200,
                            "checkboxSelection": True, 'headerCheckboxSelection': True, },
                        {'field': 'Tipo', 'maxWidth': 400, },
                        {'field': 'Nome do Arquivo', },
                    ]

                    new_df = AgGrid(
                        df,
                        gridOptions=gb,
                        fit_columns_on_grid_load=True,
                        update_mode='MODEL_CHANGED',
                        custom_css=custom_css,
                        allow_unsafe_jscode=True,
                        enable_enterprise_modules=True)
                    st.subheader(
                        'Selecione os arquivos que deseja baixar e clique em Download.')
                    download = st.form_submit_button('Download')

                if download:
                    new_df = new_df['selected_rows']
                    arquivos = [i for i in new_df['Nome do Arquivo']]
                    pasta = os.path.join(caminho_rede, emissao)
                    if not new_df is None:
                        with zipfile.ZipFile(os.path.join(caminho_rede, "download.zip"), 'w') as zipMe:
                            for tipo in listdir(pasta):
                                pasta_tipo = os.path.join(pasta, tipo)
                                for arquivo in listdir(pasta_tipo):
                                    if arquivo in arquivos:
                                        zipMe.write(os.path.join(
                                            pasta_tipo, arquivo), os.path.join(tipo, arquivo))

                        with open(os.path.join(caminho_rede, "download.zip"), 'rb') as file_data:
                            bytes_content = file_data.read()
                        st.download_button(
                            label="Download ZIP",
                            data=bytes_content,
                            file_name=emissao+'.zip',
                            mime="zip"
                        )

    with tab2:
        st.subheader('Upload de Arquivos')
        with st.form('23445', clear_on_submit=True):
            col1, col2, _ = st.columns([1, 1, 2])
            emissao = col1.selectbox('Emissão', [i['codigo'] for i in query_db(
                database, 'select codigo from icatu.info_papeis order by codigo')])
            tipos = ['Cadastro', 'Escritura', 'Termo de Securitização',
                     'Garantias', 'Tela Cetip', 'Apresentação', 'Rating Externo']
            tipo = col2.selectbox('Tipo', tipos)
            col1, _ = st.columns([1, 2])
            files = col1.file_uploader(
                'Selecione os arquivos', accept_multiple_files=True)
            limpar = st.form_submit_button('Atualizar/Limpar')

        if limpar:
            pass

        dados, categorias = [], {}
        for file in files:
            dados.append(
                {'Emissão': emissao, 'Nome do Arquivo': file.name, 'Tipo': tipo})

        with st.form('213', clear_on_submit=True):
            df = pd.DataFrame(dados)
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_grid_options(
                enableRangeSelection=True, tooltipShowDelay=0)
            gb.configure_grid_options(enableCellTextSelection=True)
            gb = gb.build()

            gb['columnDefs'] = [
                {'field': 'Emissão', 'maxWidth': 200},
                {'field': 'Nome do Arquivo', 'maxWidth': 800, },
                {'field': 'Tipo', 'editable': True,
                 'cellStyle': {'background-color': 'rgb(236, 240, 241)'},
                 'cellEditor': 'agRichSelectCellEditor',
                 'cellEditorParams': {'values': tipos},
                 'cellEditorPopup': True},
            ]

            new_df = AgGrid(
                df,
                gridOptions=gb,
                fit_columns_on_grid_load=True,
                update_mode='MODEL_CHANGED',
                custom_css=custom_css,
                allow_unsafe_jscode=True,
                enable_enterprise_modules=True)
            st.subheader('Emissão: '+emissao +
                         '. Está correta? Se sim, clique em Salvar Arquivos.')
            salvar = st.form_submit_button('Salvar Arquivos')

        if salvar and files:
            with st.spinner('Aguarde...'):
                for ind, row in new_df['data'].iterrows():
                    categorias[row['Nome do Arquivo']] = row['Tipo']
                for file in files:
                    categoria = categorias[file.name]
                    pasta = os.path.join(caminho_rede, emissao, categoria)
                    if not os.path.exists(pasta):
                        os.makedirs(pasta)
                    with open(os.path.join(pasta, file.name), mode='wb') as w:
                        w.write(file.getvalue())
                col1, _ = st.columns([1, 4])
                col1.success('Arquivos salvos com sucesso!')

    with tab3:
        st.subheader('Excluir Arquivos')
        with st.form('fsdf'):
            col1, col2, _ = st.columns([1, 1, 2])
            emissao = col1.selectbox('Emissão', [i['codigo'] for i in query_db(
                database, 'select codigo from icatu.info_papeis order by codigo')])
            consulta = st.form_submit_button('Consultar')

        if consulta or ('consulta' in st.session_state and st.session_state['consulta'] == True):
            st.session_state['consulta'] = True
            pasta = os.path.join(caminho_rede, emissao)
            arquivos = []
            for dirpath, dirnames, files in os.walk(pasta):
                arquivos += files

            if not arquivos:
                col1, _ = st.columns([1, 2])
                col1.info('Não há documentos para a emissão selecionada')
            else:
                dados = []
                for tipo in listdir(pasta):
                    for arquivo in listdir(os.path.join(pasta, tipo)):
                        dados.append(
                            {'Emissão': emissao, 'Tipo': tipo, 'Nome do Arquivo': arquivo})
                df = pd.DataFrame(dados)
                with st.form('ghjgh'):
                    gb = GridOptionsBuilder.from_dataframe(df)
                    gb.configure_grid_options(
                        enableRangeSelection=True, tooltipShowDelay=0)
                    gb.configure_grid_options(enableCellTextSelection=True)
                    gb.configure_selection('single', use_checkbox=True)
                    gb = gb.build()

                    gb['columnDefs'] = [
                        {'field': 'Emissão', 'maxWidth': 200,
                            "checkboxSelection": True, 'headerCheckboxSelection': True, },
                        {'field': 'Tipo', 'maxWidth': 400, },
                        {'field': 'Nome do Arquivo', 'maxWidth': 800, },
                    ]

                    new_df = AgGrid(
                        df,
                        gridOptions=gb,
                        fit_columns_on_grid_load=True,
                        update_mode='MODEL_CHANGED',
                        custom_css=custom_css,
                        allow_unsafe_jscode=True,
                        enable_enterprise_modules=True)

                    st.subheader(
                        'Tem certeza que deseja excluir o arquivo? Se sim, clique em Apagar Arquivo.')
                    apagar = st.form_submit_button('Apagar arquivo')

                lixeira = os.path.join(caminho_rede, 'Lixeira')
                if apagar:
                    new_df = new_df['selected_rows']
                    if not new_df is None:
                        tipo = new_df['Tipo'][0]
                        arquivo = new_df['Nome do Arquivo'][0]
                        shutil.move(os.path.join(pasta, tipo, arquivo),
                                    os.path.join(lixeira, arquivo))
                        col1, _ = st.columns([1, 4])
                        col1.success('Arquivo excluído com sucesso')

@try_error
def cadastrar_fundo(database, barra):
    with st.form("key"):
        col1, col2, col3 = st.columns([1, 1, 3])
        isin = col1.text_input('ISIN')
        isin = re.sub(r'\W+', '', isin)
        cnpj = col2.text_input("CNPJ")
        cnpj = re.sub(r'\W+', '', cnpj)
        nome = col3.text_input('Nome do Fundo')
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        codigo_brit = col1.text_input('Código Brit')
        codigo_brit = re.sub(r'\W+', '', codigo_brit)
        risco, custodiante_cnpj, classificao_fundos = {}, {}, {}
        for i in database.query_select("select * from icatu.risco_fundos"):
            risco[i[1]] = i[0]
        for i in database.query_select("select * from icatu.classificacao_fundos"):
            classificao_fundos[i[1]] = i[0]
        for i in database.query_select("select * from icatu.custodiantes"):
            custodiante_cnpj[i[2]] = i[0]
        id_risco = col2.selectbox('Nível de Risco', [
                                  i[0] for i in database.query_select("select nome from icatu.risco_fundos")])
        id_risco = risco[id_risco]
        classificacao = col3.selectbox('Classificação', [i[0] for i in database.query_select(
            "select nome from icatu.classificacao_fundos")])
        classificacao = classificao_fundos[classificacao]
        indice = col4.selectbox('Índice', ['CDI', 'TOTAL RETURN'])
        custodiante = col5.selectbox('Custodiante', [i[0] for i in database.query_select(
            "select nome_curto from icatu.custodiantes")])
        custodiante = custodiante_cnpj[custodiante]
        cadastrar = st.form_submit_button('Cadastrar')
    if cadastrar and isin and cnpj and nome and codigo_brit:
        database.add_fundos([(isin, nome, codigo_brit, cnpj, None,
                            id_risco, classificacao, custodiante, None, indice)])
        col1, _ = st.columns([1, 4])
        st.cache_resource.clear()
        col1.success('Fundo cadastrado com sucesso.')
    elif cadastrar and not (isin and cnpj and nome and codigo_brit):
        st.caption("Preencha os dados corretamente.")

@try_error
def tabela_fundos(database, barra):
    st.subheader("Lista de fundos")
    if st.button("Atualizar lista"):
        st.experimental_rerun()

    custom_css = {
        ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
        ".ag-header-cell":{"background-color": "#0D6696 !important","color": "white"},
        '.ag-header-group-cell':{"background-color": "#2E96BF","color": "white"},
        ".ag-row":  {  "font-size": "16px !important;"}
        }
    
    dados = database.query_select('''select isin, codigo_brit, f.cnpj, f.nome, indice, c.nome, r.nome, ct.nome_curto
                                    from icatu.fundos f
                                    left join icatu.classificacao_fundos c on c.id = f.id_classificacao
                                    left join icatu.risco_fundos r on r.id = f.id_risco
                                    left join icatu.custodiantes ct on ct.cnpj = f.custodiante
                                    where f.id_risco is not null
                                    order by f.atualizacao desc''')

    df = pd.DataFrame(dados, columns=['ISIN', 'Código BRIT', 'CNPJ',
                      'Nome do Fundo', 'Índice', 'Classificação', 'Risco', 'Custodiante'])
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_grid_options(enableRangeSelection=True, tooltipShowDelay=0)
    gb.configure_grid_options(enableCellTextSelection=True)
    new_df = AgGrid(
        df,
        gridOptions=gb.build(),
        fit_columns_on_grid_load=True,
        update_mode='NO_UPDATE',
        custom_css=custom_css,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True)

@try_error
def importar_excel(database, barra):
    st.write("Preencha a planilha modelo para importação manual")
    with open(r"assets\cadastro_ativos.xlsx", "rb") as file:
        btn = st.download_button(
            label="Download da planilha modelo",
            data=file,
            file_name="cadastrar_ativo.xlsx",
            mime="application/vnd.ms-excel"
        )

    with st.spinner('Aguarde...'):
        uploaded_file = st.file_uploader("Importar arquivo preenchido")
        try:
            if uploaded_file is not None:

                df_pagamentos = pd.read_excel(
                    uploaded_file, sheet_name='Pagamentos')
                df_pagamentos.sort_values(
                    ['Código do ativo', 'Data Evento', 'Tipo do Evento'])

                df_info = pd.read_excel(
                    uploaded_file, sheet_name='Informações')
                df_info = df_info[df_info['Tipo de ativo'].isin(
                    ['Debênture', 'Letra Financeira', 'FIDC', 'CRI', 'BOND', 'NC', 'CDB', 'DPGE', 'FII', 'RDB', 'Fundo Listado'])]
                df_info = df_info.drop(df_info.columns[14:], axis=1)

                df_visualizacao = df_info.copy(deep=False)
                df_visualizacao['CNPJ'] = df_visualizacao['CNPJ'].apply(lambda x: re.sub(
                    r'\W+', '', '0' * (14-len(str(x).split('.')[0])) + str(x).split('.')[0]))
                df_visualizacao['Percentual'] = df_visualizacao['Percentual'].apply(
                    lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                df_visualizacao['Juros'] = df_visualizacao['Juros'].apply(
                    lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                df_visualizacao['Data da Emissão'] = pd.to_datetime(
                    df_visualizacao['Data da Emissão'], errors='coerce').dt.strftime("%d/%m/%Y")
                df_visualizacao['Data de Vencimento'] = pd.to_datetime(
                    df_visualizacao['Data de Vencimento'], errors='coerce').dt.strftime("%d/%m/%Y")
                df_visualizacao['Início da rentabilidade'] = pd.to_datetime(
                    df_visualizacao['Início da rentabilidade'], errors='coerce').dt.strftime("%d/%m/%Y")
                df_visualizacao['Valor da Emissão'] = df_visualizacao['Valor da Emissão'].apply(
                    lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                df_visualizacao['Emissão'] = df_visualizacao['Emissão'].apply(
                    lambda x: "{:,.0f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                df_visualizacao['Série'] = df_visualizacao['Série'].apply(
                    lambda x: "{:,.0f}".format(x) if str(x).replace(".", "").isdigit() else x)

                df_consolidado = df_pagamentos.groupby(['Código do ativo'])
                df_consolidado = df_consolidado.size().to_frame(name='Eventos')
                df_consolidado.reset_index(inplace=True)
                df_visualizacao = pd.concat([df_visualizacao.set_index('Código do ativo'), df_consolidado.set_index(
                    'Código do ativo')], axis=1, join='inner').reset_index()

                hide_table_row_index = """
                            <style>
                            thead tr th:first-child {display:none}
                            tbody th {display:none}
                            </style>
                            """
                st.markdown(hide_table_row_index, unsafe_allow_html=True)
                st.table(df_visualizacao)

                df_pagamentos = df_pagamentos[df_pagamentos['Código do ativo'].isin(
                    df_visualizacao['Código do ativo'].unique())]
                df_info = df_info[df_info['Código do ativo'].isin(
                    df_visualizacao['Código do ativo'].unique())]

                cadastrar = st.button('Cadastrar ativos')
                if cadastrar:

                    dados_pagamentos, dados_info, atualizacao, lista_eventos, eventos, saldo_devedor = [
                    ], [], datetime.now(), database.tipo_eventos(), {}, {}
                    for tipo in lista_eventos:
                        eventos[tipo[2]] = tipo[0]

                    for ind, row in df_pagamentos.iterrows():
                        codigo = re.sub(
                            r'\W+', '', row['Código do ativo'].strip())
                        if codigo not in saldo_devedor:
                            saldo_devedor[codigo] = 100
                        data_evento = util.validar_data(row['Data Evento'])
                        data_pagamento = mutil.get_dia_util(data_evento)
                        tipo = eventos[unidecode.unidecode(
                            row['Tipo do Evento'].lower().replace(" ", ""))]
                        percentual_absoluto = float(row['Percentual']) if not math.isnan(
                            row['Percentual']) else None
                        if percentual_absoluto:
                            percentual_relativo = (
                                percentual_absoluto / saldo_devedor[codigo]) * 100
                            saldo_devedor[codigo] -= percentual_absoluto
                        else:
                            percentual_relativo = None
                        id = codigo + data_pagamento.strftime('%Y%m%d') + str(tipo)
                        dados_pagamentos.append(
                            (id, codigo, data_evento, data_pagamento, tipo, percentual_relativo, None, None, atualizacao, 'Manual'))

                    for ind, row in df_info.iterrows():
                        codigo = row['Código do ativo'].strip()
                        empresa = row['Empresa'].strip()
                        isin = re.sub(
                            r'\W+', '', str(row['ISIN'])) if re.sub(r'\W+', '', str(row['ISIN'])) else None
                        cnpj = re.sub(
                            r'\W+', '', '0' * (14-len(str(row['CNPJ']).split('.')[0])) + str(row['CNPJ']).split('.')[0])
                        cnpj = cnpj if cnpj else None
                        serie = "{:,.0f}".format(row['Série']) if str(
                            row['Série']).replace(".", "").isdigit() else row['Série']
                        emissao = row['Emissão'] if not math.isnan(
                            row['Emissão']) else None
                        inicio_rentabilidade = row['Início da rentabilidade']
                        valor_emissao = row['Valor da Emissão']
                        data_emissao = row['Data da Emissão']
                        data_vencimento = row['Data de Vencimento']
                        indice = row['Índice']
                        percentual = row['Percentual']
                        juros = row['Juros']
                        tipo_ativo = row['Tipo de ativo']

                        dados_info.append((codigo, empresa, isin, cnpj, serie, emissao, inicio_rentabilidade, valor_emissao, data_emissao,
                                           data_vencimento, indice, percentual, juros, None, None,
                                           None, atualizacao, tipo_ativo, 'Manual', None, None, None, None, None, None))
                        database.query_dml_simples(
                            f"delete from icatu.fluxo_papeis where codigo = '{codigo}'")

                    database.add_fluxo_eventos(dados_pagamentos)
                    database.add_info_papeis(dados_info)
                    col1, _ = st.columns([1, 3])
                    st.cache_resource.clear()
                    col1.success('Cadastro efetuado com sucesso')
        except:
            st.caption('Houve um erro')

# @try_error
def incluir_ativo(database, barra):
    with st.form("Gerar Fluxo"):
        col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 2, 2, 1, 0.8, 0.8])
        tipo_ativo = col1.selectbox('Tipo do Ativo*', 
                                    ('Debênture', 'Letra Financeira',
                                    'FIDC', 'CRI', 'BOND', 'NC', 'CDB',
                                      'DPGE', 'FII', 'RDB', 'Fundo Listado'))
        lista_codigos = col2.text_input('Código*').split()
        lista_codigos = set(lista_codigos)
        empresa = col3.text_input('Apelido')
        isin = col5.text_input('ISIN')
        emissor = {}
        for i in [i for i in database.query_select('select distinct empresa, cnpj from icatu.emissores order by empresa')]:
            emissor[i[0]] = i[1].strip()
        cnpj = col4.selectbox('Emissor*', [i[0].strip() for i in database.query_select(
            'select distinct empresa from icatu.emissores order by empresa')])
        serie = col6.text_input('Série')
        numero_emissao = col7.text_input('Emissão')

        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1, 1, 1, 1, 1, 1, 1])
        data_emissao = col1.date_input('Data de Emissão*', key='data_emissao')
        inicio_rentabilidade = col2.date_input('Início da Rentabilidade*', key='data_calculo')
        data_vencimento = col3.date_input('Data de Vencimento*', key='data_vencimento')
        valor_emissao = col4.number_input('Valor da Emissão*',  format="%.4f", key='valor_emissao')
        indice = col5.selectbox('Índice*', ('DI+', 'DI Percentual', 'IPCA+', 'IGP-M+', 'PRÉ'), key='indice')
        taxa_emissao = col6.number_input('Taxa de Emissão*',  format="%.4f", key='taxa_emissao')
        tipo_juros = col7.radio("Pagamento de juros",('Bullet', 'Periódico'), key='tipo_juros')
        tipo_amortizacao = col8.radio("Amortização", ('No vencimento', 'Periódica'), key='tipo_amortizacao')

        meses = mutil.dif_meses(data_emissao, data_vencimento)
        col1, col2, _, col3, col4 = st.columns([1, 4, 1, 1,1])
        pagamento_juros = col3.number_input('Juros (Meses)', min_value=1, step=1, key='pagamento_juros')
        pagamento_amortizacao = col4.number_input('Amortização (Meses)', min_value=1, step=1, key='pagamento_amortizacao')
        if not tipo_juros == 'Periódico':
            pagamento_juros = meses
        if not tipo_amortizacao == 'Periódica':
            pagamento_amortizacao = meses

        with col2.expander('Apenas LSFC e LFSN', expanded=False):
            ex1, ex2, ex3, ex4 = st.columns([1, 1, 1.5, 1])
            incluir_call = ex1.checkbox('Incluir', value= False, key='incluir')
            call_inicial = ex2.date_input('Primeira Call', key='data_call')
            periodo_call = ex3.selectbox('Periodicidade', ('Semestral', 'Anual', '180 Dias Corridos'), key='periodo_call')
            repeticoes_call = ex4.number_input('Repetições', min_value=1, step=1, max_value=10)

        verificar = True
        gerar_fluxo = col1.form_submit_button("Gerar Fluxo")
        if gerar_fluxo:
            st.session_state['fluxo'] = True
        if not (valor_emissao and taxa_emissao and lista_codigos):
            verificar = False
            st.caption("Preencha os dados corretamente.")

    if gerar_fluxo and verificar or ('fluxo' in st.session_state and st.session_state['fluxo'] and verificar):
        cnpj = emissor[cnpj]
        cnpj = re.sub(r'\W+', '', cnpj)
        empresa = None if empresa == '' else empresa
        fluxo = []
        data_amortizacao, data_juros, saldo, cont_juros = data_emissao, data_emissao, 100, 1
        if meses == 0:
            amort, pagamento_amortizacao, pagamento_juros, divisao_juros = 100, 1, 1, 1
        else:
            divisao_amort = mutil.truncar((meses/pagamento_amortizacao), 0)
            divisao_juros = mutil.truncar((meses/pagamento_juros), 0)
            if divisao_amort == 0:
                amort = 100
            else:
                amort = 100 / divisao_amort
                saldo -= amort
            if divisao_juros == 0:
                divisao_juros = 1

        while data_amortizacao < data_vencimento and data_juros < data_vencimento:
            ref_amort = data_amortizacao + relativedelta(months=pagamento_amortizacao)
            ref_juros = data_juros + relativedelta(months=pagamento_juros)
            if ref_amort < ref_juros:
                data_amortizacao = ref_amort
                if data_amortizacao < data_vencimento and saldo > 0:
                    fluxo.append({'Data do Evento': data_amortizacao,
                                 'Percentual': amort, 'Tipo do Evento': 'Amortização'})
                    saldo -= amort
            elif ref_amort > ref_juros:
                data_juros = ref_juros
                if data_juros < data_vencimento and cont_juros < divisao_juros:
                    fluxo.append({'Data do Evento': data_juros,
                                 'Percentual': None, 'Tipo do Evento': 'Juros'})
                    cont_juros += 1
            else:
                data_amortizacao = ref_amort
                data_juros = ref_juros
                if amort < 100:
                    if data_juros < data_vencimento and cont_juros < divisao_juros:
                        fluxo.append(
                            {'Data do Evento': data_juros, 'Percentual': None, 'Tipo do Evento': 'Juros'})
                        cont_juros += 1
                    if data_amortizacao < data_vencimento and saldo > 0:
                        fluxo.append({'Data do Evento': data_amortizacao,
                                     'Percentual': amort, 'Tipo do Evento': 'Amortização'})
                        saldo -= amort

        fluxo.append({'Data do Evento': data_vencimento, 'Percentual': None, 'Tipo do Evento': 'Juros'})
        fluxo.append({'Data do Evento': data_vencimento,'Percentual': amort, 'Tipo do Evento': 'Vencimento'})

        if tipo_ativo == 'Letra Financeira' and incluir_call:
            i = 1
            data_call = call_inicial
            while i <= repeticoes_call:
                fluxo.append({'Data do Evento': data_call,'Percentual': "", 'Tipo do Evento': 'Call'})
                if periodo_call == "Anual":
                    data_call = data_call + relativedelta(years=1)
                if periodo_call == "Semestral":
                    data_call = data_call + relativedelta(months=6)
                if periodo_call == "180 Dias Corridos":
                    data_call = data_call + relativedelta(days=180)
                i+=1
        eventos = {'Juros': 1,'Amortização': 2,'Vencimento': 3, 'Call': 4 }
        fluxo = [(i, eventos[i['Tipo do Evento']]) for i in fluxo]
        fluxo = [i[0] for i in sorted(fluxo, key=lambda x: (x[0]['Data do Evento'], x[1]))]

        for _ in range(10):
            fluxo.append({'Data do Evento': "", 'Percentual': "", 'Tipo do Evento': ''})

        st.text("")
        info_fluxo = st.expander("Informações do fluxo do ativo", expanded=True)
        total = 0
        with info_fluxo:
            col1, col2 = st.columns([1, 1])
            df = pd.DataFrame(fluxo)
            df.sort_values(['Data do Evento', 'Tipo do Evento'])
            df['Data do Evento'] = df['Data do Evento'].apply(lambda x:  x.strftime('%d/%m/%Y') if x != "" else x)
            custom_css = {
                ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                ".ag-header-cell":{"background-color": "#0D6696 !important", "color": "white"},
                '.ag-header-group-cell':{"background-color": "#2E96BF","color": "white"},
                ".ag-row":  {  "font-size": "16px !important;"}}

            with col1:
                st.subheader('Alterações')
                st.write("Selecione os eventos que você deseja incluir no fluxo:")
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_default_column(editable=True)
                gb.configure_selection('multiple', use_checkbox=True)
                gb.configure_column('Tipo do Evento',
                                    cellEditor='agRichSelectCellEditor',
                                    cellEditorParams={'values': ['Juros', 'Amortização', 'Vencimento', 'Incorporação de Juros', 'Call']},
                                    cellEditorPopup=True,
                                    filter=True
                                    )
                gb.configure_column("Percentual", type=[
                                    "numericColumn", "numberColumnFilter", "customNumericFormat"], 
                                    precision=4,
                                      aggFunc='sum')
                gb.configure_column("Data do Evento", type=[
                                    "dateColumnFilter", "customDateTimeFormat"], 
                                    headerCheckboxSelection= True,
                                    custom_format_string='dd/MM/yyyy')
                gb.configure_grid_options(enableRangeSelection=True)

                new_df = AgGrid(
                    df,
                    gridOptions=gb.build(),
                    fit_columns_on_grid_load=True,
                    allow_unsafe_jscode=True,
                    custom_css=custom_css,
                    enable_enterprise_modules=True)
                new_df = pd.DataFrame(new_df['selected_rows'])

                with col2:
                    st.subheader("Fluxo do ativo")
                    if new_df.index.tolist():
                        try:
                            hide_table_row_index = """
                            <style>
                            thead tr th:first-child {display:none}
                            tbody th {display:none}
                            </style>
                            """
                            st.markdown(hide_table_row_index, unsafe_allow_html=True)
                            new_df['Percentual'] = new_df['Percentual'].apply(lambda x: util.validar_float(x))
                            new_df = new_df.drop(new_df[new_df['Data do Evento'] == ""].index)
                            new_df['Data do Evento'] = new_df['Data do Evento'].apply(lambda x: util.validar_data(x).strftime("%d/%m/%Y"))
                            new_df['ordernar_data'] = new_df['Data do Evento'].apply(lambda x: datetime.strptime(x, "%d/%m/%Y"))
                            new_df['ordernar_evento'] = new_df['Tipo do Evento'].apply(lambda x: 1 if x == 'Juros' else 2)
                            new_df = new_df.sort_values(['ordernar_data', 'ordernar_evento'])
                            new_df = new_df.drop(columns=['ordernar_data', 'ordernar_evento'])
                            new_df = new_df.drop(new_df[new_df['Tipo do Evento'] == ""].index)
                            new_df = new_df[['Data do Evento','Percentual', 'Tipo do Evento']]

                            total = 0
                            for ind, row in new_df.iterrows():
                                if row['Tipo do Evento'] in ['Amortização', 'Vencimento']:
                                    total += row['Percentual']

                            if not (round(total, 2) <= 100 <= round(total, 2)):
                                st.error(f"O valor total de amortização não soma 100% - Total calculado: {round(total, 2)}")
                            if len(new_df.index) > 0:
                                gb = GridOptionsBuilder.from_dataframe(new_df)
                                gb.configure_column('Tipo do Evento')
                                gb.configure_column("Percentual", 
                                                    type=["numericColumn", "numberColumnFilter", "customNumericFormat"], 
                                                    precision=4)
                                gb.configure_column("Data do Evento", 
                                                    type=["dateColumnFilter", "customDateTimeFormat"], 
                                                    custom_format_string='dd/MM/yyyy')
                                gb.configure_grid_options(enableRangeSelection=True)
                                teste = AgGrid(
                                    new_df,
                                    gridOptions=gb.build(),
                                    fit_columns_on_grid_load=True,
                                    allow_unsafe_jscode=True,
                                    custom_css=custom_css,
                                    enable_enterprise_modules=True)

                        except:
                            st.caption("Preencha os dados corretamente")

        if (not (valor_emissao and taxa_emissao and lista_codigos
            and len(new_df.index) > 0
                 and ((round(total, 2) <= 100 <= round(total, 2))))):
            st.caption("Preencha os dados corretamente.")
            cadastrar = False
        else:
            cadastrar = st.button("Cadastrar")
        if (cadastrar and valor_emissao and taxa_emissao and lista_codigos and len(new_df.index) > 0
                and ((round(total, 2) <= 100 <= round(total, 2)))):
            with st.spinner('Aguarde...'):
                try:
                    indice_papel = {'DI+': 'DI', 'DI Percentual': 'DI',
                                    'IPCA+': 'IPCA', 'IGP-M+': 'IGP-M', 'PRÉ': 'PRÉ'}[indice]
                    percentual_papel = taxa_emissao if indice == 'DI Percentual' else 100
                    juros = taxa_emissao if indice != 'DI Percentual' else 0

                    atualizacao = datetime.now()
                    lista_eventos = database.tipo_eventos()
                    eventos = {}
                    for tipo in lista_eventos:
                        eventos[tipo[2]] = tipo[0]

                    fluxo, saldo, saldo_devedor, ativos = [], 100.0, valor_emissao, []
                    for ind, row in new_df.iterrows():
                        data = datetime.strptime(row['Data do Evento'], "%d/%m/%Y").date()
                        percentual = row['Percentual'] / saldo * 100 if row['Tipo do Evento'] == 'Amortização' else None
                        pu_evento = percentual/100 * saldo_devedor if row['Tipo do Evento'] == 'Amortização' else None
                        evento_tratado = unidecode.unidecode(row['Tipo do Evento'].lower().replace(" ", ""))

                        if row['Tipo do Evento'] == 'Amortização':
                            saldo -= row['Percentual']
                            saldo_devedor -= pu_evento

                        for codigo in lista_codigos:
                            id = codigo.strip() + mutil.get_dia_util(data).strftime('%Y%m%d') + str(eventos[evento_tratado])
                            fluxo.append((id, 
                                          codigo.strip(), 
                                          data, 
                                          mutil.get_dia_util(data), 
                                          eventos[evento_tratado], 
                                          percentual, 
                                          pu_evento, 
                                          None, 
                                          atualizacao, 
                                          'Manual'))

                    for codigo in lista_codigos:
                        if serie == '':
                            serie = None
                        num_emissao = None
                        if numero_emissao != '':
                            num_emissao = float(numero_emissao)
                        ativos.append((codigo.strip(), empresa, isin, cnpj, serie, num_emissao, 
                                       inicio_rentabilidade, valor_emissao, data_emissao,
                                       data_vencimento, indice_papel, percentual_papel, juros, None, None,
                                       None, atualizacao, tipo_ativo, 'Manual', None, None, None, None, None, None))
                        database.query_dml_simples(f"delete from icatu.fluxo_papeis where codigo = '{codigo.strip()}'")

                    database.add_info_papeis(ativos)
                    database.add_fluxo_eventos(fluxo)
                    col1, _ = st.columns([1, 4])
                    st.session_state['fluxo'] = False
                    st.cache_resource.clear()
                    if tipo_ativo in ('Letra Financeira', 'CDB', 'DPGE', 'RDB'):
                        automacao.atualizar_ratings_bancarios(database)
                    col1.success('Cadastro realizado com sucesso')

                except Exception as erro:
                    print(erro)
                    st.caption("Erro ao realizar o cadastro")

@try_error
def tabela_ativos(database, barra):

    dados = database.query_select('''
            select 
                i.codigo, 
                tipo_ativo, 
                em.empresa, 
                s.nome as setor,
                isin, 
                i.cnpj, 
                serie, 
                emissao, 
                valor_emissao, 
                data_emissao, 
                inicio_rentabilidade, 
                data_vencimento, 
                case 
                    when indice = 'DI' and percentual > 100 then '%CDI' 
                    when indice = 'DI' and (percentual = 100 or percentual is null) then 'CDI+' 
                    when indice = 'IPCA' then 'IPCA+' 
                    when indice = 'IGP-M' then 'IGPM+'
                    else indice 
                end as indice, 
                percentual, 
                juros, 
                case 
                    when  incentivada = true and (artigo is null or artigo = 2) then 'Sim' 
                    else 'Não' 
                end as incentivada, 
                r.rating, 
                cadastro
            from icatu.info_papeis i
            left join icatu.emissores em on em.cnpj = i.cnpj
            left join icatu.setores s on s.id = em.setor 
            left join icatu.view_ultimo_rating_ativos r on r.codigo = i.codigo
        ''')

    df = pd.DataFrame(dados, columns=[ 
                                    'Código', 
                                    'Tipo de Ativo',
                                    'Empresa', 
                                    'Setor',
                                    'ISIN',
                                    'CNPJ', 
                                    'Série', 
                                    'Emissão', 
                                    'Valor da Emissão',
                                    'Data da Emissão', 
                                    'Início da Rentabilidade', 
                                    'Data de Vencimento', 
                                    'Índice', 
                                    'Percentual', 
                                    'Juros', 
                                    'Incentivada', 
                                    'Rating',
                                    'Tipo de Cadastro'
                                    ])

    df['Código'] = df['Código'].apply(lambda x: x.strip() if x else x)
    df['ISIN'] = df['ISIN'].apply(lambda x: x.strip() if x else x)
    df['Índice'] = df['Índice'].apply(lambda x: x.strip() if x else x)
    df['Tipo de Cadastro'] = df['Tipo de Cadastro'].apply(lambda x: x.strip() if x else x)

    df_download = df.copy(deep=False)
    st.subheader("Informações")
    util.download_excel_button(
                        [df_download], 
                        ['info_papeis'], 
                        'Download em Excel', 
                        'info_papeis')

    df['Data da Emissão'] = df['Data da Emissão'].apply(lambda x: x + relativedelta(days=1) if x is not None else x)
    df['Início da Rentabilidade'] = df['Início da Rentabilidade'].apply(lambda x: x + relativedelta(days=1)if x is not None else x)
    df['Data de Vencimento'] = df['Data de Vencimento'].apply(lambda x: x + relativedelta(days=1)if x is not None else x)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_grid_options(enableCellTextSelection=True)
    gb.configure_grid_options(ensureDomOrder=True)
    gb.configure_grid_options(editable=True)

    gb.configure_column("Código",pinned='left')

    gb.configure_column("Data da Emissão", 
                        type=["dateColumnFilter", "customDateTimeFormat"], 
                        custom_format_string='dd/MM/yyyy')
    gb.configure_column("Início da Rentabilidade", 
                        type=["dateColumnFilter", "customDateTimeFormat"], 
                        custom_format_string='dd/MM/yyyy')
    gb.configure_column("Data de Vencimento",  
                        type=["dateColumnFilter", "customDateTimeFormat"], 
                        custom_format_string='dd/MM/yyyy')
    gb.configure_column("Tipo de Ativo")
    gb.configure_column("Empresa")
    gb.configure_column("ISIN")
    gb.configure_column("CNPJ")
    gb.configure_column("Rating")

    gb = gb.build()
    for campo in gb['columnDefs']:
        if campo['field'] == 'Valor da Emissão':
            campo['valueFormatter'] = "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2});"
        if campo['field'] == 'Juros':
            campo['valueFormatter'] = "value.toLocaleString('pt-BR',{maximumFractionDigits: 4, minimumFractionDigits:2});"
        if campo['field'] == 'Percentual':
            campo['valueFormatter'] = "value.toLocaleString('pt-BR',{maximumFractionDigits: 4, minimumFractionDigits:2});"

    custom_css = {
        ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
        ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
        '.ag-header-group-cell': {"background-color": "#2E96BF","color": "white"},
        ".ag-row":  {  "font-size": "16px !important;"}
        }

    new_df = AgGrid(
        df,
        gridOptions=gb,
        update_mode='NO_UPDATE',
        fit_columns_on_grid_load=False,
        allow_unsafe_jscode=True,
        height=400,
        custom_css=custom_css,
        enableRangeSelection=True,
        enable_enterprise_modules=True)

@try_error
def tabela_fluxo(database, barra):
    st.subheader('Fluxo de eventos')
    dados = database.query_select('''select codigo, data_evento, data_pagamento, t.tipo_evento, percentual, pu_evento, liquidacao, cadastro 
                                from icatu.fluxo_papeis f
                                left join icatu.tipo_eventos t on t.id = f.tipo_id''')

    df = pd.DataFrame(dados, columns=['Código', 'Data do Evento', 'Data do Pagamento', 'Tipo do Evento', 'Percentual',
                                      'PU do Evento', 'Liquidação', 'Cadastro'])

    df_download = df.copy(deep=False)
    # util.download_excel_button([df_download], ['fluxo_papeis'], 'Download em Excel', 'fluxo_papeis')

    df['Data do Evento'] = df['Data do Evento'].apply(
        lambda x: x + relativedelta(days=1) if x is not None else x)
    df['Data do Pagamento'] = df['Data do Pagamento'].apply(
        lambda x: x + relativedelta(days=1)if x is not None else x)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_grid_options(enableCellTextSelection=True)
    gb.configure_grid_options(ensureDomOrder=True)
    gb.configure_grid_options(editable=True)
    gb.configure_column("Data do Evento", type=[
                        "dateColumnFilter", "customDateTimeFormat"], custom_format_string='dd/MM/yyyy')
    gb.configure_column("Data do Pagamento", type=[
                        "dateColumnFilter", "customDateTimeFormat"], custom_format_string='dd/MM/yyyy')
    gb = gb.build()

    for campo in gb['columnDefs']:
        if campo['field'] == 'PU do Evento':
            campo['valueFormatter'] = "value.toLocaleString('pt-BR',{maximumFractionDigits: 6, minimumFractionDigits:6});"
        if campo['field'] == 'Percentual':
            campo['valueFormatter'] = "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2});"

    custom_css = {
        ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
        ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
        '.ag-header-group-cell': {"background-color": "#2E96BF","color": "white"},
        ".ag-row":  {  "font-size": "16px !important;"}
        }


    new_df = AgGrid(
        df,
        gridOptions=gb,
        update_mode='NO_UPDATE',
        height=400,
        custom_css=custom_css,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True)

@try_error
def pl_grupos_emissores(database, barra):
    st.title('Cadastro de Emissores e Grupos')
    tab3, tab4 = st.tabs(
        ['Cadastro de Patrimônio Líquido', 'Consultar Patrimônio Líquido'])

    with tab3:
        opcao = st.radio('Tipo', ['Emissor', 'Grupo'], horizontal=True)
        col1, col2, col3 = st.columns([3, 1, 1])
        emissores, grupos = {}, {}
        lista_emissores_ = database.query_select(
            'select cnpj, empresa from icatu.emissores order by empresa')
        for i in lista_emissores_:
            emissores[i[1]] = i[0]
        lista_grupos_ = database.query_select(
            'select id, nome from icatu.grupo_emissores order by nome')
        for i in lista_grupos_:
            grupos[i[1]] = str(i[0])

        empresa = col1.selectbox('Empresa' if opcao == 'Emissor' else 'Grupo',
                                 [i for i in emissores] if opcao == 'Emissor' else [i for i in grupos], key='fww')
        data = col2.date_input("Data de Referência")
        pl = col3.number_input('Patrimônio Líquido (Em R$ Milhares)')

        cadastrar = st.button('Cadastrar')

        if cadastrar and empresa and data and pl:
            cnpj = emissores[empresa] if opcao == 'Emissor' else grupos[empresa]
            id = cnpj + datetime.strftime(data, '%Y%m%d')
            database.add_patrimonio_liquido(
                [(id, cnpj, data, pl, opcao, 'Manual')])
            col1, _ = st.columns([1, 3])
            col1.success('Informação cadastrada com sucesso.')
        elif cadastrar and not (empresa and data and pl):
            st.caption("Preencha os dados corretamente.")

    with tab4:
        opcao = st.radio('Tipo', ['Emissor', 'Grupo'],
                         horizontal=True, key='consultar')
        emissores, grupos = {}, {}
        lista_emissores = database.query_select("""select cnpj, empresa 
                                                from icatu.emissores e 
                                                join icatu.patrimonio_liquido p on p.empresa_grupo = e.cnpj 
                                                order by e.empresa""")
        for i in lista_emissores:
            emissores[i[1]] = i[0]
        lista_grupos = database.query_select("""(select g.id, g.nome 
                                                from icatu.grupo_emissores g 
                                                join icatu.patrimonio_liquido p on p.empresa_grupo = g.id::varchar
                                                )
                                                union

                                                (select g.id, g.nome 
                                                from icatu.emissores e 
                                                join icatu.patrimonio_liquido p on p.empresa_grupo = e.cnpj
                                                join icatu.grupo_emissores g on g.id = e.grupo
                                                ) order by nome""")
        for i in lista_grupos:
            grupos[i[1]] = str(i[0])
        empresa = st.multiselect('Empresa' if opcao == 'Emissor' else 'Grupo',
                                 [i.strip() for i in emissores] if opcao == 'Emissor' else [i.strip() for i in grupos], key='con')

        gerar = st.button('Consultar', key='234')

        if gerar and empresa:
            try:
                if opcao == 'Emissor':
                    sql = f"""
                        select e.empresa, data_ref, patrimonio_liquido, cadastro  
                        from icatu.patrimonio_liquido p
                        join icatu.emissores e on e.cnpj = p.empresa_grupo 
                        where empresa in ({", ".join([f"'{i}'" for i in empresa])if len(empresa) > 1 else f"'{empresa[0]}'"})
                        order by e.empresa, data_ref """

                    dados = database.query_select(sql)
                    df = pd.DataFrame(dados, columns=[
                                      'Nome', 'Data', 'Patrimônio Líquido (Em R$ Milhares)', 'Cadastro'])
                    hide_table_row_index = """
                    <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                    </style>
                    """
                    st.markdown(hide_table_row_index, unsafe_allow_html=True)
                    df['Data'] = df['Data'].apply(
                        lambda x: x.strftime("%d/%m/%Y"))
                    df['Patrimônio Líquido (Em R$ Milhares)'] = df['Patrimônio Líquido (Em R$ Milhares)'].apply(
                        lambda x: "{:,.0f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))

                    st.table(df)
                else:
                    sql = f"""select e.nome, data_ref, patrimonio_liquido, cadastro  
                        from icatu.patrimonio_liquido p
                        join icatu.grupo_emissores e on e.id::varchar = p.empresa_grupo 
                        where nome in ({", ".join([f"'{i}'" for i in empresa])if len(empresa) > 1  else f"'{empresa[0]}'"}) 
                        order by e.nome, data_ref"""

                    dados = database.query_select(sql)
                    df = pd.DataFrame(dados, columns=[
                                      'Nome', 'Data', 'Patrimônio Líquido (Em R$ Milhares)', 'Cadastro'])
                    hide_table_row_index = """
                    <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                    </style>
                    """
                    st.markdown(hide_table_row_index, unsafe_allow_html=True)
                    df['Data'] = df['Data'].apply(
                        lambda x: x.strftime("%d/%m/%Y"))
                    df['Patrimônio Líquido (Em R$ Milhares)'] = df['Patrimônio Líquido (Em R$ Milhares)'].apply(
                        lambda x: "{:,.0f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))

                    st.subheader('PL do Grupo')
                    st.table(df)

                    sql = f"""select e.empresa, data_ref, patrimonio_liquido, cadastro  
                            from icatu.patrimonio_liquido p
                            join icatu.emissores e on e.cnpj = p.empresa_grupo 
                            where e.grupo in ({", ".join([f"'{grupos[i]}'" for i in empresa])if len(empresa) > 1  else f"'{grupos[empresa[0]]}'"})
                            order by e.empresa, data_ref"""

                    dados = database.query_select(sql)
                    df = pd.DataFrame(dados, columns=[
                                      'Nome', 'Data', 'Patrimônio Líquido (Em R$ Milhares)', 'Cadastro'])
                    hide_table_row_index = """
                    <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                    </style>
                    """
                    st.markdown(hide_table_row_index, unsafe_allow_html=True)
                    df['Data'] = df['Data'].apply(
                        lambda x: x.strftime("%d/%m/%Y"))
                    df['Patrimônio Líquido (Em R$ Milhares)'] = df['Patrimônio Líquido (Em R$ Milhares)'].apply(
                        lambda x: "{:,.0f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))

                    st.subheader('PL de Emissores')
                    st.table(df)
            except:
                st.caption('Houve um erro')

@try_error
def ratings(database, barra):
    st.title('Cadastro de Ratings')
    tab1, tab2, tab3 = st.tabs(['Consulta', 'Alterações de Ratings por Fundo', 'Cadastro'])

    with tab3:
        tipo = st.radio('Tipo', ['Ativo', 'Emissor'], horizontal=True)
        if tipo == 'Ativo':
            col_isin, col1, col2, col3, col4 = st.columns([1, 1, 1, 1, 1])
            lista_ativos = {i[0].strip(): i[1].strip() if i[1] else '' for i in database.query_select(
                'select distinct codigo, isin from icatu.info_papeis order by codigo')}
            isin = col_isin.multiselect(
                'ISIN', [lista_ativos[i] for i in lista_ativos])
            if isin:
                lista_ativo_emissor = [
                    i for i in lista_ativos if lista_ativos[i] in isin]
                lista_ativo_emissor = col1.multiselect(
                    tipo, lista_ativos, lista_ativo_emissor)
            else:
                lista_ativo_emissor = col1.multiselect(tipo, lista_ativos)
        else:
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            lista_ativos = database.query_select("select cnpj, empresa from icatu.emissores order by empresa")
            emissores = {}
            for i in lista_ativos:
                emissores[i[1]] = i[0]
            lista_ativos = [i for i in emissores]
            lista_ativo_emissor = col1.multiselect(tipo, lista_ativos)
        if tipo == 'Emissor':
            lista_ativo_emissor = [emissores[i] for i in lista_ativo_emissor]
        data = col2.date_input('Data')
        agencia = col3.selectbox('Agência', ['ICATU', 'S&P', 'MOODYS', 'FITCH'])
        sql = f"""
            select * from icatu.ordenacao_ratings where agencia = '{agencia}' order by ordenacao
            """
        lista_ratings = database.query_select(sql)
        ratings = {}
        for i in lista_ratings:
            ratings[i[2]] = i[0]

        ignorar = ['Aaa', 'Aa1', 'Aa2', 'Aa3', 'A1', 'A2', 'A3',
                   'Baa1', 'Baa2', 'Baa3', 'Ba1', 'Ba2', 'Ba3', 'B1', 'B2', 'B3']
        rating = col4.selectbox(
            'Rating', [i for i in ratings if i not in ignorar])
        rating_id = ratings[rating]
        col1, _ = st.columns([1, 3])
        file = col1.file_uploader('Arquivo', type='pdf')
        cadastrar = st.button('Cadastrar')

        caminho_ratings = os.path.join(r"\\ISMTZVANGUARDA", 'Dir-GestaodeAtivos$', 'Mesa Renda Fixa', '1. Gestão Crédito', 'Banco de Dados', 'Ratings')

        if cadastrar:
            col1, col2 = st.columns([1, 4])
            
            if lista_ativo_emissor:
                if file or agencia == 'ICATU':
                    for ativo_emissor in lista_ativo_emissor:
                        id = ativo_emissor + data.strftime('%Y%m%d') + str(rating_id)
                        database.add_ratings(
                            [(id, ativo_emissor, data, rating_id, tipo, 'Manual')])
                        arquivo = ativo_emissor + data.strftime('%Y%m%d')+agencia+rating+'.pdf'
                        if file:
                            with open(os.path.join(caminho_ratings, arquivo), mode='wb') as w:
                                w.write(file.getvalue())
                    col1.success('Rating(s) cadastrado(s) com sucesso.')
                else:
                    col1.error('Insira um arquivo PDF com o rating')

    with tab1:
        tipo = st.radio('Tipo', ['Ativo', 'Emissor'],
                        horizontal=True, key='hsef')
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        if tipo == 'Ativo':
            lista_ativos = [i[0].strip() for i in database.query_select(
                'select distinct codigo from icatu.info_papeis order by codigo')]
        else:
            lista_ativos = database.query_select(
                "select cnpj, empresa from icatu.emissores order by empresa")
            emissores = {}
            for i in lista_ativos:
                emissores[i[1]] = i[0]
            lista_ativos = [i for i in emissores]
        ativo_emissor = col1.multiselect(tipo, lista_ativos, key='0-')
        agencia = col2.multiselect(
            'Agência', ['ICATU', 'S&P', 'MOODYS', 'FITCH'], key='ve')
        if agencia:
            sql = f"""
                select * from icatu.ordenacao_ratings where agencia in ({", ".join([f"'{i}'" for i in agencia])if len(agencia) > 1  else f"'{agencia[0]}'"}) 
                order by ordenacao
                """

            lista_ratings = database.query_select(sql)
            ratings = {}
            for i in lista_ratings:
                ratings[i[2]] = i[0]
        else:
            ratings = [i[0].strip() for i in database.query_select(
                "select rating from icatu.ordenacao_ratings where agencia = 'FITCH' order by ordenacao")]

        rating = col3.multiselect(
            'Rating', [i for i in ratings if i.strip() not in ignorar], key='vewe')
        cadastro = col4.multiselect(
            'Cadastro', ['Manual', 'Automático'], key='8ui')
        consultar = st.button('Consultar')
        if (consultar or ('consulta' in st.session_state and st.session_state['consulta'])) and ativo_emissor:
            st.session_state['consulta'] = True
            with st.spinner('Aguarde...'):
                busca = ''
                if tipo == 'Ativo':
                    if ativo_emissor:
                        busca = f"""where r.codigo in ({", ".join([f"'{i}'" for i in ativo_emissor])if len(ativo_emissor) > 1  else f"'{ativo_emissor[0]}'"})"""

                    sql = f"""
                        select r.codigo, data, agencia, rating, r.cadastro from icatu.ratings r
                        join icatu.ordenacao_ratings o on o.id = r.rating_id
                        join icatu.info_papeis e on e.codigo = r.codigo
                        {busca}
                        order by r.codigo, data 
                    """
                    dados = database.query_select(sql)
                    df = pd.DataFrame(
                        dados, columns=['Código / CNPJ', 'Data', 'Agência', 'Rating', 'Cadastro'])
                    hide_table_row_index = """
                    <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                    </style>
                    """
                    st.markdown(hide_table_row_index,
                                unsafe_allow_html=True)
                    df['Data'] = df['Data']
                    if rating:
                        df = df[df['Rating'].isin(rating)]
                    if agencia:
                        df = df[df['Agência'].isin(agencia)]
                    if cadastro:
                        df = df[df['Cadastro'].isin(cadastro)]

                else:
                    if ativo_emissor:
                        busca = f"""where r.codigo in ({", ".join([f"'{emissores[i]}'" for i in ativo_emissor])if len(ativo_emissor) > 1  else f"'{emissores[ativo_emissor[0]]}'"})"""

                    sql = f"""
                        select codigo, data, agencia, rating, r.cadastro from icatu.ratings r
                        join icatu.ordenacao_ratings o on o.id = r.rating_id
                        join icatu.emissores e on e.cnpj = r.codigo
                        {busca}
                        order by r.codigo, data 
                    """
                    dados = database.query_select(sql)
                    df = pd.DataFrame(
                        dados, columns=['Código / CNPJ', 'Data', 'Agência', 'Rating', 'Cadastro'])
                    hide_table_row_index = """
                    <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                    </style>
                    """
                    st.markdown(hide_table_row_index,
                                unsafe_allow_html=True)
                    if rating:
                        df = df[df['Rating'].isin(rating)]
                    if agencia:
                        df = df[df['Agência'].isin(agencia)]
                    if cadastro:
                        df = df[df['Cadastro'].isin(cadastro)]

                caminho_rede = os.path.join(r"\\ISMTZVANGUARDA", 
                                            'Dir-GestaodeAtivos$', 
                                            'Mesa Renda Fixa', 
                                            '1. Gestão Crédito', 
                                            'Banco de Dados', 
                                            'Ratings')
                pasta_rating = os.path.join(caminho_rede, 'Rating Interno')

                def gerar_caminho(x):
                    codigo = x['Código / CNPJ']
                    data = x['Data'].strftime('%Y%m%d')
                    agencia = x['Agência']
                    rating = x['Rating']
                    if agencia == 'ICATU':
                        busca = [i for i in listdir(pasta_rating) if i.split(
                            '_')[0] == codigo and i.split('_')[3].replace('.pdf', '') == rating]
                        return 'Sim' if busca else 'Não'
                    else:
                        caminho = codigo+data+agencia+rating+'.pdf'
                    check = os.path.join(caminho_rede, caminho)
                    return 'Sim' if os.path.exists(check) else 'Não'

                if len(df.index) > 0:
                    df['Possui Arquivo?'] = df.apply(
                        lambda x: gerar_caminho(x), axis=1)

                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_grid_options(
                    enableRangeSelection=True, tooltipShowDelay=0)
                gb.configure_grid_options(enableCellTextSelection=True)
                gb.configure_selection('single', use_checkbox=True)
                gb = gb.build()
                gb['columnDefs'] = [
                    {'field': 'Código / CNPJ', "checkboxSelection": True},
                    {'field': "Data",
                        'type': ["dateColumnFilter", "customDateTimeFormat"], 'custom_format_string': 'dd/MM/yyyy'},
                    {'field': 'Agência'}, {'field': 'Rating'}, {
                        'field': 'Cadastro'}, {'field': 'Possui Arquivo?'}
                ]

                custom_css = {
                    ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                    ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                    ".ag-row":  {  "font-size": "16px !important;"}
                    }
                df = AgGrid(
                    df,
                    gridOptions=gb,
                    fit_columns_on_grid_load=False,
                    update_mode='SELECTION_CHANGED',
                    custom_css=custom_css,
                    height=min(50 + 45 * len(df.index), 400),
                    allow_unsafe_jscode=True,
                    enable_enterprise_modules=True)

                if df['selected_rows'] != []:
                    codigo = df['selected_rows'][0]["Código / CNPJ"]
                    agencia = df['selected_rows'][0]["Agência"]
                    data = datetime.strptime(df['selected_rows'][0]["Data"].replace('T00:00:00.000', ''), '%Y-%m-%d').strftime('%Y%m%d')
                    rating = df['selected_rows'][0]["Rating"]
                    if agencia == 'ICATU':
                        busca = [i for i in listdir(pasta_rating) if i.split('_')[0] == codigo and i.split('_')[3].replace('.pdf', '') == rating]
                        if busca:
                            arquivo = os.path.join(pasta_rating, busca[0])
                        else:
                            arquivo = 'vazio'
                    else:
                        caminho = codigo+data+agencia+rating+'.pdf'
                        arquivo = os.path.join(caminho_rede, caminho)
                    if os.path.exists(arquivo):
                        with open(arquivo, "rb") as pdf_file:
                            base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
                        shutil.copy(arquivo, 'pdf_rating.pdf')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000px" height="800px" type="application/pdf"></iframe>'
                        st.write(
                            f"Abra o PDF em uma nova aba clicando [aqui](http://{env.IP}:{env.API_PORT}/visualizar_pdf/pdf_rating.pdf)")
                        st.markdown(pdf_display, unsafe_allow_html=True)


    with tab2:
        with st.form('a'):
            col1, col2 = st.columns([1, 1])
            data = col1.selectbox('Mês', [i[0].strip() for i in database.query_select(
                "select distinct to_char(data, 'YYYY/MM') from icatu.ratings order by to_char(data, 'YYYY/MM') desc")])
            nome_fundo = col2.selectbox('Fundo', [i[0].strip() for i in database.query_select(
                'select nome from icatu.fundos order by nome')])
            calc = st.form_submit_button('Gerar relatório')

        if calc:
            with st.spinner('Aguarde...'):
                ano = data[:4]
                mes = data[5:7].replace(
                    '0', '') if data[5:7] != '10' else data[5:7]
                data = mutil.somar_dia_util(datetime(int(ano), int(
                    mes), 1).date() + relativedelta(months=1), -1)
                data_estoque = data
                if data > mutil.somar_dia_util(date.today(), -1):
                    data_estoque = mutil.somar_dia_util(date.today(), -1)
                data = data.strftime('%Y-%m-%d')
                data_estoque = data_estoque.strftime('%Y-%m-%d')

                lista_fundos = database.query_select(
                    'SELECT isin, nome, cnpj FROM icatu.fundos;')
                fundos = {}
                for i in lista_fundos:
                    fundos[i[1].strip()] = {
                        'isin': i[0].strip(), 'cnpj': i[2].strip()}
                fundo = fundos[nome_fundo]['isin']
                cnpj = fundos[nome_fundo]['cnpj']

                sql = f"""
                with rating_sp as (
                select 
                    codigo, 
                    tipo,
                    (array_agg(concat(agencia, ' ', rating) order by data desc) FILTER (WHERE agencia = 'S&P'))[2] as rating_anterior,
                    (array_agg(data order by data desc) FILTER (WHERE agencia = 'S&P'))[2] as data_anterior_rating,
                    (array_agg(concat(agencia, ' ', rating) order by data desc) FILTER (WHERE agencia = 'S&P'))[1] as ultimo_rating,
                    (array_agg(data order by data desc) FILTER (WHERE agencia = 'S&P'))[1] as data_ultimo_rating,
                    case 
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[1] < 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[2] then 'Elevado'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[1] > 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[2] then 'Rebaixado'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[1] = 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[2] then 'Estável'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[2] is null and 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[1] is not null then 'Novo Rating'
                        else null
                    end status
                from icatu.ratings r
                join icatu.ordenacao_ratings o on o.id = r.rating_id
                where data <= '{data}'
                group by codigo, tipo),

                rating_moodys as (
                select 
                    codigo, 
                    tipo,
                    (array_agg(concat(agencia, ' ', rating) order by data desc) FILTER (WHERE agencia = 'MOODYS'))[2] as rating_anterior,
                    (array_agg(data order by data desc) FILTER (WHERE agencia = 'MOODYS'))[2] as data_anterior_rating,
                    (array_agg(concat(agencia, ' ', rating) order by data desc) FILTER (WHERE agencia = 'MOODYS'))[1] as ultimo_rating,
                    (array_agg(data order by data desc) FILTER (WHERE agencia = 'MOODYS'))[1] as data_ultimo_rating,
                    case 
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[1] < 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[2] then 'Elevado'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[1] > 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[2] then 'Rebaixado'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[1] = 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[2] then 'Estável'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[2] is null and 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[1] is not null then 'Novo Rating'
                        else null
                    end status
                from icatu.ratings r
                join icatu.ordenacao_ratings o on o.id = r.rating_id
                where data <= '{data}'
                group by codigo, tipo),

                rating_fitch as (
                select 
                    codigo, 
                    tipo,
                    (array_agg(concat(agencia, ' ', rating) order by data desc) FILTER (WHERE agencia = 'FITCH'))[2] as rating_anterior,
                    (array_agg(data order by data desc) FILTER (WHERE agencia = 'FITCH'))[2] as data_anterior_rating,
                    (array_agg(concat(agencia, ' ', rating) order by data desc) FILTER (WHERE agencia = 'FITCH'))[1] as ultimo_rating,
                    (array_agg(data order by data desc) FILTER (WHERE agencia = 'FITCH'))[1] as data_ultimo_rating,
                    case 
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[1] < 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[2] then 'Elevado'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[1] > 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[2] then 'Rebaixado'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[1] = 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[2] then 'Estável'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[2] is null and 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[1] is not null then 'Novo Rating'
                        else null
                    end status
                from icatu.ratings r
                join icatu.ordenacao_ratings o on o.id = r.rating_id
                where data <= '{data}'
                group by codigo, tipo),

                empresas as (
                select cnpj as codigo, empresa
                from icatu.emissores 
                union
                (
                select distinct r.codigo, e.empresa
                from icatu.ratings r
                left join icatu.info_papeis i on i.codigo = r.codigo
                left join icatu.emissores e on e.cnpj = i.cnpj
                where tipo = 'Ativo')),

                tabela as (
                    select * from (
                        select * from rating_sp 
                            union select * from rating_moodys
                            union select * from rating_fitch) as tabela
                            where status in ('Elevado', 'Rebaixado'))

                select 
                    distinct '{cnpj}' AS CNPJ_fundo, 
                    '{nome_fundo}' as nome_fundo, 
                    t.codigo, 
                    e.empresa, 
                    rating_anterior, 
                    data_anterior_rating, 
                    ultimo_rating, 
                    data_ultimo_rating, 
                    status

                from tabela t
                left join empresas e on e.codigo = t.codigo
                left join icatu.info_papeis i on i.codigo = t.codigo
                where t.codigo in (SELECT distinct ativo from icatu.estoque_ativos where fundo = '{fundo}' and data = '{data_estoque}')
                and extract('MONTH' from data_ultimo_rating) = {mes} and extract('YEAR' from data_ultimo_rating) = {ano}
                and data_anterior_rating >= (data_ultimo_rating - interval '1 year')
                        """
                dados = database.query_select(sql)
                df_ativos = pd.DataFrame(dados, columns=['CNPJ do Fundo', 'Nome do Fundo', 'Código do Ativo',
                                         'Empresa', 'Rating Anterior',  'Data Anterior', 'Rating Atual', 'Data',  'Status'])

                sql = f"""
                with rating_sp as (
                select 
                    codigo, 
                    tipo,
                    (array_agg(concat(agencia, ' ', rating) order by data desc) FILTER (WHERE agencia = 'S&P'))[2] as rating_anterior,
                    (array_agg(data order by data desc) FILTER (WHERE agencia = 'S&P'))[2] as data_anterior_rating,
                    (array_agg(concat(agencia, ' ', rating) order by data desc) FILTER (WHERE agencia = 'S&P'))[1] as ultimo_rating,
                    (array_agg(data order by data desc) FILTER (WHERE agencia = 'S&P'))[1] as data_ultimo_rating,
                    case 
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[1] < 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[2] then 'Elevado'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[1] > 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[2] then 'Rebaixado'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[1] = 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[2] then 'Estável'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[2] is null and 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'S&P'))[1] is not null then 'Novo Rating'
                        else null
                    end status
                from icatu.ratings r
                join icatu.ordenacao_ratings o on o.id = r.rating_id
                where data <= '{data}'
                group by codigo, tipo),

                rating_moodys as (
                select 
                    codigo, 
                    tipo,
                    (array_agg(concat(agencia, ' ', rating) order by data desc) FILTER (WHERE agencia = 'MOODYS'))[2] as rating_anterior,
                    (array_agg(data order by data desc) FILTER (WHERE agencia = 'MOODYS'))[2] as data_anterior_rating,
                    (array_agg(concat(agencia, ' ', rating) order by data desc) FILTER (WHERE agencia = 'MOODYS'))[1] as ultimo_rating,
                    (array_agg(data order by data desc) FILTER (WHERE agencia = 'MOODYS'))[1] as data_ultimo_rating,
                    case 
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[1] < 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[2] then 'Elevado'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[1] > 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[2] then 'Rebaixado'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[1] = 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[2] then 'Estável'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[2] is null and 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'MOODYS'))[1] is not null then 'Novo Rating'
                        else null
                    end status
                from icatu.ratings r
                join icatu.ordenacao_ratings o on o.id = r.rating_id
                where data <= '{data}'
                group by codigo, tipo),

                rating_fitch as (
                select 
                    codigo, 
                    tipo,
                    (array_agg(concat(agencia, ' ', rating) order by data desc) FILTER (WHERE agencia = 'FITCH'))[2] as rating_anterior,
                    (array_agg(data order by data desc) FILTER (WHERE agencia = 'FITCH'))[2] as data_anterior_rating,
                    (array_agg(concat(agencia, ' ', rating) order by data desc) FILTER (WHERE agencia = 'FITCH'))[1] as ultimo_rating,
                    (array_agg(data order by data desc) FILTER (WHERE agencia = 'FITCH'))[1] as data_ultimo_rating,
                    case 
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[1] < 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[2] then 'Elevado'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[1] > 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[2] then 'Rebaixado'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[1] = 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[2] then 'Estável'
                        when (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[2] is null and 
                                (array_agg(ordenacao order by data desc) FILTER (WHERE agencia = 'FITCH'))[1] is not null then 'Novo Rating'
                        else null
                    end status
                from icatu.ratings r
                join icatu.ordenacao_ratings o on o.id = r.rating_id
                where data <= '{data}'
                group by codigo, tipo),

                empresas as (
                select cnpj as codigo, empresa
                from icatu.emissores 
                union
                (
                select distinct r.codigo, e.empresa
                from icatu.ratings r
                left join icatu.info_papeis i on i.codigo = r.codigo
                left join icatu.emissores e on e.cnpj = i.cnpj
                where tipo = 'Ativo')),

                tabela as (
                    select * from (
                        select * from rating_sp 
                            union select * from rating_moodys
                            union select * from rating_fitch) as tabela
                            where status in ('Elevado', 'Rebaixado'))

                select 
                    distinct '{cnpj}' AS CNPJ_fundo, 
                    '{nome_fundo}' as nome_fundo, 
                    t.codigo, 
                    e.empresa, 
                    rating_anterior, 
                    data_anterior_rating, 
                    ultimo_rating, 
                    data_ultimo_rating, 
                    status

                from tabela t
                left join empresas e on e.codigo = t.codigo
                left join icatu.info_papeis i on i.codigo = t.codigo
                where t.codigo in (select distinct cnpj from icatu.info_papeis where codigo in (SELECT distinct ativo from icatu.estoque_ativos where fundo = '{fundo}' and data = '{data_estoque}')) 
                and extract('MONTH' from data_ultimo_rating) = {mes} and extract('YEAR' from data_ultimo_rating) = {ano}
                        """

                dados = database.query_select(sql)
                df_emissores = pd.DataFrame(dados, columns=[
                                            'CNPJ do Fundo', 'Nome do Fundo', 'CNPJ', 'Empresa', 'Rating Anterior',  'Data Anterior', 'Rating Atual', 'Data',  'Status'])
                df_emissores_download, df_ativos_download = df_emissores.copy(
                    deep=False), df_ativos.copy(deep=False)
                hide_table_row_index = """
                <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
                </style>
                """
                st.markdown(hide_table_row_index, unsafe_allow_html=True)
                meses = {'1': 'Janeiro', '2': 'Fevereiro', '3': 'Março', '4': 'Abril', '5': 'Maio', '6': 'Junho',
                         '7': 'Julho', '8': 'Agosto', '9': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'}

                sql = f"""
                    select 
                        distinct
                        e.data,
                        e.ativo,
                        em.empresa as emissor,
                        v.agencia,
                        v.rating,
                        v.data as data_rating 
                    from icatu.estoque_ativos e
                    left join icatu.fundos f on f.isin = e.fundo
                    left join icatu.info_papeis i on i.codigo = e.ativo 
                    left join icatu.emissores em on em.cnpj = i.cnpj
                    left join icatu.view_ultimo_rating_ativos v on v.codigo =e.ativo
                    where fonte <> 'BRITECH'
                    and e.data = '{data_estoque}' and nome = '{nome_fundo}'
                    order by ativo
                """
                ratings_carteira = pd.DataFrame(database.query(sql))
                ratings_carteira = ratings_carteira.rename(columns={
                    'data': 'Data',
                    'ativo': 'Ativo',
                    'emissor': 'Emissor',
                    'agencia': 'Agência',
                    'rating': 'Rating Emissão',
                    'data_rating': 'Data Rating'
                })
                st.subheader('Alterações de Ratings - ' +
                             nome_fundo+f' ({meses[mes]}/{ano})')
                util.download_excel_button([df_emissores_download, df_ativos_download, ratings_carteira], [
                                           'Emissores', 'Ativos', 'Carteira'], 'Download em Excel', f'Alteracoes_{nome_fundo}')
                st.subheader('Emissores')

                df_emissores['Data Anterior'] = df_emissores['Data Anterior'].apply(lambda x: datetime.strptime(
                    x, '%d-%m-%Y').strftime("%d/%m/%Y") if isinstance(x, str) else x.strftime("%d/%m/%Y"))
                df_emissores['Data'] = df_emissores['Data'].apply(lambda x: datetime.strptime(
                    x, '%d-%m-%Y').strftime("%d/%m/%Y") if isinstance(x, str) else x.strftime("%d/%m/%Y"))
                df_ativos['Data Anterior'] = df_ativos['Data Anterior'].apply(lambda x: datetime.strptime(
                    x, '%d-%m-%Y').strftime("%d/%m/%Y") if isinstance(x, str) else x.strftime("%d/%m/%Y"))
                df_ativos['Data'] = df_ativos['Data'].apply(lambda x: datetime.strptime(
                    x, '%d-%m-%Y').strftime("%d/%m/%Y") if isinstance(x, str) else x.strftime("%d/%m/%Y"))
                st.table(df_emissores[[coluna for coluna in df_emissores.columns if coluna not in [
                         'CNPJ do Fundo', 'Nome do Fundo', 'CNPJ']]])
                st.subheader('Ativos')
                st.table(df_ativos[[coluna for coluna in df_ativos.columns if coluna not in [
                         'CNPJ do Fundo', 'Nome do Fundo', 'CNPJ']]])
