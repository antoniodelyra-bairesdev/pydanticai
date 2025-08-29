import { AlocacaoStatus } from "@/lib/types/api/iv/v1";
import { aguardando } from "../../../nodes";
import GrafoFluxo from "../GrafoFluxo";
import NoAbstrato from "../NoAbstrato";
import { companies } from "../companies";

export default class NoResumoRegistro extends NoAbstrato {
  constructor(grafo: GrafoFluxo, id: string) {
    super(grafo, id);
    this._no = {
      ...this._no,
      type: "in-out",
      data: {
        label: "",
        status: {
          ...aguardando("Pendente Confirmação Custodiante"),
          bgColor: "cinza.100",
        },
      },
    };
  }

  public prefixo() {
    return "resumo-";
  }
  public label() {
    return "";
  }

  public status(status: AlocacaoStatus) {
    switch (status) {
      case AlocacaoStatus.Pendente_Confirmação_Custodiante:
        return;
      case AlocacaoStatus.Pendente_Confirmação_Contraparte_Custodiante:
        {
          this.no.data.status.color = "cinza.400";
          this.no.data.status.bgColor = "cinza.100";
          this.no.data.status.text =
            "Pendente Confirmação Contraparte Custodiante";
        }
        break;
      case AlocacaoStatus.Rejeitado_pelo_Custodiante:
        {
          this.no.data.status.color = "rosa.main";
          this.no.data.status.bgColor = "rosa.100";
          this.no.data.status.text = "Rejeitado pelo Custodiante";
        }
        break;
      case AlocacaoStatus.Rejeitado_pela_Contraparte_Custodiante:
        {
          this.no.data.status.color = "rosa.main";
          this.no.data.status.bgColor = "rosa.100";
          this.no.data.status.text = "Rejeitado pela Contraparte Custodiante";
        }
        break;
      case AlocacaoStatus.Confirmado_pelo_Custodiante:
        {
          this.no.data.status.color = "rosa.main";
          this.no.data.status.bgColor = "rosa.100";
          this.no.data.status.text = "Rejeitado pela Contraparte Custodiante";
        }
        break;
      case AlocacaoStatus.Disponível_para_Registro:
        {
          this.no.data.status.color = "verde.main";
          this.no.data.status.bgColor = "verde.100";
          this.no.data.status.text = "Disponível para Registro";
        }
        break;
      case AlocacaoStatus.Pendente_de_Realocação_da_Contraparte:
        {
          this.no.data.status.color = "cinza.400";
          this.no.data.status.bgColor = "cinza.100";
          this.no.data.status.text = "Pendente de Realocação da Contraparte";
        }
        break;
      case AlocacaoStatus.Realocado:
        {
          this.no.data.status.color = "cinza.400";
          this.no.data.status.bgColor = "cinza.100";
          this.no.data.status.text = "Realocado";
        }
        break;
      case AlocacaoStatus.Pendente_de_Realocação:
        {
          this.no.data.status.color = "rosa.main";
          this.no.data.status.bgColor = "rosa.100";
          this.no.data.status.text = "Pendente de Realocação";
        }
        break;
    }
  }
}
