import {
  Box,
  Card,
  CardBody,
  CardHeader,
  HStack,
  Icon,
  Text,
  VStack,
} from "@chakra-ui/react";
import Image, { StaticImageData } from "next/image";
import CopiarTexto from "./CopiarTexto";
import { IoTrash } from "react-icons/io5";

export type CardContaProps = {
  editando?: boolean;
  imagem: StaticImageData;
  nome: string;
  valor: string;
  tipoRegistro?: string;
  cor?: string;
  onValorChange?: (valor: string) => void;
};

export default function CardRegistro({
  editando,
  imagem,
  nome,
  valor,
  tipoRegistro,
  cor,
  onValorChange,
}: CardContaProps) {
  return (
    <Box position="relative" role="group">
      <Card variant="outline" overflow="hidden">
        <HStack alignItems="stretch" gap={0}>
          <Box w="4px" bgColor={cor ?? "azul_2.main"} />
          <VStack alignItems="stretch" gap={0}>
            <CardHeader p="4px 8px">
              <HStack>
                <Box
                  p="4px"
                  borderRadius="12px"
                  w="24px"
                  h="24px"
                  border="1px solid"
                  borderColor="cinza.main"
                >
                  <Image alt="Ícone" src={imagem} />
                </Box>
                <Text>{nome}</Text>
              </HStack>
            </CardHeader>
            <CardBody
              m="0px 8px 8px 8px"
              p={0}
              border="1px solid"
              borderColor="cinza.main"
              borderRadius="4px"
            >
              <HStack alignItems="stretch" h="24px" gap={0}>
                <HStack
                  bgColor="cinza.50"
                  p="0 4px"
                  justifyContent="center"
                  borderRight="1px solid"
                  borderColor="cinza.main"
                >
                  <Text>{tipoRegistro || "Conta"}</Text>
                </HStack>
                <CopiarTexto
                  onValorChange={onValorChange}
                  editando={editando}
                  valor={valor}
                  flex={1}
                />
              </HStack>
            </CardBody>
          </VStack>
        </HStack>
      </Card>
      {editando && (
        <HStack
          justifyContent="center"
          transition="0.25s all"
          position="absolute"
          cursor="pointer"
          borderRadius="full"
          w="24px"
          h="24px"
          right="-8px"
          top="-8px"
          bgColor="rosa.main"
          opacity={0}
          _groupHover={{ opacity: 1 }}
          _hover={{ bgColor: "rosa.700" }}
        >
          <Icon w="16px" h="16px" color="white" as={IoTrash} />
        </HStack>
      )}
    </Box>
  );
}
