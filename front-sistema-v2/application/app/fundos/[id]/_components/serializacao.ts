import { FundoIndiceBenchmark } from "@/lib/types/api/iv/v1";
import { useFundoDetalhes } from "../_providers/FundoDetalhesProvider";
import { DocumentoComEstado } from "./DocumentosConteudo";
import { EstadoArquivoEnum } from "./WrapperArquivo";

export type AtualizacaoFundo = {
  isin: string | null;
  mnemonico: string | null;
  cnpj: string;
  nome: string;
  aberto_para_captacao: boolean;
  codigo_brit: number | null;
  codigo_carteira: string | null;
  conta_cetip: string | null;
  conta_selic: string | null;
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
  resumo_estrategias: string | null;
  indices: FundoIndiceBenchmark[];
  mesa_responsavel: number | null;
  mesas_contribuidoras: number[];
  caracteristicas_extras: number[];
  remover_documentos: number[];
};

export type MetadadosDocumentosFundo = {
  posicao_arquivo: number;
  titulo: string;
  data_referencia: string;
  fundo_categoria_id: number;
};

export type AtualizacaoInternaFundos = {
  metadados_documentos: MetadadosDocumentosFundo[];
  atualizacao_fundo: AtualizacaoFundo;
};

export default (
  dadosProvider: ReturnType<typeof useFundoDetalhes>,
  documentos: DocumentoComEstado[],
): AtualizacaoInternaFundos => {
  const metadados_documentos = documentos
    .filter((d) => d.estado === EstadoArquivoEnum.inserir)
    .map(({ data_referencia, titulo, categoria }, posicao_arquivo) => {
      const dados: MetadadosDocumentosFundo = {
        data_referencia,
        posicao_arquivo,
        titulo: titulo ?? "",
        fundo_categoria_id: categoria,
      };
      return dados;
    });

  const {
    isin,
    mnemonico,
    cnpj,
    nome,
    codigoCarteiraAdministrador,
    contaCetip,
    contaSelic,
    abertoCaptacao,
    administrador,
    agenciaCustodia,
    benchmark,
    caracteristicasExtras,
    contaAplicacao,
    contaBritech,
    contaMovimentacao,
    contaResgate,
    contaTributada,
    contaUnica,
    contaUnicaOuSegregada,
    controlador,
    custodia,
    diasAplicacaoCotizacao,
    diasAplicacaoFinanceiro,
    diasResgateCotizacao,
    diasResgateFinanceiro,
    disponibilidade,
    duAplicacaoCotizacao,
    duAplicacaoFinanceiro,
    duResgateCotizacao,
    duResgateFinanceiro,
    indices,
    mesaResponsavel,
    mesasContribuidoras,
    minimoAplicacao,
    minimoMovimentacao,
    minimoSaldo,
    publicoAlvo,
    resumoEstrategias,
    taxaAdministracao,
    taxaPerformance,
    textoLivreAplicacaoCotizacao,
    textoLivreAplicacaoFinanceiro,
    textoLivreResgateCotizacao,
    textoLivreResgateFinanceiro,
    tickerB3,
    tipoFundo,
  } = dadosProvider;

  const atualizacao_fundo = {
    isin,
    mnemonico,
    cnpj,
    nome,
    aberto_para_captacao: abertoCaptacao,
    codigo_brit: isNaN(Number(contaBritech)) ? null : Number(contaBritech),
    codigo_carteira: codigoCarteiraAdministrador,
    conta_cetip: contaCetip,
    conta_selic: contaSelic,
    fundo_disponibilidade_id: disponibilidade,
    ticker_b3: tickerB3.trim() || null,
    fundo_administrador_id: administrador?.id ?? null,
    codigo_carteira_administrador: "",
    fundo_controlador_id: controlador?.id ?? null,
    agencia_bancaria_custodia: agenciaCustodia,
    conta_aplicacao:
      contaUnicaOuSegregada === "u" ? contaUnica : contaAplicacao,
    conta_resgate: contaUnicaOuSegregada === "u" ? contaUnica : contaResgate,
    conta_movimentacao:
      contaUnicaOuSegregada === "u" ? contaUnica : contaMovimentacao,
    conta_tributada:
      contaUnicaOuSegregada === "u" ? contaUnica : contaTributada,
    minimo_aplicacao: minimoAplicacao,
    minimo_movimentacao: minimoMovimentacao,
    minimo_saldo: minimoSaldo,
    cotizacao_aplicacao: diasAplicacaoCotizacao,
    cotizacao_aplicacao_sao_dias_uteis: duAplicacaoCotizacao,
    cotizacao_aplicacao_detalhes: textoLivreAplicacaoCotizacao,
    cotizacao_resgate: diasResgateCotizacao,
    cotizacao_resgate_sao_dias_uteis: duResgateCotizacao,
    cotizacao_resgate_detalhes: textoLivreResgateCotizacao,
    financeiro_aplicacao: diasAplicacaoFinanceiro,
    financeiro_aplicacao_sao_dias_uteis: duAplicacaoFinanceiro,
    financeiro_aplicacao_detalhes: textoLivreAplicacaoFinanceiro,
    financeiro_resgate: diasResgateFinanceiro,
    financeiro_resgate_sao_dias_uteis: duResgateFinanceiro,
    financeiro_resgate_detalhes: textoLivreResgateFinanceiro,
    publico_alvo_id: publicoAlvo || null,
    benchmark,
    taxa_performance: taxaPerformance,
    taxa_administracao: taxaAdministracao,
    resumo_estrategias: resumoEstrategias,
    indices,
    mesa_responsavel: mesaResponsavel?.id ?? null,
    mesas_contribuidoras: mesasContribuidoras.map((m) => m.id),
    caracteristicas_extras: caracteristicasExtras.map((c) => c.id),
    remover_documentos: documentos
      .filter((d) => d.estado === EstadoArquivoEnum.remover)
      .map((d) => d.id),
  };

  return {
    metadados_documentos,
    atualizacao_fundo,
  };
};
