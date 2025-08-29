"use client";

import {
  Box,
  Button,
  Card,
  CardBody,
  CardFooter,
  HStack,
  Icon,
  Select,
  StackProps,
  Text,
  VStack,
} from "@chakra-ui/react";

import React, { useState } from "react";

import Donut from "../_components/graficos/Donut";
import { Futuro, Posicao } from "@/lib/types/leitor-carteiras-fundos/types";
import { IoCardOutline, IoReloadOutline, IoSaveOutline } from "react-icons/io5";
import Cotas from "./_components/Cotas";
import Caixa from "./_components/Caixa";
import PatrimonioLiquido from "./_components/PatrimonioLiquido";
import Hint from "../_components/texto/Hint";
import Provisoes from "./_components/Provisoes";
import TotalEmAtivos from "./_components/TotalEmAtivos";
import GraficoProvisoes from "./_components/GraficoProvisoes";
import FinanceiroAtivos from "./_components/FinanceiroAtivos";
import { Tabela } from "../_components/grid/Tabela";
import TabelaAtivos from "./_components/TabelaAtivos";
import ControlesCarteiras from "./_components/ControlesCarteiras";

export type CarteiraComponentProps = {
  posicoes: Posicao[];
} & StackProps;

export default function CarteiraComponent({
  posicoes,
  ...vstackProps
}: CarteiraComponentProps) {
  const [tiposAtivos, setTiposAtivosSelecionados] = useState<string[]>(
    posicoes.flatMap((p) =>
      p.produto_investimento && "ativos" in p.produto_investimento
        ? p.produto_investimento.ativos.map((pos) => pos.ativo.tipo)
        : [],
    ),
  );

  const [focoPosicao, setFocoPosicao] = useState(0);

  return (
    <VStack alignItems="stretch" p="8px" bgColor="cinza.main" {...vstackProps}>
      <HStack alignItems="stretch" h="100%">
        <VStack alignItems="stretch">
          <Card p={0}>
            <CardBody p="8px" minW="360px">
              <Hint>Produto em evidência</Hint>
              <Select
                isDisabled={!posicoes.length}
                w="100%"
                size="xs"
                value={focoPosicao}
                onChange={(ev) => setFocoPosicao(Number(ev.target.value))}
              >
                {posicoes.map((p, i) => (
                  <option
                    key={p.data + (p.produto_investimento?.nome ?? i)}
                    value={i}
                  >
                    {p.produto_investimento?.nome ?? "---"}
                  </option>
                ))}
              </Select>
              <Button
                isDisabled={!posicoes.length}
                w="100%"
                size="xs"
                leftIcon={<Icon as={IoCardOutline} />}
              >
                Identificadores
              </Button>
            </CardBody>
          </Card>
          <VStack flex={1} alignItems="stretch">
            <FinanceiroAtivos
              posicoes={posicoes}
              focoPosicao={focoPosicao}
              tiposAtivos={tiposAtivos}
              setTiposAtivosSelecionados={setTiposAtivosSelecionados}
              flex={1}
            />
          </VStack>
        </VStack>
        <VStack flex={1} alignItems="stretch">
          <HStack alignItems="stretch">
            <VStack alignItems="stretch" w="280px">
              <PatrimonioLiquido
                posicoes={posicoes}
                focoPosicao={focoPosicao}
                setFocoPosicao={setFocoPosicao}
                flex={1}
              />
              <Caixa
                posicoes={posicoes}
                focoPosicao={focoPosicao}
                setFocoPosicao={setFocoPosicao}
                flex={1}
              />
            </VStack>
            <Cotas
              minW="260px"
              posicoes={posicoes}
              focoPosicao={focoPosicao}
              setFocoPosicao={setFocoPosicao}
            />
            <Card flex={1}>
              <CardBody p={0} flex={1}>
                <HStack w="100%" alignItems="stretch" h="100%">
                  <Provisoes
                    posicoes={posicoes}
                    focoPosicao={focoPosicao}
                    setFocoPosicao={setFocoPosicao}
                    position="relative"
                    alignItems="stretch"
                    justifyContent="space-between"
                    minW="256px"
                  />
                  <VStack flex={1} alignItems="stretch">
                    <Box h="100%">
                      <GraficoProvisoes
                        posicoes={posicoes}
                        focoPosicao={focoPosicao}
                      />
                    </Box>
                  </VStack>
                </HStack>
              </CardBody>
            </Card>
          </HStack>
          <HStack flex={1} alignItems="stretch">
            <Card w="280px">
              <VStack w="100%" h="100%" alignItems="stretch">
                <ControlesCarteiras />
              </VStack>
              <CardFooter p="8px">
                <HStack w="100%">
                  <Button
                    flex={1}
                    size="xs"
                    leftIcon={<Icon as={IoReloadOutline} />}
                  >
                    Redefinir
                  </Button>
                  <Button
                    flex={1}
                    size="xs"
                    leftIcon={<Icon as={IoSaveOutline} />}
                  >
                    Salvar preferências
                  </Button>
                </HStack>
              </CardFooter>
            </Card>
            <Card flex={1}>
              <VStack w="100%" h="100%" alignItems="stretch">
                <TabelaAtivos
                  posicoes={posicoes}
                  focoPosicao={focoPosicao}
                  flex={1}
                />
              </VStack>
            </Card>
          </HStack>
        </VStack>
      </HStack>
    </VStack>
  );
}
