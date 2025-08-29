import GrafoFluxo from "../GrafoFluxo";
import NoAbstrato from "../NoAbstrato";

export default class NoAcatoVoice extends NoAbstrato {
  constructor(grafo: GrafoFluxo) {
    super(grafo, "");
  }

  public prefixo(): string {
    return "acato-voice";
  }
  public label(): string {
    return "Acato Voice";
  }
}
