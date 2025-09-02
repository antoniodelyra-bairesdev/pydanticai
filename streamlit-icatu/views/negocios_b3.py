import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode
import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import requests
import plotly.express as px
import plotly.graph_objects as go
from models import secundario
from models import database
from views import util
from models import util as mutil
from environment import *
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR')


cores_graficos = ['#3fad23',
                  '#bef7b0',
                  '#8acce7',
                  '#a3c9df',
                  '#0D6696',
                  '#f57a2e',
                  '#b8b8b9']
formas_graficos = ['circle',
                   'circle',
                   'circle',
                   'circle',
                   'diamond',
                   'diamond',
                   'square']
ordem_tipos_transacoes_graficos = {'Tipo':
                                   ["Mercado", 
                                    "Mercado Contraparte", 
                                    "Direta", 
                                    "Direta Contraparte",
                                    "IV Mercado - C",
                                    "IV Mercado - V",
                                    "IV Ajuste"]}
tipos_vanguarda = {'IV Mercado - C',
                   'IV Mercado - V',
                   'IV Ajuste'}


def try_error(func):
    def wrapper(database):
        try:
            return func(database)
        except:
            st.caption('Houve um erro.')
    return wrapper


def converte_dados_dataframe(transacoes):
    dados_list = [{'data':i.data, 
                   'codigo': i.ativo.codigo,
                   'quantidade': i.quantidade,
                   'side': i.side,
                   'preco': i.preco,
                   'spread': i.spread*10000 if i.spread else None,
                   'tipo': i.tipo} 
                   for i in transacoes]
    df = pd.DataFrame(dados_list)
    if len(df) > 0:
        df = df.sort_values(by='data')
    return df

def apenda_negocios_vanguarda_b3(df_vanguarda, df_b3, rename_cols):
    df_vanguarda.rename(columns=rename_cols, inplace=True)
    df_vanguarda['Fonte'] = 'vanguarda'
    df_b3 = pd.concat([df_b3, df_vanguarda])
    df_b3.sort_values(by=['Data','Tipo'], inplace=True)  
    return df_b3


def ativos_unicos(database):
    sql = """ select distinct codigo from icatu.negocios_b3;
            """
    
    return [i['codigo'] for i in database.query(sql)]


def negocios_intervalo_ativo_mercado(ativo, 
                                     tipo_transacao, 
                                     data_inicio, 
                                     data_fim, 
                                     consulta_secundario
                                     ):
    """Consolida os dados de negócios de um ativo num período."""
    dados = consulta_secundario.consulta_historico_transacoes_mercado(ativo=ativo.strip(),
                                                                      data_inicio=data_inicio, 
                                                                      data_fim=data_fim
                                                                      )
    if dados:
        df = converte_dados_dataframe(dados.transacoes)
        if tipo_transacao == 'Todos':
            pass
        elif tipo_transacao == 'Mercado':
            df = df[df['tipo'] == tipo_transacao]
        elif tipo_transacao == 'Direta':
            df = df[df['tipo'].isin(['Direta','Ajuste'])]
        elif tipo_transacao == 'Sem Contraparte':
            df = df[df['tipo'].isin(['Mercado','Direta','Ajuste'])]

        if not df.empty:
            # Converter 'data' para datetime e considerar apenas o dia
            df['data'] = pd.to_datetime(df['data']).dt.date
            # Adicionar coluna de Volume Negociado
            df['Volume Negociado'] = df['quantidade'] * df['preco']
            return df
        else:
            st.error("Nenhum dado encontrado no intervalo especificado.")
            return None
    else:
        st.error(f"Erro ao acessar a API: {dados.status_code}")
        return None
    
def ajusta_tipos_vangaurda(transacoes):
    diretas = []
    mercado = []
    
    if transacoes:
        for i in transacoes:
            if i.tipo == 'Mercado': 
                i.tipo = 'IV Mercado - ' + i.side
                mercado.append(i)
            else: diretas.append(i)
        
        if diretas:
            diretas_sem_contraparte = []
            diretas = sorted(diretas, key=lambda x: (x.data, x.quantidade, x.preco))
            for i in range(len(diretas)):
                if i%2 == 0:
                    diretas[i].tipo = 'IV Ajuste'
                    diretas_sem_contraparte.append(diretas[i])

            transacoes = [*diretas_sem_contraparte, *mercado]
    

    return transacoes
    

