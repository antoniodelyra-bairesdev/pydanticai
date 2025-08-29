import { User } from "./auth";

export type APIWarning = {
  tipo_id: string;
  id: string;
  mensagens: string[];
};

export type FundoCustodiante = {
  id: number;
  nome: string;
};

export type PartialFundo = {
  id: number;
  nome: string;
  cnpj: string;
  isin: string | null;
  codigo_brit: number | null;
  conta_cetip: string | null;
  conta_selic: string | null;
  codigo_carteira: string | null;
  mnemonico: string | null;
  aberto_para_captacao: boolean;
  fundo_disponibilidade_id: number | null;
  ticker_b3: string | null;
  fundo_administrador_id: number | null;
  codigo_carteira_administrador: string | null;
  fundo_controlador_id: number | null;
  agencia_bancaria_custodia: string | null;
  conta_aplicacao: string | null;
  conta_resgate: string | null;
  conta_movimentacao: string | null;
  conta_tributada: string | null;
  minimo_aplicacao: number | null;
  minimo_movimentacao: number | null;
  minimo_saldo: number | null;
  cotizacao_aplicacao: number | null;
  cotizacao_aplicacao_sao_dias_uteis: boolean | null;
  cotizacao_aplicacao_detalhes: string | null;
  cotizacao_resgate: number | null;
  cotizacao_resgate_sao_dias_uteis: boolean | null;
  cotizacao_resgate_detalhes: string | null;
  financeiro_aplicacao: number | null;
  financeiro_aplicacao_sao_dias_uteis: boolean | null;
  financeiro_aplicacao_detalhes: string | null;
  financeiro_resgate: number | null;
  financeiro_resgate_sao_dias_uteis: boolean | null;
  financeiro_resgate_detalhes: string | null;
  publico_alvo_id: number | null;
  benchmark: string | null;
  taxa_performance: string | null;
  taxa_administracao: string | null;
  taxa_administracao_maxima: string | null;
  resumo_estrategias: string | null;
  data_inicio: string | null;
};
export type Arquivo = {
  id: string;
  nome: string;
  extensao: string;
};

export type FundoIndiceBenchmark = {
  nome: string;
  ordenacao: number;
};

export type Fundo = PartialFundo & {
  controlador: InstituicaoFinanceira;
  administrador: InstituicaoFinanceira;
  custodiante: InstituicaoFinanceira | null;
  publicado: boolean;
  indices: FundoIndiceBenchmark[];
  mesa_responsavel: Mesa | null;
  mesas_contribuidoras: Mesa[];
  caracteristicas_extras: FundoCaracteristicaExtra[];
  detalhes_infos_publicas: FundoDetalhesSiteInstitucional | null;
  pertence_a_classe: number | null;
};

export type UpdateFundoRequest = Omit<PartialFundo, "id"> & {
  custodiante_id: number;
};

export type TipoEvento = {
  id: number;
  nome: string;
  tokens: string[];
};

export type TipoPapel = {
  id: number;
  nome: string;
};

export type IndicePapel = {
  id: number;
  nome: string;
};

export type FluxoItemLista = {
  id: number;
  data_pagamento: string;
  tipo_evento: string;
  data_evento?: string | null;
  percentual?: number | null;
  pu_evento?: number | null;
  pu_calculado?: number | null;
};

export type PapelItemLista = {
  codigo: string;
  emissor: string;
  tipo: string;
  indice: string;
  fluxos: FluxoItemLista[];
  apelido?: string | null;

  isin?: string;
};

export type AtivoIPCA = {
  id: number;
  mesversario: number;
  ipca_negativo: boolean;
  ipca_2_meses: boolean;
};

export type Ativo = {
  codigo: string;

  valor_emissao: number;
  taxa: number;

  data_emissao: string;
  inicio_rentabilidade: string;
  data_vencimento: string;

  atualizacao: string;
  cadastro_manual: boolean;

  apelido?: string | null;
  isin?: string | null;
  serie?: number | null;
  emissao?: number | null;

  ativo_ipca?: AtivoIPCA;
  fluxos: Evento[];
  tipo: TipoPapel;
  indice: IndicePapel;
  emissor: Emissor;
};

