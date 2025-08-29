import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import Hint from "@/app/_components/texto/Hint";
import { useHTTP, useWebSockets } from "@/lib/hooks";
import { CorretoraResumo, EventoOperacao } from "@/lib/types/api/iv/v1";
import {
  WSJSONMessage,
  WSMessage,
  WSMessageType,
} from "@/lib/types/api/iv/websockets";
import {
  Button,
  HStack,
  Input,
  Table,
  TableContainer,
  Tbody,
  Td,
  Tr,
  VStack,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";

export type ModalCorretoraProps = {
  isOpen: boolean;
  onClose: () => void;
  nomeContaInicial?: string;
};

export default function ModalCorretoras({
  isOpen,
  onClose,
  nomeContaInicial,
}: ModalCorretoraProps) {
  const [corretoras, setCorretoras] = useState<CorretoraResumo[]>([]);

  const [nomeCorretora, setNomeCorretora] = useState("");
  const [nomeConta, setNomeConta] = useState(nomeContaInicial ?? "");

  useEffect(() => {
    setNomeConta(nomeContaInicial ?? "");
  }, [nomeContaInicial]);

  const httpClient = useHTTP({ withCredentials: true });
  const { connection } = useWebSockets();

  const buscarCorretoras = async () => {
    await httpClient.fetch("v1/operacoes/corretoras", {
      hideToast: { success: true },
    });
  };

  const adicionarCorretora = async () => {
    if (!nomeCorretora || !nomeConta) return;
    const body = JSON.stringify({
      nome: nomeCorretora,
      conta: nomeConta,
    });
    await httpClient.fetch("v1/operacoes/corretoras", {
      hideToast: { success: true },
      method: "POST",
      body,
    });
  };

  useEffect(() => {
    if (!isOpen) return;
    buscarCorretoras();
  }, [isOpen]);

  useEffect(() => {
    const onMessage = (ev: MessageEvent) => {
      const data = JSON.parse(ev.data) as WSMessage;
      const type = data.type;
      if (type !== WSMessageType.JSON) return;
      const msg = data.content as WSJSONMessage;
      const body = msg.body as EventoOperacao;
      if (body.informacoes.tipo !== "corretoras") return;
      setCorretoras(body.informacoes.corretoras);
    };
    connection?.addEventListener("message", onMessage);
    return () => {
      connection?.removeEventListener("message", onMessage);
    };
  }, [connection]);

  return (
    <ConfirmModal
      title="Listagem de corretoras"
      isOpen={isOpen}
      overflow="auto"
      onClose={() => {
        onClose();
      }}
      hideConfirmButton={true}
      cancelContent="Fechar"
      size="4xl"
    >
      <VStack w="100%" maxH="60vh" overflow="auto" alignItems="stretch">
        <TableContainer>
          <Table>
            <Tbody>
              {corretoras.flatMap((corretora) =>
                corretora.contas.map((conta, iConta, contas) => (
                  <Tr key={corretora.nome + conta}>
                    {iConta === 0 && (
                      <Td
                        p="4px"
                        rowSpan={contas.length}
                        fontWeight="bold"
                        fontSize="sm"
                      >
                        {corretora.nome}
                      </Td>
                    )}
                    <Td p="4px" fontSize="sm">
                      {conta}
                    </Td>
                  </Tr>
                )),
              )}
            </Tbody>
          </Table>
        </TableContainer>
        <HStack alignItems="flex-end">
          <VStack flex={2} gap={0} alignItems="flex-start">
            <Hint>Corretora</Hint>
            <Input
              value={nomeCorretora}
              onChange={(ev) => setNomeCorretora(ev.target.value)}
              size="sm"
            />
          </VStack>
          <VStack flex={2} gap={0} alignItems="flex-start">
            <Hint>Nome conta</Hint>
            <Input
              value={nomeConta}
              onChange={(ev) => setNomeConta(ev.target.value)}
              size="sm"
            />
          </VStack>
          <Button flex={1} size="sm" onClick={adicionarCorretora}>
            Adicionar
          </Button>
        </HStack>
      </VStack>
    </ConfirmModal>
  );
}
