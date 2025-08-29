export type IdentificadorFundo = {
  tipo: "CNPJ" | "CETIP" | "SELIC";
  valor: string;
};

export type IdentificadorAtivo = {
  tipo_ativo: TipoTituloPrivado;
  tipo_codigo: "ISIN" | "TICKER";
  codigo: string;
};

export type IdentificadorCorretora = {
  tipo:
    | "APELIDO_VANGUARDA"
    | "NOME_DESK"
    | "NOME_INSTITUICAO"
    | "ID_DESK"
    | "ID_INSTITUICAO";
  valor: string;
};

export type SugestaoAlocacao = {
  id: number;
  id_fundo: IdentificadorFundo;
  id_ativo: IdentificadorAtivo;
  id_corretora: IdentificadorCorretora;
  lado_operacao: "C" | "V";
  data_liquidacao: string;
  preco: number;
  quantidade: number;
  horario: string;
};

export type Alocacao = SugestaoAlocacao & {
  posicao_liquidacao: "LIQUIDADA" | "CANCELADA" | null;
  posicao_liquidacao_em: string | null;
  alocacao_administrador: string | null;
  registro_nome: string | null;
  voice: string | null;
  alocacao_anterior: string | null;
  // Quem alocou no sistema
  id_usuario: number;
};

export enum PosicaoLiquidacao {
  APROVADO = 1,
  REJEITADO = 2,
}

export enum PosicaoAlocacaoAdministrador {
  LIQUIDADO = 1,
  CANCELADO = 2,
}

export type AlocacaoAdministrador = {
  id: number;
  id_administrador: number;
  codigo_alocacao: string;
  horario: string;
  posicao_administrador: PosicaoAlocacaoAdministrador | null;
  posicao_em: string | null;
  id_alocacao: number;
  id_usuario: number;
};

export type ResultadoProcessamento =
  | {
      linha: number;
      status: "OK";
      dados: SugestaoAlocacao;
      detalhes: null;
    }
  | {
      linha: number;
      status: "VAZIA";
      dados: null;
      detalhes: null;
    }
  | {
      linha: number;
      status: "AVISO";
      dados: SugestaoAlocacao;
      detalhes: string;
    }
  | {
      linha: number;
      status: "ERRO";
      dados: null;
      detalhes: string;
    };

export type SugestaoBoleta = {
  client_id?: number;
  id: number;
  mercado: Mercado | null;
  tipo: TipoOperacao;
  horario: string;
  tipo_ativo: TipoTituloPrivado;
  corretora: string;
  alocacoes: SugestaoAlocacao[];
  data_liquidacao: string;
};

export type Boleta = SugestaoBoleta & { mercado: Mercado };

export type ResultadoBuscaBoleta_Corretora = {
  id: number;
  nome: string;
};

export type ResultadoBuscaBoleta_Administrador = {
  id: number;
  nome: string;
};

export type ResultadoBuscaBoleta_Fundo = {
  id: number;
  nome: string;
  cnpj: string;
  conta_cetip: string;
  administrador: ResultadoBuscaBoleta_Administrador | null;
};

export type ResultadoBuscaBoleta_CancelamentoAdministrador = {
  alocacao_administrador_id: number;
  cancelado_em: string;
  motivo: string | null;
  usuario_id: number;
};

export type ResultadoBuscaBoleta_LiquidacaoAdministrador = {
  alocacao_administrador_id: number;
  liquidado_em: string;
  usuario_id: number;
};

export type ResultadoBuscaBoleta_AlocacaoAdministrador = {
  alocacao_id: number;
  alocacao_usuario_id: number;
  alocado_em: string;
  codigo_administrador: string | null;
  cancelamento: ResultadoBuscaBoleta_CancelamentoAdministrador | null;
  liquidacao: ResultadoBuscaBoleta_LiquidacaoAdministrador | null;
};

export type ResultadoBuscaBoleta_Cancelamento = {
  alocacao_id: number;
  cancelado_em: string;
  motivo: string | null;
  usuario_id: number;
};

export type RegistroNoMe = {
  alocacao_id: number;
  numero_controle: string;
  data: string;
  recebido_em: string;
  posicao_custodia: boolean | null;
  posicao_custodia_em: string | null;
  posicao_custodia_contraparte: boolean | null;
  posicao_custodia_contraparte_em: string | null;
};

export type EnvioDecisaoPreTrade = {
  id: number;
  erro: string | null;
  enviado_em: string;
};

export type EnvioAlocacaoPostTrade = {
  id: string;
  erro: string | null;
  enviado_em: string;
  sucesso_em: string | null;
};