def negocios_intervalo_ativo_vanguarda(ativo, 
                                       data_inicio, 
                                       data_fim, 
                                       tipo_transacao, 
                                       consulta_secundario
                                       ):

    dados = consulta_secundario.consulta_historico_transacoes_vanguarda(ativo=ativo, 
                                                                        data_inicio=data_inicio, 
                                                                        data_fim=data_fim)
    transacoes = dados.transacoes

    if dados:
        transacoes = ajusta_tipos_vangaurda(transacoes)
        if tipo_transacao == 'Mercado':
            transacoes = list(filter(lambda x: x.tipo in ['IV Mercado - C', 'IV Mercado - V'],transacoes))            
        elif tipo_transacao == 'Todos':
            pass
        elif tipo_transacao == 'Direta':
            transacoes = list(filter(lambda x: x.tipo == 'IV Ajuste', transacoes))
        elif tipo_transacao == 'Sem Contraparte':
            
            transacoes = list(filter(lambda x: x.tipo in ['IV Mercado - C', 'IV Mercado - V','IV Ajuste'],transacoes))
        df = converte_dados_dataframe(transacoes)
        
        if not df.empty:
            df['data'] = pd.to_datetime(df['data']).dt.date
            df['Volume Negociado'] = df['quantidade'] * df['preco']
            return df

    return None
    

def consolida_diario(df):
    df_new = pd.Series({
        'Volume Total': df['Volume Negociado'].sum(),
        'Spread Médio Ponderado': (df['Spread'] * df['Volume Negociado']).sum() / df['Volume Negociado'].sum(),
    })
    return df_new


def calcula_medias_moveis(df):
    tipos = df['Tipo'].unique()
    df_medias = pd.DataFrame()
    for tipo in tipos:
        df_temp = pd.DataFrame()
        df_temp= df[df.Tipo == tipo].groupby('Tipo').rolling(window=5).mean()
        df_medias= pd.concat([df_medias,df_temp])
    df_medias.rename(columns={'Spread Médio Ponderado':'Média Móvel 5 Dias'},inplace=True)
    df_medias.drop(columns=['Volume Total'],inplace=True)
    df.reset_index(inplace=True)
    df.set_index(['Data','Tipo'],inplace=True)
    df = df.merge(df_medias,how='left',left_index=True, right_index=True)
    df['Média Móvel 5 Dias - Agregado'] = df['Spread Médio Ponderado'].rolling(window=5).mean()
    
    return df

def taxa_indicativa_anbima(db, ativo, data_inicio):
    data_inicio = data_inicio.strftime('%Y-%m-%d')
    sql = f"""
    select data, codigo, spread*100 as spread from icatu.ativos_anbima aa
    where codigo = '{ativo}'
    and data >= '{data_inicio}'
    order by data desc;
    """

    df_anbima = None
    dados = db.query(sql)
    if dados:
        dados_list = [{'Data': i['data'],
                   'Código': i['codigo'],
                   'Indicativa Anbima': i['spread']} for i in dados]
        df_anbima = pd.DataFrame(dados_list)

    return df_anbima   


def resumo_por_tipo(df, du_periodo, tipo=None):
        if tipo:
            df_tipo = df[df['Tipo'] == tipo]
        else:
            tipo = 'Total'
            df_tipo = df

        dias_com_negociacao = df_tipo['Data'].nunique()
        total_volume_negociado = df_tipo['Volume Negociado'].sum()
        media_negociada_dias = total_volume_negociado / dias_com_negociacao if dias_com_negociacao > 0 else 0
        dia_mais_liquido = df_tipo.groupby('Data')['Volume Negociado'].sum().idxmax() if not df_tipo.empty else None
        maior_volume = df_tipo.groupby('Data')['Volume Negociado'].sum().max() if not df_tipo.empty else 0
        spread_maximo = df_tipo['Spread'].max() if not df_tipo.empty else None
        spread_minimo = df_tipo['Spread'].min() if not df_tipo.empty else None

        return {
            "Tipo": tipo,
            "Dias com negociação": dias_com_negociacao,
            "Dias úteis no período": du_periodo,
            "Volume Total": total_volume_negociado,
            "Média negociada nos dias com negócios": round(media_negociada_dias,2),
            "Dia com maior liquidez": dia_mais_liquido,
            "Maior Volume Negociado (R$)": round(maior_volume,2),
            "Spread Máximo": spread_maximo,
            "Spread Mínimo": spread_minimo
        }

