import streamlit as st
from io import BytesIO
from datetime import datetime
import pandas as pd
import datetime
import dateutil.parser

def download_excel_button(lista_df, lista_abas, botao, nome_arquivo, onclick=None):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book
    i = 0
    for df in lista_df:
        sheet = lista_abas[i]
        colunas_data = ['Data de pagamento', 'Data Rating', 'Data Anterior', 'Data de Referência', 
                        'Data','Data da Emissão', 'Data de Emissão', 'Início da Rentabilidade', 
                        'Data de Vencimento', 'Data Vencimento', 'Vencimento', 'Dt. Operac.',
                        'Início do Aniversário' ,'Final do Aniversário','Próximo Final','Dia com maior liquidez']
        excel_start_date = datetime.datetime(1899, 12, 30).date()

        for coluna in colunas_data:
            if coluna in df:
                df[coluna]=df[coluna].apply(lambda x: (x - excel_start_date).days if isinstance(x, type(excel_start_date)) and not pd.isnull(x) else x)
        
        df.to_excel(writer, index=False, sheet_name=sheet)
        workbook = writer.book

        for col_num, name in enumerate(df.columns.values):
            cell_format = workbook.add_format({'align': 'center'})
            column_length = max(df[name].astype(str).map(len).max(), len(name) if name != "Data" else 12) + 3

            if  name in ['Saldo Percentual', 'Peso no IFIX', 'PL Alocado', '% Par', '% do PAR','% do PL', 
                         '% do PL Médio', 'Amortização Percentual', 'Amortização Base 100', 
                         'Fluxo Percentual Descontado', 'Fluxo Percentual','Objetivo %PL','Perc Emissão']:
                cell_format = workbook.add_format({'num_format': '#,##0.00%', 'align': 'center'})
            if name in ['Saldo Devedor', 'Fluxo Projetado', 'Fluxo Descontado', 'Financeiro Estimado Icatu', 
                'Fluxo Projetado B3', 'FP Diferença', 'Fluxo Descontado B3', 'FD Diferença', 'VNA', 'Valor da Emissão', 
                'PU Par' , 'Preço','Preço Taxa','R$','Maior Preço','PL do Fundo','PL Fundo', 'Menor Preço','Preço D-1', 'Duration','Maior Duration',
                'Menor Duration','Duration Carteira','Duration Fundo', 'Spread Carteira','Spread Fundo','Duration D-1', 'Acumulado', 'PU Estimado', 
                'Quantidade', 'Variação Taxa', 'Taxa', 'Taxa D-1', 'Spread Mínimo', 'Spread Máximo', 'Diferença Percentual',  'Taxa Emissão', 'Variação Spread', 
                'Spread D-1', 'Spread', 'Financeiro','Volume Negociado','Volume Total', 'Spread Médio Ponderado', 'Média Móvel 5 Dias',
                'Média negociada nos dias com negócios','Maior Volume Negociado (R$)']:
                cell_format = workbook.add_format({'num_format': '#,##0.00', 'align': 'center'})
            if name in ['PL Alocável R$', 'PL do Fundo']:
                cell_format = workbook.add_format({'num_format': '#,##0', 'align': 'center'})
            if name in ['Taxa ', 'Retorno']:
                cell_format = workbook.add_format({'num_format': '#,##0.000%', 'align': 'center'})
            if name in ['Quant.', '','Quantidade']:
                cell_format = workbook.add_format({'num_format': '#,##0', 'align': 'center'})
            if name in ['P.U.', '']:
                cell_format = workbook.add_format({'num_format': '#.000000', 'align': 'center'})
            if name in ['Duration ', 'Spread ', 'Taxa Cálculo','Spread Máximo','Spread Mínimo']:
                cell_format = workbook.add_format({'num_format': '#.000', 'align': 'center'})
            if name in colunas_data:
                cell_format = workbook.add_format({'align': 'center', 'num_format': 'dd/mm/yyyy'})
            writer.sheets[sheet].set_column(col_num, col_num, column_length, cell_format)
        i+=1
    writer.close()
    processed_data = output.getvalue()

    st.download_button(
        label=botao,
        data=processed_data,
        file_name=f'{nome_arquivo}_Emitido_em_{datetime.datetime.now().strftime("%Y-%m-%d-às-%H-%M-%S")}.xlsx',
        key=datetime.datetime.now(),
        on_click=onclick
    )

def view_info(dado):
    texto = ""
    for i in dado:
        if isinstance(dado[i], datetime.date):
            texto+= f'<b>{i}</b>: {dado[i].strftime("%d/%m/%Y")}<br>'
        elif isinstance(dado[i], float):
            texto+= f'<b>{i}</b>: {"{:,.4f}".format(dado[i]).replace(",", "x").replace(".", ",").replace("x", ".")}<br>'
        else:
            texto+= f'<b>{i}</b>: {dado[i]}<br>'
    st.markdown(texto, unsafe_allow_html=True)

def validar_data(data):
    try:
        data = datetime.datetime.strptime(data, '%d/%m/%Y').date() 
    except:
        try:
            data = datetime.datetime.strptime(data, '%d/%m/%y').date()
        except:
            try:
                data = dateutil.parser.parse(data).date()
            except:
                pass
    return data

def validar_float(numero):
    try:
        return float(numero)
    except:
        return 0