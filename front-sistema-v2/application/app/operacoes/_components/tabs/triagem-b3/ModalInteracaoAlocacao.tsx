import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import TabelaQuebras from "./TabelaQuebras";
import { Alocacao, EventoAprovacaoBackoffice } from "@/lib/types/api/iv/v1";
import {
  Box,
  Button,
  Card,
  CardBody,
  HStack,
  Icon,
  Input,
  Radio,
  RadioGroup,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  VStack,
} from "@chakra-ui/react";
import {
  IoCalendarOutline,
  IoCheckmarkCircleOutline,
  IoCloseCircleOutline,
  IoCloseOutline,
  IoCloudDownloadOutline,
  IoPersonCircle,
  IoPersonCircleOutline,
  IoPersonOutline,
} from "react-icons/io5";
import Hint from "@/app/_components/texto/Hint";
import { User } from "@/lib/types/api/iv/auth";
import { fmtDatetime } from "@/lib/util/string";
import { useState } from "react";
import { useAsync, useHTTP, useWebSockets } from "@/lib/hooks";
import {
  WSJSONMessage,
  WSMessage,
  WSMessageType,
} from "@/lib/types/api/iv/websockets";
import { downloadBlob } from "@/lib/util/http";

export type ModalInteracaoAlocacaoProps = {
  alocacao_referente: {
    id_operacao_interna: number;
    alocacoes: Alocacao[];
    usuario: User | null;
    data: string;
  };

  habilitar_controles: boolean;
  resposta_backoffice?: {
    aprovacao: boolean;
    motivo: string | null;
    usuario: User;
    data: string;
  };
  externo?: boolean;
  isOpen: boolean;
  onClose: () => void;
};

const txt = {
  pl: "4px",
  pr: "4px",
  overflow: "hidden",
  whiteSpace: "nowrap",
  textOverflow: "ellipsis",
} as const;
const td = { ...txt, fontSize: "13px" } as const;
const th = { ...txt, fontSize: "sm" } as const;