@try_error
def negocios_b3(database):
    st.title("Análise de Negócios por Ativo")
    st.write("Insira os dados para consultar e analisar os negócios de um ativo.")

    hoje = date.today()
    consulta_secundario = secundario.ConsultaDadosSecundario(database,
                                                             ano_mes_ref_numerico=hoje.year*100+hoje.month)

    col1, col2 = st.columns([3, 2])
    with col1.form('form'):
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        data_inicio_valor = (date.today() - relativedelta(date.today, years=1))
        # Inputs do usuário
        lista_ativos = ativos_unicos(database)
        ativo = col1.selectbox("Selecione o Ativo", lista_ativos)
        data_inicio = col2.date_input("Data de início", value=data_inicio_valor)
        data_fim = col3.date_input("Data de fim")
        tipo_transacao = col4.selectbox("Tipo Transação", ['Sem Contraparte','Mercado','Direta','Todos'])
        consultar = st.form_submit_button("Consultar")


    du_periodo = mutil.contar_du(data_inicial=data_inicio, data_final=data_fim)
    # Botão para enviar a consulta
    if consultar:
        consolidado_dia = pd.DataFrame()
        consolidado_dia_tipo = pd.DataFrame()
        df_media_diaria = pd.DataFrame()
        df_medias = pd.DataFrame()
        st.cache_data.clear()

        if ativo and data_inicio and data_fim:
            with st.spinner("Consultando dados, por favor aguarde..."):
                df = negocios_intervalo_ativo_mercado(ativo=ativo, 
                                                      tipo_transacao=tipo_transacao, 
                                                      data_inicio=data_inicio, 
                                                      data_fim=data_fim,
                                                      consulta_secundario=consulta_secundario)
                df_vanguarda = negocios_intervalo_ativo_vanguarda(ativo=ativo, 
                                                                  data_inicio=data_inicio, 
                                                                  data_fim=data_fim, 
                                                                  tipo_transacao=tipo_transacao,
                                                                  consulta_secundario=consulta_secundario)
                
                if df is not None:
                    rename_cols = {'data': 'Data',
                                   'tipo': 'Tipo',
                                   'side': 'Side',
                                   'codigo': 'Código',
                                   'preco': 'Preço',
                                   'spread':'Spread',
                                   'quantidade': 'Quantidade'}
                    
                    df.rename(columns=rename_cols, inplace=True)
                    df['Fonte'] = 'b3'

                    if df_vanguarda is not None:
                        df = apenda_negocios_vanguarda_b3(df_vanguarda=df_vanguarda,
                                                          df_b3=df,
                                                          rename_cols=rename_cols)   


                    ### Dados Agrupados por Dia
                    consolidado_dia = df[df['Fonte'] == 'b3'].groupby('Data').apply(
                        lambda x: consolida_diario(x)
                    ).reset_index()


                    # Adicionar coluna de média móvel de 5 dias no Spread Médio Ponderado
                    consolidado_dia['Média Móvel 5 Dias'] = consolidado_dia['Spread Médio Ponderado'].rolling(window=5).mean()

                    consolidado_dia_tipo = df.groupby(['Data','Tipo'],as_index=False).apply(
                        lambda x: consolida_diario(x)
                    ).reset_index()
                    consolidado_dia_tipo.sort_values(by='Data', inplace=True)

                    consolidado_dia_tipo.sort_values(['Data'],inplace=True)
                    consolidado_dia_tipo.set_index(['Data'],inplace=True)

                    tipos = consolidado_dia_tipo['Tipo'].unique()
                    df_medias = pd.DataFrame()
                    for tipo in tipos:
                        df_temp = pd.DataFrame()
                        df_temp= consolidado_dia_tipo[consolidado_dia_tipo.Tipo == tipo].groupby('Tipo').rolling(window=5).mean()
                        df_medias= pd.concat([df_medias,df_temp])
                    df_medias.rename(columns={'Spread Médio Ponderado':'Média Móvel 5 Dias'},inplace=True)
                    df_medias.drop(columns=['Volume Total'],inplace=True)
                    consolidado_dia_tipo.reset_index(inplace=True)
                    consolidado_dia_tipo.set_index(['Data','Tipo'],inplace=True)
                    consolidado_dia_tipo = consolidado_dia_tipo.merge(df_medias,how='left',left_index=True, right_index=True)

                    df_media_diaria = consolidado_dia[['Data','Média Móvel 5 Dias']].set_index('Data')
                    df_media_diaria.rename(columns={'Média Móvel 5 Dias': 'Média Móvel 5 Dias - Agregado'}, inplace=True)


                    consolidado_dia_tipo.reset_index(inplace=True)
                    consolidado_dia_tipo.set_index('Data',inplace=True)
                    
                    consolidado_dia_tipo = consolidado_dia_tipo.merge(df_media_diaria, how='left', left_on='Data', right_on='Data')
                    consolidado_dia_tipo.reset_index(inplace=True)


                    # Gráfico de evolução do Spread com média móvel
                    st.write("### Gráfico: Evolução do Spread (Média Móvel de 5 Dias)")
                    
                    tipos_distintos = set(consolidado_dia_tipo['Tipo'].unique())
                    if len(tipos_distintos.intersection(tipos_vanguarda)) > 0:
                        consolidado_dia_tipo['Fonte_tamanho'] = consolidado_dia_tipo['Tipo'].map(lambda x: 15 if x in tipos_vanguarda else 3)
                        size_max = 15
                    else:
                        consolidado_dia_tipo['Fonte_tamanho'] = 0.1
                        size_max = 5
                    consolidado_dia_tipo['Volume Total  '] = consolidado_dia_tipo['Volume Total'].round(2).apply(lambda x: locale.format_string('%.2f',x,True))
                    consolidado_dia_tipo['Data  '] = consolidado_dia_tipo['Data'].apply(lambda x: x.strftime('%d/%m/%Y'))

                    
                    fig_spread = px.scatter(consolidado_dia_tipo, x='Data', 
                                            y='Spread Médio Ponderado',
                                            labels={'Spread Médio Ponderado': 'Spread (bps)',
                                                    'Data': 'Data'},title='Evolução do Spread',
                                                    size='Fonte_tamanho',
                                                    size_max=size_max,
                                                    color='Tipo',
                                                    symbol='Tipo',
                                                    symbol_sequence=formas_graficos,
                                                    hover_data={'Data  ': True,'Tipo': True,'Volume Total  ': True,'Spread Médio Ponderado': True, 'Fonte_tamanho': False, 'Data': False},
                                                    color_discrete_sequence=cores_graficos,
                                                    category_orders=ordem_tipos_transacoes_graficos)
                    

                    # Indicativa Anbima
                    df_anbima = taxa_indicativa_anbima(database, ativo, data_inicio)
                    if df_anbima is not None:
                        fig_spread.add_scatter(x=df_anbima['Data'], 
                                        y=df_anbima['Indicativa Anbima'], 
                                        mode='lines',
                                        line=dict(color='#F58C2E',width=5, dash='dot'),
                                        name='Indicativa Anbima')

                    fig_spread.add_scatter(x=consolidado_dia['Data'], 
                                        y=consolidado_dia['Média Móvel 5 Dias'], 
                                        mode='lines',
                                        line=dict(color='#F04F6E',width=5),
                                        name='Média Móvel 5 dias')
                    
                    

                    fig_spread.update_layout(hovermode='x unified')
                    st.plotly_chart(fig_spread, use_container_width=True)



                    ##### TABELA CONSOLIDADA POR DIA E TIPO NEGÓCIO
                    consolidado_dia_tipo_tabela = consolidado_dia_tipo[~consolidado_dia_tipo['Tipo'].isin(tipos_vanguarda)]
                    st.write("### Volume Negociado por Dia")


                    media_ponderada = JsCode("""
                                function media_ponderada(params) {
                                    let volumes = params.rowNode.allLeafChildren.map((x) => x.data['Volume Total']);
                                    let spread = params.rowNode.allLeafChildren.map((x) => x.data['Spread Médio Ponderado']);
                                    const [sum, weightSum] = volumes.reduce(
                                             (acc, w, i) => {
                                             acc[0] = acc[0] + spread[i] * w;
                                             acc[1] = acc[1] + w;
                                             return acc;
                                             },
                                             [0,0]
                                             );
                                             return sum / weightSum;                                    
                                }
                                """)
                    
                    media_movel_5_dias = JsCode("""
                                    function media_movel_5_dias(params) {
                                        var valor_agregado = params.rowNode.allLeafChildren.map((x) => x.data['Média Móvel 5 Dias - Agregado']);
                                        var valor = params.rowNode.rowGroupIndex === 1 ? params.rowNode.allLeafChildren[0].data['Média Móvel 5 Dias'] : valor_agregado[0];
                                            
                                        return  valor  ;
                                                }
                                            """)


                    gb = GridOptionsBuilder.from_dataframe(consolidado_dia_tipo_tabela)
                    gb.configure_grid_options(pivotMode=True)
                    gb.configure_grid_options(
                            autoGroupColumnDef=dict(
                                minWidth=300,
                                pinned="left",
                                cellRendererParams=dict(suppressCount=True)
                            )
                        )
                    gb.configure_column(field="Data", rowGroup=True, type=["dateColumnFilter", "customDateTimeFormat"], custom_format_string='dd/MM/yyyy')
                    gb.configure_column(field='Tipo', rowGroup=True)
                    gb.configure_column(
                                field='Volume Total',
                                type=["numericColumn"],
                                aggFunc="sum",
                                minWidth=200,
                                valueFormatter="value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})",
                            )
                    gb.configure_column(
                                field='Spread Médio Ponderado',
                                type=["numericColumn"],
                                header_name="Spread Médio Ponderado (bps)",
                                aggFunc="media_ponderada",
                                minWidth=200,
                                valueFormatter="value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})",
                            )
                    gb.configure_column(
                                field='Spread - Média Móvel 5 Dias',
                                header_name="Spread - Média Móvel 5 Dias (bps)",
                                type=["numericColumn"],
                                aggFunc="media_movel_5_dias",
                                minWidth=200,
                                valueFormatter="value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})",
                            )
                    
                    gb = gb.build()                      
                    gb['aggFuncs'] = {"media_ponderada": media_ponderada, "media_movel_5_dias": media_movel_5_dias}
                    gb['autoGroupColumnDef']['headerName'] = 'Data'
                    gb['suppressAggFuncInHeader'] = True

                    custom_css = {
                        ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                        ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                        ".ag-row":  {  "font-size": "16px !important;"}
                        }
                                  
                    
                    df_consolida_diario = AgGrid(
                        consolidado_dia_tipo_tabela,
                        gridOptions=gb,
                        reload_data=False,
                        fit_columns_on_grid_load=True,
                        custom_css=custom_css,
                        update_mode='VALUE_CHANGED',
                        allow_unsafe_jscode=True,
                        enable_enterprise_modules=True,
                    )

                    # Gráfico do Volume Negociado
                    fig_volume = px.bar(data_frame=consolidado_dia_tipo,
                                        x=consolidado_dia_tipo['Data'], 
                                        y=consolidado_dia_tipo['Volume Total'], 
                                        title='Volume Negociado por Dia',
                                        labels={'x':'Data','y': 'Volume Total'},
                                        color='Tipo',
                                        color_discrete_sequence=cores_graficos,
                                        category_orders=ordem_tipos_transacoes_graficos
                                        )
                    st.plotly_chart(fig_volume, use_container_width=True)

                    # Informações Resumidas
                    st.write("### Resumo de Informações (Por Tipo de Operação)")
                    if tipo_transacao == 'Todos':
                        tipos_operacao = ["Mercado", "Mercado Contraparte", "Direta", "Direta Contraparte"]
                    elif tipo_transacao == 'Sem Contraparte':
                        tipos_operacao = ["Mercado", "Direta"]
                    else: 
                        tipos_operacao = [tipo_transacao]

                    
                    resumo_geral = [resumo_por_tipo(df, du_periodo=du_periodo)] 
                    for tipo in tipos_operacao:
                        resumo_geral.append(resumo_por_tipo(df, du_periodo=du_periodo,tipo=tipo))

                    resumo_df = pd.DataFrame(resumo_geral)
                    gb = GridOptionsBuilder.from_dataframe(resumo_df)
                    gb.configure_column("Tipo", filter=True)
                    gb.configure_column("Dias com negociação",
                                        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                        valueFormatter="data['Dias com negociação'].toLocaleString('pt-BR',{minimumFractionDigits: 0, maximumFractionDigits: 0});")
                    gb.configure_column("Volume Total",
                                        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                        valueFormatter="data['Volume Total'].toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});")
                    gb.configure_column("Média negociada nos dias com negócios",
                                        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                        valueFormatter="data['Média negociada nos dias com negócios'].toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});")
                    gb.configure_column("Dia com maior liquidez", type=["dateColumnFilter", "customDateTimeFormat"], custom_format_string='dd/MM/yyyy')
                    gb.configure_column("Maior Volume Negociado (R$)",
                                        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                        valueFormatter="data['Maior Volume Negociado (R$)'].toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});")
                    gb.configure_column("Spread Máximo",
                                        header_name="Spread Máx (bps)",
                                        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                        valueFormatter="data['Spread Máximo'].toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});")
                    gb.configure_column("Spread Mínimo",
                                        header_name="Spread Mín (bps)",
                                        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                        valueFormatter="data['Spread Mínimo'].toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});")

                    custom_css = {
                        ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                        ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                        ".ag-row":  {  "font-size": "16px !important;"}
                        }

                    new_df = AgGrid(
                        resumo_df,
                        gridOptions=gb.build(),
                        update_mode='NO_UPDATE',
                        fit_columns_on_grid_load=True,
                        allow_unsafe_jscode=True,
                        enableRangeSelection=True,
                        custom_css=custom_css,
                        height=200,
                        enable_enterprise_modules=True)
                    

                    # Tabela Aberta por Transação
                    st.write("### Dados Abertos Por Transação")
                    gb = GridOptionsBuilder.from_dataframe(df[['Data','Código','Quantidade','Preço','Spread','Tipo','Volume Negociado']])
                    gb.configure_column("Tipo", filter=True)
                    gb.configure_column("Código", filter=True)
                    gb.configure_column("Data", type=["dateColumnFilter", "customDateTimeFormat"], custom_format_string='dd/MM/yyyy')

                    gb.configure_column("Preço",
                                        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                        valueFormatter="data.Preço.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});")
                    gb.configure_column(field="Spread",
                                        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                        header_name="Spread (bps)",
                                        valueFormatter="data.Spread.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});")
                    gb.configure_column("Volume Negociado",
                                        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                        valueFormatter="data['Volume Negociado'].toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2});")
                    gb.configure_column("Quantidade",
                                        type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
                                        valueFormatter="data['Quantidade'].toLocaleString('pt-BR',{maximumFractionDigits: 0, minimumFractionDigits: 0});")

                    custom_css = {
                        ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                        ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                        ".ag-row":  {  "font-size": "16px !important;"}
                        }

                    new_df = AgGrid(
                        df,
                        gridOptions=gb.build(),
                        update_mode='NO_UPDATE',
                        fit_columns_on_grid_load=True,
                        allow_unsafe_jscode=True,
                        enableRangeSelection=True,
                        custom_css=custom_css,
                        height=400,
                        enable_enterprise_modules=True)
                    

                    # Opção para download dos resultados como Excel
                    st.write("### Baixar Dados em Excel")
                    util.download_excel_button([df,consolidado_dia,resumo_df],
                                        ['Negócios Consolidados','Consolidado por Dia','Resumo por Tipo'],
                                        nome_arquivo=f'dados_{ativo}.xlsx',
                                        botao="Baixar Dados em Excel")
                    
        else:
            st.error("Por favor, preencha todos os campos para realizar a consulta.")