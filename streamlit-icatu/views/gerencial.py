from datetime import date, datetime, timedelta
import numpy as np
import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from views import util
from models import util as mutil
from models import taxas_lf
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import win32com.client as win32
import pythoncom
from pathlib import Path
import os
import base64
import shutil
from statistics import mean
from environment import *
from os import listdir
import xml.etree.ElementTree as ET
from models import automacao


def relatorio(barra, database):
    tipo = barra.selectbox("Selecione a ferramenta",
                           ('Conferir Preço e Taxa de Ativos',
                            'Posição dos Fundos',
                            'Preços e Taxas',
                            'Próximos Eventos',
                            'Cota dos Fundos',
                            'Estoque de Ativos',
                            'Carrego dos Fundos',
                            'Preços Ajustados',
                            'Conferir Pagamentos',
                            'Evolução de Taxas'))

    if tipo == 'Conferir Preço e Taxa de Ativos':
        conferir_ativos(database, barra)
    if tipo == 'Preços e Taxas':
        conferir_precos(database, barra)
    if tipo == 'Estoque de Ativos':
        estoque_ativos(database, barra)
    if tipo == 'Cota dos Fundos':
        cota_fundos(database, barra)
    if tipo == 'Próximos Eventos':
        proximos_eventos(database, barra)
    if tipo == 'Posição dos Fundos':
        posicao_fundos(database, barra)
    if tipo == 'Carrego dos Fundos':
        taxa_fundos(database, barra)
    if tipo == 'Preços Ajustados':
        precos_ajustados(database, barra)
    if tipo == 'Conferir Pagamentos':
        conferir_pagamentos_calculados(database, barra)
    if tipo == 'Evolução de Taxas':
        evolucao_taxas(database, barra)


@st.cache_resource(show_spinner=False)
def query_db(_database, query):
    return _database.query_select(query)


@st.cache_resource(show_spinner=False)
def query(_database, query):
    return _database.query(query)


def try_error(func):
    def wrapper(database, barra):
        try:
            return func(database, barra)
        except Exception as erro:
            print(erro)
            st.caption('Houve um erro.')
    return wrapper


def indexador(indice, taxa):
    try:
        if isinstance(indice, str) and indice.strip() == 'DI' and taxa > 100:
            return '%CDI'
        if isinstance(indice, str) and indice.strip() == 'DI' and taxa < 100:
            return 'CDI+'
        if isinstance(indice, str) and indice.strip() == 'IPCA':
            return 'IPCA+'
        if isinstance(indice, str) and indice.strip() == 'IGP-M':
            return 'IGPM+'
        else:
            return indice.strip() if isinstance(indice, str) else indice
    except:
        return 'Erro'

@try_error
def posicao_fundos(database, barra):
    st.title('Posição dos fundos')
    with st.form("my_form", clear_on_submit=False):
        col1, col2, _ = st.columns([1, 1, 5])
        data_inicial = col1.date_input('Data Inicial', mutil.somar_dia_util(date.today(), -1), key='confesdf')
        data_inicial_query = mutil.somar_dia_util(data_inicial, -1)
        data_inicial_query = data_inicial_query.strftime('%Y-%m-%d')
        data_final = col2.date_input('Data Final', mutil.somar_dia_util(date.today(), -1), key='sdf')
        data_final_query = data_final.strftime('%Y-%m-%d')
        col1, col2, col3 = st.columns([1, 1, 1])

        fundo = col1.multiselect('Fundo', [i[0].strip() for i in query_db(
                                                            database, 
                                            f"""select distinct nome from icatu.fundos 
                                            where tipo is not null order by nome""")])
        grupo = col1.multiselect('Grupo', 
                                 [i[0].strip() for i in query_db(
                                                        database, 
                                                        f"""select distinct nome 
                                                        from icatu.grupo_emissores order by nome""")])
        sql_empresas = """
            select distinct e.empresa 
            from icatu.emissores e
            join icatu.info_papeis i on i.cnpj = e.cnpj
            join icatu.estoque_ativos et on et.ativo = i.codigo
            order by e.empresa
        """
        lista_empresas = [i[0].strip() if i[0] is not None else '' for i in query_db(
            database, sql_empresas)]
        tipo = col2.multiselect('Tipo do Ativo', 
                                ('Debênture', 'Letra Financeira',
                                'FIDC', 'CRI', 'BOND', 'NC', 'CDB', 
                                'DPGE', 'FII', 'RDB', 'Fundo Listado'), key='jrt')
        indice = col3.multiselect('Índice', 
                                  ['CDI+', '%CDI', 'IPCA+', 'IGPM+', 'PRÉ'])
        setor = col3.multiselect('Setor', [i[0].strip() for i in query_db(
            database, f"select distinct nome from icatu.setores order by nome")])
        empresa = col2.multiselect('Emissor', lista_empresas)
        col1, col2 = st.columns([1, 3])
        ativo = col1.multiselect('Papel', [i[0].strip() for i in query_db(
            database, f"select distinct ativo from icatu.estoque_ativos order by ativo")])
        fonte = col2.multiselect('Fonte', 
                                 [i[0].strip() for i in query_db(
                                                            database, 
                                                                f"""select distinct fonte 
                                                                from icatu.estoque_ativos order by fonte"""
                                                                )], 
                                [i[0].strip() for i in query_db(
                                                            database, 
                                                            f"""select distinct fonte 
                                                            from icatu.estoque_ativos where fonte <> 'BRITECH'""")])
        pesquisa_indice = {'CDI+': 'DI', '%CDI': 'DI',
                           'IPCA+': 'IPCA', 'IGPM+': 'IGP-M', 'PRÉ': 'PRÉ'}
        col1, col2 = st.columns([1, 1])
        fic = col1.radio('Posições em cotas de fundos', 
                         ['Não explodir carteira', 
                         'Explodir carteira', 
                         'Somente posições em fundos'], 
                         horizontal=True)
        with col1:
            calcular = st.form_submit_button('Pesquisar')
        with st.expander('Colunas'):
            colunas_tabela = st.multiselect('Colunas', 
                                            ['ISIN', 'CNPJ', 'Razão Social', 'Código BRIT', 
                                             'Data de Emissão', 'Data de Vencimento', 
                                             'Índice', 'Taxa de Emissão', 'Fonte',
                                            'Emissor', 'Grupo', 'Setor', 'PL do Fundo', 
                                            '% do PL', 'Taxa', 'Duration', 'Spread', 'Fonte Taxa', 
                                            'FIC', 'Rating Ativo', 'Rating Emissor'], 
                                            key='1984')
            colunas_tabela = ['Fundo', 'Tipo do Ativo', 'Ativo', 'Data',
                              'Quantidade', 'Preço', 'Financeiro'] + colunas_tabela
        with st.expander('Ordenação'):
            col1, col2 = st.columns([1, 1])
            colunas = col1.multiselect('Colunas', 
                                       ['Fundo', 'Ativo', 'Tipo do Ativo', 'ISIN','Código BRIT', 'Data de Emissão', 
                                        'Data de Vencimento', 'Índice', 'Taxa de Emissão', 'Emissor', 'Grupo', 'Setor',
                                       'Data', 'Quantidade', 'Preço', 'Financeiro', 'Fonte', 'PL do Fundo', '% do PL',  
                                       'Taxa', 'Duration', 'Spread', 'Fonte Taxa'], 
                                       ['Ativo', 'Fundo', 'Financeiro'], key='234')
            ordem = col2.multiselect('Ordem', ['Crescente' if i % 2 == 0 else 'Decrescente' for i in range(
                22)], ['Crescente', 'Crescente', 'Decrescente'], key='dfv')

    if calcular and (ativo or empresa or tipo or indice or fundo or fonte):
        with st.spinner('Aguarde...'):
            ordenacao = ''
            colunas_ordem = {
                'Ativo': 'e.ativo',
                'ISIN': 'i.isin',
                'CNPJ': 'f.cnpj',
                'Razão Social': 'f.nome_xml',
                'Código BRIT': 'f.codigo_brit',
                'Data de Emissão': 'i.data_emissao',
                'Data de Vencimento': 'i.data_vencimento',
                'Tipo do Ativo': 'i.tipo_ativo',
                'Fundo': 'f.nome', 'Data': 'e.data',
                'Quantidade': 'round((e.preco * (quantidade_disponivel + quantidade_garantia))::numeric, 4)::float',
                'Preço': 'round(preco::numeric, 6)::float',
                'Financeiro': 'round((e.preco * (quantidade_disponivel + quantidade_garantia))::numeric, 2)::float',
                'Fonte': 'e.fonte',
                'Grupo': 'g.nome',
                'Emissor': 'em.empresa',
                'Setor': 's.nome',
                'Índice': 'indice',
                'Taxa de Emissão': 'taxa_emissao',
                'PL do Fundo': 'p.financeiro',
                '% do PL': 'perc_fundo',
                'Taxa': 't.taxa',
                'Duration': 't.duration',
                'Spread': 't.spread',
                'Fonte Taxa': 't.fonte'
            }

            if colunas:
                for i in range(len(colunas)):
                    temp = "desc" if ordem[i] == "Decrescente" else ''
                    ordenacao += f'{colunas_ordem[colunas[i]]} {temp}, '

            ativos, empresas, tipos, indices, fundos, fontes, grupos, setores = '', '', '', '', '', '', '', ''
            if ativo:
                ativos = f"""and e.ativo in ({", ".join([f"'{i}'" for i in ativo]) if len(ativo) > 1  else f"'{ativo[0]}'"})"""
            if empresa:
                empresas = f"""AND em.empresa in ({", ".join([f"'{i}'" for i in empresa]) if len(empresa) > 1  else f"'{empresa[0]}'"})"""
            if tipo:
                tipos = f"""AND i.tipo_ativo in ({", ".join([f"'{i}'" for i in tipo]) if len(tipo) > 1  else f"'{tipo[0]}'"})"""
            if indice:
                indices = f"""AND i.indice in ({", ".join([f"'{pesquisa_indice[i]}'" for i in indice]) if len(indice) > 1  else f"'{pesquisa_indice[indice[0]]}'"})"""
            if fundo:
                fundos = f"""AND f.nome in ({", ".join([f"'{i}'" for i in fundo]) if len(fundo) > 1  else f"'{fundo[0]}'"})"""
            if fonte:
                fontes = f"""AND e.fonte in ({", ".join([f"'{i}'" for i in fonte]) if len(fonte) > 1  else f"'{fonte[0]}'"})"""
            if grupo:
                grupos = f"""AND g.nome in ({", ".join([f"'{i}'" for i in grupo]) if len(grupo) > 1  else f"'{grupo[0]}'"})"""
            if setor:
                setores = f"""AND s.nome in ({", ".join([f"'{i}'" for i in setor]) if len(setor) > 1  else f"'{setor[0]}'"})"""

            if fic == 'Explodir carteira':
                fic = ''
            if fic == 'Não explodir carteira':
                fic = 'and (fic <> true or fic is null)'
            if fic == 'Somente posições em fundos':
                fic = 'and fic = true'

            query = f"""  
            with pl_fundos as (
                select 
                    fundo,
                    data,
                    cota * quantidade as financeiro
                from icatu.posicao_fundos
                where data between '{data_inicial_query}' and '{data_final_query}'),

            taxas as (
                select *,
                case 
                    when fonte = 'ANBIMA' then 1
                    when fonte like '%CALCULADORA%' or fonte = 'OUTROS' then 2
                    else 3
                end as rank_fonte
                from (
                    select distinct data, codigo, preco, taxa, duration, spread, 'ANBIMA' as fonte
                    from icatu.ativos_anbima WHERE data between '{data_inicial_query}' and '{data_final_query}'
                    union
                    select distinct data, codigo, preco, taxa, duration, spread, fonte
                    from icatu.taxas_ativos WHERE data between '{data_inicial_query}' and '{data_final_query}') t
            ),

            taxa_ativos as (
            select
                distinct
                data, 
                codigo,
                round(preco::numeric,2) as preco,
                (array_remove(array_agg(taxa order by rank_fonte), null))[1] as taxa,
                (array_remove(array_agg(duration order by rank_fonte), null))[1] as duration,
                (array_remove(array_agg(spread order by rank_fonte), null))[1] as spread,
                (array_remove(array_agg(case 
                        when fonte like '%CALCULADORA%' then 'CALCULADORA' 
                        else fonte end
                        order by rank_fonte), null))[1] as fonte
            from taxas
            WHERE data between '{data_inicial_query}' and '{data_final_query}'
            group by data, codigo, round(preco::numeric,2))

            select 
                distinct 
                f.nome,
                i.tipo_ativo,
                i.isin,
                f.cnpj,
                f.nome_xml,
                f.codigo_brit,
                i.data_emissao,
                i.data_vencimento,
                case 
                    when i.indice = 'DI' and percentual > 100 then '%CDI' 
                    when i.indice = 'DI' and (percentual = 100 or percentual is null) then 'CDI+' 
                    when i.indice = 'IPCA' then 'IPCA+' 
                    when i.indice = 'IGP-M' then 'IGPM+'
                    else i.indice 
                end as indice,
                case 
                    when i.indice = 'DI' and percentual > 100 then i.percentual
                    else juros 
                end as taxa_emissao,                    
                ativo, 
                e.data, 
                round((quantidade_disponivel + quantidade_garantia)::numeric, 4)::float as qtd_adm, 
                round(e.preco::numeric, 6)::float as preco, 
                round((e.preco * (quantidade_disponivel + quantidade_garantia))::numeric, 2)::float  as financeiro, 
                e.fonte,
                fic,
                case when e.fonte = 'BRITECH' then 1 else 0 end as ordem_fonte,
                em.empresa,
                g.nome,
                s.nome,
                p.financeiro as pl_fundo,
                round((e.preco * (quantidade_disponivel + quantidade_garantia))::numeric, 2)::float / p.financeiro as perc_fundo,
                t.taxa,
                t.duration,
                t.spread,
                t.fonte,
                case when r.rating is null then 'Sem Rating' else
                    concat( r.rating, ' (',to_char(r.data, 'DD/MM/YY') , '  ', r.agencia, ')') end as rating_ativo,
                case when re.rating is null then 'Sem Rating' else
                    concat( re.rating, ' (',to_char(re.data, 'DD/MM/YY') , '  ', re.agencia, ')') end as rating_emissor
            from icatu.estoque_ativos e
            join icatu.fundos f on f.isin = e.fundo
            left join pl_fundos p on p.fundo = e.fundo and p.data = e.data
            left join icatu.info_papeis i on i.codigo = e.ativo
            left join icatu.emissores em on em.cnpj = i.cnpj
            left join icatu.setores s on s.id = em.setor
            left join icatu.grupo_emissores g on g.id = em.grupo
            left join taxa_ativos t on t.codigo = e.ativo and t.data = e.data and t.preco = round(e.preco::numeric, 2)
            left join icatu.view_ultimo_rating_ativos r on r.codigo = e.ativo
            left join icatu.view_ultimo_rating_emissores re on re.codigo = i.cnpj
            WHERE e.data between '{data_inicial_query}' and '{data_final_query}' {fic}
            {ativos} {tipos} {empresas} {indices} {fundos} {fontes} {setores} {grupos}
            order by {ordenacao} ordem_fonte
                        """
            lista = database.query_select(query)
            df = pd.DataFrame(lista, columns=['Fundo', 'Tipo do Ativo', 'ISIN', 'CNPJ', 'Razão Social', 'Código BRIT', 'Data de Emissão', 
                                                'Data de Vencimento', 'Índice', 'Taxa de Emissão', 'Ativo', 'Data',
                                                'Quantidade','Preço', 'Financeiro', 'Fonte', 'FIC', 'ordem_fonte', 'Emissor', 
                                                'Grupo', 'Setor', 'PL do Fundo', '% do PL', 'Taxa', 'Duration', 
                                                'Spread', 'Fonte Taxa', "Rating Ativo", 'Rating Emissor'])
            df = df[(df['Data'] >= data_inicial) & (df['Data'] <= data_final)]
            df['Ativo'] = df['Ativo'].apply(lambda x: x.strip())
            df['ISIN'] = df['ISIN'].apply(lambda x: x.strip() if x else None)
            df['Código BRIT'] = df['Código BRIT'].apply(lambda x: x.strip() if x else None)
            df['Índice'] = df['Índice'].apply(lambda x: x.strip() if x else None)
            df['FIC'] = df['FIC'].apply(lambda x: 'Sim' if x else 'Não')
            df = df.drop(columns=['ordem_fonte'])
            df_download = df.copy(deep=False)
            df['% do PL'] = df['% do PL'].apply(lambda x: x*100 if x else None) 
            df = df.drop_duplicates(['Ativo', 'Tipo do Ativo', 'Fundo', 
                                        'Data', 'Quantidade', 'Preço', 'Financeiro'], 
                                    keep='first')
            df = df[colunas_tabela]
            util.download_excel_button([df_download], ['ativos'], 'Download em Excel', 'posicao_ativos')

            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_column("Fundo", filter=True)
            gb.configure_column("Tipo do Ativo", filter=True)
            gb.configure_column("Ativo", filter=True)
            gb.configure_column("Data", 
                                type=["dateColumnFilter", "customDateTimeFormat"], 
                                custom_format_string='dd/MM/yyyy')

            if 'Data de Emissão' in colunas_tabela:
                gb.configure_column("Data de Emissão", type=["dateColumnFilter", "customDateTimeFormat"], custom_format_string='dd/MM/yyyy')
            if 'Taxa de Emissão' in colunas_tabela:
                gb.configure_column("Taxa de Emissão",
                                    type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                    valueFormatter="value.toLocaleString('pt-BR',{minimumFractionDigits: 2});")
            if 'Data de Vencimento' in colunas_tabela:
                gb.configure_column("Data de Vencimento", 
                                    type=["dateColumnFilter", "customDateTimeFormat"], 
                                    custom_format_string='dd/MM/yyyy')
            gb.configure_column("Financeiro", 
                                type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                valueFormatter="data.Financeiro.toLocaleString('pt-BR',{minimumFractionDigits: 2});")
            gb.configure_column("Preço",
                                type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                valueFormatter="data.Preço.toLocaleString('pt-BR',{minimumFractionDigits: 6});",
                                )
            gb.configure_column("Quantidade", 
                                type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                valueFormatter="data.Quantidade.toLocaleString('pt-BR',{minimumFractionDigits: 1});"
                                )
            if 'Taxa' in colunas_tabela:
                gb.configure_column("Taxa",
                                    type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                    valueFormatter="data.Taxa.toLocaleString('pt-BR',{minimumFractionDigits: 2});")
            if 'PL do Fundo' in colunas_tabela:
                gb.configure_column("PL do Fundo",
                                    type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                    valueFormatter="value.toLocaleString('pt-BR',{maximumFractionDigits: 0});")
            if '% do PL' in colunas_tabela:
                gb.configure_column("% do PL",
                                    type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                    valueFormatter="value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits: 2})+'%';")
            if 'Duration' in colunas_tabela:
                gb.configure_column("Duration",
                                    type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                    valueFormatter="data.Duration.toLocaleString('pt-BR',{minimumFractionDigits: 2});")
            if 'Spread' in colunas_tabela:
                gb.configure_column("Spread",
                                    type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                    valueFormatter="data.Spread.toLocaleString('pt-BR',{minimumFractionDigits: 2});")
            
            if 'FIC' in colunas_tabela: gb.configure_column("FIC",filter=True)
            if 'Rating Ativo' in colunas_tabela: gb.configure_column("Rating Ativo", filter=True)
            if 'Rating Emissor' in colunas_tabela: gb.configure_column("Rating Emissor", filter=True)
            if 'Código BRIT' in colunas_tabela: gb.configure_column("Código BRIT", filter=True)
            if 'CNPJ' in colunas_tabela: gb.configure_column("CNPJ", filter=True)
            if 'Razão Social' in colunas_tabela:gb.configure_column("Razão Social", filter=True)


            custom_css = {
                ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                ".ag-row":  {  "font-size": "16px !important;"},
                ".ag-row-footer" : {"background-color": "#0D6696 !important", "color": "white"},
                }

            gb.configure_grid_options(enableCellTextSelection=True)
            gb.configure_grid_options(ensureDomOrder=True)
            gb.configure_grid_options(editable=True)
            gb = gb.build()
            count_fundos = len(set([i for i in df['Fundo'].to_list()]))
            qtd = ''
            if (len(set([i for i in df['Ativo'].to_list()])) ==1 and
                len(set([i for i in df['Data'].to_list()])) ==1):
                qtd = df['Quantidade'].sum()
            gb['pinnedBottomRowData'] = [{
                    'Fundo': "Total (" + str(count_fundos)+ " Fundos)",
                    'Quantidade': qtd,
                    'Financeiro': df['Financeiro'].sum()
                    },
                ]
            new_df = AgGrid(
                df,
                gridOptions=gb,
                update_mode='NO_UPDATE',
                fit_columns_on_grid_load=True,
                allow_unsafe_jscode=True,
                enableRangeSelection=True,
                custom_css=custom_css,
                height=400,
                enable_enterprise_modules=True)