export type Voice = {
  id_trader: string;
  envios_pre_trade: EnvioDecisaoPreTrade[];
  envios_post_trade: EnvioAlocacaoPostTrade[];
  horario_recebimento_post_trade: string | null;
};

export type CasamentoAlocacaoB3Voice = {
  casado_em: string;
  voice: Voice;
};

export type ResultadoBuscaBoleta_Alocacao = {
  id: number;
  codigo_ativo: string;
  vanguarda_compra: boolean;
  preco_unitario: string;
  quantidade: string;
  data_liquidacao: string;
  data_negociacao: string;
  alocado_em: string;
  aprovado_em: string | null;
  corretora_id: number;
  alocacao_usuario: string;
  aprovacao_usuario: string | null;
  alocacao_anterior_id: number | null;
  fundo: ResultadoBuscaBoleta_Fundo;
  cancelamento: ResultadoBuscaBoleta_Cancelamento | null;
  alocacao_administrador: ResultadoBuscaBoleta_AlocacaoAdministrador | null;

  casamento: CasamentoAlocacaoB3Voice | null;
  quebras: ResultadoBuscaBoleta_Alocacao[];
  registro_NoMe: RegistroNoMe | null;
};

export type ResultadoBuscaBoleta = {
  id: number;
  data_liquidacao: string;
  tipo_ativo_id: TipoTituloPrivadoEnum;
  natureza_operacao_id: TipoOperacaoEnum;
  mercado_negociado_id: MercadoEnum;
  corretora: ResultadoBuscaBoleta_Corretora;
  alocacoes: ResultadoBuscaBoleta_Alocacao[];
};

export type TipoTituloPrivado =
  | "BOND"
  | "CDB"
  | "CRA"
  | "CRI"
  | "Debênture"
  | "DPGE"
  | "FIDC"
  | "FII"
  | "LF"
  | "LFS"
  | "LFSC"
  | "LFSN"
  | "NC"
  | "RDB"
  | "FIAGRO";
export enum TipoTituloPrivadoEnum {
  BOND = 1,
  CDB = 2,
  CRA = 3,
  CRI = 4,
  Debênture = 5,
  DPGE = 6,
  FIDC = 7,
  FII = 8,
  LF = 9,
  LFS = 10,
  LFSC = 11,
  LFSN = 12,
  NC = 13,
  RDB = 14,
  FIAGRO = 15
}
export const TipoTituloPrivadoMap: Record<
  TipoTituloPrivadoEnum,
  TipoTituloPrivado
> = {
  [TipoTituloPrivadoEnum.BOND]: "BOND",
  [TipoTituloPrivadoEnum.CDB]: "CDB",
  [TipoTituloPrivadoEnum.CRA]: "CRA",
  [TipoTituloPrivadoEnum.CRI]: "CRI",
  [TipoTituloPrivadoEnum.Debênture]: "Debênture",
  [TipoTituloPrivadoEnum.DPGE]: "DPGE",
  [TipoTituloPrivadoEnum.FIDC]: "FIDC",
  [TipoTituloPrivadoEnum.FII]: "FII",
  [TipoTituloPrivadoEnum.LF]: "LF",
  [TipoTituloPrivadoEnum.LFS]: "LFS",
  [TipoTituloPrivadoEnum.LFSC]: "LFSC",
  [TipoTituloPrivadoEnum.LFSN]: "LFSN",
  [TipoTituloPrivadoEnum.NC]: "NC",
  [TipoTituloPrivadoEnum.RDB]: "RDB",
  [TipoTituloPrivadoEnum.FIAGRO]: "FIAGRO",
};

export type Mercado = "INDEFINIDO" | "PRIMARIO" | "SECUNDARIO";
export enum MercadoEnum {
  INDEFINIDO = 0,
  PRIMARIO = 1,
  SECUNDARIO = 2,
}
export const MercadoMap: Record<MercadoEnum, Mercado> = {
  [MercadoEnum.INDEFINIDO]: "INDEFINIDO",
  [MercadoEnum.PRIMARIO]: "PRIMARIO",
  [MercadoEnum.SECUNDARIO]: "SECUNDARIO",
};

export type TipoOperacao = "EXTERNA" | "INTERNA";
export enum TipoOperacaoEnum {
  EXTERNA = 1,
  INTERNA = 2,
}
export const TipoOperacaoMap: Record<TipoOperacaoEnum, TipoOperacao> = {
  [TipoOperacaoEnum.EXTERNA]: "EXTERNA",
  [TipoOperacaoEnum.INTERNA]: "INTERNA",
};
