from datetime import date
from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit as st
import pandas as pd
import plotly.express as px
from views import util
from models import util as mutil
from models import automacao

@st.cache_resource(show_spinner=False)
def query_db(_database, query):
    return _database.query_select(query)

@st.cache_resource(show_spinner=False)
def get_curva_ntnb(_database, data=date.today()):
    return automacao.curva_ntnb_interpolada(_database, data)

def gerencial_previo(barra, database):
    previo(database, barra)

def previo(database, barra):
    st.title('Gerencial Prévio')
    menu = barra.selectbox('Selecione a tela', ['Conferir diferenças', 'Informações para o cálculo'])
    if menu == 'Conferir diferenças':
        st.subheader('Conferir diferenças')
        col1, col2, col3, col4, _ = st.columns([1, 2, 2, 2, 3])
        data = col1.date_input('Data', mutil.somar_dia_util(date.today(), -1), key=1)
        lista_ativos = [i[0].strip() for i in query_db(database, f"select distinct ativo from icatu.estoque_ativos where data = '{data}' order by ativo")]
        ativo = col2.multiselect('Ativo', lista_ativos, key='36')
        divergencias = col3.radio('Tipo de busca', ('Apenas divergências', 'Todos os ativos'), key='89')

        busca = 'and round(abs(((p.preco / g.preco) -1)*100)::numeric, 2) > 0.01'
        if divergencias == 'Todos os ativos': busca = ''  
        ativos = ''
        if ativo:  ativos = f"""AND g.codigo in ({", ".join([f"'{i}'" for i in ativo]) if len(ativo) > 1  else f"'{ativo[0]}'"})"""

        sql = f"""
        with taxas as (
            select distinct * from (
            select distinct codigo, data, preco, taxa, spread from icatu.taxas_ativos where fonte like '%CALCULADORA%' and data = '{data.strftime('%Y-%m-%d')}'
            union
            select distinct codigo, data, preco, taxa, spread from icatu.ativos_anbima where data = '{data.strftime('%Y-%m-%d')}') t  
        )

        SELECT 
            distinct 
            g.codigo, 
            em.empresa,
            case 
                when i.indice = 'DI' and i.percentual > 100 then '%CDI' 
                when i.indice = 'DI' and (i.percentual = 100 or i.percentual is null) then 'CDI+' 
                when i.indice = 'IPCA' then 'IPCA+' 
                when i.indice = 'IGP-M' then 'IGPM+'
                else indice 
            end as indice,
            g.spread as spread_estimado,
            t.spread as spread_observado,
            g.preco as preco_gerencial, 
            p.preco as preco_custodiante,
            p.fonte as fonte,
            abs(t.spread - g.spread) as diferenca_spread
        FROM icatu.gerencial_previo g
        left join icatu.estoque_ativos p on p.ativo = g.codigo and g.fonte = p.fonte
        left join taxas t on t.codigo = g.codigo and t.codigo = p.ativo and round(p.preco::numeric, 3) = round(t.preco::numeric, 3) 
        left join icatu.info_papeis i on i.codigo = g.codigo
        left join icatu.emissores em on em.cnpj = i.cnpj
        where p.data = '{data.strftime('%Y-%m-%d')}' and p.fonte <> 'BRITECH'
        and i.tipo_ativo <> 'BOND'
        and g.data = '{data.strftime('%Y-%m-%d')}'
        and g.codigo <> 'CVRDA6' {busca} {ativos}
        order by abs(t.spread - g.spread) desc"""

        dados = query_db(database,(sql))

        df = pd.DataFrame(dados, columns=['Código', 'Emissor','Índice', 'Spread Estimado', 'Spread Observado', 'Preço Estimado', 'Preço Observado', 'Fonte', 'Diferença Spread'])        
        
        custom_css = {
        ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
        ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
        '.ag-header-group-cell': {"background-color": "#2E96BF","color": "white"},
        ".ag-row":  {  "font-size": "16px !important;"}
        }

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_grid_options(enableRangeSelection=True, tooltipShowDelay=0)
        gb.configure_grid_options(enableCellTextSelection=True)
        gb  = gb.build()
        gb['columnDefs'] = [
                {'field': 'Código','pinned': 'left'},{'field': 'Emissor'},{'field': 'Índice'},
                { 'field': 'Spread Estimado', 
                'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 3, minimumFractionDigits:3});",
                "type": ["numericColumn","numberColumnFilter","customNumericFormat"]},
                { 'field': 'Spread Observado', 
                'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 3, minimumFractionDigits:3});",
                "type": ["numericColumn","numberColumnFilter","customNumericFormat"]},
                { 'field': 'Preço Estimado', 
                'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 6, minimumFractionDigits:6});",
                "type": ["numericColumn","numberColumnFilter","customNumericFormat"]},
                { 'field': 'Preço Observado', 
                'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 6, minimumFractionDigits:6});",
                "type": ["numericColumn","numberColumnFilter","customNumericFormat"]},
                {'field': 'Fonte'},
                { 'field': 'Diferença Spread', 
                'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2});",
                "type": ["numericColumn","numberColumnFilter","customNumericFormat"]}]
        st.text('')
        df = AgGrid(
            df, key='gerencial_previo',
            gridOptions=gb,
            reload_data=True,
            fit_columns_on_grid_load=False,
            custom_css=custom_css,
            update_mode='NO_UPDATE',
            allow_unsafe_jscode=True,
            enable_enterprise_modules=True)
            
    
    if menu == 'Informações para o cálculo':
        st.subheader('Informações para o cálculo')
        col1, col2, col3, col4, _ = st.columns([1, 2, 2, 2, 3])
        data = col1.date_input('Data', mutil.somar_dia_util(date.today(), -1), key=22)
        lista_ativos = [i[0].strip() for i in query_db(database, f"select distinct ativo from icatu.estoque_ativos where data = '{data}' order by ativo")]
        ativo = col2.multiselect('Ativo', lista_ativos, key='353')
        ativos = ''
        if ativo:  ativos = f"""where t.ativo in ({", ".join([f"'{i}'" for i in ativo]) if len(ativo) > 1  else f"'{ativo[0]}'"})"""

        sql = f"""
        with spreads as (
        select distinct * from (
        select codigo, data, taxa as taxa_ativo, round(duration*252) as duration, spread, 'ANBIMA' as fonte from icatu.ativos_anbima where data = '{data.strftime('%Y-%m-%d')}'
        union
        select codigo, data, taxa as taxa_ativo, round(duration*252) as duration, spread, fonte from icatu.taxas_ativos where data = '{mutil.somar_dia_util(data, -1).strftime('%Y-%m-%d')}'
        and codigo not in (select distinct codigo from icatu.ativos_anbima where data = '{data.strftime('%Y-%m-%d')}')
        and fonte like '%CALCULADORA%') t

        ),

        ativos as (
            select 
                distinct e.ativo, 
                s.data,
                s.taxa_ativo,
                s.duration, 
                s.spread,
                s.fonte
            from icatu.estoque_ativos e
            left join spreads s on s.codigo = e.ativo
            where e.data = '{mutil.somar_dia_util(data, -1).strftime('%Y-%m-%d')}'),

        taxas as (
            select 
                distinct a.*, 
                em.empresa,
                case 
                    when i.indice = 'DI' and i.percentual > 100 then '%CDI' 
                    when i.indice = 'DI' and (i.percentual = 100 or i.percentual is null) then 'CDI+' 
                    when i.indice = 'IPCA' then 'IPCA+' 
                    when i.indice = 'IGP-M' then 'IGPM+'
                    else indice 
                end as indice,
                case 
                    when i.indice in ('DI', 'PRÉ') then c.taxa
                    when i.indice in ('IPCA', 'IGP-M') then 0
                    else a.spread
                end as taxa_curva
  

            from ativos a
            left join icatu.curva_di c on c.dias_uteis = a.duration
            left join icatu.info_papeis i on i.codigo = a.ativo
            left join icatu.emissores em on em.cnpj = i.cnpj
            where c.data = '{mutil.somar_dia_util(data, 1).strftime('%Y-%m-%d')}' 
            order by ativo)


        select 
            *, 
            case 
                when t.indice = '%CDI' then ((power((1+taxa_curva/100), (1/252.0))*power((1+spread/100), (1/252.0)) -1) / ((power((1+taxa_curva/100), (1/252.0))-1)))*100
                when t.indice = 'CDI+' then spread
                else ((1+taxa_curva/100)*(1+spread/100)-1)*100
            end as taxa_calculo 
        from taxas t {ativos}
        """
        dados = query_db(database, sql)
        try:
            df = pd.DataFrame(dados, columns=['Código', 'Data', 'Taxa', 'Duration (Dias)', 'Spread', 'Fonte', 'Emissor', 'Índice', 'Taxa Curva', 'Taxa Estimada'])
            curva_ntnb = get_curva_ntnb(database, data)
            df['Taxa Curva'] = df.apply(lambda x: curva_ntnb[int(x['Duration (Dias)'])-1] if x['Índice'] in ['IPCA+', 'IGP-M+'] else x['Taxa Curva'] , axis=1)

            custom_css = {
                ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                '.ag-header-group-cell': {"background-color": "#2E96BF","color": "white"},
                ".ag-row":  {  "font-size": "16px !important;"}
                }

            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_grid_options(enableRangeSelection=True, tooltipShowDelay=0)
            gb.configure_grid_options(enableCellTextSelection=True)
            gb  = gb.build()
            gb['columnDefs'] = [
                    {'field': 'Código','pinned': 'left'},{'field': 'Emissor'},
                    {'field': 'Data','type':["dateColumnFilter","customDateTimeFormat"], 'custom_format_string':'dd/MM/yyyy'},
                    { 'field': 'Taxa', 
                    'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2});",
                    "type": ["numericColumn","numberColumnFilter","customNumericFormat"]},
                    { 'field': 'Duration (Dias)', 
                    'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 0, minimumFractionDigits:0});",
                    "type": ["numericColumn","numberColumnFilter","customNumericFormat"]},
                    { 'field': 'Spread', 
                    'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2});",
                    "type": ["numericColumn","numberColumnFilter","customNumericFormat"]},
                    {'field': 'Fonte', 'width': 400},{'field': 'Índice'},
                    { 'field': 'Taxa Curva', 
                    'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2});",
                    "type": ["numericColumn","numberColumnFilter","customNumericFormat"]},
                { 'field': 'Taxa Estimada', 
                    'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2});",
                    "type": ["numericColumn","numberColumnFilter","customNumericFormat"]}
                    ]
            
            st.text('')
            df = AgGrid(
                df, key='gerencial_previo2',
                gridOptions=gb,
                reload_data=True,
                fit_columns_on_grid_load=False,
                custom_css=custom_css,
                update_mode='NO_UPDATE',
                allow_unsafe_jscode=True,
                enable_enterprise_modules=True)

        except:
            st.caption('Houve um erro')