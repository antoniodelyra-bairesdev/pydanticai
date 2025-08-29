"use client";

import { useAsync, useHTTP } from "@/lib/hooks";
import { Arquivo as ArquivoType } from "@/lib/types/api/iv/v1";
import { downloadBlob } from "@/lib/util/http";
import {
  Box,
  Button,
  Card,
  CardBody,
  HStack,
  Icon,
  Progress,
  Text,
  VStack,
} from "@chakra-ui/react";
import styled from "@emotion/styled";
import { IoDocumentOutline, IoDownloadOutline, IoTrash } from "react-icons/io5";

const ThinIcon = styled(Icon)`
  path {
    stroke-width: 12;
  }
`;

export type ArquivoProps = {
  arquivo: ArquivoType;
  permitirDownload?: boolean | (() => Promise<void>);
  rotulo?: string;
  onDelete?: (arquivo: ArquivoType) => void;
};

export default function Arquivo({
  arquivo,
  rotulo,
  onDelete,
  permitirDownload,
}: ArquivoProps) {
  const httpClient = useHTTP({ withCredentials: true });

  const [baixando, iniciarDownload] = useAsync();

  const baixar = () =>
    iniciarDownload(
      typeof permitirDownload === "function"
        ? permitirDownload
        : async () => {
            const response = await httpClient.fetch(
              "/sistema/arquivos/" + arquivo.id,
              { method: "GET", hideToast: { success: true } },
            );
            if (!response.ok) return;
            const blob = await response.blob();
            downloadBlob(blob, arquivo.nome);
          },
    );

  const deletarArquivo = () => {
    onDelete?.(arquivo);
  };

  const fragmentos = arquivo.nome.split(".");
  const extensao = fragmentos.length > 1 ? (fragmentos.at(-1) ?? "") : "";

  const cor =
    {
      pdf: "rosa.main",

      xls: "verde.main",
      xlsx: "verde.main",
      xlsm: "verde.main",
      csv: "verde.main",

      jpeg: "azul_3.main",
      jpg: "azul_3.main",
      png: "azul_3.main",

      ppt: "amarelo.main",
      pptx: "amarelo.main",
    }[extensao] ?? "azul_1.main";

  return (
    <Card
      transform="translate(0, 0)"
      _hover={{
        boxShadow: "0 5px 3px 0 rgba(0, 0, 0, 0.1)",
        transform: "translate(0px, -4px)",
      }}
      transition="0.125s all"
      role="group"
    >
      <CardBody
        p="8px 4px"
        color={baixando ? "cinza.400" : undefined}
        position="relative"
      >
        {onDelete && (
          <VStack
            opacity={0}
            cursor="pointer"
            transition="0.25s all"
            onClick={deletarArquivo}
            position="absolute"
            justifyContent="center"
            w="24px"
            h="24px"
            bgColor="rosa.main"
            borderRadius="full"
            right="-4px"
            top="-4px"
            _groupHover={{ opacity: 1 }}
            _hover={{ bgColor: "rosa.700" }}
          >
            <Icon as={IoTrash} color="white" boxSize="16px" />
          </VStack>
        )}
        <VStack pt="4px">
          <HStack justifyContent="center" position="relative" w="36px" h="36px">
            <Box position="absolute">
              <VStack
                color={cor}
                w="48px"
                h="48px"
                position="relative"
                opacity={1}
                _groupHover={permitirDownload ? { opacity: 0 } : undefined}
                transition="0.125s all"
                justifyContent="center"
              >
                <ThinIcon
                  as={IoDocumentOutline}
                  position="absolute"
                  boxSize="48px"
                />
                <Text
                  pt="8px"
                  fontSize="10px"
                  fontWeight="bold"
                  position="absolute"
                >
                  {extensao ? "." : ""}
                  {extensao.toUpperCase()}
                </Text>
              </VStack>
            </Box>
            {permitirDownload && (
              <Button
                colorScheme="azul_3"
                position="absolute"
                opacity={0}
                _groupHover={{ opacity: 1 }}
                transition="0.25s all"
                p={0}
                isDisabled={baixando}
                onClick={baixar}
                cursor={baixando ? "wait" : "pointer"}
              >
                <Icon as={IoDownloadOutline} boxSize="18px" />
              </Button>
            )}
          </HStack>
          <Text
            w="144px"
            lineHeight={1.25}
            textAlign="center"
            fontSize="xs"
            maxW="196px"
          >
            {rotulo ?? arquivo.nome}
          </Text>
        </VStack>
      </CardBody>
      {baixando ? (
        <Progress isIndeterminate colorScheme="verde" h="4px" />
      ) : (
        <Box w="1px" h="4px" />
      )}
    </Card>
  );
}
