import GrafoFluxo from "../GrafoFluxo";
import NoAbstrato from "../NoAbstrato";
import { companies } from "../companies";
import { RegistroNoMe } from "@/lib/types/api/iv/v1";
import { BotaoDetalhesEmissao } from "./BotaoDetalhesEmissao";

export default class NoEmissaoNCN extends NoAbstrato {
  public registros: RegistroNoMe[] = [];

  constructor(grafo: GrafoFluxo, id: string) {
    super(grafo, id);
    this.no.data = { ...this.no.data, company: companies.b3 };
  }

  public prefixo() {
    return "emissao-ncn-";
  }
  public label() {
    return "Emissão registros NoMe";
  }

  public detalhes() {
    return (
      <BotaoDetalhesEmissao
        preco_unitario={this.grafo.operacao.preco_unitario}
        registros={this.registros}
      />
    );
  }
}