export type AnalistaCredito = {
  id: number;
  user: User;
};

export type EmissorGrupo = {
  id: number;
  nome: string;
};

export type EmissorSetor = {
  id: number;
  nome: string;
  sistema_icone?: string;
};

export type Emissor = {
  nome: string;
  id: number;
  cnpj: string;

  grupo: EmissorGrupo | null;
  setor: EmissorSetor | null;
  analista_credito: AnalistaCredito | null;

  codigo_cvm: number | null;
  tier: number | null;
};

export type Evento = {
  id: number;
  ativo_codigo: string;
  data_pagamento: string;
  tipo: TipoEvento;

  data_evento?: string | null;
  percentual?: number | null;
  pu_evento?: number | null;
  pu_calculado?: number | null;
};

export type EventoSchema = Omit<Evento, "tipo"> & { tipo_id: number };

export type InsertedAtivoSchema = {
  codigo: string;

  valor_emissao: number;
  taxa: number;

  data_emissao: string;
  inicio_rentabilidade: string;
  data_vencimento: string;

  apelido?: string | null;
  isin?: string | null;
  serie?: number | null;
  emissao?: number | null;

  tipo_id: number;
  indice_id: number;
  ativo_ipca?: Omit<AtivoIPCA, "id">;
  emissor_id: number;
  fluxos: EventoSchema[];
};

export type ModifiedAtivoSchema = Omit<InsertedAtivoSchema, "fluxos"> & {
  fluxos: {
    deleted: number[];
    modified: EventoSchema[];
    added: EventoSchema[];
  };
};

export type CurvaDIResponse = {
  dia: string;
  atualizacao: string | null;
  curva: {
    taxa: number;
    dias_uteis: number;
    dias_corridos: number;
    data_referencia: string;
    interpolado: boolean;
  }[];
};

export type InfosData = {
  data_referencia: string;
  atualizacao: string | null;
};

export type PontoCurvaNTNB = {
  taxa: number;
  duration: number;
};

export type PontoCurvaNTNBReal = PontoCurvaNTNB & { data_vencimento: string };

export type CurvaNTNBResponse = {
  data: string;
  ajustes_dap: InfosData & {
    dados: (PontoCurvaNTNBReal & { utilizado: boolean })[];
  };
  taxas_indicativas: InfosData & {
    dados: PontoCurvaNTNBReal[];
  };
  curva: PontoCurvaNTNB[];
};

export type IPCA = {
  data: string;
  indice_acumulado: number;
  indice_mes: number;
  percentual: number;
  atualizacao: string;
};

export type IPCAProj = {
  data: string;
  projetado: boolean;
  indice: number;
  projecao: number;
  atualizacao: string;
};

export type VisualEmpresa = {
  id: number;
  nome: string;
  imagem?: {
    provedor: string;
    dados: string;
  };
  decoracao?: {
    cor: string;
    tamanho: number;
  }[];
};

export type EventoOperacaoAcatoVoice = {
  tipo: "acato-voice";
  voice: Voice;
};

export type FundoComQuebras = PartialFundo & {
  custodiante: FundoCustodiante;
  quebras: number[];
};

export type EventoAlocacaoOperador = {
  tipo: "alocacao-operador";
  operacao: OperacaoAlocadaInternamente;
};

export type EventoAprovacaoBackoffice = {
  id: number;
  numero_controle_nome?: string;
  tipo: "aprovacao-backoffice";
  usuario: Omit<User, "devices">;
  aprovacao: boolean;
  criado_em: string;
  motivo: string | null;
};

export type RegistroNoMe = {
  id: number;
  numero_controle_nome: string;
  casamento_operacao_voice_id: number;
  criado_em: string;
  registro_nome_novo_id: number | null;
  quantidade: number;
  fundo: FundoAlocacao;
};

