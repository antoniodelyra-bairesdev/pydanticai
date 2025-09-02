
import streamlit as st
from models import automacao
from models import util as mutil
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import re
from os import listdir
import xml.etree.ElementTree as ET
import os

def rotinas(barra, database, notion_controller):
    st.title("Rotinas automáticas")
    opcao = barra.radio('Selecione a opção', [
        'Relatório de Status',
        'Gerar Rotinas Manualmente',
        'Rotinas da Manhã',
        'Relatório de XMLs',
        'Fundos não Importados',
        'Validador de Dados',
    ], horizontal=True)

    if opcao == 'Validador de Dados':
        st.subheader('Validador de Dados')
        df = pd.DataFrame(database.query(
            'select nome, informacoes, status, atualizacao from icatu.rotinas'))
        df = df.rename(columns={'nome': 'Rotina', 'informacoes': 'Informações',
                       'status': 'Status', 'atualizacao': 'Último Horário'})
        df = df.sort_values(['Status', 'Último Horário'],
                            ascending=[True, False])
        df['Informações'] = df['Informações'].apply(
            lambda x: '' if not x else x)
        df['Último Horário'] = df['Último Horário'].apply(
            lambda x: x.strftime("%d/%m/%Y, %H:%M:%S"))

        rotinas_validador = [
            'Validar Coleta do Histórico CDI',
            'Validar ativos não cadastrados',
            'Validar cotas BD vs XMLs',
            'Validar cotas BD vs Comdinheiro',
            'Verificar XMLs duplicados da rede',
            'Validar Ativos Sem Estratégia',
            'Valida Ratings Duplicados',
            'Valida Coleta de Índices',
            'Validar Ativos sem ISIN',
            'Validar Ativos Sem Rating Interno',
            'Validar Calculadora',
            'Validar Importação da Alocação de FOFs e RV',
            'Validar Taxas dos Fundos Listados',
            'Validar Ativos Sem Spread',
            'Valida Setores Renda Variável - BD vs Planilha Rede',
            'Valida Classificação FOF - BD vs Planilha Rede',
            'Valida XML Vazio',
            'Validar Índices com Comdinheiro',
            'Validar Liquidação Compras',
            'Valida Ativos da Carteira Vanguarda sem Fluxo Cadastrado',
            'Validar Compras e Vendas - BD vs Planilha Histórico Boletão'
        ]
        df = df[df['Rotina'].isin(rotinas_validador)]
        hide_table_row_index = """
        <style>
        thead tr th:first-child {display:none}
        tbody th {display:none}
        thead th:nth-child(2){width: 20%}
        thead th:nth-child(3){width: 50%}
        thead th:nth-child(4){width: 10%}
        thead th:nth-child(5){width: 15%}
        </style>
        """
        st.markdown(hide_table_row_index, unsafe_allow_html=True)
        st.table(df)

    if opcao == 'Relatório de Status':
        st.subheader('Relatório de Status')
        df = pd.DataFrame(database.query('select nome, informacoes, status, atualizacao from icatu.rotinas'))
        df = df.rename(columns={'nome': 'Rotina', 'informacoes': 'Informações',
                       'status': 'Status', 'atualizacao': 'Último Horário'})
        df = df.sort_values(['Status', 'Último Horário'],
                            ascending=[True, False])
        df['Informações'] = df['Informações'].apply(lambda x: '' if not x else x)
        df['Último Horário'] = df['Último Horário'].apply(lambda x: x.strftime("%d/%m/%Y, %H:%M:%S"))

        hide_table_row_index = """
        <style>
        thead tr th:first-child {display:none}
        tbody th {display:none}
        thead th:nth-child(2){width: 20%}
        thead th:nth-child(3){width: 50%}
        thead th:nth-child(4){width: 10%}
        thead th:nth-child(5){width: 15%}
        </style>
        """
        st.markdown(hide_table_row_index, unsafe_allow_html=True)
        st.table(df)

    if opcao == 'Gerar Rotinas Manualmente':
        rotinas_manuais(database, notion_controller)

    if opcao == 'Rotinas da Manhã':
        rotinas_manha(database, None)

    if opcao == 'Relatório de XMLs':
        relatorio_xmls(database)

    if opcao == 'Fundos não Importados':
        estoque_fundos(database)


def try_error(func):
    def wrapper(database, notion=None):
        try:
            return func(database, notion)
        except Exception as erro:
            print(erro)
            st.caption('Houve um erro.')
    return wrapper


