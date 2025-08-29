import {
  Box,
  Button,
  Card,
  CardBody,
  Divider,
  Heading,
  Text,
  VStack,
} from "@chakra-ui/react";
import { Wave } from "./login/_components/Waves";
import Boat from "./_components/misc/Boat";
import Link from "next/link";
import { IoArrowBack, IoHome } from "react-icons/io5";
import { ArrowBackIcon } from "@chakra-ui/icons";

export default async function NotFound() {
  return (
    <>
      <Box
        bgColor="cinza.main"
        width="100vw"
        height="100vh"
        position="absolute"
        top={0}
        left={0}
        display="flex"
        flexDirection="column-reverse"
        overflow="hidden"
        zIndex={-1000}
      >
        <Wave color="azul_1.main" depth={1} />
        <Wave color="azul_2.main" depth={2} />
        <Boat />
        <Wave color="azul_3.main" depth={3} />
        <Wave color="azul_4.main" depth={4} />
      </Box>
      <VStack
        gap="48px"
        top={0}
        left={0}
        position="absolute"
        w="100%"
        h="100%"
        justifyContent="center"
        alignItems="center"
      >
        <Heading size="2xl" fontWeight="normal" color="azul_1.main">
          Recurso não encontrado
        </Heading>
        <VStack alignItems="stretch">
          <Link href="/">
            <Button leftIcon={<IoHome />} colorScheme="azul_1">
              Voltar para a página inicial
            </Button>
          </Link>
          <Button as="div" colorScheme="red" leftIcon={<IoArrowBack />}>
            <div
              dangerouslySetInnerHTML={{
                __html:
                  '<button onclick="history.back()">Página anterior</button>',
              }}
            />
          </Button>
        </VStack>
      </VStack>
    </>
  );
}