export type EnvioAlocacao = {
  id: string;
  casamento_operacao_voice_id: number;
  registro_nome_id: number | null;
  conteudo: string;
  criado_em: string;
  erro: Erro | null;
  registro_nome: RegistroNoMe | null;
  atualizado_em: string;
};

export type EventoEnvioAlocacao = {
  tipo: "envio-alocacao";
  mensagem: EnvioAlocacao;
};

export type EventoAlocacaoContraparte = {
  tipo: "alocacao-contraparte";
  final: boolean;
};

export type QuebraRTC = {
  numero_controle_nome?: string;
  hora: string;
  fundo_nome: string;
  custodiante: string;
  status_custodiante?: number;
  status_custodiante_contraparte?: number;
  quantidade: number;
};

export type EventoEmissaoNumerosControle = {
  tipo: "emissao-numeros-controle";
  quebras: RegistroNoMe[];
};

export type EventoAtualizacaoCustodiante = {
  tipo: "atualizacao-custodiante";
  casamento_operacao_voice_id: number;
  registro_nome_id: number;
  registro_nome: RegistroNoMe;
  status: number;
  criado_em: string;
};

export type EventoListarTudo = {
  tipo: "listar-tudo";
  voices: Voice[];
  operacoes: CasamentoOperacaoVoice[];
};

export type CorretoraResumo = {
  nome: string;
  contas: string[];
};

export type EventoAtualizacaoCorretoras = {
  tipo: "corretoras";
  corretoras: CorretoraResumo[];
};

export type Erro = {
  resumo: string;
  detalhes: string[];
};

export type EventoErroMensagem = {
  tipo: "erro-mensagem";
  id_mensagem: string;
  erro: Erro;
};

export type EventoOperacao = {
  criado_em: string;
  casamento_operacao_voice_id: number | null;
  informacoes:
    | EventoAtualizacaoCorretoras // Interno
    | EventoListarTudo // Interno
    | EventoOperacaoAcatoVoice // B3: secl.001.001.03
    | EventoAlocacaoOperador // Interno
    | EventoAprovacaoBackoffice // Interno
    | EventoEnvioAlocacao // B3: bvmf.234.01
    | EventoAlocacaoContraparte // B3: bvmf.234.01
    | EventoEmissaoNumerosControle // B3: bvmf.234.01
    | EventoAtualizacaoCustodiante // B3: bvmf.234.01
    | EventoErroMensagem; // B3: bvmf.234.01
};

export type OperacaoType = {
  id: number;
  casamento_operacao_voice_id: number;
  codigo_ativo: string;
  cadastro_ativo: AtivoResumo | null;
  contraparte_nome: string | null;
  contraparte_conta: string | null;
  preco_unitario: number;
  quantidade: number;
  taxa: number;

  vanguarda_compra: boolean;
  negocio_b3_id: string | null;
  criado_em: string;

  eventos: EventoOperacao[];
};

export type IDB3 = {
  id: number;
  id_b3: string;
};

export type Corretora = {
  id: number;
  nome: string;
  ids_b3: IDB3[];
};

export type Voice = {
  id: number;
  id_trader: string;
  codigo_ativo: string;
  registro_ativo?: Ativo;
  indice?: string;
  taxa: number;
  preco_unitario: number;
  quantidade: number;
  data_operacao: string;
  criado_em: string;
  nome_contraparte: string;
  registro_contraparte?: Corretora;
  vanguarda_compra: boolean;
};

export type FundoAlocacao = {
  nome: string;
  conta_cetip: string;
  ymf: string;
  cnpj: string;
  nome_custodiante: string;
};

export type Alocacao = {
  fundo: FundoAlocacao;
  registro_fundo: Fundo | null;
  quantidade: number;
  total: number;
};

export type OperacaoProcessada = {
  vanguarda_compra: boolean;
  data_operacao: string;
  indice: string;
  taxa: number;
  preco_unitario: number;
  rating: string;
  total_negociado: number;
  quantidade: number;
  alocacoes: Alocacao[];

  voice_casado: Voice | null;
  voices_candidatos: Voice[];

  ativo: string;
  registro_ativo: AtivoResumo | null;

  contraparte: string;
  registro_contraparte: Corretora | null;
};

