"use client";

import { getColorHex } from "@/app/theme";
import { PastaCarteiras } from "@/lib/types/api/iv/carteiras";
import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  AccordionProps,
  Box,
  HStack,
  Icon,
  StackProps,
  Text,
  Tooltip,
  VStack,
} from "@chakra-ui/react";
import {
  IoCheckmarkCircleOutline,
  IoCloseOutline,
  IoDocumentOutline,
  IoFolder,
  IoFolderOutline,
  IoInformationCircleOutline,
  IoInformationOutline,
  IoWarningOutline,
} from "react-icons/io5";

export type VisualizacaoPastasProps = {
  pastas: PastaCarteiras[];
} & StackProps;

const stsMap: Record<string, number> = {
  OK: 0,
  ERRO: 1,
};
const comparaStatus = (sts1: string, sts2: string) =>
  (stsMap[sts1] ?? 2) - (stsMap[sts2] ?? 2);

export default function VisualizacaoPastas({
  pastas,
  ...stackProps
}: VisualizacaoPastasProps) {
  const ps = [...pastas]
    .sort((p1, p2) => p1.nome.localeCompare(p2.nome))
    .sort((p1, p2) => comparaStatus(p1.status, p2.status));
  return (
    <VStack alignItems="stretch" {...stackProps} gap={0}>
      {ps.map((p) => (
        <ArquivosEPastas key={p.nome} pasta={p} />
      ))}
    </VStack>
  );
}

export function ArquivosEPastas({
  pasta,
  nomePastaAnterior = "",
  ...accordionProps
}: { pasta: PastaCarteiras; nomePastaAnterior?: string } & AccordionProps) {
  const erro = pasta.status === "ERRO";
  const cs = [...pasta.carteiras]
    .sort((p1, p2) => p1.nome.localeCompare(p2.nome))
    .sort((p1, p2) => comparaStatus(p1.status, p2.status));
  return (
    <Accordion allowToggle {...accordionProps}>
      <AccordionItem
        isDisabled={erro}
        color={erro ? "rosa.main" : undefined}
        fontSize="xs"
        border="none"
      >
        <AccordionButton
          fontSize="xs"
          p="4px"
          bgColor={erro ? "rosa.50" : "none"}
        >
          <Tooltip
            label={erro ? pasta.detalhes : ""}
            hasArrow
            bgColor="rosa.50"
            color="rosa.main"
            placement="top"
          >
            <HStack w="100%">
              <Icon as={IoFolder} color="amarelo.main" />
              {erro ? (
                <Icon as={IoCloseOutline} w="15px" h="15px" />
              ) : (
                <AccordionIcon />
              )}
              <Text fontWeight={600}>{pasta.nome}</Text>
            </HStack>
          </Tooltip>
        </AccordionButton>
        <AccordionPanel p={0}>
          <VStack w="100%" h="100%" alignItems="stretch" gap={0} pl="12px">
            {cs.map((c) => {
              const erro = c.status === "ERRO";
              return (
                <HStack
                  alignItems="flex-start"
                  bgColor="cinza.100"
                  borderBottom="1px solid"
                  borderColor="cinza.main"
                >
                  <HStack
                    flex={1}
                    alignItems="stretch"
                    gap={0}
                    overflow="hidden"
                  >
                    <HStack m="4px">
                      <Icon as={IoDocumentOutline} />
                    </HStack>
                    <HStack
                      bgColor={erro ? "rosa.50" : "verde.50"}
                      color={erro ? "rosa.main" : "verde.main"}
                    >
                      <Text w="64px" textAlign="center" fontWeight={600}>
                        {c.status}
                      </Text>
                    </HStack>
                    <HStack
                      pl="8px"
                      flex={1}
                      color={erro ? "rosa.main" : undefined}
                      bgColor={
                        (erro
                          ? getColorHex("rosa.50")
                          : getColorHex("verde.50")) + "7F"
                      }
                      overflow="hidden"
                    >
                      <Text
                        maxW="100%"
                        whiteSpace="nowrap"
                        textOverflow="ellipsis"
                        overflow="hidden"
                      >
                        {c.nome}
                      </Text>
                    </HStack>
                    <HStack
                      p="0 8px"
                      fontWeight={300}
                      justifyContent="flex-end"
                      color={erro ? "rosa.main" : undefined}
                      overflow="none"
                      whiteSpace="nowrap"
                      textOverflow="ellipsis"
                      bgColor={
                        (erro
                          ? getColorHex("rosa.50")
                          : getColorHex("verde.50")) + "7F"
                      }
                    >
                      {c.tipo === "XML_ANBIMA_5.0" ? (
                        <Tooltip
                          fontSize="xs"
                          placement="top"
                          hasArrow
                          label="Possível perda de dados durante a conversão. Um XML 5.0 pode gerar mais de um XML 4.01 como resultado."
                        >
                          <Box>
                            <Icon
                              as={IoInformationCircleOutline}
                              color="roxo.main"
                            />
                          </Box>
                        </Tooltip>
                      ) : (
                        c.tipo === "XML_ANBIMA_4.01" && (
                          <Icon
                            as={IoCheckmarkCircleOutline}
                            color="verde.main"
                          />
                        )
                      )}{" "}
                      <Text>{c.tipo ?? c.detalhes}</Text>
                    </HStack>
                  </HStack>
                </HStack>
              );
            })}
            {pasta.subpastas.map((p) => (
              <HStack alignItems="flex-start">
                <ArquivosEPastas
                  pasta={p}
                  nomePastaAnterior={pasta.nome}
                  flex={1}
                  bgColor="white"
                />
              </HStack>
            ))}
          </VStack>
        </AccordionPanel>
      </AccordionItem>
    </Accordion>
  );
}
