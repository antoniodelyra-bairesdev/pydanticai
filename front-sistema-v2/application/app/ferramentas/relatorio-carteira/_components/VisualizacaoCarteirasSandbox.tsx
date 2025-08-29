"use client";

import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Checkbox,
  CheckboxGroup,
  HStack,
  Text,
  VStack,
} from "@chakra-ui/react";
import CarteiraComponent from "@/app/carteira-diaria/Carteira";
import { Posicao } from "@/lib/types/leitor-carteiras-fundos/types";
import { useCallback, useState } from "react";
import { posicoes } from "../_data/posicoes";

export default function VisualizacaoCarteirasSandbox() {
  const [iPosSel, setIPosSel] = useState<number[]>([]);
  const [pos, setPos] = useState<Posicao[]>([]);
  const atualizarDados = useCallback(() => {
    setPos(posicoes);
  }, []);

  return (
    <VStack
      w="100%"
      h="100%"
      alignItems="stretch"
      bgColor="cinza.main"
      pt="8px"
    >
      <HStack p="0 8px 0 8px">
        <Card flex={1}>
          <CardBody p="4px 12px 4px 24px">
            <Text>Fonte de dados</Text>
            <Button isDisabled size="xs" onClick={atualizarDados}>
              Atualizar fonte de dados
            </Button>
            <CheckboxGroup
              size="sm"
              value={iPosSel}
              onChange={(p) => setIPosSel(p.map((i) => Number(i)))}
            >
              {pos.map((p, i) => (
                <Checkbox key={i} isChecked={iPosSel.includes(i)} value={i}>
                  {p.data + " | " + p.produto_investimento?.nome}
                </Checkbox>
              ))}
            </CheckboxGroup>
          </CardBody>
        </Card>
      </HStack>
      <CarteiraComponent posicoes={pos} flex={1} />
    </VStack>
  );
}
