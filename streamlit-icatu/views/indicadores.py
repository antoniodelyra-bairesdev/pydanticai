from datetime import datetime
from dateutil.relativedelta import relativedelta
from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit as st
import pandas as pd
import plotly.express as px
import models.automacao as at
import models.util as mutil
import views.util as util
import math
import os
import base64


@st.cache_resource(show_spinner=False)
def get_curva_di(_database, data):
    return at.curva_di_to_df(data, _database)


@st.cache_resource(show_spinner=False)
def get_curva_ntnb(_database, data, dataframe):
    return at.curva_ntnb_interpolada(_database, data, dataframe)


@st.cache_resource(show_spinner=False)
def query_db(_database, query):
    return _database.query(query)


def try_error(func):
    def wrapper(database, barra):
        try:
            return func(database, barra)
        except:
            st.caption('Houve um erro.')
    return wrapper


@try_error
def indicadores(barra, database):
    st.title('Indicadores Financeiros')
    with barra:
        tipo = st.selectbox('Selecione a tela', [
                            'Calcular Spread/Taxa', 'Indicadores', 'Fundos Imobiliários', 'Bancários'])

    if tipo == 'Calcular Spread/Taxa':
        spread_taxa(database)

    if tipo == 'Indicadores':
        with st.spinner('Aguarde...'):
            with st.expander('Curva DI', expanded=True):
                curva_di(database)
            with st.expander('Curva NTN-B', expanded=True):
                curva_ntnb(database)
            with st.expander('Inflação', expanded=True):
                ipca(database)

    if tipo == 'Fundos Imobiliários':
        fii(database)

    if tipo == 'Bancários':
        indicadores_bancarios(database)


def indicadores_bancarios(database):
    st.subheader('Indicadores Bancários')
    col1, _ = st.columns([1, 4])
    with col1.form('123', border=False):
        periodo = st.selectbox('Período', [i['periodo'] for i in database.query(
            "select distinct to_char(data, 'DD/MM/YYYY') as periodo, data from icatu.indicadores order by data desc")])
        gerar = st.form_submit_button('Gerar PDF')
    data = datetime.strptime(periodo, '%d/%m/%Y')

    if gerar:
        with st.spinner('Aguarde...'):
            at.gerar_pdf_bancos(database, data)
            cwd = os.getcwd()
            arquivo = os.path.join(cwd,  "assets", 'bancarios.pdf')

            if os.path.exists(arquivo):
                with open(arquivo, "rb") as pdf_file:
                    base64_pdf = base64.b64encode(
                        pdf_file.read()).decode('utf-8')

                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1300px" height="800px" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)


