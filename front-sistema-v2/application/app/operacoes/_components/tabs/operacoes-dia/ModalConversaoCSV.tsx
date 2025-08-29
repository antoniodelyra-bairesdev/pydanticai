import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import Hint from "@/app/_components/texto/Hint";
import { useAsync, useHTTP, useWebSockets } from "@/lib/hooks";
import { CorretoraResumo, EventoOperacao } from "@/lib/types/api/iv/v1";
import {
  WSJSONMessage,
  WSMessage,
  WSMessageType,
} from "@/lib/types/api/iv/websockets";
import {
  Box,
  Button,
  HStack,
  Icon,
  Input,
  Progress,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Tr,
  VStack,
} from "@chakra-ui/react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { IoCloudDownloadOutline } from "react-icons/io5";

export type ModalConversaoCSVProps = {
  isOpen: boolean;
  onClose: () => void;
};

export default function ModalConversaoCSV({
  isOpen,
  onClose,
}: ModalConversaoCSVProps) {
  const arquivoBoletasRef = useRef<HTMLInputElement>(null);
  const arquivoVoicesRef = useRef<HTMLInputElement>(null);

  const [arquivoBoleta, setArquivoBoleta] = useState<File | null>(null);
  const [arquivoVoices, setArquivoVoices] = useState<File | null>(null);
  const [processedBlobURL, setProcessedBlobURL] = useState("");
  const [loadingSheet, loadSheet] = useAsync();
  const httpClient = useHTTP({ withCredentials: true });

  useEffect(() => {
    if (arquivoBoleta === null || arquivoVoices === null) return;
    loadSheet(async () => {
      if (arquivoBoleta === null || arquivoVoices === null) return;
      const body = new FormData();
      body.append("arquivoBoleta", arquivoBoleta);
      body.append("arquivoVoices", arquivoVoices);
      const response = await httpClient.fetch("v1/operacoes/conversao-boleta", {
        hideToast: { success: true },
        method: "POST",
        body,
        multipart: true,
      });
      if (!response.ok) return;
      const url = URL.createObjectURL(await response.blob());
      setProcessedBlobURL(url);
    });
  }, [arquivoBoleta, arquivoVoices]);

  const limpar = () => {
    [arquivoBoletasRef, arquivoVoicesRef].forEach((ref) => {
      if (ref.current) {
        (ref.current as any).value = null;
      }
    });
    setArquivoBoleta(null);
    setArquivoVoices(null);
    URL.revokeObjectURL(processedBlobURL);
    setProcessedBlobURL("");
  };

  return (
    <ConfirmModal
      title="Conversão de boleta para formato B3 (.csv)"
      isOpen={isOpen}
      overflow="auto"
      onClose={() => {
        limpar();
        onClose();
      }}
      hideConfirmButton={true}
      cancelContent="Fechar"
      size="4xl"
    >
      <VStack gap={0} w="100%" maxH="60vh" overflow="auto" alignItems="stretch">
        <HStack alignItems="flex-end">
          <VStack alignItems="flex-start" flex={1} gap={0}>
            <Hint>Arquivo boletas</Hint>
            <Input
              size="sm"
              p="4px"
              ref={arquivoBoletasRef}
              type="file"
              accept=".xlsx"
              onChange={(ev) =>
                setArquivoBoleta(ev.target.files?.item(0) ?? null)
              }
            />
          </VStack>
          <VStack alignItems="flex-start" flex={1} gap={0}>
            <Hint>Arquivo voices</Hint>
            <Input
              size="sm"
              p="4px"
              ref={arquivoVoicesRef}
              type="file"
              accept=".xlsx"
              onChange={(ev) =>
                setArquivoVoices(ev.target.files?.item(0) ?? null)
              }
            />
          </VStack>
          <Button onClick={limpar} size="sm" colorScheme="rosa">
            Limpar
          </Button>
        </HStack>
        <Progress
          visibility={loadingSheet ? "visible" : "hidden"}
          isIndeterminate
          colorScheme="verde"
        />
        {processedBlobURL && (
          <Link href={processedBlobURL} target={"_blank"}>
            <Button
              size="sm"
              colorScheme="azul_3"
              leftIcon={<Icon as={IoCloudDownloadOutline} />}
            >
              Baixar
            </Button>
          </Link>
        )}
      </VStack>
    </ConfirmModal>
  );
}
