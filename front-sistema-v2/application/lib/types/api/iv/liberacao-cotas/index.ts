export enum CampoRequestLiberacaoCotas {
  Csv_Relatorio_Bip = "csv_relatorio_bip",
  Xls_Caracteristicas_Fundos = "xls_caracteristicas_fundos",
  Xlsm_Depara_Derivativos = "xlsm_depara_derivativos",
  Xlsx_Depara_Bonds = "xlsx_depara_bonds_offshore",
  Xlsx_Depara_Credito_Privado = "xlsx_depara_ativos_credito_privado",
  Xlsx_Depara_Ativos_Marcados_Na_Curva = "xlsx_depara_ativos_marcados_na_curva",
  Xlsx_Depara_Cotas_Fundos = "xlsx_depara_cotas_fundos",
  Xlsx_Relatorio_Antecipacao = "xlsx_relatorio_antecipacao",
  Xlsx_Relatorio_Despesas_Britech = "xlsx_relatorio_despesas_britech",
  Xlsx_Estoque_Renda_Fixa = "xlsx_estoque_renda_fixa",
  Xlsx_Estoque_Renda_Variavel = "xlsx_estoque_renda_variavel",
  Xlsx_Estoque_Futuro = "xlsx_estoque_futuro",
  Xlsx_Estoque_Cota = "xlsx_estoque_cota",
  Xlsxs_Relatorios_Movimentacoes_Pgbl = "xlsxs_relatorios_movimentacoes_pgbl",
  Zip_Arqs_Xml_Anbima_401 = "zips_arqs_xml_anbima_401",
  Xlsx_Fundos_Investidos = "xlsx_fundos_investidos",
}

export type FundoInfo = {
  codigo_britech: string;
  codigo_administrador: string;
  cnpj: string;
  nome: string;
  tipo_cota: string;
};

export type FundoInfoComXml = FundoInfo & {
  nome_arq_xml_anbima_401: string;
};

export type ComparacaoPl = {
  fundo_codigo_britech: string;
  fundo_codigo_administrador: string;
  fundo_cnpj: string;
  fundo_nome: string;
  data_referente: string;
  pl_xml: number;
  pl_calculado: number;
  diferenca_pl: number;
};

export type ComparacaoAtivo = {
  fundo_codigo_britech: string;
  fundo_nome: string;
  fundo_cnpj: string;
  fundo_codigo_administrador: string;
  data_referente: string;
  ativo_xml?: AtivoCarteira;
  ativo_britech?: AtivoCarteira;
  tipo_ativo: TipoAtivo;
  diferenca_pu?: number;
  diferenca_quantidade?: number;
  diferenca_financeiro?: number;
};

export type AtivoCarteira = {
  isin?: string;
  codigo: string;
  quantidade: number;
  preco_unitario_posicao: number;
  financeiro: number;
  tipo: TipoAtivo;
  vencimento: string | null;
};

export type PrecoCreditoPrivado = {
  codigo: string;
  isin?: string;
  preco_unitario_posicao: number;
  data_referente: string;
  fundo_info: FundoInfoComXml;
};

export enum TipoAtivo {
  Renda_Fixa = "RendaFixa",
  Renda_Variavel = "RendaVariavel",
  Futuro = "Futuro",
  Cota = "CotasFundos",
}
