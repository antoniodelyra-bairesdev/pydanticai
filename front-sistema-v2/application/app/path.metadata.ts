export const publicPathsMetadata = {
  "/login": {
    title: "Sistema Icatu Vanguarda",
  },
} as const;

export const authPathsMetadata = {
  "/": {
    title: "Página Inicial",
  },
  "/dashboard": {
    title: "Dashboard",
  },
  "/ativos": {
    title: "Ativos",
  },
  "/calculadora": {
    title: "Calculadora",
  },
  "/emissores": {
    title: "Emissores",
  },
  "/fundos": {
    title: "Fundos",
  },
  "/fontes-dados": {
    title: "Fontes de dados",
  },
  "/indicadores": {
    title: "Indicadores e taxas",
  },
  "/mensagens": {
    title: "Mensagens",
  },
  "/notificacoes": {
    title: "Notificações",
  },
  "/operacoes": {
    title: "Operações",
  },
  "/site-institucional": {
    title: "Site Institucional",
  },
  "/usuarios": {
    title: "Usuários",
  },
  "/liberacao-cotas": {
    title: "Liberação de Cotas",
  },
  "/enquadramento": {
    title: "Enquadramento OMNiS",
  },
  "/locacoes": {
    title: "Locações de FIIs",
  },
  "/carteira-diaria": {
    title: "Carteira diária",
  },
  "/ferramentas": {
    title: "Ferramentas",
  },
  "/ferramentas/relatorio-carteira": {
    title: "Visualização de carteiras",
  },
  "/ferramentas/conversor-carteiras": {
    title: "Conversor de carteiras",
  },
  // '/relatorio-gerencial': {
  //     title: 'Relatório Gerencial'
  // },
  // '/gerencial-previo': {
  //     title: 'Gerencial Prévio'
  // },
  // '/indicadores-financeiros': {
  //     title: 'Indicadores Financeiros'
  // },
  // '/banco-de-dados': {
  //     title: 'Banco de dados'
  // },
  // '/tarefas': {
  //     title: 'Acompanhamento de Tarefas'
  // },
  // '/rotinas': {
  //     title: 'Rotinas automáticas'
  // },
  // '/power-bi': {
  //     title: 'Relatórios do PowerBI'
  // },
  // '/transcricao': {
  //     title: 'Ferramenta de transcrição'
  // },
  // '/boletas': {
  //     title: 'Simulação de boletas'
  // }
} as const;

export const pathMetadata = {
  ...publicPathsMetadata,
  ...authPathsMetadata,
};
