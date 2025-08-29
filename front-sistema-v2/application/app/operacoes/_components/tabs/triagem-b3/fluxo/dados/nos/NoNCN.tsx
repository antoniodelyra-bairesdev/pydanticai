import GrafoFluxo from "../GrafoFluxo";
import NoAbstrato from "../NoAbstrato";
import { companies } from "../companies";

export default class NoNCN extends NoAbstrato {
  private _numero_controle: string;
  private _quantidade: number;

  constructor(grafo: GrafoFluxo, id: string, ncn: string, quantidade: number) {
    super(grafo, ncn);
    this._numero_controle = ncn;
    this._quantidade = quantidade;
    this.no.data = {
      ...this.no.data,
      label: this.label(),
      company: companies.b3,
    };
    this.atualizar();
  }

  public get numero_controle() {
    return this._numero_controle;
  }

  public prefixo() {
    return "registro-nome-";
  }
  public label() {
    return "Registro NoMe " + this.numero_controle;
  }

  public detalhes() {
    return "Quantidade: " + this._quantidade;
  }
}
