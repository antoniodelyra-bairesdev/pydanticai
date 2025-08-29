import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import Hint from "@/app/_components/texto/Hint";
import { useAsync, useHTTP } from "@/lib/hooks";
import { downloadBlob } from "@/lib/util/http";
import { wait } from "@/lib/util/misc";
import {
  Box,
  Button,
  Divider,
  HStack,
  Icon,
  Input,
  StackDivider,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useEffect, useRef, useState } from "react";
import {
  IoAddCircleOutline,
  IoCheckmarkCircle,
  IoClose,
  IoCloseCircle,
  IoCloudUploadOutline,
  IoDownloadOutline,
  IoEllipse,
  IoEllipseOutline,
} from "react-icons/io5";

export type ModalArquivoHubBalcaoProps = {
  isOpen: boolean;
  onClose: () => void;
};

const round = {
  border: "1px solid",
  borderColor: "cinza.main",
  borderRadius: "4px",
  p: "8px",
};

export default function ModalArquivoHubBalcao({
  isOpen,
  onClose,
}: ModalArquivoHubBalcaoProps) {
  const [download, setDownload] = useState(null);
  const [resultado, setResultado] = useState(null);
  const [erro, setErro] = useState(null);

  const [boleta, setBoleta] = useState<File | null>(null);
  const boletaInputRef = useRef<HTMLInputElement>(null);

  const [voicesHubBalcao, setVoicesHubBalcao] = useState<File | null>(null);
  const voicesHubBalcaoInputRef = useRef<HTMLInputElement>(null);

  const httpClient = useHTTP({ withCredentials: true });

  const [carregando, carregar] = useAsync();
  const enviar = () => {
    if (carregando) return;
    carregar(async () => {
      setResultado(null);
      setErro(null);
      setDownload(null);
      const body = new FormData();
      if (!boleta || !voicesHubBalcao) return;
      body.append("boleta", boleta);
      body.append("voices", voicesHubBalcao);
      const response = await httpClient.fetch(
        "v1/b3/contingencia/importacao-hub-balcao",
        {
          method: "POST",
          multipart: true,
          body,
        },
      );
      if (!response.ok) {
        const json = await response.json();
        return setErro(
          json?.detail?.message ??
            "Erro do servidor. Entre em contato com o time de tecnologia.",
        );
      }
      const dados = await response.formData();
      const detalhes = dados.get("avisos");
      setResultado({ detalhes } as any);

      const arquivo = dados.get("arquivo") as File;
      setDownload(arquivo as any);
    });
  };

  const baixar = () => {
    downloadBlob(download as any as File, (download as any as File).name);
  };

  useEffect(() => {
    if (boleta === null || voicesHubBalcao === null) {
      setResultado(null);
      setErro(null);
      setDownload(null);
    }
  }, [boleta, voicesHubBalcao]);

  return (
    <ConfirmModal
      isOpen={isOpen}
      onClose={onClose}
      size="4xl"
      hideConfirmButton
    >
      <VStack
        w="100%"
        h="100%"
        alignItems="stretch"
        gap="32px"
        p="16px 16px 0 16px"
      >
        <HStack alignItems="stretch" gap={0}>
          <VStack flex={1} alignItems="stretch">
            <VStack
              flex={1}
              alignItems="stretch"
              {...round}
              borderColor={boleta ? "verde.main" : "cinza.main"}
              bgColor={boleta ? "verde.50" : undefined}
            >
              <Hint color={boleta ? "verde.main" : "cinza.500"}>
                Arquivo da boleta
              </Hint>
              <HStack gap={0}>
                <Input
                  ref={boletaInputRef}
                  p="1px"
                  flex={5}
                  size="xs"
                  type="file"
                  onChange={(ev) => setBoleta(ev.target.files?.item(0) ?? null)}
                  accept=".xlsx"
                />
                <Button
                  isDisabled={!boleta}
                  flex={1}
                  size="xs"
                  colorScheme="rosa"
                  leftIcon={<Icon as={IoClose} />}
                  onClick={() => {
                    (boletaInputRef.current as any).value = null;
                    setBoleta(null);
                  }}
                >
                  Limpar
                </Button>
              </HStack>
            </VStack>
            <VStack
              flex={1}
              alignItems="stretch"
              {...round}
              borderColor={voicesHubBalcao ? "verde.main" : "cinza.main"}
              bgColor={voicesHubBalcao ? "verde.50" : undefined}
            >
              <Hint color={voicesHubBalcao ? "verde.main" : "cinza.500"}>
                Voices Hub Balcão
              </Hint>
              <HStack gap={0}>
                <Input
                  ref={voicesHubBalcaoInputRef}
                  p="1px"
                  flex={5}
                  size="xs"
                  type="file"
                  onChange={(ev) =>
                    setVoicesHubBalcao(ev.target.files?.item(0) ?? null)
                  }
                  accept=".xlsx"
                />
                <Button
                  isDisabled={!voicesHubBalcao}
                  flex={1}
                  size="xs"
                  colorScheme="rosa"
                  leftIcon={<Icon as={IoClose} />}
                  onClick={() => {
                    (voicesHubBalcaoInputRef.current as any).value = null;
                    setVoicesHubBalcao(null);
                  }}
                >
                  Limpar
                </Button>
              </HStack>
            </VStack>
          </VStack>
          <HStack gap={0} flex={1} alignItems="stretch">
            <HStack flex={1} alignItems="center" gap={0}>
              <HStack flex={1} h="50%" alignItems="center" gap={0}>
                <Box
                  h="100%"
                  flex={1}
                  border="1px solid"
                  borderLeft="none"
                  borderColor="cinza.main"
                  borderTopColor={boleta ? "verde.main" : "cinza.main"}
                  borderBottomColor={
                    voicesHubBalcao ? "verde.main" : "cinza.main"
                  }
                  borderRightColor={
                    boleta && voicesHubBalcao ? "verde.main" : "cinza.main"
                  }
                  position="relative"
                >
                  <Icon
                    as={boleta ? IoCheckmarkCircle : IoAddCircleOutline}
                    color={boleta ? "verde.main" : "cinza.main"}
                    bgColor="white"
                    w="16px"
                    h="16px"
                    position="absolute"
                    top="-8px"
                    right="-8px"
                  />
                  <Icon
                    as={
                      voicesHubBalcao ? IoCheckmarkCircle : IoAddCircleOutline
                    }
                    color={voicesHubBalcao ? "verde.main" : "cinza.main"}
                    bgColor="white"
                    w="16px"
                    h="16px"
                    position="absolute"
                    bottom="-8px"
                    right="-8px"
                  />
                </Box>
                <Box
                  h="1px"
                  bgColor={
                    boleta && voicesHubBalcao ? "verde.main" : "cinza.main"
                  }
                  flex={1}
                />
              </HStack>
            </HStack>
            <HStack>
              <Button
                isLoading={carregando}
                isDisabled={!boleta || !voicesHubBalcao}
                size="xs"
                colorScheme="azul_1"
                leftIcon={<Icon as={IoCloudUploadOutline} />}
                onClick={enviar}
              >
                Processar arquivos
              </Button>
            </HStack>
            <VStack flex={1} gap={0}>
              <Box flex={1} />
              <HStack
                justifyContent="center"
                w="100%"
                h="1px"
                zIndex={1}
                gap={0}
              >
                <Box
                  flex={1}
                  h="1px"
                  bgColor={
                    resultado ? "verde.main" : erro ? "rosa.main" : "cinza.main"
                  }
                />
                <Icon
                  as={
                    resultado
                      ? IoCheckmarkCircle
                      : erro
                        ? IoCloseCircle
                        : IoAddCircleOutline
                  }
                  color={
                    resultado ? "verde.main" : erro ? "rosa.main" : "cinza.main"
                  }
                  bgColor="white"
                  w="16px"
                  h="16px"
                />
                <Box
                  flex={1}
                  h="1px"
                  bgColor={resultado ? "verde.main" : "cinza.main"}
                />
              </HStack>
              <Box
                flex={1}
                w="1px"
                bgColor={
                  resultado ? "verde.main" : erro ? "rosa.main" : "cinza.main"
                }
                position="relative"
              >
                <Box
                  position="absolute"
                  bottom="-32px"
                  bgColor={
                    resultado ? "verde.main" : erro ? "rosa.main" : "cinza.main"
                  }
                  w="1px"
                  h="32px"
                />
              </Box>
            </VStack>
            <HStack>
              <Button
                isDisabled={!download}
                size="xs"
                colorScheme="verde"
                leftIcon={<Icon as={IoDownloadOutline} />}
                onClick={baixar}
              >
                Baixar resultado
              </Button>
            </HStack>
          </HStack>
        </HStack>
        <VStack
          alignItems="stretch"
          fontSize="xs"
          {...round}
          borderColor={
            resultado ? "verde.main" : erro ? "rosa.main" : "cinza.main"
          }
          bgColor={resultado ? "verde.50" : erro ? "rosa.50" : "cinza.50"}
        >
          <Text>
            Resultado do processamento:{" "}
            <Text
              as="span"
              color={
                resultado ? "verde.main" : erro ? "rosa.main" : "cinza.500"
              }
            >
              {resultado
                ? "Sucesso"
                : erro
                  ? "Erro"
                  : "Aguardando processamento"}
            </Text>
          </Text>
          <Text>
            Mais informações:{" "}
            <Text
              as="span"
              color={
                resultado ? "verde.main" : erro ? "rosa.main" : "cinza.500"
              }
            >
              {(resultado as any)?.detalhes ?? erro}
            </Text>
          </Text>
        </VStack>
      </VStack>
    </ConfirmModal>
  );
}