def conferir_ativos(database, barra):
    st.title('Conferir Preço e Taxa de Ativos')
    with st.form('form'):
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 2, 4, 2, 2])
        data_inicial = col1.date_input(
            'Data Inicial', mutil.somar_dia_util(date.today(), -1), key='conferir2')
        data_inicial = data_inicial.strftime('%Y-%m-%d')
        data_final = col2.date_input(
            'Data Final', mutil.somar_dia_util(date.today(), -1), key='conferir3')
        data_final = data_final.strftime('%Y-%m-%d')
        ativo = col5.multiselect('Papel', [i[0].strip() for i in query_db(
            database, f"select distinct ativo from icatu.estoque_ativos order by ativo")])
        lista_empresas = [i[0].strip() if i[0] is not None else '' for i in query_db(database, f"""select 
                                                                                            distinct em.empresa 
                                                                                        from icatu.emissores  em
                                                                                        join icatu.info_papeis i on i.cnpj = em.cnpj 
                                                                                        join icatu.estoque_ativos e on e.ativo = i.codigo 
                                                                                        order by em.empresa""")]
        empresa = col4.multiselect('Emissor', lista_empresas)
        tipo = col3.multiselect('Tipo do Ativo', ('Debênture', 'Letra Financeira',
                                'FIDC', 'CRI', 'BOND', 'NC', 'CDB', 'DPGE', 'FII', 'RDB', 'Fundo Listado'))
        indice = col6.multiselect(
            'Índice', ('CDI+', '%CDI', 'IPCA+', 'IGPM+', 'PRÉ'))
        pesquisa_indice = {'CDI+': 'DI', '%CDI': 'DI',
                           'IPCA+': 'IPCA', 'IGPM+': 'IGP-M', 'PRÉ': 'PRÉ'}
        calcular = st.form_submit_button('Pesquisar')

    if calcular and (ativo or empresa or tipo or indice):
        try:
            with st.spinner('Aguarde...'):
                vazio = st.empty()
                ativos_ativo, ativos_codigo, empresas, tipos, join_info_ativo, join_info_codigo, indices = '', '', '', '', '', '', ''
                if ativo:
                    ativos_ativo = f"""AND p.ativo in ({", ".join([f"'{i}'" for i in ativo]) if len(ativo) > 1  else f"'{ativo[0]}'"})"""
                    ativos_codigo = f"""AND p.codigo in ({", ".join([f"'{i}'" for i in ativo]) if len(ativo) > 1  else f"'{ativo[0]}'"})"""
                if empresa:
                    empresas = f"""AND em.empresa in ({", ".join([f"'{i}'" for i in empresa]) if len(empresa) > 1  else f"'{empresa[0]}'"})"""
                if tipo:
                    tipos = f"""AND i.tipo_ativo in ({", ".join([f"'{i}'" for i in tipo]) if len(tipo) > 1  else f"'{tipo[0]}'"})"""
                if indice:
                    indices = f"""AND i.indice in ({", ".join([f"'{pesquisa_indice[i]}'" for i in indice]) if len(indice) > 1  else f"'{pesquisa_indice[indice[0]]}'"})"""
                if empresa or tipo or indice:
                    join_info_ativo = """JOIN icatu.info_papeis i ON i.codigo = p.ativo left join icatu.emissores em on em.cnpj = i.cnpj"""
                    join_info_codigo = """JOIN icatu.info_papeis i ON i.codigo = p.codigo left join icatu.emissores em on em.cnpj = i.cnpj"""

                query = f"""    
                        (SELECT distinct
                            p.ativo as codigo, p.fonte, preco, p.data
                            FROM icatu.estoque_ativos p 
                            {join_info_ativo} 
                            WHERE p.data between '{data_inicial}' and '{data_final}' {ativos_ativo} {tipos} {empresas} {indices})
                        
                        union 

                        (SELECT distinct
                                p.codigo, 'ANBIMA' as fonte, preco, p.data
                                FROM icatu.ativos_anbima p 
                                {join_info_codigo} 
                                WHERE p.data between '{data_inicial}' and '{data_final}' {ativos_codigo} {tipos} {empresas} {indices})
                        ORDER BY codigo, data, fonte, preco
                            """

                lista = database.query_select(query)
                resposta = []

                for i in lista:
                    info = database.papel_info(i[0].strip())
                    juros = info['percentual'] if info['percentual'] > 100 else info['juros']
                    resposta.append((info['tipo_ativo'], i[0], info['emissor'],
                                    info['data_vencimento'], info['indice'], juros, i[3], i[1], i[2]))

                df_precos = pd.DataFrame(resposta, columns=[
                                         'Tipo do Ativo', 'Ativo', 'Emissor', 'Data de Vencimento', 'Índice', 'Taxa Emissão', 'Data', 'Fonte', 'Preço'])
                df_precos['Índice'] = df_precos.apply(
                    lambda x: indexador(x['Índice'], x['Taxa Emissão']), axis=1)
                if indice:
                    df_precos = df_precos[df_precos['Índice'].isin(indice)]

                ativos, empresas, tipos, join_info, indices = '', '', '', '', ''
                if ativo:
                    ativos = f"""AND p.codigo in ({", ".join([f"'{i}'" for i in ativo]) if len(ativo) > 1  else f"'{ativo[0]}'"})"""
                if empresa:
                    empresas = f"""AND em.empresa in ({", ".join([f"'{i}'" for i in empresa]) if len(empresa) > 1  else f"'{empresa[0]}'"})"""
                if tipo:
                    tipos = f"""AND i.tipo_ativo in ({", ".join([f"'{i}'" for i in tipo]) if len(tipo) > 1  else f"'{tipo[0]}'"})"""
                if indice:
                    indices = f"""AND i.indice in ({", ".join([f"'{pesquisa_indice[i]}'" for i in indice]) if len(indice) > 1  else f"'{pesquisa_indice[indice[0]]}'"})"""
                if empresa or tipo or indice:
                    join_info = """JOIN icatu.info_papeis i ON i.codigo = p.codigo  left join icatu.emissores em on em.cnpj = i.cnpj"""

                query = f"""    
                        (SELECT distinct
                            p.codigo, p.fonte, preco, taxa, duration, spread, p.data, pu_par
                            FROM icatu.taxas_ativos p 
                            {join_info} 
                            WHERE p.data between '{data_inicial}' and '{data_final}' {ativos} {tipos} {empresas} {indices})
                        
                        union 

                        (SELECT distinct
                                p.codigo, 'ANBIMA' as fonte, preco, taxa, duration, spread, p.data, pu_par
                                FROM icatu.ativos_anbima p 
                                {join_info} 
                                WHERE p.data between '{data_inicial}' and '{data_final}' {ativos} {tipos} {empresas} {indices})
                        ORDER BY codigo, fonte, data, taxa
                            """

                lista = database.query_select(query)
                resposta = []

                for i in lista:
                    info = database.papel_info(i[0].strip())
                    juros = info['percentual'] if info['percentual'] > 100 else info['juros']
                    try:
                        taxa = i[3]
                        duration = i[4]
                        spread = i[5]
                        pu_par = i[7]
                        resposta.append((info['tipo_ativo'], i[0], info['emissor'], info['data_vencimento'],
                                        info['indice'], juros, i[6],  i[1],  i[2], taxa, duration, spread, pu_par))
                    except:
                        resposta.append((info['tipo_ativo'], i[0], info['emissor'], info['data_vencimento'],
                                        info['indice'], juros, i[6], i[1],  i[2], 'Erro', 'Erro', 'Erro', 'Erro'))

                df_taxas = pd.DataFrame(resposta, columns=['Tipo do Ativo', 'Ativo', 'Emissor', 'Data de Vencimento',
                                        'Índice', 'Taxa Emissão', 'Data', 'Fonte',  'Preço',   'Taxa',  'Duration', 'Spread', 'PU Par'])
                df_taxas['Índice'] = df_taxas.apply(
                    lambda x: indexador(x['Índice'], x['Taxa Emissão']), axis=1)
                df_taxas['% Par'] = df_taxas.apply(lambda x: (
                    x['Preço'] / x['PU Par'])*100 if x['PU Par'] else None, axis=1)
                df_precos['Ativo'] = df_precos['Ativo'].apply(
                    lambda x: x.strip())
                if indice:
                    df_taxas = df_taxas[df_taxas['Índice'].isin(indice)]

                df_precos_download, df_taxas_download = df_precos.copy(
                    deep=False), df_taxas.copy(deep=False)
                df_taxas_download['% Par'] = df_taxas_download['% Par'].apply(
                    lambda x: x/100 if x else None)
                util.download_excel_button([df_precos_download, df_taxas_download], [
                                           'Preços', 'Taxas'], 'Download em Excel', 'precos_taxas')
                df_taxas = df_taxas.drop(
                    columns=['PU Par', 'Emissor', 'Data de Vencimento'])
                df_precos = df_precos.drop(
                    columns=['Emissor', 'Data de Vencimento'])
                df_precos['Ativo'] = df_precos['Ativo'].apply(
                    lambda x: x.strip())

                st.subheader('Preços')
                gb = GridOptionsBuilder.from_dataframe(df_precos)
                gb.configure_grid_options(enableRangeSelection=True)
                gb.configure_grid_options(enableCellTextSelection=True)
                gb = gb.build()
                gb['columnDefs'] = [
                    {'field': 'Tipo do Ativo', 'headerName': 'Tipo', 'filter': True}, 
                    { 'field': 'Ativo', 'filter': True}, {'field': 'Índice', 'filter': True},
                    {'field': 'Taxa Emissão', 'headerName': 'Emissão',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2})+'%'"},
                    {'field': "Data", 'type': [
                        "dateColumnFilter", "customDateTimeFormat"], 'custom_format_string': 'dd/MM/yyyy'},
                    {'field': 'Fonte'},
                    {'field': 'Preço',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6});"}]

                custom_css = {
                    ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                    ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                    ".ag-row":  {  "font-size": "16px !important;"}
                    }


                new_df = AgGrid(
                    df_precos,
                    gridOptions=gb,
                    update_mode='NO_UPDATE',
                    fit_columns_on_grid_load=True,
                    allow_unsafe_jscode=True,
                    enableRangeSelection=True,
                    custom_css=custom_css,
                    height=400,
                    enable_enterprise_modules=True)

                vazio.progress(1)
                vazio.empty()

                st.subheader('Taxas')
                gb = GridOptionsBuilder.from_dataframe(df_taxas)
                gb.configure_grid_options(enableRangeSelection=True)
                gb.configure_grid_options(enableCellTextSelection=True)
                gb = gb.build()
                gb['columnDefs'] = [
                    {'field': 'Tipo do Ativo', 'headerName': 'Tipo', 'filter': True}, 
                    {'field': 'Ativo', 'filter': True},
                    {'field': 'Índice', 'filter': True},
                    {'field': 'Taxa Emissão', 'headerName': 'Emissão', 'filter': True,
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2})+'%'"},
                    {'field': "Data", 'type': [
                        "dateColumnFilter", "customDateTimeFormat"], 'custom_format_string': 'dd/MM/yyyy'},
                    {'field': 'Fonte', 'filter': True,'width': 400},
                    {'field': 'Preço',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6});"},
                    {'field': 'Taxa',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 4, maximumFractionDigits: 4})+'%';"},
                    {'field': 'Duration',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                    {'field': 'Spread',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%';"},
                    {'field': '% Par',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%';"}]

                new_df = AgGrid(
                    df_taxas,
                    gridOptions=gb,
                    update_mode='NO_UPDATE',
                    fit_columns_on_grid_load=True,
                    allow_unsafe_jscode=True,
                    enableRangeSelection=True,
                    custom_css=custom_css,
                    height=400,
                    enable_enterprise_modules=True)

        except Exception as erro:
            print(erro)
            vazio.empty()
            st.caption("Houve um erro")


def conf_precos(database):
    st.subheader('Conferir Preços')
    col1, col2, col3, col4, col5 = st.columns([3, 4, 9, 5, 3])
    data = col1.date_input('Data', mutil.somar_dia_util(date.today(), -1))
    data = data.strftime('%Y-%m-%d')
    lista_ativos = [i[0].strip() for i in query_db(
        database, f"select distinct ativo from icatu.estoque_ativos where data = '{data}' order by ativo")]
    lista_fontes = [i[0].strip() for i in query_db(
        database, f"select distinct fonte from icatu.estoque_ativos order by fonte")]
    fonte = col3.multiselect('Fonte', ['ANBIMA']+lista_fontes)
    ativo = col2.multiselect('Ativo', lista_ativos)
    gerar = col1.button('Gerar informações', key='234')
    divergencias = col4.radio(
        'Tipo de busca', ('Apenas divergências', 'Todos os ativos'), key='divergencias')
    busca = 'HAVING coalesce(round((((max(preco)/min(preco))-1)*100)::numeric,2)::float, 0) > 0.01'
    ativos, fontes = '', ''
    if ativo:
        ativos = f"""AND p.ativo in ({", ".join([f"'{i}'" for i in ativo]) if len(ativo) > 1  else f"'{ativo[0]}'"})"""
    if divergencias == 'Todos os ativos':
        busca = ''
    if fonte:
        fontes = f"""AND p.fonte in ({", ".join([f"'{i}'" for i in fonte]) if len(fonte) > 1  else f"'{fonte[0]}'"})"""

    if gerar:
        sql = f'''
        with precos as (
            select 
            distinct data, ativo, preco, fonte from icatu.estoque_ativos 
            union
            select distinct data, codigo as ativo, preco, 'ANBIMA' as fonte from icatu.ativos_anbima)
        select 
            ativo, 
            tipo_ativo,
            count(distinct preco) as contagem, 
            min(preco) as preco_min, 
            max(preco) as preco_maximo, 
            coalesce(round(abs((((max(preco)/min(preco))-1)*100))::numeric,2)::float, 0) as divergencia,
            (array_agg(fonte order by preco))[1] as menor_preco_fonte, 
            (array_agg(fonte order by preco desc))[1] as maior_preco_fonte
            FROM precos p
            LEFT JOIN icatu.info_papeis i on i.codigo = p.ativo
            where data = '{data}' {ativos} {fontes}
            group by tipo_ativo, ativo
            {busca}
            order by divergencia desc, tipo_ativo desc'''

        dados = database.query_select(sql)
        dados = [list(i) for i in dados]
        for i in range(len(dados)):
            dados[i].append(dados[i][3])
            dados[i].append(dados[i][4])
            dados[i][3] = "{:,.6f}".format(dados[i][3]).replace(",", "x").replace(
                ".", ",").replace("x", ".") + f' ({dados[i][6]})'
            dados[i][4] = "{:,.6f}".format(dados[i][4]).replace(",", "x").replace(
                ".", ",").replace("x", ".") + f' ({dados[i][7]})'

        df = pd.DataFrame(dados, columns=['Ativo', 'Tipo', 'Contagem de preços', 'Preço Mínimo', 'Preço Máximo',
                          'Diferença Percentual', 'Menor Preço Fonte', 'Maior Preço Fonte', 'Menor Preço', 'Maior Preço'])
        hide_table_row_index = """
        <style>
        thead tr th:first-child {display:none}
        tbody th {display:none}
        </style>
        """
        st.markdown(hide_table_row_index, unsafe_allow_html=True)
        df['Ativo'] = df['Ativo'].apply(lambda x: x.strip())
        df_download = df.copy(deep=False)
        df_download = df_download[['Ativo', 'Tipo', 'Menor Preço', 'Menor Preço Fonte',
                                   'Maior Preço', 'Maior Preço Fonte', 'Diferença Percentual']]
        df = df.drop(columns=['Menor Preço Fonte',
                     'Maior Preço Fonte', 'Maior Preço', 'Menor Preço'])
        df['Diferença Percentual'] = df['Diferença Percentual'].apply(
            lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
        util.download_excel_button(
            [df_download], ['ativos'], 'Download em Excel', 'diferença_precos')
        st.table(df)


def conf_taxas(database):
    st.subheader('Conferir Taxas')
    col1, col2, col3, col4, col5 = st.columns([3, 4, 9, 5, 3])
    data = col1.date_input('Data', mutil.somar_dia_util(
        date.today(), -1), key='data_taxas')
    data = data.strftime('%Y-%m-%d')
    lista_fontes = [i[0].strip() for i in query_db(
        database, f"select distinct fonte from icatu.taxas_ativos order by fonte")]
    lista_ativos = [i[0].strip() for i in query_db(
        database, f"select distinct ativo from icatu.estoque_ativos where data = '{data}' order by ativo")]
    fonte = col3.multiselect('Fonte', lista_fontes + ['ANBIMA'], key='ioç')
    ativo = col2.multiselect('Ativo', lista_ativos, key='34')
    gerar = col1.button('Gerar informações', key='2456')
    divergencias = col4.radio(
        'Tipo de busca', ('Apenas divergências', 'Todos os ativos'), key='gh')
    busca = 'HAVING coalesce(round(abs(max(spread) - min(spread))::numeric,2)::float, 0) > 0.01'
    ativos, fontes = '', ''
    if ativo:
        ativos = f"""AND t.codigo in ({", ".join([f"'{i}'" for i in ativo]) if len(ativo) > 1  else f"'{ativo[0]}'"})"""
    if divergencias == 'Todos os ativos':
        busca = ''
    if fonte:
        fontes = f"""AND t.fonte in ({", ".join([f"'{i}'" for i in fonte]) if len(fonte) > 1  else f"'{fonte[0]}'"})"""

    if gerar:
        try:
            sql = f'''
            with taxas as (
                select * from
                (select codigo,data, taxa, duration, 'ANBIMA' as fonte, spread from icatu.ativos_anbima
                union
                select codigo, data, taxa, duration, fonte, spread from icatu.taxas_ativos) as tabela
                where data = '{data}'
            )

            select 
                t.codigo,
                tipo_ativo,
                count(distinct taxa) as contagem_taxa,
                min(taxa) as taxa_min, 
                max(taxa) as taxa_maximo,
                min(spread) as spread_min, 
                max(spread) as spread_maximo,
                coalesce(round(abs(max(spread) - min(spread))::numeric,2)::float, 0) as divergencia,
                (array_agg(t.fonte order by spread))[1] as menor_taxa_fonte, 
                (array_agg(t.fonte order by spread desc))[1] as maior_taxa_fonte
            from taxas t
            left join icatu.info_papeis i on i.codigo = t.codigo
            join icatu.estoque_ativos e on e.ativo = t.codigo
            where e.data = '{data}' and taxa <> 0 {ativos} {fontes}
            group by t.codigo, tipo_ativo
            {busca}
            order by divergencia desc
            '''

            dados = database.query_select(sql)
            dados = [list(i) for i in dados]
            for i in range(len(dados)):
                dados[i].append(dados[i][3])
                dados[i].append(dados[i][4])
                dados[i][3] = "{:,.2f}".format(dados[i][3]).replace(",", "x").replace(
                    ".", ",").replace("x", ".") + f' ({dados[i][8].replace("(", "").replace(")", "")})'
                dados[i][4] = "{:,.2f}".format(dados[i][4]).replace(",", "x").replace(
                    ".", ",").replace("x", ".") + f' ({dados[i][9].replace("(", "").replace(")", "")})'
                dados[i][5] = "{:,.2f}".format(dados[i][5]).replace(
                    ",", "x").replace(".", ",").replace("x", ".")
                dados[i][6] = "{:,.2f}".format(dados[i][6]).replace(
                    ",", "x").replace(".", ",").replace("x", ".")

            df = pd.DataFrame(dados, columns=['Ativo', 'Tipo', 'Contagem de taxas', 'Taxa Mínima', 'Taxa Máxima', 'Spread Mínimo',
                              'Spread Máximo', 'Diferença', 'Menor Taxa Fonte', 'Maior Taxa Fonte', 'Menor Taxa', 'Maior Taxa'])
            hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            df_download = df.copy(deep=False)
            df_download['Spread Mínimo'] = df_download['Spread Mínimo'].apply(
                lambda x: float(x.replace(',', '.')))
            df_download['Spread Máximo'] = df_download['Spread Máximo'].apply(
                lambda x: float(x.replace(',', '.')))
            df_download = df_download[['Ativo', 'Tipo', 'Menor Taxa', 'Menor Taxa Fonte',
                                       'Maior Taxa', 'Maior Taxa Fonte', 'Spread Mínimo', 'Spread Máximo', 'Diferença']]
            df['Diferença'] = df['Diferença'].apply(lambda x: "{:,.2f}".format(
                x).replace(",", "x").replace(".", ",").replace("x", "."))
            df = df.drop(
                columns=['Menor Taxa Fonte', 'Maior Taxa Fonte', 'Menor Taxa', 'Maior Taxa'])
            util.download_excel_button(
                [df_download], ['ativos'], 'Download em Excel', 'diferença_taxas')
            st.table(df)

        except:
            st.caption('Houve um erro')


def conf_durations(database):
    st.subheader('Conferir Durations')
    col1, col2, col3, col4, col5 = st.columns([3, 4, 9, 5, 3])
    data = col1.date_input(
        'Data', mutil.somar_dia_util(date.today(), -1), key='15')
    data = data.strftime('%Y-%m-%d')
    gerar = col1.button('Gerar informações', key='7896')
    lista_fontes = [i[0].strip() for i in query_db(
        database, f"select distinct fonte from icatu.taxas_ativos order by fonte")]
    lista_ativos = [i[0].strip() for i in query_db(
        database, f"select distinct ativo from icatu.estoque_ativos where data = '{data}' order by ativo")]
    ativo = col2.multiselect('Ativo', lista_ativos, key='36')
    fonte = col3.multiselect('Fonte', lista_fontes + ['ANBIMA'], key='ge')
    divergencias = col4.radio(
        'Tipo de busca', ('Apenas divergências', 'Todos os ativos'), key='89')
    busca = 'HAVING coalesce(round((((max(duration)/min(duration))-1)*100)::numeric,2)::float, 0) > 0.01'

    ativos, fontes = '', ''
    if ativo:
        ativos = f"""AND t.codigo in ({", ".join([f"'{i}'" for i in ativo]) if len(ativo) > 1  else f"'{ativo[0]}'"})"""
    if divergencias == 'Todos os ativos':
        busca = ''
    if fonte:
        fontes = f"""AND t.fonte in ({", ".join([f"'{i}'" for i in fonte]) if len(fonte) > 1  else f"'{fonte[0]}'"})"""

    if gerar:
        try:
            sql = f'''
            with durations as (
                select * from
                (select codigo,data, taxa, duration, 'ANBIMA' as fonte from icatu.ativos_anbima
                union
                select codigo, data, taxa, duration, fonte from icatu.taxas_ativos) as tabela
                where data = '{data}'
            )

            select 
                t.codigo,
                tipo_ativo,
                count(distinct duration) as contagem_duration,
                min(duration) as duration_min, 
                max(duration) as duration_maximo,
                coalesce(round(abs((((max(duration)/min(duration))-1)*100))::numeric,2)::float, 0) as divergencia, 
                (array_agg(t.fonte order by duration))[1] as menor_duration_fonte, 
                (array_agg(t.fonte order by duration desc))[1] as maior_duration_fonte
            from durations t
            left join icatu.info_papeis i on i.codigo = t.codigo
            join icatu.estoque_ativos e on e.ativo = t.codigo
            where e.data = '{data}' and duration <> 0 {ativos} {fontes}
            group by t.codigo, tipo_ativo
            {busca}
            order by divergencia desc
            '''

            dados = database.query_select(sql)
            dados = [list(i) for i in dados]
            for i in range(len(dados)):
                dados[i].append(dados[i][3])
                dados[i].append(dados[i][4])
                dados[i][3] = "{:,.2f}".format(dados[i][3]).replace(",", "x").replace(
                    ".", ",").replace("x", ".") + f' ({dados[i][6].replace("(", "").replace(")", "")})'
                dados[i][4] = "{:,.2f}".format(dados[i][4]).replace(",", "x").replace(
                    ".", ",").replace("x", ".") + f' ({dados[i][7].replace("(", "").replace(")", "")})'

            df = pd.DataFrame(dados, columns=['Ativo', 'Tipo', 'Contagem de Durations', 'Duration Mínima', 'Duration Máxima',
                              'Diferença Percentual', 'Menor Duration Fonte', 'Maior Duration Fonte', 'Maior Duration', 'Menor Duration'])
            hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            df_download = df.copy(deep=False)
            df_download = df_download[['Ativo', 'Tipo', 'Menor Duration', 'Menor Duration Fonte',
                                       'Maior Duration', 'Maior Duration Fonte', 'Diferença Percentual']]
            df['Diferença Percentual'] = df['Diferença Percentual'].apply(
                lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
            df = df.drop(columns=[
                         'Menor Duration Fonte', 'Maior Duration Fonte', 'Maior Duration', 'Menor Duration'])
            util.download_excel_button(
                [df_download], ['ativos'], 'Download em Excel', 'diferença_durations')
            st.table(df)
        except:
            st.caption('Houve um erro')


def taxas_calculadas(database):
    st.subheader('Taxas Calculadas')
    col1, col2, col3, col4, _ = st.columns([1, 2, 2, 2, 3])
    data = col1.date_input(
        'Data', mutil.somar_dia_util(date.today(), -1), key=1)
    datad1 = mutil.somar_dia_util(data, -1).strftime('%Y-%m-%d')
    data = data.strftime('%Y-%m-%d')
    tipo_ativo, lista_indexador, selecao_ativo = None, None, None
    lista_tipos = [i[0].strip() for i in query_db(
        database, f"select distinct tipo_ativo from icatu.info_papeis order by tipo_ativo")]
    tipo_ativo = col2.multiselect('Tipo de Ativo', lista_tipos, key=3)
    lista_indexador = col3.multiselect(
        'Índice', ['CDI+', '%CDI', 'IPCA+', 'IGPM+', 'PRÉ'], key=4)
    lista_ativos = [i[0].strip() for i in query_db(
        database, f"select distinct ativo from icatu.estoque_ativos where data = '{data}' order by ativo")]
    selecao_ativo = col4.multiselect('Ativo', lista_ativos, key=2)
    gerar_relatorio = st.button('Gerar relatório')

    if gerar_relatorio:
        try:
            with st.spinner("Aguarde..."):
                sql = f"""
                    with taxad1 as (
                    select * from (
                    select data, codigo, preco, taxa, duration, spread, fonte
                    from icatu.taxas_ativos 
                    union
                    select data, codigo, preco, taxa, duration, spread, 'ANBIMA' as fonte
                    from icatu.ativos_anbima) as dados
                    where data = '{datad1}' 

                    ),

                    taxad0 as (
                    select * from (
                    select data, codigo, preco, taxa, duration, spread, fonte, pu_par
                    from icatu.taxas_ativos 
                    union
                    select data, codigo, preco, taxa, duration, spread, 'ANBIMA' as fonte, pu_par
                    from icatu.ativos_anbima) as dados
                    where data = '{data}'

                    ),

                    dados as (
                        select 
                            d0.codigo, 
                            d0.fonte,
                            d0.preco,
                            d1.preco as precod1,
                            d1.taxa as taxad1,     
                            d0.taxa, 
                            d0.duration,
                            d1.duration as durationd1,
                            d1.spread as spreadd1,
                            d0.spread,
                            d0.pu_par
                        from taxad0 as d0
                        left join taxad1 as d1 on d1.codigo = d0.codigo and d1.fonte = d0.fonte
                        
                    ),

                    info as (
                        select 
                            codigo, 
                            tipo_ativo, 
                            e.empresa, 
                            data_vencimento, 
                            case 
                                when indice = 'DI' and percentual > 100 then '%CDI' 
                                when indice = 'DI' and (percentual = 100 or percentual is null) then 'CDI+' 
                                when indice = 'IPCA' then 'IPCA+' 
                                when indice = 'IGP-M' then 'IGPM+'
                                else indice end as indice,
                            case when percentual > 100 then percentual else juros end as taxa_emissao
                        from icatu.info_papeis i
                        left join icatu.emissores e on e.cnpj = i.cnpj

                    )

                    select distinct i.*,         
                            fonte,
                            preco,
                            precod1,
                            taxa, 
                            taxad1,     
                            duration,
                            durationd1,
                            spreadd1,
                            spread,
                            spread - spreadd1 as variacao_spread,
                            coalesce((taxa / nullif(taxad1,0)-1)*100, 0) as variacao_taxa,
                            pu_par
                    from dados d
                    left join info i on i.codigo = d.codigo
                    order by codigo, fonte, taxa"""

                dados = database.query_select(sql)
                df = pd.DataFrame(dados, columns=['Código do Ativo',
                                                  'Tipo do Ativo',
                                                  'Emissor',
                                                  'Data Vencimento',
                                                  'Índice',
                                                  'Taxa Emissão',
                                                  'Fonte',
                                                  'Preço',
                                                  'Preço D-1',
                                                  'Taxa',
                                                  'Taxa D-1',
                                                  'Duration',
                                                  'Duration D-1',
                                                  'Spread D-1',
                                                  'Spread',
                                                  'Variação Spread',
                                                  'Variação Taxa',
                                                  'PU Par'])
                df = df.dropna(subset=['Código do Ativo'])
                df = df.drop_duplicates()
                df = df.drop_duplicates(
                    ['Preço', 'Taxa', 'Duration', 'Taxa D-1'])
                df['Código do Ativo'] = df['Código do Ativo'].apply(
                    lambda x: x.strip())
                df['% do PAR'] = df.apply(
                    lambda x: x['Preço'] / x['PU Par'] if x['PU Par'] else None, axis=1)
                df['Índice'] = df['Índice'].apply(lambda x: x.strip())
                if selecao_ativo:
                    df = df[df['Código do Ativo'].isin(selecao_ativo)]
                if lista_indexador:
                    df = df[df['Índice'].isin(lista_indexador)]
                if tipo_ativo:
                    df = df[df['Tipo do Ativo'].isin(tipo_ativo)]
                df_download = df.copy(deep=False)
                df_download = df_download.drop(columns=['PU Par'])
                util.download_excel_button(
                    [df_download], [f'Taxas_{data}'], 'Download em Excel', f'Taxas_{data}')

                df_graficos = df_download[pd.to_numeric(
                    df_download['Spread'], errors='coerce').notnull()]
                df_graficos = df_graficos[pd.to_numeric(
                    df_graficos['Duration'], errors='coerce').notnull()]

                df_spread = df_graficos[pd.to_numeric(
                    df_graficos['Spread'], errors='coerce').notnull()]
                df_spread = df_spread[df_spread['Spread'] < 15]
                df_spread = df_spread[df_spread['Spread'] > -15]
                df_spread = df_spread.sort_values(
                    ['Spread'], ascending=[False]).head(8)
                df_spread = df_spread.drop_duplicates(
                    subset=['Código do Ativo'], keep='last')
                fig = px.bar(df_spread, x='Código do Ativo', y='Spread',
                             title='Top 8 Ativos com maior spread em pontos percentuais',
                             text_auto=True, color='Índice',
                             hover_data={
                                 "Código do Ativo": False,
                                 'Tipo do Ativo': True,
                                 "Índice": True,
                                 "Spread": True})
                fig.update_yaxes(title='')
                fig.update_layout(separators=',.', font=dict(
                    size=15), hovermode="x unified")

                st.plotly_chart(fig, use_container_width=True)

                df_variacao = df_graficos[pd.to_numeric(
                    df_graficos['Variação Spread'], errors='coerce').notnull()]
                df_variacao = df_variacao[df_variacao['Spread'] < 10]
                df_variacao = df_variacao[df_variacao['Spread'] > -10]
                df_variacao = df_variacao.sort_values(
                    ['Variação Spread'], ascending=[False]).head(8)
                df_variacao = df_variacao.drop_duplicates(
                    subset=['Código do Ativo'], keep='last')
                fig = px.bar(df_variacao, x='Código do Ativo', y='Variação Spread',
                             title='Top 8 Ativos com maior variação de spread em relação ao dia anterior em pontos percentuais',
                             text_auto=True, color='Índice',
                             hover_data={
                                 "Código do Ativo": False,
                                 'Tipo do Ativo': True,
                                 "Índice": True,
                                 "Spread": True})
                fig.update_layout(separators=',.', font=dict(
                    size=15), hovermode="x unified")
                fig.update_yaxes(title='')
                st.plotly_chart(fig, use_container_width=True)

                col1, col2 = st.columns([1, 1])
                df_mediana = df_graficos.groupby(
                    ['Índice'])[['Duration', 'Spread']].median().reset_index()
                fig = px.scatter(df_mediana, x="Duration", y="Spread",
                                 color='Índice',
                                 title='Mediana de spread/duration por Indexador')
                fig.update_traces(marker_size=20)
                fig.update_layout(separators=',.', font=dict(size=15))
                col1.plotly_chart(fig, use_container_width=True)

                df_mediana = df_graficos.groupby(['Tipo do Ativo'])[
                    ['Duration', 'Spread']].median().reset_index()
                df_mediana = df_mediana[df_mediana['Spread'] < 10]
                df_mediana = df_mediana[df_mediana['Spread'] > -10]
                fig = px.scatter(df_mediana, x="Duration", y="Spread",
                                 color='Tipo do Ativo',
                                 title='Mediana de spread/duration por Tipo de Ativo')
                fig.update_traces(marker_size=20)
                fig.update_layout(separators=',.', font=dict(size=15))
                col2.plotly_chart(fig, use_container_width=True)

                df_graficos = df_graficos[df_graficos['Spread'] < 10]
                df_graficos = df_graficos[df_graficos['Spread'] > -10]

                col1, col2 = st.columns([1, 1])
                fig_spread = px.box(df_graficos, x="Índice", y="Spread", color='Índice', title='Spread em pontos percentuais',
                                    hover_data={
                                        "Código do Ativo": True,
                                        'Tipo do Ativo': True,
                                        "Índice": False,
                                        "Spread": True})
                fig_spread.update_layout(separators=',.', font=dict(size=15))
                fig_spread.update_yaxes(title='')
                fig_spread.update_xaxes(title='')
                col1.plotly_chart(fig_spread, use_container_width=False)

                fig_duration = px.box(df_graficos, x="Índice", y="Duration", color='Índice', title='Duration em anos',
                                      hover_data={
                                          "Código do Ativo": True,
                                          'Tipo do Ativo': True,
                                          "Índice": False,
                                          "Spread": True})
                fig_duration.update_layout(separators=',.', font=dict(size=15))
                fig_duration.update_yaxes(title='')
                fig_duration.update_xaxes(title='')
                col2.plotly_chart(fig_duration, use_container_width=False)
        except:
            st.caption('Houve um erro')


def conferir_precos(database, barra):
    st.title('Preços e taxas dos ativos')
    menu = barra.selectbox('Selecione a tela', [
                           'Conferir Preços',  'Conferir Taxas', 'Conferir Durations', 'Taxas Calculadas', 'Conferir LFs'])
    if menu == 'Conferir Preços':
        conf_precos(database)
    if menu == 'Conferir Taxas':
        conf_taxas(database)
    if menu == 'Conferir Durations':
        conf_durations(database)
    if menu == 'Taxas Calculadas':
        taxas_calculadas(database)
    if menu == 'Conferir LFs':
        st.subheader('Conferir Letras Financeiras')
        tab1, tab2, tab3 = st.tabs(
            ['Conferir LF', 'Diferença de Preços', 'Conferir Taxas'])
        with tab1:
            conferir_lfs(barra, database)
        with tab2:
            conf_precos_lfs(barra, database)
        with tab3:
            conf_taxas_lfs(barra, database)


@try_error
def conf_taxas_lfs(barra, database):
    with st.form('sdf'):
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
        data = col1.date_input('Data', mutil.somar_dia_util(
            date.today(), -1), key='45654654')

        lista_ativos = [i[0].strip() for i in query_db(
            database, f"select distinct codigo from icatu.info_papeis where tipo_ativo = 'Letra Financeira'")]
        lista_ISIN = [i[0].strip() for i in query_db(
            database, f"select distinct isin from icatu.info_papeis where tipo_ativo = 'Letra Financeira' and (isin is not null and isin <> '')")]
        lista_emissores = [i[0].strip() for i in query_db(
            database, f"select distinct empresa from icatu.emissores where setor = 30 order by empresa")]

        isin = col3.multiselect('ISIN', lista_ISIN, key=23423)
        ativo = col2.multiselect('Ativo', lista_ativos, key=4434)
        emissor = col4.multiselect('Emissor', lista_emissores, key=55643)
        banda_dif = col1.number_input(
            'Dif. Spread Máxima', min_value=0.0, max_value=1.0, value=0.25)
        banda_anbima = col2.number_input(
            'Banda Duration Anbima', min_value=0.1, max_value=1.0, value=0.25)
        meses_venc_call = col3.number_input(
            'Banda Meses Vencimento', min_value=1, max_value=12, value=6, step=1)
        gerar = col1.form_submit_button('Gerar informações')

    if gerar:
        with st.spinner('Aguarde...'):

            relatorio = taxas_lf.consulta(
                database, data, meses_venc_call, banda_anbima, ativo, isin, emissor)
            df = relatorio.gerar()

            if len(df.index) < 1:
                st.caption('Não há dados para os filtros informados')
                return

            df_copia = df.copy()
            util.download_excel_button(
                [df_copia], ['LFs'], 'Download Excel', 'LFs_comparativo')
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_grid_options(enableRangeSelection=True)
            gb.configure_grid_options(enableCellTextSelection=True)
            gb = gb.build()
            dif_spread_style = JsCode(f"""
                function(params) {{
                    if (params.value > {banda_dif}) 
                    {{return {{ 'backgroundColor': '#ff6c6c', 'color': 'white','fontWeight': 'bold'  }} }} }};""")

            def if_call(coluna, coluna_banda, tipo):
                if tipo == 'max':
                    return f"params.data['{coluna}'] > (params.data['{coluna_banda}'] + {banda_dif}) && params.data['{coluna_banda}'] !== null"
                if tipo == 'min':
                    return f"params.data['{coluna}'] < (params.data['{coluna_banda}'] - {banda_dif}) && params.data['{coluna_banda}'] !== null"

            def spread_style(tipo): return JsCode(f"""
                function(params) {{
                    if (
                        ({if_call(f'Spread {tipo}','ATIVA Compra', 'max')}) ||
                        ({if_call(f'Spread {tipo}','BGC Compra', 'max')}) ||
                        ({if_call(f'Spread {tipo}','NECTON Compra', 'max')}) ||
                        ({if_call(f'Spread {tipo}','Spread Anbima', 'max')})
                        )
                    {{return {{ 'backgroundColor': '#ff6c6c', 'color': 'white','fontWeight': 'bold'  }} }}  
                    else if(
                        ({if_call(f'Spread {tipo}', 'ATIVA Venda', 'min')}) ||
                        ({if_call(f'Spread {tipo}', 'BGC Venda', 'min')}) ||
                        ({if_call(f'Spread {tipo}', 'NECTON Venda', 'min')}) ||
                        ({if_call(f'Spread {tipo}', 'Spread Anbima', 'min')})
                        ) 
                    {{ return {{ 'backgroundColor': '#2E96BF', 'color': 'white','fontWeight': 'bold' }}}}
                    }};""")

            corretoras = ['ATIVA', 'BGC', 'NECTON']
            colunas_corretoras = []
            for corretora in corretoras:
                colunas_corretoras += [
                    {'field': f'{corretora} Venda',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                    {'field': f'{corretora} Compra',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                    {'field': f'{corretora} Venc Ref.'}
                ]

            gb['columnDefs'] = [
                {'field': 'ISIN', 'pinned': 'left', 'filter': True}, 
                {'field': 'Emissor', 'pinned': 'left', 'filter': True},
                {'field': "Vencimento", 'pinned': 'left'},
                {'field':  'Duration', 'pinned': 'left',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                {'field':  'Spread Mínimo', 'cellStyle': spread_style('Mínimo'), 'pinned': 'left',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                {'field':  'Spread Máximo', 'cellStyle': spread_style('Máximo'), 'pinned': 'left',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                {'field': 'Índice', 'filter': True},
                {'field': 'Cód Spread Mín', 'cellStyle': spread_style('Mínimo')},
                {'field': 'Cód Spread Máx','cellStyle': spread_style('Máximo')},
                {'field': 'Dif Spread', 'cellStyle': dif_spread_style,
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%';"},
                {'field': '', 'headerName': '', },
                {'field': 'Spread Anbima',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
            ]+colunas_corretoras+[
                {'field': 'Negócio B3',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                {'field': "Negócio B3 Data", 'type': [
                    "dateColumnFilter", "customDateTimeFormat"], 'custom_format_string': 'dd/MM/yyyy'},

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
                fit_columns_on_grid_load=False,
                allow_unsafe_jscode=True,
                enableRangeSelection=True,
                custom_css=custom_css,
                height=400,
                enable_enterprise_modules=True)


@try_error
def conf_precos_lfs(barra, database):
    with st.form('sdfdf'):
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
        data = col1.date_input('Data', mutil.somar_dia_util(
            date.today(), -1), key='2csds')
        data = data.strftime('%Y-%m-%d')
        lista_ativos = [i[0].strip() for i in query_db(
            database, f"select distinct codigo from icatu.info_papeis where tipo_ativo = 'Letra Financeira'")]
        lista_ISIN = [i[0].strip() for i in query_db(
            database, f"select distinct isin from icatu.info_papeis where tipo_ativo = 'Letra Financeira' and (isin is not null and isin <> '')")]
        lista_emissores = [i[0].strip() for i in query_db(
            database, f"select distinct empresa from icatu.emissores where setor = 30 order by empresa")]

        isin = col3.multiselect('ISIN', lista_ISIN, key=954)
        ativo = col2.multiselect('Ativo', lista_ativos, key=9)
        emissor = col4.multiselect('Emissor', lista_emissores, key=19)
        gerar = col1.form_submit_button('Gerar informações')

    if gerar:
        with st.spinner('Aguarde...'):
            filtros, ativos, isins, emissores = '', '', '', ''
            if ativo:
                ativos = ','.join(f"'{i}'" for i in ativo)
                ativos = [i['codigo'] for i in database.query(
                    f'select codigo from icatu.info_papeis where isin in (select distinct isin from icatu.info_papeis where codigo in ({ativos}))')]
                ativos = ','.join(f"'{i}'" for i in ativos)
            if isin:
                isins = ','.join(f"'{i}'" for i in isin)
                isins = [i['codigo'] for i in database.query(
                    f'select codigo from icatu.info_papeis where isin in (select distinct isin from icatu.info_papeis where isin in ({isins}))')]
                isins = ','.join(f"'{i}'" for i in isins)

            if ativos or isin:
                filtros += f'and ativo in ({ativos+isins})'
            if emissor:
                emissores = ', '.join([f"'{i}'" for i in emissor])
                emissores = f'and em.empresa in ({emissores})'

            sql = f"""
                select 
                    i.isin, 
                    em.empresa as emissor, 
                    concat((array_agg(replace(e.ativo, ' ','') order by e.preco))[1],' (', (array_agg(e.fonte order by e.preco))[1],')') as codigo_min, 
                    (array_agg(spread order by e.preco))[1] as spread_min, 
                    min(e.preco) as preco_min, 
                    concat((array_agg(replace(e.ativo, ' ','') order by e.preco desc))[1],' (', (array_agg(e.fonte order by e.preco desc))[1],')') as codigo_max, 
                    (array_agg(spread order by e.preco desc))[1] as spread_max, 
                    max(e.preco) as preco_max, 
                    ((max(e.preco) / min(e.preco))-1)*100 as dif_perc,
                    abs((array_agg(spread order by e.preco desc))[1] - (array_agg(spread order by e.preco))[1]) as dif_spread
                from icatu.estoque_ativos e 
                left join icatu.info_papeis i on i.codigo = e.ativo
                left join icatu.emissores em on em.cnpj = i.cnpj 
                left join icatu.taxas_ativos t on t.codigo = e.ativo and t.data = e.data and round(e.preco::numeric, 2) = round(t.preco::numeric, 2)
                where e.data = '{data}' and tipo_ativo = 'Letra Financeira' and t.fonte like '%CALCULADORA%'
                {filtros} {emissores}
                group by i.isin, em.empresa order by (max(e.preco) / min(e.preco)-1)*100 desc
            """
            df = pd.DataFrame(database.query(sql))
            if len(df.index) < 1:
                st.caption('Não há dados para os filtros informados')
                return
            df['dif_perc'] = df['dif_perc'].apply(lambda x: round(x, 2))

            df = df.rename(columns={
                'isin': 'ISIN',
                'emissor': 'Emissor',
                'codigo_min': 'Código P.Mín',
                'preco_min': 'Preço Mínimo',
                'codigo_max': 'Código P.Máx',
                'preco_max': 'Preço Máximo',
                'dif_perc': 'Dif Preço Perc.',
                'spread_min': 'Spread P.Mín',
                'spread_max': 'Spread P.Máx',
                'dif_spread': 'Dif Spread'})
            util.download_excel_button(
                [df], ['LFS'], 'Download Excel', 'LFs_comparativo')
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_grid_options(enableRangeSelection=True)
            gb.configure_grid_options(enableCellTextSelection=True)
            gb = gb.build()
            gb['columnDefs'] = [
                {'field': 'ISIN', 'filter': True }, {'field': 'Emissor', 'filter': True },
                {'field': 'Código P.Mín', },
                {'field':  'Preço Mínimo',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                {'field':  'Código P.Máx', },
                {'field':  'Preço Máximo',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                {'field': 'Dif Preço Perc.', 'cellStyle': {'background-color': 'rgb(236, 240, 241)'},
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%';"},
                {'field': '', 'headerName': '', },
                {'field':  'Spread P.Mín',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%';"},
                {'field':  'Spread P.Máx',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%';"},
                {'field': 'Dif Spread',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%';"},

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
                fit_columns_on_grid_load=False,
                allow_unsafe_jscode=True,
                enableRangeSelection=True,
                custom_css=custom_css,
                height=400,
                enable_enterprise_modules=True)


@try_error
def conferir_lfs(barra, database):
    with st.form('fgn'):
        col1, col2, col3, _ = st.columns([1, 1, 1, 3])
        data = col1.date_input('Data', mutil.somar_dia_util(date.today(), -1))
        data = data.strftime('%Y-%m-%d')
        lista_ativos = [i[0].strip() for i in query_db(
            database, f"select distinct codigo from icatu.info_papeis where tipo_ativo = 'Letra Financeira'")]
        lista_ISIN = [i[0].strip() for i in query_db(
            database, f"select distinct isin from icatu.info_papeis where tipo_ativo = 'Letra Financeira' and (isin is not null and isin <> '')")]
        isin = col3.multiselect('ISIN', lista_ISIN)
        ativo = col2.multiselect('Ativo', lista_ativos)
        gerar = col1.form_submit_button('Gerar informações')

    if (ativo or isin) and (gerar or 'consulta_lf' in st.session_state and st.session_state['consulta_lf']):
        st.session_state['consulta_lf'] = True
        isins, ativos = '', ''
        if ativo:
            ativos = ','.join(f"'{i}'" for i in ativo)
            ativos = [i['codigo'] for i in database.query(
                f'select codigo from icatu.info_papeis where isin in (select distinct isin from icatu.info_papeis where codigo in ({ativos}))')]
            ativos = ','.join(f"'{i}'" for i in ativos)
        if isin:
            isins = ','.join(f"'{i}'" for i in isin)
            isins = [i['codigo'] for i in database.query(
                f'select codigo from icatu.info_papeis where isin in (select distinct isin from icatu.info_papeis where isin in ({isins}))')]
            isins = ','.join(f"'{i}'" for i in isins)

        df = pd.DataFrame(database.query(f"""select  distinct t.codigo, i.isin, e.empresa as emissor,
                                                case 
                                                when i.indice = 'DI' and percentual > 100 then '%CDI' 
                                                when i.indice = 'DI' and (percentual = 100 or percentual is null) then 'CDI+' 
                                                when i.indice = 'IPCA' then 'IPCA+' 
                                                when i.indice = 'IGP-M' then 'IGPM+'
                                                else i.indice 
                                            end as indice,
                                            t.data, t.preco, t.taxa, spread, t.duration, t.fonte from icatu.taxas_ativos t
                                            left join icatu.info_papeis i on i.codigo = t.codigo
                                            left join icatu.emissores e on e.cnpj = i.cnpj
                                            where data = '{data}' and t.codigo in ({ativos+isins})
                                            order by isin, t.codigo, fonte"""))

        gb = GridOptionsBuilder.from_dataframe(df)

        # Configure the grid options
        gb.configure_grid_options(enableRangeSelection=True)
        gb.configure_grid_options(enableCellTextSelection=True)

        # Configure each column individually
        gb.configure_column('codigo', header_name='Código', checkboxSelection=True)
        gb.configure_column('isin', header_name='ISIN')
        gb.configure_column('emissor', header_name='Emissor')
        gb.configure_column('indice', header_name='Índice')
        gb.configure_column("data", header_name='Data', type=["dateColumnFilter", "customDateTimeFormat"], custom_format_string='dd/MM/yyyy')
        gb.configure_column('preco', header_name='Preço', type=["numericColumn", "numberColumnFilter", "customNumericFormat"], valueFormatter="value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6});")
        gb.configure_column('taxa', header_name='Taxa', type=["numericColumn", "numberColumnFilter", "customNumericFormat"], valueFormatter="value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});")
        gb.configure_column('spread', header_name='Spread', type=["numericColumn", "numberColumnFilter", "customNumericFormat"], valueFormatter="value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});")
        gb.configure_column('duration', header_name='Duration', type=["numericColumn", "numberColumnFilter", "customNumericFormat"], valueFormatter="value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});")
        gb.configure_column('fonte', header_name='Fonte')

        # Now, configure selection
        gb.configure_selection('multiple', use_checkbox=True)

        # Finally, build the grid options
        gb = gb.build()

        custom_css = {
        ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
        ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
        ".ag-row": { "font-size": "16px !important;"}
        }


        new_df = AgGrid(
            df,
            gridOptions=gb,
            update_mode='SELECTION_CHANGED',
            fit_columns_on_grid_load=False,
            allow_unsafe_jscode=True,
            enableRangeSelection=True,
            custom_css=custom_css,
            height=400,
            enable_enterprise_modules=True)
        caminho_telas_cetip = os.path.join(r"\\ISMTZVANGUARDA", 'Dir-GestaodeAtivos$', 'Mesa Renda Fixa', '2. Boletas Crédito', 'Tela Cetip')
        telas = {}
        if not new_df['selected_rows'] is None:
            for ativo in [row['codigo'] for row in new_df['selected_rows']]:
                for root, dirs, files in os.walk(caminho_telas_cetip):
                    for name in files:
                        if ativo.lower() in name.lower():
                            tela = os.path.join(root, name)
                            telas[ativo] = tela
        for ativo in telas:
            if os.path.exists(telas[ativo]):
                with st.expander(ativo, expanded=True):
                    with open(telas[ativo], "rb") as pdf_file:
                        base64_pdf = base64.b64encode(
                            pdf_file.read()).decode('utf-8')

                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1000px" height="400px" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)


def estoque_ativos(database, barra):
    st.title('Conferir estoque de ativos')
    hide_table_row_index = """
    <style>
    thead tr th:first-child {display:none}
    tbody th {display:none}
    </style>
    """
    menu = barra.selectbox('Selecione a tela', [
                           'Consolidado por fundos', 'Relatório completo', 'Ativos não cadastrados', 'Conferir ISINs'])
    if menu == 'Consolidado por fundos':
        st.subheader('Consolidado por fundos')
        col1, col2, _ = st.columns([1, 3, 5])
        data = col1.date_input(
            'Data', mutil.somar_dia_util(date.today(), -1), key='1')
        divergencias = col2.radio(
            'Tipo de busca', ('Apenas divergências', 'Todos os fundos'), key='2')
        gerar = st.button('Gerar relatório', key='gerar_tab1')
        if gerar:
            data = data.strftime('%Y-%m-%d')
            dados = database.query_select(f'''with qtd_divergencias as (
                                        select 
                                            nome,  sum(case when diferenca > 0.01 then 1 else 0 end) as ativos_diferentes
                                        from(
                                            select 
                                                f.nome, 
                                                ativo,
                                                sum(case when fonte = 'BRITECH' THEN quantidade_garantia + quantidade_disponivel else 0 end) as quantidade_brit,
                                                sum(case when fonte <> 'BRITECH' THEN quantidade_garantia + quantidade_disponivel else 0 end) as quantidade_adm,
                                                round(abs(sum(case when fonte = 'BRITECH' THEN quantidade_garantia + quantidade_disponivel else 0 end) 
                                                    - sum(case when fonte <> 'BRITECH' THEN quantidade_garantia + quantidade_disponivel else 0 end))::numeric, 6) as diferenca
                                            from icatu.estoque_ativos e
                                            left join icatu.fundos f on f.isin = e.fundo
                                            where data = '{data}' 
                                            group by f.nome, ativo ) as lista
                                        group by nome)

                                    select 
                                        f.nome,
                                        c.nome_curto, 
                                        sum(case when fonte = 'BRITECH' and (quantidade_disponivel + quantidade_garantia) > 0 THEN 1 ELSE 0 END) as ativos_brit,
                                        sum(case when fonte <> 'BRITECH' and (quantidade_disponivel + quantidade_garantia) > 0 THEN 1 ELSE 0 END) as ativos_adm,
                                        abs(sum(case when fonte = 'BRITECH' and (quantidade_disponivel + quantidade_garantia) > 0 THEN 1 ELSE 0 END) 
                                            - sum(case when fonte <> 'BRITECH' and (quantidade_disponivel + quantidade_garantia) > 0 THEN 1 ELSE 0 END)) AS diferenca,
                                        q.ativos_diferentes
                                    from icatu.fundos f
                                    left join icatu.estoque_ativos e on e.fundo = f.isin
                                    left join qtd_divergencias q on q.nome = f.nome
                                    left join icatu.custodiantes c on c.cnpj = f.custodiante
                                    where e.data = '{data}' and (fic <> true or fic is null)
                                    group by f.nome, q.ativos_diferentes, c.nome_curto
                                    order by q.ativos_diferentes desc''')

            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            col1, _ = st.columns([3, 1])
            df = pd.DataFrame(dados, columns=['Nome do Fundo', 'Custodiante', 'Contagem Ativos BRITECH',
                              'Contagem Ativos ADM', 'Diferença na contagem', 'Ativos divergentes'])
            if divergencias == 'Apenas divergências':
                df = df[df['Ativos divergentes'] > 0]
            col1.table(df)

    if menu == 'Relatório completo':
        st.subheader('Relatório completo')
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
        data = col1.date_input('Data', mutil.somar_dia_util(date.today(), -1))
        data = data.strftime('%Y-%m-%d')
        lista_fundos = [i[0].strip() for i in query_db(
            database, f"select distinct f.nome from icatu.estoque_ativos e left join icatu.fundos f on f.isin = e.fundo where data = '{data}' order by nome")]
        lista_ativos = [i[0].strip() for i in query_db(
            database, f"select distinct ativo from icatu.estoque_ativos where data = '{data}' order by ativo")]
        lista_fontes = [i[0].strip() for i in query_db(
            database, f"select distinct fonte from icatu.estoque_ativos where fonte <> 'BRITECH' order by fonte")]

        fundo = col2.multiselect('Fundo', lista_fundos)
        tipo = col3.multiselect('Tipo do Ativo', ('Debênture', 'Letra Financeira',
                                'FIDC', 'CRI', 'BOND', 'NC', 'CDB', 'DPGE', 'FII', 'RDB', 'Fundo Listado'))
        ativo = col4.multiselect('Ativo', lista_ativos)
        fonte = col5.multiselect('Fonte', lista_fontes)
        divergencias = col6.radio(
            'Tipo de busca', ('Apenas divergências', 'Todos os ativos'))
        gerar_2 = st.button('Gerar relatório', key='gerar_tab2')
        if gerar_2:
            busca, fundos, ativos, fontes, tipos = '', '', '', '', ''
            if divergencias == 'Apenas divergências':
                busca = 'AND (round(abs(b.qtd_brit - a.qtd_adm)::numeric, 6) is null or round(abs(b.qtd_brit - a.qtd_adm)::numeric, 6) > 0.01)'

            if tipo:
                tipos = f"""AND i.tipo_ativo in ({", ".join([f"'{i}'" for i in tipo])if len(tipo) > 1  else f"'{tipo[0]}'"})"""
            if fundo:
                fundos = f"""AND f.nome in ({", ".join([f"'{i}'" for i in fundo])if len(fundo) > 1  else f"'{fundo[0]}'"})"""
            if ativo:
                ativos = f"""AND e.ativo in ({", ".join([f"'{i}'" for i in ativo]) if len(ativo) > 1  else f"'{ativo[0]}'"})"""
            if fonte:
                fontes = f"""AND a.fonte in ({", ".join([f"'{i}'" for i in fonte]) if len(fonte) > 1  else f"'{fonte[0]}'"})"""

            sql = f'''with qtd_brit as (
                    SELECT fundo, ativo, quantidade_disponivel + quantidade_garantia as qtd_brit
                    FROM icatu.estoque_ativos WHERE data ='{data}' and fonte = 'BRITECH'),

                    qtd_adm as (
                    SELECT fundo, ativo, quantidade_disponivel + quantidade_garantia as qtd_adm, fonte
                    FROM icatu.estoque_ativos WHERE data ='{data}' and fonte <> 'BRITECH' and (fic <> true or fic is null))

                    SELECT DISTINCT f.codigo_brit, f.nome, i.tipo_ativo, e.ativo, COALESCE(b.qtd_brit, 0), COALESCE(a.qtd_adm, 0), (round(abs(COALESCE(b.qtd_brit, 0) - COALESCE(a.qtd_adm, 0))::numeric, 6)::float / coalesce(a.qtd_adm, b.qtd_brit))*100 as diferenca, a.fonte
                    FROM icatu.estoque_ativos e
                    LEFT JOIN icatu.fundos f ON e.fundo = f.isin
                    LEFT JOIN qtd_brit b ON b.fundo = e.fundo AND b.ativo = e.ativo
                    LEFT JOIN qtd_adm a ON a.fundo = e.fundo AND a.ativo = e.ativo
                    LEFT JOIN icatu.info_papeis i ON i.codigo = e.ativo
                    WHERE data = '{data}' {busca} {fundos} {ativos} {fontes} {tipos}
                    AND NOT ((qtd_brit = 0  AND qtd_adm IS NULL) OR (qtd_brit IS NULL  AND qtd_adm = 0))
                    ORDER BY diferenca desc, codigo_brit, tipo_ativo, ativo'''

            dados = database.query_select(sql)
            df = pd.DataFrame(dados, columns=['Código BRIT', 'Nome do Fundo', 'Tipo do Ativo', 'Ativo',
                              'Quantidade BRIT', 'Quantidade Administrador', 'Diferença Percentual', 'Fonte'])
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            df_group = df.groupby(['Ativo', 'Tipo do Ativo'])[
                ['Quantidade BRIT', 'Quantidade Administrador']].sum().reset_index()
            if len(df_group.index) > 0:
                df_group['Diferença Percentual'] = df_group.apply(lambda x: (
                    (abs((x['Quantidade Administrador'] / x['Quantidade BRIT'])-1)*100) if x['Quantidade BRIT'] > 0 else 100), axis=1)
                df_group = df_group.sort_values(
                    ['Diferença Percentual'], ascending=[False])
                df_group['Quantidade BRIT'] = df_group['Quantidade BRIT'].apply(
                    lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                df_group['Quantidade Administrador'] = df_group['Quantidade Administrador'].apply(
                    lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                df_group['Diferença Percentual'] = df_group['Diferença Percentual'].apply(
                    lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
            st.subheader('Estoque total por ativo')
            col1, _ = st.columns([1.2, 1])
            col1.table(df_group)
            df['Quantidade BRIT'] = df['Quantidade BRIT'].apply(lambda x: "{:,.2f}".format(
                x).replace(",", "x").replace(".", ",").replace("x", "."))
            df['Quantidade Administrador'] = df['Quantidade Administrador'].apply(
                lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
            df['Diferença Percentual'] = df['Diferença Percentual'].apply(
                lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
            st.subheader('Estoque por ativo em cada fundo')
            st.table(df)

    if menu == 'Ativos não cadastrados':
        st.subheader('Ativos não cadastrados')
        gerar_3 = st.button('Gerar relatório', key='gerar_tab3')
        if gerar_3:
            col1, col2 = st.columns([1, 1])

            st.subheader('Ativos não cadastrados (Carteira Atual)')
            sql = f'''select distinct ativo 
                        from icatu.estoque_ativos 
                        where ativo not in (select distinct codigo from icatu.info_papeis)
                        and data = '{mutil.somar_dia_util(date.today(), -1).strftime('%Y-%m-%d')}'
                        and fonte <> 'BRITECH'
                        order by ativo'''
            dados = database.query_select(sql)
            col1, _ = st.columns([1, 4])
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            df = pd.DataFrame(dados, columns=['Código do ativo'])
            col1.table(df)

            st.subheader('Ativos não cadastrados (Carteira Antiga)')
            sql = f'''select distinct ativo 
                        from icatu.estoque_ativos 
                        where ativo not in (select distinct codigo from icatu.info_papeis)
                        and data < '{mutil.somar_dia_util(date.today(), -1).strftime('%Y-%m-%d')}'
                        and fonte <> 'BRITECH'
                        order by ativo'''
            dados = database.query_select(sql)
            col1, _ = st.columns([1, 4])
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            df = pd.DataFrame(dados, columns=['Código do ativo'])
            col1.table(df)

    if menu == 'Conferir ISINs':
        st.subheader('Conferir ISINs')
        col1, _ = st.columns([1, 6])
        data = col1.date_input('Data', mutil.somar_dia_util(date.today(), -1))
        dia = data.strftime('%d')
        mes = data.strftime('%m')
        ano = data.strftime('%Y')
        caminho = os.path.join(r'\\ISMTZVANGUARDA', 'Dir-GestaodeAtivos$', 'Controle', 'BackOffice', '01 - Atividades Diárias', '1.01 - XML', ano, mes, dia)
        gerar = st.button('Conferir')

        if gerar:
            dados = []
            with st.spinner('Aguarde...'):
                automacao.excluir_xml_vazio(2)
                arquivos = [f for f in listdir(
                    caminho) if f.lower().endswith(".xml")]
                ativos = {}
                codigo_fidcs = {i['isin'].strip(): i['codigo'].strip() for i in database.query(
                    "select isin, codigo from icatu.info_papeis where tipo_ativo = 'FIDC'")}
                cnpj_fundos = {i['cnpj'].strip(): i['nome'].strip() for i in database.query(
                    "select cnpj, nome from icatu.fundos  where tipo is not null ")}

                for arquivo in arquivos:
                    xml = ET.parse(caminho + '\\' + arquivo).getroot()
                    fundo = xml[0].find('header')
                    cnpj_fundo = fundo.find('cnpj').text if fundo.find(
                        'cnpj') is not None else ""
                    fundo = cnpj_fundos[cnpj_fundo] if cnpj_fundo in cnpj_fundos else None

                    if not fundo:
                        continue
                    for element in xml[0]:

                        if element.tag in ['titprivado', 'debenture', 'cotas']:
                            if element.tag == 'debenture':
                                codigo = element.find(
                                    'coddeb').text.replace(" ", "")
                            if element.tag == 'titprivado':
                                codigo = element.find(
                                    'codativo').text.replace(" ", "")
                            if element.tag == 'cotas':
                                isin = element.find(
                                    'isin').text.replace(" ", "")
                                if isin in codigo_fidcs:
                                    codigo = codigo_fidcs[isin]
                                else:
                                    continue
                            isin = element.find('isin').text
                            dados.append(
                                {'Código': codigo, 'Fundo': fundo, 'ISIN XML': isin})

                df = pd.DataFrame(dados)

                isin_banco = {i['codigo'].strip(): i['isin'].strip(
                ) if i['isin'] else None for i in database.query("select codigo, isin from icatu.info_papeis")}
                df['ISIN BD'] = df.apply(
                    lambda x: isin_banco[x['Código']] if x['Código'] in isin_banco else None, axis=1)
                df['Comparação'] = df.apply(
                    lambda x: 'OK' if x['ISIN XML'] == x['ISIN BD'] else 'Diferente', axis=1)

                df = df.sort_values(
                    ['Comparação', 'Código'], ascending=[True, True])
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_grid_options(enableRangeSelection=True)
                gb.configure_grid_options(enableCellTextSelection=True)
                gb = gb.build()
                gb['columnDefs'] = [{'field': "Código"}, {'field': "Fundo"}, {
                    'field': "ISIN XML"}, {'field': "ISIN BD"}, {'field': "Comparação"},]

                custom_css = {
                ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                ".ag-row":  {  "font-size": "16px !important;"}
                }

                new_df = AgGrid(
                    df,
                    gridOptions=gb,
                    update_mode='NO_UPDATE',
                    fit_columns_on_grid_load=False,
                    allow_unsafe_jscode=True,
                    enableRangeSelection=True,
                    custom_css=custom_css,
                    height=400,
                    enable_enterprise_modules=True)


def proximos_eventos(database, barra):
    st.title("Próximos eventos dos ativos de crédito")

    cwd = os.getcwd()
    df = pd.read_excel(os.path.join(cwd, 'assets', 'Relatórios', 'Próximos pagamentos.xlsx'))
    graf_dias, graf_ativo, df_download = df.copy(
        deep=False), df.copy(deep=False), df.copy(deep=False)
    df['Data'] = df['Data'].apply(lambda x: x.strftime("%d/%m/%Y"))
    df_download['Data'] = df_download['Data'].apply(lambda x: x.date())
    df['PU Estimado'] = df['PU Estimado'].apply(lambda x: "{:,.6f}".format(
        x).replace(",", "x").replace(".", ",").replace("x", "."))
    df['Quantidade'] = df['Quantidade'].apply(lambda x: "{:,.2f}".format(
        x).replace(",", "x").replace(".", ",").replace("x", "."))
    df['Financeiro Estimado Icatu'] = df['Financeiro Estimado Icatu'].apply(
        lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))

    graf_dias['Financeiro Estimado Icatu'] = graf_dias['Financeiro Estimado Icatu'].apply(
        lambda x: x/1000)
    graf_dias = graf_dias.groupby(
        ['Data'])[['Financeiro Estimado Icatu']].sum().reset_index()
    fig_dias = px.bar(graf_dias, x='Data', y='Financeiro Estimado Icatu',
                      text_auto=True, title="Por dia (em R$ Milhares)")
    fig_dias.update_yaxes(tickformat=",.0f", title='')
    fig_dias.update_layout(separators=',.', font=dict(size=15))
    fig_dias.update_xaxes(dtick="D1",  tickformat="%d/%m")

    graf_ativo['Financeiro Estimado Icatu'] = graf_ativo['Financeiro Estimado Icatu'].apply(
        lambda x: x/1000)
    graf_ativo = graf_ativo.groupby(['Código do Ativo'])[
        ['Financeiro Estimado Icatu']].sum().reset_index()
    graf_ativo = graf_ativo.sort_values(
        ['Financeiro Estimado Icatu'], ascending=False)
    graf_ativo = graf_ativo.head(5)
    fig_ativo = px.bar(graf_ativo, x='Código do Ativo', y='Financeiro Estimado Icatu',
                       text_auto=True, title="Por ativo (5 maiores em R$ Milhares)")
    fig_ativo.update_yaxes(tickformat=",.0f", title='')
    fig_ativo.update_layout(separators=',.', font=dict(size=15))

    cwd = os.getcwd()
    eventos_360 = pd.read_excel(os.path.join(cwd, 'assets', 'Relatórios', 'eventos360dias.xlsx'), sheet_name='Eventos')
    eventos_360['Data'] = eventos_360['Data'].apply(lambda x: x.date())
    eventos_360['Código do Ativo'] = eventos_360['Código do Ativo'].apply(lambda x: x.strip())
    eventos_download = eventos_360.copy(deep=False)
    eventos_360['Data'] = eventos_360['Data'].apply(lambda x: x.strftime('%d/%m/%Y'))
    eventos_360['Quantidade'] = eventos_360['Quantidade'].apply(
        lambda x: "{:,.0f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
    eventos_360['PU Estimado'] = eventos_360['PU Estimado'].apply(
        lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
    eventos_download['financeiro'] = eventos_download['Financeiro Estimado Icatu']
    eventos_download['mes'] = eventos_download.apply(lambda x: x['Data'].strftime('%Y/%m'), axis=1)
    eventos_360['Financeiro Estimado Icatu'] = eventos_360['Financeiro Estimado Icatu'].apply(
        lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
    tab1, tab2 = st.tabs(["Próximos 7 dias", "Próximos 360 dias"])

    with tab1:
        col1, col2 = st.columns([1, 1])
        col1.empty()
        col2.empty()
        col1.plotly_chart(fig_dias, use_container_width=True,
                          )
        col2.plotly_chart(fig_ativo, use_container_width=True,
                          )

        hide_table_row_index = """
        <style>
        thead tr th:first-child {display:none}
        tbody th {display:none}
        </style>
        """
        st.markdown(hide_table_row_index, unsafe_allow_html=True)
        with st.expander('Eventos discriminados por fundos', expanded=True):
            util.download_excel_button([df_download], ['Eventos'], 'Download em Excel', 'eventos_7dias')
            st.table(df)

    with tab2:
        try:
            col1, col2,  col3, col4 = st.columns([1, 1, 1, 1])
            fundos = col1.multiselect('Fundo', sorted([str(i) for i in eventos_360['Nome do Fundo'].unique()]))
            tipos = col2.multiselect('Tipo do Ativo', [str(i) for i in eventos_360['Tipo do Ativo'].unique()])
            emissores = col3.multiselect('Emissor', sorted([str(i) for i in eventos_360['Emissor'].unique()]))
            if not emissores:
                lista_emissores = sorted(
                    [str(i) for i in eventos_360['Código do Ativo'].unique()])
            else:
                lista_emissores = sorted([str(i) for i in eventos_360[eventos_360['Emissor'].isin(emissores)]['Código do Ativo'].unique()])
            ativos = col4.multiselect('Código do Ativo', lista_emissores)
            with st.spinner('Aguarde...'):
                if fundos:
                    eventos_download = eventos_download[eventos_download['Nome do Fundo'].isin(fundos)]
                if tipos:
                    eventos_download = eventos_download[eventos_download['Tipo do Ativo'].isin(tipos)]
                if ativos:
                    eventos_download = eventos_download[eventos_download['Código do Ativo'].isin(ativos)]
                if emissores:
                    eventos_download = eventos_download[eventos_download['Emissor'].isin(emissores)]
                if len(eventos_download.index) > 0:
                    eventos_consolidado, consolidado_download = eventos_download.copy(deep=False), eventos_download.copy(deep=False)
                    eventos_consolidado = eventos_consolidado.groupby(
                        ['Janela'])[['Financeiro Estimado Icatu']].sum().reset_index()
                    ordenacao = ['0 a 30 dias', '31 a 60 dias',
                                    '61 a 90 dias', '91 a 180 dias', '181 a 360 dias']
                    eventos_consolidado['ordem'] = pd.Categorical(
                        eventos_consolidado['Janela'],
                        categories=ordenacao,
                        ordered=True
                    )
                    eventos_consolidado = eventos_consolidado.sort_values(['ordem'], ascending=[True]).reset_index()
                    eventos_consolidado = eventos_consolidado.drop(columns=['ordem', 'index'])

                    for ind, row in eventos_consolidado.iterrows():
                        if ind == 0:
                            eventos_consolidado.at[ind, 'Acumulado'] = eventos_consolidado.loc[0,'Financeiro Estimado Icatu']
                        else:
                            eventos_consolidado.at[ind, 'Acumulado'] = eventos_consolidado.loc[ind,'Financeiro Estimado Icatu'] + eventos_consolidado.loc[ind-1, 'Acumulado']

                    consolidado_download, agg_emissor = eventos_consolidado.copy(deep=False), eventos_download.copy(deep=False)

                    df_dias = eventos_download.copy(deep=False)
                    util.download_excel_button([eventos_download, consolidado_download], [
                                                'Eventos', 'Consolidado'], 'Download Eventos 360 dias', 'eventos_360dias')
                    arquivo_eventos = os.path.join(cwd, 'assets', 'Relatórios', 'eventos_completo.xlsx')
                    with open(arquivo_eventos, "rb") as file:
                        btn = st.download_button(
                            label="Download Eventos Completo",
                            data=file,
                            file_name="eventos_completo.xlsx"
                        )

                    df_dias['Mês'] = df_dias['Data'].apply(lambda x: x.strftime('%b/%y'))
                    df_dias['Mês Número'] = df_dias['Data'].apply(lambda x: x.strftime('%Y%m'))
                    df_dias = df_dias.groupby(['Mês', 'Mês Número'])[['Financeiro Estimado Icatu']].sum().reset_index()
                    df_dias = df_dias.sort_values(['Mês Número'])

                    fig = px.bar(df_dias, x="Mês", y="Financeiro Estimado Icatu",
                                    title='Financeiro Estimado (Em R$ Milhões)', text_auto='.2s')
                    fig.update_xaxes(dtick="M1")
                    fig.update_yaxes(title='')
                    fig.update_layout(separators=',.', font=dict(size=15))
                    col1, _, col2 = st.columns([2.4, 0.1, 1.5])
                    col1.plotly_chart(
                        fig, use_container_width=True, )
                    col2.text("")
                    col2.text("")
                    col2.text("")
                    col2.text("")
                    col2.text("")
                    col2.text("")
                    df_tabela = eventos_consolidado.copy(deep=False)
                    df_tabela['Financeiro Estimado'] = df_tabela.apply(
                        lambda x: "{:,.2f}".format(x['Financeiro Estimado Icatu']).replace(",", "x").replace(".", ",").replace("x", "."), axis=1)
                    df_tabela['Acumulado'] = df_tabela['Acumulado'].apply(lambda x: "{:,.2f}".format(
                        x).replace(",", "x").replace(".", ",").replace("x", "."))
                    df_tabela = df_tabela[['Janela', 'Financeiro Estimado', 'Acumulado']]
                    with col2:
                        gb = GridOptionsBuilder.from_dataframe(df_tabela)
                        gb.configure_grid_options(enableRangeSelection=True)
                        gb.configure_grid_options(enableCellTextSelection=True)
                        gb = gb.build()

                        custom_css = {
                        ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                        ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                        ".ag-row":  {  "font-size": "16px !important;"}
                        }

                        st.subheader('Agregação por Janela')
                        new_df = AgGrid(
                            df_tabela,
                            gridOptions=gb,
                            update_mode='NO_UPDATE',
                            fit_columns_on_grid_load=False,
                            allow_unsafe_jscode=True,
                            enableRangeSelection=True,
                            custom_css=custom_css,
                            height=200,
                            enable_enterprise_modules=True)


                    df_pizza = eventos_download.copy(deep=False)
                    df_pizza['Financeiro Estimado Icatu'] = df_pizza['Financeiro Estimado Icatu'].apply(lambda x: x/1000000)
                    df_pizza = df_pizza.groupby(['Tipo do evento'])[
                        ['Financeiro Estimado Icatu']].sum().reset_index()
                    fig_pizza = px.pie(
                        df_pizza,
                        values='Financeiro Estimado Icatu',
                        names='Tipo do evento',
                        hole=.3, title='Tipo de Evento (Em R$ Milhões)', color='Tipo do evento',
                        color_discrete_map={
                            'Amortização': 'darkblue',
                            'Juros': 'Teal',
                            'Vencimento': 'royalblue'})

                    fig_pizza.update_traces(
                        text=[i.replace(".", ",") for i in df_pizza['Financeiro Estimado Icatu'].map(
                            "{:.0f}M".format)],
                        textinfo='percent+label+text',
                        insidetextorientation='horizontal')
                    fig_pizza.update_layout(
                        separators=',.', font=dict(size=15), showlegend=False)

                    eventos_consolidado['Financeiro Estimado Icatu'] = eventos_consolidado['Financeiro Estimado Icatu'].apply(
                        lambda x: x/1000000)
                    fig_waterfall = go.Figure(go.Waterfall(
                        measure=['relative' for _ in range(
                            len(eventos_consolidado['Janela'].tolist()))] + ["total"],
                        x=eventos_consolidado['Janela'].tolist() + ['Total'],
                        text=["{:.0f}M".format(i).replace(".", ",") for i in eventos_consolidado['Financeiro Estimado Icatu'].tolist(
                        )] + ["{:.0f}M".format(eventos_consolidado['Financeiro Estimado Icatu'].sum()).replace(".", ",")],
                        y=eventos_consolidado['Financeiro Estimado Icatu'].tolist(
                        ) + [eventos_consolidado['Financeiro Estimado Icatu'].sum()],
                        connector={"line": {"color": "rgb(63, 63, 63)"}},
                        increasing={"marker": {"color": "Teal"}},
                        totals={"marker": {"color": "rgb(99, 110, 250)"}}
                    ))

                    fig_waterfall.update_layout(
                        title="Distribuição por Período (Em R$ Milhões)", separators=',.', font=dict(size=15))
                    col1, col2 = st.columns([1, 1])
                    col1.plotly_chart(
                        fig_waterfall, use_container_width=True, )
                    col2.plotly_chart(
                        fig_pizza, use_container_width=True, )
                    
                    df_emissor = pd.pivot_table(agg_emissor, 
                                            values='financeiro', 
                                            index='Emissor', 
                                            columns='Janela', 
                                            aggfunc='sum',
                                            fill_value=0).reset_index()
                    colunas = ['Emissor', 
                                '0 a 30 dias', 
                                '31 a 60 dias',
                                '61 a 90 dias',
                                '91 a 180 dias',
                                '181 a 360 dias'
                                ]
                    df_emissor = df_emissor[[i for i in colunas if i in df_emissor.columns]]
                    df_emissor['Total'] = df_emissor.sum(axis=1)
                    df_emissor = df_emissor.sort_values(['Total'], ascending=[False])
                    gb = GridOptionsBuilder.from_dataframe(df_emissor)
                    gb.configure_grid_options(enableRangeSelection=True)
                    gb.configure_grid_options(enableCellTextSelection=True)
                    gb = gb.build()
                    gb['columnDefs'] = [
                        {'field': 'Emissor', }, 
                        {'field':  '0 a 30 dias',
                        'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                        'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                            {'field':  '31 a 60 dias',
                        'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                        'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                        {'field':  '61 a 90 dias',
                        'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                        'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                        {'field':  '91 a 180 dias',
                        'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                        'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                        {'field':  '181 a 360 dias',
                        'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                        'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                        {'field':  'Total',
                        'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                        'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},

                    ]

                    custom_css = {
                        ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                        ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                        ".ag-row":  {  "font-size": "16px !important;"}
                        }

                    
                    st.subheader('Agregação por Emissor por Janela')
                    new_df = AgGrid(
                        df_emissor,
                        gridOptions=gb,
                        update_mode='NO_UPDATE',
                        fit_columns_on_grid_load=False,
                        allow_unsafe_jscode=True,
                        enableRangeSelection=True,
                        custom_css=custom_css,
                        height=400,
                        enable_enterprise_modules=True)
                    

                    df_emissor_mes = pd.pivot_table(agg_emissor, 
                                            values='financeiro', 
                                            index='Emissor', 
                                            columns='mes', 
                                            aggfunc='sum',
                                            fill_value=0).reset_index()

                    df_emissor_mes = df_emissor_mes[sorted(df_emissor_mes.columns)]
                    df_emissor_mes['Total'] = df_emissor_mes.sum(axis=1)
                    df_emissor_mes = df_emissor_mes.sort_values(['Total'], ascending=[False])
                    gb = GridOptionsBuilder.from_dataframe(df_emissor_mes)
                    gb.configure_grid_options(enableRangeSelection=True)
                    gb.configure_grid_options(enableCellTextSelection=True)
                    gb = gb.build()
                    meses = [i for i in df_emissor_mes.columns if i not in ('Emissor', 'Total')]
                    gb['columnDefs'] = [{'field': 'Emissor','pinned': 'left' }]+ [
                                {'field':  i,
                                'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"}
                            for i in meses]+[
                                {'field':  'Total',
                                'pinned': 'right',
                                'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"}
                            ]
                    

                    custom_css = {
                    ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                    ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                    ".ag-row":  {  "font-size": "16px !important;"}
                    }

                    st.subheader('Agregação por Emissor Por Mês')
                    new_df = AgGrid(
                        df_emissor_mes,
                        gridOptions=gb,
                        update_mode='NO_UPDATE',
                        fit_columns_on_grid_load=False,
                        allow_unsafe_jscode=True,
                        enableRangeSelection=True,
                        custom_css=custom_css,
                        height=400,
                        enable_enterprise_modules=True)

                else:
                    st.caption('Redefina os filtros')
        except:
            st.caption('Houve um erro')

@try_error
def cota_fundos(database, barra):
    st.title(f"Cota diária dos fundos")
    col1, col2, col3, _ = st.columns([1.5, 2, 6, 2])
    data = col1.date_input('Data', mutil.somar_dia_util(date.today(), -1))
    selecao = col2.selectbox(
        'Seleção de fundos', 
        ('Fundos de Crédito', 
        'Todos os fundos', 
        'Seleção individual')
        )
    selecao_fundos = ''

    if selecao == 'Fundos de Crédito':
        fundos_credito = f"""(
            'CREDIT',
            'Caixa Ativo 2',
            'CP INSTITUCIONAL',
            'Iporã CP PG',
            'CREDIT PLUS',
            'MIRANTE CP',
            'ÁGUIA',
            'SYNGENTA BASEL',
            'MOLICO CP',
            'AILOS',
            'GERDAU CP 3',
            'RONDÔNIA',
            'VITRA CREDIT PLUS',
            'FUNSSEST',
            'ABSOLUTO FIFE',
            'ABSOLUTO II FIE',
            'ABSOLUTO II FIFE',
            'ABSOLUTO PLUS FIE',
            'ABSOLUTO PLUS FIFE',
            'ITAU PREV',
            'Itau Prev II', 
            'Itau II FIFE',
            'ITAU PREV QUALIFICADO FIFE',
            'BTG ABSOLUTO II',
            'BRADESCO ABSOLUTO II', 
            'WM PREV',
            'RIO GRANDE ABSOLUTO',
            'DINÂMICO PREV', 
            'IV TOTAL RETURN',
            'TR Institucional',
            'TR PG',
            'IV INFRAESTRUTURA',
            'VANG11 I',
            'CEARÁ',
            'EMBRAER VI FIM CP',
            'COPEL',
            'ENERPREV',
            'ENERGISA PREV',
            'LARANJEIRAS',
            'ICATU SEG INFRA',
            'TFO INFRAESTRUTURA',
            'ABSOLUTO TR FIE',
            'ABSOLUTO TR FIFE',
            'ITAU PREV TR', 
            'CP LIQUIDEZ', 
            'Veículo Especial IE', 
            'DINÂMICO CDI',
            'DINÂMICO INSTITUCIONAL',
            'DINÂMICO IPCA', 
            'Vitra Infraestrutura',
            'Veículo Especial DC',
            'INFRA PVT',
            'ICATU CAP INFRA',
            'BRASILPREV ABSOLUTO PLUS',
            'INFRA PVT DI',
            'TFO Infraestrutura CDI',
            'Quanta QP4',
            'Credit Plus II',
            'IRB CDI', 
            'Veneto Credit Plus',
            'ABSOLUTO INFLAÇÃO LC',
            'BANCÁRIO LC',
            'XP ABSOLUTO PLUS',
            'ABSOLUTO II LC',
            'XP ABSOLUTO II'
            )"""
        selecao_fundos = "AND f.nome in " + fundos_credito

    if selecao == 'Seleção individual':
        fundos = 'SELECT distinct nome FROM icatu.fundos  where tipo is not null order by nome'
        selecao_individual = col3.multiselect(
            'Nome do Fundo', 
            [i[0].strip() for i in database.query_select(fundos)]
            )
        if selecao_individual:
            selecao_individual = [str("'" + i + "'") for i in selecao_individual]
            selecao_fundos = f"AND f.nome in ({', '.join(selecao_individual)})"

    if data == date.today():
        data = mutil.somar_dia_util(data, -1)
    data = mutil.get_dia_util(data)
    data_anterior = mutil.somar_dia_util(data, -1)

    sql = f"""SELECT data, f.cnpj, c.nome as classificacao, f.nome, indice, cota
            FROM icatu.posicao_fundos p
            LEFT JOIN icatu.fundos f on f.isin = p.fundo
            LEFT JOIN icatu.classificacao_fundos c on c.id = f.id_classificacao
            WHERE data BETWEEN '{data_anterior}' AND '{data}' {selecao_fundos}"""

    dados = database.query_select(sql)
    df = pd.DataFrame(
        dados, 
        columns=['Data',
                    'CNPJ', 
                    'Classificação', 
                    'Nome', 
                    'Benchmark', 
                    'Cota']
                    )
    lista_fundos = [i for i in df['CNPJ'].unique()]

    ret_cdi = (database.cdi_dia(data)['indice']-1)*100
    sql = f"""SELECT ret_diario
        FROM icatu.indices_anbima 
        WHERE data = '{data}' and indice = 'IMA-B 5'"""
    ret_imab = round(database.query_select(sql)[0][0], 2)

    dados = []
    for cnpj in lista_fundos:
        try:
            rentabilidade = ((df.loc[(df['CNPJ'] == cnpj) & (df['Data'] == data), 'Cota'].iloc(0)[0] /
                                df.loc[(df['CNPJ'] == cnpj) & (df['Data'] == data_anterior), 'Cota'].iloc(0)[0])-1)*100
            dado = {
                'Tipo': 'Fundo',
                'Classificação': df.loc[df['CNPJ'] == cnpj, 'Classificação'].iloc(0)[0],
                'Nome': df.loc[df['CNPJ'] == cnpj, 'Nome'].iloc(0)[0],
                'Benchmark': df.loc[df['CNPJ'] == cnpj, 'Benchmark'].iloc(0)[0],
                'Rentabilidade': rentabilidade}
            dados.append(dado)
        except:
            pass

    fundos = pd.DataFrame(dados)
    pesquisa = len(fundos[fundos['Benchmark'] == 'TOTAL RETURN'].index)
    ret_tr = 0
    if pesquisa > 0:
        ret_tr = fundos[fundos['Benchmark'] == 'TOTAL RETURN'].groupby('Benchmark')['Rentabilidade'].mean()[0]

    for ind, row in fundos.iterrows():
        if row['Benchmark'] == 'CDI':
            fundos.at[ind, 'Prêmio s/ Benchmark'] = "{:,.4f}".format((row['Rentabilidade'] / ret_cdi)*100).replace(",", "x").replace(".", ",").replace("x", ".")
            fundos.at[ind, 'Valores'] = (row['Rentabilidade'] / ret_cdi)*100

        else:
            premio = ((1+row['Rentabilidade']/100) /(1+ret_tr/100)-1)*10000
            fundos.at[ind, 'Valores'] = ((1+row['Rentabilidade']/100) / (1+ret_tr/100)-1)*10000
            if premio >= 0:
                fundos.at[ind, 'Prêmio s/ Benchmark'] = "{:,.0f}".format(premio).replace(",", "x").replace(".", ",").replace("x", ".") + 'BPS'
            else:
                fundos.at[ind, 'Prêmio s/ Benchmark'] = "{:,.0f}".format(premio).replace(",", "x").replace(".", ",").replace("x", ".") + 'BPS'

    fundos = pd.concat([fundos, pd.DataFrame([
        {
            'Tipo': 'Benchmark', 
            'Classificação': "-", 
            'Nome': 'CDI',
            'Benchmark': "-", 
            'Rentabilidade': ret_cdi, 
            'Prêmio s/ Benchmark': '-'
            },
        {
            'Tipo': 'Benchmark', 
            'Classificação': "-", 
            'Nome': 'Média dos Total Return',
            'Benchmark': "-", 
            'Rentabilidade': ret_tr, 
            'Prêmio s/ Benchmark': '-'
            },
        {
            'Tipo': 'Benchmark', 
            'Classificação': "-", 
            'Nome': 'IMA-B 5',
            'Benchmark': "-", 
            'Rentabilidade': ret_imab, 
            'Prêmio s/ Benchmark': '-'
            }
    ])], ignore_index=True)

    ordenacao = ['CDI', 
                'Média dos Total Return', 
                'IMA-B 5', 
                'CREDIT', 
                'Caixa Ativo 2', 
                'CP INSTITUCIONAL', 
                'Iporã CP PG', 
                'CREDIT PLUS', 
                'CP LIQUIDEZ', 
                'Veículo Especial IE', 
                'DINÂMICO INSTITUCIONAL',
                'DINÂMICO CDI', 
                'Veículo Especial DC',
                'BANCÁRIO LC',
                'MIRANTE CP',
                'ÁGUIA', 
                'SYNGENTA BASEL', 
                'MOLICO CP', 
                'AILOS', 
                'GERDAU CP 3', 
                'RONDÔNIA', 
                'LARANJEIRAS',
                'VITRA CREDIT PLUS',
                'FUNSSEST', 
                'Quanta QP4', 
                'Credit Plus II',
                'IRB CDI', 
                'Veneto Credit Plus',
                'ABSOLUTO FIFE', 
                'ABSOLUTO II FIE', 
                'ABSOLUTO II FIFE', 
                'ABSOLUTO PLUS FIE', 
                'ABSOLUTO PLUS FIFE', 
                'ITAU PREV', 
                'Itau II FIFE', 
                'Itau Prev II', 
                'ITAU PREV QUALIFICADO FIFE', 
                'BTG ABSOLUTO II', 
                'BRADESCO ABSOLUTO II', 
                'WM PREV', 
                'RIO GRANDE ABSOLUTO', 
                'DINÂMICO PREV', 
                'BRASILPREV ABSOLUTO PLUS', 
                'ABSOLUTO INFLAÇÃO LC',
                'ABSOLUTO II LC',
                'XP ABSOLUTO PLUS',
                'IV TOTAL RETURN', 
                'TR Institucional',
                'TR PG', 
                'IV INFRAESTRUTURA', 
                'VANG11 I', 
                'CEARÁ', 
                'EMBRAER VI FIM CP', 
                'COPEL', 
                'ENERPREV', 
                'ENERGISA PREV', 
                'DINÂMICO IPCA', 
                'ICATU SEG INFRA', 
                'TFO INFRAESTRUTURA', 
                'Vitra Infraestrutura', 
                'INFRA PVT',
                'ICATU CAP INFRA', 
                'INFRA PVT DI', 
                'TFO Infraestrutura CDI',
                'ABSOLUTO TR FIE',
                'ABSOLUTO TR FIFE', 
                'ITAU PREV TR'
                ]
    fundos['ordem'] = pd.Categorical(
        fundos['Nome'],
        categories=ordenacao,
        ordered=True
    )
    fundos = fundos.sort_values(['Tipo', 'Benchmark', 'ordem'], ascending=[True, True, True])
    grafico_cdi, grafico_tr, tabela = fundos.copy( deep=False), fundos.copy(deep=False), fundos.copy(deep=False)
    tabela = fundos.drop(columns=['Valores', 'ordem'])

    fundos['Prêmio s/ Benchmark'] = fundos['Valores']
    fundos = fundos.drop(columns=['Valores'])
    fundos['Rentabilidade'] = fundos['Rentabilidade'].apply(lambda x: round(x, 4))
    tabela['Rentabilidade'] = tabela['Rentabilidade'].apply(lambda x: "{:,.4f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
    fundos['Prêmio s/ Benchmark'] = fundos['Prêmio s/ Benchmark'].apply(lambda x: round(x, 4))

    grafico_cdi['Rentabilidade'] = grafico_cdi['Rentabilidade'].apply(lambda x: round(x, 4))
    grafico_cdi = grafico_cdi[(grafico_cdi['Tipo'] == 'Fundo') & (grafico_cdi['Benchmark'] == 'CDI')]
    fig1 = px.scatter(
        grafico_cdi,
        labels={"Valores": "Percentual do CDI"},
        title='Benchmark CDI', 
        y="Nome", 
        x="Valores",
        color="Classificação", 
        symbol="Classificação",
        hover_name="Nome",
        hover_data={
            'Nome': False,
            'Classificação': False,
            'Rentabilidade': True,
            'Valores': False,
            "Prêmio s/ Benchmark": True})
    fig1.add_vline(x=100, line_width=3, line_dash="dash")
    fig1.update_layout(
        font=dict(size=15),
        height=900,
        legend=dict(orientation="h", y=-0.15),
        hoverlabel=dict(
            bgcolor="white",
            font_size=16))
    fig1.update_traces(marker_size=10)
    fig1.update_yaxes(title='')

    grafico_tr['Rentabilidade'] = grafico_tr['Rentabilidade'].apply(lambda x: round(x, 4))
    grafico_tr = grafico_tr[(grafico_tr['Tipo'] == 'Fundo') & (grafico_tr['Benchmark'] == 'TOTAL RETURN')]
    fig2 = px.scatter(
        grafico_tr, 
        title='Benchmark Total Return',
        labels={"Valores": "Prêmio sob a média dos Total Return (BPs)"},
        y="Nome",
        x="Valores",
        color="Classificação", 
        symbol="Classificação",
        hover_name="Nome",
        hover_data={
            'Nome': False,
            'Classificação': False,
            'Rentabilidade': True,
            'Valores': False,
            "Prêmio s/ Benchmark": True})
    fig2.add_vline(x=0, line_width=3, line_dash="dash")
    fig2.update_layout(
        font=dict(size=15),
        height=900,
        legend=dict(orientation="h", y=-0.15),
        hoverlabel=dict(
            bgcolor="white",
            font_size=16))
    fig2.update_traces(marker_size=10)
    fig2.update_yaxes(title='')

    col1, col2 = st.columns([1, 1])
    col1.plotly_chart(fig1, use_container_width=True, )
    col2.plotly_chart(fig2, use_container_width=True, )

    hide_table_row_index = """
    <style>
    thead tr th:first-child {display:none}
    tbody th {display:none}
    </style>
    """
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    with st.expander('Tabela de valores', expanded=True):
        fundos = fundos.drop(columns=['ordem'])
        util.download_excel_button([fundos], 
                                    [f'Cota_fundos_{data.strftime("%Y-%m-%d")}'], 
                                    'Download em Excel', 
                                    f'Cota_fundos_{data.strftime("%Y-%m-%d")}'
                                    )
        st.table(tabela)


@try_error
def taxa_fundos(database, barra):
    with barra:
        opcao = st.selectbox('Selecione a terra', [
                             'Carrego total', 'Carrego por Faixa de Rating'])
    if opcao == 'Carrego por Faixa de Rating':
        st.title('Calcular Carrego dos Fundos por Faixa de Rating')
        col1, col2, col3, col4 = st.columns([1, 1, 3, 3])
        data_inicial = col1.date_input(
            'Data Inicial', datetime(2023, 1, 1).date())
        data_final = col2.date_input(
            'Data Final', mutil.somar_dia_util(date.today(), -1))
        busca_ratings = col3.multiselect('Rating', [i[0] for i in query_db(
            database, "select rating from icatu.ordenacao_ratings where agencia = 'FITCH' order by ordenacao")])
        fundo = col4.selectbox('Fundo', [i[0] for i in query_db(
            database, 'select nome from icatu.fundos  where tipo is not null  order by nome')])
        agrupar = st.checkbox('Agrupar ratings')
        calc = st.button('Gerar informações')

        if fundo:
            fundo = f"and nome = '{fundo}'"
        else:
            fundo = ''
        if busca_ratings:
            rating = f""" and rating in ({", ".join([f"'{i}'" for i in busca_ratings]) if len(busca_ratings) > 1  else f"'{busca_ratings[0]}'"})"""
        else:
            rating = ''

        data_inicial = data_inicial.strftime('%Y-%m-%d')
        data_final = data_final.strftime('%Y-%m-%d')

        if calc and fundo:
            with st.spinner('Aguarde...'):
                ratings = database.query(
                    "select * from icatu.view_ratings_ativos where agencia  <> 'ICATU' and rating <> 'Retirado' order by codigo, data")

                historico_ratings = {}
                for linha in ratings:
                    ativo = linha['codigo']
                    if not ativo in historico_ratings:
                        historico_ratings[ativo] = []
                    historico_ratings[ativo].append({
                        'data': linha['data'],
                        'agencia': linha['agencia'],
                        'rating': linha['rating'],
                        'ordenacao': linha['ordenacao']})

                sql = f"""
                select 
                    data, 
                    ativo, 
                    nome, 
                    spread, 
                    duration,
                    perc_credito  
                from icatu.view_taxas_ativos_fundos 
                where data between '{data_inicial}' and '{data_final}' {fundo}
                """
                ativos = database.query(sql)
                ativos = pd.DataFrame(ativos)

                def rating(x):
                    ativo = x['ativo']
                    data = x['data']
                    if ativo in historico_ratings:
                        rating_moodys = [[i['rating'], i['ordenacao'], i['data']] for i in historico_ratings[ativo]
                                         if data > i['data'] and i['data'] > (data - timedelta(days=365)) and i['agencia'] == 'MOODYS']
                        rating_moodys.sort(key=lambda x: x[2], reverse=True)
                        if rating_moodys:
                            rating_moodys = rating_moodys[0]
                        ratings_sp = [[i['rating'], i['ordenacao'], i['data']] for i in historico_ratings[ativo]
                                      if data > i['data'] and i['data'] > (data - timedelta(days=365)) and i['agencia'] == 'S&P']
                        ratings_sp.sort(key=lambda x: x[2], reverse=True)
                        if ratings_sp:
                            ratings_sp = ratings_sp[0]
                        ratings_fitch = [[i['rating'], i['ordenacao'], i['data']] for i in historico_ratings[ativo]
                                         if data > i['data'] and i['data'] > (data - timedelta(days=365)) and i['agencia'] == 'FITCH']
                        ratings_fitch.sort(key=lambda x: x[2], reverse=True)
                        if ratings_fitch:
                            ratings_fitch = ratings_fitch[0]
                        ratings = [rating_moodys, ratings_sp, ratings_fitch]
                        ratings = [i for i in ratings if i]
                        if ratings:
                            ratings.sort(key=lambda x: x[1], reverse=True)
                            rating = ratings[0][0]
                            if agrupar:
                                if ratings[0][1] > 10:
                                    rating = 'Sem grau de investimento'
                                else:
                                    rating = rating.replace(
                                        '-', '').replace('+', '')
                        else:
                            rating = 'Sem Rating'
                    else:
                        rating = 'Sem Rating'
                    return rating

                ativos['rating'] = ativos.apply(lambda x: rating(x), axis=1)
                if busca_ratings:
                    ativos = ativos[ativos['rating'].isin(busca_ratings)]
                df = pd.DataFrame(ativos)
                df = df.groupby(['data', 'rating'])[
                    'spread', 'duration'].mean().reset_index()
                df = df.rename(columns={
                    'data': 'Data',
                    'rating': 'Rating',
                    'spread': 'Spread',
                    'duration': 'Duration'})
                df = df.sort_values(['Data'], ascending=[True])
                df = df.round(2)
                df = df[df['Spread'] != 0]
                df = df[pd.to_numeric(df['Spread'], errors='coerce').notnull()]

                df_ponderado = ativos.copy(deep=True)
                df_ponderado['spread ponderado'] = df_ponderado.apply(
                    lambda x: x['spread'] * x['perc_credito'], axis=1)
                df_ponderado['duration ponderado'] = df_ponderado.apply(
                    lambda x: x['duration'] * x['perc_credito'], axis=1)
                df_ponderado = df_ponderado.groupby(['data', 'rating'])[
                    'spread ponderado', 'duration ponderado', 'perc_credito'].sum().reset_index()
                df_ponderado['Spread'] = df_ponderado.apply(
                    lambda x: x['spread ponderado'] / x['perc_credito'], axis=1)
                df_ponderado['Duration'] = df_ponderado.apply(
                    lambda x: x['duration ponderado'] / x['perc_credito'], axis=1)
                df_ponderado = df_ponderado.rename(
                    columns={'data': 'Data', 'rating': 'Rating'})
                df_ponderado = df_ponderado[df_ponderado['Spread'] != 0]

                df_download = df.copy(deep=True)
                df_download = df_download[[
                    'Data', 'Spread', 'Duration', 'Rating']]
                df_download_ponderado = df_ponderado.copy(deep=True)
                df_download = df_download[[
                    'Data',  'Rating', 'Spread', 'Duration']]
                df_download_ponderado = df_download_ponderado[[
                    'Data',  'Rating', 'Spread', 'Duration']]
                df_download_ponderado = df_download_ponderado.round(2)
                df_download = df_download.sort_values(
                    ['Data', 'Rating'], ascending=[True, True])
                df_download_ponderado = df_download_ponderado.sort_values(
                    ['Data', 'Rating'], ascending=[True, True])
                util.download_excel_button([df_download, df_download_ponderado], [
                                           'Média Ativos', 'Média Carteira'], 'Download em Excel', 'Taxas_fundos')

                fig = px.line(df, x="Data", y="Spread", color='Rating',
                              title=f'Carrego por Faixa de Rating (Média dos Ativos)',
                              markers=True, symbol="Rating")
                fig.update_layout(font=dict(size=15),
                                  legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.6,
                    xanchor="auto"),
                    hovermode="x unified",
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=16))
                fig.update_xaxes(dtick="M1", title='', tickformat="%m/%Y")
                fig.update_traces(
                    hovertemplate="<br>Data: %{x|%d/%m/%Y}<br>" +
                    "Spread: %{y:.2f}<br>")

                st.plotly_chart(fig, use_container_width=True,
                                )

                fig2 = px.line(df_ponderado, x="Data", y="Spread", color='Rating',
                               title=f'Carrego por Faixa de Rating (Média Ponderada da Carteira)',
                               markers=True, symbol="Rating")
                fig2.update_layout(font=dict(size=15),
                                   legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.6,
                    xanchor="auto"),
                    hovermode="x unified",
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=16))

                fig2.update_xaxes(dtick="M1", title='', tickformat="%m/%Y")
                fig2.update_traces(
                    hovertemplate="<br>Data: %{x|%d/%m/%Y}<br>" +
                    "Spread: %{y:.2f}<br>")

                st.plotly_chart(fig2, use_container_width=True,
                                )

    if opcao == 'Carrego total':
        st.title('Calcular Carrego dos Fundos')
        col1, col2, col3 = st.columns([1, 1, 6])
        data_inicial = col1.date_input(
            'Data Inicial', mutil.somar_dia_util(date.today(), -1))
        data_final = col2.date_input(
            'Data Final', mutil.somar_dia_util(date.today(), -1))
        fundos = col3.multiselect('Fundo', [i[0] for i in query_db(
            database, 'select nome from icatu.fundos where tipo is not null order by nome')])
        calc = st.button('Gerar informações')

        if fundos:
            fundos = f"""({", ".join([f"'{i}'" for i in fundos]) if len(fundos) > 1  else f"'{fundos[0]}'"})"""

        data_inicial = data_inicial.strftime('%Y-%m-%d')
        data_final = data_final.strftime('%Y-%m-%d')

        if calc and fundos:
            with st.spinner('Aguarde...'):
                sql = f"""
                    select * from icatu.view_taxas_fundos
                    where data between '{data_inicial}' and '{data_final}'
                    and nome in {fundos}
                """
                df = pd.DataFrame(database.query(sql))
                df = df.rename(columns={
                    'data': 'Data',
                    'nome': 'Fundo',
                    'spread': 'Spread',
                    'duration': 'Duration',
                    'perc_alocado': 'PL Alocado',
                    'pl': 'PL Fundo',
                    'emissores': 'Emissores',
                    'avg_perc_pl': '% do PL Médio'})
                df['PL Alocado'] = df['PL Alocado'].apply(lambda x: x*100)
                df['% do PL Médio'] = df['% do PL Médio'].apply(
                    lambda x: x*100)
                df = df.sort_values(['Fundo', 'Data'], ascending=[True, True])

                sql = f"""
                    select 
                        distinct 
                        ec.data, 
                        f.nome as fundo, 
                        ativo, 
                        sum(ec.quantidade * preco) as financeiro,
                        juros,
                        data_vencimento,
                        pf.quantidade * pf.cota as pl_fundo
                    from icatu.estoque_compromissadas ec 
                    left join icatu.info_papeis ip on ip.codigo = concat('COMP_', ec.ativo)
                    left join icatu.posicao_fundos pf on pf.fundo = ec.fundo and pf.data = ec.data
                    left join icatu.fundos f on f.isin = ec.fundo
                    where ec.data between '{data_inicial}' and '{data_final}'
                    group by ec.data, f.nome, ativo, juros, data_vencimento, pf.quantidade, pf.cota
                """
                if database.query(sql):
                    df_comp = pd.DataFrame(database.query(sql))
                    df_comp['duration'] = df_comp.apply(lambda x: mutil.contar_du(
                        x['data'], x['data_vencimento'])/252, axis=1)
                    df_comp['duration_ponderada'] = df_comp.apply(
                        lambda x: x['duration'] * (x['financeiro'] / x['pl_fundo']), axis=1)
                    df_comp['juros_ponderado'] = df_comp.apply(
                        lambda x: x['juros'] * (x['financeiro'] / x['pl_fundo']), axis=1)
                    df_comp = df_comp.groupby(['data', 'fundo'])[
                        'financeiro', 'duration_ponderada', 'juros_ponderado'].sum().reset_index()
                    compromissada = {}

                    for ind, row in df_comp.iterrows():
                        fundo = row['fundo']
                        duration = row['duration_ponderada']
                        juros = row['juros_ponderado']
                        data = row['data']
                        if not fundo+data.strftime('%Y%m%d') in compromissada:
                            compromissada[fundo+data.strftime('%Y%m%d')] = {
                                'duration': duration, 'juros': juros}
                else:
                    compromissada = {}
                df['Spread Fundo'] = df.apply(lambda x: x['Spread'] * x['PL Alocado']/100 - compromissada[x['Fundo']+x['Data'].strftime(
                    '%Y%m%d')]['juros'] if x['Fundo']+x['Data'].strftime('%Y%m%d') in compromissada else x['Spread'] * x['PL Alocado']/100, axis=1)
                df['Duration Fundo'] = df.apply(lambda x: x['Duration'] * x['PL Alocado']/100 - compromissada[x['Fundo']+x['Data'].strftime(
                    '%Y%m%d')]['duration'] if x['Fundo']+x['Data'].strftime('%Y%m%d') in compromissada else x['Duration'] * x['PL Alocado']/100, axis=1)
                df = df.round(2)
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_grid_options(enableRangeSelection=True)
                gb.configure_grid_options(enableCellTextSelection=True)
                gb = gb.build()
                gb['columnDefs'] = [
                    {'field': 'Fundo'},
                    {'field': "Data", 'type': [
                        "dateColumnFilter", "customDateTimeFormat"], 'custom_format_string': 'dd/MM/yyyy'},
                    {'field': 'Spread', 'headerName': 'Spread Crédito',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                    {'field': 'Duration', 'headerName': 'Duration Crédito',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                    {'field': 'Spread Fundo',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                    {'field': 'Duration Fundo',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});"},
                    {'field': 'PL Alocado',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%';"},
                    {'field': 'PL Fundo',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 0, maximumFractionDigits: 0});"},
                    {'field': 'Emissores',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 0, maximumFractionDigits: 0});"},
                    {'field': '% do PL Médio',
                     'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                     'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})+'%';"}]

                custom_css = {
                ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                ".ag-row":  {  "font-size": "16px !important;"}
                }


                df_download = df.copy(deep=False)
                df_download['PL Alocado'] = df_download['PL Alocado'].apply(
                    lambda x: x/100)
                df_download['% do PL Médio'] = df_download['% do PL Médio'].apply(
                    lambda x: x/100)
                df_download = df_download.rename(
                    columns={'Spread': 'Spread Carteira', 'Duration': 'Duration Carteira'})
                df_download = df_download[['Fundo', 'Data', 'Spread Carteira', 'Duration Carteira',
                                           'Spread Fundo', 'Duration Fundo', 'PL Alocado', 'PL Fundo', 'Emissores', '% do PL Médio']]

                util.download_excel_button(
                    [df_download], ['Fundos'], 'Download em Excel', 'Taxas_fundos')
                new_df = AgGrid(
                    df,
                    gridOptions=gb,
                    update_mode='NO_UPDATE',
                    fit_columns_on_grid_load=False,
                    allow_unsafe_jscode=True,
                    enableRangeSelection=True,
                    custom_css=custom_css,
                    height=400,
                    enable_enterprise_modules=True)


def precos_ajustados(database, barra):
    menu = barra.selectbox('Selecione a tela', [
                           'Evolução de preços ajustados', 'Conferir preços ajustados'])
    if menu == 'Conferir preços ajustados':
        conferir_precos_ajustados(database, barra)
    if menu == 'Evolução de preços ajustados':
        evolucao_precos_ajustados(database, barra)


@try_error
def evolucao_precos_ajustados(database, barra):
    st.title('Evolução de Preços Ajustados')
    col1, col2, col3, _ = st.columns([1, 1, 3, 3])
    data_inicial = col1.date_input('Data Inicial', datetime(2023, 1, 1).date())
    data_final = col2.date_input(
        'Data Final', mutil.somar_dia_util(date.today(), -1))
    sql = """
        select distinct ativo 
        from icatu.estoque_ativos e
        left join icatu.info_papeis i on i.codigo = e.ativo
        where fonte <> 'BRITECH' and tipo_ativo not in ('FIDC', 'BOND')
        order by ativo
    """
    ativo = col3.multiselect('Papel', [i[0].strip()
                             for i in query_db(database, sql)])
    media_custodiante = st.checkbox('Discriminar preços por custodiante')
    data_inicial_busca = mutil.somar_dia_util(data_inicial, -1)
    if ativo:
        ativo = f"""({", ".join([f"'{i}'" for i in ativo]) if len(ativo) > 1  else f"'{ativo[0]}'"})"""
        with st.spinner('Aguarde...'):
            sql = f"""
            select * from (
            select distinct * from (
                select 
                    data, ativo, c.nome_curto as custodiante, e.fundo,
                    avg(preco) as preco, avg(preco_ajustado) as preco_ajustado 
                    from icatu.estoque_ativos e
                    left join icatu.fundos f on f.isin = e.fundo
                    left join icatu.custodiantes c on c.cnpj = f.custodiante 
                    where fonte <> 'BRITECH' 
                    and (fic <> true or fic is null)
                    and data between '{data_inicial_busca.strftime('%Y-%m-%d')}' and '{data_final.strftime('%Y-%m-%d')}'
                    and ativo in {ativo}
                    group by data, ativo, nome_curto, e.fundo
                    order by data) t
            union
                select distinct data, 
                'CDI' as ativo, 
                'Índice' as custodiante, '' as fundo,
                indice_acum as preco, 
                indice_acum as preco_ajustado
                from icatu.historico_cdi hc 
                where data between '{data_inicial_busca.strftime('%Y-%m-%d')}' and '{data_final.strftime('%Y-%m-%d')}'
                order by data) t
            union
                select 
                data,
                'IMA-B 5' as ativo,
                'Índice' as custodiante, '' as fundo,
                num_indice as preco,
                num_indice as preco_ajustado
                from icatu.indices_anbima ia 
                where indice = 'IMA-B 5'
                and data between '{data_inicial_busca.strftime('%Y-%m-%d')}' and '{data_final.strftime('%Y-%m-%d')}'
                order by data
            """

            df = pd.DataFrame([i for i in database.query_select(sql)], columns=[
                              'Data', 'Ativo', 'Custodiante', 'Fundo', 'Preço', 'Preço Ajustado'])
            df['Ativo'] = df['Ativo'].apply(lambda x: x.strip())
            precos_datas = {}
            for ind, row in df.iterrows():
                ativo = row['Ativo'].strip()
                data = row['Data']
                fundo = row['Fundo'].strip()
                if not ativo+fundo in precos_datas:
                    precos_datas[ativo+fundo] = {}
                precos_datas[ativo+fundo][data] = row['Preço Ajustado']

            retorno_fundos = {}
            for ind, row in df.iterrows():
                ativo = row['Ativo'].strip()
                data = row['Data']
                data_anterior = mutil.somar_dia_util(data, -1)
                custodiante = row['Custodiante']
                fundo = row['Fundo'].strip()
                if ativo+fundo in precos_datas and data_anterior in precos_datas[ativo+fundo]:
                    if not ativo+custodiante in retorno_fundos:
                        retorno_fundos[ativo+custodiante] = {}
                    if retorno_fundos[ativo+custodiante] and data.strftime('%Y%m%d') in retorno_fundos[ativo+custodiante]:
                        lista = retorno_fundos[ativo +
                                               custodiante][data.strftime('%Y%m%d')]
                    else:
                        lista = []
                    retorno_fundos[ativo+custodiante][data.strftime('%Y%m%d')] = [
                        row['Preço Ajustado'] / precos_datas[ativo+fundo][data_anterior]]+lista
            for i in retorno_fundos:
                for j in retorno_fundos[i]:
                    retorno_fundos[i][j] = mean(retorno_fundos[i][j])

            if not media_custodiante:
                symbol = 'Ativo'
                for ind, row in df.iterrows():
                    ativo = row['Ativo'].strip()
                    custodiante = row['Custodiante']
                    data = row['Data']
                    if data > data_inicial_busca:
                        if not data.strftime('%Y%m%d') in retorno_fundos[ativo+custodiante]:
                            df.at[ind, 'retorno_indice'] = 0
                        else:
                            df.at[ind, 'retorno_indice'] = retorno_fundos[ativo +
                                                                          custodiante][data.strftime('%Y%m%d')]
                    else:
                        df.at[ind, 'retorno_indice'] = 1

                retornos = {}
                for ind, row in df[df['retorno_indice'] != 0].groupby(['Ativo', 'Data'])['retorno_indice'].mean().reset_index().iterrows():
                    ativo = row['Ativo'].strip()
                    data = row['Data']
                    retornos[ativo +
                             data.strftime('%Y%m%d')] = row['retorno_indice']

                def ajustar_retorno(x):
                    if x['Ativo'].strip()+x['Data'].strftime('%Y%m%d') in retornos and x['retorno_indice'] == 0:
                        return retornos[x['Ativo'].strip()+x['Data'].strftime('%Y%m%d')]
                    else:
                        return x['retorno_indice']

                df['retorno_indice'] = df.apply(
                    lambda x:  ajustar_retorno(x), axis=1)
                df = df[df['retorno_indice'] != 0]
                df['Mês'] = df.apply(
                    lambda x: x['Data'].strftime('%Y/%m'), axis=1)
                lista_meses = sorted(
                    df[df['Data'] >= data_inicial]['Mês'].unique())
                dados = []
                for ativo in df['Ativo'].unique():
                    colunas = {}
                    for mes in lista_meses:
                        indices = df[(df['Mês'] == mes) & (df['Ativo'] == ativo)].groupby(['Data'])[
                            'retorno_indice'].mean().reset_index()['retorno_indice'].tolist()
                        prod = (np.prod(indices)-1)*100
                        colunas[mes] = "{:,.2f}%".format(
                            round(prod, 2)).replace('.', ',')

                    indices = df[df['Ativo'] == ativo].groupby(
                        ['Data'])['retorno_indice'].mean().reset_index()['retorno_indice'].tolist()
                    prod = (np.prod(indices)-1)*100
                    total = "{:,.2f}%".format(round(prod, 2)).replace('.', ',')
                    dados.append(
                        {**{**{'Ativo': ativo}, **colunas}, **{'Total': total}})
                df = df.groupby(['Ativo', 'Data'])[
                    'retorno_indice', 'Preço', 'Preço Ajustado'].mean().reset_index()
                for ind, row in df.iterrows():
                    ativo = row['Ativo'].strip()
                    data = row['Data']
                    indices = df[(df['Data'] <= data) & (df['Ativo'] == ativo)].groupby(['Data'])[
                        'retorno_indice'].mean().reset_index()['retorno_indice'].tolist()
                    prod = np.prod(indices)
                    df.at[ind, 'Retorno'] = prod
            else:
                symbol = 'Custodiante'
                for ind, row in df.iterrows():
                    ativo = row['Ativo'].strip()
                    custodiante = row['Custodiante']
                    data = row['Data']
                    if data > data_inicial_busca:
                        if ativo+custodiante in retorno_fundos and not data.strftime('%Y%m%d') in retorno_fundos[ativo+custodiante]:
                            df.at[ind, 'retorno_indice'] = 0
                        if ativo+custodiante in retorno_fundos and data.strftime('%Y%m%d') in retorno_fundos[ativo+custodiante]:
                            df.at[ind, 'retorno_indice'] = retorno_fundos[ativo +
                                                                          custodiante][data.strftime('%Y%m%d')]
                    else:
                        df.at[ind, 'retorno_indice'] = 1

                retornos = {}
                for ind, row in df[df['retorno_indice'] != 0].groupby(['Ativo', 'Data', 'Custodiante'])['retorno_indice'].mean().reset_index().iterrows():
                    ativo = row['Ativo'].strip()
                    data = row['Data']
                    custodiante = row['Custodiante']
                    retornos[ativo+data.strftime('%Y%m%d') +
                             custodiante] = row['retorno_indice']

                def ajustar_retorno(x):
                    if x['Ativo'].strip()+x['Data'].strftime('%Y%m%d')+x['Custodiante'] in retornos and x['retorno_indice'] == 0:
                        return retornos[x['Ativo'].strip()+x['Data'].strftime('%Y%m%d')+x['Custodiante']]
                    else:
                        return x['retorno_indice']

                df['retorno_indice'] = df.apply(
                    lambda x:  ajustar_retorno(x), axis=1)
                df = df[df['retorno_indice'] != 0]
                df['Mês'] = df.apply(
                    lambda x: x['Data'].strftime('%Y/%m'), axis=1)
                lista_meses = sorted(
                    df[df['Data'] >= data_inicial]['Mês'].unique())
                dados = []
                for ativo in df['Ativo'].unique():
                    for custodiante in df['Custodiante'].unique():
                        colunas = {}
                        for mes in lista_meses:
                            indices = df[(df['Mês'] == mes) & (df['Ativo'] == ativo) & (df['Custodiante'] == custodiante)].groupby(
                                ['Data'])['retorno_indice'].mean().reset_index()['retorno_indice'].tolist()
                            prod = (np.prod(indices)-1)*100
                            if round(prod, 2) == 0:
                                colunas[mes] = '-'
                            else:
                                colunas[mes] = "{:,.2f}%".format(
                                    round(prod, 2)).replace('.', ',')

                        indices = df[(df['Ativo'] == ativo) & (df['Custodiante'] == custodiante)].groupby(
                            ['Data'])['retorno_indice'].mean().reset_index()['retorno_indice'].tolist()
                        prod = (np.prod(indices)-1)*100
                        total = "{:,.2f}%".format(
                            round(prod, 2)).replace('.', ',')
                        if (ativo in ['CDI', 'IMA-B 5'] and custodiante == 'Índice') or (ativo not in ['CDI', 'IMA-B 5'] and custodiante != 'Índice'):
                            dados.append(
                                {**{**{'Ativo': ativo+' ('+custodiante+')'}, **colunas}, **{'Total': total}})

                df = df.groupby(['Ativo', 'Data', 'Custodiante'])[
                    'retorno_indice', 'Preço', 'Preço Ajustado'].mean().reset_index()
                for ind, row in df.iterrows():
                    ativo = row['Ativo'].strip()
                    data = row['Data']
                    custodiante = row['Custodiante']
                    menor_data = min(df[(df['Ativo'] == ativo) & (
                        df['Custodiante'] == custodiante)]['Data'].tolist())
                    menor_preco = min(df[(df['Data'] == menor_data) & (
                        df['Custodiante'] == custodiante) & (df['Ativo'] == ativo)]['Preço'].tolist())
                    indices = df[(df['Data'] <= data) & (df['Ativo'] == ativo) & (df['Custodiante'] == custodiante)].groupby(
                        ['Data'])['retorno_indice'].mean().reset_index()['retorno_indice'].tolist()
                    prod = np.prod(indices)
                    df.at[ind, 'Retorno'] = prod
                    if data > menor_data:
                        df.at[ind, 'Preço Ajustado'] = prod*menor_preco
                    else:
                        df.at[ind, 'Preço Ajustado'] = menor_preco

            if media_custodiante:
                df = df.groupby(['Data', 'Ativo', 'Custodiante'])[
                    'Retorno', 'Preço', 'Preço Ajustado'].mean().reset_index()
            df['Retorno'] = df['Retorno'].apply(lambda x: (x-1)*100)
            if 'retorno_indice' in df.columns:
                df = df.drop(columns=['retorno_indice'])
            df_download = df.copy(deep=False)
            df_download['Retorno'] = df_download['Retorno'].apply(
                lambda x: x/100)
            tabela = pd.DataFrame(dados)
            ordenacao = ['CDI', 'IMA-B 5', 'CDI (Índice)', 'IMA-B 5 (Índice)',]
            tabela['ordem'] = pd.Categorical(
                tabela['Ativo'],
                categories=ordenacao,
                ordered=True
            )
            tabela = tabela.sort_values(['ordem'], ascending=[True])
            tabela = tabela.drop(columns=['ordem'])
            df['ordem'] = pd.Categorical(
                df['Ativo'],
                categories=ordenacao,
                ordered=True
            )
            df = df.sort_values(['ordem', 'Data'], ascending=[True, True])
            df = df.drop(columns=['ordem'])
            tabela = tabela[['Ativo']+lista_meses+['Total']]
            tabela = tabela.fillna('-').replace('nan%', '-')
            tabela_download = tabela.copy(deep=False)
            for coluna in tabela_download.columns:
                if coluna != 'Ativo':
                    tabela_download[coluna] = tabela_download[coluna].apply(
                        lambda x: float(x.replace('%', '').replace(',', '.')) if '%' in x else None)
            util.download_excel_button([df_download, tabela_download], [
                                       'Evolução', 'Retorno %'], 'Download em Excel', 'Evolucao_precos_ajustados')

            fig = px.line(df, x="Data", y="Retorno",
                          title=f'Evolução base 100',
                          symbol=symbol,
                          color='Ativo')
            fig.update_layout(font=dict(size=15),
                              legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="auto"
            ),
                hovermode="x unified",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=16))
            fig.update_xaxes(dtick="M1", title='', tickformat="%m/%Y")
            fig.update_traces(hovertemplate="<br>Data: %{x|%d/%m/%Y}<br>"
                                            "Retorno: %{y:.2f}%<br>"
                              )

            st.plotly_chart(fig, use_container_width=True, )

            hide_table_row_index = """
                        <style>
                        thead tr th:first-child {display:none}
                        tbody th {display:none}
                        </style>
                        """
            st.markdown(hide_table_row_index, unsafe_allow_html=True)

            tamanho = len(lista_meses)
            if tamanho == 1:
                col1, _ = st.columns([2/12, 10/12])
            else:
                col1, _ = st.columns(
                    [(tamanho+1)/12, (12-tamanho)/12 if tamanho < 13 else 0.1])
            col1.table(tabela)

            fig = px.line(df[~df['Ativo'].isin(['CDI', 'IMA-B 5'])], x="Data", y="Preço Ajustado",
                          title=f'Evolução de preços ajustados',
                          symbol=symbol,
                          color='Ativo')
            fig.update_layout(font=dict(size=15),
                              legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="auto"
            ),
                hovermode="x unified",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=16))
            fig.update_xaxes(dtick="M1", title='', tickformat="%m/%Y")
            fig.update_traces(hovertemplate="<br>Data: %{x|%d/%m/%Y}<br>"
                                            "Preço Ajustado: %{y:.6f}<br>"
                              )

            st.plotly_chart(fig, use_container_width=True, )

            fig = px.line(df[~df['Ativo'].isin(['CDI', 'IMA-B 5'])], x="Data", y="Preço",
                          title=f'Evolução de preços',
                          symbol=symbol,
                          color='Ativo')
            fig.update_layout(font=dict(size=15),
                              legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="auto"
            ),
                hovermode="x unified",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=16))
            fig.update_xaxes(dtick="M1", title='', tickformat="%m/%Y")
            fig.update_traces(hovertemplate="<br>Data: %{x|%d/%m/%Y}<br>"
                                            "Preço: %{y:.6f}<br>"
                              )
            st.plotly_chart(fig, use_container_width=True, )


@try_error
def conferir_precos_ajustados(database, barra):
    st.title('Conferir preços ajustados por ativo e fundo')
    col1, col2, col3, col4 = st.columns([1, 1, 3, 3])
    data_inicial = col1.date_input(
        'Data Inicial', mutil.somar_dia_util(date.today(), -1))
    data_final = col2.date_input(
        'Data Final', mutil.somar_dia_util(date.today(), -1))
    ativo = col3.multiselect('Papel', [i[0].strip() for i in query_db(
        database, 'select distinct ativo from icatu.estoque_ativos order by ativo')])
    fundo = col4.multiselect('Fundo', [i[0].strip() for i in query_db(
        database, 'select nome from icatu.fundos  where tipo is not null order by nome')])
    fundos, ativos = '', ''
    if fundo:
        fundos = f"""AND f.nome in ({", ".join([f"'{i}'" for i in fundo]) if len(fundo) > 1  else f"'{fundo[0]}'"})"""
    if ativo:
        ativos = f"""AND ativo in ({", ".join([f"'{i}'" for i in ativo]) if len(ativo) > 1  else f"'{ativo[0]}'"})"""

    calc = st.button('Gerar informações')
    if calc:
        with st.spinner('Aguarde...'):
            sql = f"""
            with eventos as (

            select codigo, data_pagamento as data, sum(pu_evento) as pagamentos, 
            sum(pu_calculado) as pagamentos_calculados from icatu.fluxo_papeis fp 
            where tipo_id not in (8, 18, 9) 
            group by codigo, data_pagamento)

            select 
                distinct e.data, ativo, f.nome as fundo, preco, preco_ajustado, 
                coalesce(ev.pagamentos,0) as pagamentos, coalesce(ev.pagamentos_calculados,0) as pagamentos_calculados
            from icatu.estoque_ativos e 
            left join eventos ev on ev.data = e.data and ev.codigo = e.ativo
            left join icatu.fundos f on f.isin = e.fundo
            where  fonte <> 'BRITECH'
            and e.data between  '{mutil.somar_dia_util(data_inicial, -1).strftime('%Y-%m-%d')}'
            and '{data_final.strftime('%Y-%m-%d')}' 
            and (fic <> true or fic is null)
            and true {fundos} {ativos}
            
            """

            df = pd.DataFrame(database.query(sql))

            dados = {}
            for ind, row in df.iterrows():
                data = row['data'].strftime('%Y-%m-%d')
                ativo = row['ativo']
                fundo = row['fundo']
                if not ativo in dados:
                    dados[ativo] = {}
                if not data in dados[ativo]:
                    dados[ativo][data] = {}
                if not fundo in dados[ativo][data]:
                    dados[ativo][data][fundo] = {}
                dados[ativo][data][fundo]['preco'] = row['preco']
                dados[ativo][data][fundo]['preco_ajustado'] = row['preco_ajustado']

            def preco_d1(x):
                data_d1 = mutil.somar_dia_util(
                    x['data'], -1).strftime('%Y-%m-%d')
                try:
                    return dados[x['ativo']][data_d1][x['fundo']]['preco']
                except:
                    return None

            def preco_ajustado_d1(x):
                data_d1 = mutil.somar_dia_util(
                    x['data'], -1).strftime('%Y-%m-%d')
                try:
                    return dados[x['ativo']][data_d1][x['fundo']]['preco_ajustado']
                except:
                    return None

            def dif_preco_pagamentos(x):
                if x['pagamentos'] > 0 or x['pagamentos_calculados'] > 0:
                    return x['dif_preco'] + max(x['pagamentos'], x['pagamentos_calculados'])
                else:
                    return x['dif_preco']

            def dif_total(x):
                if x['dif_preco_pagamentos'] and x['dif_preco_ajustado']:
                    return abs(x['dif_preco_pagamentos'] - x['dif_preco_ajustado'])
                if x['dif_preco_ajustado'] and not x['dif_preco_pagamentos']:
                    return 0
                else:
                    return None

            def retorno_preco(x):
                data_d1 = mutil.somar_dia_util(
                    x['data'], -1).strftime('%Y-%m-%d')
                try:
                    preco_d1 = dados[x['ativo']][data_d1][x['fundo']]['preco']
                    if x['pagamentos'] > 0:
                        pagamentos = x['pagamentos']
                    elif x['pagamentos_calculados'] > 0:
                        pagamentos = x['pagamentos_calculados']
                    else:
                        pagamentos = 0
                    return (((x['preco'] + pagamentos)/preco_d1)-1)*100
                except:
                    return None

            def retorno_preco_ajustado(x):
                data_d1 = mutil.somar_dia_util(
                    x['data'], -1).strftime('%Y-%m-%d')
                try:
                    preco_d1 = dados[x['ativo']
                                     ][data_d1][x['fundo']]['preco_ajustado']
                    return ((x['preco_ajustado'] / preco_d1)-1)*100
                except:
                    return None

            df['preco_d1'] = df.apply(lambda x: preco_d1(x), axis=1)
            df['preco_ajustado_d1'] = df.apply(
                lambda x: preco_ajustado_d1(x), axis=1)
            df['dif_preco'] = df.apply(
                lambda x: x['preco'] - x['preco_d1'], axis=1)
            df['dif_preco_ajustado'] = df.apply(
                lambda x: x['preco_ajustado'] - x['preco_ajustado_d1'] if x['preco_ajustado_d1'] else None, axis=1)
            df['dif_preco_pagamentos'] = df.apply(
                lambda x: dif_preco_pagamentos(x), axis=1)
            df['dif_total'] = df.apply(lambda x: dif_total(x), axis=1)
            df['retorno_preco'] = df.apply(lambda x: retorno_preco(x), axis=1)
            df['retorno_preco_ajustado'] = df.apply(
                lambda x: retorno_preco_ajustado(x), axis=1)
            df['dif_perc'] = df.apply(lambda x: abs(
                x['retorno_preco_ajustado'] - x['retorno_preco']) if x['retorno_preco_ajustado'] else None, axis=1)
            df = df.sort_values(['dif_perc'], ascending=[False])
            df = df[df['data'] >= data_inicial]
            df = df[df['data'] <= data_final]

            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_grid_options(enableRangeSelection=True)
            gb.configure_grid_options(enableCellTextSelection=True)
            gb = gb.build()
            gb['columnDefs'] = [
                {'field': "data", 'headerName': 'Data', 'pinned': 'left',
                 'type': ["dateColumnFilter", "customDateTimeFormat"], 'custom_format_string': 'dd/MM/yyyy'},
                {'field': 'ativo', 'headerName': 'Ativo', 'pinned': 'left', },
                {'field': 'fundo', 'headerName': 'Fundo', 'pinned': 'left', },
                {'field': 'dif_perc',  'headerName': 'Diferença Percentual',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6})+ '%';"},
                {'field': 'retorno_preco',  'headerName': 'Ret Preço',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6})+ '%';"},
                {'field': 'retorno_preco_ajustado',  'headerName': 'Ret Preço Ajustado',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6})+ '%';"},
                {'field': 'preco',  'headerName': 'Preço',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6});"},
                {'field': 'preco_d1',  'headerName': 'Preço D-1',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6});"},
                {'field': 'dif_preco',  'headerName': 'Dif. Preço',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6});"},
                {'field': 'pagamentos',  'headerName': 'Pagamentos',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6});"},
                {'field': 'pagamentos_calculados',  'headerName': 'Pagamentos Calculados',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6});"},
                {'field': 'preco_ajustado',  'headerName': 'Preço Ajustado',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6});"},
                {'field': 'preco_ajustado_d1',  'headerName': 'Preço Ajuste D-1',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6});"},
                {'field': 'dif_preco_ajustado',  'headerName': 'Dif Preço Ajuste',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6});"},
                {'field': 'dif_preco_pagamentos',  'headerName': 'Dif Após Pagamentos',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6});"},
                {'field': 'dif_total',  'headerName': 'Dif Total',
                 'type': ["numericColumn", "numberColumnFilter", "customNumericFormat"],
                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6, maximumFractionDigits: 6});"},]

            custom_css = {
                ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                ".ag-row":  {  "font-size": "16px !important;"}
                }

            new_df = AgGrid(
                df,
                gridOptions=gb,
                update_mode='NO_UPDATE',
                fit_columns_on_grid_load=False,
                allow_unsafe_jscode=True,
                enableRangeSelection=True,
                custom_css=custom_css,
                height=400,
                enable_enterprise_modules=True)


@try_error
def conferir_pagamentos_calculados(database, barra):
    st.title('Conferir Pagamentos Calculados para o Dia')
    col1, _ = st.columns([1, 8])
    data = col1.date_input('Selecione a data', mutil.somar_dia_util(date.today(), -1))
    gerar = st.button('Gerar relatório')
    if gerar:
        with st.spinner('Aguarde...'):
            outlook = win32.Dispatch('outlook.application', pythoncom.CoInitialize()).GetNamespace("MAPI")
            stores = outlook.Stores
            pasta = stores.Session.Folders[env.EMAIL_FOLDER].folders('Pagamentos do Dia')
            messages = pasta.Items
            messages = [message for message in messages if message.Senton.date() == data]
            if not messages:
                st.caption('O e-mail de pagamentos da CETIP não foi enviado.')
            else:
                cwd = os.getcwd()
                caminho_download = os.path.join(cwd, 'assets', 'email_cetip')
                Path(caminho_download).mkdir(parents=True, exist_ok=True)
                
                email_nao_enviado = True
                for message in messages:
                    arquivo = [i for i in message.Attachments if str(i).lower().endswith('.xls')]
                    if message.Senton.date() == data and arquivo:
                        email_nao_enviado = False
                        attachment = arquivo[0]
                        attachment.SaveAsFile(os.path.join( caminho_download, str(attachment)))
                        df = pd.read_excel(os.path.join(caminho_download, str(attachment)))
                        shutil.rmtree(caminho_download, ignore_errors=True)

                        sql = f"""
                            select distinct ativo 
                            from icatu.estoque_ativos where fonte <> 'BRITECH'
                            and fundo not in ('012811','012812')
                        """
                        df = df[df['Cd Ativo'].isin([i['ativo'] for i in query(database, sql)])]
                        sql = f"""
                            select f.codigo, em.empresa as emissor, sum(pu_calculado) as pagamentos
                            from icatu.fluxo_papeis f
                            left join icatu.info_papeis i on i.codigo = f.codigo
                            left join icatu.emissores em on em.cnpj = i.cnpj
                            where data_pagamento = '{data.strftime('%Y-%m-%d')}'
                            and f.codigo in (select distinct ativo from icatu.estoque_ativos where fonte <> 'BRITECH' 
                            and data = '{data.strftime('%Y-%m-%d')}')
                            group by f.codigo, em.empresa
                            having sum(pu_calculado) is not null
                        """
                        calculos = database.query(sql)

                        ativos = [i['ativo'] for i in database.query(
                            f"select distinct ativo from icatu.estoque_ativos")]
                        emissores = {i['codigo']: i['empresa'] for i in database.query(
                            "select i.codigo, em.empresa from icatu.info_papeis i left join icatu.emissores em on em.cnpj = i.cnpj")}

                        pagamentos = {}
                        for ind, row in df.iterrows():
                            ativo = str(row['Cd Ativo']).strip()
                            if not ativo in pagamentos and ativo in ativos:
                                total = float(row['Vr Rec CETIP'].replace('.', '').replace(',', '.')) if isinstance(
                                    row['Vr Rec CETIP'], str) else float(row['Vr Rec CETIP'])
                                qtd = float(row['Quantidade'].replace('.', '').replace(',', '.')) if isinstance(
                                    row['Quantidade'], str) else float(row['Quantidade'])
                                if qtd > 0:
                                    pagamentos[ativo] = total / qtd

                        if not pagamentos and not calculos:
                            st.caption('Não houve pagamentos na data buscada.')
                        else:
                            batimento = {}
                            for linha in calculos:
                                if not linha['codigo'] in batimento:
                                    batimento[linha['codigo']] = {}
                                    batimento[linha['codigo']]['emissor'] = linha['emissor']
                                if not 'calculado' in batimento[linha['codigo']]:
                                    batimento[linha['codigo']]['calculado'] = linha['pagamentos']

                            for codigo in pagamentos:
                                if not codigo in batimento:
                                    batimento[codigo] = {}
                                    batimento[codigo]['emissor'] = emissores[codigo]
                                if not 'cetip' in batimento[codigo]:
                                    batimento[codigo]['cetip'] = pagamentos[codigo]

                            diferenca = []
                            for ativo in batimento:
                                emissor = batimento[ativo]['emissor']
                                calculado = batimento[ativo]['calculado'] if 'calculado' in batimento[ativo] else None
                                cetip = batimento[ativo]['cetip'] if 'cetip' in batimento[ativo] else None
                                dif = abs(((cetip - calculado) / cetip)) * 100 if calculado and cetip else 100
                                diferenca.append({
                                    'Ativo': ativo,
                                    'Emissor': emissor,
                                    'Eventos Calculadora': "{:,.6f}".format(calculado).replace(",", "x").replace(".", ",").replace("x", ".") if calculado else '-',
                                    'Eventos CETIP': "{:,.6f}".format(cetip).replace(",", "x").replace(".", ",").replace("x", ".") if cetip else '-',
                                    'Dif. Percentual': "{:,.2f}".format(dif).replace(",", "x").replace(".", ",").replace("x", ".")
                                })
                            hide_table_row_index = """
                            <style>
                            thead tr th:first-child {display:none}
                            tbody th {display:none}
                            </style>
                            """
                            st.markdown(hide_table_row_index, unsafe_allow_html=True)
                            col1, _ = st.columns([1, 1])
                            col1.table(pd.DataFrame(diferenca).sort_values(
                                ['Dif. Percentual'], ascending=[False]))
                        break
                if email_nao_enviado:
                    st.caption('O e-mail de pagamentos da CETIP não foi enviado.')
        

def evolucao_taxas(database, barra):
    st.subheader('Evolução das Taxas')
    tipo = barra.selectbox('Escolha a tela', ['Único ativo', 'Vários ativos'])
    if tipo == 'Único ativo':
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
        sql = """
        select distinct ativo from icatu.estoque_ativos 
            union
            select distinct codigo as ativo from icatu.ativos_anbima aa 
            order by ativo
        """
        lista_ativos = [i[0].strip() for i in query_db(database, sql)]
        ativo = col1.selectbox('Ativo', lista_ativos, key='sv')
        data_inicial = mutil.somar_dia_util(date.today(), -40)
        data_inicial = col2.date_input('Data Inicial', data_inicial)
        data_final = col3.date_input('Data Final')
        fonte = col4.multiselect('Fonte', ['BRADESCO', 'SANTANDER','DAYCOVAL', 'MELLON', 'ITAU', 'ANBIMA', 'OUTROS',
                                           'CALCULADORA (ITAU)', 'CALCULADORA (MELLON)',  'CALCULADORA (SANTANDER)', 
                                           'CALCULADORA (BRADESCO)','CALCULADORA (DAYCOVAL)',
                                           'GERENCIAL PRÉVIO (ANBIMA)', 'GERENCIAL PRÉVIO (BRADESCO)', 
                                           'GERENCIAL PRÉVIO (ITAU)','GERENCIAL PRÉVIO (DAYCOVAL)', 
                                           'GERENCIAL PRÉVIO (SANTANDER)', 'GERENCIAL PRÉVIO (MELLON)',])

        try:
            sql = f"""  select codigo, data, spread, fonte from icatu.taxas_ativos where codigo = '{ativo}' and spread is not null
                        union
                        select codigo, data, spread, 'ANBIMA' as fonte from icatu.ativos_anbima where codigo = '{ativo}' and spread is not null
                        order by data desc
                    """
            dados = query_db(database, sql)
            df_spread = pd.DataFrame(
                dados, columns=['Código', 'Data', 'Spread', 'Fonte'])
            df_spread = df_spread[df_spread['Data'] >= data_inicial]
            df_spread = df_spread[df_spread['Data'] <= data_final]
            if fonte:
                df_spread = df_spread[df_spread['Fonte'].isin(fonte)]

            fig = px.line(df_spread, x="Data", y="Spread", color='Fonte',
                          title=f'Evolução de spread ({ativo})', markers=True, symbol="Fonte")
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
                                            "Spread: %{y:.6f}<br>"
                              )

            st.plotly_chart(fig, use_container_width=True, )

            sql = f"""  select codigo, data, taxa, concat('GERENCIAL PRÉVIO (', fonte, ')') as fonte from icatu.gerencial_previo where codigo = '{ativo}'
                        union
                        select codigo, data, taxa, fonte from icatu.taxas_ativos where codigo = '{ativo}' and spread is not null
                        union
                        select codigo, data, taxa, 'ANBIMA' as fonte from icatu.ativos_anbima where codigo = '{ativo}'
                        order by data
                    """
            dados = database.query_select(sql)
            df_taxas = pd.DataFrame(
                dados, columns=['Código', 'Data', 'Taxa', 'Fonte'])
            df_taxas = df_taxas[df_taxas['Data'] >= data_inicial]
            df_taxas = df_taxas[df_taxas['Data'] <= data_final]
            if fonte:
                df_taxas = df_taxas[df_taxas['Fonte'].isin(fonte)]
            fig = px.line(df_taxas, x="Data", y="Taxa", color='Fonte', title=f'Comparação de taxas ({ativo})',
                          markers=True, symbol="Fonte")
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
                                            "Taxa: %{y:.6f}<br>"
                              )

            st.plotly_chart(fig, use_container_width=True, )

            sql = f"""  select codigo, data, preco, concat('GERENCIAL PRÉVIO (', fonte, ')') as fonte from icatu.gerencial_previo where codigo = '{ativo}'
                        union
                        select ativo, data, preco, fonte from icatu.estoque_ativos where ativo = '{ativo}' and fonte <> 'BRITECH' and fundo not in ('012811', '012812')
                        union
                        select codigo, data, preco, 'ANBIMA' as fonte from icatu.ativos_anbima where codigo = '{ativo}'
                        order by data
                    """
            dados = database.query_select(sql)
            df_precos = pd.DataFrame(
                dados, columns=['Código', 'Data', 'Preço', 'Fonte'])
            df_precos = df_precos[df_precos['Data'] >= data_inicial]
            df_precos = df_precos[df_precos['Data'] <= data_final]
            if fonte:
                df_precos = df_precos[df_precos['Fonte'].isin(fonte)]
            fig = px.line(df_precos, x="Data", y="Preço", color='Fonte',
                          title=f'Comparação de preços ({ativo})', markers=True, symbol="Fonte")
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
                                            "Preço: %{y:.6f}<br>"
                              )

            st.plotly_chart(fig, use_container_width=True, )

            sql_taxas = f"""
            select codigo, data, preco, taxa, Null as spread,  concat('GERENCIAL PRÉVIO (', fonte, ')') as fonte from icatu.gerencial_previo where codigo = '{ativo}'
                union
                select codigo, data, preco, taxa, spread, fonte from icatu.taxas_ativos where codigo = '{ativo}'  
                union
                select codigo, data, preco, taxa, spread, 'ANBIMA' as fonte from icatu.ativos_anbima where codigo = '{ativo}'
                order by data
            """
            sql_precos = f"""
                select distinct data, ativo, preco, fonte
                from icatu.estoque_ativos where fonte <> 'BRITECH'
                and ativo = '{ativo}' and preco is not null order by data 
            """
            dados_taxas = database.query_select(sql_taxas)
            dados_precos = database.query_select(sql_precos)
            df_taxas = pd.DataFrame(dados_taxas, columns=[
                                    'Código', 'Data', 'Preço', 'Taxa', 'Spread',  'Fonte'])
            df_precos = pd.DataFrame(dados_precos, columns=[
                                     'Data', 'Código', 'Preço', 'Fonte'])
            df_precos['Código'] = df_precos['Código'].apply(
                lambda x: x.strip())

            df_taxas = df_taxas[(df_taxas['Data'] >= data_inicial) & (
                df_taxas['Data'] <= data_final)]
            df_precos = df_precos[(df_precos['Data'] >= data_inicial) & (
                df_precos['Data'] <= data_final)]

            util.download_excel_button([df_taxas, df_precos], [
                                       'Taxas', 'Preços'], 'Download em Excel ', 'taxas')

            # df['Data'] = df['Data'].apply(lambda x: x.strftime('%d/%m/%Y') if not pd.isnull(x) else x)
            # df['Taxa'] = df['Taxa'].apply(lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", ".") if x != "Erro" else x)
            # df['Spread'] = df['Spread'].apply(lambda x: "{:,.2f}".format(x).replace(",", "x").replace(".", ",").replace("x", ".") if x != "Erro" else x)
            # df['Preço'] = df['Preço'].apply(lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", ".") if x != "Erro" else x)

        except:
            st.caption('Houve um erro')

    if tipo == 'Vários ativos':
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
        sql = """
        select distinct ativo from icatu.estoque_ativos 
            union
            select distinct codigo as ativo from icatu.ativos_anbima aa 
            order by ativo
        """
        lista_ativos = [i[0].strip() for i in query_db(database, sql)]
        ativos = col1.multiselect('Ativos', lista_ativos, key='sv')
        ativos = ', '.join([f"'{i}'" for i in ativos])
        data_inicial = mutil.somar_dia_util(date.today(), -40)
        data_inicial = col2.date_input('Data Inicial', data_inicial)
        data_final = col3.date_input('Data Final')
        fonte = col4.multiselect('Fonte', ['BRADESCO', 'SANTANDER', 'MELLON','DAYCOVAL', 'ITAU', 'ANBIMA', 'OUTROS',
                                           'CALCULADORA (ITAU)', 'CALCULADORA (MELLON)',  'CALCULADORA (SANTANDER)', 
                                           'CALCULADORA (BRADESCO)',
                                           'CALCULADORA (DAYCOVAL)'])

        sql = f"""  select codigo, data, spread, fonte from icatu.taxas_ativos where codigo in ({ativos}) and spread is not null
                    union
                    select codigo, data, spread, 'ANBIMA' as fonte from icatu.ativos_anbima where codigo in ({ativos}) and spread is not null
                    order by data desc
                """
        dados = query_db(database, sql)
        df_spread = pd.DataFrame(
            dados, columns=['Código', 'Data', 'Spread', 'Fonte'])
        df_spread = df_spread[df_spread['Data'] >= data_inicial]
        df_spread = df_spread[df_spread['Data'] <= data_final]
        if fonte:
            df_spread = df_spread[df_spread['Fonte'].isin(fonte)]

        fig = px.line(df_spread, x="Data", y="Spread", color='Código',
                      title=f'Evolução de spread', markers=True, symbol="Fonte")
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
                                        "Spread: %{y:.6f}<br>",
                          marker=dict(size=8))

        st.plotly_chart(fig, use_container_width=True, )
