
import pandas as pd
import streamlit as st
from models import util as mutil
from datetime import date
from views import util
from models import automacao
from models import b3
import math
import models.calculadora as calculadora
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, DataReturnMode


@st.cache_resource(show_spinner=False)
def query_db(_database, query):
    return _database.query_select(query)


@st.cache_resource(show_spinner=False)
def get_curva_di(_database, data=date.today()):
    return [i[3] for i in _database.curva_di(data)]


@st.cache_resource(show_spinner=False)
def get_curva_ntnb(_database, data=date.today()):
    return automacao.curva_ntnb_interpolada(_database, data)


@st.cache_resource(show_spinner=False)
def calc_pu_b3(ativo, taxa_corretora):
    pu_b3 = b3.b3()
    pu_b3 = pu_b3.calcular_pu(ativo, date.today(), taxa_corretora)['PU']
    return pu_b3


def fluxo_ativos_calc(db):
    sql = '''SELECT codigo, data_pagamento, percentual, pu_evento, tipo_evento
                    FROM icatu.fluxo_papeis p
                    LEFT JOIN icatu.tipo_eventos t ON t.id = p.tipo_id
                    ORDER BY codigo, data_pagamento, tipo_id'''
    dados = query_db(db, sql)
    fluxo_papeis = {}
    for dado in dados:
        if not dado[0].strip() in fluxo_papeis:
            codigo = dado[0].strip()
            fluxo_papeis[dado[0].strip()] = []
        temp = fluxo_papeis[codigo]
        temp.append(dado[1:])
        fluxo_papeis[codigo] = temp

    return fluxo_papeis


def info_papeis_calculo(db):
    dados = query_db(db, '''
                    SELECT distinct indice, percentual, juros, data_emissao, valor_emissao,
                        inicio_rentabilidade,  data_vencimento, i.empresa, codigo, tipo_ativo,
                        aniversario, ipca_negativo, ipca_2meses, e.empresa, i.isin
                    FROM icatu.info_papeis i
                    left join icatu.emissores e on e.cnpj = i.cnpj
                    ''')

    info = {}
    for linha in dados:
        info[linha[8].strip()] = {
            'indice': linha[0].strip(),
            'percentual': linha[1] if linha[1] else 100,
            'juros': linha[2] if linha[2] else 0,
            'data_emissao': linha[3],
            'valor_emissao': linha[4],
            'inicio_rentabilidade': linha[5],
            'data_vencimento': linha[6],
            'empresa': linha[7].replace('.', '') if linha[7] else None,
            'codigo': linha[8].strip(),
            'tipo_ativo': linha[9],
            'aniversario': linha[10],
            'ipca_negativo': linha[11],
            'ipca_2meses': linha[12],
            'emissor': linha[13].replace('.', '') if linha[13] else None,
            'isin': linha[14].strip() if linha[14] else ''
        }
    return info


def lista_de_ativos(db):
    return query_db(db, f'''SELECT
                        distinct codigo, e.empresa
                    FROM icatu.info_papeis i
                    left join icatu.emissores e on e.cnpj = i.cnpj
                    join icatu.estoque_ativos et on et.ativo = i.codigo
                    and fonte <> 'BRITECH' 
                    and et.fundo not in ('012812', '012811')
                    where et.data = '{mutil.somar_dia_util(date.today(), -1).strftime('%Y-%m-%d')}'
                    ''')


def lista_emissores(db):
    sql = f"""
        select distinct e.empresa
        from icatu.emissores e
        join icatu.info_papeis i on i.cnpj = e.cnpj
        join icatu.estoque_ativos et on et.ativo = i.codigo
        where et.data = '{mutil.somar_dia_util(date.today(), -1).strftime('%Y-%m-%d')}'
        and fonte <> 'BRITECH'
        order by empresa
    """
    lista_emissores = query_db(db, sql)
    return lista_emissores


def lista_grupos(db):
    sql = """
        select
            distinct
            g.nome as grupo, empresa
        from icatu.emissores e
        left join icatu.grupo_emissores g on g.id = e.grupo
        where g.nome is not null
    """
    dados = query_db(db, sql)
    grupos = {}
    for linha in dados:
        grupos[linha[1].strip().replace(
            '.', '')] = linha[0].strip().replace('.', '')
    return grupos


def patrimonio_fundos(db):
    sql = f"""select
                nome,
                coalesce(round((cota * quantidade)::numeric*pl_alocavel::numeric,0),1) as pl_fundo
            from icatu.fundos f
            left join icatu.posicao_fundos p on p.fundo = f.isin
            where data = '{mutil.somar_dia_util(date.today(), -1).strftime('%Y-%m-%d')}'
            and f.tipo is not null
            and f.isin not in ('012812', '012811')
            order by nome"""

    dados = query_db(db, sql)
    return dados


def financeiro_fundos(db):
    sql = f"""
        with pl_alocado as (
            select
                distinct
                fundo,
                sum(financeiro) as pl_credito
            from (
            select
                distinct
                f.nome as fundo,
                ativo,
                (quantidade_garantia + quantidade_disponivel) * preco as financeiro
            from icatu.estoque_ativos e
            left join icatu.fundos f on f.isin = e.fundo
            where data = '{mutil.somar_dia_util(date.today(), -1).strftime('%Y-%m-%d')}'
            and fonte <> 'BRITECH'
            and (fic <> true or fic is null)) t
            group by fundo
        )

        select
            distinct
            f.nome,
            r.nome,
            c.nome,
            p.pl_credito,
            f.codigo_brit,
            f.cnpj,
            ct.nome_curto,
            f.nome_xml,
            f.cetip
        from icatu.fundos f
        left join icatu.risco_fundos r on r.id = f.id_risco
        left join icatu.classificacao_fundos c on c.id = f.id_classificacao
        left join icatu.custodiantes ct on ct.cnpj = f.custodiante
        left join pl_alocado p on p.fundo = f.nome
        where f.tipo is not null and f.isin not in ('012812','012811')
    """
    dados = query_db(db, sql)
    info_fundos = {}
    for linha in dados:
        info_fundos[linha[0].strip()] = {}
        info_fundos[linha[0].strip()]['risco'] = linha[1].strip()
        info_fundos[linha[0].strip()]['classe'] = linha[2].strip()
        info_fundos[linha[0].strip()]['pl_credito'] = float(
            linha[3]) if linha[3] else 0
        info_fundos[linha[0].strip()]['codigo_brit'] = linha[4].strip()
        cnpj = linha[5].strip()[:2]+'.' + linha[5].strip()[2:5]+'.' + linha[5].strip()[
            5:8]+'/'+linha[5].strip()[8:12] + '-'+linha[5].strip()[-2:]
        info_fundos[linha[0].strip()]['cnpj'] = cnpj
        info_fundos[linha[0].strip()]['custodiante'] = linha[6].strip()
        info_fundos[linha[0].strip()]['nome_cliente'] = linha[7].strip()
        info_fundos[linha[0].strip()]['cetip'] = linha[8].strip(
        ) if linha[8] else ''

    return info_fundos


@st.cache_resource(show_spinner=False)
def preco_ativos(_db, tipo, data=date.today()):
    sql = f""" with
        taxas as (
            select *,
            case
                when fonte = 'ANBIMA' then 1
                when fonte like '%CALCULADORA%' or fonte = 'OUTROS' then 2
                else 3
            end as rank_fonte
            from (
                select distinct data, codigo, preco, taxa, duration, spread, 'ANBIMA' as fonte
                from icatu.ativos_anbima
                union
                select distinct data, codigo, preco, taxa, duration, spread, fonte
                from icatu.taxas_ativos) t
        ),

        tx as (
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
        group by data, codigo, round(preco::numeric,2)),


        preco as (
            select
                ativo,
                (array_agg(preco))[1] as preco
            from icatu.estoque_ativos
            where data = '{mutil.somar_dia_util(date.today(), -1).strftime('%Y-%m-%d')}'
            and fonte <> 'BRITECH'
            group by ativo
        ),

        rating as (
        SELECT
            codigo,
            rating as ultimo_rating
        FROM icatu.view_ultimo_rating_ativos)

        select
            distinct
            et.ativo,
            f.nome as fundo,
            e.empresa as emissor,
            g.nome as grupo,
            (quantidade_garantia + quantidade_disponivel) as quantidade,
            (quantidade_garantia + quantidade_disponivel) * p.preco as financeiro,
            p.preco,
            i.tipo_ativo,
            i.data_vencimento,
            case
                when i.indice = 'DI' and percentual > 100 then '%CDI'
                when i.indice = 'DI' and (percentual = 100 or percentual is null) then 'CDI+'
                when i.indice = 'IPCA' then 'IPCA+'
                when i.indice = 'IGP-M' then 'IGPM+'
                else i.indice
            end as indice,
            r.ultimo_rating,
            t.taxa,
            t.spread,
            t.duration,
            i.isin
        from icatu.estoque_ativos et
        left join icatu.info_papeis i on i.codigo = et.ativo
        left join icatu.emissores e on e.cnpj = i.cnpj
        left join icatu.grupo_emissores g on g.id = e.grupo
        left join icatu.fundos f on f.isin = et.fundo
        left join preco p on p.ativo = et.ativo
        left join rating r on r.codigo = et.ativo
	    left join tx t on t.codigo = et.ativo and t.data = et.data and round(p.preco::numeric,2) = t.preco
        where et.data = '{mutil.somar_dia_util(date.today(), -1).strftime('%Y-%m-%d')}'
        and et.fonte <> 'BRITECH'
        and f.isin not in ('012812', '012811')
        and (fic <> true or fic is null)
    """
    dados = query_db(_db, sql)

    curva_di = get_curva_di(_db, date.today())
    papeis_calculo = info_papeis_calculo(_db)
    fluxo_papeis = fluxo_ativos_calc(_db)

    info_ativos = {}
    precos = {}
    for linha in dados:
        ativo = linha[0].strip()
        if ativo not in info_ativos:
            info_ativos[ativo] = {}
            info_ativos[ativo]['grupo'] = linha[3].strip().replace(
                '.', '') if linha[3] else ''
            info_ativos[ativo]['emissor'] = linha[2].strip().replace(
                '.', '') if linha[2] else ''
            info_ativos[ativo]['preco'] = linha[6]
            info_ativos[ativo]['tipo'] = linha[7].strip() if linha[7] else ''
            info_ativos[ativo]['vencimento'] = linha[8]
            info_ativos[ativo]['indice'] = linha[9].strip() if linha[9] else ''
            info_ativos[ativo]['rating'] = linha[10].strip(
            ) if linha[10] else ''
            info_ativos[ativo]['taxa'] = linha[11] if linha[11] else None
            info_ativos[ativo]['spread'] = linha[12] if linha[12] else None
            info_ativos[ativo]['duration'] = linha[13] if linha[13] else None
            info_ativos[ativo]['isin'] = linha[14].strip() if linha[14] else ''
        fundo = linha[1].strip()
        if fundo not in info_ativos[ativo]:
            info_ativos[ativo][fundo] = {}
        info_ativos[ativo][fundo]['qtd'] = linha[4]
        if tipo == 'Dia Anterior':
            info_ativos[ativo][fundo]['financeiro'] = linha[5]
        else:
            try:
                taxa = info_ativos[ativo]['taxa']
                qtd = info_ativos[ativo][fundo]['qtd']
                if not ativo in precos:
                    precos[ativo] = {}
                if not taxa in precos[ativo]:
                    info, fluxo = papeis_calculo[ativo], fluxo_papeis[ativo]
                    calculo = calculadora.papel(info, fluxo, _db)
                    preco_calculado = calculo.duration(
                        date.today(), taxa, curva_di)['PU']
                    info_ativos[ativo][fundo]['financeiro'] = preco_calculado * qtd
                    info_ativos[ativo]['preco'] = preco_calculado
                    precos[ativo][taxa] = preco_calculado
                else:
                    info_ativos[ativo][fundo]['financeiro'] = precos[ativo][taxa] * qtd
                    info_ativos[ativo]['preco'] = precos[ativo][taxa]
            except:
                info_ativos[ativo][fundo]['financeiro'] = linha[5]
    return info_ativos


def financeiro_emissores(db):
    sql = f"""
        select
            distinct
            empresa,
            fundo,
            sum(financeiro) as financeiro
        from (
        select
            distinct
            ativo,
            f.nome as fundo,
            em.empresa,
            (quantidade_garantia + quantidade_disponivel)*preco as financeiro
        from icatu.estoque_ativos e
        left join icatu.fundos f on f.isin = e.fundo
        left join icatu.info_papeis i on i.codigo = e.ativo
        left join icatu.emissores em on em.cnpj = i.cnpj
        where data = '{mutil.somar_dia_util(date.today(), -1).strftime('%Y-%m-%d')}'
        and fonte <> 'BRITECH'
        and f.isin not in ('012812', '012811')
        and (fic <> true or fic is null)) t
        group by empresa, fundo
    """

    dados = query_db(db, sql)
    info_emissores = {}
    for linha in dados:
        emissor = linha[0].strip().replace('.', '') if linha[0] else ''
        if not emissor in info_emissores:
            info_emissores[emissor] = {}
        info_emissores[emissor][linha[1].strip()] = float(linha[2])

    return info_emissores


def financeiro_grupos(db):
    sql = f"""
      select
            distinct
            grupo,
            fundo,
            sum(financeiro) as financeiro
        from (
        select
            distinct
            ativo,
            f.nome as fundo,
            g.nome as grupo,
            (quantidade_garantia + quantidade_disponivel)*preco as financeiro
        from icatu.estoque_ativos e
        left join icatu.fundos f on f.isin = e.fundo
        left join icatu.info_papeis i on i.codigo = e.ativo
        left join icatu.emissores em on em.cnpj = i.cnpj
		left join icatu.grupo_emissores g on g.id = em.grupo
        where data = '{mutil.somar_dia_util(date.today(), -1).strftime('%Y-%m-%d')}'
        and fonte <> 'BRITECH'
        and f.isin not in ('012812', '012811')
        and (fic <> true or fic is null)) t
        group by grupo, fundo
    """

    dados = query_db(db, sql)
    info_grupos = {}
    for linha in dados:
        if not linha[0].strip().replace('.', '') in info_grupos:
            info_grupos[linha[0].strip().replace('.', '')] = {}
        info_grupos[linha[0].strip().replace('.', '')][linha[1].strip()] = float(linha[2])

    return info_grupos


