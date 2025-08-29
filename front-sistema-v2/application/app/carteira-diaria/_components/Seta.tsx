import { HStack, Icon, StackProps } from "@chakra-ui/react";
import { IoCaretBack, IoCaretForward } from "react-icons/io5";

export type SetaProps = {
  orientacao: "ESQUERDA" | "DIREITA";
  posicao: number;
  setPosicao: (novaPosicao: number) => void;
  tamanho: number;
} & StackProps;

export default function Seta({
  orientacao,
  posicao,
  setPosicao,
  tamanho,
  ...stackProps
}: SetaProps) {
  const ativo =
    orientacao === "ESQUERDA" ? posicao !== 0 : posicao !== tamanho - 1;
  return (
    <HStack
      cursor={ativo ? "pointer" : "not-allowed"}
      borderRadius="full"
      w="18px"
      h="18px"
      bgColor={ativo ? "cinza.main" : "cinza.200"}
      color={ativo ? "azul_2.main" : "cinza.400"}
      _hover={ativo ? { color: "azul_2.500" } : {}}
      onClick={() => {
        if (ativo) {
          setPosicao(posicao + (orientacao === "ESQUERDA" ? -1 : 1));
        }
      }}
      justifyContent={orientacao === "ESQUERDA" ? "flex-start" : "flex-end"}
      transition="all 0.125s"
      {...stackProps}
    >
      <Icon as={orientacao === "ESQUERDA" ? IoCaretBack : IoCaretForward} />
    </HStack>
  );
}
