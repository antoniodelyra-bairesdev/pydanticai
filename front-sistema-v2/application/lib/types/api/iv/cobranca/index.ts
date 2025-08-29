export type Inquilino = {
  id: number;
  razao_social: string;
  cnpj: string;
  cep: string;
  logradouro: string;
  bairro: string;
  cidade: string;
  estado: string;
  contrato: ContratoLocacao;
};

export type ContratoLocacao = {
  id: number;
  fundo_id: number;
  inquilino_id: number;
  dia_vencimento: number;
  percentual_juros_mora_ao_mes: number;
  faixas_cobranca_multa_mora: FaixaMultaMora[];
};

export type FaixaMultaMora = {
  contrato_locacao_id: number;
  dias_a_partir_vencimento: number;
  percentual_sobre_valor: number;
};