@try_error
def relatorio_xmls(database, notion=None):
    st.subheader('Relatório de XMLs Não Importados')
    col1, _ = st.columns([1, 8])
    data = col1.date_input('Selecione a data', mutil.somar_dia_util(date.today(), -1))
    if st.button('Verificar importação'):
        caminho = os.path.join(r"\\ISMTZVANGUARDA", 'Dir-GestaodeAtivos$', 'Controle', 'BackOffice', 'Caracteristicas Fundos Icatu Vanguarda.xls')
        ano = data.strftime('%Y')
        mes = data.strftime('%m')
        dia = data.strftime('%d')
        caminho_xmls = os.path.join(r'\\ISMTZVANGUARDA', 'Dir-GestaodeAtivos$', 'Controle', 'BackOffice', '01 - Atividades Diárias', '1.01 - XML', ano, mes, dia)

        st.write('Caminho: '+caminho_xmls[1:].replace(r'\ISMTZVANGUARDA\Dir-GestaodeAtivos$', "H:\\"))
        with st.spinner('Aguarde...'):
            df = pd.read_excel(caminho, sheet_name='Gestão Icatu')
            df = df[['Cód. Brit', 'ADMINISTRADOR', 'CUSTODIANTE','CNPJ', 'NOME DO FUNDO', 'Processamento']]
            df = df.rename(columns={'Cód. Brit': 'Código Brit', 'ADMINISTRADOR': 'Administrador',
                           'CUSTODIANTE': 'Custodiante', 'NOME DO FUNDO': 'Nome do Fundo'})
            df['CNPJ'] = df['CNPJ'].apply(
                lambda x: '0' * (14-len(''.join(re.findall(r"\d+", str(x))))) + ''.join(re.findall(r"\d+", str(x))))
            arquivos = [f for f in listdir(
                caminho_xmls) if f.lower().endswith(".xml")]
            cnpj_xmls = []
            for arquivo in arquivos:
                try:
                    xml = ET.parse(caminho_xmls + '\\' + arquivo).getroot()
                    fundo = xml[0].find('header')
                    cnpj_fundo = fundo.find('cnpj').text if fundo.find(
                        'cnpj') is not None else ""
                    cnpj_xmls.append(cnpj_fundo)
                except:
                    pass
            for ind, row in df.iterrows():
                if (row['CNPJ'] in cnpj_xmls or row['Código Brit'] == 'x'):
                    df = df.drop(ind)

            hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            thead th:nth-child(2){width: 10%}
            thead th:nth-child(3){width: 10%}
            thead th:nth-child(4){width: 10%}
            thead th:nth-child(5){width: 10%}
            thead th:nth-child(6){width: 60%}
            </style>
            """
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            df = pd.DataFrame(df)
            df = df.sort_values(['Custodiante'], ascending=[
                                True]).reset_index()
            df = df.drop(columns=['index'])
            st.table(df)


@try_error
def estoque_fundos(database, notion=None):
    query_fundos_expirados = " and (data_encerramento is null or data_encerramento >= current_date) "
    st.subheader('Relatório de Fundos não Importados')
    col1, _ = st.columns([1, 8])
    data = col1.date_input(
        'Selecione a data', mutil.somar_dia_util(date.today(), -1))
    
    ignorar = ['17453712000169']
    if st.button('Verificar importação'):
        caminho = os.path.join(r"\\ISMTZVANGUARDA", 
                               'Dir-GestaodeAtivos$', 
                               'Controle', 
                               'BackOffice', 
                               'Caracteristicas Fundos Icatu Vanguarda.xls')

        with st.spinner('Aguarde...'):
            df = pd.read_excel(caminho, sheet_name='Gestão Icatu')
            df = df[['Cód. Brit', 'ADMINISTRADOR', 'CUSTODIANTE',
                     'CNPJ', 'NOME DO FUNDO', 'Processamento']]
            df = df.rename(columns={'Cód. Brit': 'Código Brit', 'ADMINISTRADOR': 'Administrador',
                           'CUSTODIANTE': 'Custodiante', 'NOME DO FUNDO': 'Nome do Fundo'})
            df['Código Brit'] = df['Código Brit'].apply(lambda x: str(x).strip().replace('.0', ''))
            df['CNPJ'] = df['CNPJ'].apply(
                lambda x: '0' * (14-len(''.join(re.findall(r"\d+", str(x))))) + ''.join(re.findall(r"\d+", str(x))))
            
            fundos = {i['isin']: i['cnpj'] for i in database.query(
                f"select isin, cnpj from icatu.fundos where tipo is not null {query_fundos_expirados}")}
            cnpj_fundos = [i['cnpj'] for i in database.query(
                f"select isin, cnpj from icatu.fundos where codigo_brit not in ('6180', '6160', '6241', '6150') and tipo is not null {query_fundos_expirados}")]
            cnpj_importados = [fundos[i['fundo']] for i in database.query(
                f"select distinct fundo from icatu.estoque_ativos where data = '{data.strftime('%Y-%m-%d')}'")
                if i['fundo'] in fundos]

            for ind, row in df.iterrows():
                if ((row['CNPJ'] in cnpj_importados or row['Código Brit'] == 'x') or 
                    (row['CNPJ'] not in cnpj_fundos and str(row['Processamento']).strip() != 'Noturno') or 
                    row['CNPJ'] not in cnpj_fundos or
                    row['CNPJ'] in ignorar
                    ):
                    df = df.drop(ind)

            hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            thead th:nth-child(2){width: 10%}
            thead th:nth-child(3){width: 10%}
            thead th:nth-child(4){width: 10%}
            thead th:nth-child(5){width: 10%}
            thead th:nth-child(6){width: 60%}
            </style>
            """
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            df = pd.DataFrame(df)
            df['ordem'] = pd.Categorical(
                df['Custodiante'],
                categories=df[df['Custodiante'] != 'Bradesco']['Custodiante'].unique(
                ).tolist()+['Bradesco'],
                ordered=True
            )
            df = df.sort_values(['ordem'], ascending=[True]).reset_index()
            df = df.drop(columns=['ordem', 'index', 'Processamento'])
            st.table(df)


