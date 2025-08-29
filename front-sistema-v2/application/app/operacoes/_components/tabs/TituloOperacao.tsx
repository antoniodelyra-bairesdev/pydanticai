import { Ativo, AtivoResumo } from "@/lib/types/api/iv/v1";
import { fmtNumber } from "@/lib/util/string";
import { Icon, Text, VStack } from "@chakra-ui/react";
import { IoCubeOutline, IoWarningOutline } from "react-icons/io5";

export type TituloAtivoProps = {
  ativo?: AtivoResumo | null;
  preco_unitario: number;
  quantidade: number;
  taxa: number;
  fallback_codigo_ativo: string;
  fallback_indice_nome: string;
};

export default function TituloOperacao({
  ativo,
  preco_unitario,
  quantidade,
  fallback_codigo_ativo,
  fallback_indice_nome,
  taxa,
}: TituloAtivoProps) {
  const codigo = ativo?.codigo ?? fallback_codigo_ativo;
  const indice = ativo?.indice ?? fallback_indice_nome;
  return (
    <VStack
      w="128px"
      justifyContent="center"
      alignItems="flex-start"
      p="0px 12px"
      gap={0}
    >
      <Text
        borderRadius="4px"
        p="0px 2px"
        fontSize="16px"
        fontWeight={900}
        color={!ativo ? "laranja.main" : undefined}
        bgColor={!ativo ? "laranja.100" : undefined}
      >
        {!ativo && <Icon mr="2px" as={IoWarningOutline} color="laranja.main" />}
        {codigo}
      </Text>
      <Text fontSize="13px" color="azul_2.main" fontWeight="bold">
        <Text as="span" color={!ativo ? "laranja.main" : undefined}>
          {indice}
        </Text>{" "}
        {fmtNumber(taxa, 4)}%
      </Text>
      <Text fontSize="11px" color="verde.main" fontWeight="bold">
        R$ {fmtNumber(preco_unitario, 6)}
      </Text>
      <Text fontSize="11px">
        <Icon as={IoCubeOutline} mr="4px" color="cinza.500" />
        {fmtNumber(quantidade, 0)}
      </Text>
    </VStack>
  );
}
