import { Edge } from "reactflow";
import GrafoFluxo from "./GrafoFluxo";
import { companies } from "./companies";
import { EstadoNo, No, NoData } from "./tipos";
import { getColorHex } from "@/app/theme";

import { aguardando, ok, recusado } from "../../nodes";
import React from "react";

const makePos = () => ({ x: 0, y: 0 });

export default abstract class NoAbstrato {
  protected _no: No;
  protected _estado: EstadoNo;

  public passado: boolean;

  public abstract prefixo(): string;
  public abstract label(): string;
  public detalhes(): React.ReactNode | undefined {
    return undefined;
  }

  constructor(
    protected grafo: GrafoFluxo,
    id: string,
    data?: NoData,
  ) {
    this.passado = false;
    this._estado = EstadoNo.AGUARDANDO;
    this._no = {
      id: this.prefixo() + id,
      type: "company-in-out",
      position: makePos(),
      data: {
        label: this.label(),
        company: companies.vanguarda,
        status: { ...aguardando(), pending: false },
        ...data,
      },
    };
    this.grafo.adicionarNos([this]);
  }

  get no() {
    return this._no;
  }

  get id() {
    return this._no.id;
  }

  get estado() {
    return this._estado;
  }

  private alterarEstadoAresta(aresta: Edge, estado: EstadoNo) {
    switch (this.estado) {
      case EstadoNo.AGUARDANDO:
      case EstadoNo.PENDENTE:
        {
          aresta.animated = true;
          aresta.style = { stroke: getColorHex("cinza.main") };
        }
        break;
      case EstadoNo.DESATIVADO:
        {
          aresta.animated = false;
          aresta.style = { stroke: getColorHex("cinza.main") };
        }
        break;
      case EstadoNo.SUCESSO:
        {
          aresta.animated = false;
          aresta.style = { stroke: getColorHex("verde.main") };
        }
        break;
      case EstadoNo.FALHA:
        {
          aresta.animated = false;
          aresta.style = { stroke: getColorHex("rosa.main") };
        }
        break;
    }
  }

  public alterarEstado(estado: EstadoNo, texto?: string) {
    if (this._estado === estado) return;
    this._estado = estado;
    switch (estado) {
      case EstadoNo.PENDENTE:
        this._no.data.status = { ...aguardando(texto), pending: true };
        break;
      case EstadoNo.AGUARDANDO:
        this._no.data.status = { ...aguardando(texto), pending: false };
        break;
      case EstadoNo.DESATIVADO:
        this._no.data.status = {
          ...aguardando(texto),
          pending: false,
          bgColor: "cinza.main",
        };
        break;
      case EstadoNo.SUCESSO:
        this._no.data.status = { ...ok(texto), pending: false };
        break;
      case EstadoNo.FALHA:
        this._no.data.status = { ...recusado(texto), pending: false };
        break;
    }
    this.arestasSaida().forEach((aresta) =>
      this.alterarEstadoAresta(aresta, this._estado),
    );
    this.atualizar();
  }

  public arestasSaida() {
    return this.grafo.arestas.filter((e) => e.source === this._no.id);
  }

  public adicionarArestaSaida(alvo: NoAbstrato) {
    const aresta: Edge = {
      id: `${this._no.id}|${alvo.id}`,
      source: this._no.id,
      target: alvo.id,
    };
    this.alterarEstadoAresta(aresta, this.estado);
    this.grafo.adicionarArestas([aresta]);
  }

  public renomear(novoId: string) {
    const antigo = this._no.id;
    const novo = this.prefixo() + novoId;
    this._no.id = novo;
    this.grafo.arestas.forEach((a) => {
      if (a.source === antigo) {
        a.source = novo;
        a.id = `${novo}|${a.target}`;
      }
      if (a.target === antigo) {
        a.target = novo;
        a.id = `${a.source}|${novo}`;
      }
    });
  }

  public atualizar() {
    this.no.data.details = this.detalhes();
  }
}
