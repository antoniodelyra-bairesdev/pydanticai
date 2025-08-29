import { Edge } from "reactflow";
import NoAbstrato from "./NoAbstrato";
import NoAcatoVoice from "./nos/NoAcatoVoice";
import {
  AlocacaoStatus,
  EventoAlocacaoOperador,
  EventoAprovacaoBackoffice,
  EventoAtualizacaoCustodiante,
  EventoEmissaoNumerosControle,
  EventoEnvioAlocacao,
  EventoOperacao,
  EventoOperacaoAcatoVoice,
  OperacaoType,
} from "@/lib/types/api/iv/v1";
import { EstadoNo, No } from "./tipos";
import NoAlocacaoOperador from "./nos/NoAlocacaoOperador";
import NoAprovacaoBackoffice from "./nos/NoAprovacaoBackoffice";
import NoEnvioMensagemFIX from "./nos/NoEnvioMensagemFIX";
import NoEmissaoNCN from "./nos/NoEmissaoNCN";
import NoNCN from "./nos/NoNCN";
import NoAprovacaoCustodiante from "./nos/NoAprovacaoCustodiante";
import { companies } from "./companies";
import NoResumoRegistro from "./nos/NoResumoRegistro";

export default class GrafoFluxo {
  private _nos: NoAbstrato[] = [];
  private _arestas: Edge[] = [];
  private _eventos: EventoOperacao[] = [];

  public operacao: OperacaoType;

  public passado: boolean = false;

  constructor(operacao: OperacaoType) {
    this.operacao = operacao;
  }

  public static makefluxoOperacoes(operacao: OperacaoType): GrafoFluxo {
    const grafo = new GrafoFluxo(operacao);
    const acato = new NoAcatoVoice(grafo);
    acato.alterarEstado(EstadoNo.PENDENTE);
    const aloc = new NoAlocacaoOperador(grafo, "inicial-null");
    aloc.alterarEstado(EstadoNo.PENDENTE);
    const ap = aloc.adicionarAprovacaoPendente(false);
    const msg = new NoEnvioMensagemFIX(grafo, "inicial-null");
    acato.adicionarArestaSaida(msg);
    ap.adicionarArestaSaida(msg);
    const emissaoNcn = new NoEmissaoNCN(grafo, "inicial");
    msg.adicionarArestaSaida(emissaoNcn);
    return grafo;
  }

  public foco: No[] = [];

  get nos() {
    return this._nos.map((_no) => _no.no);
  }

  get arestas() {
    return [...this._arestas];
  }

  public adicionarNos(nos: NoAbstrato[]) {
    nos.forEach((no) => (no.passado = this.passado));
    this._nos.push(...nos);
  }

  public adicionarArestas(arestas: Edge[]) {
    this._arestas.push(...arestas);
  }

  public encontrar<T extends NoAbstrato>(Tipo: { new (...args: any[]): T }) {
    return this._nos.filter((_no) => _no instanceof Tipo) as T[];
  }

  public adicionarEvento(evento: EventoOperacao) {
    this._eventos.push(evento);
    switch (evento.informacoes.tipo) {
      case "acato-voice":
        this.processaAcatoVoice(evento.informacoes);
        break;
      case "alocacao-operador":
        if (evento.informacoes.operacao.externa) {
          this.processaAlocacaoExterna(evento.informacoes);
        } else {
          this.processaAlocacaoInterna(evento.informacoes);
        }
        break;
      case "aprovacao-backoffice":
        const ncn = evento.informacoes.numero_controle_nome ?? "inicial";
        const sufixo = `${ncn}-null`;
        const noAp = this.encontrar(NoAprovacaoBackoffice).find((no) =>
          no.id.endsWith(sufixo),
        );
        if (!noAp) return;
        noAp.eventoAprovacao = evento.informacoes;
        if (evento.informacoes.aprovacao) {
          this.processaAprovacaoBackoffice(evento.informacoes, noAp);
        } else {
          this.processaReprovacaoBackoffice(evento.informacoes, noAp);
        }
        break;
      case "envio-alocacao":
        this.processaEnvioMensagemFIX(evento.informacoes);
        break;
      case "emissao-numeros-controle":
        this.processaEmissaoNCN(evento.informacoes);
        break;
      case "atualizacao-custodiante":
        this.processaAtualizacaoCustodiante(evento.informacoes);
        break;
    }
    this._nos.forEach((no) => {
      no.passado = this.passado;
      no.atualizar();
    });
  }

  private processaAcatoVoice(evento: EventoOperacaoAcatoVoice) {
    const no = this.encontrar(NoAcatoVoice).at(0);
    if (!no) return;
    no.alterarEstado(EstadoNo.SUCESSO);
    this.foco = [no.no];
  }

