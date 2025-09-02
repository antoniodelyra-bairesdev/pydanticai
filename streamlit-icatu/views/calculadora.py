from datetime import datetime, date
from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit as st
import pandas as pd
import models.calculadora as calc
import views.util as util
import views.gerencial as ge
from models import automacao as au


def calculadora(barra, database):
    tipo_calc = barra.radio("Selecione a ferramenta",
            ('Calculadora', 'Comparativo B3', 'Vários ativos'))

    if tipo_calc == 'Calculadora':
        ativo(database)
    if tipo_calc == 'Comparativo B3':
        comparativo(database)
    if tipo_calc == 'Vários ativos':
        varios_ativos(database)


@st.cache_resource(show_spinner=False)
def info_cache(_database):
    return _database.info_papeis()

@st.cache_resource(show_spinner=False)
def get_curva_di(_database, data=date.today()):
    return [i[3] for i in _database.curva_di(data)]

@st.cache_resource(show_spinner=False)
def get_curva_ntnb(_database, data=date.today()):
    return au.curva_ntnb_interpolada(_database, data)

@st.cache_resource(show_spinner=False)
def info_ativo(_database):
    dados = """
    SELECT indice, percentual, juros, data_emissao, valor_emissao, 
            inicio_rentabilidade,  data_vencimento, i.empresa, codigo, tipo_ativo, 
            aniversario, i.codigo, ipca_negativo, ipca_2meses, e.empresa, i.isin,
            case 
                when indice = 'DI' and percentual > 100 then '%CDI' 
                when indice = 'DI' and (percentual = 100 or percentual is null) then 'CDI+' 
                when indice = 'IPCA' then 'IPCA+' 
                when indice = 'IGP-M' then 'IGPM+'
                else indice end as indice,
            case when percentual > 100 then percentual else juros end as taxa_emissao
        FROM icatu.info_papeis i
        left join icatu.emissores e on e.cnpj = i.cnpj"""
    
    dados = _database.query_select(dados)
    info_papeis = {}
    for papel in dados:
        info_papeis[papel[8].strip()] = {
                'indice': papel[0].strip(),
                'percentual': papel[1] if papel[1] else 100, 
                'juros': papel[2] if papel[2] else 0, 
                'data_emissao': papel[3], 
                'valor_emissao' : papel[4],
                'inicio_rentabilidade':papel[5],
                'data_vencimento':papel[6],
                'empresa': papel[7],
                'codigo': papel[8].strip(),
                'tipo_ativo': papel[9],
                'aniversario': papel[10],
                'codigo': papel[11],
                'ipca_negativo': papel[12],
                'ipca_2meses': papel[13],
                'emissor': papel[14] if papel[14] else '',
                'isin': papel[15].strip() if papel[15] else None,
                'Índice': papel[16].strip(),
                'Taxa Emissão': papel[17]
                }
    return info_papeis

@st.cache_resource(show_spinner=False)
def fluxo_ativos(_database):
    fluxo_papeis = {}
    dados = '''SELECT codigo, data_pagamento, percentual, pu_evento, tipo_evento 
                    FROM icatu.fluxo_papeis p
                    LEFT JOIN icatu.tipo_eventos t ON t.id = p.tipo_id
                    ORDER BY codigo, data_pagamento, tipo_id'''
    dados = _database.query_select(dados)
    for dado in dados:
        if not dado[0].strip() in fluxo_papeis:
            codigo = dado[0].strip()
            fluxo_papeis[dado[0].strip()] = []
        temp = fluxo_papeis[codigo]
        temp.append(dado[1:])
        fluxo_papeis[codigo] = temp
    
    return fluxo_papeis


