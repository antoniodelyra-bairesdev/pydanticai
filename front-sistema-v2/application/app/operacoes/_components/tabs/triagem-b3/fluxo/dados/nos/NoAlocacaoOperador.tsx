import {
  EventoAlocacaoOperador,
  EventoAprovacaoBackoffice,
} from "@/lib/types/api/iv/v1";
import NoAbstrato from "../NoAbstrato";
import NoAprovacaoBackoffice from "./NoAprovacaoBackoffice";
import { EstadoNo } from "../tipos";
import { BotaoDetalhesAlocacao } from "./BotaoDetalhesAlocacao";

export default class NoAlocacaoOperador extends NoAbstrato {
  public eventoAlocacao: EventoAlocacaoOperador | null = null;
  public eventoAprovacaoReferente: EventoAprovacaoBackoffice | null = null;
  public proximoNoAprovacao: NoAprovacaoBackoffice | null = null;

  public prefixo(): string {
    return "aloc-op-";
  }
  public label(): string {
    return "Alocação interna";
  }

  public detalhes() {
    if (!this.eventoAlocacao) return;
    return (
      <BotaoDetalhesAlocacao
        operacao={this.eventoAlocacao.operacao}
        mostrar_usuario="alocacao"
        habilitar_controles={false}
      />
    );
  }

  public adicionarAprovacaoPendente(pendente = true) {
    let ap = this.proximoNoAprovacao;
    if (!ap) {
      ap = new NoAprovacaoBackoffice(this.grafo, "inicial-null");
      this.adicionarArestaSaida(ap);
      this.proximoNoAprovacao = ap;
    }
    ap.alterarEstado(pendente ? EstadoNo.PENDENTE : EstadoNo.AGUARDANDO);
    ap.eventoAlocacaoReferente = this.eventoAlocacao;
    ap.atualizar();
    return ap;
  }
}