  private processaAlocacaoExterna(evento: EventoAlocacaoOperador) {
    if (!evento.operacao.externa) return;
    const id = String(evento.operacao.id);
    const registro_nome = evento.operacao.registro_nome ?? "inicial";
    const nosAlocacao = this.encontrar(NoAlocacaoOperador).filter((no) =>
      no.id.includes(`-${registro_nome}-`),
    );
    const nosAprovacao = this.encontrar(NoAprovacaoBackoffice).filter((no) =>
      no.id.includes(`-${registro_nome}-`),
    );
    const noEnvioInicial = this.encontrar(NoEnvioMensagemFIX).filter((no) =>
      no.id.endsWith(`-null`),
    );
    const noAcato = this.encontrar(NoAcatoVoice);
    const nosRegistro = [
      ...nosAlocacao,
      ...nosAprovacao,
      ...noEnvioInicial,
      ...noAcato,
    ];
    nosRegistro.forEach((no) => no.alterarEstado(EstadoNo.DESATIVADO));
    const noEventosPendentes = nosRegistro.filter((no) =>
      no.id.endsWith(`${registro_nome}-null`),
    );
    const ultimo =
      noEventosPendentes.length === 1
        ? noEventosPendentes[0]
        : noEventosPendentes.findLast(
            (no) => no instanceof NoAprovacaoBackoffice,
          );
    if (!ultimo) return;
    const noAlocacaoExterna = new NoAlocacaoOperador(
      this,
      `${registro_nome}-${id}`,
    );
    noAlocacaoExterna.eventoAlocacao = evento;
    noAlocacaoExterna.alterarEstado(EstadoNo.SUCESSO);
    ultimo.adicionarArestaSaida(noAlocacaoExterna);
    const noEmissao = this.encontrar(NoEmissaoNCN).find((no) =>
      no.id.endsWith("-inicial"),
    );
    if (noEmissao) {
      noAlocacaoExterna.adicionarArestaSaida(noEmissao);
    }
    [noAlocacaoExterna, ultimo].forEach((n) => n.atualizar());
    this.foco = [noAlocacaoExterna.no];
  }

  private processaAlocacaoInterna(evento: EventoAlocacaoOperador) {
    if (evento.operacao.externa) return;
    const id = String(evento.operacao.id);
    const registro_nome = evento.operacao.registro_nome ?? "inicial";
    const noAlocacaoPendente = this.encontrar(NoAlocacaoOperador).find((no) =>
      no.id.includes(`-${registro_nome}-null`),
    );
    if (!noAlocacaoPendente) return;
    noAlocacaoPendente.eventoAlocacao = evento;
    noAlocacaoPendente.renomear(`${registro_nome}-${id}`);
    noAlocacaoPendente.alterarEstado(EstadoNo.SUCESSO);
    noAlocacaoPendente.adicionarAprovacaoPendente();
    noAlocacaoPendente.atualizar();
    this.foco = [noAlocacaoPendente.no];
  }

  private processaAprovacaoBackoffice(
    evento: EventoAprovacaoBackoffice,
    noAp: NoAprovacaoBackoffice,
  ) {
    if (!evento.aprovacao) return;
    noAp.alterarEstado(EstadoNo.SUCESSO);
    noAp.renomear(`${evento.numero_controle_nome ?? "inicial"}-${evento.id}`);
    noAp.atualizar();
    this.foco = [noAp.no];
  }

  private processaReprovacaoBackoffice(
    evento: EventoAprovacaoBackoffice,
    noAp: NoAprovacaoBackoffice,
  ) {
    if (evento.aprovacao) return;
    const ncn = evento.numero_controle_nome ?? "inicial";
    const sufixo = `${ncn}-null`;
    noAp.alterarEstado(EstadoNo.FALHA);
    noAp.renomear(`${ncn}-${evento.id}`);
    const aloc = new NoAlocacaoOperador(this, sufixo);
    aloc.alterarEstado(EstadoNo.PENDENTE);
    aloc.adicionarAprovacaoPendente(false);
    noAp.atualizar();
    this.foco = [noAp.no];
  }

  private processaEnvioMensagemFIX(evento: EventoEnvioAlocacao) {
    const ncn =
      evento.mensagem.registro_nome?.numero_controle_nome ?? "inicial";
    const id = evento.mensagem.id;
    const noEnvio = this.encontrar(NoEnvioMensagemFIX).find((no) =>
      no.id.endsWith(`-${ncn}-${evento.mensagem.erro ? id : "null"}`),
    );
    if (!noEnvio) return;
    noEnvio.alterarEstado(
      evento.mensagem.erro ? EstadoNo.FALHA : EstadoNo.SUCESSO,
    );
    this.foco = [noEnvio.no];
  }