export type AtivoResumo = {
  codigo: string;
  emissor: string;
  tipo: string;
  indice: string;
  isin: string | null;
};

export type AlocacaoOperacaoAlocadaInternamente = {
  criado_em: string;
  quantidade: number;
  total: number;
  fundo: FundoAlocacao;
};

export type OperacaoAlocadaInternamente = {
  id: number;
  casamento_operacao_voice_id: number;
  aprovacao_anterior_backoffice_id: number | null;
  registro_nome_id: number | null;
  registro_nome: string | null;

  codigo_ativo: string;
  registro_ativo: AtivoResumo | null;
  vanguarda_compra: boolean;
  nome_contraparte: string | null;
  taxa: number;
  preco_unitario: number;
  quantidade: number;
  data_operacao: string;
  criado_em: string;

  usuario_id: number | null;
  usuario: User | null;
  rating_id: number | null;
  indice: string | null;

  externa: boolean;

  alocacoes: AlocacaoOperacaoAlocadaInternamente[];
};

export type AprovacaoBackoffice = {
  id: number;
  casamento_operacao_voice_id: number;
  registro_nome_id: number | null;
  usuario_id: number;
  usuario: User;
  operacao_alocada_internamente_id: number;
  aprovacao: boolean;
  motivo: string | null;
  criado_em: string;
};

export type CasamentoOperacaoVoice = {
  voices: Voice[];
  registros_nome: RegistroNoMe[];
  aprovacoes_backoffice: AprovacaoBackoffice[];
  atualizacoes_custodiante: EventoAtualizacaoCustodiante[];
  operacoes: OperacaoAlocadaInternamente[];
  envios_alocacao: EnvioAlocacao[];
};

export enum AlocacaoStatus {
  Pendente_Confirmação_Custodiante = 1,
  Pendente_Confirmação_Contraparte_Custodiante = 2,
  Rejeitado_pelo_Custodiante = 3,
  Rejeitado_pela_Contraparte_Custodiante = 4,
  Confirmado_pelo_Custodiante = 5,
  Disponível_para_Registro = 6,
  Pendente_de_Realocação_da_Contraparte = 7,
  Realocado = 8,
  Pendente_de_Realocação = 9,
}

export type CategoriaRelatorio = {
  id: number;
  nome: string;
  ordem: number;
  documentos: DocumentoRelatorio[];
  plano_de_fundo: PlanoDeFundo | null;
};

export type DocumentoRelatorio = {
  id: number;
  nome: string;
  categoria_id: number;
  arquivo_id: string;
  arquivo: Arquivo;
};

export type PlanoDeFundo = {
  id: number;
  conteudo_b64: string;
};

export enum EstrategiaAgrupamentoOperacoes {
  Todas = "todas",
  Bloco = "bloco",
  Linha = "linha",
}

export type FundoSiteInstitucionalClassificacao = {
  id: number;
  nome: string;
};

export type FundoSiteInstitucionalTipo = {
  id: number;
  nome: string;
};

export type FundoInstitucional = {
  id: number;
  fundo_id: number;
  nome: string;
  apelido: string;
  classificacao: FundoSiteInstitucionalClassificacao;
  tipo: FundoSiteInstitucionalTipo;
};

export enum DisponibilidadeFundoEnum {
  Listado = 1,
  Aberto = 2,
  Fechado = 3,
  Exclusivo = 4,
}

export enum PublicoAlvoEnum {
  Investidor_Geral = 1,
  Investidor_Qualificado = 2,
  Investidor_Profissional = 3,
}

export type IndiceBenchmark = {
  id: number;
  nome: string;
  ordenacao: number;
};

export type Mesa = {
  id: number;
  nome: string;
  sobre: string;
  fundos_responsavel: { id: number; nome: string }[];
  fundos_contribuidora: { id: number; nome: string }[];
  ordenacao: number;
};

export type InstituicaoFinanceira = {
  id: number;
  nome: string;
};

export type GestorFundo = {
  id: number;
  nome: string;
};

