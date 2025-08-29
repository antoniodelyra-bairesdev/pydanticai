"use client";

import FileDragAndDrop from "@/app/_components/files/FileDragAndDrop";
import { useHTTP } from "@/lib/hooks";
import { downloadBlob } from "@/lib/util/http";
import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box,
  Button,
  Divider,
  Heading,
  HStack,
  Icon,
  Spinner,
  Text,
  VStack,
} from "@chakra-ui/react";
import isObjEmpty from "@/lib/util/object";
import { useCallback, useState } from "react";
import { IoWarning } from "react-icons/io5";

type Avisos = {
  codigos_fundos_fora_da_data_ou_em_reprocessamento: string[];
  fundos_sem_cadastro_caracteristicas: string[];
};

export default function ExportacaoPassivo() {
  const httpClient = useHTTP({ withCredentials: true });
  const [arquivosPassivo, setArquivosPassivo] = useState<FileList | null>(null);
  const [arquivosCaracteristicas, setArquivosCaracteristicas] =
    useState<FileList | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [avisos, setAvisos] = useState<Avisos | null>(null);

  const onPassivoChangeCallback = useCallback(
    (files: FileList | null) => {
      if (isLoading || !files) {
        return;
      }

      setArquivosPassivo(files);
    },
    [arquivosPassivo, isLoading],
  );

  const onCaracteristicasChangeCallback = useCallback(
    (files: FileList | null) => {
      if (isLoading || !files) {
        return;
      }

      setArquivosCaracteristicas(files);
    },
    [arquivosPassivo, isLoading],
  );

  const isButtonsDisabled = !arquivosPassivo || isLoading;

  let nomeArquivoPassivo: string | null = null;
  let nomeArquivoCaracteristicas: string | null = null;

  if (arquivosPassivo?.length) {
    nomeArquivoPassivo = arquivosPassivo[0].name;
  }
  if (arquivosCaracteristicas?.length) {
    nomeArquivoCaracteristicas = arquivosCaracteristicas[0].name;
  }

  const exportaPassivo = async (
    arquivo_passivo: File,
    arquivo_caracteristicas: File,
  ) => {
    if (isLoading) {
      return;
    }

    setIsLoading(true);

    const body = new FormData();
    body.append("arquivo_passivo", arquivo_passivo);
    body.append("arquivo_caracteristicas", arquivo_caracteristicas);

    const response = await httpClient.fetch("v1/enquadramento/omnis/passivo", {
      method: "POST",
      body,
      multipart: true,
    });

    if (!response.ok) {
      setIsLoading(false);
      return;
    }

    const responseFormData = await response.formData();
    const responseAvisosJSON = JSON.parse(
      responseFormData.get("avisos") as string,
    ) as Avisos;

    if (isObjEmpty(responseAvisosJSON)) {
      setAvisos(null);
    } else {
      setAvisos(responseAvisosJSON);
    }

    const blob = responseFormData.get("arquivo") as Blob;
    downloadBlob(blob, "passivo_omnis.xlsx");

    setIsLoading(false);
  };

  return (
    <Box p="24px" h="100%">
      <VStack alignItems="flex-start" w="100%" gap={4}>
        <Heading size="lg" fontWeight={500}>
          Exportação de movimentações de passivo para o OMNiS
        </Heading>
        <Divider />
        <VStack w="100%" alignItems="stretch">
          <VStack alignItems="stretch" gap={0}>
            <Heading size="md" fontWeight={600}>
              Movimentações
            </Heading>
            <Text>
              H:\Controle\MiddleOffice\01 - Conta e Ordem\1.17 - Relatorios
              Bradesco\Movimento do dia
            </Text>
            <FileDragAndDrop
              state={arquivosPassivo}
              shownText={nomeArquivoPassivo}
              onChangeCallback={onPassivoChangeCallback}
            />
          </VStack>
          <VStack alignItems="stretch" gap={0}>
            <Heading size="md" fontWeight={600}>
              Características dos fundos
            </Heading>
            <Text>
              H:\Controle\BackOffice\Caracteristicas Fundos Icatu Vanguarda.xls
            </Text>
            <FileDragAndDrop
              state={arquivosCaracteristicas}
              shownText={nomeArquivoCaracteristicas}
              onChangeCallback={onCaracteristicasChangeCallback}
            />
          </VStack>
          <Divider m="16px 0" />
          <HStack alignSelf="flex-end" justifyContent="flex-end" gap={2}>
            <Button
              size="sm"
              width="90px"
              variant="outline"
              colorScheme="azul_1"
              onClick={() => {
                setArquivosPassivo(null);
                setArquivosCaracteristicas(null);
                setAvisos(null);
              }}
            >
              Limpar
            </Button>
            <Button
              isDisabled={isButtonsDisabled}
              size="sm"
              colorScheme="verde"
              onClick={async () => {
                if (
                  !arquivosPassivo?.length ||
                  !arquivosCaracteristicas?.length
                ) {
                  return;
                }

                await exportaPassivo(
                  arquivosPassivo[0],
                  arquivosCaracteristicas[0],
                );
              }}
            >
              Exportar
            </Button>
          </HStack>
        </VStack>
        {isLoading && (
          <HStack w="100%" justifyContent="center" alignItems="center">
            <Spinner size="xl" />
          </HStack>
        )}
        {avisos && Object.keys(avisos) && !isLoading && (
          <VStack w="100%" alignItems="flex-start">
            <Heading size="md" fontWeight={500} textAlign="center">
              Avisos{" "}
              <Text as="span">
                <Icon color="amarelo.main" boxSize={6} as={IoWarning} />
              </Text>
            </Heading>
            <Accordion allowToggle w="100%">
              <AccordionItem>
                <h2>
                  <AccordionButton>
                    <HStack
                      flex="1"
                      textAlign="left"
                      justifyContent="space-between"
                    >
                      <Text as="span">
                        Códigos dos fundos fora da data ou em reprocessamento
                      </Text>
                      <AccordionIcon />
                    </HStack>
                  </AccordionButton>
                </h2>
                <AccordionPanel pb={4}>
                  <VStack alignItems="flex-start">
                    {avisos.codigos_fundos_fora_da_data_ou_em_reprocessamento.map(
                      (aviso, index) => {
                        return (
                          <Box key={index}>
                            <Text as="span">{aviso}</Text>
                          </Box>
                        );
                      },
                    )}
                  </VStack>
                </AccordionPanel>
              </AccordionItem>
              <AccordionItem>
                <h2>
                  <AccordionButton>
                    <HStack
                      flex="1"
                      textAlign="left"
                      justifyContent="space-between"
                    >
                      <Text as="span">
                        Códigos das classes/subclasses com cadastro errado ou
                        sem cadastro no "Características Fundos"
                      </Text>
                      <AccordionIcon />
                    </HStack>
                  </AccordionButton>
                </h2>
                <AccordionPanel pb={4}>
                  <VStack alignItems="flex-start">
                    {avisos.fundos_sem_cadastro_caracteristicas.map(
                      (aviso, index) => {
                        return (
                          <Box key={index}>
                            <Text as="span">{aviso}</Text>
                          </Box>
                        );
                      },
                    )}
                  </VStack>
                </AccordionPanel>
              </AccordionItem>
            </Accordion>
          </VStack>
        )}
      </VStack>
    </Box>
  );
}