  private processaEmissaoNCN(evento: EventoEmissaoNumerosControle) {
    this.foco = [];
    const noEmissaoNCN = this.encontrar(NoEmissaoNCN).find((no) =>
      no.id.endsWith(`-inicial`),
    );
    if (!noEmissaoNCN) return;
    noEmissaoNCN.alterarEstado(EstadoNo.SUCESSO);
    evento.quebras.forEach((quebra) => {
      const idNcn = String(quebra.id);
      const noNCN = new NoNCN(
        this,
        idNcn,
        quebra.numero_controle_nome,
        quebra.quantidade,
      );
      noNCN.alterarEstado(EstadoNo.SUCESSO);
      noNCN.atualizar();
      noEmissaoNCN.adicionarArestaSaida(noNCN);
      noEmissaoNCN.registros.push(quebra);
      const [primeiroNome, segundoNome] = quebra.fundo.nome_custodiante
        .toLowerCase()
        .split(" ");
      const custodiante =
        companies[primeiroNome] ??
        companies[segundoNome] ??
        companies.nao_registrado;
      const noCust = new NoAprovacaoCustodiante(
        this,
        "cust-" + idNcn,
        custodiante,
        quebra.fundo.nome,
      );
      const noCustCtp = new NoAprovacaoCustodiante(
        this,
        "cust-ctp-" + idNcn,
        companies.custodiante_contraparte,
      );
      noNCN.adicionarArestaSaida(noCust);
      noNCN.adicionarArestaSaida(noCustCtp);
      const noResumo = new NoResumoRegistro(this, idNcn);
      noCust.adicionarArestaSaida(noResumo);
      noCustCtp.adicionarArestaSaida(noResumo);
      this.foco.push(noNCN.no, noCust.no, noCustCtp.no, noResumo.no);
    });
    noEmissaoNCN.atualizar();
  }

  private processaAtualizacaoCustodiante(evento: EventoAtualizacaoCustodiante) {
    const noResumo = this.encontrar(NoResumoRegistro).find((no) =>
      no.id.endsWith(`-${evento.registro_nome_id}`),
    );
    const noCust = this.encontrar(NoAprovacaoCustodiante).find((no) =>
      no.id.endsWith(`cust-${evento.registro_nome_id}`),
    );
    const noCustCtp = this.encontrar(NoAprovacaoCustodiante).find((no) =>
      no.id.endsWith(`cust-ctp-${evento.registro_nome_id}`),
    );
    if (!noResumo || !noCust || !noCustCtp) return;
    noResumo.status(evento.status);
    switch (evento.status) {
      case AlocacaoStatus.Pendente_Confirmação_Custodiante:
        return;
      case AlocacaoStatus.Pendente_Confirmação_Contraparte_Custodiante:
        {
          noCust.alterarEstado(EstadoNo.SUCESSO);
          noCustCtp.alterarEstado(EstadoNo.AGUARDANDO);
        }
        break;
      case AlocacaoStatus.Rejeitado_pelo_Custodiante:
        {
          noCust.alterarEstado(EstadoNo.FALHA);
          noCustCtp.alterarEstado(EstadoNo.DESATIVADO);
        }
        break;
      case AlocacaoStatus.Rejeitado_pela_Contraparte_Custodiante:
        {
          noCust.alterarEstado(EstadoNo.DESATIVADO);
          noCustCtp.alterarEstado(EstadoNo.FALHA);
        }
        break;
      case AlocacaoStatus.Confirmado_pelo_Custodiante:
        {
          noCust.alterarEstado(EstadoNo.SUCESSO);
          noCustCtp.alterarEstado(EstadoNo.AGUARDANDO);
        }
        break;
      case AlocacaoStatus.Disponível_para_Registro:
        {
          noCust.alterarEstado(EstadoNo.SUCESSO);
          noCustCtp.alterarEstado(EstadoNo.SUCESSO);
        }
        break;
      case AlocacaoStatus.Pendente_de_Realocação_da_Contraparte:
        {
          noCust.alterarEstado(EstadoNo.AGUARDANDO);
          noCustCtp.alterarEstado(EstadoNo.AGUARDANDO);
        }
        break;
      case AlocacaoStatus.Realocado:
        {
          noCust.alterarEstado(EstadoNo.DESATIVADO);
          noCustCtp.alterarEstado(EstadoNo.DESATIVADO);
        }
        break;
    }
  }
}