export enum TipoFundoEnum {
  Listado = 1,
  Aberto = 2,
  Fechado = 3,
  Exclusivo = 4,
}

export type FundoDocumento = {
  id: number;
  criado_em: string;
  data_referencia: string;
  titulo: string | null;
  arquivo: Arquivo;
};

export type FundoClassificacaoDocumento = {
  id: number;
  nome: string;
};

export type DocumentosDoFundo = {
  classificacao: FundoClassificacaoDocumento;
  arquivos: FundoDocumento[];
};

export type FundoDetalhes = Fundo & {
  documentos: DocumentosDoFundo[];
};

export type PublicoAlvo = {
  id: number;
  nome: string;
};

export type FundoDetalhesSiteInstitucional = {
  id: number | null;
  atualizado_em: string | null;
  nome: string | null;
  cnpj: string | null;
  aberto_para_captacao: boolean | null;
  ticker_b3: string | null;
  cotizacao_resgate: number | null;
  cotizacao_resgate_sao_dias_uteis: boolean | null;
  cotizacao_resgate_detalhes: string | null;
  financeiro_resgate: number | null;
  financeiro_resgate_sao_dias_uteis: boolean | null;
  financeiro_resgate_detalhes: string | null;
  publico_alvo_id: number | null;
  publico_alvo: PublicoAlvo | null;
  benchmark: string | null;
  taxa_performance: string | null;
  taxa_administracao: string | null;
  taxa_administracao_maxima: string | null;
  resumo_estrategias: string | null;
  mesa_id: number | null;
  mesa: Mesa | null;

  classificacao: FundoSiteInstitucionalClassificacao | null;
  tipo: FundoSiteInstitucionalTipo | null;
  indices_benchmark: IndiceBenchmark[];
  caracteristicas_extras: FundoCaracteristicaExtra[];
  documentos: DocumentosDoFundo[];

  pertence_a_classe: number | null;
};

export type FundoCaracteristicaExtra = {
  id: number;
  nome: string;
};

export type FundoRentabilidade = {
  fundo_id: number;
  data_posicao: string;
  preco_cota: number | null;
  rentabilidade_dia: number | null;
  rentabilidade_mes: number | null;
  rentabilidade_ano: number | null;
  rentabilidade_12meses: number | null;
  rentabilidade_24meses: number | null;
  rentabilidade_36meses: number | null;
};

export type IndiceBenchmarkRentabilidade = {
  indice_benchmark_id: number;
  data_posicao: string;
  rentabilidade_dia: number | null;
  rentabilidade_mes: number | null;
  rentabilidade_ano: number | null;
  rentabilidade_12meses: number | null;
  rentabilidade_24meses: number | null;
  rentabilidade_36meses: number | null;
};

export type FundoPL = {
  fundo_id: number;
  data_posicao: string;
  patrimonio_liquido: number | null;
  media_12meses: number | null;
  media_24meses: number | null;
  media_36meses: number | null;
};

export type IndicadorRentabilidadeStatus = {
  indices_benchmark_id_rentabilidades_inseridos: number[];
  indices_benchmark_id_rentabilidades_nao_inseridos: number[];
};

export type FundoPLStatus = {
  fundos_ids_patrimonio_liquido_rentabilidades_inseridos: number[];
  fundos_ids_patrimonio_liquido_rentabilidades_nao_inseridos: number[];
};

export type FundoRentabilidadeStatus = {
  fundos_ids_cotas_rentabilidades_inseridos: number[];
  fundos_ids_cotas_rentabilidades_nao_inseridos: number[];
};

export type ProcessamentoBdFolder =
  | {
      persist: false;
      indicadores: IndiceBenchmarkRentabilidade[];
      fundos: {
        pls: FundoPL[];
        rentabilidades: FundoRentabilidade[];
      };
    }
  | {
      persist: true;
      indicadores: IndicadorRentabilidadeStatus[];
      fundos: {
        pls: FundoPLStatus[];
        rentabilidades: FundoRentabilidadeStatus[];
      };
    };