def ativo(database):
    st.title(f"Calculadora de ativos")
    st.write("")
    curva_di = get_curva_di(database, date.today())
    curva_ntnb = get_curva_ntnb(database, date.today())
    info_papeis = info_ativo(database)
    fluxo_papeis = fluxo_ativos(database)

    col1, col2, col3 = st.columns([1, 3, 3])
    lista = info_cache(database)

    lista_empresa = ['Todos'] + sorted(list(set([i[2] for i in lista if i[2]])))
    lista_isin = ['Todos'] + list(set([i[3] for i in lista]))
    lista_cnpj = ['Todos'] + sorted(list(set([i[6] for i in lista if i[6]])))

    tipo = col1.selectbox('Tipo', ['Todos', 'Debênture', 'Letra Financeira', 'FIDC', 'CRI', 'BOND', 
                                   'NC', 'CDB', 'DPGE', 'FII', 'RDB', 'Fundo Listado'])
    if tipo == 'Todos':
        empresa = col2.selectbox('Apelido', lista_empresa)
        cnpj = col3.selectbox('Emissor', lista_cnpj)
        col1, col2, col3, _ = st.columns([1, 1, 2, 3])
        isin = col1.selectbox('ISIN', lista_isin)
    else:
        lista_empresa = ['Todos']
        lista_empresa = lista_empresa + sorted(list(set([i[2] for i in lista if i[2] and i[1] == tipo])))
        lista_isin = ['Todos']
        lista_isin = lista_isin + list(set([i[3] for i in lista if i[1] == tipo]))
        lista_cnpj = ['Todos']
        lista_cnpj = lista_cnpj + sorted(list(set([i[6] for i in lista if i[6] and i[1] == tipo])))
        empresa = col2.selectbox('Apelido', lista_empresa)
        cnpj = col3.selectbox('Emissor', lista_cnpj)
        col1, col2, col3, _ = st.columns([1, 1, 2, 3])
        isin = col1.selectbox('ISIN', lista_isin)
    tipo_vencimento = col3.radio("Busca de vencimento", ('Maior ou igual','Menor ou igual', 'Igual'), horizontal=True)
    vencimento = col2.date_input('Data de Vencimento')     

    col1, col2, col3, col4, col5, col6, _ = st.columns([1.4, 1, 1, 1.2, 1, 1.2, 2])
    papel = col1.selectbox('Papel', sorted(set([i[0].strip() for i in lista 
                                    if (i[1] == tipo or tipo == 'Todos') and
                                       (i[2] == empresa or empresa == 'Todos') and 
                                       (i[3] == isin or isin == 'Todos') and
                                       (i[6] == cnpj or cnpj == 'Todos') and
                                        (((isinstance(i[5], date) and i[5] >= vencimento and tipo_vencimento == 'Maior ou igual') or
                                        (isinstance(i[5], date) and i[5] <= vencimento and tipo_vencimento == 'Menor ou igual') or
                                        (isinstance(i[5], date) and i[5] == vencimento and tipo_vencimento == 'Igual')))                                       
                                       ])))
    data = col2.date_input('Data do cálculo')
    tipo_calc = col3.radio("Tipo de cálculo", ('Calcular PU','Calcular Taxa', 'Por % do Par'))
    submitted = st.button("Calcular")
    taxa, validar, vna = 0, False, None
    if tipo_calc == 'Calcular PU':
        taxa = col4.number_input('Taxa',  format="%.6f")
        if taxa > 0: validar = True
        if col5.radio("Tipo de VNA", ('Calcular VNA','Inserir VNA')) == 'Inserir VNA':
            validar = False
            vna = col6.number_input('VNA',format="%.6f")
            if vna > 0: validar = True
    if tipo_calc == 'Calcular Taxa':
        preco = col4.number_input('PU',  format="%.6f")
        if preco > 0: validar = True
    if tipo_calc == 'Por % do Par':
        percentual_par = col4.number_input('% do PAR',  format="%.6f")
        if percentual_par > 0: validar = True

    if submitted and papel and data and validar:
        with st.spinner('Aguarde...'):
            try:
                info, fluxo = info_papeis[papel], fluxo_papeis[papel]

                curva_di = get_curva_di(database, data)
                curva_ntnb = get_curva_ntnb(database, data)

                if vna:
                    vna = {data: vna}
                    calculo = calc.papel(info, fluxo, database, vna)
                else:
                    calculo = calc.papel(info, fluxo, database)

                if tipo_calc == 'Calcular PU':
                    resposta = calculo.informacoes(data, taxa, curva_di)
                if tipo_calc == 'Calcular Taxa':
                    resposta = calculo.taxa(data, preco, curva_di)
                    taxa = resposta['Taxa']
                    resposta = calculo.informacoes(data, taxa, curva_di)
                if tipo_calc == 'Por % do Par':
                    taxa = info_papeis[papel]['Taxa Emissão']
                    pu_par = calculo.informacoes(data, taxa, curva_di)['calculo']['PU Par']
                    preco = pu_par * percentual_par/100
                    resposta = calculo.taxa(data, preco, curva_di)
                    taxa = resposta['Taxa']
                    resposta = calculo.informacoes(data, taxa, curva_di)

                st.text("")

                if isinstance(resposta['fluxo'], pd.DataFrame):
                    _, col1, col2, col3 = st.columns([0.2, 1, 1, 1])
                    col1.metric("VNA", "{:,.6f}".format(resposta['calculo']['VNA']).replace(",", "x").replace(".", ",").replace("x", "."))
                    col2.metric("PU Par", "{:,.6f}".format(resposta['calculo']['PU Par']).replace(",", "x").replace(".", ",").replace("x", "."))
                    col3.metric("Preço", "{:,.6f}".format(resposta['calculo']['PU']).replace(",", "x").replace(".", ",").replace("x", "."))
                    st.text("")
                    st.text("")
                    _, col1, col2, col3, col4 = st.columns([0.2, 1, 1, 1, 1])
                    col1.metric("Duration (Anos)", "{:,.6f}".format(resposta['calculo']['Duration']).replace(",", "x").replace(".", ",").replace("x", "."))    
                    col2.metric("Taxa", "{:,.6f}%".format(taxa).replace(",", "x").replace(".", ",").replace("x", "."))   
                    col3.metric("% do PAR", "{:,.2f}%".format((resposta['calculo']['PU'] / resposta['calculo']['PU Par'])*100).replace(",", "x").replace(".", ",").replace("x", "."))                
                    spread = au.calcular_spread(
                        taxa, 
                        ge.indexador(info['indice'], taxa),
                        taxa,
                        resposta['calculo']['Duration'],
                        data.strftime('%Y-%m-%d'),
                        curva_di,
                        curva_ntnb
                        )
                    col4.metric("Spread", "{:,.2f}%".format(spread).replace(",", "x").replace(".", ",").replace("x", "."))        
                    st.text("")
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.subheader('Informações')
                        st.text("")
                        util.view_info(resposta['info'])
                        df_download = resposta['fluxo'].copy(deep=False)
                        util.download_excel_button([pd.DataFrame(i) for i in calculo.memoria_calculo(data, curva_di=curva_di, taxa=taxa)], ['VNA', 'PU Par','PU', 'Fluxo'], 'Download em Excel', papel)
                    with col2:
                        st.subheader('Fluxo')
                        hide_table_row_index = """
                                    <style>
                                    thead tr th:first-child {display:none}
                                    tbody th {display:none}
                                    </style>
                                    """
                        st.markdown(hide_table_row_index, unsafe_allow_html=True)
                        df = resposta['fluxo']
                        df['Data de pagamento'] = df['Data de pagamento'].apply(lambda x: x.strftime("%d/%m/%Y"))
                        resposta = resposta['fluxo'].drop(columns=['Saldo Percentual', 'Amortização Percentual', 
                                        'Amortização Base 100', 'Fluxo Percentual Descontado', 'Fluxo Percentual', 'Código', 'Taxa Cálculo'])
                        resposta['Fluxo Projetado'] = resposta['Fluxo Projetado'].apply(lambda x: "{:,.4f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                        resposta['Fluxo Descontado'] = resposta['Fluxo Descontado'].apply(lambda x: "{:,.4f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                        resposta['Saldo Devedor'] = resposta['Saldo Devedor'].apply(lambda x: "{:,.4f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                        resposta['Taxa'] = resposta['Taxa'].apply(lambda x: "{:,.4f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                        st.table(resposta)
            except Exception as erro:
                print(erro)
                st.caption("Erro ao calcular PU")

def comparativo(database):
    st.title("Comparativo B3")
    st.write("")

    col1, col2, col3, _ = st.columns([1, 1, 1, 3])
    papel = col1.selectbox('Papel', (database.lista_debentures()))
    submitted = col1.button("Calcular")
    data = col2.date_input('Data')
    taxa = col3.number_input('Taxa',  format="%.4f")
            
    if submitted and papel and data and taxa > 0:
        with st.spinner('Aguarde...'):
            try:
                st.text("")
                info, fluxo = database.papel_info(papel), database.fluxo_papel(papel)
                info = calc.papel(info, fluxo, database)
                info = info.comparativo_b3(data, taxa)

                col1, col2 = st.columns([1.2, 2])
                hide_table_row_index = """
                            <style>
                            thead tr th:first-child {display:none}
                            tbody th {display:none}
                            </style>
                            """
                with col1:
                    st.subheader('Resultado')
                    st.markdown(hide_table_row_index, unsafe_allow_html=True)
                    df = info['quadro']
                    quadro_download, fluxo_download = df.copy(deep=False), info['fluxo'].copy(deep=False)
                    df['VNA'] = df['VNA'].apply(lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                    df['PU Par'] = df['PU Par'].apply(lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                    df['Preço'] = df['Preço'].apply(lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                    df['Duration'] = df['Duration'].apply(lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                    st.table(df)
                    util.download_excel_button([quadro_download, fluxo_download],['info', 'fluxo'], 'Download em excel', papel)
                with col2:
                    st.write("")

                st.subheader('Fluxo Comparado')
                st.markdown(hide_table_row_index, unsafe_allow_html=True)
                df = info['fluxo']
                df['Data de pagamento'] = df['Data de pagamento'].apply(lambda x: x.strftime("%d/%m/%Y"))
                df['Fluxo Projetado'] = df['Fluxo Projetado'].apply(lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                df['Fluxo Descontado'] = df['Fluxo Descontado'].apply(lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                df['Fluxo Projetado B3'] = df['Fluxo Projetado B3'].apply(lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                df['Fluxo Descontado B3'] = df['Fluxo Descontado B3'].apply(lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                df['FD Diferença'] = df['FD Diferença'].apply(lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                df['FP Diferença'] = df['FP Diferença'].apply(lambda x: "{:,.6f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                df['Taxa'] = df['Taxa'].apply(lambda x: "{:,.4f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                df['Taxa B3'] = df['Taxa B3'].apply(lambda x: "{:,.4f}".format(x).replace(",", "x").replace(".", ",").replace("x", "."))
                st.table(df)
            except:
                st.caption("Erro ao calcular PU")

def varios_ativos(database):
    st.title("Calcular o preço de vários ativos")
    curva_di = get_curva_di(database)
    info_papeis = info_ativo(database)
    info_papeis = {i.upper() : info_papeis[i] for i in info_papeis}
    fluxo_papeis = fluxo_ativos(database)
    fluxo_papeis = {i.upper() : fluxo_papeis[i] for i in fluxo_papeis}
    
    papeis = st.text_input('Papéis')
    papeis = papeis.upper()
    papeis = papeis.split()
    datas = st.text_input('Datas')
    datas = [util.validar_data(i) for i in datas.split()]
    tipo = st.radio("Tipo", ('Calcular PU','Calcular Taxa'), horizontal=True)
    planilha_fluxo = st.checkbox('Gerar planilha de fluxo')
    taxas, precos = ["0"], ["0"]

    if tipo == 'Calcular PU':
        taxas = st.text_input('Taxas')
        taxas = taxas.split()
    if tipo == 'Calcular Taxa':
        precos = st.text_input('Preços')
        precos = precos.split()

    if tipo == 'Calcular PU':
        col1, col2, col3, _ = st.columns([1, 1, 1, 4.5])
        corretagem_compra = col1.checkbox('Corretagem compra')
        corretagem_venda = col2.checkbox('Corretagem venda')
        corretagem_int = col3.checkbox('Corretagem interna')
    
    calcular = False
    lista_papeis = [i.upper() for i in database.lista_papeis()]

    try:
        tamanho = 0
        if tipo == 'Calcular PU':
            tamanho = min(len(papeis), len(datas), len(taxas))
        if tipo == 'Calcular Taxa':
            tamanho = min(len(papeis), len(datas), len(precos))

        nova_papeis, nova_data, nova_taxa, nova_preco = [], [], [], []
        for i in range(tamanho):
            if papeis[i] in lista_papeis:
                taxa = float(taxas[i].replace(",", ".").replace("%", "")) if len(taxas) >= tamanho else 0
                preco = float(precos[i].replace(",", ".")) if len(precos) >= tamanho else 0

                if (tipo == 'Calcular PU' and taxa > 0) or (tipo == 'Calcular Taxa' and preco > 0):
                    if tipo == 'Calcular PU':
                        if corretagem_compra:
                            nova_papeis.append(papeis[i])
                            nova_data.append(datas[i].strftime('%d/%m/%Y'))
                            if taxa >= 100:
                                nova_taxa.append(taxa+0.1)
                            else:
                                nova_taxa.append(taxa+0.01)
                            nova_preco.append(preco)             
                        if corretagem_venda:
                            nova_papeis.append(papeis[i])
                            nova_data.append(datas[i].strftime('%d/%m/%Y'))
                            if taxa >= 100:
                                nova_taxa.append(taxa-0.1)
                            else:
                                nova_taxa.append(taxa-0.01)
                            nova_preco.append(preco) 
                        if corretagem_int:
                            nova_papeis.append(papeis[i])
                            nova_data.append(datas[i].strftime('%d/%m/%Y'))
                            if taxa >= 100:
                                nova_taxa.append(taxa+0.05)
                            else:
                                nova_taxa.append(taxa+0.005)
                            nova_preco.append(preco)    
                    nova_papeis.append(papeis[i])
                    nova_data.append(datas[i].strftime('%d/%m/%Y'))
                    nova_taxa.append(taxa) 
                    nova_preco.append(preco)       
                

        if tipo == 'Calcular PU':
            dados = {'Papel': nova_papeis, 'Data': nova_data, 'Taxa': nova_taxa}
        if tipo == 'Calcular Taxa':
            dados = {'Papel': nova_papeis, 'Data': nova_data, 'Preço': nova_preco}

        df = pd.DataFrame(dados)
        hide_table_row_index = """
                    <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                    </style>
                    """
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 3])
        with col1:
            if nova_papeis and nova_data and nova_taxa and nova_preco:
                aviso = st.empty()
                aviso.info('Verifique se os dados estão corretos.')
                tabela = st.empty()
                tabela.table(df)

                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_column("Data", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='dd/MM/yyyy')
                
                if tipo == 'Calcular PU':
                    gb.configure_column("Taxa", 
                    type=["numericColumn","numberColumnFilter","customNumericFormat"], 
                    valueFormatter="value.toLocaleString('pt-BR',{maximumFractionDigits: 6, minimumFractionDigits: 2})+'%';") 
                else:
                    gb.configure_column("Preço", 
                    type=["numericColumn","numberColumnFilter","customNumericFormat"], 
                    valueFormatter="value.toLocaleString('pt-BR',{maximumFractionDigits: 6, minimumFractionDigits: 2});") 

                custom_css = {
                    ".ag-root.ag-unselectable.ag-layout-normal": {"font-size": "16px !important"},
                    ".ag-header-cell": {"background-color": "#0D6696 !important", "color": "white"},
                    ".ag-row":  {  "font-size": "16px !important;"}
                    }


                gb.configure_grid_options(enableCellTextSelection=True)
                gb.configure_grid_options(ensureDomOrder=True)
                gb.configure_grid_options(editable=True)
                with tabela:
                    new_df = AgGrid(
                    df,
                    gridOptions=gb.build(),
                    update_mode='NO_UPDATE',
                    fit_columns_on_grid_load=True,
                    allow_unsafe_jscode=True,
                    enableRangeSelection= True,
                    custom_css=custom_css,
                    height=min(50 + 45 * len(df.index), 400),
                    enable_enterprise_modules=True)


                calcular = st.button("Calcular")
            else:
                raise Exception
    except:
        col1, col2 = st.columns([1, 5])
        with col1:
            st.caption("Preencha os dados corretamente.")

    if calcular:
        try:

            aviso.empty()
            tabela.empty()
            vazio = st.empty()
            vazio.empty()
            vazio.progress(0)
            vna, pu_par, preco, duration, ind, taxa = [], [], [], [], [], []
            taxa_calc, empresa, erros, perc_par, spread, total = [], [], [], [], [], len(df.index)
            df_iteracao = df.copy(deep=False)
            df_fluxo = pd.DataFrame(columns=[
            'Data de pagamento',	
            'Dados do Evento',	'Dias Úteis',	'Taxa',	'Fluxo Projetado'	,'Fluxo Descontado'	,'Fluxo Percentual',
            'Fluxo Percentual Descontado', 'Saldo Devedor', 'Saldo Percentual', 'Amortização Percentual', 'Amortização Base 100'])
            for indice, row in df_iteracao.iterrows():
                try:
                    infos = info_papeis[row['Papel']]
                    df.at[indice,'ISIN'] = infos['isin']
                    fluxo = fluxo_papeis[row['Papel']]
                    info = calc.papel(infos, fluxo, database)
                    data = datetime.strptime(row['Data'], '%d/%m/%Y').date()
                    curva_di = get_curva_di(database, data)
                    curva_ntnb = get_curva_ntnb(database, data)

                    if tipo == 'Calcular PU':
                        resultado = info.duration(data, row['Taxa'], curva_di)
                        taxa_spread = row['Taxa']
                    if tipo == 'Calcular Taxa':
                        resultado = info.taxa(data, row['Preço'], curva_di)['Taxa']
                        taxa_calc.append(resultado)
                        taxa_spread = resultado
                        resultado = info.duration(data, resultado, curva_di)

                    if resultado:
                        vna.append(resultado['VNA'])
                        pu_par.append(resultado['PU Par'])
                        preco.append(resultado['PU'])
                        duration.append(resultado['Duration'])
                        ind.append(infos['Índice'])
                        taxa.append(infos['Taxa Emissão'])
                        empresa.append(infos['emissor'])
                        perc_par.append(resultado['PU'] / resultado['PU Par'])
                        spread.append(
                                au.calcular_spread(
                                taxa_spread, 
                                ge.indexador(infos['indice'], infos['Taxa Emissão']),
                                taxa_spread,
                                resultado['Duration'],
                                data.strftime('%Y-%m-%d'),
                                curva_di,
                                curva_ntnb
                            )
                        )
                        if df_fluxo.empty:
                            df_fluxo = pd.DataFrame(resultado['Fluxo'])
                        else:
                            novo_df = pd.DataFrame(resultado['Fluxo'])
                            df_fluxo = pd.concat([df_fluxo, novo_df], ignore_index=True)
                except:
                    try:
                        if infos['isin']:
                            df = df[df['ISIN']!= infos['isin']]
                        else:
                            df = df[df['Papel']!= row['Papel']]
                    except:
                        df = df[df['Papel']!= row['Papel']]
                    
                    if tipo == 'Calcular PU':
                        erros.append({'Ativo': row['Papel'], 'Data':row['Data'], 'Taxa':row['Taxa']})
                    if tipo == 'Calcular Taxa':
                        erros.append({'Ativo': row['Papel'], 'Data':row['Data'], 'Preço':row['Preço']})
            
                vazio.progress((indice+1)/total)     

            df.reset_index(drop=True, inplace=True)
            df['Emissor'] = empresa
            df['Índice'] = ind
            df['Taxa de Emissão'] = taxa

            df['VNA'] = vna
            df['PU Par'] = pu_par
            if tipo == 'Calcular PU': df['Preço'] = preco
            if tipo == 'Calcular Taxa': df['Taxa'] = taxa_calc
            df['Duration'] = duration   
            df['% do PAR'] = perc_par   
            df['Spread'] = spread   

            df = df[['Papel', 'Emissor', 'Índice', 'Taxa de Emissão', 'Data', 
                        'Taxa','VNA', 'PU Par','Preço','Duration', '% do PAR', 'Spread']]
            download = df.copy(deep=False)
            download['Data'] = download['Data'].apply(lambda x: datetime.strptime(x, "%d/%m/%Y").date())
            vazio.empty()
            try:
                st.subheader('Informações')
                if planilha_fluxo:
                    util.download_excel_button([download, df_fluxo],['Papeis', 'Fluxo Papeis'], 'Download em Excel', 'papeis')
                else:
                    util.download_excel_button([download],['Papeis'], 'Download em Excel', 'papeis')
                
                df['% do PAR'] = df['% do PAR'].apply(lambda x: x*100)
                
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_column("Data", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='dd/MM/yyyy')
                gb.configure_column("Taxa de Emissão", 
                type=["numericColumn","numberColumnFilter","customNumericFormat"], 
                valueFormatter="value.toLocaleString('pt-BR',{maximumFractionDigits: 6, minimumFractionDigits: 2})+'%';") 
                gb.configure_column("Taxa", 
                type=["numericColumn","numberColumnFilter","customNumericFormat"], 
                valueFormatter="value.toLocaleString('pt-BR',{maximumFractionDigits: 6, minimumFractionDigits: 2})+'%';") 
                gb.configure_column("VNA", 
                type=["numericColumn","numberColumnFilter","customNumericFormat"], 
                valueFormatter="value.toLocaleString('pt-BR',{maximumFractionDigits: 6, minimumFractionDigits: 6});") 
                gb.configure_column("Preço", 
                type=["numericColumn","numberColumnFilter","customNumericFormat"], 
                valueFormatter="value.toLocaleString('pt-BR',{maximumFractionDigits: 6, minimumFractionDigits: 6});")
                gb.configure_column("PU Par", 
                type=["numericColumn","numberColumnFilter","customNumericFormat"], 
                valueFormatter="value.toLocaleString('pt-BR',{maximumFractionDigits: 6, minimumFractionDigits: 6});")
                gb.configure_column("Duration", 
                type=["numericColumn","numberColumnFilter","customNumericFormat"], 
                valueFormatter="value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits: 2});")                 
                gb.configure_column("% do PAR", 
                type=["numericColumn","numberColumnFilter","customNumericFormat"], 
                valueFormatter="value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits: 2})+'%';") 
                gb.configure_column("Spread", 
                type=["numericColumn","numberColumnFilter","customNumericFormat"], 
                valueFormatter="value.toLocaleString('pt-BR',{maximumFractionDigits: 2, minimumFractionDigits: 2})+'%';") 

                gb.configure_grid_options(enableCellTextSelection=True)
                gb.configure_grid_options(ensureDomOrder=True)
                gb.configure_grid_options(editable=True)
                new_df = AgGrid(
                df,
                gridOptions=gb.build(),
                update_mode='NO_UPDATE',
                fit_columns_on_grid_load=False,
                allow_unsafe_jscode=True,
                enableRangeSelection= True,
                custom_css=custom_css,
                height=400,
                enable_enterprise_modules=True)

                if erros:
                    df_erros = pd.DataFrame(erros)
                    st.markdown('**Houve erro no cálculo dos seguintes registros**')
                    col1, _ = st.columns([1, 3])
                    col1.table(df_erros)
            except:
                vazio.empty()
                st.caption("Houve um erro")
        except:
            vazio.empty()
            st.caption("Houve um erro")

        