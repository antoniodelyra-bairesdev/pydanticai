import {
  Box,
  Button,
  Divider,
  HStack,
  Icon,
  Text,
  useDisclosure,
  VStack,
} from "@chakra-ui/react";
import {
  IoCloudUploadOutline,
  IoDocumentTextOutline,
  IoDownloadOutline,
  IoWarning,
} from "react-icons/io5";
import ModalNovaBoleta from "./ModalNovaBoleta";
import { useContext, useEffect, useState } from "react";
import BoletaComponent from "../../boletas/BoletaComponent";
import {
  AlocacoesContext,
  BoletaClient,
} from "@/lib/providers/AlocacoesProvider";
import Hint from "@/app/_components/texto/Hint";
import ModalArquivoHubBalcao from "./ModalArquivoHubBalcao";

export default function AbaSimulacao({
  onContagemChange,
}: {
  onContagemChange: (contagem: number) => void;
}) {
  const { isOpen, onClose, onOpen } = useDisclosure();

  const {
    isOpen: isOpenHB,
    onClose: onCloseHB,
    onOpen: onOpenHB,
  } = useDisclosure();

  const { boletas: boletasEnviadas } = useContext(AlocacoesContext);

  const [boletas, setBoletas] = useState<BoletaClient[]>([]);

  useEffect(() => {
    const removerDoRascunho = boletasEnviadas.filter((enviada) =>
      boletas.map((b) => b.client_id).includes(enviada.client_id),
    );
    if (removerDoRascunho.length > 0) {
      for (const remover of removerDoRascunho) {
        const index = boletas.findIndex(
          (b) => b.client_id === remover.client_id,
        );
        boletas.splice(index, 1);
      }
      setBoletas([...boletas]);
    }
  }, [boletas, boletasEnviadas]);

  useEffect(() => {
    onContagemChange(boletas.length);
  }, [boletas]);

  return (
    <HStack
      h="100%"
      alignItems="stretch"
      p="8px"
      bgColor="cinza.main"
      overflowX="auto"
    >
      <VStack
        alignItems="stretch"
        p="8px"
        borderRadius="8px"
        minW="256px"
        bgColor="white"
      >
        <Button
          size="xs"
          colorScheme="azul_4"
          leftIcon={<Icon as={IoDocumentTextOutline} />}
          onClick={onOpen}
        >
          Importar boleta
        </Button>
        <Divider />
        <Hint>Contingência</Hint>
        <Button
          size="xs"
          colorScheme="azul_1"
          leftIcon={<Icon as={IoCloudUploadOutline} />}
          onClick={onOpenHB}
        >
          Arquivo de alocação Hub Balcão
        </Button>
      </VStack>
      <VStack minW="512px" flex={1} alignItems="stretch" overflowY="auto">
        <HStack
          bgColor="amarelo.100"
          alignItems="stretch"
          borderRadius="6px"
          overflow="hidden"
          minH="90px"
        >
          <Box w="6px" bgColor="amarelo.main" />
          <HStack p="16px">
            <Icon as={IoWarning} w="28px" h="28px" color="amarelo.900" />
          </HStack>
          <HStack p="24px 24px 24px 0px" color="amarelo.900">
            <Text fontSize="sm">
              <strong>Aviso</strong>: as boletas na aba de simulação{" "}
              <strong>não</strong> são persistentes: após mudar ou recarregar a
              página, as informações serão perdidas.
              <br />
              Para armazenar as alocações, envie a versão final para triagem.
            </Text>
          </HStack>
        </HStack>
        <VStack p="8px" borderRadius="8px" bgColor="white" alignItems="stretch">
          {boletas.length === 0 ? (
            <Text textAlign="center" color="cinza.400" fontSize="sm">
              Não há alocações na área de rascunho.
            </Text>
          ) : (
            boletas.map((b, i) => (
              <BoletaComponent
                key={i}
                passo="SIMULACAO"
                boleta={b}
                onBoletaChange={(b) => {
                  boletas[i] = b;
                  setBoletas([...boletas]);
                }}
              />
            ))
          )}
        </VStack>
      </VStack>
      <ModalNovaBoleta
        isOpen={isOpen}
        onClose={onClose}
        onBoletasChange={(bs) => setBoletas([...bs, ...boletas])}
      />
      <ModalArquivoHubBalcao isOpen={isOpenHB} onClose={onCloseHB} />
    </HStack>
  );
}
