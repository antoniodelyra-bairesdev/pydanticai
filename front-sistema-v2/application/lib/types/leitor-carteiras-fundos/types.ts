export interface Posicao {
  data: string;
  produto_investimento:
    | ProdutoInvestimento
    | Classe
    | Subclasse
    | CarteiraAdministrada
    | FundoNaoAdaptado
    | null;
  fonte: FonteDeDados | null;
  erros_validacao: string[];
}

export interface FonteDeDados {
  tipo: string;
  link: string;
}

export interface ProdutoInvestimento {
  tipo: string;
  isin: ISIN | null;
  identificadores: Identificador[];
  nome: string;
  financeiro: Financeiro;
  valor_ativos: string;
  patrimonio_liquido: string;
  administrador: Administrador | null;
  gestor: Gestor | null;
  custodiante: Custodiante;
}

export interface Administrador {
  nome: string;
  cnpj: CNPJ;
}

export interface Gestor {
  nome: string;
  cnpj: CNPJ;
}

export interface Custodiante {
  nome: string;
  cnpj: CNPJ;
}

export interface Financeiro {
  caixas: Caixa[];
  despesas: Pagamento[];
  valores_a_pagar: Pagamento[];
  valores_a_receber: Pagamento[];
}

export type TipoConta = "D" | "P" | "N" | "I" | "J";

export interface Caixa {
  isin_instituicao_financeira: ISIN;
  identificadores: Identificador[];
  tipo_conta: TipoConta;
  valor_financeiro: string;
}

export interface Pagamento {
  codigo: string | null;
  nome: string;
  valor: string;
  data_pagamento: string;
}

export interface DetalhesCotas {
  quantidade: string;
  valor_cotas_a_emitir: string;
  valor_cotas_a_resgatar: string;
  valor_unitario: string;
  valor_bruto_unitario: string | null;
}

export interface TaxaPagamento {
  indice: string;
  percentual_indice: string;
  cupom: string;
}

export interface DetalhesQuantidade {
  total: string;
  disponivel: string;
  alugado: string;
  bloqueado: string;
  garantia: string;
  margem: string;
  pendente_recebimento: string;
}

export interface Mercado {
  identificacao_mic: string;
  balcao_ou_formal: "BALCAO" | "FORMAL";
}

export interface AtivoCarteira {
  mercado: Mercado | null;
  ativo: Ativo;
  vendido: boolean;
  quantidade: DetalhesQuantidade;
  preco: PrecoPosicao;
  valor_provisionado_imposto: string;
  data_operacao: string | null;
  codigos_internos?: Record<string, string>;
}

export interface PrecoPosicao {
  preco_compra: string | null;
  preco_venda: string | null;
  preco_mercado: string | null;
  preco_curva: string | null;
  preco_vencimento: string | null;
  provisao: string | null;
}

export interface TaxaCambio {
  moeda_base: string;
  moeda_alvo: string;
  taxa: string;
}

export interface Ativo {
  isin: ISIN | null;
  ticker: Identificador | null;
  codigos_internos: Record<string, string>;
  identificadores: Identificador[];
  tipo: string;
}

export interface TituloPublico extends Ativo {
  taxa: TaxaPagamento;
  data_emissao: string;
  preco_emissao: string;
  data_vencimento: string;
  tipo: "TituloPublico";
}

export interface TituloPrivado extends Ativo {
  cnpj_emissor: CNPJ | null;
  taxa: TaxaPagamento;
  data_emissao: string;
  preco_emissao: string;
  data_vencimento: string;
  tipo: "TituloPrivado";
}

export interface Debenture extends Ativo {
  cnpj_emissor: CNPJ | null;
  taxa: TaxaPagamento;
  data_emissao: string;
  preco_emissao: string;
  data_vencimento: string;
  conversivel_em_acoes: boolean;
  participacao_lucros_emissor: boolean;
  emitida_por_spe: boolean;
  tipo: "Debenture";
}

export type OperacaoCompromissada =
  | "COMPRA_COM_REVENDA"
  | "VENDA_COM_RECOMPRA"
  | "INVALIDA";
export type TipoAtivoBase = "TituloPrivado" | "TituloPublico" | "Debenture";

export interface Compromissada extends Ativo {
  operacao: OperacaoCompromissada;
  isin_ativo_base: ISIN;
  tipo_ativo_base: TipoAtivoBase;
  cnpj_emissor_ativo_base: CNPJ | null;
  taxa: TaxaPagamento;
  data_emissao: string;
  data_vencimento: string;
  tipo: "Compromissada";
}

export interface CotaDeFundo extends Ativo {
  cnpj: CNPJ | null;
  tipo: "CotaDeFundo";
}

export type TipoHedge = "RENDA_FIXA" | "RENDA_VARIAVEL" | null;

