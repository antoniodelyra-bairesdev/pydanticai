"use client";

import {
  DisponibilidadeFundoEnum,
  Fundo,
  FundoCaracteristicaExtra,
  FundoDetalhes,
  FundoIndiceBenchmark,
  InstituicaoFinanceira,
  Mesa,
  PublicoAlvoEnum,
  TipoFundoEnum,
} from "@/lib/types/api/iv/v1";
import {
  Dispatch,
  ReactNode,
  SetStateAction,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

export type FundoDetalhesProviderProps = {
  fundoInicial: FundoDetalhes;
  children?: ReactNode;
};

export function useFundoDetalhes() {
  const ctx = useContext(FundoDetalhesContext);
  return ctx;
}

export function FundoDetalhesProvider({
  fundoInicial,
  children,
}: FundoDetalhesProviderProps) {
  console.log({ fundoInicial });

  const [editando, setEditando] = useState(false);
  const [fundoAtualizado, setFundoAtualizado] = useState(fundoInicial);

  // Informações gerais
  const [nome, setNome] = useState("");
  const [gestor, setGestor] = useState("");
  const [cogestor, setCogestor] = useState("");

  const [abertoCaptacao, setAbertoCaptacao] = useState(true);
  const [disponibilidade, setDisponibilidade] = useState(
    DisponibilidadeFundoEnum.Aberto,
  );

  const [tickerB3, setTickerB3] = useState("");

  const [tipoFundo, setTipoFundo] = useState(TipoFundoEnum.Aberto);
  const [cnpj, setCnpj] = useState("");
  const [isin, setIsin] = useState("");
  const [mnemonico, setMnemonico] = useState("");

  // Administração
  const [administrador, setAdministrador] = useState<InstituicaoFinanceira>();
  const [codigoCarteiraAdministrador, setCodigoCarteiraAdministrador] =
    useState("");

  const [controlador, setControlador] = useState<InstituicaoFinanceira>();

  const [custodia, setCustodia] = useState<InstituicaoFinanceira>();
  const [agenciaCustodia, setAgenciaCustodia] = useState("");

  const [contaUnicaOuSegregada, setContaUnicaOuSegregada] = useState<"u" | "s">(
    "u",
  );

  const [contaUnica, setContaUnica] = useState("");

  const [contaAplicacao, setContaAplicacao] = useState("");
  const [contaResgate, setContaResgate] = useState("");
  const [contaMovimentacao, setContaMovimentacao] = useState("");
  const [contaTributada, setContaTributada] = useState("");

  // Cadastros e contas
  const [contaBritech, setContaBritech] = useState("");
  const [contaCetip, setContaCetip] = useState("");
  const [contaSelic, setContaSelic] = useState("");

  // Datas e limites
  const [diasAplicacaoCotizacao, setDiasAplicacaoCotizacao] = useState(0);
  const [duAplicacaoCotizacao, setDuAplicacaoCotizacao] = useState(true);
  const [textoLivreAplicacaoCotizacao, setTextoLivreAplicacaoCotizacao] =
    useState("");

  const [diasAplicacaoFinanceiro, setDiasAplicacaoFinanceiro] = useState(0);
  const [duAplicacaoFinanceiro, setDuAplicacaoFinanceiro] = useState(true);
  const [textoLivreAplicacaoFinanceiro, setTextoLivreAplicacaoFinanceiro] =
    useState("");

  const [diasResgateCotizacao, setDiasResgateCotizacao] = useState(0);
  const [duResgateCotizacao, setDuResgateCotizacao] = useState(true);
  const [textoLivreResgateCotizacao, setTextoLivreResgateCotizacao] =
    useState("");

  const [diasResgateFinanceiro, setDiasResgateFinanceiro] = useState(0);
  const [duResgateFinanceiro, setDuResgateFinanceiro] = useState(true);
  const [textoLivreResgateFinanceiro, setTextoLivreResgateFinanceiro] =
    useState("");

  const [publicoAlvo, setPublicoAlvo] = useState<PublicoAlvoEnum>(
    PublicoAlvoEnum.Investidor_Geral,
  );
  const [minimoAplicacao, setMinimoAplicacao] = useState(0);
  const [minimoMovimentacao, setMinimoMovimentacao] = useState(0);
  const [minimoSaldo, setMinimoSaldo] = useState(0);
  // Benchmark e taxas
  const [benchmark, setBenchmark] = useState("");
  const [indices, setIndices] = useState<FundoIndiceBenchmark[]>([]);
  const [taxaPerformance, setTaxaPerformance] = useState("");
  const [taxaAdministracao, setTaxaAdministracao] = useState("");
  // Gestão
  const [mesaResponsavel, setMesaResponsavel] = useState<Mesa>();
  const [mesasContribuidoras, setMesasContribuidoras] = useState<Mesa[]>([]);
  const [resumoEstrategias, setResumoEstrategias] = useState("");
  const [caracteristicasExtras, setCaracteristicasExtras] = useState<
    FundoCaracteristicaExtra[]
  >([]);
  // Documentos

  const reset = useCallback(() => {
    const contasIguais =
      fundoAtualizado.conta_aplicacao === fundoAtualizado.conta_movimentacao &&
      fundoAtualizado.conta_movimentacao === fundoAtualizado.conta_resgate &&
      fundoAtualizado.conta_resgate === fundoAtualizado.conta_tributada;

    // Informações gerais
    setNome(fundoAtualizado.nome);
    setGestor("");
    setCogestor("");
    setAbertoCaptacao(fundoAtualizado.aberto_para_captacao);
    setDisponibilidade(
      fundoAtualizado.fundo_disponibilidade_id ??
        DisponibilidadeFundoEnum.Fechado,
    );
    setTickerB3(fundoAtualizado.ticker_b3 ?? "");
    setTipoFundo(TipoFundoEnum.Aberto);
    setCnpj(fundoAtualizado.cnpj);
    setIsin(fundoAtualizado.isin ?? "");
    setMnemonico(fundoAtualizado.mnemonico ?? "");
    // Administração
    setAdministrador(fundoAtualizado.administrador);
    setCodigoCarteiraAdministrador(fundoAtualizado.codigo_carteira ?? "");
    setControlador(fundoAtualizado.controlador);
    setCustodia(fundoAtualizado?.custodiante ?? undefined);
    setAgenciaCustodia(fundoAtualizado.agencia_bancaria_custodia ?? "");
    setContaUnicaOuSegregada(contasIguais ? "u" : "s");
    setContaUnica(contasIguais ? (fundoAtualizado.conta_aplicacao ?? "") : "");
    setContaAplicacao(fundoAtualizado.conta_aplicacao ?? "");
    setContaResgate(fundoAtualizado.conta_resgate ?? "");
    setContaMovimentacao(fundoAtualizado.conta_movimentacao ?? "");
    setContaTributada(fundoAtualizado.conta_tributada ?? "");
    // Cadastros e contas
    setContaBritech(String(fundoAtualizado.codigo_brit ?? ""));
    setContaCetip(fundoAtualizado.conta_cetip ?? "");
    setContaSelic(fundoAtualizado.conta_selic ?? "");
    // Datas e limites
    setDiasAplicacaoCotizacao(fundoAtualizado.cotizacao_aplicacao ?? 0);
    setDuAplicacaoCotizacao(
      fundoAtualizado.cotizacao_aplicacao_sao_dias_uteis ?? false,
    );
    setTextoLivreAplicacaoCotizacao(
      fundoAtualizado.cotizacao_aplicacao_detalhes ?? "",
    );

    setDiasAplicacaoFinanceiro(fundoAtualizado.financeiro_aplicacao ?? 0);
    setDuAplicacaoFinanceiro(
      fundoAtualizado.financeiro_aplicacao_sao_dias_uteis ?? false,
    );
    setTextoLivreAplicacaoFinanceiro(
      fundoAtualizado.financeiro_aplicacao_detalhes ?? "",
    );

    setDiasResgateCotizacao(fundoAtualizado.cotizacao_resgate ?? 0);
    setDuResgateCotizacao(
      fundoAtualizado.cotizacao_resgate_sao_dias_uteis ?? false,
    );
    setTextoLivreResgateCotizacao(
      fundoAtualizado.cotizacao_resgate_detalhes ?? "",
    );

    setDiasResgateFinanceiro(fundoAtualizado.financeiro_resgate ?? 0);
    setDuResgateFinanceiro(
      fundoAtualizado.financeiro_resgate_sao_dias_uteis ?? false,
    );
    setTextoLivreResgateFinanceiro(
      fundoAtualizado.financeiro_resgate_detalhes ?? "",
    );

    setPublicoAlvo((fundoAtualizado.publico_alvo_id as any) || 0);
    setMinimoAplicacao(fundoAtualizado.minimo_aplicacao ?? 0);
    setMinimoMovimentacao(fundoAtualizado.minimo_movimentacao ?? 0);
    setMinimoSaldo(fundoAtualizado.minimo_saldo ?? 0);
    // Benchmark e taxas
    setBenchmark(fundoAtualizado.benchmark ?? "");
    setIndices(fundoAtualizado.indices);
    setTaxaPerformance(fundoAtualizado.taxa_performance ?? "");
    setTaxaAdministracao(fundoAtualizado.taxa_administracao ?? "");
    // Gestão
    setMesaResponsavel(fundoAtualizado.mesa_responsavel ?? undefined);
    setMesasContribuidoras(fundoAtualizado.mesas_contribuidoras);
    setResumoEstrategias(fundoAtualizado.resumo_estrategias ?? "");
    setCaracteristicasExtras(fundoAtualizado.caracteristicas_extras);
  }, [fundoAtualizado]);

  useEffect(() => {
    reset();
  }, []);

  return (
    <FundoDetalhesContext.Provider
      value={{
        reset,
        editando,
        setEditando,
        fundoAtualizado,
        setFundoAtualizado,
        nome,
        setNome,
        gestor,
        setGestor,
        cogestor,
        setCogestor,
        abertoCaptacao,
        setAbertoCaptacao,
        disponibilidade,
        setDisponibilidade,
        tickerB3,
        setTickerB3,
        tipoFundo,
        setTipoFundo,
        cnpj,
        setCnpj,
        isin,
        setIsin,
        mnemonico,
        setMnemonico,
        //
        administrador,
        setAdministrador,
        codigoCarteiraAdministrador,
        setCodigoCarteiraAdministrador,
        controlador,
        setControlador,
        custodia,
        setCustodia,
        agenciaCustodia,
        setAgenciaCustodia,
        contaUnicaOuSegregada,
        setContaUnicaOuSegregada,
        contaUnica,
        setContaUnica,
        contaAplicacao,
        setContaAplicacao,
        contaResgate,
        setContaResgate,
        contaMovimentacao,
        setContaMovimentacao,
        contaTributada,
        setContaTributada,
        //
        contaBritech,
        setContaBritech,
        contaCetip,
        setContaCetip,
        contaSelic,
        setContaSelic,
        //
        diasAplicacaoCotizacao,
        setDiasAplicacaoCotizacao,
        duAplicacaoCotizacao,
        setDuAplicacaoCotizacao,
        textoLivreAplicacaoCotizacao,
        setTextoLivreAplicacaoCotizacao,
        diasAplicacaoFinanceiro,
        setDiasAplicacaoFinanceiro,
        duAplicacaoFinanceiro,
        setDuAplicacaoFinanceiro,
        textoLivreAplicacaoFinanceiro,
        setTextoLivreAplicacaoFinanceiro,
        diasResgateCotizacao,
        setDiasResgateCotizacao,
        duResgateCotizacao,
        setDuResgateCotizacao,
        textoLivreResgateCotizacao,
        setTextoLivreResgateCotizacao,
        diasResgateFinanceiro,
        setDiasResgateFinanceiro,
        duResgateFinanceiro,
        setDuResgateFinanceiro,
        textoLivreResgateFinanceiro,
        setTextoLivreResgateFinanceiro,
        publicoAlvo,
        setPublicoAlvo,
        minimoAplicacao,
        setMinimoAplicacao,
        minimoMovimentacao,
        setMinimoMovimentacao,
        minimoSaldo,
        setMinimoSaldo,
        //
        benchmark,
        setBenchmark,
        indices,
        setIndices,
        taxaPerformance,
        setTaxaPerformance,
        taxaAdministracao,
        setTaxaAdministracao,
        //
        mesaResponsavel,
        setMesaResponsavel,
        mesasContribuidoras,
        setMesasContribuidoras,
        resumoEstrategias,
        setResumoEstrategias,
        caracteristicasExtras,
        setCaracteristicasExtras,
      }}
    >
      {children}
    </FundoDetalhesContext.Provider>
  );
}

type Setter<T> = Dispatch<SetStateAction<T>>;
const noop = () => {};

type UnicaOuSegregada = "u" | "s";

export const FundoDetalhesContext = createContext<{
  reset: () => void;
  editando: boolean;
  setEditando: Setter<boolean>;
  fundoAtualizado: FundoDetalhes;
  setFundoAtualizado: Setter<FundoDetalhes>;
  nome: string;
  setNome: Setter<string>;
  gestor: string;
  setGestor: Setter<string>;
  cogestor: string;
  setCogestor: Setter<string>;
  abertoCaptacao: boolean;
  setAbertoCaptacao: Setter<boolean>;
  disponibilidade: DisponibilidadeFundoEnum;
  setDisponibilidade: Setter<DisponibilidadeFundoEnum>;
  tickerB3: string;
  setTickerB3: Setter<string>;
  tipoFundo: TipoFundoEnum;
  setTipoFundo: Setter<TipoFundoEnum>;
  cnpj: string;
  setCnpj: Setter<string>;
  isin: string;
  setIsin: Setter<string>;
  mnemonico: string;
  setMnemonico: Setter<string>;
  administrador: InstituicaoFinanceira | undefined;
  setAdministrador: Setter<InstituicaoFinanceira | undefined>;
  codigoCarteiraAdministrador: string;
  setCodigoCarteiraAdministrador: Setter<string>;
  controlador: InstituicaoFinanceira | undefined;
  setControlador: Setter<InstituicaoFinanceira | undefined>;
  custodia: InstituicaoFinanceira | undefined;
  setCustodia: Setter<InstituicaoFinanceira | undefined>;
  agenciaCustodia: string;
  setAgenciaCustodia: Setter<string>;
  contaUnicaOuSegregada: UnicaOuSegregada;
  setContaUnicaOuSegregada: Setter<UnicaOuSegregada>;
  contaUnica: string;
  setContaUnica: Setter<string>;
  contaAplicacao: string;
  setContaAplicacao: Setter<string>;
  contaResgate: string;
  setContaResgate: Setter<string>;
  contaMovimentacao: string;
  setContaMovimentacao: Setter<string>;
  contaTributada: string;
  setContaTributada: Setter<string>;
  contaBritech: string;
  setContaBritech: Setter<string>;
  contaCetip: string;
  setContaCetip: Setter<string>;
  contaSelic: string;
  setContaSelic: Setter<string>;
  diasAplicacaoCotizacao: number;
  setDiasAplicacaoCotizacao: Setter<number>;
  duAplicacaoCotizacao: boolean;
  setDuAplicacaoCotizacao: Setter<boolean>;
  textoLivreAplicacaoCotizacao: string;
  setTextoLivreAplicacaoCotizacao: Setter<string>;
  diasAplicacaoFinanceiro: number;
  setDiasAplicacaoFinanceiro: Setter<number>;
  duAplicacaoFinanceiro: boolean;
  setDuAplicacaoFinanceiro: Setter<boolean>;
  textoLivreAplicacaoFinanceiro: string;
  setTextoLivreAplicacaoFinanceiro: Setter<string>;
  diasResgateCotizacao: number;
  setDiasResgateCotizacao: Setter<number>;
  duResgateCotizacao: boolean;
  setDuResgateCotizacao: Setter<boolean>;
  textoLivreResgateCotizacao: string;
  setTextoLivreResgateCotizacao: Setter<string>;
  diasResgateFinanceiro: number;
  setDiasResgateFinanceiro: Setter<number>;
  duResgateFinanceiro: boolean;
  setDuResgateFinanceiro: Setter<boolean>;
  textoLivreResgateFinanceiro: string;
  setTextoLivreResgateFinanceiro: Setter<string>;
  publicoAlvo: PublicoAlvoEnum;
  setPublicoAlvo: Setter<PublicoAlvoEnum>;
  minimoAplicacao: number;
  setMinimoAplicacao: Setter<number>;
  minimoMovimentacao: number;
  setMinimoMovimentacao: Setter<number>;
  minimoSaldo: number;
  setMinimoSaldo: Setter<number>;
  benchmark: string;
  setBenchmark: Setter<string>;
  indices: FundoIndiceBenchmark[];
  setIndices: Setter<FundoIndiceBenchmark[]>;
  taxaPerformance: string;
  setTaxaPerformance: Setter<string>;
  taxaAdministracao: string;
  setTaxaAdministracao: Setter<string>;
  mesaResponsavel: Mesa | undefined;
  setMesaResponsavel: Setter<Mesa | undefined>;
  mesasContribuidoras: Mesa[];
  setMesasContribuidoras: Setter<Mesa[]>;
  resumoEstrategias: string;
  setResumoEstrategias: Setter<string>;
  caracteristicasExtras: FundoCaracteristicaExtra[];
  setCaracteristicasExtras: Setter<FundoCaracteristicaExtra[]>;
}>({
  reset: noop,
  editando: false,
  setEditando: noop,
  fundoAtualizado: {} as any,
  setFundoAtualizado: noop,
  nome: "",
  setNome: noop,
  gestor: "",
  setGestor: noop,
  cogestor: "",
  setCogestor: noop,
  abertoCaptacao: false,
  setAbertoCaptacao: noop,
  disponibilidade: DisponibilidadeFundoEnum.Aberto,
  setDisponibilidade: noop,
  tickerB3: "",
  setTickerB3: noop,
  tipoFundo: TipoFundoEnum.Aberto,
  setTipoFundo: noop,
  cnpj: "",
  setCnpj: noop,
  isin: "",
  setIsin: noop,
  mnemonico: "",
  setMnemonico: noop,
  administrador: {} as any,
  setAdministrador: noop,
  codigoCarteiraAdministrador: "",
  setCodigoCarteiraAdministrador: noop,
  controlador: {} as any,
  setControlador: noop,
  custodia: {} as any,
  setCustodia: noop,
  agenciaCustodia: "",
  setAgenciaCustodia: noop,
  contaUnicaOuSegregada: "u",
  setContaUnicaOuSegregada: noop,
  contaUnica: "",
  setContaUnica: noop,
  contaAplicacao: "",
  setContaAplicacao: noop,
  contaResgate: "",
  setContaResgate: noop,
  contaMovimentacao: "",
  setContaMovimentacao: noop,
  contaTributada: "",
  setContaTributada: noop,
  contaBritech: "",
  setContaBritech: noop,
  contaCetip: "",
  setContaCetip: noop,
  contaSelic: "",
  setContaSelic: noop,
  diasAplicacaoCotizacao: 0,
  setDiasAplicacaoCotizacao: noop,
  duAplicacaoCotizacao: false,
  setDuAplicacaoCotizacao: noop,
  textoLivreAplicacaoCotizacao: "",
  setTextoLivreAplicacaoCotizacao: noop,
  diasAplicacaoFinanceiro: 0,
  setDiasAplicacaoFinanceiro: noop,
  duAplicacaoFinanceiro: false,
  setDuAplicacaoFinanceiro: noop,
  textoLivreAplicacaoFinanceiro: "",
  setTextoLivreAplicacaoFinanceiro: noop,
  diasResgateCotizacao: 0,
  setDiasResgateCotizacao: noop,
  duResgateCotizacao: false,
  setDuResgateCotizacao: noop,
  textoLivreResgateCotizacao: "",
  setTextoLivreResgateCotizacao: noop,
  diasResgateFinanceiro: 0,
  setDiasResgateFinanceiro: noop,
  duResgateFinanceiro: false,
  setDuResgateFinanceiro: noop,
  textoLivreResgateFinanceiro: "",
  setTextoLivreResgateFinanceiro: noop,
  publicoAlvo: PublicoAlvoEnum.Investidor_Geral,
  setPublicoAlvo: noop,
  minimoAplicacao: 0,
  setMinimoAplicacao: noop,
  minimoMovimentacao: 0,
  setMinimoMovimentacao: noop,
  minimoSaldo: 0,
  setMinimoSaldo: noop,
  benchmark: "",
  setBenchmark: noop,
  indices: [],
  setIndices: noop,
  taxaPerformance: "",
  setTaxaPerformance: noop,
  taxaAdministracao: "",
  setTaxaAdministracao: noop,
  mesaResponsavel: undefined,
  setMesaResponsavel: noop,
  mesasContribuidoras: [],
  setMesasContribuidoras: noop,
  resumoEstrategias: "",
  setResumoEstrategias: noop,
  caracteristicasExtras: [],
  setCaracteristicasExtras: noop,
});
