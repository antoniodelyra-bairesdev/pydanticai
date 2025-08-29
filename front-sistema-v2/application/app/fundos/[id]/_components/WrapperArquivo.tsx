import Arquivo, { ArquivoProps } from "@/app/_components/misc/Arquivo";
import { getColorHex } from "@/app/theme";
import { Box, HStack, Icon } from "@chakra-ui/react";
import { IoArrowUndo, IoCloseOutline } from "react-icons/io5";

export enum EstadoArquivoEnum {
  normal,
  inserir,
  remover,
}

export type WrapperArquivoProps = {
  estado: EstadoArquivoEnum;
  onReverse: () => void;
} & ArquivoProps;

export default function WrapperArquivo({
  estado,
  onReverse,
  ...props
}: WrapperArquivoProps) {
  return (
    <HStack alignItems="stretch" position="relative">
      <HStack
        pointerEvents={estado !== EstadoArquivoEnum.normal ? "none" : undefined}
        alignItems="stretch"
        position="relative"
      >
        <Arquivo {...props} />
        {estado !== EstadoArquivoEnum.normal && (
          <Box
            borderRadius="4px"
            bgColor={
              getColorHex(
                estado === EstadoArquivoEnum.remover
                  ? "rosa.main"
                  : "verde.main",
              ) + "3f"
            }
            w="100%"
            h="100%"
            position="absolute"
            top={0}
            left={0}
          />
        )}
      </HStack>
      {estado !== EstadoArquivoEnum.normal && (
        <HStack
          onClick={onReverse}
          cursor="pointer"
          transition="0.25s all"
          position="absolute"
          justifyContent="center"
          w="24px"
          h="24px"
          bgColor={
            estado === EstadoArquivoEnum.remover
              ? "azul_3.main"
              : "laranja.main"
          }
          borderRadius="full"
          right="-4px"
          top="-4px"
          _groupHover={{ opacity: 1 }}
          _hover={{
            bgColor:
              estado === EstadoArquivoEnum.remover
                ? "azul_3.700"
                : "laranja.700",
          }}
        >
          <Icon
            as={
              estado === EstadoArquivoEnum.inserir
                ? IoCloseOutline
                : IoArrowUndo
            }
            color="white"
            boxSize="16px"
          />
        </HStack>
      )}
    </HStack>
  );
}
