import {
  ComponentWithAs,
  Divider,
  StackProps,
  Text,
  VStack,
} from "@chakra-ui/react";
import React from "react";

export type ColunaFluxoOperacoesProps = {
  title: string;
  children?: React.ReactNode;
} & StackProps;

export default function ColunaFluxoOperacoes({
  title,
  children,
  ...props
}: ColunaFluxoOperacoesProps) {
  return (
    <VStack alignItems="stretch" overflow="auto" gap={0} {...props}>
      <VStack borderBottom="1px solid" bgColor="azul_1.main" color="white">
        <Text
          m="4px"
          textAlign="center"
          w="100%"
          overflow="hidden"
          whiteSpace="nowrap"
          textOverflow="ellipsis"
          fontSize="xl"
        >
          {title}
        </Text>
      </VStack>
      <VStack
        flex={1}
        overflow="auto"
        alignItems="stretch"
        p="12px"
        borderRight="1px solid"
        borderColor="cinza.main"
      >
        <VStack flex={1} gap="2px">
          {children}
        </VStack>
      </VStack>
    </VStack>
  );
}
