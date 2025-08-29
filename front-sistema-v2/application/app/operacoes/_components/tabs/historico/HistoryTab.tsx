import { useEffect, useState } from "react";
import TriagemB3 from "../triagem-b3/TriagemB3";
import { CasamentoOperacaoVoice, OperacaoType } from "@/lib/types/api/iv/v1";
import { Progress, VStack } from "@chakra-ui/react";
import { useAsync, useHTTP } from "@/lib/hooks";
import { processarNegocios } from "../../ComprasVendas";

export default function HistoryTab() {
  const [dataConsulta, setDataConsulta] = useState("");
  const [negocios, setNegocios] = useState<OperacaoType[]>([]);

  const [carregando, iniciarCarregamento] = useAsync();
  const httpClient = useHTTP({ withCredentials: true });

  useEffect(() => {
    if (!dataConsulta) {
      setNegocios([]);
      return;
    }
    if (carregando) return;
    iniciarCarregamento(async () => {
      const response = await httpClient.fetch(
        "v1/operacoes?data=" + dataConsulta,
      );
      if (!response.ok) return;
      const dados = (await response.json()) as CasamentoOperacaoVoice[];
      setNegocios(processarNegocios(dados));
    });
  }, [dataConsulta]);

  return (
    <VStack gap={0} alignItems="stretch">
      <Progress
        visibility={carregando ? "visible" : "hidden"}
        isIndeterminate
        colorScheme="verde"
        h="8px"
        mb="-8px"
      />
      <TriagemB3
        negocios={negocios}
        historico
        onDataConsultaChange={(data) => setDataConsulta(data)}
      />
    </VStack>
  );
}