def boletas(db):
    st.markdown('# Simulação de Boletas')
    st.markdown("""[Comparação de Portfólios dos Fundos](https://app.powerbi.com/reportEmbed?reportId=b0559159-ce16-45ab-9f28-395c5f2d8f96&autoAuth=true&ctid=828d299c-d85c-4fc7-abf2-9c0724378d20&navContentPaneEnabled=false) """)
    try:
        tipo_operacao = None
        l_emissores = lista_emissores(db)
        lista_ativos = lista_de_ativos(db)
        curva_di = get_curva_di(db, date.today())
        curva_ntnb = get_curva_ntnb(db, date.today())
        info_fundos = financeiro_fundos(db)
        info_emissores = financeiro_emissores(db)
        info_grupos = financeiro_grupos(db)
        grupos = lista_grupos(db)
        papeis_calculo = info_papeis_calculo(db)
        fluxo_papeis = fluxo_ativos_calc(db)
        info_ativos_dia_anterior = preco_ativos(db, 'Dia Anterior', date.today())
        info_ativos_hoje = preco_ativos(db, 'Hoje', date.today())

        if not 'calc' in st.session_state:
            st.session_state['calc'] = False
        if not 'dados' in st.session_state:
            st.session_state['dados'] = None

        col1, col2, col3 = st.columns([1, 1, 1])
        classe_fundos = col1.multiselect('Classificação', set([info_fundos[i]['classe'] for i in info_fundos]))
        risco_fundos = col2.multiselect('Risco', ['G1', 'G2', 'G3', 'G4'])

        if classe_fundos and not risco_fundos:
            fundos = col3.multiselect('Fundo', [i for i in info_fundos if info_fundos[i]['classe'] in classe_fundos])
            if not fundos:
                fundos = [i for i in info_fundos if info_fundos[i]['classe'] in classe_fundos]
        elif classe_fundos and risco_fundos:
            fundos = col3.multiselect('Fundo', [i for i in info_fundos if info_fundos[i]
                                      ['classe'] in classe_fundos and info_fundos[i]['risco'] in risco_fundos])
            if not fundos:
                fundos = [i for i in info_fundos if info_fundos[i]['classe']
                          in classe_fundos and info_fundos[i]['risco'] in risco_fundos]
        elif risco_fundos and not classe_fundos:
            fundos = col3.multiselect('Fundo', [i for i in info_fundos if info_fundos[i]['risco'] in risco_fundos])
            if not fundos:
                fundos = [i for i in info_fundos if info_fundos[i]['risco'] in risco_fundos]
        else:
            fundos = col3.multiselect('Fundo', [i[0].strip() for i in query_db(
                db, 'select distinct nome from icatu.fundos where tipo is not null order by nome')])
            if not fundos:
                fundos = [i[0].strip() for i in query_db(
                    db, 'select distinct nome from icatu.fundos where tipo is not null order by nome')]

        col1, col2, col3 = st.columns([1, 1, 1])
        grupo = col1.multiselect('Grupo', [i for i in info_grupos])
        if grupo:
            emissor = col2.multiselect('Emissor', [i for i in grupos if grupos[i] in grupo])
            if not emissor:
                emissor = [i for i in grupos if grupos[i] in grupo]
        else:
            emissor = col2.multiselect('Emissor', [i[0].strip().replace('.', '') for i in l_emissores])
        if emissor:
            ativos = col3.multiselect('Ativo', [i[0].strip() for i in lista_ativos if i[1] and i[1].strip().replace('.', '') in emissor])
        else:
            ativos = col3.multiselect('Ativo', sorted([ativo for ativo in info_ativos_dia_anterior]))

        # ver_pl_atual = col1.checkbox('Mostrar coluna %PL atual', value=True)
        ver_pl_atual = True
        tipo_operacao = col1.radio('Tipo de simulação', ('Ajuste',
                                                         'Ajuste Proporcional',
                                                         'Externa por Financeiro',
                                                         'Externa por % do PL',
                                                         'Externa por Quantidade'))
        usar_banda = False
        if not tipo_operacao == "Ajuste Proporcional":
            usar_banda = col2.checkbox('Utilizar banda em %PL', value=True)
            risco = col3.checkbox('Alocação por grupo de risco')
        else:
            risco = False
            redistribuir = col3.radio('Tipo de Ajuste', ('Distribuir proporcionalmente', 'Forçar até o objetivo'))
        data_precos = col2.radio('Referência de Preço', ('Dia Anterior','Hoje'))
        permite_ajuste = False
        if tipo_operacao not in ('Ajuste', "Ajuste Proporcional"):
            permite_ajuste = st.checkbox('Permitir Ajuste', False)
        tipo_risco = None
        if risco and tipo_operacao == 'Externa por % do PL':
            tipo_risco = '% do PL'
        if risco and tipo_operacao != 'Externa por % do PL':
            tipo_risco = 'Proporção da alocação'
        col1, _ = st.columns([1, 3])

        custom_css = {
            ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
            ".ag-header-cell":{"background-color": "#0D6696 !important", "color": "white"},
            '.ag-header-group-cell':{"background-color": "#2E96BF","color": "white"},
            ".ag-row":  {  "font-size": "16px !important;"}}

        if not ativos and emissor:
            ativos = [i[0].strip() for i in lista_ativos if i[1]and i[1].strip().replace('.', '') in emissor]

    except:
        ativos = None
        st.caption('Houve um erro')
    alocacao_incorreta = False
    if ativos or tipo_operacao == 'Ajuste Proporcional':
        try:
            dados = []
            if data_precos == 'Dia Anterior':
                info_ativos = info_ativos_dia_anterior
            else:
                info_ativos = info_ativos_hoje

            def gerar_df_objetivo(ativos):
                for ativo in ativos:
                    pl_atual = sum([info_ativos[ativo][fundo]['financeiro']
                                    for fundo in fundos if fundo in info_ativos[ativo]])/1000000
                    qtd_atual = sum([info_ativos[ativo][fundo]['qtd']
                                    for fundo in fundos if fundo in info_ativos[ativo]])
                    
                    dados.append({'Grupo': info_ativos[ativo]['grupo'],
                                  'Emissor': info_ativos[ativo]['emissor'],
                                  'Ativo': ativo,
                                  'atual': pl_atual,
                                  'qtd_atual': qtd_atual,
                                  'objetivo': None,
                                  'Spread': info_ativos[ativo]['spread'],
                                  'Duration': info_ativos[ativo]['duration'],
                                  'Quantidade': None,
                                  'Índice': info_ativos[ativo]['indice'],
                                  'Rating':info_ativos[ativo]['rating'],
                                  'PU': None,
                                  'Tipo': None,
                                  'Taxa': None
                                  })
                return pd.DataFrame(dados)

            if ativos and tipo_operacao != 'Ajuste Proporcional':
                df = gerar_df_objetivo(ativos)
                col1, col2 = st.columns([4, 1.2])
                with col1:
                    st.subheader('Financeiro Total por Ativo')
                    gb = GridOptionsBuilder.from_dataframe(df)
                    gb.configure_grid_options(
                        enableRangeSelection=True, tooltipShowDelay=0)
                    gb.configure_grid_options(enableCellTextSelection=True)
                    gb.configure_selection('multiple', use_checkbox=True)

                    gb = gb.build()
                    gb['columnDefs'] = [
                        {'field': 'Grupo', 'suppressMenu': True},  
                        {'field': 'Emissor', 'suppressMenu': True},
                        {'field': 'Ativo', 'suppressMenu': True,'headerCheckboxSelection': True, "checkboxSelection": True },
                        {
                        'field': 'atual',  
                        'headerName': 'Atual R$ (Milhões)',  
                        'suppressMenu': True,
                        'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2})",
                        "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                        }
                    ]

                    if tipo_operacao == 'Externa por Quantidade':
                        gb['columnDefs'].append({'field': 'qtd_atual',
                                                'headerName': 'Quantidade Atual',
                                                 'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 0})", 
                                                 'suppressMenu': True,
                                                 "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]})

                    if (tipo_operacao == 'Externa por Financeiro'):
                        gb['columnDefs'].append({'field': 'objetivo',
                                                'headerName': 'Variação R$ (Milhões)',
                                                 'editable': True if tipo_operacao != 'Ajuste' else False,
                                                 'cellStyle': {'background-color': 'rgb(236, 240, 241)' if tipo_operacao != 'Ajuste' else 'rgb(255, 255, 255)'},
                                                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2})", 'suppressMenu': True,
                                                 "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]})

                    if tipo_operacao == 'Externa por Quantidade':
                        gb['columnDefs'] = gb['columnDefs'] + [
                            {'field': 'Tipo', 'headerName': 'C/V', 'editable': True,
                             'cellStyle': {'background-color': 'rgb(236, 240, 241)'},
                             'cellEditor': 'agRichSelectCellEditor',
                             'cellEditorParams': {'values': ['Compra', 'Venda']},
                             'cellEditorPopup': True},
                            {
                                'field': 'Quantidade',
                                'editable': True,
                                'cellStyle': {'background-color': 'rgb(236, 240, 241)'},
                                'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 0})", 'suppressMenu': True,
                                "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                            {
                                'field': 'PU',
                                'editable': True,
                                'cellStyle': {'background-color': 'rgb(236, 240, 241)'}, 'minWidth': 160,
                                'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6})", 'suppressMenu': True,
                                "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                            {
                                'field': 'Taxa',
                                'editable': True,
                                'cellStyle': {'background-color': 'rgb(236, 240, 241)'}, 'minWidth': 100,
                                'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 4}) + '%'", 'suppressMenu': True,
                                "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]}]
                    else:
                        gb['columnDefs'] = gb['columnDefs'] + [{'field': 'Spread',  'suppressMenu': True,
                                                                'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2})",
                                                                "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                                                               {'field': 'Duration',  'suppressMenu': True,
                                                                'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2})",
                                                                "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]}]
                    if tipo_operacao != "Ajuste Proporcional":
                        df_objetivo = AgGrid(
                            df,
                            gridOptions=gb,
                            fit_columns_on_grid_load=False,
                            update_mode='MODEL_CHANGED',
                            height=min(45 + 45 * len(df.index), 400) if tipo_operacao != 'Externa por Quantidade' else min(
                                200 + 45 * len(df.index), 400),
                            custom_css=custom_css,
                            allow_unsafe_jscode=True,
                            enable_enterprise_modules=True)
        except:
            st.caption('Houve um erro')
            erro = True

        if ativos and not tipo_operacao == 'Ajuste Proporcional':
            try:
                erro = False
                ativos = [i['Ativo'] for i in df_objetivo['selected_rows']] if not df_objetivo['selected_rows'] == [] else []
                df_objetivo = df_objetivo['data']
                df_objetivo['Quantidade'] = pd.to_numeric(df_objetivo['Quantidade'], errors='coerce')
                df_objetivo['Taxa'] = df_objetivo['Taxa'].apply(lambda x: str(x).replace(',', '.'))
                df_objetivo['PU'] = df_objetivo['PU'].apply(lambda x: str(x).replace('.', '').replace(
                    ',', '.') if all([char in str(x) for char in ['.', ',']]) else str(x).replace(',', '.'))
                df_objetivo['Taxa'] = pd.to_numeric(df_objetivo['Taxa'], errors='coerce')
                df_objetivo['PU'] = pd.to_numeric(df_objetivo['PU'], errors='coerce')

                if tipo_operacao == 'Externa por Quantidade':
                    df_objetivo['objetivo'] = df_objetivo.apply(lambda x: x['Quantidade'] * info_ativos[x['Ativo']]['preco'] /
                                                                1000000 if x['Tipo'] == 'Compra' else -x['Quantidade'] * info_ativos[x['Ativo']]['preco'] / 1000000, axis=1)

                with col2:
                    if risco:
                        st.subheader('Alocação por Risco')
                        df_risco = pd.DataFrame([
                            {'Risco': 'G1', 'Alocação': '0,25'},
                            {'Risco': 'G2', 'Alocação': '0,50'},
                            {'Risco': 'G3', 'Alocação': '1,00'},
                            {'Risco': 'G4', 'Alocação': '0,00'},
                            {'Risco': 'G5', 'Alocação': '0,00'},
                        ])
                        gb = GridOptionsBuilder.from_dataframe(df_risco)
                        gb.configure_grid_options(
                            enableRangeSelection=True, tooltipShowDelay=0)
                        gb.configure_grid_options(enableCellTextSelection=True)
                        gb.configure_default_column(sortable=False)

                        gb = gb.build()
                        if tipo_risco == '% do PL':
                            formater = "value.toLocaleString('pt-BR',{minimumFractionDigits: 2}) + '%'"
                        else:
                            formater = "value.toLocaleString('pt-BR',{minimumFractionDigits: 2}) + 'x'"
                        gb['columnDefs'] = [
                            {'field': 'Risco', 'suppressMenu': True},
                            {'field': 'Alocação',  'editable': True, 'suppressMenu': True,
                             'cellStyle': {'background-color': 'rgb(236, 240, 241)'},
                             'valueFormatter':  formater,
                             "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]}]
                        df_risco = AgGrid(
                            df_risco,
                            gridOptions=gb,
                            fit_columns_on_grid_load=True,
                            update_mode='VALUE_CHANGED',
                            height=180,
                            custom_css=custom_css,
                            allow_unsafe_jscode=True,
                            enable_enterprise_modules=True)
                        df_risco = df_risco['data']

                        def num(x):
                            try:
                                return float(x.replace(",", '.'))
                            except:
                                return 0
                        df_risco['Alocação'] = df_risco['Alocação'].apply(lambda x: num(x))
                        matriz_risco = {}
                        for ind, row in df_risco.iterrows():
                            matriz_risco[row['Risco']] = row['Alocação']

                calc = None
                verificar_externa_quantidade = True
                if tipo_operacao == 'Externa por Quantidade':
                    for ativo in ativos:
                        pu = df_objetivo[df_objetivo['Ativo'] == ativo]['PU'].tolist()[0]
                        taxa = df_objetivo[df_objetivo['Ativo'] == ativo]['Taxa'].tolist()[0]
                        side_externa = df_objetivo[df_objetivo['Ativo'] == ativo]['Tipo'].tolist()[0]
                        if (not pu > 0) or (not taxa > 0) or (not side_externa in ['Compra', 'Venda']):
                            verificar_externa_quantidade = False

                if ativos and verificar_externa_quantidade:
                    with st.form('d'):

                        dados = patrimonio_fundos(db)
                        df = pd.DataFrame(dados, columns=['Fundo', 'pl_fundo'])
                        if fundos:
                            df = df[df['Fundo'].isin(fundos)]
                        df = df.sort_values(['pl_fundo'], ascending=[False])
                        df['Classe'] = df.apply(lambda x: info_fundos[x['Fundo']]['classe'], axis=1)
                        df['Risco'] = df.apply(lambda x: info_fundos[x['Fundo']]['risco'], axis=1)
                        df['%Alocado'] = df.apply(lambda x: round(info_fundos[x['Fundo']]['pl_credito'] / float(x['pl_fundo'])*100 if float(x['pl_fundo']) > 0 else 0, 2), axis=1)
                        # df = df[df['%Alocado'] > 0]
                        df = df[df['pl_fundo'] > 1]
                        fundos = df[df['%Alocado'] > 0]['Fundo'].tolist()

                        for ativo in ativos:
                            df[ativo] = None
                            df['%pl'+ativo] = df.apply(lambda x: (info_ativos[ativo][x['Fundo']]['financeiro'] / float(x['pl_fundo']))*100 if x['Fundo'] in info_ativos[ativo] else None, axis=1)

                        df = df.sort_values(['Risco', 'Classe'], ascending=[True, True])
                        gb = GridOptionsBuilder.from_dataframe(df)
                        gb.configure_grid_options(enableRangeSelection=True, tooltipShowDelay=0)
                        gb.configure_grid_options(enableCellTextSelection=True)
                        gb.configure_selection('multiple', use_checkbox=True)

                        gb = gb.build()

                        gb['columnDefs'] = [
                            {
                            'field': 'Classe', 
                            'pinned': 'left',
                            'tooltipField': "Classe",
                            'minWidth': 230
                            },
                            {'field': 'Risco', 'pinned': 'left','minWidth': 80},
                            {
                            'field': 'Fundo', 'pinned': 'left', 
                            'tooltipField': "Fundo", 
                            'minWidth': 250,
                            'headerCheckboxSelection': True, 
                            "checkboxSelection": True
                            },
                            {
                            'field': 'pl_fundo',  
                            'pinned': 'left',
                            'headerName': 'PL Alocável R$', 
                            'maxWidth': 155,
                            'valueFormatter': "data.pl_fundo.toLocaleString('pt-BR',{minimumFractionDigits: 0});",
                            "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                            },
                            {
                            'field': '%Alocado', 
                            'headerName': '% Alocado',  
                            'pinned': 'left', 
                            'minWidth': 120,
                            'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2}) + '%'",
                            "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                            }
                        ]

                        emissores = {}
                        for i in lista_ativos:
                            if i[0].strip() in ativos and i[1].strip().replace('.', '') not in emissores:
                                emissores[i[1].strip().replace('.', '')] = []
                            if i[0].strip() in ativos:
                                emissores[i[1].strip().replace('.', '')].append({'field': i[0].strip(), 'headerName': i[0].strip()+' %PL Objetivo',  'editable': True,
                                                                                'cellStyle': {'background-color': 'rgb(236, 240, 241)'},
                                                                                 'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2}) + '%'",
                                                                                 "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]})
                                if ver_pl_atual:
                                    emissores[i[1].strip().replace('.', '')].append({'field': '%pl'+i[0].strip(), 'headerName': i[0].strip() + ' %PL Atual',
                                                                                    'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2}) + '%'",
                                                                                     "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]})

                        defs = []
                        for emissor in emissores:
                            df['%emissor'+emissor] = df.apply(lambda x: round((info_emissores[emissor][x['Fundo']] / float(
                                x['pl_fundo']))*100, 2) if x['Fundo'] in info_emissores[emissor] else None, axis=1)
                            df['%grupo'+emissor] = df.apply(lambda x: round((info_grupos[grupos[emissor]][x['Fundo']] / float(
                                x['pl_fundo']))*100, 2) if x['Fundo'] in info_grupos[grupos[emissor]] else None, axis=1)

                            if ver_pl_atual:
                                emissores[emissor].append({
                                    'field': '%emissor'+emissor, 'headerName': '%PL Emissor',
                                    'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2}) + '%'",
                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                                })
                                emissores[emissor].append({
                                    'field': '%grupo'+emissor, 'headerName': '%PL Grupo',
                                    'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2}) + '%'",
                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                                })

                            defs.append({
                                'headerName': emissor,
                                'children': emissores[emissor]})

                        gb['columnDefs'] = gb['columnDefs'] + defs
                        ordem = ['CONSERVADOR',  'MODERADO', 'RIO GRANDE I', 'RIO GRANDE II', 'RIO GRANDE ABSOLUTO', 'RF PLUS PREV', 'WM PREV', 'ABSOLUTO FIFE', 'ABSOLUTO II FIE',
                                 'ABSOLUTO II FIFE', 'ABSOLUTO PLUS FIE', 'ABSOLUTO PLUS FIFE', 'ABSOLUTO TR FIE', 'ABSOLUTO TR FIFE', 'BTG ABSOLUTO II', 'BRADESCO ABSOLUTO II',
                                 'ITAU PREV', 'ITAU PREV QUALIFICADO FIFE', 'ITAU PREV TR', 'SEG DURATION', 'GOLD FIRF', 'RF PLUS', 'CREDIT', 'CP LIQUIDEZ', 'CP INSTITUCIONAL', 'Credito PG FIM',
                                 'CREDIT PLUS', 'GERDAU BD', 'GERDAU CP 3', 'WM ASSET', 'MIRANTE CP', 'ÁGUIA', 'SYNGENTA BASEL', 'MOLICO CP', 'VITRA CREDIT PLUS', 'RONDÔNIA', 'FAELBA', 'AILOS', 'TI LD',
                                 'HEDGE', 'SEG HEDGE', 'IV INFRAESTRUTURA', 'ICATU SEG INFRA', 'TFO INFRAESTRUTURA', 'IV TOTAL RETURN', 'TR Institucional', 'TR PG', 'ENERPREV', 'COPEL', 'LARANJEIRAS',
                                 'EMBRAER VI FIM CP', 'ENERGISA PREV', 'CEARÁ']
                        df['ordem'] = pd.Categorical(
                            df['Fundo'],
                            categories=ordem,
                            ordered=True
                        )
                        df = df.sort_values(['ordem'], ascending=[True])
                        st.subheader('Simular Composição em % do PL')
                        df_alteracao = AgGrid(
                            df,
                            gridOptions=gb,
                            fit_columns_on_grid_load=False,
                            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                            header_checkbox_selection_filtered_only=True,
                            update_mode='MODEL_CHANGED',
                            height=min(50 + 45 * len(df.index), 400),
                            custom_css=custom_css,
                            allow_unsafe_jscode=True,
                            enable_enterprise_modules=True)

                        df_alteracao = pd.DataFrame(df_alteracao['selected_rows'])
                        if len(df_alteracao.index) > 0:
                            fundos = df_alteracao['Fundo'].tolist()
                        calc = st.form_submit_button('Calcular')
            except:
                if not erro:
                    st.caption('Houve um erro')
                    erro = True
                calc = None

            try:
                op_incorreta = False
                if tipo_operacao == 'Externa por Financeiro' or (tipo_operacao == 'Externa por Quantidade' and verificar_externa_quantidade):
                    for ativo in ativos:
                        try:
                            operacao = float(
                                df_objetivo[df_objetivo['Ativo'] == ativo]['objetivo'].tolist()[0])*1000000
                        except:
                            operacao = 0

                        if operacao < 0:
                            if tipo_risco and not permite_ajuste:
                                saldo_ativo = sum([info_ativos[ativo][fundo]['financeiro']
                                                   for fundo in fundos if fundo in info_ativos[ativo] and matriz_risco[info_fundos[fundo]['risco']] > 0])
                            else:
                                saldo_ativo = sum([info_ativos[ativo][fundo]['financeiro']
                                                   for fundo in fundos if fundo in info_ativos[ativo]])
                            if saldo_ativo < -operacao:
                                msg = f'O valor total de venda para o ativo {ativo} é superior à posição atual dos fundos selecionados.'
                                op_incorreta = True
                                break
            except:
                if not erro:
                    st.caption('Houve um erro')
                calc = None
        if tipo_operacao == "Ajuste Proporcional":
            try:
                if len(fundos)>2:
                    st.caption('Escolha apenas 2 fundos para alocação')
                    alocacao_incorreta = True
                    calc = None
                else:
                    calc = None
                    op_incorreta = False
                    dados_fundos = []
                    pl_fundos = patrimonio_fundos(db)
                    pl_fundos = {i[0]: i[1] for i in pl_fundos}
                    externa_com_interna = False

                    fundos = [
                        fundo for fundo in fundos if fundo in pl_fundos and pl_fundos[fundo] > 1]

                    dados_fundos.append({**{'Informações': 'Risco'}, **
                                        {fundo: info_fundos[fundo]['risco'] for fundo in fundos if fundo in info_fundos}})
                    dados_fundos.append({**{'Informações': 'Classe'}, **
                                        {fundo: info_fundos[fundo]['classe'] for fundo in fundos if fundo in info_fundos}})
                    dados_fundos.append({**{'Informações': 'PL Alocável R$'}, **
                                        {fundo: pl_fundos[fundo] for fundo in fundos if fundo in pl_fundos}})
                    dados_fundos.append({**{'Informações': '%PL Alocado'}, **
                                        {fundo: round(info_fundos[fundo]['pl_credito'] / float(
                                            pl_fundos[fundo])*100 if float(pl_fundos[fundo]) > 0 else 0, 2) for fundo in fundos if fundo in pl_fundos}})
                    dados_fundos.append({**{'Informações': '%PL Objetivo'}, **
                                        {fundo: '' for fundo in fundos if fundo in pl_fundos}})
                    import locale
                    locale.setlocale(locale.LC_ALL, 'pt_BR')

                    df_fundos = pd.DataFrame(dados_fundos)
                    for fundo in fundos:
                        pl = "{:n}".format(round(df_fundos[df_fundos['Informações'] == 'PL Alocável R$'][fundo].tolist()[0]))
                        df_fundos.at[2, fundo] = pl
                        perc_pl_alocado = "{:n}%".format(round(df_fundos[df_fundos['Informações'] == '%PL Alocado'][fundo].tolist()[0], 1))
                        df_fundos.at[3, fundo] = perc_pl_alocado

                    gb = GridOptionsBuilder.from_dataframe(df_fundos)
                    gb.configure_grid_options(enableRangeSelection=True, tooltipShowDelay=0)
                    gb.configure_grid_options(enableCellTextSelection=True)
                    gb.configure_selection('multiple', use_checkbox=True)

                    gb = gb.build()

                    gb['columnDefs'] = [
                        {'field': 'Informações', 'pinned': 'left', 'minWidth': 100, }]

                    cellStyle = JsCode("""
                            function(params) {
                                if (params.value == '') {
                                    return {
                                        'backgroundColor': 'rgb(236, 240, 241)',
                                    }
                                }
                            };
                        """)

                    formatCell = JsCode("""
                            function(params) {
                                if (params.data.Informações == '%PL Objetivo') {
                                    return  params.value.toLocaleString("pt-BR") + "%"
                                }
                            };
                        """)

                    enableEdit = JsCode("""
                            function(params) {
                                if (params.data.Informações == '%PL Objetivo') {
                                    return  true
                                } else {return false}
                            };
                        """)

                    for fundo in fundos:
                        gb['columnDefs'].append(
                            {'field': fundo,
                            'editable': enableEdit,
                            'cellStyle': cellStyle,
                            'valueFormatter': formatCell})

                    form = st.form('ajuste_proporcional')
                    with form:
                        st.subheader('Informações dos Fundos')
                        df_objetivo_fundos = AgGrid(
                            df_fundos,
                            gridOptions=gb,
                            fit_columns_on_grid_load=False,
                            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                            header_checkbox_selection_filtered_only=True,
                            update_mode='MODEL_CHANGED',
                            height=200,
                            custom_css=custom_css,
                            allow_unsafe_jscode=True,
                            enable_enterprise_modules=True)
                        df_objetivo_fundos = df_objetivo_fundos['data']

                        loop_ativos = set()
                        if not ativos:
                            for fundo in fundos:
                                for ativo in info_ativos:
                                    if fundo in info_ativos[ativo]:
                                        loop_ativos.add(ativo)
                        else:
                            loop_ativos = ativos
                        df_objetivo = gerar_df_objetivo(loop_ativos)

                        dados = []
                        for ativo in loop_ativos:
                            colunas_fundos = {}
                            for fundo in fundos:

                                colunas_fundos['obj_'+fundo] = ''
                                colunas_fundos['atual_'+fundo] = (info_ativos[ativo][fundo]['financeiro'] / float(pl_fundos[fundo]))*100 if fundo in info_ativos[ativo] else 0
                            dados.append(
                                {**{'Ativo': ativo, 
                                    'Tipo': info_ativos[ativo]['tipo'], 
                                    'Emissor': info_ativos[ativo]['emissor'],
                                    'Índice': info_ativos[ativo]['indice'],
                                    'Rating': info_ativos[ativo]['rating'],
                                    }, **colunas_fundos})
                        df = pd.DataFrame(dados)
                        ativos = df['Ativo'].tolist()
                        df = df.sort_values(['atual_'+fundos[0]], ascending=[False])
                        gb = GridOptionsBuilder.from_dataframe(df)
                        gb.configure_grid_options(
                            enableRangeSelection=True, tooltipShowDelay=0)
                        gb.configure_grid_options(enableCellTextSelection=True)
                        gb.configure_selection('multiple', use_checkbox=True)

                        gb = gb.build()

                        cellStyle = JsCode("""
                            function(params) {
                                if (params.value == 0) {
                                    return {
                                        'backgroundColor': 'rgb(247, 125, 129)',
                                    }
                                }
                            };
                        """)

                        gb['columnDefs'] = [
                            {'field': 'Ativo', 'pinned': 'left', 'minWidth': 100, "checkboxSelection": True},
                            {'field': 'Tipo', 'pinned': 'left', 'minWidth': 100, },
                            {'field': 'Emissor', 'pinned': 'left', 'minWidth': 100, },
                            {'field': 'Índice', 'pinned': 'left', 'minWidth': 100, },
                            {'field': 'Rating', 'pinned': 'left', 'minWidth': 100, }]
                        for fundo in fundos:
                            gb['columnDefs'].append({
                                'field': 'obj_'+fundo, 'headerName': fundo + " %PL Obj",
                                'editable': True,
                                'cellStyle': {'background-color': 'rgb(236, 240, 241)'},
                                'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2,maximumFractionDigits: 2}) + '%'",
                                "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                            })
                            gb['columnDefs'].append({
                                'field': 'atual_'+fundo, 'headerName': fundo + " %PL Atual",
                                'cellStyle': cellStyle,
                                'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%'",
                                "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                            })

                        st.subheader('Simular Composição em % do PL')
                        df_alteracao = AgGrid(
                            df,
                            gridOptions=gb,
                            fit_columns_on_grid_load=False,
                            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                            header_checkbox_selection_filtered_only=True,
                            update_mode='MODEL_CHANGED',
                            height=min(50 + 45 * len(df.index), 400),
                            custom_css=custom_css,
                            allow_unsafe_jscode=True,
                            enable_enterprise_modules=True)
                        calc = st.form_submit_button('Calcular')
                        ativos = [i['Ativo'] for i in df_alteracao['selected_rows']] if not df_alteracao['selected_rows'] is None else []
                        df_alteracao = df_alteracao['data']

                        dados = []
                        for fundo in fundos:
                            dados.append({
                                'Fundo': fundo,
                                'pl_fundo': pl_fundos[fundo],
                                'Classe': info_fundos[fundo]['classe'],
                                'Risco': info_fundos[fundo]['risco'],
                                '%Alocado': round(info_fundos[fundo]['pl_credito'] / float(pl_fundos[fundo])*100 if float(pl_fundos[fundo]) > 0 else 0, 2)
                            })

                        for linha_fundo in dados:
                            for ativo in ativos:
                                fundo = linha_fundo['Fundo']
                                linha_fundo[ativo] = df_alteracao[(df_alteracao['Ativo'] == ativo)]['obj_'+fundo].tolist()[0]
                                linha_fundo['%pl'+ativo] = df_alteracao[(df_alteracao['Ativo'] == ativo)]['atual_'+fundo].tolist()[0]
                                emissor = info_ativos[ativo]['emissor']
                                linha_fundo['%emissor'+emissor] = round((info_emissores[emissor][fundo] / float(pl_fundos[fundo]))*100, 2) if fundo in info_emissores[emissor] else None
                                grupo = info_ativos[ativo]['grupo']
                                linha_fundo['%grupo'+grupo] = round((info_grupos[grupos[emissor]][fundo] / float(pl_fundos[fundo]))*100, 2) if fundo in info_grupos[grupos[emissor]] else None

                        df_alteracao = pd.DataFrame(dados)
                        somatorio_ativos_selecionados = {}
                        for fundo in fundos:
                            somatorio_ativos_selecionados[fundo] = sum([float(df_alteracao[df_alteracao['Fundo'] == fundo]['%pl'+ativo].tolist()[0]) for ativo in ativos])
                            if somatorio_ativos_selecionados[fundo] == 0:
                                alocacao_incorreta = True
            except:
                calc = form.form_submit_button(label='Calcular')
                st.caption('Houve um erro')

        if ((calc
            or (st.session_state['calc'] == True and sorted(fundos+ativos) == sorted(st.session_state['dados'])))
                and len(df_alteracao.index) > 1) and ativos and (op_incorreta == False) and not alocacao_incorreta:
            try:
                with st.spinner('Aguarde...'):
                    if not 'dados_simulacao' in st.session_state:
                        st.session_state['dados_simulacao'] = {}
                        st.session_state['dados_simulacao']['usar'] = False
                        
                    if st.session_state['dados_simulacao']['usar'] == False:
                        def simulacao(x, ativo, pl_ativo, pl_fundos, tipo_operacao, risco, multiplicador=None, soma_multiplicador=None):

                            if ((tipo_operacao == 'Ajuste' and risco == False) or
                                    ((tipo_operacao == 'Externa por Financeiro' or tipo_operacao == 'Externa por Quantidade') and risco == False and permite_ajuste)):
                                perc_ativo = str(x[ativo]).replace(',', '.')
                                if x[ativo] and x[ativo] != 'None':
                                    return float(perc_ativo) if not math.isnan(float(perc_ativo)) else 0
                                else:
                                    return round(((float(x['pl_fundo']) / pl_fundos)*pl_ativo) / float(x['pl_fundo'])*100, 6)

                            if ((tipo_operacao == 'Ajuste' and risco == True) or
                                    ((tipo_operacao == 'Externa por Financeiro' or tipo_operacao == 'Externa por Quantidade') and risco == True and permite_ajuste)):
                                perc_ativo = str(x[ativo]).replace(',', '.')
                                if x[ativo] and x[ativo] != 'None':
                                    return float(perc_ativo) if not math.isnan(float(perc_ativo)) else 0
                                else:
                                    return round((pl_ativo * (multiplicador[x['Fundo']] / soma_multiplicador))/x['pl_fundo']*100, 6)

                            if ((tipo_operacao == 'Externa por Financeiro' or tipo_operacao == 'Externa por Quantidade') and risco == False and not permite_ajuste):
                                perc_ativo = str(x[ativo]).replace(',', '.')
                                if x[ativo] and x[ativo] != 'None':
                                    return float(perc_ativo) if not math.isnan(float(perc_ativo)) else 0
                                else:
                                    try:
                                        perc_ativo = float(x['%pl'+ativo])
                                    except:
                                        perc_ativo = 0
                                    if math.isnan(perc_ativo):
                                        perc_ativo = 0

                                    return round(perc_ativo + ((float(x['pl_fundo']) / pl_fundos)*round(pl_ativo)) / float(x['pl_fundo'])*100, 6)

                            if ((tipo_operacao == 'Externa por Financeiro' or tipo_operacao == 'Externa por Quantidade') and risco == True and not permite_ajuste):
                                perc_ativo = str(x[ativo]).replace(',', '.')
                                if x[ativo] and x[ativo] != 'None':
                                    return float(perc_ativo) if not math.isnan(float(perc_ativo)) else 0
                                else:
                                    try:
                                        perc_ativo = float(x['%pl'+ativo])
                                    except:
                                        perc_ativo = 0
                                    if math.isnan(perc_ativo):
                                        perc_ativo = 0
                                    return round(perc_ativo + (pl_ativo * (multiplicador[x['Fundo']] / soma_multiplicador))/x['pl_fundo']*100, 6)

                            if tipo_operacao == 'Externa por % do PL' and risco == False:
                                perc_ativo = str(x[ativo]).replace(',', '.')
                                if x[ativo] and x[ativo] != 'None':
                                    return float(perc_ativo) if not math.isnan(float(perc_ativo)) else 0
                                else:
                                    return 0

                            if tipo_operacao == 'Externa por % do PL' and risco == True:
                                perc_ativo = str(x[ativo]).replace(',', '.')
                                if x[ativo] and x[ativo] != 'None':
                                    return float(perc_ativo) if not math.isnan(float(perc_ativo)) else 0
                                else:
                                    return matriz_risco[x['Risco']]

                            if tipo_operacao == 'Ajuste Proporcional':
                                perc_ativo = str(x[ativo]).replace(',', '.')
                                if x[ativo] and x[ativo] != 'None' and x[ativo] != 'nan':
                                    return float(perc_ativo) if not math.isnan(float(perc_ativo)) else 0
                                else:
                                    if 'alocado_obj' in x:
                                        perc_ativo = float(x['simulacao'+ativo])
                                    else:
                                        perc_ativo = float(x['%pl'+ativo])
                                    if x['Fundo'] in fundos_sem_objetivo:
                                        if not ativo in saldo_ativos:
                                            return perc_ativo
                                        mov_fin_ativo = saldo_ativos[ativo] * (fundos_sem_objetivo[x['Fundo']] / pl_fundos_sem_objetivo)
                                        mov_perc_ativo = mov_fin_ativo / x['pl_fundo']
                                        return perc_ativo + mov_perc_ativo*100
                                    else:
                                        if somatorio_ativos_selecionados[x['Fundo']] > 0:
                                            mov_fin_ativo = saldo_fundos[x['Fundo']] * (perc_ativo / somatorio_ativos_selecionados[x['Fundo']])
                                            mov_perc_ativo = mov_fin_ativo / x['pl_fundo']*100
                                            return perc_ativo + mov_perc_ativo
                                        else:
                                            return 0

                        if tipo_operacao == 'Ajuste Proporcional':
                            objetivos_travados = {}
                            for ativo in ativos:
                                for fundo in fundos:
                                    perc_travado = df_alteracao[df_alteracao['Fundo']== fundo][ativo].tolist()[0]
                                    try:
                                        perc_travado = float(perc_travado.replace(',', '.'))
                                    except:
                                        perc_travado = 0
                                    if perc_travado > 0:
                                        if not ativo in objetivos_travados:
                                            objetivos_travados[ativo] ={}
                                        objetivos_travados[ativo][fundo] = perc_travado

                            def infos_ajuste_proporcional(ativos):
                                saldo_fundos, saldo_ativos = {}, {}
                                fundos_sem_objetivo = {}
                                somatorio_ativos_selecionados = {}
                                emissores = set([info_ativos[ativo]['emissor'] for ativo in ativos])

                                pl_fundos = 0
                                for fundo in fundos:
                                    pl = float(df_objetivo_fundos[df_objetivo_fundos['Informações'] == 'PL Alocável R$'][fundo].tolist()[0].replace('.', ''))
                                    pl_fundos += pl
                                    def perc_pl(ativo):
                                        return float(df_alteracao[df_alteracao['Fundo'] == fundo]['%pl'+ativo].tolist()[0])
                                    def perc_objetivo(ativo):
                                        try:
                                            return float(df_alteracao[df_alteracao['Fundo'] == fundo][ativo].tolist()[0].replace(',', '.'))
                                        except:
                                            return 0

                                    if 'alocado_obj' in df_alteracao[df_alteracao['Fundo'] == fundo].columns:
                                        pl_alocado = df_alteracao[df_alteracao['Fundo'] == fundo]['alocado_obj'].tolist()[0]/100
                                        somatorio_ativos_selecionados[fundo] = sum([float(df_alteracao[df_alteracao['Fundo'] == fundo]['simulacao'+ativo].tolist()[0]) for ativo in ativos])
                                    else:
                                        somatorio_ativos_selecionados[fundo] = sum([perc_pl(ativo) if perc_objetivo(ativo) == 0 else 0 for ativo in ativos])
                                        pl_alocado = float(df_objetivo_fundos[df_objetivo_fundos['Informações'] == '%PL Alocado'][fundo].tolist(
                                        )[0].replace(',', '.').replace('%', ''))/100
                                    try:
                                        objetivo = float(df_objetivo_fundos[df_objetivo_fundos['Informações'] == '%PL Objetivo'][fundo].tolist(
                                        )[0].replace(',', '.').replace('%', ''))/100
                                    except:
                                        objetivo = 0
                                    somatorio_ativos_alocados = sum([perc_objetivo(ativo) -perc_pl(ativo)  for ativo in ativos if perc_objetivo(ativo) > 0])
                                    saldo_fundos[fundo] = (objetivo - pl_alocado)*pl
                                    saldo_fundos[fundo] -= somatorio_ativos_alocados/100 * pl
                                    if objetivo > pl_alocado:
                                        for ativo in ativos:
                                            if 'alocado_obj' in df_alteracao[df_alteracao['Fundo'] == fundo].columns:
                                                perc_ativo = df_alteracao[df_alteracao['Fundo'] == fundo]['simulacao'+ativo].tolist()[0]
                                            else:
                                                perc_ativo = df_alteracao[df_alteracao['Fundo'] == fundo]['%pl'+ativo].tolist()[0]
                                            if not ativo in saldo_ativos:
                                                saldo_ativos[ativo] = 0
                                            obj_ativo_str = df_alteracao[df_alteracao['Fundo'] == fundo][ativo].tolist()[0]
                                            obj_ativo = str(obj_ativo_str).replace(',', '.')

                                            if (obj_ativo_str and obj_ativo_str != 'None') and not math.isnan(float(obj_ativo)):
                                                obj_ativo = float(obj_ativo) if not math.isnan(float(obj_ativo)) else 0
                                                saldo_ativos[ativo] -= (obj_ativo - perc_ativo)/100 * pl
                                            else:
                                                if somatorio_ativos_selecionados[fundo] > 0:
                                                    saldo_ativos[ativo] -= saldo_fundos[fundo] * (perc_ativo /somatorio_ativos_selecionados[fundo])
                                    if objetivo < pl_alocado and objetivo > 0:
                                        for ativo in ativos:
                                            if 'alocado_obj' in df_alteracao[df_alteracao['Fundo'] == fundo].columns:
                                                perc_ativo = df_alteracao[df_alteracao['Fundo'] == fundo]['simulacao'+ativo].tolist()[0]
                                            else:
                                                perc_ativo = df_alteracao[df_alteracao['Fundo'] == fundo]['%pl'+ativo].tolist()[0]
                                            if not ativo in saldo_ativos:
                                                saldo_ativos[ativo] = 0
                                            obj_ativo_str = df_alteracao[df_alteracao['Fundo'] == fundo][ativo].tolist()[0]
                                            obj_ativo = str(obj_ativo_str).replace(',', '.')

                                            if obj_ativo_str and obj_ativo_str != 'None':
                                                obj_ativo = float(obj_ativo) if not math.isnan(
                                                    float(obj_ativo)) else 0
                                                saldo_ativos[ativo] -= (obj_ativo -
                                                                        perc_ativo)/100 * pl
                                            else:
                                                if somatorio_ativos_selecionados[fundo] > 0:
                                                    saldo_ativos[ativo] -= saldo_fundos[fundo] * (perc_ativo /somatorio_ativos_selecionados[fundo])

                                    if objetivo == 0:
                                        fundos_sem_objetivo[fundo] = pl                                     

                                saldo_movimentacoes = sum([saldo_fundos[fundo] for fundo in saldo_fundos])
                                pl_fundos_sem_objetivo = sum([fundos_sem_objetivo[fundo] for fundo in fundos_sem_objetivo])
                                for fundo in fundos_sem_objetivo:
                                    saldo_fundos[fundo] = (fundos_sem_objetivo[fundo] / pl_fundos_sem_objetivo) * -saldo_movimentacoes

                                return fundos_sem_objetivo, pl_fundos_sem_objetivo, saldo_fundos, saldo_ativos, somatorio_ativos_selecionados, emissores, df_alteracao

                            fundos_sem_objetivo, pl_fundos_sem_objetivo, saldo_fundos, saldo_ativos, somatorio_ativos_selecionados, emissores, df_alteracao = infos_ajuste_proporcional(ativos)

                        if tipo_operacao not in ('Externa por Quantidade', "Ajuste Proporcional"):
                            df_objetivo['objetivo'] = df_objetivo['objetivo'].apply(
                                lambda x: float(x.replace(',', ".")) if x and x != 'None' and x != '' else 0)
                            df_objetivo['objetivo'] = pd.to_numeric(df_objetivo['objetivo'], errors='coerce')

                        def calcular(df_alteracao, df_objetivo, ativo):
                            fundos = df_alteracao['Fundo'].tolist()
                            df_alteracao['pl_fundo'] = pd.to_numeric(df_alteracao['pl_fundo'], errors='coerce')
                            if tipo_operacao == 'Ajuste Proporcional':
                                df_alteracao[ativo] = df_alteracao[ativo].apply(lambda x: x.replace(',', '.').replace(
                                    ' ', '').replace('nan', '') if x and not isinstance(x, float) else str(x))
                            else:
                                df_alteracao[ativo] = df_alteracao[ativo].apply(lambda x: x.replace(',', '.').replace(
                                    ' ', '').replace('nan', '') if x and not isinstance(x, float) else None)
                            df_alteracao['pos'+ativo] = df_alteracao.apply(lambda x: (float(x[ativo].replace(
                                ',', '.'))/100) * x['pl_fundo'] if x[ativo] and x[ativo] != 'None' else 0, axis=1)

                            if (tipo_operacao == 'Externa por Financeiro' or tipo_operacao == 'Externa por Quantidade') and permite_ajuste:
                                var_ativo = float(
                                    df_objetivo[df_objetivo['Ativo'] == ativo]['objetivo'].sum())*1000000
                                pl_ativo = sum([info_ativos[ativo][fundo]['financeiro']
                                                for fundo in fundos if fundo in info_ativos[ativo]]) - df_alteracao['pos'+ativo].sum()
                                pl_ativo += var_ativo
                            elif (tipo_operacao == 'Externa por Financeiro' or tipo_operacao == 'Externa por Quantidade') and not permite_ajuste:
                                var_ativo = float(
                                    df_objetivo[df_objetivo['Ativo'] == ativo]['objetivo'].sum())*1000000
                                fundos_eletivos = df_alteracao[pd.to_numeric(
                                    df_alteracao[ativo], errors='coerce').notnull()]['Fundo'].tolist()
                                pl_ativo = df_alteracao['pos'+ativo].sum() - sum([info_ativos[ativo][fundo]['financeiro']
                                                                                for fundo in fundos if fundo in fundos_eletivos and fundo in info_ativos[ativo]])
                                pl_ativo = var_ativo - pl_ativo

                            else:
                                pl_ativo = sum([info_ativos[ativo][fundo]['financeiro']
                                                for fundo in fundos if fundo in info_ativos[ativo]]) - df_alteracao['pos'+ativo].sum()
                            pl_fundos = df_alteracao[pd.to_numeric(df_alteracao[ativo], errors='coerce').isnull()]['pl_fundo'].sum()
                            fundos_eletivos = df_alteracao[pd.to_numeric(df_alteracao[ativo], errors='coerce').isnull()]['Fundo'].tolist()

                            if risco:
                                multiplicador = {fundo[0]: fundo[1] for fundo in [(fundo, matriz_risco[df_alteracao[df_alteracao['Fundo'] == fundo]['Risco'].tolist(
                                )[0]] * (df_alteracao[df_alteracao['Fundo'] == fundo]['pl_fundo'].tolist()[0]/pl_fundos)) for fundo in fundos_eletivos]}
                                soma_multiplicador = sum(
                                    [multiplicador[fundo] for fundo in multiplicador])
                            else:
                                multiplicador, soma_multiplicador = 0, 0

                            df_alteracao['simulacao'+ativo] = df_alteracao.apply(lambda x: simulacao(
                                x, ativo, pl_ativo, pl_fundos, tipo_operacao, risco, multiplicador, soma_multiplicador), axis=1)
                            return df_alteracao

                        def loop_calcular(df_alteracao, ativos):
                            for ativo in ativos:
                                df_alteracao = calcular(df_alteracao, df_objetivo, ativo)
                                lista = [i for i in df_alteracao['simulacao'+ativo].tolist() if i < 0]
                                while lista:

                                    for fundo in fundos:
                                        perc_objetivo = df_alteracao[df_alteracao['Fundo']== fundo]['simulacao'+ativo].tolist()[0]
                                        perc_atual = df_alteracao[df_alteracao['Fundo'] == fundo]['%pl'+ativo].tolist()[0]
                                        if not perc_atual:
                                            perc_atual = 0

                                        idx = df_alteracao.index[df_alteracao['Fundo']== fundo][0]
                                        if tipo_operacao == 'Ajuste Proporcional':
                                            df_alteracao.loc[idx, ativo] = str(perc_objetivo)

                                        if perc_objetivo < 0:
                                            df_alteracao.loc[idx, ativo] = str(0)

                                    df_alteracao = calcular(df_alteracao, df_objetivo, ativo)
                                    lista = [i for i in df_alteracao['simulacao'+ativo].tolist() if i < 0]

                                if usar_banda:
                                    for fundo in fundos:
                                        perc_objetivo = df_alteracao[df_alteracao['Fundo'] == fundo]['simulacao'+ativo].tolist()[0]
                                        perc_atual = df_alteracao[df_alteracao['Fundo'] == fundo]['%pl'+ativo].tolist()[0]
                                        if not perc_atual:
                                            perc_atual = 0

                                        idx = df_alteracao.index[df_alteracao['Fundo']== fundo][0]
                                        if ((0 < perc_atual <= 1 and (perc_atual*0.9 < perc_objetivo < perc_atual*1.1)) or
                                                (perc_atual > 1 and (perc_atual*0.95 < perc_objetivo < perc_atual*1.05))):
                                            df_alteracao.loc[idx, ativo] = str(perc_atual)

                                    df_alteracao = calcular(df_alteracao, df_objetivo, ativo)
                        
                        loop_calcular(df_alteracao, ativos)

                        for ativo in ativos:
                            valores_negativos = [valor for valor in df_alteracao['simulacao'+ativo].tolist() if valor < 0]
                            if valores_negativos:
                                alocacao_incorreta = True

                        def quant(x, ativo, usar_banda):
                            try:
                                perc_pl = float(x['%pl'+ativo])
                            except:
                                perc_pl = 0

                            if x['%pl'+ativo] and (perc_pl > 0 or perc_pl < 0):
                                perc = x['%pl'+ativo]
                            else:
                                perc = 0

                            if usar_banda:
                                if 0 < perc <= 1 and (perc*0.9 < x['simulacao'+ativo] < perc*1.1):
                                    return 0
                                if perc > 1 and (perc*0.95 < x['simulacao'+ativo] < perc*1.05):
                                    return 0
                            if perc > 0 and x['simulacao'+ativo] == 0:
                                return -info_ativos[ativo][x['Fundo']]['qtd']
                            if perc == 0 and x['simulacao'+ativo] == 0:
                                return 0
                            else:
                                return mutil.truncar(((x['simulacao'+ativo] - perc)/100 * float(x['pl_fundo'])) / info_ativos[ativo]['preco'], 0)

                        def calcular_quant(df_alteracao):
                            for ativo in ativos:
                                df_alteracao[ativo] = df_alteracao[ativo].apply( lambda x: str(x))
                                df_alteracao[ativo] = df_alteracao[ativo].apply(lambda x: x.replace(',', '.') if isinstance(x, str) else 0)
                                df_alteracao[ativo] = pd.to_numeric(df_alteracao[ativo], errors='coerce')
                                df_alteracao['quantidade_'+ativo] = df_alteracao.apply(lambda x: quant(x, ativo, usar_banda), axis=1)
                                df_alteracao['financeiro_'+ativo] = df_alteracao.apply(lambda x: round(x['quantidade_'+ativo]*info_ativos[ativo]['preco'], 0), axis=1)
                            return df_alteracao
                        df_alteracao = calcular_quant(df_alteracao)

                        def corrigir_saldo_quantidade(fundos_sem_objetivo, ativos):
                            saldo_ativos = {}
                            pl_fundos_com_objetivo = {}
                            pl_fundos_sem_objetivo = {}
                            fundos_com_saldo = {}
                            for ativo in ativos:
                                saldo = sum(df_alteracao['financeiro_'+ativo])
                                if saldo != 0:
                                    saldo_ativos[ativo] = saldo
                                    for fundo in fundos:
                                        perc_fundo = df_alteracao[df_alteracao['Fundo']== fundo]['simulacao'+ativo].tolist()[0]
                                        if perc_fundo > 0:
                                            if (ativo in objetivos_travados and not fundo in objetivos_travados[ativo]) or not ativo in objetivos_travados:
                                                if not ativo in pl_fundos_com_objetivo and fundo not in fundos_sem_objetivo:
                                                    pl_fundos_com_objetivo[ativo] = 0
                                                if not ativo in pl_fundos_sem_objetivo and fundo in fundos_sem_objetivo:
                                                    pl_fundos_sem_objetivo[ativo] = 0
                                                if fundo in fundos_sem_objetivo:
                                                    pl_fundos_sem_objetivo[ativo] += df_alteracao[df_alteracao['Fundo']== fundo]['pl_fundo'].tolist()[0]
                                                else:
                                                    pl_fundos_com_objetivo[ativo] += df_alteracao[df_alteracao['Fundo']== fundo]['pl_fundo'].tolist()[0]
                                                if not ativo in fundos_com_saldo:
                                                    fundos_com_saldo[ativo] = set()
                                                fundos_com_saldo[ativo].add(fundo)

                            for ativo in saldo_ativos:
                                if ativo in fundos_com_saldo:
                                    for fundo in fundos_com_saldo[ativo]:
                                        perc_simulacao = df_alteracao[df_alteracao['Fundo']== fundo]['simulacao'+ativo].tolist()[0]
                                        perc_atual = df_alteracao[df_alteracao['Fundo']== fundo]['%pl'+ativo].tolist()[0] 
                                        pl = df_alteracao[df_alteracao['Fundo']
                                                        == fundo]['pl_fundo'].tolist()[0]
                                        if fundo in fundos_sem_objetivo:
                                            saldo_perc = (saldo_ativos[ativo] *
                                                        (pl / pl_fundos_sem_objetivo[ativo])) / pl * 100
                                        else:
                                            saldo_perc = (saldo_ativos[ativo] *
                                                        (pl / pl_fundos_com_objetivo[ativo])) / pl * 100
                                        perc_simulacao -= saldo_perc
                                        if perc_simulacao < 0 :
                                            perc_simulacao = 0
                                            saldo_ativos[ativo] -= perc_atual/100 * pl
                                        elif saldo_ativos[ativo] > 0 and perc_simulacao < perc_atual:
                                            perc_simulacao = perc_atual
                                        df_alteracao.loc[df_alteracao['Fundo']
                                                        == fundo, 'simulacao'+ativo] = perc_simulacao
                                # else:
                                #     perc_atual = df_alteracao[df_alteracao['Fundo']== fundo]['%pl'+ativo].tolist()[0] 
                                #     df_alteracao.loc[df_alteracao['Fundo']
                                #                         == fundo, 'simulacao'+ativo] = perc_atual
                                        
                            df_alteracao['alocado_obj'] = df_alteracao.apply(
                                lambda x: sum([x['simulacao'+ativo] - x['%pl'+ativo] for ativo in ativos]) + x['%Alocado'], axis=1)

                        def verificar_pl_alavancado():
                            resposta = False
                            df_alteracao['alocado_obj'] = df_alteracao.apply(
                                lambda x: sum([x['simulacao'+ativo] - x['%pl'+ativo] for ativo in ativos]) + x['%Alocado'], axis=1)

                            for fundo in fundos:
                                pl_objetivo = df_alteracao[df_alteracao['Fundo'] == fundo]['alocado_obj'].tolist()[
                                    0]
                                if pl_objetivo > 100:
                                    resposta = True
                            return resposta

                        if tipo_operacao == "Ajuste Proporcional":
                            corrigir_saldo_quantidade(fundos_sem_objetivo, ativos)
                            alocacao_incorreta = verificar_pl_alavancado()

                        df_alteracao = calcular_quant(df_alteracao)
                        if tipo_operacao == "Ajuste Proporcional":
                            df_alteracao['alocado_obj'] = df_alteracao.apply(
                                lambda x: sum([x['simulacao'+ativo] - x['%pl'+ativo] for ativo in ativos]) + x['%Alocado'], axis=1)

                            recalcular = False
                            for fundo in fundos:
                                obj_simulacao = df_alteracao[df_alteracao['Fundo']
                                                            == fundo]['alocado_obj'].tolist()[0]
                                try:
                                    objetivo = float(df_objetivo_fundos[df_objetivo_fundos['Informações'] == '%PL Objetivo'][fundo].tolist(
                                    )[0].replace(',', '.').replace('%', ''))
                                except:
                                    objetivo = 0
                                if objetivo > 0:
                                    dif = obj_simulacao - objetivo
                                    if abs(dif) > 1:
                                        recalcular = True

                            if recalcular and redistribuir == 'Forçar até o objetivo':
                                novos_ativos = set()
                                for ativo in ativos:
                                    for fundo in fundos:
                                        perc_ativo = df_alteracao[df_alteracao['Fundo']
                                                                == fundo]['simulacao'+ativo].tolist()[0]
                                        if perc_ativo > 0 and fundo in fundos_sem_objetivo:
                                            novos_ativos.add(ativo)
                                if novos_ativos:
                                    fundos_sem_objetivo, pl_fundos_sem_objetivo, saldo_fundos, saldo_ativos, somatorio_ativos_selecionados, emissores, df_alteracao = infos_ajuste_proporcional(
                                        novos_ativos)
                                    loop_calcular(df_alteracao, novos_ativos)
                                    df_alteracao = calcular_quant(df_alteracao)
                                    saldo = 10001
                                    i = 1
                                    while abs(saldo) > 10_000 and i <10:
                                        saldo = 0
                                        corrigir_saldo_quantidade(fundos_sem_objetivo, novos_ativos)
                                        df_alteracao = calcular_quant(df_alteracao)
                                        for ativo in ativos:
                                            saldo += abs(sum(df_alteracao['financeiro_'+ativo]))
                                        i+=1

                                    df_alteracao['alocado_obj'] = df_alteracao.apply(
                                        lambda x: sum([x['simulacao'+ativo] - x['%pl'+ativo] for ativo in ativos]) + x['%Alocado'], axis=1)
                    
                    if st.session_state['dados_simulacao']['usar'] and tipo_operacao == 'Ajuste Proporcional':
                        df_alteracao = st.session_state['dados_simulacao']['distribuição por ativos']
                        emissores = st.session_state['dados_simulacao']['emissores']
                    else:
                        st.session_state['dados_simulacao']['distribuição por ativos']=df_alteracao
                        st.session_state['dados_simulacao']['emissores'] = emissores
        
                    def novo_emissor(x, emissor):
                        fin_total = 0
                        for ativo in ativos:
                            if info_ativos[ativo]['emissor'] == emissor:
                                fin_total += x['financeiro_'+ativo]

                        if x['Fundo'] in info_emissores[emissor]:
                            return round(((info_emissores[emissor][x['Fundo']] + fin_total) / float(x['pl_fundo']))*100, 2)
                        else:
                            return round((fin_total / float(x['pl_fundo']))*100, 2)

                    def novo_grupo(x, emissor):
                        fin_total = 0
                        for ativo in ativos:
                            if info_ativos[ativo]['grupo'] == grupos[emissor]:
                                fin_total += x['financeiro_'+ativo]
                        if x['Fundo'] in info_grupos[grupos[emissor]]:
                            return round(((info_grupos[grupos[emissor]][x['Fundo']] + fin_total) / float(x['pl_fundo']))*100, 2)
                        else:
                            return round((fin_total / float(x['pl_fundo']))*100, 2)

                    for emissor in emissores:
                        df_alteracao['novo_emissor'+emissor] = df_alteracao.apply(
                            lambda x: novo_emissor(x, emissor), axis=1)
                        df_alteracao['novo_grupo'+emissor] = df_alteracao.apply(
                            lambda x: novo_grupo(x, emissor), axis=1)

                    df_alteracao['pl_fundo'] = pd.to_numeric(
                        df_alteracao['pl_fundo'], errors='coerce')
                    df_alteracao.loc['Total'] = df_alteracao.sum(numeric_only=True)
                    df_alteracao.loc['Total', '%Alocado'] = None
                    df_alteracao.at['Total', 'Fundo'] = 'Saldo'
                    saldo = {}
                    for ativo in ativos:
                        if not ativo in saldo:
                            saldo[ativo] = {}
                        saldo[ativo]['fin'] = float(
                            df_alteracao['financeiro_'+ativo].loc['Total'])
                        saldo[ativo]['qtd'] = float(
                            df_alteracao['quantidade_'+ativo].loc['Total'])

                    gb_emissores = GridOptionsBuilder.from_dataframe(df_alteracao.drop(index='Total'))
                    gb_grupos = GridOptionsBuilder.from_dataframe(df_alteracao.drop(index='Total'))
                    gb_emissores.configure_grid_options(enableRangeSelection=True, tooltipShowDelay=0)
                    gb_grupos.configure_grid_options(enableRangeSelection=True, tooltipShowDelay=0)
                    gb_grupos.configure_grid_options(enableCellTextSelection=True)
                    gb_emissores.configure_grid_options(enableCellTextSelection=True)

                    cellsytle_jscode = JsCode("""
                        function(params) {
                            if (params.value < 0) {
                                return {
                                    'color': 'white',
                                    'backgroundColor': 'red'
                                }
                            }
                        };
                        """)

                    gb_emissores, gb_grupos = gb_emissores.build(), gb_grupos.build()
                    emissores_tabela, grupos = {}, {}
                    for i in lista_ativos:
                        if i[0].strip() in ativos and i[1].strip().replace('.', '') not in emissores_tabela:
                            emissores_tabela[i[1].strip().replace('.', '')] = []
                        if i[0].strip() in ativos and tipo_operacao != 'Ajuste Proporcional':
                            coluna = 'simulacao' + i[0].strip()
                            emissores_tabela[i[1].strip().replace('.', '')].append(
                                {'field': coluna,
                                    'headerName': i[0].strip() + ' %PL Objetivo',
                                    'minWidth': 180,
                                    'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2}) + '%';",
                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"], 'cellStyle': cellsytle_jscode
                                })
                            if ver_pl_atual and tipo_operacao != 'Ajuste Proporcional':
                                emissores_tabela[i[1].strip().replace('.', '')].append(
                                    {'field': '%pl'+i[0].strip(),
                                        'headerName': i[0].strip() + ' %PL Atual',
                                        'minWidth': 180,
                                        'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2}) + '%';",
                                        "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                                    })

                    for emissor in emissores:
                        if not emissor in grupos:
                            grupos[emissor] = []
                        grupos[emissor].append(
                            {'field': 'novo_emissor' + emissor,
                                'headerName': 'Objetivo %PL Emissor',
                                'minWidth': 200,
                                'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2}) + '%';",
                                "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                            })
                        if ver_pl_atual:
                            grupos[emissor].append(
                                {'field': '%emissor'+emissor,
                                    'headerName': 'Atual %PL Emissor',
                                    'minWidth': 180,
                                    'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2}) + '%';",
                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                                })
                        grupos[emissor].append(
                            {'field': 'novo_grupo' + emissor,
                                'headerName': 'Objetivo %PL Grupo',
                                'minWidth': 160,
                                'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2}) + '%';",
                                "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                            })
                        if ver_pl_atual:
                            grupos[emissor].append(
                                {'field': '%grupo'+emissor,
                                    'headerName': 'Atual %PL Grupo',
                                    'minWidth': 160,
                                    'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2}) + '%';",
                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                                })

                    defs_emissores = []
                    for emissor in emissores_tabela:
                        defs_emissores.append({
                            'headerName': emissor,
                            'children': emissores_tabela[emissor]
                        })

                    defs_grupos = []
                    for grupo in grupos:
                        defs_grupos.append({
                            'headerName': grupo,
                            'children': grupos[grupo]
                        })

                    colunas = [
                        {'field': 'Classe', 'pinned': 'left',
                            'tooltipField': "Classe", 'minWidth': 230},
                        {'field': 'Risco', 'pinned': 'left',
                            'minWidth': 80, 'maxWidth': 80},
                        {'field': 'Fundo', 'pinned': 'left',
                            'tooltipField': "Fundo", 'minWidth': 250},
                        {'field': 'pl_fundo',  'pinned': 'left',
                            'headerName': 'PL Alocável R$', 'minWidth': 155, 'maxWidth': 155,
                            'valueFormatter': "data.pl_fundo.toLocaleString('pt-BR',{minimumFractionDigits: 0});",
                            "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                        {'field': '%Alocado', 'headerName': '% Alocado', 'pinned': 'left', 'minWidth': 120, 'maxWidth': 120,
                            'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2}) + '%'",
                            "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]}]
                    if tipo_operacao == 'Ajuste Proporcional':
                        colunas.append({'field': 'alocado_obj', 'headerName': '% Alocado Obj',
                                    'pinned': 'left', 'minWidth': 160, 'maxWidth': 160,
                                        'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%'",
                                        "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]})
                    gb_emissores['columnDefs'] = colunas
                    gb_grupos['columnDefs'] = colunas

                    gb_emissores['columnDefs'] = gb_emissores['columnDefs'] + \
                        defs_emissores
                    gb_grupos['columnDefs'] = gb_grupos['columnDefs'] + defs_grupos

                    st.subheader('Resultado da Simulação')

                    with st.expander('Nova distribuição por ativos' if tipo_operacao != 'Ajuste Proporcional' else 'Nova distribuição da carteira', expanded=True):
                        df_operacoes = AgGrid(
                            df_alteracao.drop(index='Total').reset_index(), key='1',
                            gridOptions=gb_emissores,
                            reload_data=True,
                            fit_columns_on_grid_load=False,
                            height=min(50 + 45 * len(df_alteracao.index), 400),
                            custom_css=custom_css,
                            update_mode='VALUE_CHANGED',
                            allow_unsafe_jscode=True,
                            enable_enterprise_modules=True)

                    df_simulacao = df_operacoes['data'].copy(deep=False)

                    if tipo_operacao != 'Ajuste Proporcional':
                        with st.expander('Nova distribuição por emissor/grupo'):
                                df_operacoes = AgGrid(
                                    df_alteracao.drop(index='Total').reset_index(), key='12',
                                    gridOptions=gb_grupos,
                                    reload_data=True,
                                    fit_columns_on_grid_load=False,
                                    height=min(50 + 45 * len(df_alteracao.index), 400),
                                    custom_css=custom_css,
                                    update_mode='VALUE_CHANGED',
                                    allow_unsafe_jscode=True,
                                    enable_enterprise_modules=True)
                                
                    if not st.session_state['dados_simulacao']['usar']:
                        df_operacoes = df_operacoes['data'][['Fundo']+['financeiro_' + ativo for ativo in ativos]].T.reset_index()
                        new_header = df_operacoes.iloc[0]
                        df_operacoes = df_operacoes[1:]
                        df_operacoes.columns = new_header
                        df_operacoes = df_operacoes.rename(columns={'Fundo': 'Ativo'})
                        df_operacoes['Ativo'] = df_operacoes['Ativo'].apply(lambda x: x.replace("financeiro_", ''))
                        for coluna in df_operacoes.columns:
                            def novo_perc(x, coluna, df_alteracao):
                                pl_fundo = float(df_alteracao[df_alteracao['Fundo'] == coluna]['pl_fundo'])
                                if coluna in info_ativos[x['Ativo']]:
                                    return round(((info_ativos[x['Ativo']][coluna]['financeiro'] + x[coluna]) / pl_fundo)*100, 2)
                                else:
                                    return round((x[coluna] / pl_fundo)*100, 2)
                            if coluna not in ('Ativo', 'Grupo', 'Emissor'):
                                df_operacoes[coluna] = df_operacoes.apply(lambda x: novo_perc(x, coluna, df_alteracao), axis=1)
                        df_operacoes['Grupo'] = df_operacoes.apply(lambda x: info_ativos[x['Ativo']]['grupo'], axis=1)
                        df_operacoes['Emissor'] = df_operacoes.apply(lambda x: info_ativos[x['Ativo']]['emissor'], axis=1)
                        df_operacoes['Ativo'].to_list()
                        grupos, outros_ativos = [], []
                        for ativo in ativos:
                            if info_ativos[ativo]['grupo'] not in grupos:
                                grupos.append(info_ativos[ativo]['grupo'])
                        for ativo in info_ativos:
                            if info_ativos[ativo]['grupo'] in grupos:
                                if ativo not in ativos:
                                    outros_ativos.append(ativo)

                        fundos_op = [fundo for fundo in df_operacoes.columns if fundo not in ['Ativo', 'Grupo', 'Emissor']]
                        df_operacoes = df_operacoes[['Grupo', 'Emissor', 'Ativo']+fundos_op]

                        for ativo in outros_ativos:
                            perc_pl = {}
                            for fundo in fundos_op:
                                pl_fundo = float(df_alteracao[df_alteracao['Fundo'] == fundo]['pl_fundo'])
                                if fundo in info_ativos[ativo]:
                                    perc_pl[fundo] = round((info_ativos[ativo][fundo]['financeiro']/pl_fundo)*100, 2)
                                else:
                                    perc_pl[fundo] = 0
                            df1 = pd.DataFrame([dict({
                                'Grupo': info_ativos[ativo]['grupo'],
                                'Emissor': info_ativos[ativo]['emissor'],
                                'Ativo': ativo,
                            }, **perc_pl)])
                            df_operacoes = df_operacoes.append(df1)
                        if tipo_operacao == 'Ajuste Proporcional':
                            df_operacoes = df_operacoes.rename(columns={fundo: '%Obj '+fundo for fundo in fundos})
                            for fundo in fundos:
                                df_operacoes['%Atual '+fundo] = 0
                                def perc_atual(x, fundo, df_simulacao):
                                    ativo = x['Ativo']
                                    if fundo in info_ativos[ativo]:
                                        perc = info_ativos[ativo][fundo]['financeiro'] / df_simulacao[df_simulacao['Fundo']==fundo]['pl_fundo'].tolist()[0] *100
                                    else:
                                        perc = 0
                                    return perc
                                df_operacoes['%Atual '+fundo] = df_operacoes.apply(lambda x: perc_atual(x, fundo, df_simulacao), axis=1)
                                df_operacoes['%Var '+fundo] = df_operacoes['%Obj '+fundo] - df_operacoes['%Atual '+fundo]

                        gb = GridOptionsBuilder.from_dataframe(df_operacoes)
                        gb.configure_grid_options(enableRangeSelection=True)
                        gb.configure_grid_options(enableCellTextSelection=True)
                        gb.configure_grid_options(pivotMode=True)
                        gb.configure_grid_options(
                            autoGroupColumnDef=dict(
                                minWidth=300,
                                pinned="left",
                                cellRendererParams=dict(suppressCount=True)
                            )
                        )
                        gb.configure_column(field="Grupo", rowGroup=True)
                        gb.configure_column(field="Emissor", rowGroup=True)
                        gb.configure_column(field="Ativo", rowGroup=True)
                        for fundo in fundos_op:
                            gb.configure_column(
                                field='%Obj '+fundo if tipo_operacao == 'Ajuste Proporcional' else fundo,
                                type=["numericColumn"],
                                aggFunc="sum",
                                minWidth=200,
                                valueFormatter="value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%'",
                            )
                            cellsytle_jscode = JsCode("""function(params) {return {'color': 'grey'}}""")
                            if tipo_operacao == 'Ajuste Proporcional':
                                gb.configure_column(
                                    field='%Atual '+fundo,
                                    type=["numericColumn"],
                                    aggFunc="sum",
                                    minWidth=200,
                                    cellStyle=cellsytle_jscode,
                                    valueFormatter="value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%'",
                                )
                                cellsytle_jscode = JsCode("""
                                    function(params) {
                                        if (params.value <= -0.02) {
                                            return {'color': 'red',}
                                        } 
                                        if (params.value >= 0.02) {
                                            return {'color': 'blue',}
                                        } else {
                                            return {'color': 'grey'}
                                        }
                                    };
                                    """)
                                gb.configure_column(
                                    field='%Var '+fundo,
                                    type=["numericColumn"],
                                    aggFunc="sum",
                                    minWidth=200,
                                    cellStyle=cellsytle_jscode,
                                    valueFormatter="value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%'",
                                )
                            gb.configure_column(field='   ')
                        gb = gb.build()
                        gb['autoGroupColumnDef']['headerName'] = 'Grupo/Emissor'
                        gb['suppressAggFuncInHeader'] = True
                        ordem = []
                        for fundo in fundos:
                            for coluna in ['%Obj ', '%Atual ', '%Var ']:
                                ordem+=[i for i in range(len(gb['columnDefs'])) if gb['columnDefs'][i]['headerName']==coluna+fundo]
                            ordem+=[i for i in range(len(gb['columnDefs'])) if gb['columnDefs'][i]['headerName']=='   ' and i not in ordem]
                        gb['columnDefs'] = [gb['columnDefs'][i] for i in [0, 1, 2]+ordem]                    

                    if st.session_state['dados_simulacao']['usar'] and tipo_operacao == 'Ajuste Proporcional':
                        df_operacoes = st.session_state['dados_simulacao']['Tabela transposta']
                        gb = st.session_state['dados_simulacao']['gb']
                    else:
                        st.session_state['dados_simulacao']['Tabela transposta']= df_operacoes
                        st.session_state['dados_simulacao']['gb']= gb
                    
                    with st.expander('Nova distribuição por emissor/grupo (Tabela transposta)', 
                                     expanded= True if tipo_operacao== 'Ajuste Proporcional' else False):
                        df_operacoes = AgGrid(
                            df_operacoes, key='3',
                            gridOptions=gb,
                            reload_data=True,
                            fit_columns_on_grid_load=False,
                            height=min(80 + 50 * len(df_operacoes.index), 400),
                            custom_css=custom_css,
                            update_mode='VALUE_CHANGED',
                            allow_unsafe_jscode=True,
                            enable_enterprise_modules=True)

                    gb = GridOptionsBuilder.from_dataframe(df_alteracao.drop(index='Total').reset_index())
                    gb.configure_grid_options(enableRangeSelection=True, tooltipShowDelay=0)
                    gb.configure_grid_options(enableCellTextSelection=True)
                    gb = gb.build()

                    operacoes = {}
                    for ativo in ativos:
                        operacoes[ativo] = [
                            {'field': 'quantidade_'+ativo,
                                'headerName': 'Quantidade',
                                'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 0});",
                                "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                                },
                            {'field': 'financeiro_'+ativo,
                                'headerName': 'Financeiro',
                                'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 0});",
                                "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]
                                }]

                    defs = []
                    for ativo in ativos:
                        defs.append({
                            'headerName': ativo,
                            'children': operacoes[ativo]
                        })
                    gb['columnDefs'] = [
                        {'field': 'Classe', 'pinned': 'left',
                            'tooltipField': "Classe", 'minWidth': 230},
                        {'field': 'Risco', 'pinned': 'left',
                            'minWidth': 80},
                        {'field': 'Fundo', 'pinned': 'left',
                            'tooltipField': "Fundo", 'minWidth': 250},
                        {'field': 'pl_fundo',  'pinned': 'left',
                            'headerName': 'PL Alocável R$', 'maxWidth': 155,
                            'valueFormatter': "data.pl_fundo.toLocaleString('pt-BR',{minimumFractionDigits: 0});",
                            "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                        {'field': '%Alocado', 'headerName': '% Alocado', 'pinned': 'left', 'minWidth': 120,
                            'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2}) + '%'",
                            "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]}]
                    if tipo_operacao == 'Ajuste Proporcional':
                        gb['columnDefs'].append({'field': 'alocado_obj', 'headerName': '% Alocado Obj',
                                                    'pinned': 'left', 'minWidth': 160, 'maxWidth': 160,
                                                    'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2}) + '%'",
                                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]})

                    gb['columnDefs'] = gb['columnDefs'] + defs

                    if st.session_state['dados_simulacao']['usar'] and tipo_operacao == 'Ajuste Proporcional':
                        df_alteracao = st.session_state['dados_simulacao']['Descrição das Operações']
                    else:
                        st.session_state['dados_simulacao']['Descrição das Operações']= df_alteracao

                    st.subheader('Descrição das Operações')
                    df_operacoes = AgGrid(
                        df_alteracao.drop(index='Total'), key='2',
                        gridOptions=gb,
                        reload_data=True,
                        fit_columns_on_grid_load=False,
                        height=min(50 + 45 * len(df_alteracao.index), 400),
                        custom_css=custom_css,
                        update_mode='VALUE_CHANGED',
                        allow_unsafe_jscode=True,
                        enable_enterprise_modules=True)
                    
                df_saldo, externa_com_interna = [], False
                for ativo in ativos:
                    compras = [valor for valor in df_alteracao['quantidade_'+ativo].tolist() if valor > 0]
                    vendas = [valor for valor in df_alteracao['quantidade_'+ativo].tolist() if valor < 0]
                    if tipo_operacao not in ('Ajuste', 'Ajuste Proporcional') and (len(compras) > 0 and len(vendas) > 0):
                        externa_com_interna = True

                    residuo_quantidade = None
                    if tipo_operacao == 'Externa por Quantidade':
                        tipo = df_objetivo[df_objetivo['Ativo'] == ativo]['Tipo'].tolist()[0]
                        if tipo == 'Venda':
                            qtd_objetivo = - df_objetivo[df_objetivo['Ativo'] == ativo]['Quantidade'].tolist()[0]
                        else:
                            qtd_objetivo = df_objetivo[df_objetivo['Ativo'] == ativo]['Quantidade'].tolist()[0]
                        qtd_simulacao = df_alteracao['quantidade_' + ativo].loc['Total']
                        residuo_quantidade = qtd_objetivo - qtd_simulacao

                    pu_b3, preco_calculado, pu_operacao = None, None, None
                    if tipo_operacao == 'Externa por Quantidade':
                        with st.spinner('Calculando...'):
                            taxa_corretora = df_objetivo[df_objetivo['Ativo'] == ativo]['Taxa'].tolist()[0]
                            pu_operacao = df_objetivo[df_objetivo['Ativo'] == ativo]['PU'].tolist()[0]

                            try:
                                pu_b3 = calc_pu_b3(ativo, taxa_corretora)
                            except:
                                pu_b3 = 0

                            try:
                                info, fluxo = papeis_calculo[ativo], fluxo_papeis[ativo]
                                calculo = calculadora.papel(info, fluxo, db)
                                preco_calculado = calculo.duration(
                                    date.today(), taxa_corretora, curva_di)['PU']
                            except:
                                preco_calculado = 0

                    df_saldo.append({'Ativo': ativo,
                                    'Saldo Quantidade': df_alteracao['quantidade_'+ativo].loc['Total'],
                                        'Saldo Financeiro': df_alteracao['financeiro_'+ativo].loc['Total'] if df_alteracao['quantidade_'+ativo].loc['Total'] != 0 else 0,
                                        'Escolher Fundo': None,
                                        'Taxa': None,
                                        'Taxa Ajuste': None,
                                        'Quantidade Externa': df_objetivo[df_objetivo['Ativo'] == ativo]['Quantidade'].tolist()[0] if tipo_operacao != 'Ajuste Proporcional' else None,
                                        'Resíduo Quantidade': residuo_quantidade,
                                        'Resíduo Financeiro': residuo_quantidade * pu_operacao if tipo_operacao == 'Externa por Quantidade' else None,
                                        'PU B3': pu_b3,
                                        'PU Calculadora': preco_calculado,
                                        'PU Corretora': pu_operacao,
                                        'Financeiro B3': df_objetivo[df_objetivo['Ativo'] == ativo]['Quantidade'].tolist()[0] * pu_b3 if tipo_operacao == 'Externa por Quantidade' else None,
                                        'Financeiro Calculadora': df_objetivo[df_objetivo['Ativo'] == ativo]['Quantidade'].tolist()[0] * preco_calculado if tipo_operacao == 'Externa por Quantidade' else None,
                                        'Financeiro Corretora': df_objetivo[df_objetivo['Ativo'] == ativo]['Quantidade'].tolist()[0] * pu_operacao if tipo_operacao == 'Externa por Quantidade' else None,
                                        'Diferença (B3)': df_objetivo[df_objetivo['Ativo'] == ativo]['Quantidade'].tolist()[0] * pu_b3 - df_objetivo[df_objetivo['Ativo'] == ativo]['Quantidade'].tolist()[0] * pu_operacao if tipo_operacao == 'Externa por Quantidade' else None,
                                        'Diferença (Calculadora)': df_objetivo[df_objetivo['Ativo'] == ativo]['Quantidade'].tolist()[0] * preco_calculado - df_objetivo[df_objetivo['Ativo'] == ativo]['Quantidade'].tolist()[0] * pu_operacao if tipo_operacao == 'Externa por Quantidade' else None,
                                        'Contraparte': None,
                                        'Contraparte Ajuste': None,
                                        'abs': abs(df_alteracao['financeiro_'+ativo].loc['Total'])})

                df_saldo = pd.DataFrame(df_saldo)
                df_saldo = df_saldo.sort_values(['abs'], ascending=[False])
                gb_saldo = GridOptionsBuilder.from_dataframe(df_saldo)
                gb_financeiro = GridOptionsBuilder.from_dataframe(df_saldo)
                gb_saldo.configure_grid_options(enableRangeSelection=True, tooltipShowDelay=0)
                gb_financeiro.configure_grid_options(enableRangeSelection=True, tooltipShowDelay=0)
                gb_saldo.configure_grid_options(enableCellTextSelection=True)
                gb_financeiro.configure_grid_options(enableCellTextSelection=True)
                gb_saldo, gb_financeiro = gb_saldo.build(), gb_financeiro.build()

                contrapartes = [
                    'ABC Brasil', 'Alfa CCVM', 'Ativa', 'Banco ABC', 'Banco Alfa', 'BANCO DO BRASIL',
                    'Banco Pan', 'Banco Paulista', 'BANRISUL', 'BB BI', 'BGC', 'BNP PARIBAS',
                    'BOCOM BBM', 'BR Partners', 'Bradesco', 'Bradesco BBI', 'BTG Pactual', 'Caixa',
                    'Citibank', 'CM Capital', 'Credit Suisse', 'CSF', 'Daycoval', 'FRAM CAPITAL',
                    'Genial', 'GUIDE', 'Industrial', 'Inter', 'Itau', 'Itaú BBA',
                    'J.P. Morgan', 'MAF', 'Mercedes-Benz', 'Mirae', 'Modal', 'Necton',
                    'OPEA', 'ÓRAMA', 'Parana Banco', 'Planner', 'Porto Seguro', 'Porto Seguro Financeira',
                    'Quadra', 'Rabobank', 'RB CAPITAL', 'Renascença', 'Safra', 'Santander',
                    'Sicredi', 'Singulare', 'TERRA', 'Toyota', 'Tribanco', 'UBS',
                    'UBS BB', 'UBS Brasil', 'Votorantim', 'Warren', 'XP'
                ]

                defs = []
                defs.append({
                    'headerName': 'Informações de PU',
                    'children': [{'field': 'PU B3', 'headerName': 'B3', 'minWidth': 120,
                                    'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6});",
                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                                    {'field': 'PU Calculadora', 'headerName': 'Calculadora',
                                    'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6});",
                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                                    {'field': 'PU Corretora',  'headerName': 'Corretora',
                                    'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 6});",
                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]}]
                })
                defs.append({'headerName': '', 'minWidth': 120})
                defs.append({
                    'headerName': 'Financeiro Total R$',
                    'children': [{'field': 'Financeiro B3', 'headerName': 'B3',
                                    'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});",
                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                                    {'field': 'Financeiro Calculadora',   'headerName': 'Calculadora',
                                    'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});",
                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                                    {'field': 'Financeiro Corretora',  'headerName': 'Corretora',
                                    'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});",
                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]}]
                })
                defs.append({'headerName': '', 'minWidth': 120})
                defs.append({
                    'headerName': 'Diferença R$',
                    'children': [{'field': 'Diferença (B3)', 'headerName': 'B3',
                                    'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});",
                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                                    {'field': 'Diferença (Calculadora)',  'headerName': 'Calculadora',
                                    'valueFormatter': "value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});",
                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]}]
                })

                gb_financeiro['columnDefs'] = [{'field': 'Ativo', 'minWidth': 150}] + defs
                gb_saldo['columnDefs'] = [{'field': 'Ativo', 'minWidth': 150},]
                if tipo_operacao != 'Externa por Quantidade':
                    gb_saldo['columnDefs'].append(
                        {'field': 'Saldo Quantidade',
                            'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 0});",
                            "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]})
                    gb_saldo['columnDefs'].append(
                        {'field': 'Saldo Financeiro', 'headerName': 'Saldo Financeiro R$',
                            'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 0});",
                            "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]})

                if tipo_operacao == 'Externa por Quantidade':
                    gb_saldo['columnDefs'].append({'field': 'Resíduo Quantidade',  'headerName': 'Saldo Quantidade',
                                                    'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 0});",
                                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]})
                    gb_saldo['columnDefs'].append({'field': 'Resíduo Financeiro',  'headerName': 'Saldo Financeiro R$',
                                                    'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 0});",
                                                    "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]})

                if tipo_operacao in ['Ajuste', 'Ajuste Proporcional', 'Externa por Quantidade']:
                    gb_saldo['columnDefs'].append({'field': 'Escolher Fundo', 'editable': True,
                                                    'cellStyle': {'background-color': 'rgb(236, 240, 241)'},
                                                    'cellEditor': 'agRichSelectCellEditor',
                                                    'cellEditorParams': {'values': sorted(df_alteracao[df_alteracao['Fundo'] != 'Saldo']['Fundo'].tolist())},
                                                    'cellEditorPopup': True})

                if tipo_operacao not in ('Externa por Quantidade'):
                    gb_saldo['columnDefs'] = gb_saldo['columnDefs'] + [{'field': 'Taxa',  'editable': True,
                                                                        'headerName': 'Taxa Externa' if externa_com_interna else 'Taxa',
                                                                        'cellStyle': {'background-color': 'rgb(236, 240, 241)'},
                                                                        'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 3}) + '%';",
                                                                        "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]}]

                gb_saldo['columnDefs'] = gb_saldo['columnDefs'] + [
                    {'field': 'Contraparte', 'editable': True,
                        'headerName': 'Contraparte Externa' if externa_com_interna else 'Contraparte',
                        'cellStyle': {'background-color': 'rgb(236, 240, 241)'},
                        'cellEditor': 'agRichSelectCellEditor',
                        'cellEditorParams': {'values': contrapartes},
                        'cellEditorPopup': True}]

                if externa_com_interna and tipo_operacao not in ('Externa por Quantidade'):
                    gb_saldo['columnDefs'] = gb_saldo['columnDefs'] + [
                        {'field': 'Taxa Ajuste',  'editable': True,
                            'cellStyle': {'background-color': 'rgb(236, 240, 241)'},
                            'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 3}) + '%';",
                            "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]}]

                if externa_com_interna:
                    gb_saldo['columnDefs'] = gb_saldo['columnDefs'] + [
                        {'field': 'Contraparte Ajuste', 'editable': True,
                            'cellStyle': {'background-color': 'rgb(236, 240, 241)'},
                            'cellEditor': 'agRichSelectCellEditor',
                            'cellEditorParams': {'values': contrapartes},
                            'cellEditorPopup': True}]

                form = st.form('a')
                st.session_state['dados_simulacao']['usar'] = False

                with form:
                    df_financeiro = df_saldo.copy(deep=False)
                    st.subheader('Informações para as boletas')
                    key = '23' if externa_com_interna else '29'
                    if tipo_operacao == 'Externa por Quantidade':
                        df_fin = AgGrid(
                            df_financeiro, key='wtgv',
                            gridOptions=gb_financeiro,
                            fit_columns_on_grid_load=False,
                            custom_css=custom_css,
                            height=min(
                                80 + 45 * len(df_financeiro.index), 400),
                            reload_data=True,
                            update_mode='MODEL_CHANGED',
                            allow_unsafe_jscode=True,
                            enable_enterprise_modules=True)

                    df_saldo = AgGrid(
                        df_saldo, key=key,
                        gridOptions=gb_saldo,
                        fit_columns_on_grid_load=False,
                        custom_css=custom_css,
                        reload_data=True,
                        update_mode='MODEL_CHANGED',
                        allow_unsafe_jscode=True,
                        enable_enterprise_modules=True)

                    def calc_gerar():
                        st.session_state['calc'] = True
                        st.session_state['dados'] = fundos + ativos
                        if tipo_operacao == 'Ajuste Proporcional':
                            st.session_state['dados_simulacao']['usar'] = True
                        else:
                            st.session_state['dados_simulacao']['usar'] = False
                    st.session_state['dados_simulacao']['usar'] = False

                    if tipo_operacao == 'Externa por Quantidade':
                        aviso = []
                        for ativo in ativos:
                            diferenca = df_financeiro[df_financeiro['Ativo'] == ativo]['Diferença (B3)'].tolist()[
                                0]
                            if abs(diferenca) > 0:
                                aviso.append(ativo)

                        if aviso:
                            col1, _ = st.columns([3, 1])
                            col1.error(
                                'Existe diferença de PU para os seguintes ativos: ' + ', '.join(aviso))
                    gerar = st.form_submit_button(
                        'Gerar boletas', on_click=calc_gerar)
            except:
                try:
                    def calc_gerar():
                        st.session_state['calc'] = True
                        st.session_state['dados'] = fundos + ativos
                    with form:
                        gerar = st.form_submit_button(
                            'Gerar boletas', on_click=calc_gerar())
                except:
                    pass
                st.caption('Houve um erro')
                gerar = None

            try:
                lista_quantidade = []
                for ativo in ativos:
                    for quantidade in df_operacoes['data']['quantidade_'+ativo].tolist():
                        if quantidade != 0:
                            lista_quantidade.append(quantidade)

                if not lista_quantidade:
                    st.caption('A simulação não gerou boletas')
                if gerar and lista_quantidade:
                    with st.spinner('Aguarde...'):
                        st.markdown(
                            ''' <a target="_self" href="#1eb1a24">Voltar ao Topo</a>''', unsafe_allow_html=True)

                        df_operacoes = df_operacoes['data']
                        df_saldo = df_saldo['data']

                        if (('None' in df_saldo[(df_saldo['Saldo Quantidade'] > 0) | (df_saldo['Saldo Quantidade'] < 0)]['Escolher Fundo'].tolist() or
                            None in df_saldo[(df_saldo['Saldo Quantidade'] > 0) | (df_saldo['Saldo Quantidade'] < 0)]['Escolher Fundo'].tolist() or
                            '' in df_saldo[(df_saldo['Saldo Quantidade'] > 0) | (df_saldo['Saldo Quantidade'] < 0)]['Escolher Fundo'].tolist()) and
                                not df_saldo['Saldo Quantidade'].sum() == 0) and tipo_operacao in ('Ajuste', 'Ajuste Proporcional'):

                            with form:
                                col1, _ = st.columns(2)
                                col1.error(
                                    'Escolha os fundos para zeragem de saldo.')
                        elif permite_ajuste == False and externa_com_interna:
                            with form:
                                col1, _ = st.columns(2)
                                col1.error(
                                    'Esta simulação não é permitida. Marque a opção "Permitir ajuste" para prosseguir')
                        elif alocacao_incorreta and tipo_operacao == 'Ajuste Proporcional':
                            with form:
                                col1, _ = st.columns(2)
                                col1.error(
                                    'Esta simulação não é permitida. Não foram selecionados ativos suficientes para a alocação ou o PL de um dos fundos está alavancado.')
                        elif alocacao_incorreta:
                            with form:
                                col1, _ = st.columns(2)
                                col1.error(
                                    'Esta simulação não é permitida. Existem valores negativos na simulação.')
                        else:

                            info_boletas = {}
                            for ind, row in df_saldo.iterrows():
                                info_boletas[row['Ativo']] = {}
                                info_boletas[row['Ativo']]['Taxa'] = float(str(row['Taxa']).replace(",", '.')) if (
                                    row['Taxa'] != 'None' and row['Taxa'] != '' and row['Taxa'] != None) else None
                                info_boletas[row['Ativo']]['Taxa Ajuste'] = float(str(row['Taxa Ajuste']).replace(",", '.')) if (
                                    row['Taxa Ajuste'] != 'None' and row['Taxa Ajuste'] != '' and row['Taxa Ajuste'] != None) else None
                                info_boletas[row['Ativo']]['Contraparte'] = row['Contraparte'] if (
                                    row['Contraparte'] != 'None' and row['Contraparte'] != '' and row['Contraparte'] != None) else None
                                info_boletas[row['Ativo']]['Contraparte Ajuste'] = row['Contraparte Ajuste'] if (
                                    row['Contraparte Ajuste'] != 'None' and row['Contraparte Ajuste'] != '' and row['Contraparte Ajuste'] != None) else None

                                if not (row['Escolher Fundo'] == 'None' or row['Escolher Fundo'] == None):
                                    index = df_operacoes[df_operacoes['Fundo']
                                                        == row['Escolher Fundo']].index[0]
                                    qtd = df_operacoes.at[index,
                                                        'quantidade_'+row['Ativo']]
                                    if tipo_operacao != 'Externa por Quantidade':
                                        df_operacoes.at[index, 'quantidade_' +
                                                        row['Ativo']] = qtd - row['Saldo Quantidade']
                                    else:
                                        df_operacoes.at[index, 'quantidade_' +
                                                        row['Ativo']] = qtd + row['Resíduo Quantidade']

                            info_saldo = {}
                            if tipo_operacao in ['Ajuste', 'Externa por Quantidade', 'Ajuste Proporcional']:
                                for ativo in ativos:
                                    for fundo in df_operacoes['Fundo'].tolist():
                                        qtd_operacao = df_operacoes[df_operacoes['Fundo'] == fundo]['quantidade_'+ativo].tolist()[
                                            0]
                                        if qtd_operacao < 0 and fundo not in info_ativos[ativo]:
                                            info_saldo['fundo'] = fundo
                                            info_saldo['ativo'] = ativo
                                        if qtd_operacao < 0 and fundo in info_ativos[ativo] and abs(qtd_operacao) > info_ativos[ativo][fundo]['qtd']:
                                            info_saldo['fundo'] = fundo
                                            info_saldo['ativo'] = ativo

                            escolher_fundo = False

                            for ativo in ativos:
                                saldo = abs(
                                    sum(df_operacoes['quantidade_'+ativo].tolist()))
                                if saldo != df_objetivo[df_objetivo['Ativo'] == ativo]['Quantidade'].tolist()[0] and tipo_operacao == 'Externa por Quantidade':
                                    with form:
                                        col1, _ = st.columns(2)
                                        col1.error(
                                            'Escolha os fundos para zeragem de saldo.')
                                        escolher_fundo = True
                                        break
                            if escolher_fundo and tipo_operacao == 'Externa por Quantidade':
                                pass
                            elif 'fundo' in info_saldo:
                                with form:
                                    col1, _ = st.columns(2)
                                    col1.error(
                                        f'O fundo {info_saldo["fundo"]} não possui quantidade suficiente para venda do ativo {info_saldo["ativo"]}. Escolha outro fundo para distribuição do saldo.')
                            else:
                                operacoes = []

                                def filas(ativo, df):
                                    df_fila_vendedores = df[df['quantidade_'+ativo] < 0]
                                    df_fila_vendedores = df_fila_vendedores[['Fundo', 'quantidade_'+ativo]].sort_values(
                                        ['quantidade_'+ativo], ascending=[True]).reset_index(drop=True)

                                    df_fila_compradores = df[df['quantidade_'+ativo] > 0]
                                    df_fila_compradores = df_fila_compradores[['Fundo', 'quantidade_'+ativo]].sort_values(
                                        ['quantidade_'+ativo], ascending=[True]).reset_index(drop=True)

                                    fila_compradores, indice = {}, 1
                                    for ind, row in df_fila_compradores.iterrows():
                                        fila_compradores[indice] = {
                                            'Fundo': row['Fundo'], 'Quantidade': row['quantidade_'+ativo]}
                                        indice += 1

                                    fila_vendedores, indice = {}, 1
                                    for ind, row in df_fila_vendedores.iterrows():
                                        fila_vendedores[indice] = {
                                            'Fundo': row['Fundo'], 'Quantidade': abs(row['quantidade_'+ativo])}
                                        indice += 1
                                    return fila_compradores, fila_vendedores

                                if tipo_operacao in ('Ajuste', "Ajuste Proporcional"):
                                    for ativo in ativos:
                                        fila_compradores, fila_vendedores = filas(
                                            ativo, df_operacoes)

                                        for i in sorted(fila_compradores.keys()):
                                            comprador = fila_compradores[i]['Fundo']
                                            qtd_comprada = fila_compradores[i]['Quantidade']

                                            while qtd_comprada > 0:
                                                for j in sorted(fila_vendedores.keys()):
                                                    vendedor = fila_vendedores[j]['Fundo']
                                                    qtd_vendida = fila_vendedores[j]['Quantidade']
                                                    if qtd_vendida > 0 and qtd_vendida > qtd_comprada:
                                                        operacoes.append(
                                                            {'Ativo': ativo, 'Side': 'C', 'Fundo': comprador, 'Quantidade': qtd_comprada})
                                                        operacoes.append(
                                                            {'Ativo': ativo, 'Side': 'V', 'Fundo': vendedor, 'Quantidade': qtd_comprada})
                                                        fila_vendedores[j]['Quantidade'] -= qtd_comprada
                                                        qtd_comprada = 0
                                                        break
                                                    if qtd_vendida > 0 and qtd_vendida == qtd_comprada:
                                                        operacoes.append(
                                                            {'Ativo': ativo, 'Side': 'C', 'Fundo': comprador, 'Quantidade': qtd_comprada})
                                                        operacoes.append(
                                                            {'Ativo': ativo, 'Side': 'V', 'Fundo': vendedor, 'Quantidade': qtd_comprada})
                                                        fila_vendedores[j]['Quantidade'] = 0
                                                        qtd_comprada = 0
                                                        break
                                                    if qtd_vendida > 0 and qtd_vendida < qtd_comprada:
                                                        operacoes.append(
                                                            {'Ativo': ativo, 'Side': 'C', 'Fundo': comprador, 'Quantidade': qtd_vendida})
                                                        operacoes.append(
                                                            {'Ativo': ativo, 'Side': 'V', 'Fundo': vendedor, 'Quantidade': qtd_vendida})
                                                        fila_vendedores[j]['Quantidade'] = 0
                                                        qtd_comprada -= qtd_vendida

                                if tipo_operacao in ['Externa por % do PL', 'Externa por Financeiro', 'Externa por Quantidade']:
                                    for ativo in ativos:
                                        fila_compradores, fila_vendedores = filas(
                                            ativo, df_operacoes)
                                        saldo = df_operacoes['financeiro_'+ativo].sum()
                                        if externa_com_interna:
                                            if saldo < 0:
                                                fila = fila_compradores
                                                fila_contraparte = fila_vendedores
                                                operacao = 'C'
                                                operacao_contraparte = 'V'
                                            else:
                                                fila = fila_vendedores
                                                fila_contraparte = fila_compradores
                                                operacao = 'V'
                                                operacao_contraparte = 'C'

                                            for i in sorted(fila.keys()):
                                                fundo = fila[i]['Fundo']
                                                qtd_fundo = fila[i]['Quantidade']

                                                while qtd_fundo > 0:
                                                    for j in sorted(fila_contraparte.keys()):
                                                        fundo_contraparte = fila_contraparte[j]['Fundo']
                                                        qtd_contraparte = fila_contraparte[j]['Quantidade']
                                                        if qtd_contraparte > 0 and qtd_contraparte > qtd_fundo:
                                                            operacoes.append(
                                                                {'Ativo': ativo, 'Side': operacao, 'Fundo': fundo, 'Quantidade': qtd_fundo, 'Tipo': 'Ajuste'})
                                                            operacoes.append(
                                                                {'Ativo': ativo, 'Side': operacao_contraparte, 'Fundo': fundo_contraparte, 'Quantidade': qtd_fundo, 'Tipo': 'Ajuste'})
                                                            fila_contraparte[j]['Quantidade'] -= qtd_fundo
                                                            qtd_fundo = 0
                                                            break
                                                        if qtd_contraparte > 0 and qtd_contraparte == qtd_fundo:
                                                            operacoes.append(
                                                                {'Ativo': ativo, 'Side': operacao, 'Fundo': fundo, 'Quantidade': qtd_fundo, 'Tipo': 'Interna'})
                                                            operacoes.append(
                                                                {'Ativo': ativo, 'Side': operacao_contraparte, 'Fundo': fundo_contraparte, 'Quantidade': qtd_fundo, 'Tipo': 'Ajuste'})
                                                            fila_contraparte[j]['Quantidade'] = 0
                                                            qtd_fundo = 0
                                                            break
                                                        if qtd_contraparte > 0 and qtd_contraparte < qtd_fundo:
                                                            operacoes.append(
                                                                {'Ativo': ativo, 'Side': operacao, 'Fundo': fundo, 'Quantidade': qtd_contraparte, 'Tipo': 'Ajuste'})
                                                            operacoes.append(
                                                                {'Ativo': ativo, 'Side': operacao_contraparte, 'Fundo': fundo_contraparte, 'Quantidade': qtd_contraparte, 'Tipo': 'Ajuste'})
                                                            fila_contraparte[j]['Quantidade'] = 0
                                                            qtd_fundo -= qtd_contraparte

                                            for i in sorted(fila_contraparte.keys()):
                                                fundo = fila_contraparte[i]['Fundo']
                                                qtd_fundo = fila_contraparte[i]['Quantidade']
                                                if qtd_fundo > 0:
                                                    operacoes.append(
                                                        {'Ativo': ativo, 'Side': operacao_contraparte, 'Fundo': fundo, 'Quantidade': qtd_fundo, 'Tipo': 'Externa'})
                                        else:
                                            for ind, row in df_operacoes.iterrows():
                                                if row['quantidade_'+ativo] > 0:
                                                    operacoes.append(
                                                        {'Ativo': ativo, 'Side': 'C', 'Fundo': row['Fundo'], 'Quantidade': row['quantidade_'+ativo], 'Tipo': 'Externa'})
                                                else:
                                                    operacoes.append({'Ativo': ativo, 'Side': 'V', 'Fundo': row['Fundo'], 'Quantidade': abs(
                                                        row['quantidade_'+ativo]), 'Tipo': 'Externa'})

                                boletas, dados_boleta = [], {}

                                def calc_taxa(indice, side, taxa, tipo):
                                    taxa_venda = 0
                                    if tipo == 'Ajuste':
                                        if indice == '%CDI':
                                            taxa_venda = taxa + 0.025
                                            taxa -= 0.025
                                        else:
                                            taxa_venda = taxa + 0.0025
                                            taxa -= 0.0025
                                    else:
                                        if indice == '%CDI' and side == 'C':
                                            taxa = taxa - 0.1
                                        elif indice == '%CDI' and side == 'V':
                                            taxa_venda = taxa + 0.1
                                        elif indice != '%CDI' and side == 'C':
                                            taxa = taxa - 0.01
                                        else:
                                            taxa_venda = taxa + 0.01
                                    return taxa, taxa_venda

                                operacoes = pd.DataFrame(operacoes)
                                calculos = {}
                                for ind, row in operacoes.iterrows():
                                    ativo = row['Ativo']
                                    ajuste, tipo = '', 'Ajuste'
                                    taxa_corretora = df_objetivo[df_objetivo['Ativo'] == ativo]['Taxa'].tolist()[0]
                                    pu_operacao = df_objetivo[df_objetivo['Ativo'] == ativo]['PU'].tolist()[0]
                                    side_externa = df_objetivo[df_objetivo['Ativo'] == ativo]['Tipo'].tolist()[0]

                                    if 'Tipo' in operacoes.columns and row['Tipo'] == 'Externa':
                                        tipo = 'Externa'
                                    if 'Tipo' in operacoes.columns and row['Tipo'] == 'Ajuste' and externa_com_interna:
                                        ajuste = ' Ajuste'

                                    if tipo_operacao == 'Externa por Quantidade':
                                        calcular_compra, calcular_venda = False, False
                                        if not ativo in calculos:
                                            calculos[ativo] = {}

                                        if tipo == 'Externa':
                                            taxa_venda, taxa = taxa_corretora, taxa_corretora
                                            preco_compra, preco_venda = pu_operacao, pu_operacao
                                        else:
                                            indice = info_ativos[ativo]['indice']

                                            if side_externa == 'Compra' and row['Side'] == 'V' and indice == '%CDI':
                                                taxa_venda = taxa_corretora + 0.025
                                                taxa = taxa_corretora - 0.025
                                                calcular_venda = True
                                                calcular_compra = False
                                            if side_externa == 'Compra' and row['Side'] == 'V' and indice != '%CDI':
                                                taxa_venda = taxa_corretora + 0.0025
                                                taxa = taxa_corretora - 0.0025
                                                calcular_compra = False
                                                calcular_venda = True
                                            if side_externa == 'Compra' and row['Side'] == 'C' and indice == '%CDI':
                                                taxa_venda = taxa_corretora + 0.025
                                                taxa = taxa_corretora - 0.025
                                                calcular_compra = False
                                                calcular_venda = True
                                            if side_externa == 'Compra' and row['Side'] == 'C' and indice != '%CDI':
                                                taxa_venda = taxa_corretora + 0.0025
                                                taxa = taxa_corretora - 0.0025
                                                calcular_compra = False
                                                calcular_venda = True
                                            if side_externa == 'Venda' and row['Side'] == 'V' and indice == '%CDI':
                                                taxa_venda = taxa_corretora + 0.025
                                                taxa = taxa_corretora - 0.025
                                                calcular_compra = True
                                                calcular_venda = False
                                            if side_externa == 'Venda' and row['Side'] == 'V' and indice != '%CDI':
                                                taxa_venda = taxa_corretora + 0.0025
                                                taxa = taxa_corretora - 0.0025
                                                calcular_compra = True
                                                calcular_venda = False

                                            if row['Side'] == 'V':
                                                if not taxa_venda in calculos[ativo]:
                                                    info, fluxo = papeis_calculo[ativo], fluxo_papeis[ativo]
                                                    calculo = calculadora.papel(info, fluxo, db)
                                                    calc = calculo.duration(date.today(), taxa_venda, curva_di)
                                                    try:
                                                        preco_venda = calc_pu_b3(ativo, taxa_venda)
                                                    except:
                                                        preco_venda = calc['PU']
                                                    duration_venda = calc['Duration']
                                                    calculos[ativo][taxa_venda] = {}
                                                    if calcular_venda:
                                                        calculos[ativo][taxa_venda]['PU'] = preco_venda
                                                    else:
                                                        calculos[ativo][taxa_venda]['PU'] = pu_operacao
                                                        preco_venda = pu_operacao
                                                    calculos[ativo][taxa_venda]['Duration'] = duration_venda

                                                    spread_venda = calculo.calcular_spread(taxa_venda,
                                                                                        duration_venda,
                                                                                        date.today(),
                                                                                        curva_di,
                                                                                        curva_ntnb)
                                                    calculos[ativo][taxa_venda]['Spread'] = spread_venda
                                                else:
                                                    preco_venda = calculos[ativo][taxa_venda]['PU']
                                                    duration_venda = calculos[ativo][taxa_venda]['Duration']
                                                    spread_venda = calculos[ativo][taxa_venda]['Spread']

                                        if not taxa in calculos[ativo]:
                                            info, fluxo = papeis_calculo[ativo], fluxo_papeis[ativo]
                                            calculo = calculadora.papel(info, fluxo, db)
                                            calc = calculo.duration(date.today(), taxa, curva_di)
                                            try:
                                                preco_compra = calc_pu_b3(ativo, taxa)
                                            except:
                                                preco_compra = calc['PU']
                                            duration_compra = calc['Duration']
                                            duration_venda = duration_compra
                                            calculos[ativo][taxa] = {}
                                            if calcular_compra:
                                                calculos[ativo][taxa]['PU'] = preco_compra
                                            else:
                                                calculos[ativo][taxa]['PU'] = pu_operacao
                                                preco_compra = pu_operacao
                                            calculos[ativo][taxa]['Duration'] = duration_compra

                                            spread_compra = calculo.calcular_spread(taxa,
                                                                                    duration_compra,
                                                                                    date.today(),
                                                                                    curva_di,
                                                                                    curva_ntnb)
                                            calculos[ativo][taxa]['Spread'] = spread_compra

                                        else:
                                            preco_compra = calculos[ativo][taxa]['PU']
                                            duration_compra = calculos[ativo][taxa]['Duration']
                                            duration_venda = duration_compra
                                            spread_compra = calculos[ativo][taxa]['Spread']

                                        if row['Side'] == 'V' and (not taxa_venda in calculos[ativo]):
                                            spread_venda = calculo.calcular_spread(taxa_venda,
                                                                                duration_venda,
                                                                                date.today(),
                                                                                curva_di,
                                                                                curva_ntnb)
                                            calculos[ativo][taxa_venda]['Spread'] = spread_venda
                                        if row['Side'] == 'V' and (taxa_venda in calculos[ativo]):
                                            spread_venda = calculos[ativo][taxa_venda]['Spread']

                                    else:
                                        try:
                                            if info_boletas[ativo]['Taxa'+ajuste]:
                                                taxa = info_boletas[ativo]['Taxa'+ajuste]

                                                if not (ativo in dados_boleta and 'taxa'+ajuste in dados_boleta[ativo]):
                                                    info, fluxo = papeis_calculo[ativo], fluxo_papeis[ativo]
                                                    calculo = calculadora.papel(
                                                        info, fluxo, db)
                                                    dados_boleta[ativo] = {}
                                                    dados_boleta[ativo]['taxa'+ajuste] = round(taxa, 3)
                                                    calc = calculo.duration(date.today(), taxa, curva_di)
                                                    preco_compra = calc['PU']
                                                    duration_compra = calc['Duration']
                                                    spread_compra = calculo.calcular_spread(
                                                        taxa,
                                                        duration_compra,
                                                        date.today(),
                                                        curva_di,
                                                        curva_ntnb)
                                                    dados_boleta[ativo]['preco_compra' + ajuste] = preco_compra
                                                    dados_boleta[ativo]['duration_compra' +ajuste] = duration_compra
                                                    dados_boleta[ativo]['spread_compra' +ajuste] = spread_compra
                                                    taxa, taxa_venda = calc_taxa(
                                                        info_ativos[ativo]['indice'], row['Side'], taxa, tipo)

                                                    calc = calculo.duration(date.today(), taxa_venda, curva_di)
                                                    preco_venda = calc['PU']
                                                    duration_venda = calc['Duration']
                                                    spread_venda = calculo.calcular_spread(
                                                        taxa_venda,
                                                        duration_venda,
                                                        date.today(),
                                                        curva_di,
                                                        curva_ntnb)
                                                    dados_boleta[ativo]['preco_venda' +ajuste] = preco_venda
                                                    dados_boleta[ativo]['duration_venda'+ajuste] = duration_venda
                                                    dados_boleta[ativo]['spread_venda'+ajuste] = spread_venda
                                                else:
                                                    taxa, taxa_venda = calc_taxa(info_ativos[ativo]['indice'], row['Side'], taxa, tipo)

                                                    preco_compra = dados_boleta[ativo]['preco_compra'+ajuste]
                                                    preco_venda = dados_boleta[ativo]['preco_venda'+ajuste]
                                                    duration_compra = dados_boleta[ativo]['duration_compra'+ajuste]
                                                    duration_venda = dados_boleta[ativo]['duration_venda'+ajuste]
                                                    spread_compra = dados_boleta[ativo]['spread_compra'+ajuste]
                                                    spread_venda = dados_boleta[ativo]['spread_venda'+ajuste]

                                            else:
                                                if not ativo in dados_boleta:
                                                    info, fluxo = papeis_calculo[ativo], fluxo_papeis[ativo]
                                                    calculo = calculadora.papel(info, fluxo, db)
                                                    dados_boleta[ativo] = {}
                                                if 'taxa'+ajuste in dados_boleta[ativo]:
                                                    taxa = dados_boleta[ativo]['taxa'+ajuste]
                                                    taxa, taxa_venda = calc_taxa(
                                                        info_ativos[ativo]['indice'], row['Side'], taxa, tipo)

                                                    preco_compra = dados_boleta[ativo]['preco_compra'+ajuste]
                                                    preco_venda = dados_boleta[ativo]['preco_venda'+ajuste]
                                                    duration_compra = dados_boleta[ativo]['duration_compra'+ajuste]
                                                    duration_venda = dados_boleta[ativo]['duration_venda'+ajuste]
                                                    spread_compra = dados_boleta[ativo]['spread_compra'+ajuste]
                                                    spread_venda = dados_boleta[ativo]['spread_venda'+ajuste]
                                                else:
                                                    taxa = info_ativos[ativo]['taxa']
                                                    dados_boleta[ativo]['taxa' +ajuste] = taxa
                                                    calc = calculo.duration(date.today(), taxa, curva_di)
                                                    preco_compra = calc['PU']
                                                    duration_compra = calc['Duration']
                                                    spread_compra = calculo.calcular_spread(
                                                        taxa,
                                                        duration_compra,
                                                        date.today(),
                                                        curva_di,
                                                        curva_ntnb)
                                                    dados_boleta[ativo]['preco_compra' +ajuste] = preco_compra
                                                    dados_boleta[ativo]['duration_compra' +ajuste] = duration_compra
                                                    dados_boleta[ativo]['spread_compra' +ajuste] = spread_compra
                                                    taxa, taxa_venda = calc_taxa(info_ativos[ativo]['indice'], row['Side'], taxa, tipo)

                                                    calc = calculo.duration(date.today(), taxa_venda, curva_di)
                                                    preco_venda = calc['PU']
                                                    duration_venda = calc['Duration']
                                                    spread_venda = calculo.calcular_spread(
                                                        taxa_venda,
                                                        duration_venda,
                                                        date.today(),
                                                        curva_di,
                                                        curva_ntnb)
                                                    dados_boleta[ativo]['preco_venda' +ajuste] = preco_venda
                                                    dados_boleta[ativo]['duration_venda' +ajuste] = duration_venda
                                                    dados_boleta[ativo]['spread_venda' +ajuste] = spread_venda
                                        except:
                                            taxa, taxa_venda = None, None
                                            duration_compra, duration_venda = None, None
                                            spread_compra, spread_venda = None, None
                                            preco_compra, preco_venda = info_ativos[ativo]['preco'], info_ativos[ativo]['preco']

                                    if row['Quantidade'] > 0:
                                        if not taxa:
                                            taxa = 0
                                        if not taxa_venda:
                                            taxa_venda = 0
                                        boletas.append({
                                            'Nº YMF': float(info_fundos[row['Fundo']]['codigo_brit']),
                                            'Fundo': row['Fundo'],
                                            'Cliente': info_fundos[row['Fundo']]['nome_cliente'],
                                            'Side': row['Side'],
                                            'Ativo': info_ativos[ativo]['tipo'],
                                            'Código': ativo,
                                            'Vencimento': info_ativos[ativo]['vencimento'],
                                            'Dt. Operac.': date.today(),
                                            'P.U.': preco_compra if row['Side'] == 'C' else preco_venda,
                                            'Quant.': row['Quantidade'],
                                            'R$': preco_compra * row['Quantidade'] if row['Side'] == 'C' else preco_venda * row['Quantidade'],
                                            'Contraparte': info_boletas[ativo]['Contraparte Ajuste'] if 'Tipo' in operacoes.columns and row['Tipo'] == 'Ajuste' else info_boletas[ativo]['Contraparte'],
                                            'Tipo': row['Tipo'] if 'Tipo' in operacoes.columns else 'Ajuste',
                                            'CNPJ': info_fundos[row['Fundo']]['cnpj'],
                                            'CETIP': info_fundos[row['Fundo']]['cetip'],
                                            'Custodiante': info_fundos[row['Fundo']]['custodiante'],
                                            'Taxa ': taxa/100 if row['Side'] == 'C' else taxa_venda/100,
                                            'Indexador': info_ativos[ativo]['indice'],
                                            'Emissor': info_ativos[ativo]['emissor'],
                                            'Rating': info_ativos[ativo]['rating'],
                                            'Duration ': duration_compra if row['Side'] == 'C' else duration_venda,
                                            'Spread ': spread_compra if row['Side'] == 'C' else spread_venda,
                                            'ISIN': info_ativos[ativo]['isin']
                                        })

                                df_boletas = pd.DataFrame(boletas)
                                boletas, contrapartes, df_exibicao, df_boletao = [], [], df_boletas.copy(deep=False), df_boletas.copy(deep=False)
                                df_boletao = df_boletao.drop(columns=['Rating', 'Fundo', 'Tipo'])
                                df_boletao = df_boletao.sort_values(['Código', 'Quant.', 'Side'], ascending=[True, True, True])
                                boletas.append(df_boletao)
                                contrapartes.append('Modelo Boletão')

                                for contraparte in set(df_boletas['Contraparte'].tolist()):
                                    if not contraparte:
                                        contraparte = 'Boleta'
                                        df = df_boletas
                                        df = df.drop(columns=['Spread ', 'Duration ', 'Fundo', 'Tipo'])
                                    else:
                                        df = df_boletas[df_boletas['Contraparte']== contraparte]
                                        df = df.drop(columns=['Spread ', 'Duration ', 'Fundo', 'Tipo'])
                                    df = df.sort_values(['Código', 'Quant.', 'Side'], ascending=[True, True, True])
                                    boletas.append(df)
                                    contrapartes.append(contraparte)

                                grupos = lista_grupos(db)
                                df_simulacao = df_simulacao.rename(columns={'pl_fundo': 'PL Alocável R$'})
                                for emissor in set(emissores):
                                    df_simulacao = df_simulacao.rename(columns={'novo_emissor'+emissor: 'Emissor '+emissor+' Objetivo %PL'})
                                    df_simulacao = df_simulacao.rename(columns={'novo_grupo'+emissor: 'Grupo '+grupos[emissor]+' Objetivo %PL'})
                                    df_simulacao['Emissor '+emissor+' Objetivo %PL'] = df_simulacao['Emissor ' +emissor+' Objetivo %PL'].apply(lambda x: x/100)

                                for grupo in set([grupos[emissor] for emissor in emissores]):
                                    df_simulacao['Grupo '+grupo+' Objetivo %PL'] = df_simulacao['Grupo ' + grupo+' Objetivo %PL'].apply(lambda x: x/100)

                                for ativo in ativos:
                                    df_simulacao = df_simulacao.rename(columns={'simulacao'+ativo: ativo+' Objetivo %PL'})
                                    df_simulacao[ativo+' Objetivo %PL'] = df_simulacao[ativo +' Objetivo %PL'].apply(lambda x: x/100)

                                df_simulacao = df_simulacao.loc[:, ~df_simulacao.columns.duplicated()].copy()
                                df_simulacao = df_simulacao[['Classe', 'Risco', 'Fundo', 'PL Alocável R$'] +
                                                            ['Grupo '+grupo+' Objetivo %PL' for grupo in set([grupos[emissor] for emissor in emissores])] +
                                                            ['Emissor '+emissor+' Objetivo %PL' for emissor in set(emissores)] +
                                                            [ativo+' Objetivo %PL' for ativo in ativos]]

                                boletas.append(df_simulacao)
                                contrapartes.append('Simulação')

                                st.subheader('Boletas')
                                df_exibicao['Taxa '] = df_exibicao['Taxa '].apply(lambda x: x*100)
                                def usar_chache_simulacao():
                                    if tipo_operacao == 'Ajuste Proporcional':
                                        st.session_state['dados_simulacao']['usar'] = True
                                    else:
                                        st.session_state['dados_simulacao']['usar'] = False

                                util.download_excel_button(
                                    boletas, 
                                    contrapartes, 
                                    'Download em Excel', 
                                    'Boleta', 
                                    onclick=usar_chache_simulacao
                                    )
                                gb = GridOptionsBuilder.from_dataframe(df_exibicao)
                                gb.configure_grid_options(
                                    enableRangeSelection=True, tooltipShowDelay=0)
                                gb.configure_grid_options(
                                    enableCellTextSelection=True)
                                gb = gb.build()
                                gb['columnDefs'] = [
                                    {'field': 'Nº YMF'}, 
                                    {'field': 'Fundo'}, 
                                    {'field': 'Cliente'},
                                    {'field': 'Side'}, 
                                    {'field': 'Ativo'}, 
                                    {'field': 'Código'},
                                    {'field': 'Vencimento', 'type': [
                                        "dateColumnFilter", "customDateTimeFormat"], 'custom_format_string': 'dd/MM/yyyy'},
                                    {'field': 'Dt. Operac.', 'type': [
                                        "dateColumnFilter", "customDateTimeFormat"], 'custom_format_string': 'dd/MM/yyyy'},
                                    {'field': 'P.U.',
                                        'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 6, minimumFractionDigits:6});",
                                        "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                                    {'field': 'Quant.',
                                        'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 0, minimumFractionDigits:0});",
                                        "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                                    {'field': 'R$',
                                        'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2});",
                                        "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                                    {'field': 'Contraparte'}, 
                                    {'field': 'Tipo'}, 
                                    {'field': 'CNPJ'}, 
                                    {'field': 'CETIP'}, 
                                    {'field': 'Custodiante'},
                                    {'field': 'Taxa ',
                                        'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 3, minimumFractionDigits:3})+ '%';",
                                        "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                                    {'field': 'Indexador'}, 
                                    {'field': 'Emissor'}, 
                                    {'field': 'Rating'},
                                    {'field': 'Duration ',
                                        'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2});",
                                        "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]},
                                    {'field': 'Spread ',
                                        'valueFormatter': "value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits:2})+ '%';",
                                        "type": ["numericColumn", "numberColumnFilter", "customNumericFormat"]}]
                                df_exibicao = AgGrid(
                                    df_exibicao, key='15',
                                    gridOptions=gb,
                                    reload_data=True,
                                    fit_columns_on_grid_load=False,
                                    custom_css=custom_css,
                                    update_mode='NO_UPDATE',
                                    allow_unsafe_jscode=True,
                                    enable_enterprise_modules=True)


            except:
                st.caption('Houve um erro')
        else:
            if calc:
                if op_incorreta:
                    col1, _ = st.columns([1, 4])
                    col1.error(msg)
                else:
                    st.caption('Preencha os dados corretamente')
