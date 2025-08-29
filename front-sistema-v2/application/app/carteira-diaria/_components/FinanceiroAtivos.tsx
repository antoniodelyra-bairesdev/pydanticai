import Donut from "@/app/_components/graficos/Donut";
import { Futuro, Posicao } from "@/lib/types/leitor-carteiras-fundos/types";
import {
  Box,
  Card,
  CardBody,
  CardFooter,
  StackProps,
  Text,
  VStack,
} from "@chakra-ui/react";
import TotalEmAtivos from "./TotalEmAtivos";
import BarrasHorizontais from "@/app/_components/graficos/BarrasHorizontais";

export type FinanceiroAtivosProps = {
  posicoes: Posicao[];
  focoPosicao: number;
  tiposAtivos: string[];
  setTiposAtivosSelecionados: React.Dispatch<React.SetStateAction<string[]>>;
} & StackProps;

export default function FinanceiroAtivos({
  posicoes,
  focoPosicao,
  tiposAtivos: tiposAtivosSelecionados,
  setTiposAtivosSelecionados,
  ...stackProps
}: FinanceiroAtivosProps) {
  return (
    <VStack alignItems="stretch" {...stackProps}>
      <Card flex={1} overflow="hidden">
        <CardBody p={0}>
          <VStack alignItems="stretch" h="100%">
            <Box flex={1}>
              <BarrasHorizontais
                datasets={posicoes.map((posicao) => ({
                  nomeDataset: posicao.produto_investimento?.nome ?? "---",
                  dados:
                    posicao.produto_investimento &&
                    "ativos" in posicao.produto_investimento
                      ? Object.entries(
                          posicao.produto_investimento.ativos.reduce(
                            (mapa, posicao_ativo) => {
                              let valor = 0;
                              if (posicao_ativo.ativo.tipo == "Futuro") {
                                const ativo = posicao_ativo.ativo as Futuro;
                                valor = Number(ativo.valor_de_ajuste);
                              } else {
                                valor =
                                  Number(posicao_ativo.preco.preco_mercado) *
                                  Number(posicao_ativo.quantidade.total) *
                                  (posicao_ativo.vendido ? -1 : 1);
                              }
                              mapa[posicao_ativo.ativo.tipo] ??= 0;
                              mapa[posicao_ativo.ativo.tipo] += valor;
                              return mapa;
                            },
                            {} as Record<string, number>,
                          ),
                        ).map(([tipo, valor]) => ({ nome: tipo, valor }))
                      : [],
                }))}
                mainDatasetIndex={focoPosicao}
                maxHeight={500}
              />
              {/* dados={}
                selecionados={tiposAtivosSelecionados}
                setSelecionados={setTiposAtivosSelecionados}
                cores={{
                  background: [
                    "rgba(27, 49, 87, 0.7)",
                    "rgba(13, 102, 150, 0.7)",
                    "rgba(46, 150, 191, 0.7)",
                    "rgba(0, 186, 219, 0.7)",
                    "rgba(95, 187, 71, 0.7)",
                    "rgba(230, 231, 232, 0.7)",
                  ],
                  border: [
                    "rgba(27, 49, 87, 1)",
                    "rgba(13, 102, 150, 1)",
                    "rgba(46, 150, 191, 1)",
                    "rgba(0, 186, 219, 1)",
                    "rgba(95, 187, 71, 1)",
                    "rgba(230, 231, 232, 1)",
                  ],
                }}
              /> */}
            </Box>
          </VStack>
        </CardBody>
        {/* <CardFooter p="4px 12px" bgColor="verde.50">
          <Text w="100%" textAlign="center" fontSize="xs">
            Ativos com impacto positivo no PL
          </Text>
        </CardFooter> */}
      </Card>
      {/* <Card flex={1} overflow="hidden">
        <CardBody p="8px">
          <VStack h="100%">
            <Box flex={1}>
              <Donut
                dados={posicoes.map((posicao) => ({
                  rotulo: posicao.produto_investimento?.nome ?? "---",
                  dados:
                    posicao.produto_investimento &&
                    "ativos" in posicao.produto_investimento
                      ? Object.entries(
                          posicao.produto_investimento.ativos.reduce(
                            (mapa, posicao_ativo) => {
                              let valor = 0;
                              if (posicao_ativo.ativo.tipo == "Futuro") {
                                const ativo = posicao_ativo.ativo as Futuro;
                                valor = Number(ativo.valor_de_ajuste);
                              } else {
                                valor =
                                  Number(posicao_ativo.preco.preco_mercado) *
                                  Number(posicao_ativo.quantidade.total) *
                                  (posicao_ativo.vendido ? -1 : 1);
                              }
                              if (valor < 0) {
                                mapa[posicao_ativo.ativo.tipo] ??= 0;
                                mapa[posicao_ativo.ativo.tipo] += -valor;
                              }
                              return mapa;
                            },
                            {} as Record<string, number>,
                          ),
                        ).map(([tipo, valor]) => ({ rotulo: tipo, valor }))
                      : [],
                }))}
                selecionados={tiposAtivosSelecionados}
                setSelecionados={setTiposAtivosSelecionados}
                cores={{
                  background: [
                    "rgba(150, 59, 130, 0.7)",
                    "rgba(240, 79, 110, 0.7)",
                    "rgba(245, 140, 46, 0.7)",
                    "rgba(255, 194, 79, 0.7)",
                  ],
                  border: [
                    "rgba(150, 59, 130, 1)",
                    "rgba(240, 79, 110, 1)",
                    "rgba(245, 140, 46, 1)",
                    "rgba(255, 194, 79, 1)",
                  ],
                }}
              />
            </Box>
          </VStack>
        </CardBody>
        <CardFooter p="4px 12px" bgColor="rosa.50">
          <Text w="100%" textAlign="center" fontSize="xs">
            Ativos com impacto negativo no PL
          </Text>
        </CardFooter>
      </Card> */}
      <TotalEmAtivos posicoes={posicoes} focoPosicao={focoPosicao} />
    </VStack>
  );
}
