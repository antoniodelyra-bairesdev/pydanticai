from PIL import Image
import streamlit as st
from os import listdir
import os
import logging
import sys
import models.database as database
import models.notion as nt
import views.calculadora as cal
import views.indicadores as cd
import views.acompanhamento as ac
import views.rotinas as rt
import views.cadastro as cadastro
import views.gerencial as ge
import views.book_fundos 
import views.gerencial_previo as gp
import views.boletas as bo
import views.comite as comite
import views.mapa as mapa
import views.laminas as lm
import views.relatorio_fundos as rel
import views.negocios_b3 as b3
import views.holders_ativos as ha
from views import fatos_relevantes as fr
from views import assembleias
from environment import *


# Classe que duplica a saída: terminal + log
class DualStream:
    def __init__(self, stream1, stream2):
        self.stream1 = stream1  # geralmente sys.__stdout__
        self.stream2 = stream2  # logger

    def write(self, message):
        self.stream1.write(message)
        self.stream1.flush()

        if message.strip() and not message.isdigit():  # evita linhas desnecessárias
            logging.info(message.strip())

    def flush(self):
        self.stream1.flush()

# Configuração do logger
logging.basicConfig(
    filename="streamlit_app.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)

# Redireciona print() para DualStream (terminal + log)
sys.stdout = DualStream(sys.__stdout__, logging.getLogger())
sys.stderr = DualStream(sys.__stderr__, logging.getLogger())


st.set_page_config(
    page_title="Icatu Vanguarda",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

ip = env.IP

@st.cache_resource
def init_connection():
    return database.database(ip, application_name='streamlit')

db = init_connection()

notion_controller = nt.notion_service(db)

barra = st.sidebar
with barra:
    image = Image.open(r'assets\logo.png')
    st.image(image)
    st.text("")
    st.text("")
    option = st.selectbox(
        'Selecione o menu',
        ('Calculadora',
         'Relatório Gerencial',
         'Gerencial Prévio',
         'Indicadores Financeiros',
         'Banco de Dados',
         'Rotinas automáticas',
         'Relatórios do Power BI',
         'Simulação de Boletas',
         'Gerar Ata de Comitê',
         'Mapa do Sistema',
         'Fatos Relevantes',
         'Assembleias', 
         'Lâminas Mensais',
         'Relatório de Fundos',
         'Negócios B3',
         'Holders Ativos',
         'Book de Fundos'
         ))


if option == "Book de Fundos":
    views.book_fundos.book_fundos(barra, db)

if option == "Indicadores Financeiros":
    cd.indicadores(barra, db)

if option == "Assembleias":
    assembleias.assembleias(barra, db, notion_controller)

if option == "Fatos Relevantes":
    fr.fatos(barra, db, notion_controller)

if option == "Calculadora":
    cal.calculadora(barra, db)

if option == "Acompanhamento de Tarefas":
    ac.acompanhamento(barra)

if option == "Mapa do Sistema":
    mapa.mapa(barra)

if option == "Rotinas automáticas":
    rt.rotinas(barra, db, notion_controller)

if option == "Banco de Dados":
    cadastro.banco_dados(db, barra)

if option == "Relatório Gerencial":
    ge.relatorio(barra, db)

if option == "Gerencial Prévio":
    gp.gerencial_previo(barra, db)

if option == "Simulação de Boletas":
    bo.boletas(db)

if option == "Lâminas Mensais":
    lm.laminas(barra, db, notion_controller)

if option == "Relatório de Fundos":
    rel.relatorio_fundos(barra, db, notion_controller)

if option == "Negócios B3":
    b3.negocios_b3(db)

if option == 'Holders Ativos':
    ha.asset_holders_page(db)


if option == "Relatórios do Power BI":
    st.title('Relatórios do Power BI')
    st.markdown("""
            - [Relatório de Ratings](https://app.powerbi.com/reportEmbed?reportId=b06e174f-80c7-48f8-980c-20d225b919db&autoAuth=true&ctid=828d299c-d85c-4fc7-abf2-9c0724378d20&navContentPaneEnabled=false)
            - [Relatório de FIDCs](https://app.powerbi.com/reportEmbed?reportId=21202f06-be37-4d93-aca3-4012ecf1e136&autoAuth=true&ctid=828d299c-d85c-4fc7-abf2-9c0724378d20&navContentPaneEnabled=false)
            - [Relatório de Alocação](https://app.powerbi.com/reportEmbed?reportId=b259f358-e082-4f61-b71e-cacd84e41e3a&autoAuth=true&ctid=828d299c-d85c-4fc7-abf2-9c0724378d20&navContentPaneEnabled=false)
            - [Comparação de Portfólios dos Fundos](https://app.powerbi.com/reportEmbed?reportId=b0559159-ce16-45ab-9f28-395c5f2d8f96&autoAuth=true&ctid=828d299c-d85c-4fc7-abf2-9c0724378d20&navContentPaneEnabled=false)
            - [Distribuição de Empresas por Analistas](https://app.powerbi.com/reportEmbed?reportId=07d999ad-4877-4c70-bf20-d62925dac6ef&autoAuth=true&ctid=828d299c-d85c-4fc7-abf2-9c0724378d20&navContentPaneEnabled=false)
            - [Relatório de Compras e Vendas](https://app.powerbi.com/reportEmbed?reportId=0e0c77e9-d016-4ec6-8491-3832ceecc0fd&autoAuth=true&ctid=828d299c-d85c-4fc7-abf2-9c0724378d20&navContentPaneEnabled=false)
            - [Relatório de Bancos](https://app.powerbi.com/reportEmbed?reportId=178f06e1-fd0a-4e97-8e5c-090f847c0650&autoAuth=true&ctid=828d299c-d85c-4fc7-abf2-9c0724378d20&navContentPaneEnabled=false)
            - [Comparativo ISPs](https://app.powerbi.com/reportEmbed?reportId=f86cd26b-bf33-414b-94f3-f158f389c7f7&autoAuth=true&ctid=828d299c-d85c-4fc7-abf2-9c0724378d20&navContentPaneEnabled=false)
            - [Relatório de PnL](https://app.powerbi.com/reportEmbed?reportId=28159305-f496-4c18-a89e-d854e05234dd&autoAuth=true&ctid=828d299c-d85c-4fc7-abf2-9c0724378d20)
            - [Acompanhamento da Indústria](https://app.powerbi.com/reportEmbed?reportId=24998cb7-4c37-491d-bb9d-ff2dd9efebc9&autoAuth=true&ctid=828d299c-d85c-4fc7-abf2-9c0724378d20&navContentPaneEnabled=false)
            - [Mercado Secundário](https://app.powerbi.com/reportEmbed?reportId=aea731ec-338c-4d0f-88ea-be9a054f60b8&autoAuth=true&ctid=828d299c-d85c-4fc7-abf2-9c0724378d20&navContentPaneEnabled=false)
            """)

if option == "Gerar Ata de Comitê":
    comite.ata_comite(db)

