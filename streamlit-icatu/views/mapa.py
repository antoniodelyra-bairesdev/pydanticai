import streamlit as st

def mapa(barra):
    st.title('Mapa do Sistema')

    st.markdown('''
    #
    ### Calculadora
    **Calculadora**: Calcular individualmente o preço/taxa dos ativos salvos no banco de dados

    **Comparativo B3**: Comparativo de cálculo de preço/taxa entre a calculadora proprietária e a calculadora da B3

    **Vários ativos**: Calcular diversos ativos ao mesmo tempo

    ### Relatório Gerencial
    **Conferir Preço e Taxa de Ativos**: Conferir os preços e taxas dos ativos das carteiras dos fundos

    **Posição dos Fundos**: Relatório com informações das carteiras dos fundos

    **Preços e Taxas**: Verificar divergências de marcação de preços, taxas e durations dos ativos das carteiras

    **Próximos Eventos**: Relatório com informações dos próximos pagamentos dos ativos da carteira

    **Cota dos Fundos**: Verificar a rentabilidade diária das cotas dos fundos

    **Estoque de Ativos**: Verificar divergências no estoque de ativos entre Britech e o banco de dados do sistema

    **Carrego dos Fundos**: Relatório da evolução do carrego dos fundos (total ou por faixa de rating)

    **Preços Ajustados**: Evolução da rentabilidade acumulada do preço ajustado dos ativos 

    **Conferir Pagamentos**: Conferir cálculo feito pela calculadora proprietária com os pagamentos feitos nas contas CETIPs dos fundos

    **Evolução de Taxas**: Relatório da evolução dos spreads dos fundos

    ### Gerencial Prévio
    Comparação de preços estimados e observados para os ativos da carteira. O preço estimado de um dia é calculado considerando o mesmo nível de spread do dia anterior

    ### Indicadores Financeiros
    **Calcular Spread/Taxa**: É possível calcular o spread/taxa de um ativo informando seu índice e duration
    
    **Indicadores**: Dados históricos da curva DI e dos índices de inflação

    **Fundos Imobiliários**: Mostra o retorno acumulado dos fundos imobiliários e seus respectivos setores

    ### Banco de Dados
    **Ativos**: Tela de cadastro dos ativos

    **Fundos**: Tela de cadastro dos fundos

    **PL de Emissores/Grupos**: Tela de cadastro do Patrimônio Líquido dos emissores e grupos

    **Ratings**: Tela de cadastro dos ratings

    ### Rotinas Automáticas
    **Relatório de Status**: Relatório de controle de status das rotinas de coleta de dados

    **Gerar Rotinas Manualmente**: Ferramenta para geração manual de rotinas

    **Rotinas da Manhã**: Relatório para controle das rotinas diárias de coleta de dados

    **Relatório de XMLs**: Relatório que mostra o controle de importação dos XMLs dos fundos

    **Fundos Não Importados**: Relatório que mostra quais fundos não foram importados para o banco de dados
    
    ### Relatórios do Power BI
    Links de acesso aos relatórios do Power BI

    ### Ferramenta de Transcrição
    Ferramenta para geração de arquivo de texto com transcrição de gravações de reuniões
    
    ### Simulação de Boletas
    Ferramenta para simulação de compras e vendas de ativos com objetivo final de geração de boletas para o backoffice
    
    ### Gerar Ata de Comitê
    Tela para geração dos documentos (PDF) de ata dos comitês

    ### Fatos Relevantes
    Tela para acompanhamento das publicações de fatos relevantes dos emissores, agrupados por fundo

    ### Assembleias
    Tela para acompanhamento das Assembleias das emissões

    '''
    )