import {
  Box,
  HStack,
  Icon,
  keyframes,
  Stack,
  StackProps,
  Text,
  TextProps,
  VStack,
} from "@chakra-ui/react";
import React from "react";
import {
  IoCheckmarkCircle,
  IoCloseCircle,
  IoEllipse,
  IoEllipseOutline,
  IoEllipsisHorizontalCircle,
  IoEllipsisHorizontalCircleOutline,
  IoHelpCircleOutline,
  IoReloadCircleOutline,
  IoSyncCircleOutline,
} from "react-icons/io5";

export enum PassoEstado {
  AGUARDANDO,
  EM_ANDAMENTO,
  CONCLUIDO,
  ERRO,
  DESCONHECIDO
}

export type PassoInfo = {
  estado: PassoEstado;
  titulo: string;
  conteudo?: React.ReactNode;
};

export type PassosProps = {
  passos: PassoInfo[];
  orientacao?: "V" | "H";
  tituloProps?: TextProps;
} & StackProps;

const frames = keyframes`
    0% { transform: rotate(0turn); }
    100% { transform: rotate(1turn); }
`;

const animation = `${frames} 1s linear infinite`;

export default function Passos({
  passos,
  tituloProps,
  orientacao = "V",
  ...props
}: PassosProps) {
  return (
    <Stack
      flexDirection={orientacao === "V" ? "column" : "row"}
      {...props}
      alignItems="stretch"
      gap={0}
    >
      {passos.map((p, i) => (
        <HStack
          flex={1}
          key={i}
          alignItems="stretch"
          {...{ [orientacao === "V" ? "pt" : "pl"]: i === 0 ? "12px" : 0 }}
          gap={0}
        >
          <Stack
            alignItems="flex-start"
            justifyContent={orientacao === "V" ? undefined : "center"}
            flexDirection={orientacao === "V" ? "column" : "row"}
            {...{ [orientacao === "V" ? "minH" : "minW"]: "48px" }}
            flex={1}
            gap={0}
            position="relative"
          >
            {orientacao === "H" && i !== 0 && (
              <Box
                position="absolute"
                h="4px"
                w="50%"
                left={0}
                top="14px"
                zIndex={2}
                bgColor={
                  {
                    [PassoEstado.AGUARDANDO]: "cinza.main",
                    [PassoEstado.EM_ANDAMENTO]: "cinza.main",
                    [PassoEstado.CONCLUIDO]: "verde.main",
                    [PassoEstado.ERRO]: "cinza.main",
                    [PassoEstado.DESCONHECIDO]: "cinza.main",
                  }[passos[i - 1].estado]
                }
              />
            )}
            {i !== passos.length - 1 && (
              <Box
                position="absolute"
                w={orientacao === "V" ? "4px" : "50%"}
                h={orientacao === "V" ? "100%" : "4px"}
                left={orientacao === "V" ? "14px" : "50%"}
                top={orientacao === "V" ? 0 : "14px"}
                zIndex={2}
                bgColor={
                  {
                    [PassoEstado.AGUARDANDO]: "cinza.main",
                    [PassoEstado.EM_ANDAMENTO]: "cinza.main",
                    [PassoEstado.CONCLUIDO]: "verde.main",
                    [PassoEstado.ERRO]: "cinza.main",
                    [PassoEstado.DESCONHECIDO]: "cinza.main",
                  }[p.estado]
                }
              />
            )}
            <Stack
              flexDirection={orientacao === "V" ? "row" : "column"}
              alignItems={orientacao === "V" ? "flex-start" : "center"}
            >
              <Box
                w="32px"
                h="32px"
                {...{ [orientacao === "V" ? "mt" : "ml"]: "-4px" }}
                bgColor="white"
                borderRadius="full"
                zIndex={3}
              >
                <Icon
                  w="100%"
                  h="100%"
                  as={
                    {
                      [PassoEstado.AGUARDANDO]: IoEllipseOutline,
                      [PassoEstado.EM_ANDAMENTO]: IoSyncCircleOutline,
                      [PassoEstado.CONCLUIDO]: IoCheckmarkCircle,
                      [PassoEstado.ERRO]: IoCloseCircle,
                      [PassoEstado.DESCONHECIDO]: IoHelpCircleOutline,
                    }[p.estado]
                  }
                  color={
                    {
                      [PassoEstado.AGUARDANDO]: "cinza.main",
                      [PassoEstado.EM_ANDAMENTO]: "azul_4.main",
                      [PassoEstado.CONCLUIDO]: "verde.main",
                      [PassoEstado.ERRO]: "rosa.main",
                      [PassoEstado.DESCONHECIDO]: "cinza.main",
                    }[p.estado]
                  }
                  animation={
                    p.estado === PassoEstado.EM_ANDAMENTO
                      ? animation
                      : undefined
                  }
                />
              </Box>
              <VStack flex={1} alignItems="stretch" p="4px 12px 4px 12px">
                <Text
                  alignSelf={orientacao === "H" ? "center" : "flex-start"}
                  fontSize="sm"
                  {...tituloProps}
                >
                  {p.titulo}
                </Text>
                {p.conteudo}
              </VStack>
            </Stack>
          </Stack>
        </HStack>
      ))}
    </Stack>
  );
}
