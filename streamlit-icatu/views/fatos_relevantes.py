import streamlit as st
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import unidecode
from models import util as mutil


@st.cache_resource(show_spinner=False)
def query_db(_database, query):
    return _database.query_select(query)


@st.cache_resource(show_spinner=False)
def documentos_notion(_notion, filtros, get_db=True):
    return _notion.documentos_filtrados(filtros)


@st.cache_resource(show_spinner=False)
def coletar_infos(_notion, data):
    status, props = _notion.coletar_infos_db()
    return status, props


def fatos(barra, db, notion_controller):
    st.title('Fatos Relevantes')
    with st.form('re'):
        col1, col2 = st.columns([1, 4])
        mes = col1.selectbox('Mês', [i[0].strip() for i in query_db(
            db, "select distinct to_char(data, 'YYYY/MM') from icatu.estoque_ativos order by to_char(data, 'YYYY/MM') desc")])
        fundo = col2.selectbox('Fundo', [i[0].strip() for i in query_db(
            db, 'select distinct nome from icatu.fundos where tipo is not null order by nome')])
        gerar = st.form_submit_button('Gerar')

        data_inicio = datetime(int(mes[:4]), int(mes[5:7]), 1).date()
        data_fim = mutil.somar_dia_util(
            data_inicio + relativedelta(months=1), -1)
        data_inicio = data_inicio.strftime('%Y-%m-%d')
        data_fim = data_fim.strftime('%Y-%m-%d')

        filtros = {
            "filter":
                {'and': [
                    {"property": "Tipo", "select": {"equals": 'Fato Relevante'}},
                    {"property": "Data", "date": {"on_or_after": data_inicio}},
                    {"property": "Data", "date": {"on_or_before": data_fim}},
                    {"property": "tag","multi_select": {"does_not_contain": 'Ignorar Python'}}    
                ]
                }
        }

    if st.button('Limpar cache'):
        documentos_notion.clear()
        coletar_infos.clear()
        col1, _ = st.columns([1, 4])
        col1.success('Cache limpo!')

    if gerar:
        with st.spinner('Aguarde...'):
            try:
                sql = f"""
                    select 
                        distinct i.cnpj
                    from icatu.estoque_ativos e
                    join icatu.info_papeis i on i.codigo = e.ativo 
                    join icatu.fundos f on f.isin = e.fundo 
                    where f.nome = '{fundo}'
                    and data between '{data_inicio}' and '{data_fim}'
                """
                emissores = [i[0].strip() for i in query_db(db, sql)]
                status, infos = coletar_infos(notion_controller, date.today())
                if status == 'OK':
                    for chave in infos:
                        setattr(notion_controller, chave, infos[chave])

                    fatos = documentos_notion(notion_controller, filtros)
                    fatos = sorted(
                        fatos, key=lambda d: unidecode.unidecode(d['props']['emissor'])+d['props']['data_inicial'].strftime('%Y-%m-%d'))
                    st.title(f'Fatos Relevantes - {fundo}  ({mes[5:7]}/{mes[:4]})')
                    for fato in fatos:
                        emissor = fato['props']['emissor_cnpj']
                        if emissor in emissores:
                            emissor = fato['props']['emissor']
                            data = fato['props']['data']
                            titulo = fato['props']['titulo']
                            st.subheader(f'{emissor} - {data} - {titulo}')
                            conteudo = fato['conteudo']
                            for fragmento in conteudo:
                                for chave in fragmento:
                                    if chave == 'image':
                                        texto = fragmento[chave]
                                        st.markdown(
                                            f'<img src="data:image/jpeg;base64,{texto}"></img>', unsafe_allow_html=True)
                                    else:
                                        texto = fragmento[chave]
                                        texto = texto.replace("$", r"\$")
                                        st.write(texto)
                else:
                    coletar_infos.clear()
                    coletar_infos(notion_controller, date.today())
                    raise Exception
            except:
                st.caption('Houve um erro')
