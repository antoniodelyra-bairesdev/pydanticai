import { HStack, Icon, Text, Tooltip } from "@chakra-ui/react";
import { IoSwapHorizontalOutline, IoWarningOutline } from "react-icons/io5";

export type PartesNegocioProps = {
  vanguarda_compra: boolean;
  contraparte_nome: string | null;
  nao_registrada?: boolean;
};

export default function PartesNegocio({
  vanguarda_compra,
  contraparte_nome,
  nao_registrada = false,
}: PartesNegocioProps) {
  return (
    <HStack>
      <Text fontSize="14px">
        <Text as="span">Icatu Vanguarda </Text>
        <Text
          as="span"
          fontWeight={900}
          color={vanguarda_compra ? "azul_3.main" : "rosa.main"}
          fontSize="10px"
          border="2px solid"
          borderRadius="4px"
          borderColor={vanguarda_compra ? "azul_3.main" : "rosa.main"}
          p="1px 2px 0px 2px"
          lineHeight={1}
        >
          {vanguarda_compra ? "COMPRA" : "VENDE"}
        </Text>
      </Text>
      <Icon as={IoSwapHorizontalOutline} color="verde.main" />
      {nao_registrada ? (
        <HStack
          fontSize="14px"
          p="0px 4px"
          borderRadius="4px"
          bgColor="rosa.50"
          color="rosa.main"
        >
          <Icon boxSize="14px" as={IoWarningOutline} />
          <Text whiteSpace="nowrap" fontWeight="bold">
            {contraparte_nome}
          </Text>
        </HStack>
      ) : (
        <Text fontSize="14px">
          <Text as="span">{contraparte_nome} </Text>
        </Text>
      )}
    </HStack>
  );
}
