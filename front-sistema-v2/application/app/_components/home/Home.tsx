"use client";

import { useUser } from "@/lib/hooks";
import {
  Box,
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Divider,
  HStack,
  Heading,
  Icon,
  List,
  ListIcon,
  ListItem,
  Text,
  VStack,
} from "@chakra-ui/react";
import Link from "next/link";
import React from "react";
import {
  IoHelpCircleOutline,
  IoSearchOutline,
  IoWarning,
} from "react-icons/io5";

export default function Home() {
  const { user } = useUser();

  const quickAccess: {
    title: string;
    description: React.ReactNode;
    link: string;
  }[] = [
    {
      title: "Streamlit - Crédito Privado",
      description: (
        <>
          <Text fontSize="sm">
            Sistema de crédito com calculadora, boletador, rotinas e outras
            funcionalidades.
          </Text>
          <Text fontSize="sm" as="span" color="amarelo.main">
            <Icon as={IoWarning} /> Acessível somente pelo AQWA.
          </Text>
        </>
      ),
      link: "http://192.168.254.47:8501",
    },
    {
      title: "Ferramentas",
      description: (
        <Text fontSize="sm">Ferramentas de carteiras de fundos.</Text>
      ),
      link: "/ferramentas",
    },
    {
      title: "Dashboards",
      description: (
        <Text fontSize="sm">
          Agrupamento de relatórios de Power BI das áreas.
        </Text>
      ),
      link: "/dashboard",
    },
    {
      title: "Liberação de cotas",
      description: (
        <VStack alignItems="flex-start">
          <Text fontSize="sm">Rotinas de liberação de cotas.</Text>
        </VStack>
      ),
      link: "/liberacao-cotas",
    },
    {
      title: "Enquadramento OMNiS",
      description: (
        <Text fontSize="sm">
          Exportação de arquivos de entrada para o OMNiS
        </Text>
      ),
      link: "/enquadramento",
    },
    {
      title: "Boletamento Fluxo II",
      description: (
        <Text fontSize="sm">
          Sistema para visualização, auto-alocação e acompanhamento de ordens de
          Debêntures, CRIs, CRAs e CFFs.
        </Text>
      ),
      link: "/operacoes",
    },
    {
      title: "Inquilinos GRUL11",
      description: (
        <Text fontSize="sm">
          Painel de controle de emissão de boletos para os inquilinos do galpão
          logístico do fundo GRUL11.
        </Text>
      ),
      link: "/locacoes",
    },
    {
      title: "Lista de fundos",
      description: (
        <Text fontSize="sm">
          Visualização de fundos cadastrados no sistema.
        </Text>
      ),
      link: "/fundos",
    },
    {
      title: "Painel do Site Institucional",
      description: (
        <Text fontSize="sm">
          Painel administrativo para alterar dados do site institucional.
        </Text>
      ),
      link: "/site-institucional",
    },
  ];

  return (
    <VStack
      alignItems="flex-start"
      p="64px"
      gap={0}
      h="100%"
      justifyContent="space-between"
    >
      <Box w="100%">
        <Heading size="lg" mb="12px" data-test-id="welcome-heading">
          Bem vindo(a) {user?.nome}!
        </Heading>
        <Divider />
        <Heading mt="24px" mb="12px" size="md">
          Acesso rápido
        </Heading>
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
      </Box>
      <Box w="100%">
        <Divider />
        <Heading mt="24px" size="md">
          Links úteis
        </Heading>
        <List>
          <ListItem>
            <Link
              href="https://www.notion.so/icatu-vanguarda/Como-utilizar-o-sistema-fae9ad0942ee4ccda5e7bc99d4d8cbe2"
              target="_blank"
            >
              <ListIcon as={IoHelpCircleOutline} />
              <Text textDecoration="underline" as="span">
                Notion: Como utilizar o sistema
              </Text>
            </Link>
          </ListItem>
          <ListItem>
            <Link
              href="https://www.notion.so/icatu-vanguarda/Wiki-de-An-lise-9959c1ced68e47fba4591438f6157535"
              target="_blank"
            >
              <ListIcon as={IoSearchOutline} />
              <Text textDecoration="underline" as="span">
                Notion: Wiki de Análise de Crédito
              </Text>
            </Link>
          </ListItem>
        </List>
      </Box>
    </VStack>
  );
}
