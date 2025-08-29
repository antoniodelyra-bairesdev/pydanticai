import { Box, HStack, StackProps } from "@chakra-ui/react";

export type ContagemBolinhasProps = {
  posicao: number;
  tamanho: number;
} & StackProps;

export default function ContagemBolinhas({
  posicao,
  tamanho,
  ...stackProps
}: ContagemBolinhasProps) {
  return (
    <HStack gap="4px" justifyContent="center" {...stackProps}>
      {Array(tamanho)
        .fill(0)
        .map((_, i) => (
          <Box
            key={i}
            w="4px"
            h="4px"
            borderRadius="full"
            bgColor={posicao === i ? "azul_3.main" : "cinza.main"}
            transition="all 0.125s"
          />
        ))}
    </HStack>
  );
}
