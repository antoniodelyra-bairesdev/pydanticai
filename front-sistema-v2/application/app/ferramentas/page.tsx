import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Divider,
  HStack,
  Heading,
  Text,
  VStack,
} from "@chakra-ui/react";
import Link from "next/link";
import React from "react";

export default function FerramentasPage() {
  const quickAccess: {
    title: string;
    description: React.ReactNode;
    link: string;
  }[] = [
    {
      title: "Conversor de carteiras",
      description: (
        <VStack alignItems="flex-start">
          <Text fontSize="sm">
            Conversor de carteiras no formato XML5.0 para XML4.01.
          </Text>
        </VStack>
      ),
      link: "/ferramentas/conversor-carteiras",
    },
    {
      title: "Visualização de carteiras",
      description: (
        <Text fontSize="sm">Visualizador e comparador de carteiras</Text>
      ),
      link: "/ferramentas/relatorio-carteira",
    },
  ];

  return (
    <VStack alignItems="stretch" p="64px" h="100%">
      <Heading size="lg" mb="12px" data-test-id="welcome-heading">
        Ferramentas
      </Heading>
      <Divider mb="12px" />
      <HStack mb="12px" alignItems="flex-start" gap="12px" wrap="wrap">
        {quickAccess.map(({ description, link, title }) => (
          <Card key={link + title} overflow="hidden" w="300px" minH="256px">
            <CardHeader bgColor="azul_1.main" p="16px">
              <Heading color="white" size="sm">
                {title}
              </Heading>
            </CardHeader>
            <CardBody p="12px 16px">{description}</CardBody>
            <CardFooter>
              <Link href={link}>
                <Button colorScheme="verde">Acessar</Button>
              </Link>
            </CardFooter>
          </Card>
        ))}
      </HStack>
    </VStack>
  );
}