def spread_taxa(database):
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    data = col1.date_input('Data')
    tipo = col2.selectbox('Tipo', ['Calcular Spread', 'Calcular Taxa'])
    if tipo == 'Calcular Spread':
        indice = col3.selectbox('Índice', ['CDI+', 'CDI%', 'IPCA+', 'PRÉ'])
        taxa = col4.number_input('Taxa')
    else:
        indice = col3.selectbox('Índice', ['CDI', 'IPCA'])
        spread = col4.number_input('Spread')
    duration_anos = col5.number_input('Duration (Anos)')
    calc = st.button('Calcular')

    if calc and tipo == 'Calcular Taxa' and spread > 0 and duration_anos > 0:
        du = mutil.contar_du(data, mutil.somar_dia_util(data, round(duration_anos*252, 0)))
        if indice in ['CDI']:
            df = get_curva_di(database, data)
            taxa_curva = df[df['Dias Úteis'] == du]['Taxa'].tolist()[0]
        else:
            df = get_curva_ntnb(database, data, dataframe=None)
            taxa_curva = df[du]

        if indice == 'CDI':
            taxa_cdi_mais = (((1+spread/100) * (1+taxa_curva/100))-1)*100
            taxa_cdi_perc = (((((1+spread/100) * (1+taxa_curva/100))** (1/252))-1) / (((1+taxa_curva/100)**(1/252))-1))*100
            df = pd.DataFrame([
                {'Data': data, 'Tipo': 'PRÉ', 'Taxa': taxa_cdi_mais,'Duration': duration_anos, 'Spread': spread, 'Taxa Curva': taxa_curva},
                {'Data': data, 'Tipo': 'CDI+', 'Taxa': spread,'Duration': duration_anos, 'Spread': spread, 'Taxa Curva': taxa_curva},
                {'Data': data, 'Tipo': 'CDI%', 'Taxa': taxa_cdi_perc, 'Duration': duration_anos, 'Spread': spread, 'Taxa Curva': taxa_curva}])
        else:
            taxa = (((1+spread/100) * (1+taxa_curva/100))-1)*100
            df = pd.DataFrame([
                {'Data': data, 'Tipo': 'IPCA+', 'Taxa': taxa, 'Duration': duration_anos, 'Spread': spread, 'Taxa Curva': taxa_curva}])

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_grid_options(enableRangeSelection=True)
        gb.configure_grid_options(enableCellTextSelection=True)
        gb = gb.build()
        gb['columnDefs'] = [
            {'field': "Data", 'type': [
                "dateColumnFilter", "customDateTimeFormat"], 'custom_format_string': 'dd/MM/yyyy'},
            {'field': 'Tipo'},
            {'field': 'Taxa',
             'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
             'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%'"},
            {'field': 'Duration',
             'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
             'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
            {'field': 'Spread',
             'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
             'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%';"},
            {'field': 'Taxa Curva',
             'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
             'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%';"}]

        custom_css = {
        ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
        ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
        ".ag-row":  {  "font-size": "16px !important;"}
        }


        col1, col2 = st.columns([1, 1])
        with col1:
            new_df = AgGrid(
                df,
                gridOptions=gb,
                update_mode='NO_UPDATE',
                fit_columns_on_grid_load=True,
                allow_unsafe_jscode=True,
                enableRangeSelection=True,
                custom_css=custom_css,
                height=140 if indice == 'CDI' else 80,
                enable_enterprise_modules=True)

    if calc and tipo == 'Calcular Spread' and taxa > 0 and duration_anos > 0:
        with st.spinner('Aguarde...'):
            df = pd.DataFrame([at.calcular_spread_dia(database, data, duration_anos, indice, taxa)])
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_grid_options(enableRangeSelection=True)
            gb.configure_grid_options(enableCellTextSelection=True)
            gb = gb.build()
            gb['columnDefs'] = [
                {'field': "Data", 'type': [
                    "dateColumnFilter", "customDateTimeFormat"], 'custom_format_string': 'dd/MM/yyyy'},
                {'field': 'Tipo'},
                {'field': 'Taxa',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%'"},
                {'field': 'Duration',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                {'field': 'Spread',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%';"},
                {'field': 'Taxa Curva',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%';"}]

            custom_css = {
                ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                ".ag-row":  {  "font-size": "16px !important;"}
                }

            col1, col2 = st.columns([1, 1])
            with col1:
                new_df = AgGrid(
                    df,
                    gridOptions=gb,
                    update_mode='NO_UPDATE',
                    fit_columns_on_grid_load=True,
                    allow_unsafe_jscode=True,
                    enableRangeSelection=True,
                    custom_css=custom_css,
                    height=80,
                    enable_enterprise_modules=True)


def fii(database):
    st.subheader('Fundos Imobiliários')
    with st.form('ffsd'):
        col1, col2, col3, col4 = st.columns([1, 1, 2.5, 2.5])
        data_inicial = col1.date_input('Data Inicial')
        data_final = col2.date_input('Data Final')
        setores = col3.multiselect('Setor', [i['nome'] for i in query_db(
            database, 'select nome from icatu.setores_fii order by nome')])
        fundos = col4.multiselect('FII', [i['codigo'] for i in query_db(
            database, 'select codigo from icatu.fundos_imobiliarios order by codigo')])
        calc = st.form_submit_button("Calcular")
    if calc:
        with st.spinner('Aguarde...'):
            sql = f"""
            select c.*, s.nome as setor from icatu.cotas_fiis c
            left join icatu.fundos_imobiliarios f on f.codigo = c.fundo
            left join icatu.setores_fii s on s.id = f.setor
            where c.data between '{data_inicial.strftime('%Y-%m-%d')}' and '{data_final.strftime('%Y-%m-%d')}'
            """
            df = pd.DataFrame(database.query(sql))

            df = df.sort_values(['fundo', 'data'], ascending=[True, True])
            dados, retornos = {}, []
            for ind, row in df.iterrows():
                data_d1 = mutil.somar_dia_util(
                    row['data'], -1).strftime('%Y%m%d')
                data = row['data'].strftime('%Y%m%d')
                fundo = row['fundo']
                if not fundo in dados:
                    dados[fundo] = {}
                if not data in dados[fundo]:
                    dados[fundo][data] = row['cota_ajustada']
                try:
                    retornos.append(
                        (row['cota_ajustada']/dados[fundo][data_d1]))
                except:
                    retornos.append(1)

            df['retorno'] = retornos
            calc_fundos = {}
            if fundos:
                df_acumulado_fundo = df[df['fundo'].isin(
                    fundos)][['data', 'fundo', 'retorno']]
                df_acumulado_fundo['retorno'] = df_acumulado_fundo['retorno']
                df_acumulado_fundo.dropna(subset=['retorno'], inplace=True)
                for ind, row in df_acumulado_fundo.iterrows():
                    data = row['data']
                    data_d1 = mutil.somar_dia_util(data, -1)
                    fundo = row['fundo']
                    if not fundo in calc_fundos:
                        calc_fundos[fundo] = {}
                    if not data_d1.strftime('%d%m%Y') in calc_fundos[fundo]:
                        prod = math.prod(df_acumulado_fundo[(df_acumulado_fundo['data'] <= data) & (
                            df_acumulado_fundo['fundo'] == fundo)]['retorno'].tolist())
                        calc_fundos[fundo][data.strftime('%d%m%Y')] = prod
                    else:
                        prod = calc_fundos[fundo][data_d1.strftime(
                            '%d%m%Y')] * row['retorno']

                    df_acumulado_fundo.at[ind, 'retorno_acumulado'] = prod
                df_acumulado_fundo = df_acumulado_fundo[[
                    'data', 'fundo', 'retorno_acumulado']]

            df['retorno_ponderado'] = df.apply(
                lambda x: (x['peso_ifix']/100*x['retorno']), axis=1)
            df_setor = df.groupby(['data', 'setor'])[
                'peso_ifix', 'retorno_ponderado'].sum().reset_index()
            df_setor['retorno_setor'] = df_setor['retorno_ponderado'] / \
                (df_setor['peso_ifix']/100)
            df_setor = df_setor[df_setor['retorno_ponderado'] != 0]

            if setores:
                df_acumulado_setor = df_setor[df_setor['setor'].isin(
                    setores)][['data', 'setor', 'retorno_setor']]
                for ind, row in df_acumulado_setor.iterrows():
                    data = row['data']
                    data_d1 = mutil.somar_dia_util(data, -1)
                    setor = row['setor']
                    if not setor in calc_fundos:
                        calc_fundos[setor] = {}
                    if not data_d1.strftime('%d%m%Y') in calc_fundos[setor]:
                        prod = math.prod(df_acumulado_setor[(df_acumulado_setor['data'] <= data) & (
                            df_acumulado_setor['setor'] == setor)]['retorno_setor'].tolist())
                        calc_fundos[setor][data.strftime('%d%m%Y')] = prod
                    else:
                        prod = calc_fundos[setor][data_d1.strftime(
                            '%d%m%Y')] * row['retorno_setor']
                    df_acumulado_setor.at[ind, 'retorno_acumulado'] = prod
                df_acumulado_setor = df_acumulado_setor[[
                    'data', 'setor', 'retorno_acumulado']]
                df_acumulado_setor = df_acumulado_setor.rename(
                    columns={'setor': 'fundo'})

            if setores and fundos:
                df_historico = pd.concat(
                    [df_acumulado_fundo, df_acumulado_setor], ignore_index=True)
            if fundos and not setores:
                df_historico = df_acumulado_fundo
            if setores and not fundos:
                df_historico = df_acumulado_setor

            if fundos or setores:
                df_historico['retorno_acumulado'] = df_historico['retorno_acumulado']*100
                df_historico = df_historico.rename(
                    columns={'data': 'Data', 'retorno_acumulado': 'Retorno Acumulado', 'fundo': 'Fundo'})

            df_acumulado = df_setor.groupby(
                ['setor'])['retorno_setor'].prod().reset_index()
            df_acumulado = df_acumulado.rename(
                columns={'setor': 'Setor', 'retorno_setor': 'Retorno Acumulado'})
            df_acumulado['Retorno Acumulado'] = df_acumulado['Retorno Acumulado'].apply(
                lambda x: (x-1)*100)
            df_acumulado = df_acumulado.sort_values(
                ['Setor'], ascending=[True])
            col1, col2, _ = st.columns([1, 2, 1])
            custom_css = {
            ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
            ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
            ".ag-row":  {  "font-size": "16px !important;"}
            }


            gb = GridOptionsBuilder.from_dataframe(df_acumulado)
            gb.configure_grid_options(enableCellTextSelection=True)
            gb.configure_grid_options(ensureDomOrder=True)
            gb = gb.build()
            gb['columnDefs'] = [
                {'field': 'Setor'},
                {'field': 'Retorno Acumulado', 'headerName': 'Retorno',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%'"}]

            with col1:
                new_df = AgGrid(
                    df_acumulado,
                    gridOptions=gb,
                    update_mode='NO_UPDATE',
                    fit_columns_on_grid_load=True,
                    allow_unsafe_jscode=True,
                    enableRangeSelection=True,
                    custom_css=custom_css,
                    height=400,
                    enable_enterprise_modules=True)

            df_fundos = df.groupby(['fundo', 'setor'])['peso_ifix', 'retorno'].agg(
                {'retorno': 'prod', 'peso_ifix': 'mean'}).reset_index()
            df_fundos['retorno'] = df_fundos['retorno'].apply(
                lambda x: (x-1)*100 if x != 1 and (x-1)*100 != -100 else None)
            df_fundos = df_fundos.rename(
                columns={'fundo': 'Fundo', 'retorno': 'Retorno'})
            df_fundos = df_fundos.sort_values(['peso_ifix'], ascending=[False])
            gb = GridOptionsBuilder.from_dataframe(df_fundos)
            gb.configure_grid_options(enableCellTextSelection=True)
            gb.configure_grid_options(ensureDomOrder=True)
            gb = gb.build()
            gb['columnDefs'] = [
                {'field': 'Fundo'}, {'field': 'setor', 'headerName': 'Setor'},
                {'field': 'peso_ifix', 'headerName': 'Peso no IFIX',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%'"},
                {'field': 'Retorno',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%'"}]

            with col2:
                new_df = AgGrid(
                    df_fundos,
                    gridOptions=gb,
                    update_mode='NO_UPDATE',
                    fit_columns_on_grid_load=True,
                    allow_unsafe_jscode=True,
                    enableRangeSelection=True,
                    custom_css=custom_css,
                    height=400,
                    enable_enterprise_modules=True)

            if fundos or setores:
                df_historico = df_historico.sort_values(
                    ['Data'], ascending=[True])
                fig = px.line(df_historico, x="Data", y="Retorno Acumulado", color='Fundo',
                              title=f'Índice Acumulado', markers=True, symbol="Fundo")
                fig.update_layout(font=dict(size=15),
                                  legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.6,
                    xanchor="auto"
                ),
                    hovermode="x unified",
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=16))
                fig.update_xaxes(dtick="M1", title='', tickformat="%m/%Y")
                fig.update_traces(hovertemplate="<br>Data: %{x|%d/%m/%Y}<br>"
                                                "Índice acumulado: %{y:.2f}<br>"
                                  )
                st.plotly_chart(fig, use_container_width=True,
                                )


def curva_di(database):
    col1, col2 = st.columns([1, 4])
    with col1:
        st.subheader(f"Curva DI")
        data = st.date_input('Data', key='egv')
        if data:
            df = get_curva_di(database, data)
            util.download_excel_button(
                [df], ['Curva DI'], 'Download em Excel', 'curva_di')

    with col2:
        fig = px.line(df, x="Dias Úteis", y="Taxa", title=f'Curva DI para o dia {data.strftime("%d/%m/%Y")}',
                      labels={
                          "Dias Úteis": "Dias Úteis",
                          "Taxa": "Taxa"
                      },)
        fig.update_layout(font=dict(size=15))
        st.plotly_chart(fig, use_container_width=True, )


def curva_ntnb(database):
    col1, col2 = st.columns([1, 4])
    with col1:
        st.subheader(f"Curva NTN-B")
        data = st.date_input('Data')
        if data:
            df = get_curva_ntnb(database, data, dataframe=True)
            util.download_excel_button(
                [df], ['Curva NTN-B'], 'Download em Excel', 'curva_ntnb')

    with col2:
        fig = px.line(df, x="Duration", y="Taxa", title=f'Curva NTN-B para o dia {data.strftime("%d/%m/%Y")}',
                      labels={
                          "Dias Úteis": "Dias Úteis",
                          "Taxa": "Taxa"
                      },)
        fig.update_layout(font=dict(size=15))
        st.plotly_chart(fig, use_container_width=True, )


def ipca(database):
    st.subheader(f"Índices de inflação")
    data = datetime.now() + relativedelta(months=-12)
    data = datetime(data.year, data.month, 1).strftime('%Y-%m-%d')
    dados_ipca = database.query_select(
        f"select data, percentual from icatu.historico_ipca where data >= '{data}'")
    dados_igpm = database.query_select(
        f"select data, percentual from icatu.historico_igpm where data >= '{data}'")
    df_ipca = pd.DataFrame(dados_ipca, columns=['Data',  'Percentual'])
    df_igpm = pd.DataFrame(dados_igpm, columns=['Data',  'Percentual'])
    historico_ipca = database.query_select(
        f"select data, indice_acum, indice_mes, percentual from icatu.historico_ipca order by data")
    historico_igpm = database.query_select(
        f"select data, indice_acum, indice_mes, percentual from icatu.historico_igpm order by data")
    ipca_proj = database.query_select(
        f"select data, projecao, indice, tipo from icatu.ipca_proj order by data")
    igpm_proj = database.query_select(
        f"select data, projecao, indice, tipo from icatu.igpm_proj order by data")
    historico_ipca = pd.DataFrame(historico_ipca, columns=[
                                  'Data',  'Índice Acum', 'Índice Mês', 'Percentual'])
    historico_igpm = pd.DataFrame(historico_igpm, columns=[
                                  'Data',  'Índice Acum', 'Índice Mês', 'Percentual'])
    ipca_proj = pd.DataFrame(
        ipca_proj, columns=['Data',  'Projeção', 'Índice', 'Tipo'])
    igpm_proj = pd.DataFrame(
        igpm_proj, columns=['Data',  'Projeção', 'Índice', 'Tipo'])
    util.download_excel_button(
        [historico_ipca, historico_igpm, ipca_proj, igpm_proj],
        ['IPCA', 'IGP-M', 'IPCA proj', 'IGP-M proj'],
        'Download em Excel', 'indices')
    df_ipca['Percentual'] = df_ipca['Percentual'].apply(
        lambda x: round(x/100, 4))
    df_igpm['Percentual'] = df_igpm['Percentual'].apply(
        lambda x: round(x/100, 4))
    fig_ipca = px.bar(df_ipca, x='Data', y='Percentual',
                      text_auto=True, title="IPCA nos últimos 12 meses")
    fig_ipca.layout.yaxis.tickformat = ',.2%'
    fig_ipca.update_layout(font=dict(size=15))
    fig_ipca.update_xaxes(title='')
    st.plotly_chart(fig_ipca, use_container_width=True, )
    fig_igpm = px.bar(df_igpm, x='Data', y='Percentual',
                      text_auto=True, title="IGP-M nos últimos 12 meses")
    fig_igpm.layout.yaxis.tickformat = ',.2%'
    fig_igpm.update_layout(font=dict(size=15))
    fig_igpm.update_xaxes(title='')
    st.plotly_chart(fig_igpm, use_container_width=True, )
