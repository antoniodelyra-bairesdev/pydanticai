import GrafoFluxo from "../GrafoFluxo";
import NoAbstrato from "../NoAbstrato";
import { companies } from "../companies";
import { Company } from "../tipos";

export default class NoAprovacaoCustodiante extends NoAbstrato {
  private _nomeFundo?: string;
  constructor(
    grafo: GrafoFluxo,
    id: string,
    empresa: Company,
    nomeFundo?: string,
  ) {
    super(grafo, id);
    this._nomeFundo = nomeFundo;
    this.no.data = { ...this.no.data, company: empresa };
    this.atualizar();
  }

  public prefixo() {
    return "aprovacao-custodiante-";
  }
  public label() {
    return "Aprovação";
  }
  public detalhes() {
    return this._nomeFundo;
  }
}