@try_error
def rotinas_manuais(database, notion_controller):
    st.subheader('Gerar rotinas manualmente')
    robos = st.multiselect('Selecione as rotinas automáticas',
                           [
                               'Curva DI',
                               'Curva NTN-B',
                               'Índices de mercado',
                               'Características das debêntures',
                               'Fluxo de debêntures',
                               'Correção manual das informações',
                               'Índices Anbima',
                               'Taxas Indicativas Anbima',
                               'Coletar XMLs Bradesco',
                               'Coletar XMLs Itaú',
                               'Coletar XMLs Daycoval',
                               'Coletar XMLs E-mail',
                               'Coletar XMLs Bradesco últimos 22 dias úteis',
                               'Coletar XMLs Bradesco últimos 44 dias úteis',
                               'Coletar planilhas BRIT',
                               'Importar XMLs',
                               'Importar planilhas BRIT',
                               'Coletar Ratings',
                               'Importar Ratings',
                               'Importar Taxas dos Ativos do Bradesco',
                               'Importar Taxas dos Ativos do Itaú',
                               'Coletar dados dos FIDCs',
                               'Coletar PL dos Emissores',
                               'Coletar ISIN da B3',
                               'Relatório de eventos (7 dias)',
                               'Relatório de eventos (360 dias)',
                               'Relatório de Eventos Completo',
                               'Calcular Taxas dos Ativos',
                               'Calcular Taxas dos FIDCs',
                               'Calcular Taxa VANG11',
                               'Calcular Taxa IVCI11',
                               'Coletar Taxas dos Bonds',
                               'Relatório de Alterações de Rating',
                               'Gerar Gerencial Prévio',
                               'Gerar Backup do Banco de Dados',
                               'Enviar E-mail das Carteiras',
                               'Enviar Carteiras Daycoval',
                               'Enviar E-mail de Taxas',
                               'Enviar E-mail de Taxas D-2',
                               'Calcular Rentabilidade',
                               'Coletar Dados dos FIIs',
                               'E-mail de divergência de preços',
                               'Atualizar Base de Dados de Bancos',
                               'Baixar Carteiras do Itaú',
                               'Gerar Planilha de Ratings',
                               'Calcular Preços Ajustados',
                               'Atualizar Ratings de Ativos Bancários',
                               'Gerar Explosão de Carteira',
                               'Limpar Cache do Streamlit',
                               'Rotina de Importação de XMLs',
                               'Calcular Taxas FIIs',
                               'Coletar LFs Anbima',
                               'Atualizar Emissões Notion',
                               'Atualizar Ratings Notion',
                               'Atualizar Emissores Notion',
                               'Salvar Infos do Notion no Banco',
                               'Salvar Documentos do Notion no Banco',
                               'Gerar Assembleias do período',
                               'Gerar Ratings Internos do período',
                               'Coletar Calls Ativa',
                               'Coletar Calls BGC',
                               'Coletar Calls Necton',
                               'E-mail de Ratings Expirados',
                               'Coletar Negócios B3',
                               'Salvar planilha de NTN-B na rede',
                               'Coletar Atividades RI',
                               'Coletar CIAS Abertas CVM',
                               'Enviar E-mails de Demandas do RI',
                               'Coletar Composicao IMAs',
                               'Coletar IHFA',
                               'Coletar IFIX e IBX da B3',
                               'Importar Alocação RV',
                               'Importar Classificação RV',
                               'Importar Alocação FOFs',
                               'Importar Classificação FOFs',
                               'Coletar taxa BDIF11',
                               'Atualizar Fundos RI',
                               'Coletar Histórico de Compras e Vendas',
                               'Validar Coleta do Histórico CDI',
                               'Rotinas de Validação',
                               'Validar ativos não cadastrados',
                               'Validar cotas BD vs XMLs',
                               'Validar cotas BD vs Comdinheiro',
                               'Atualizar Estratégia dos Ativos',
                               'Excluir XMLs duplicados da rede',
                               'Verificar XMLs duplicados da rede',
                               'Validar Ativos Sem Estratégia',
                               'Valida Ratings Duplicados',
                               'Valida Coleta de Índices',
                               'Validar Ativos sem ISIN',
                               'Salvar Planilha de Durations no Backoffice',
                               'Validar Ativos Sem Rating Interno',
                               'Validar Calculadora',
                               'Corrigir Transações Vanguarda na Tabela Negócios B3',
                               'Coletar XMLs Bradesco D0 e D1',
                               'Coletar XMLs Itaú D0 e D1',
                               'Validar Importação da Alocação de FOFs e RV',
                               'Calcular Taxas Fundos Listados 5du',
                               'Validar Taxas dos Fundos Listados',
                               'E-mail Eventos Verificar PU',
                               'Validar Ativos Sem Spread',
                               'Valida Setores Renda Variável - BD vs Planilha Rede',
                               'Valida Classificação FOF - BD vs Planilha Rede',
                               'Valida XML Vazio',
                               'Excluir XML Vazio',
                               'Validar Índices com Comdinheiro',
                               'Coletar XMLs Bradesco do Ano Inteiro',
                               'Coletar XMLs Itaú últimos 22 dias úteis',
                               'Coletar XMLs Itaú últimos 44 dias úteis',
                               'Salvar Planilha Ativos Securitizados - Enquadramento',
                               'Coletar XMLs Daycoval do Ano Inteiro',
                               'Enviar E-mail Últimos Documentos CVM',
                               'Alerta de Basiléia - Fundo IRB CDI',
                               'Valida Relatório Fundos',
                               'Validar Liquidação Compras',
                               'Derrubar Conexões Inativas do Banco de Dados',
                               'Gerar Mapa de Crédito',
                               'Cadastrar Ativos Parcerias Icatu Seguros',
                               'Salvar planilha de emissores bancários na rede',
                               'Gerar Lâminas para o Itaú',
                               'Valida Ativos da Carteira Vanguarda sem Fluxo Cadastrado',
                               'Calcular Dados BI Secundário',
                               'Salvar Planilha Emissores Bancários - Backoffice',
                               'Salvar Planilha FI Analytics na Rede',
                               'Coletar Holders Ativos com Dinheiro',
                               'Salvar Planilha Negócios B3 - Rede',
                               'Validar Compras e Vendas - BD vs Planilha Histórico Boletão'
                           ])

    executar_indices = st.button("Executar")
    df = pd.DataFrame(list(
                        zip(
                            robos, 
                            ["" for _ in range(len(robos))], 
                            ["" for _ in range(len(robos))]
                            )
                        ), 
                    columns=['Descrição', 'Informações', 'Status'])
    hide_table_row_index = """
    <style>
    thead tr th:first-child {display:none}
    tbody th {display:none}
    thead th:nth-child(2){width: 30%}
    thead th:nth-child(3){width: 60%}
    </style>
    """
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    tabela = st.empty()
    if len(df.index) > 0:
        tabela.table(df)
    if executar_indices:
        for rotina in robos:
            atualizar_status(rotina, df, tabela, database, notion_controller)