export default function ModalInteracaoAlocacao({
  habilitar_controles,
  alocacao_referente,
  resposta_backoffice,
  isOpen,
  onClose,
  externo,
}: ModalInteracaoAlocacaoProps) {
  const [dia, hora] = fmtDatetime(alocacao_referente.data).split(" ");
  const [aprovacao, setAprovacao] = useState("0");
  const [motivo, setMotivo] = useState("");

  const httpClient = useHTTP({ withCredentials: true });

  const enviarAprovacao = (aprovado: boolean, motivo?: string) => {
    if (resposta_backoffice) return;
    const body = JSON.stringify({
      id_operacao_interna: alocacao_referente.id_operacao_interna,
      aprovacao: aprovado,
      motivo: aprovado ? null : (motivo ?? ""),
    });
    httpClient.fetch("v1/operacoes/aprovacao-backoffice", {
      method: "POST",
      body,
      hideToast: { success: true },
    });
  };

  const [baixando, iniciarDownload] = useAsync();

  const baixar = () => {
    iniciarDownload(async () => {
      const response = await httpClient.fetch(
        `v1/operacoes/alocacoes/${alocacao_referente.id_operacao_interna}/download`,
        { method: "GET", hideToast: { success: true } },
      );
      if (!response.ok) return;
      const file = await response.blob();
      downloadBlob(file, "download.xlsx");
    });
  };

  return (
    <ConfirmModal
      isOpen={isOpen}
      onClose={onClose}
      title="Revisar a alocação interna"
      size="6xl"
      overflow="auto"
      hideCancelButton={true}
      confirmContent="Fechar"
    >
      <HStack alignItems="stretch" gap={0}>
        {externo ? (
          <Text color="cinza.500">Alocação externa</Text>
        ) : (
          <VStack alignItems="flex-start">
            <Button
              onClick={baixar}
              size="xs"
              leftIcon={<Icon as={IoCloudDownloadOutline} />}
              colorScheme="verde"
            >
              Baixar alocações
            </Button>
            <TabelaQuebras
              alocacoes={alocacao_referente.alocacoes}
              verificarFundos={false}
            />
          </VStack>
        )}
      </HStack>
      <HStack alignItems="stretch">
        <VStack mt="12px" gap={0} alignItems="flex-start">
          <Hint>Data alocação:</Hint>
          <Card variant="outline" flex={1}>
            <CardBody p="12px">
              <HStack gap="16px">
                <Icon
                  color="azul_2.main"
                  boxSize="24px"
                  as={IoCalendarOutline}
                />
                <VStack alignItems="flex-start" gap={0}>
                  <Text fontSize="sm">{hora}</Text>
                  <Text color="cinza.500" fontSize="xs">
                    {dia}
                  </Text>
                </VStack>
              </HStack>
            </CardBody>
          </Card>
        </VStack>
        {!externo && (
          <>
            <VStack mt="12px" gap={0} alignItems="flex-start">
              <Hint>Alocado por:</Hint>
              <Card variant="outline" flex={1}>
                <CardBody p="12px">
                  <HStack gap="16px">
                    <Icon
                      color="azul_2.main"
                      boxSize="24px"
                      as={IoPersonCircleOutline}
                    />
                    <VStack alignItems="flex-start" gap={0}>
                      <Text fontSize="sm">
                        {alocacao_referente.usuario?.nome ??
                          "Informação externa"}
                      </Text>
                      <Text color="cinza.500" fontSize="xs">
                        {alocacao_referente.usuario?.email ??
                          "Informação externa"}
                      </Text>
                    </VStack>
                  </HStack>
                </CardBody>
              </Card>
            </VStack>
            {habilitar_controles && (
              <VStack flex={1} mt="12px" gap={0} alignItems="stretch">
                <Hint>Resposta Backoffice:</Hint>
                <Card variant="outline" flex={1}>
                  <CardBody p="12px">
                    {resposta_backoffice ? (
                      <HStack
                        alignItems="flex-end"
                        justifyContent="space-between"
                        gap="16px"
                      >
                        <HStack
                          gap="16px"
                          alignSelf="stretch"
                          alignItems="flex-start"
                        >
                          <Icon
                            color="azul_2.main"
                            boxSize="24px"
                            as={IoPersonCircleOutline}
                          />
                          <VStack alignItems="flex-start" gap={0}>
                            <Text fontSize="sm">
                              {resposta_backoffice.usuario.nome}
                            </Text>
                            <Text color="cinza.500" fontSize="xs">
                              {resposta_backoffice.usuario.email}
                            </Text>
                          </VStack>
                        </HStack>
                        <HStack
                          alignSelf="stretch"
                          flex={1}
                          gap="16px"
                          color="white"
                          bgColor={
                            resposta_backoffice.aprovacao
                              ? "verde.main"
                              : "rosa.main"
                          }
                          p="2px 16px 2px 16px"
                          borderRadius="8px"
                        >
                          <Icon
                            boxSize="24px"
                            as={
                              resposta_backoffice.aprovacao
                                ? IoCheckmarkCircleOutline
                                : IoCloseCircleOutline
                            }
                          />
                          <VStack alignItems="flex-start" gap={0}>
                            <Text fontSize="sm" fontWeight="bold">
                              {resposta_backoffice.aprovacao
                                ? "Aprovado"
                                : "Rejeitado"}
                            </Text>
                            {!resposta_backoffice.aprovacao && (
                              <Text fontSize="xs" fontStyle="italic">
                                {resposta_backoffice.motivo ??
                                  "Nenhum motivo informado"}
                              </Text>
                            )}
                          </VStack>
                        </HStack>
                      </HStack>
                    ) : (
                      <HStack
                        alignItems="flex-end"
                        justifyContent="space-between"
                      >
                        <RadioGroup
                          size="sm"
                          onChange={setAprovacao}
                          value={aprovacao}
                        >
                          <VStack gap={0} alignItems="flex-start">
                            <Radio value={"1"} colorScheme="verde">
                              <Text
                                fontSize="sm"
                                color={
                                  aprovacao === "1" ? "verde.700" : undefined
                                }
                              >
                                Aprovar
                              </Text>
                            </Radio>
                            <Radio value={"0"} colorScheme="rosa">
                              <Text
                                fontSize="sm"
                                color={
                                  aprovacao === "0" ? "rosa.700" : undefined
                                }
                              >
                                Reprovar
                              </Text>
                            </Radio>
                          </VStack>
                        </RadioGroup>
                        {aprovacao === "0" && (
                          <VStack gap={0} alignItems="flex-start" flex={1}>
                            <Hint>Motivo reprovação</Hint>
                            <Input
                              size="xs"
                              onChange={(ev) => setMotivo(ev.target.value)}
                              value={motivo}
                            />
                          </VStack>
                        )}
                        <Button
                          size="xs"
                          onClick={() => enviarAprovacao(!!+aprovacao, motivo)}
                          colorScheme={aprovacao === "0" ? "rosa" : "verde"}
                        >
                          Enviar{" "}
                          {aprovacao === "0" ? "reprovação" : "aprovação"}
                        </Button>
                      </HStack>
                    )}
                  </CardBody>
                </Card>
              </VStack>
            )}
          </>
        )}
      </HStack>
    </ConfirmModal>
  );
}
