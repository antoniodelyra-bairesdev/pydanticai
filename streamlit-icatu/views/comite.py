import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from models import automacao
import pandas as pd
import os

assuntos = {
    'assunto 1': {'data': 'data', 'rating': 1, 'presenca': ['pessoa 1', 'pessoa 2']},
    'assunto 2': {'data': 'data', 'rating': 2, 'presenca': ['pessoa 1', 'pessoa 2']}
}


def try_error(func):
    def wrapper(database):
        try:
            return func(database)
        except:
            st.caption('Houve um erro.')
    return wrapper


@st.cache_resource(show_spinner=False)
def query_db(_database, query):
    return _database.query(query)


@try_error
def ata_comite(database):
    st.title('Gerar Ata de Comitê')
    st.subheader('Novas emissões no mês')
    with st.spinner('Aguarde...'):
        col1, _ = st.columns([1, 5])
        mes = col1.selectbox('Selecione o mês', [i['mes'] for i in query_db(database, """
                                    select 
                                    distinct to_char(data, 'YYYY/mm') as mes
                                    from icatu.estoque_ativos 
                                    order by to_char(data, 'YYYY/mm') desc""")])
        sql = f"""
            WITH rating AS (
                
                select 
                    codigo,
                    (array_remove(array_agg(o.rating order by r.data desc) , null))[1] as rating
                from icatu.ratings r 
                left join icatu.ordenacao_ratings o on o.id = r.rating_id
                where agencia = 'ICATU' and tipo = 'Ativo'
                group by codigo
            )

            select 
                to_char(min(e.data), 'YYYY/MM') as min_data,
                tipo_ativo,
                ativo,
                v.rating ,
                min(e.data) as data,
                em.empresa,
                concat(concat(
                    concat(i.emissao, case when emissao is not null then 'ª Emissão de ' else 'Emissão de ' end), 
                        case 
                            when tipo_ativo = 'Debênture' then 'Debêntures de '
                            when tipo_ativo = 'CRI' then 'CRI de '
                            when tipo_ativo = 'BOND' then 'BONDs de '
                            when tipo_ativo = 'CDB' then 'CDBs do '
                            when tipo_ativo like  'FIDC' then 'Cotas Seniores do '
                            when tipo_ativo = 'Letra Financeira' then 'Letras Financeiras do '
                            else  concat(tipo_ativo, ' de ')
                        end),
                    em.empresa) as texto
            from icatu.estoque_ativos e
            left join icatu.info_papeis i on i.codigo = e.ativo 
            left join icatu.emissores em on em.cnpj = i.cnpj
            left join rating v on v.codigo = e.ativo
            where fonte <> 'BRITECH'
            and fundo not in ('012812', '012811')
            group by ativo, em.empresa, tipo_ativo, i.emissao, v.rating
            having to_char(min(e.data), 'YYYY/MM') = '{mes}'
            order by to_char(min(e.data), 'YYYY/MM') desc, min(e.data)
        """

        df = pd.DataFrame(query_db(database, sql))
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_grid_options(enableCellTextSelection=True)
        gb.configure_grid_options(ensureDomOrder=True)
        gb = gb.build()

        custom_css = {
        ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
        ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
        ".ag-row":  {  "font-size": "16px !important;"}
        }


        gb['columnDefs'] = [
            {'field': "data", 'type': [
                "dateColumnFilter", "customDateTimeFormat"], 'custom_format_string': 'dd/MM/yyyy'},
            {'field': 'tipo_ativo',  'headerName': 'Tipo'},
            {'field': 'ativo',  'headerName': 'Ativo'},
            {'field': 'rating',  'headerName': 'Rating'},
            {'field': 'empresa', 'minWidth': 300, 'headerName': 'Emissor'},
            {'field': 'texto', 'minWidth': 400, 'headerName': 'Texto'},
        ]
        new_df = AgGrid(
            df,
            gridOptions=gb,
            update_mode='NO_UPDATE',
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
            enableRangeSelection=True,
            custom_css=custom_css,
            height=min(45 + 45 * len(df.index), 400),
            enable_enterprise_modules=True)

    st.subheader('Adicionar comitê')
    with st.form('form'):
        col1, col2 = st.columns([1, 5])
        data = col1.date_input('Data')
        assunto = col2.text_input('Assunto')
        col1, col2 = st.columns([1, 5])
        rating = col1.selectbox('Rating Interno', [1, 2, 3, 4, 5, 6])
        lista_presenca = {i['nome']: i['nome_completo'] for i in query_db(
            database, "select nome, nome_completo from icatu.analistas where mesa in ('Crédito Privado', 'Imobiliário') and ativo = true ")}
        lista_credito = {i['nome']: i['nome_completo'] for i in query_db(
            database, "select nome, nome_completo from icatu.analistas where mesa in ('Crédito Privado') and ativo = true ")}

        presenca = col2.multiselect('Lista de Presença',
                                    sorted([i for i in lista_presenca]),
                                    sorted([i for i in lista_credito]))
        # col1, _ = st.columns([1, 2])
        # arquivo = col1.file_uploader('Arquivo')
        if presenca:
            presenca_texto = ', '.join(sorted(presenca))
        adicionar = st.form_submit_button('Adicionar')

    # if arquivo and arquivo.name.lower().endswith('.vtt'):
    #     transcricao = arquivo.getvalue().decode("utf-8")
    #     transcricao = (re.sub('(?:[01]\d|2[0-3]):([0-5]?\d):([0-5]?\d)(:|\.)\d{3}', '', transcricao)
    #          .replace('-->', '')
    #          .replace('<v','')
    #          .replace('</v>', '')
    #          .replace('WEBVTT',''))
    # else:
    #     transcricao =None
    if not 'dados' in st.session_state:
        dados = []
    else:
        if st.button('Limpar lista'):
            dados = []
            st.session_state.pop('dados')
        else:
            dados = st.session_state['dados']

    if adicionar and presenca and assunto:
        dados.append({
            'Assunto': assunto,
            'Data': data,
            'Rating Interno': rating,
            'Presença texto': presenca_texto,
            'Presença': sorted([lista_presenca[i] for i in presenca]),
            # 'Arquivo': arquivo.name if arquivo and arquivo.name.lower().endswith('.vtt') else '',
            # 'transcricao': transcricao
        })
        st.session_state['dados'] = dados

    if dados:
        df = pd.DataFrame(dados)
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_grid_options(enableCellTextSelection=True)
        gb.configure_grid_options(ensureDomOrder=True)
        gb = gb.build()

        gb['columnDefs'] = [
            {'field': 'Assunto', 'suppressMenu': True},
            {'field': "Data", 'suppressMenu': True, 'maxWidth': 120, 'type': [
                "dateColumnFilter", "customDateTimeFormat"], 'custom_format_string': 'dd/MM/yyyy'},
            {'field': 'Rating Interno', 'suppressMenu': True, 'maxWidth': 150, },
            {'field': 'Presença texto', 'suppressMenu': True,
                'tooltipField': "Presença texto", 'headerName': 'Presença', 'minWidth': 350},
            # {'field': 'Arquivo','suppressMenu':True}
        ]

        custom_css = {
        ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
        ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
        ".ag-row":  {  "font-size": "16px !important;"}
        }


        new_df = AgGrid(
            df,
            gridOptions=gb,
            update_mode='NO_UPDATE',
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
            enableRangeSelection=True,
            custom_css=custom_css,
            height=min(45 + 45 * len(df.index), 400),
            enable_enterprise_modules=True)
        # gerar_resumo = st.checkbox('Gerar resumo pelo ChatGPT', False)

        if st.button('Gerar Ata'):
            assuntos = {}
            data = max(i['Data'] for i in dados)
            for linha in dados:
                assuntos[linha['Assunto']] = {
                    'data': linha['Data'],
                    'rating': linha['Rating Interno'],
                    'presenca': linha['Presença'],
                    # 'transcricao': linha['transcricao']
                }
            with st.spinner('Aguarde...'):
                automacao.gerar_ata_comite(data, assuntos)
                cwd = os.getcwd()
                caminho_pdf = cwd + f"\\assets\\Relatórios\\ata_comite.pdf"
                caminho_word = cwd + f"\\assets\\Relatórios\\ata_comite.docx"

                with open(caminho_word, "rb") as file:
                    btn = st.download_button(
                        label="Download em Word",
                        data=file,
                        file_name='Ata Comitês de Análise e Monitoramento de Crédito - ' +
                        data.strftime('%m %Y')+'.docx',
                        mime="docx"
                    )
                with open(caminho_pdf, "rb") as file:
                    btn = st.download_button(
                        label="Download em PDF",
                        data=file,
                        file_name='Ata Comitês de Análise e Monitoramento de Crédito - ' +
                        data.strftime('%m %Y')+'.pdf',
                        mime="pdf"
                    )