@try_error
def rotinas_manha(database, notion=None):
    st.subheader('Rotinas para o dia '+date.today().strftime('%d/%m/%Y'))

    df = pd.DataFrame(database.query(
        'select nome, status, informacoes, atualizacao from icatu.rotinas'))
    df = df.rename(columns={'nome': 'Rotina', 'informacoes': 'Informações',
                   'status': 'Status', 'atualizacao': 'Último Horário'})
    df = df.sort_values(['Status', 'Último Horário'], ascending=[True, False])
    df['Informações'] = df['Informações'].apply(lambda x: '' if not x else x)
    df['Último Horário'] = df['Último Horário'].apply(
        lambda x: x.strftime("%d/%m/%Y, %H:%M:%S"))

    tabela = []
    rotinas = [
        'Coletar XMLs Bradesco',
        'Coletar XMLs Itaú',
        'Coletar XMLs E-mail',
        'Importar XMLs',
        'Excluir XMLs duplicados da rede',
        'E-mail de divergência de preços',
        'Gerar Explosão de Carteira',
        'Curva DI',
        'Curva NTN-B',
        'Salvar planilha de NTN-B na rede',
        'Índices de mercado',
        'Características das debêntures',
        'Fluxo de debêntures',
        'Correção manual das informações',
        'Índices Anbima',
        'Taxas Indicativas Anbima',
        'Importar Taxas dos Ativos do Bradesco',
        'Coletar Taxas dos Bonds',
        'Calcular Taxas dos FIDCs',
        'Calcular Taxas dos Ativos',
        'Coletar Dados dos FIIs',
        'Calcular Taxas FIIs',
        'Coletar taxa BDIF11',
        'Enviar E-mail de Taxas',
        'Calcular Preços Ajustados',
        'Calcular Rentabilidade',
        'Gerencial Prévio',
        'Coletar ISIN da B3',
        'Relatório de eventos (360 dias)',
        'Relatório de Eventos Completo',
        'Atualizar Ratings de Ativos Bancários',
        'Coletar LFs Anbima',
        'Coletar Calls Ativa',
        'Coletar Calls BGC',
        'Coletar Calls Necton',
        'Coletar CIAS Abertas CVM',
        'Enviar E-mails de Demandas do RI',
        'Atualizar Estratégia dos Ativos',
        'Salvar Planilha de Durations no Backoffice',
        'E-mail Eventos Verificar PU',
        'Alerta de Basiléia - Fundo IRB CDI',
        'Derrubar Conexões Inativas do Banco de Dados',
        'Salvar planilha de emissores bancários na rede',
        'Salvar Planilha Emissores Bancários - Backoffice',
        'Salvar Planilha FI Analytics na Rede',
        'Coletar Histórico de Compras e Vendas',
        'Coletar Negócios B3',
        'Salvar Planilha Negócios B3 - Rede',
        'Calcular Dados BI Secundário'
    ]

    df = df[df['Rotina'].isin(rotinas)]
    for ind, row in df.iterrows():
        rotina = row['Rotina']
        horario = datetime.strptime(row['Último Horário'], '%d/%m/%Y, %H:%M:%S').date()
        if not horario == date.today():
            df.at[ind, 'Status'] = 'Pendente'
            df.at[ind, 'Informações'] = ''
            df.at[ind, 'Último Horário'] = ''

    gerar = st.button('Rodar rotinas')

    hide_table_row_index = """
    <style>
    thead tr th:first-child {display:none}
    tbody th {display:none}
    thead th:nth-child(2){width: 30%}
    thead th:nth-child(3){width: 10%}
    thead th:nth-child(4){width: 45%}
    thead th:nth-child(5){width: 15%}
    </style>
    """
    st.markdown(hide_table_row_index, unsafe_allow_html=True)

    tabela = df
    tabela['ordem'] = pd.Categorical(
        tabela['Rotina'],
        categories=rotinas,
        ordered=True
    )
    tabela = tabela.sort_values(['ordem'], ascending=[True]).reset_index()
    tabela = tabela.drop(columns=['ordem', 'index'])
    relatorio = st.table(tabela)
    if gerar:
        for i in range(len(rotinas)):
            rotina = rotinas[i]
            if i == 0 and tabela[tabela['Rotina'] == rotina]['Status'].tolist()[0] != 'OK':
                tabela = atualizar_rotina_manha(relatorio, rotina, tabela, database)
            elif (i > 0 and tabela[tabela['Rotina'] == rotinas[i-1]]['Status'].tolist()[0] == 'OK'
                  and tabela[tabela['Rotina'] == rotina]['Status'].tolist()[0] != 'OK'):
                tabela = atualizar_rotina_manha(relatorio, rotina, tabela, database)
            else:
                pass


