import {
  EventoAlocacaoOperador,
  EventoAprovacaoBackoffice,
} from "@/lib/types/api/iv/v1";
import NoAbstrato from "../NoAbstrato";
import { BotaoDetalhesAlocacao } from "./BotaoDetalhesAlocacao";

export default class NoAprovacaoBackoffice extends NoAbstrato {
  public eventoAprovacao: EventoAprovacaoBackoffice | null = null;
  public eventoAlocacaoReferente: EventoAlocacaoOperador | null = null;

  public prefixo(): string {
    return "aloc-bo-";
  }
  public label(): string {
    return "Aprovação Backoffice";
  }

  public detalhes() {
    if (!this.eventoAlocacaoReferente) return "";
    const ap = this.eventoAprovacao;
    return (
      <BotaoDetalhesAlocacao
        operacao={this.eventoAlocacaoReferente.operacao}
        habilitar_controles={true}
        mostrar_usuario="aprovacao"
        resposta_backoffice={
          ap
            ? {
                aprovacao: ap.aprovacao,
                data: ap.criado_em,
                motivo: ap.motivo,
                usuario: { ...ap.usuario, devices: [] },
              }
            : undefined
        }
      />
    );
  }
}