export interface Futuro extends Ativo {
  isin_ativo_base: ISIN | null;
  valor_de_ajuste: string;
  hedge: TipoHedge;
  vencimento: string;
  cnpj_corretora: CNPJ | null;
  tipo: "Futuro";
}

export type PreferenciaPagamento = "ORDINARIA" | "PREFERENCIAL" | null;
export type FormaRegistro = "AO_PORTADOR" | "NOMINATIVO" | null;

export interface Equity extends Ativo {
  tamanho_do_lote: string;
  preferencia_para_pagamento: PreferenciaPagamento;
  forma_de_registro: FormaRegistro;
  tipo_equity: string;
  tipo: "Equity";
}

export type EstiloOpcao = "AMERICANA" | "EUROPEIA" | null;
export type TipoOpcao = "CALL" | "PUT";

export interface Opcao extends Ativo {
  estilo_opcao: EstiloOpcao;
  operacao: TipoOpcao;
  preco_exercicio: string;
  hedge: TipoHedge;
  data_vencimento: string;
  tipo: "Opcao";
}

export interface OpcaoAcao extends Ativo {
  estilo_opcao: EstiloOpcao;
  operacao: TipoOpcao;
  preco_exercicio: string;
  hedge: TipoHedge;
  data_vencimento: string;

  identificador_ativo_objeto: Identificador;
  cnpj_emissor_ativo_objeto: CNPJ | null;
  tipo: "OpcaoAcao";
}

export interface OpcaoDerivativo extends Ativo {
  estilo_opcao: EstiloOpcao;
  operacao: TipoOpcao;
  preco_exercicio: string;
  hedge: TipoHedge;
  data_vencimento: string;

  identificador_derivativo_objeto: Identificador;
  tipo: "OpcaoDerivativo";
}

export interface OpcaoMoeda extends Ativo {
  estilo_opcao: EstiloOpcao;
  operacao: TipoOpcao;
  preco_exercicio: string;
  hedge: TipoHedge;
  data_vencimento: string;

  taxa_de_cambio: TaxaCambio;
  tipo: "OpcaoMoeda";
}

export interface Termo extends Ativo {
  data_liquidacao: string;
  hedge: TipoHedge;
  tipo: "Termo";
}

export interface TermoRendaFixa extends Ativo {
  data_liquidacao: string;
  hedge: TipoHedge;

  isin_ativo_objeto: ISIN;
  taxa_negociacao: TaxaPagamento;

  tipo: "TermoRendaFixa";
}

export interface TermoEquity extends Ativo {
  data_liquidacao: string;
  hedge: TipoHedge;

  isin_ativo_objeto: ISIN;
  ticker_ativo_objeto: Identificador | null;

  tipo: "TermoEquity";
}

export interface TermoMoeda extends Ativo {
  data_liquidacao: string;
  hedge: TipoHedge;

  taxa_cambio: TaxaCambio;

  tipo: "TermoMoeda";
}

export interface Swap extends Ativo {
  taxa_ativa: TaxaPagamento;
  taxa_passiva: TaxaPagamento;

  tipo: "Swap";
}

export interface EmprestimoEquity extends Ativo {
  isin_ativo_objeto: ISIN;
  cnpj_corretora: CNPJ;
  data_vencimento: string;
  taxa_aluguel: TaxaPagamento;
  cnpj_emissor_ativo_objeto: CNPJ | null;
  tamanho_lote: string;

  tipo: "EmprestimoEquity";
}

export interface FundoNaoAdaptado extends ProdutoInvestimento {
  cotas: DetalhesCotas;
  ativos: AtivoCarteira[];

  tipo: "FundoNaoAdaptado";
}

export interface Classe extends ProdutoInvestimento {
  cnpj_fundo_casca: CNPJ | null;
  cotas: DetalhesCotas;
  ativos: AtivoCarteira[];
  subclasses: Subclasse[];

  tipo: "Classe";
}

export interface Subclasse extends ProdutoInvestimento {
  cnpj_classe: CNPJ | null;
  cnpj_fundo_casca: CNPJ | null;
  cotas: DetalhesCotas;
  codigo_cvm: Identificador;

  tipo: "Subclasse";
}

export interface CarteiraAdministrada extends ProdutoInvestimento {
  ativos: AtivoCarteira[];
  identificador_titular: CNPJ | CPF;
  codigo_banco: Identificador;
  codigo_agencia: Identificador;
  codigo_conta: Identificador;

  tipo: "CarteiraAdministrada";
}

export interface Identificador {
  tipo: string;
  valor: string;
}

export interface ISIN extends Identificador {
  tipo: "ISIN";
}

export interface CNPJ extends Identificador {
  tipo: "CNPJ";
}

export interface CPF extends Identificador {
  tipo: "CPF";
}