def atualizar_rotina_manha(relatorio, rotina, tabela, database):
    tabela.loc[tabela.index[tabela['Rotina'] == rotina][0], ['Status']] = 'Executando'
    tabela.loc[tabela.index[tabela['Rotina'] == rotina][0], ['Último Horário']] = ''
    tabela.loc[tabela.index[tabela['Rotina'] == rotina][0], ['Informações']] = ''
    relatorio.empty()
    relatorio.table(tabela)

    if rotina == 'Curva DI':
        status, informacao = automacao.get_curva_di_b3(database)
    if rotina == 'Curva NTN-B':
        status, informacao = automacao.get_curva_ntnb(database)
    if rotina == 'Índices de mercado':
        status, informacao = automacao.get_tabela_anbima(database)
    if rotina == 'Características das debêntures':
        status, informacao = automacao.get_info_debentures_anbima(database, rodar_correcao=True)
    if rotina == 'Fluxo de debêntures':
        status, informacao = automacao.get_fluxo_debentures(database, rodar_correcao=True)
    if rotina == 'Correção manual das informações':
        status, informacao = automacao.correcao_manual(database)
    if rotina == 'Índices Anbima':
        status, informacao = automacao.get_indices_anbima(database)
    if rotina == 'Taxas Indicativas Anbima':
        status, informacao = automacao.get_taxas_indicativas_anbima(database)
    if rotina == 'Coletar XMLs Bradesco':
        status, informacao = automacao.coletar_xml_bradesco()
    if rotina == 'Coletar XMLs Daycoval':
        status, informacao = automacao.coletar_xml_daycoval()
    if rotina == 'Coletar XMLs Itaú':
        status, informacao = automacao.coletar_xml_itau()
    if rotina == 'Coletar XMLs E-mail':
        status, informacao = automacao.coletar_xmls_email()
    if rotina == 'Importar XMLs':
        status, informacao = automacao.importar_xml(database)
    if rotina == 'Relatório de eventos (360 dias)':
        status, informacao = automacao.proximos_eventos_360dias(database, mutil.somar_dia_util(date.today(), -1))
    if rotina == 'Relatório de Eventos Completo':
        status, informacao = automacao.proximos_eventos_completo(database, mutil.somar_dia_util(date.today(), -1))
    if rotina == 'Calcular Taxas dos Ativos':
        status, informacao = automacao.calcular_taxa_ativos(mutil.somar_dia_util(date.today(), -1), database)
    if rotina == 'Importar Taxas dos Ativos do Bradesco':
        status, informacao = automacao.coletar_taxas_bradesco(database)
    if rotina == 'Gerencial Prévio':
        status, informacao = automacao.gerencial_previo(mutil.somar_dia_util(date.today(), -1), database)
    if rotina == 'Coletar ISIN da B3':
        status, informacao = automacao.coletar_isin_b3()
    if rotina == 'Coletar Taxas dos Bonds':
        status, informacao = automacao.coletar_taxas_bonds(database)
    if rotina == 'Enviar E-mail de Taxas':
        status, informacao = automacao.enviar_email_taxas(database)
    if rotina == 'Calcular Rentabilidade':
        status, informacao = automacao.calcular_rentabilidade(mutil.somar_dia_util(date.today(), -1), database)
    if rotina == 'Calcular Taxas dos FIDCs':
        status, informacao = automacao.taxas_fidcs(mutil.somar_dia_util(date.today(), -1), database)
    if rotina == 'Gerar Explosão de Carteira':
        status, informacao = automacao.gerar_explosao_carteira(database)
    if rotina == 'Calcular Taxas FIIs':
        status, informacao = automacao.taxas_fiis(database, mutil.somar_dia_util(date.today(), -1))
    if rotina == 'Atualizar Ratings de Ativos Bancários':
        status, informacao = automacao.atualizar_ratings_bancarios(database)
    if rotina == 'Coletar Dados dos FIIs':
        status, informacao = automacao.coletar_fii(database, mutil.somar_dia_util(date.today(), -22), date.today())
    if rotina == 'Calcular Preços Ajustados':
        status, informacao = automacao.calcular_preco_ajustado(database, 
                                                               mutil.somar_dia_util(date.today(), -10), 
                                                               mutil.somar_dia_util(date.today(), -1))
    if rotina == 'Coletar LFs Anbima':
        status, informacao = automacao.coletar_lfs_anbima(mutil.somar_dia_util(date.today(), -1))
    if rotina == 'Coletar Calls Ativa':
        status, informacao = automacao.coletar_calls_ativa(database)
    if rotina == 'Coletar Calls BGC':
        status, informacao = automacao.coletar_calls_bgc(database)
    if rotina == 'Coletar Calls Necton':
        status, informacao = automacao.coletar_calls_necton(database)
    if rotina == 'Coletar Negócios B3':
        status, informacao = automacao.coletar_negocios_b3(database)
    if rotina == 'Salvar planilha de NTN-B na rede':
        status, informacao = automacao.gerar_planilha_ntnb_rede(database)
    if rotina == 'Coletar CIAS Abertas CVM':
        status, informacao = automacao.coletar_cias_abertas_cvm(database)
    if rotina == 'E-mail de divergência de preços':
        status, informacao = automacao.email_divergencia_precos(database, mutil.somar_dia_util(date.today(), -1))
    if rotina == 'Enviar E-mails de Demandas do RI':
        status, informacao = automacao.enviar_email_demandas_ri(database)
    if rotina == 'Coletar taxa BDIF11':
        status, informacao = automacao.coletar_taxa_bdif11(database)
    if rotina == 'Atualizar Fundos RI':
        status, informacao = automacao.atualizar_fundos_atividades_ri(database)
    if rotina == 'Excluir XMLs duplicados da rede':
        status, informacao = automacao.excluir_xmls_duplicados(10)
    if rotina == 'Atualizar Estratégia dos Ativos':
        status, informacao = automacao.atualizar_estrategia_ativos(database)
    if rotina == 'Salvar Planilha de Durations no Backoffice':
        status, informacao = automacao.salvar_taxas_backoffice(database)
    if rotina == 'E-mail Eventos Verificar PU':
        status, informacao = automacao.enviar_email_eventos_verificar_pu(database)
    if rotina == 'Alerta de Basiléia - Fundo IRB CDI':
        status, informacao = automacao.alerta_basileia_irb(database)
    if rotina == 'Valida Relatório Fundos':
        status, informacao = automacao.valida_relatorio_fundos(database)
    if rotina == 'Derrubar Conexões Inativas do Banco de Dados':
        status, informacao = automacao.derrubar_conexoes_inativas(database)
    if rotina == 'Salvar planilha de emissores bancários na rede':
        status, informacao = automacao.salvar_planilha_bancos_rede(database)
    if rotina == 'Calcular Dados BI Secundário':
        status, informacao = automacao.secundario_calcula_dados_bi(database)
    if rotina == 'Salvar Planilha Emissores Bancários - Backoffice':
        status, informacao = automacao.salvar_planilha_emissores_bancarios_backoffice(database)
    if rotina == 'Salvar Planilha FI Analytics na Rede':
        status, informacao = automacao.salvar_planilha_fi_analytics_rede()
    if rotina == 'Salvar Planilha Negócios B3 - Rede':
        status, informacao = automacao.salvar_planilha_negocios_b3_rede(database)
    if rotina == 'Coletar Histórico de Compras e Vendas':
        status, informacao = automacao.coletar_historico_compras_vendas(database)


    tabela.loc[tabela.index[tabela['Rotina'] == rotina][0], ['Status']] = status
    tabela.loc[tabela.index[tabela['Rotina'] == rotina][0], ['Informações']] = informacao
    tabela.loc[tabela.index[tabela['Rotina'] == rotina][0], ['Último Horário']] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    relatorio.empty()
    relatorio.table(tabela)
    return tabela


