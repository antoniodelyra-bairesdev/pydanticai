import streamlit as st

def acompanhamento(barra):
    st.title('Últimas entregas')
    # st.markdown('''<form action="https://tarry-sweatpants-841.notion.site/60961b9c162c484ca354d8f5ad7bcd26?v=461a1945bc744b3491f0fb5735d280ec" target="_blank">
    # <input style="background-color:white; border: 1px solid LightGrey; border-radius: 5px" type="submit" value="Abrir Notion" /> </form>''', unsafe_allow_html=True)

    st.markdown('''
    #
    ##### 30/09/2023 - Diversas entregas
    - Foram cadastrados os novos fundos Dinâmico IPCA  e CDI
    - Nova funcionalidade de cálculo de preço/taxa dos ativos através de API. Ou seja, via Python, outras mesas vão poder utilizar a nossa calculadora
    - Novo gráfico de comparação de indicador no relatório de setor bancário no Power BI. Relatório de barra 100% empilhada mostrando CP / RWA
    - Pequena correção do valor de PL Alocável no simulador de boletas
    - Alteração dos scripts de rotinas automáticas para uso do email robo@icatuvanguarda.com.br 
    - Criação da caixa corporativa robo@icatuvanguarda.com.br para envio automático de e-mails
    - Nova funcionalidade de abertura da composição da carteira de crédito dos bancos no relatórios de setor bancário no Power BI
    - Nova coluna mostrando o total alocado em crédito no relatório de comparação de portfólios no Power BI
    - Nova funcionalidade de seleção de período no retorno acumulado do fundo no relatório de alocação do Power BI
    - Foi criado novo workspace no Power BI para possibilitar a atualização de relatórios por todos da equipe
    - Melhoria no código de importação de XMLs
    - Cálculo do valor de carrego dos fundos considerando os ativos com operações compromissadas
    - Alteração no script de rotina.py para contemplar as mudanças de persistência do status das rotinas no banco de dados
    - Alteração para mostrar informações de compromissada no Power BI
    - Cálculo de taxa a partir do spread em **Indicadores Financeiros**
    - Foi feita alteração no script de atualização dos status da rotinas automáticas para persistência no banco de dados
    - Correção na calculadora pra cálculo de ativos IPCA com data aniversário para o dia 28
    - Ajuste na base de dados dos ratings de ativos bancários
    - Tela para cálculo de spread a partir da taxa em **Indicadores Financeiros**
    #
    ##### 30/08/2023 - Diversas entregas
    - Foi incluída a fonte ANBIMA no relatório de divergência de preços no módulo de **Relatório Gerencial** > **Preços e Taxas**
    - Foi criado um script para salvamento automático na rede dos XMLs coletados dos pelo administradores
    - Foram incluídos mais dois usuários no script de coleta do XML do Itaú, para atender pedido do Backoffice
    - Foi criado script que possibilita a atualização automática de ratings dos ativos bancários a partir do rating do emissor
    - Foi realizada manutenção no script de coleta da planilha da Bloomberg que mostra as taxas dos bonds 
    - Foi criado novo relatório para batimentos dos eventos calculados para os ativos da carteira em relação as valores pagos nas contas CETIP dos fundos
    - Foi incluído filtro de emissor no relatório de eventos previstos para os próximos 365 dias
    - Foi realizado cadastro do FIDC Solfacil III
    - Foi criada nova funcionalidade para geração automática das atas dos comitês de crédito
    - Foi realizada uma correção no cálculo que mostra a variação de spread dos ativos no relatório de alocação do Power Bi
    - Foi incluído o pagamento de prêmio no cálculo dos preços ajustados dos ativos da carteira
    - Melhoria no código para padronizar as pastas de salvamento dos robôs e facilitar  a configuração do banco de dados
    - Agora é possível explodir a carteira dos fundos que compram cotas de outros fundos de crédito. As mudanças foram feitas no bancos de dados, no Streamlit e nos relatórios do Power BI
    - Foi aperfeiçoado o processo de debug do código, sendo possível parar a execução de uma tarefa a partir do acionamento no Streamlit
    - Agora a tela de Evolução das taxas dos ativos é possível de ser acessada no módulo de Relatório Gerencial
    - Foi feita uma correção na informação de % do PL médio por emissor nos relatórios do Streamlit e Power BI
    - Foi criada nova funcionalidade para visualização do carrego da carteira dos fundos agregado por faixa de rating
    - Agora o relatório de alterações de rating por fundo possui a informação dos ratings de toda a carteira, não somente as alterações
    - Foi feita correção da tela que mostra a evolução dos preços ajustados dos ativos
    - Foi criada uma opção de visualização do mapa do sistema do Streamlit
    - Foi criada nova funcionalidade no banco de dados e no Power BI para visualização dos títulos associados a operações compromissadas
    - Foi criada nova visualização no Power BI de setor bancário para demonstrar os limites de alocação por categoria de rating
    #
    '''
    )