import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime
from views import util
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode
import plotly.express as px
import plotly.graph_objects as go

# --- Configuração ---
# Substitua com o seu URL base da API se for diferente
API_BASE_URL = "http://localhost:8000/carteira_fundos/holders_ativo/ativo="

# Endpoint para buscar os códigos de ativos
ASSET_CODES_URL = 'http://localhost:8000/carteira_fundos/ativos_unicos'

def try_error(func):
    def wrapper(database):
        try:
            return func(database)
        except:
            st.caption('Houve um erro.')
    return wrapper

@try_error
def asset_holders_page(database):
    """
    Renderiza a página Streamlit do Dashboard de Holders de Ativos Financeiros.
    Esta página permite aos usuários selecionar um código de ativo, visualizar seus detentores,
    ver a evolução de seu valor ao longo do tempo e fazer o download dos dados.
    """
    # --- Título da Página ---
    st.title("Holders Ativos")
    
    response = requests.get(ASSET_CODES_URL)
    response.raise_for_status()  # Levanta um HTTPError para respostas de erro
    ASSET_CODES = response.json()

    # --- Formulário de Seleção de Ativo ---
    st.header("Escolha o Ativo")
    with st.form("asset_selection_form"):
        selected_asset_code = st.selectbox(
            "Selecione o Código do Ativo:",
            options=ASSET_CODES,
            help="Selecione o código do ativo financeiro para ver seus detentores."
        )
        submit_button = st.form_submit_button("Consultar")

    # --- Exibição e Visualização de Dados ---
    # Busca e processa os dados apenas quando o formulário é submetido
    if submit_button and selected_asset_code:
        st.session_state['selected_asset_code'] = selected_asset_code
        api_url = f"{API_BASE_URL}{selected_asset_code}"

        try:
            # Busca dados da API
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            if data:
                # Converte para DataFrame e renomeia colunas
                df = pd.DataFrame(data)
                df.rename(columns={
                    'nome_gestor_ajustado': 'Gestor', 
                    'qtd_ativo': 'Quantidade', 
                    'valor_ativo': 'Financeiro', 
                    'codigo_ativo': 'Ativo', 
                    'data_carteira': 'Data Carteira',
                    'qtd_emissao': 'Quantidade Emissão'
                }, inplace=True)

                df['Perc Emissão'] = None
                df['Perc Emissão'] = df.apply(lambda row: (row['Quantidade'] / row['Quantidade Emissão']) if row['Quantidade Emissão'] and row['Quantidade Emissão'] != 0 else 0, axis=1)

                cols_order = ['Data Carteira', 'Gestor', 'Quantidade', 'Financeiro', 'Perc Emissão', 'Ativo']	
                df = df[cols_order]

                df['Gestor'] = df['Gestor'].fillna('Não Identificado')  # Remove espaços em branco extras
                
                # Converte 'Data Carteira' para datetime para ordenação
                df['Data Carteira'] = pd.to_datetime(df['Data Carteira'])
                # --- Ordenação e Pré-processamento ---
                # Ordena por Data Carteira descendente, Financeiro descendente
                df_sorted = df.sort_values(by=['Data Carteira', 'Financeiro'], ascending=[False, False])
                
                # Reordena colunas para colocar 'Data Carteira' no final
                cols = [col for col in df_sorted.columns if col != 'Data Carteira'] + ['Data Carteira']
                df_sorted = df_sorted[cols]

                # Armazena o dataframe processado no estado da sessão
                st.session_state['df_sorted'] = df_sorted
                
                # Agrega dados para o gráfico de linha e armazena
                df_monthly_value_per_holder = df.copy()
                df_monthly_value_per_holder['month_year'] = df_monthly_value_per_holder['Data Carteira'].dt.to_period('M')
                df_monthly_agg_per_holder = df_monthly_value_per_holder.groupby(['month_year', 'Gestor'])[['Financeiro', 'Perc Emissão']].sum().reset_index()
                df_monthly_agg_per_holder['month_year'] = df_monthly_agg_per_holder['month_year'].astype(str)
                st.session_state['df_monthly_agg_per_holder'] = df_monthly_agg_per_holder

            else:
                st.warning(f"Nenhum dado encontrado para o código de ativo: {selected_asset_code}. Por favor, verifique o código do ativo ou a resposta da API.")
                # Limpa o estado da sessão se nenhum dado for encontrado
                if 'df_sorted' in st.session_state:
                    del st.session_state['df_sorted']
                if 'df_monthly_agg_per_holder' in st.session_state:
                    del st.session_state['df_monthly_agg_per_holder']
                if 'selected_asset_code' in st.session_state:
                    del st.session_state['selected_asset_code']

        except requests.exceptions.ConnectionError:
            st.error("Erro de Conexão: Não foi possível conectar à API. Por favor, garanta que o servidor backend está rodando em `http://localhost:8000`.")
            if 'df_sorted' in st.session_state: del st.session_state['df_sorted']
        except requests.exceptions.Timeout:
            st.error("Erro de Tempo Limite: A requisição da API demorou muito para responder.")
            if 'df_sorted' in st.session_state: del st.session_state['df_sorted']
        except requests.exceptions.RequestException as e:
            st.error(f"Ocorreu um erro ao buscar os dados: {e}")
            if 'df_sorted' in st.session_state: del st.session_state['df_sorted']
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
            if 'df_sorted' in st.session_state: del st.session_state['df_sorted']
    elif submit_button and not selected_asset_code:
        st.warning("Por favor, selecione um código de ativo antes de consultar.")
    elif 'df_sorted' not in st.session_state:
        st.info("Selecione um código de ativo na lista e clique em 'Consultar' para visualizar as informações.")

    # --- Exibe os dados se estiverem no estado da sessão ---
    if 'df_sorted' in st.session_state:
        df_sorted = st.session_state['df_sorted']
        df_monthly_agg_per_holder = st.session_state['df_monthly_agg_per_holder']
        selected_asset_code = st.session_state['selected_asset_code']

        st.subheader(f"Ativo: {selected_asset_code}")

        # --- Exibição da Tabela com Separação Sutil de Mês ---
        st.markdown("### Posição Mensal Por Gestor")

        # --- AG-Grid Table ---
        gb = GridOptionsBuilder.from_dataframe(df_sorted)
        # Configura as colunas para agrupar por 'Data Carteira' e 'Gestor'
        gb.configure_column(
            field="Data Carteira",
            rowGroup=True,
            type=["dateColumnFilter", "customDateTimeFormat"],
            custom_format_string='dd/MM/yyyy',
            hide=True
        )
        gb.configure_column(field='Gestor')
        gb.configure_column(
            field='Quantidade',
            type=["numericColumn"],
            aggFunc="sum",
            minWidth=200,
            valueFormatter="value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})",
        )
        gb.configure_column(
            field='Perc Emissão',
            type=["numericColumn"],
            aggFunc="sum",
            minWidth=200,
            valueFormatter="`${(value * 100).toFixed(2)}%`",
        )
        gb.configure_column(
            field='Financeiro',
            type=["numericColumn"],
            aggFunc="sum",
            minWidth=200,
            valueFormatter="value.toLocaleString('pt-BR',{minimumFractionDigits: 2, maximumFractionDigits: 2})",
        )
        gb.configure_column(field='Ativo', aggFunc='first')
        # Configura a coluna de agrupamento automática
        gb.configure_grid_options(
            autoGroupColumnDef=dict(
                minWidth=300,
                pinned="left",
                cellRendererParams=dict(suppressCount=True)
            )
        )
        
        gridOptions = gb.build() 
        gridOptions['autoGroupColumnDef']['headerName'] = 'Data Carteira'
        gridOptions['suppressAggFuncInHeader'] = True

        custom_css = {
            ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
            ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
            ".ag-row":  { "font-size": "16px !important;"}
            }
        
        AgGrid(
            df_sorted,
            gridOptions=gridOptions,
            reload_data=False,
            fit_columns_on_grid_load=True,
            custom_css=custom_css,
            update_mode='VALUE_CHANGED',
            allow_unsafe_jscode=True,
            enable_enterprise_modules=True,
        )

        # --- Gráfico de Linha ---
        st.markdown("---") # Adiciona um separador
        st.markdown("### Evolução Mensal Holders")

        df_monthly_agg_per_holder['Perc Emissão (%)'] = (df_monthly_agg_per_holder['Perc Emissão']).apply(lambda x: f'{x * 100:.2f}%')
        df_monthly_agg_per_holder = df_monthly_agg_per_holder.sort_values('Financeiro', ascending=False)
        fig_holders = px.bar(
            data_frame=df_monthly_agg_per_holder,
            x='month_year',
            y='Financeiro',
            title='Clique sobre o nome do Gestor na legenda para excluir do gráfico. Dê dois cliques sobre o nome e isole-o no gráfico.',
            labels={'month_year': 'Mês/Ano', 'Financeiro': 'Valor Financeiro'},
            color='Gestor',
            hover_data={'Perc Emissão (%)': True}
        )
        st.plotly_chart(fig_holders, use_container_width=True)

        # --- Botão de Download ---
        st.markdown("---") # Adiciona um separador
        
        # Prepara o DataFrame para download em Excel
        df_sorted['Data Carteira'] = pd.to_datetime(df_sorted['Data Carteira'])
        df_sorted_for_excel = df_sorted.copy()
        df_sorted_for_excel['Data Carteira'] = df_sorted_for_excel['Data Carteira'].dt.date
        df_sorted_for_excel.rename(columns={'Data Carteira': 'Data'}, inplace=True)

        st.write("### Download Dados")
        util.download_excel_button([df_sorted_for_excel],
                                [f'Holders Ativos | {selected_asset_code}'],
                                nome_arquivo=f'holders_ativo_{selected_asset_code}',
                                botao="Baixar Dados em Excel")