def atualizar_status(rotina, 
                     df, 
                     tabela, 
                     database, 
                     notion_controller=None
                     ):

    df.loc[df.index[df['Descrição'] == rotina][0], ['Status']] = 'Executando'
    tabela.empty()
    tabela.table(df)

    if rotina == 'Curva DI':
        status, informacao = automacao.get_curva_di_b3(database)
    if rotina == 'Curva NTN-B':
        status, informacao = automacao.get_curva_ntnb(database)
    if rotina == 'Índices de mercado':
        status, informacao = automacao.get_tabela_anbima(database)
    if rotina == 'Características das debêntures':
        status, informacao = automacao.get_info_debentures_anbima(database, rodar_correcao=True)
    if rotina == 'Fluxo de debêntures':
        status, informacao = automacao.get_fluxo_debentures(database, rodar_correcao=True)
    if rotina == 'Correção manual das informações':
        status, informacao = automacao.correcao_manual(database)
    if rotina == 'Índices Anbima':
        status, informacao = automacao.get_indices_anbima(database)
    if rotina == 'Taxas Indicativas Anbima':
        status, informacao = automacao.get_taxas_indicativas_anbima(database)
    if rotina == 'Coletar XMLs Bradesco':
        status, informacao = automacao.coletar_xml_bradesco()
    if rotina == 'Coletar XMLs Daycoval':
        status, informacao = automacao.coletar_xml_daycoval()
    if rotina == 'Coletar XMLs Itaú':
        status, informacao = automacao.coletar_xml_itau()
    if rotina == 'Coletar XMLs E-mail':
        status, informacao = automacao.coletar_xmls_email()
    if rotina == 'Coletar XMLs Bradesco últimos 22 dias úteis':
        status, informacao = automacao.coletar_xml_bradesco_22du()
    if rotina == 'Coletar XMLs Bradesco últimos 44 dias úteis':
        status, informacao = automacao.coletar_xml_bradesco_44du()
    if rotina == 'Coletar planilhas BRIT':
        status, informacao = automacao.coletar_dados_brit()
    if rotina == 'Importar XMLs':
        status, informacao = automacao.importar_xml(database)
    if rotina == 'Importar planilhas BRIT':
        status, informacao = automacao.importar_dados_brit(database)
    if rotina == 'Relatório de eventos (7 dias)':
        status, informacao = automacao.enviar_email_eventos(database)
    if rotina == 'Relatório de eventos (360 dias)':
        status, informacao = automacao.proximos_eventos_360dias(database, mutil.somar_dia_util(date.today(), -1))
    if rotina == 'Relatório de Eventos Completo':
        status, informacao = automacao.proximos_eventos_completo(database, mutil.somar_dia_util(date.today(), -1))
    if rotina == 'Coletar Ratings':
        status, informacao = automacao.coletar_ratings(database)
    if rotina == 'Importar Ratings':
        status, informacao = automacao.importar_ratings(database)
    if rotina == 'Relatório de Alterações de Rating':
        status, informacao = automacao.enviar_email_ratings(database)
    if rotina == 'Calcular Taxas dos Ativos':
        status, informacao = automacao.calcular_taxa_ativos(mutil.somar_dia_util(date.today(), -1), database)
    if rotina == 'Importar Taxas dos Ativos do Bradesco':
        status, informacao = automacao.coletar_taxas_bradesco(database)
    if rotina == 'Importar Taxas dos Ativos do Itaú':
        for i in range(5):
            status, informacao = automacao.coletar_taxas_itau(mutil.somar_dia_util(date.today(), -(i+1)), database)
    if rotina == 'Coletar dados dos FIDCs':
        status, informacao = automacao.coletar_dados_fidcs(database)
    if rotina == 'Gerar Gerencial Prévio':
        status, informacao = automacao.gerencial_previo(mutil.somar_dia_util(date.today(), -1), database)
    if rotina == 'Coletar PL dos Emissores':
        status, informacao = automacao.coletar_patrimonio_liquido(database)
    if rotina == 'Gerar Backup do Banco de Dados':
        status, informacao = automacao.gerar_backup_db()
    if rotina == 'Enviar E-mail das Carteiras':
        status, informacao = automacao.enviar_email_carteiras(database)
    if rotina == 'Coletar ISIN da B3':
        status, informacao = automacao.coletar_isin_b3()
    if rotina == 'Coletar Taxas dos Bonds':
        status, informacao = automacao.coletar_taxas_bonds(database)
    if rotina == 'Calcular Taxas dos FIDCs':
        status, informacao = automacao.taxas_fidcs(mutil.somar_dia_util(date.today(), -1), database)
    if rotina == 'Enviar E-mail de Taxas':
        status, informacao = automacao.enviar_email_taxas(database)
    if rotina == 'Enviar E-mail de Taxas D-2':
        data = mutil.somar_dia_util(date.today(), -2)
        status, informacao = automacao.enviar_email_taxas(database,data)
    if rotina == 'Calcular Rentabilidade':
        status, informacao = automacao.calcular_rentabilidade(mutil.somar_dia_util(date.today(), -1), database)
    if rotina == 'Coletar Dados dos FIIs':
        status, informacao = automacao.coletar_fii(database, mutil.somar_dia_util(date.today(), -22), date.today())
    if rotina == 'E-mail de divergência de preços':
        status, informacao = automacao.email_divergencia_precos(database)
    if rotina == 'Atualizar Base de Dados de Bancos':
        status, informacao = automacao.atualizar_indicadores_bancos(database)
    if rotina == 'Baixar Carteiras do Itaú':
        status, informacao = automacao.coletar_carteiras_itau()
    if rotina == 'Gerar Planilha de Ratings':
        status, informacao = automacao.gerar_planilha_rating(database)
    if rotina == 'Atualizar Ratings de Ativos Bancários':
        status, informacao = automacao.atualizar_ratings_bancarios(database)
    if rotina == 'Calcular Preços Ajustados':
        status, informacao = automacao.calcular_preco_ajustado(database, 
                                                               mutil.somar_dia_util(date.today(), -10), 
                                                               mutil.somar_dia_util(date.today(), -1))
    if rotina == 'Calcular Taxas FIIs':
        status, informacao = automacao.taxas_fiis(database, mutil.somar_dia_util(date.today(), -1))
    if rotina == 'Gerar Explosão de Carteira':
        status, informacao = automacao.gerar_explosao_carteira(database)
    if rotina == 'Limpar Cache do Streamlit':
        st.cache_resource.clear()
        status, informacao = 'OK', ''
    if rotina == 'Rotina de Importação de XMLs':
        status, informacao = automacao.rotina_xml(database)
    if rotina == 'Coletar LFs Anbima':
        status, informacao = automacao.coletar_lfs_anbima(mutil.somar_dia_util(date.today(), -1))
    if rotina == 'Atualizar Emissões Notion':
        status, informacao = automacao.atualizar_emissoes_notion(database)
    if rotina == 'Atualizar Ratings Notion':
        status, informacao = automacao.atualizar_ratings_notion(database)
    if rotina == 'Atualizar Emissores Notion':
        status, informacao = automacao.atualizar_emissores_notion(database)
    if rotina == 'Salvar Infos do Notion no Banco':
        status, informacao = automacao.salvar_infos_notion(database)
    if rotina == 'Salvar Documentos do Notion no Banco':
        status, informacao = automacao.salvar_documentos_notion(database)
    if rotina == 'Gerar Assembleias do período':
        hoje = date.today()
        data_fim = datetime(hoje.year, hoje.month, 1).date()
        data_fim = mutil.somar_dia_util(data_fim, -1)
        data_inicio = datetime(data_fim.year, data_fim.month, 1).date()
        status, informacao = automacao.gerar_assembleias(database, data_inicio, data_fim)
    if rotina == 'Gerar Ratings Internos do período':
        hoje = date.today()
        data_fim = datetime(hoje.year, hoje.month, 1).date()
        data_fim = mutil.somar_dia_util(data_fim, -1)
        data_inicio = datetime(data_fim.year, data_fim.month, 1).date()
        status, informacao = automacao.gerar_ratings_internos(database, data_inicio, data_fim)
    if rotina == 'Coletar Calls Ativa':
        status, informacao = automacao.coletar_calls_ativa(database)
    if rotina == 'Coletar Calls BGC':
        status, informacao = automacao.coletar_calls_bgc(database)
    if rotina == 'Coletar Calls Necton':
        status, informacao = automacao.coletar_calls_necton(database)
    if rotina == 'E-mail de Ratings Expirados':
        status, informacao = automacao.ratings_expirados(database)
    if rotina == 'Coletar Negócios B3':
        status, informacao = automacao.coletar_negocios_b3(database)
    if rotina == 'Salvar planilha de NTN-B na rede':
        status, informacao = automacao.gerar_planilha_ntnb_rede(database)
    if rotina == 'Coletar Atividades RI':
        status, informacao = automacao.coletar_atividades_ri(database)
    if rotina == 'Coletar CIAS Abertas CVM':
        status, informacao = automacao.coletar_cias_abertas_cvm(database)
    if rotina == 'Enviar Carteiras Daycoval':
        status, informacao = automacao.enviar_carteiras_daycoval(mutil.somar_dia_util(date.today(), -1))
    if rotina == 'Enviar E-mails de Demandas do RI':
        status, informacao = automacao.enviar_email_demandas_ri(database)
    if rotina == 'Importar Alocação FOFs':
        status, informacao = automacao.importar_alocacao_fofs(database)
    if rotina == 'Coletar Composicao IMAs':
        status, informacao = automacao.coletar_composicao_ima(database)
    if rotina == 'Coletar IHFA':
        status, informacao = automacao.coletar_ihfa(database)
    if rotina == 'Coletar IFIX e IBX da B3':
        status, informacao = automacao.coletar_ifix_ibx(database)
    if rotina == 'Importar Alocação RV':
        status, informacao = automacao.importar_alocacao_rv(database)
    if rotina == 'Importar Classificação RV':
        status, informacao = automacao.importar_classificacao_rv(database)
    if rotina == 'Importar Classificação FOFs':
        status, informacao = automacao.importar_classificacao_fofs(database)
    if rotina == 'Calcular Taxa VANG11':
        status, informacao = automacao.calcular_taxa_vang11(mutil.somar_dia_util(date.today(), -1), database)
    if rotina == 'Calcular Taxa IVCI11':
        status, informacao = automacao.calcular_taxa_ivci11(mutil.somar_dia_util(date.today(), -1), database)
    if rotina == 'Coletar taxa BDIF11':
        status, informacao = automacao.coletar_taxa_bdif11(database)
    if rotina == 'Atualizar Fundos RI':
        status, informacao = automacao.atualizar_fundos_atividades_ri(database)
    if rotina == 'Coletar Histórico de Compras e Vendas':
        data_inicio = mutil.somar_dia_util(date.today(), -30)
        data_fim = date.today()
        status, informacao = automacao.coletar_historico_compras_vendas(database ,data_inicio, data_fim)
    if rotina == 'Validar Coleta do Histórico CDI':
        status, informacao = automacao.validador_historico_cdi(database)
    if rotina == 'Rotinas de Validação':
        status, informacao = automacao.rotinas_validacao(database)
    if rotina == 'Validar ativos não cadastrados':
        status, informacao = automacao.validar_cadastro_ativos(database)
    if rotina == 'Validar cotas BD vs XMLs':
        status, informacao = automacao.valida_cota_bd_versus_xml(database)
    if rotina == 'Validar cotas BD vs Comdinheiro':
        status, informacao = automacao.valida_cota_bd_versus_comdinheiro(database)
    if rotina == 'Atualizar Estratégia dos Ativos':
        status, informacao = automacao.atualizar_estrategia_ativos(database)
    if rotina == 'Excluir XMLs duplicados da rede':
        status, informacao = automacao.excluir_xmls_duplicados()
    if rotina == 'Verificar XMLs duplicados da rede':
        status, informacao = automacao.verificar_xmls_duplicados()
    if rotina == 'Validar Ativos Sem Estratégia':
        status, informacao = automacao.validar_ativos_sem_estrategia()
    if rotina == 'Valida Ratings Duplicados':
        status, informacao = automacao.valida_ratings_duplicados(database)
    if rotina == 'Valida Coleta de Índices':
        data = datetime(date.today().year, date.today().month, 1) - relativedelta(days=1)
        status, informacao = automacao.validar_coleta_indices(database, data)
    if rotina == 'Validar Ativos sem ISIN':
        status, informacao = automacao.validar_ativos_sem_isin(database)
    if rotina == 'Salvar Planilha de Durations no Backoffice':
        status, informacao = automacao.salvar_taxas_backoffice(database)
    if rotina == 'Validar Ativos Sem Rating Interno':
        status, informacao = automacao.validar_ativos_sem_rating_interno(database)
    if rotina == 'Validar Calculadora':
        status, informacao = automacao.validar_calculadora(database)
    if rotina == 'Corrigir Transações Vanguarda na Tabela Negócios B3':
        status, informacao = automacao.corrige_transacao_vanguarda_negocios_b3(database)
    if rotina == 'Coletar XMLs Bradesco D0 e D1':
        status, informacao = automacao.coletar_xml_bradesco_d0_d1()
    if rotina == 'Coletar XMLs Itaú D0 e D1':
        status, informacao = automacao.coletar_xml_itau_d0_d1()
    if rotina == 'Validar Importação da Alocação de FOFs e RV':
        status, informacao = automacao.validar_alocacao_fofs_rv_xml_bd(database)
    if rotina == 'Calcular Taxas Fundos Listados 5du':
        status, informacao = automacao.calcular_taxas_fundos_listados_5du(database)
    if rotina == 'Validar Taxas dos Fundos Listados':
        status, informacao = automacao.validar_taxas_fundos_listados(database)
    if rotina == 'E-mail Eventos Verificar PU':
        status, informacao = automacao.enviar_email_eventos_verificar_pu(database)
    if rotina == 'Validar Ativos Sem Spread':
        status, informacao = automacao.validar_ativos_sem_spread_fechamento_mes(database)
    if rotina == 'Valida Setores Renda Variável - BD vs Planilha Rede':
        status, informacao = automacao.validar_setores_rv_planilha_bd(database)
    if rotina == 'Valida Classificação FOF - BD vs Planilha Rede':
        status, informacao = automacao.validar_classificacao_fof_planilha_bd(database)
    if rotina == 'Valida XML Vazio':
        status, informacao = automacao.valida_xml_vazio()
    if rotina == 'Excluir XML Vazio':
        status, informacao = automacao.excluir_xml_vazio()
    if rotina == 'Validar Índices com Comdinheiro':
        status, informacao = automacao.validar_indices_comdinheiro(database)
    if rotina == 'Coletar XMLs Bradesco do Ano Inteiro':
        status, informacao = automacao.coletar_xml_bradesco_ano()
    if rotina == 'Coletar XMLs Itaú últimos 22 dias úteis':
        status, informacao = automacao.coletar_xml_itau_22du()
    if rotina == 'Coletar XMLs Itaú últimos 44 dias úteis':
        status, informacao = automacao.coletar_xml_itau_44du()
    if rotina == 'Salvar Planilha Ativos Securitizados - Enquadramento':
        status, informacao = automacao.salvar_planilha_ativos_securitizados(database)
    if rotina == 'Coletar XMLs Daycoval do Ano Inteiro':
        status, informacao = automacao.coletar_xml_daycoval_ano()
    if rotina == 'Enviar E-mail Últimos Documentos CVM':
        status, informacao = automacao.enviar_email_documentos_cvm(database)
    if rotina == 'Alerta de Basiléia - Fundo IRB CDI':
        status, informacao = automacao.alerta_basileia_irb(database)
    if rotina == 'Valida Relatório Fundos':
        status, informacao = automacao.valida_relatorio_fundos(database)
    if rotina == 'Validar Liquidação Compras':
        status, informacao = automacao.validar_liquidacao_compras(database)
    if rotina == 'Derrubar Conexões Inativas do Banco de Dados':
        status, informacao = automacao.derrubar_conexoes_inativas(database)
    if rotina == 'Gerar Mapa de Crédito':
        status, informacao = automacao.gerar_mapa_credito()
    if rotina == 'Cadastrar Ativos Parcerias Icatu Seguros':
        status, informacao = automacao.cadastrar_ativos_parcerias_icatu(database)
    if rotina == 'Salvar planilha de emissores bancários na rede':
        status, informacao = automacao.salvar_planilha_bancos_rede(database)
    if rotina == 'Gerar Lâminas para o Itaú':
        status, informacao = automacao.gerar_laminas_itau(database)
    if rotina == 'Valida Ativos da Carteira Vanguarda sem Fluxo Cadastrado':
        status, informacao = automacao.valida_ativos_carteira_sem_fluxo(database)
    if rotina == 'Calcular Dados BI Secundário':
        status, informacao = automacao.secundario_calcula_dados_bi(database)
    if rotina == 'Salvar Planilha Emissores Bancários - Backoffice':
        status, informacao = automacao.salvar_planilha_emissores_bancarios_backoffice(database)
    if rotina == 'Enviar E-mail FIDCs - Últimos Documentos CVM':
        status, informacao = automacao.enviar_email_documentos_fidcs_cvm(database)
    if rotina == 'Salvar Planilha FI Analytics na Rede':
        status, informacao = automacao.salvar_planilha_fi_analytics_rede()
    if rotina == 'Coletar Holders Ativos com Dinheiro':
        status, informacao = automacao.coletar_holders_ativos_comdinheiro(database)
    if rotina == 'Salvar Planilha Negócios B3 - Rede':
        status, informacao = automacao.salvar_planilha_negocios_b3_rede(database)
    if rotina == 'Validar Compras e Vendas - BD vs Planilha Histórico Boletão':
        status, informacao = automacao.validador_compras_vendas(database)



    df.loc[df.index[df['Descrição'] == rotina][0], ['Status']] = status
    df.loc[df.index[df['Descrição'] == rotina][0], ['Informações']] = informacao
    tabela.empty()
    tabela.table(df)
