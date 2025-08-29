import { HStack, Icon, Text, Textarea, VStack } from "@chakra-ui/react";
import InputBenchmark from "./InputBenchmark";
import {
  IoAnalyticsOutline,
  IoBarChartOutline,
  IoPeopleOutline,
} from "react-icons/io5";
import { useFundoDetalhes } from "../_providers/FundoDetalhesProvider";

export default function BenchmarkETaxasConteudo() {
  const {
    editando,
    benchmark,
    setBenchmark,
    indices,
    setIndices,
    taxaPerformance,
    setTaxaPerformance,
    taxaAdministracao,
    setTaxaAdministracao,
  } = useFundoDetalhes();

  // console.log({ benchmark, indices })

  return (
    <VStack flex={1} alignItems="stretch" p="8px">
      <VStack alignItems="stretch">
        <HStack fontSize="sm">
          <Icon as={IoBarChartOutline} color="verde.main" />
          <Text>Benchmark</Text>
        </HStack>
        <InputBenchmark
          editando={editando}
          size="xs"
          listaIndices={[
            "CDI",
            "Dólar",
            "FED Funds Over",
            "IBrX-100",
            "IMA-B 5",
            "IMA-B 5+",
            "IRF-M 1+",
            "IPCA",
          ]}
          tokens={benchmark.split(" ")}
          indices={indices.map((i) => i.nome)}
          onTokensUpdate={(ts) => setBenchmark(ts.join(" "))}
          onIndicesUpdate={(i) =>
            setIndices(i.map((nome, ordenacao) => ({ nome, ordenacao })))
          }
        />
      </VStack>
      <VStack flex={1} alignItems="stretch">
        <HStack fontSize="sm">
          <Icon as={IoAnalyticsOutline} color="verde.main" />
          <Text>Taxa de performance</Text>
        </HStack>
        <Textarea
          value={taxaPerformance}
          onChange={(ev) => setTaxaPerformance(ev.currentTarget.value)}
          isDisabled={!editando}
          rows={1}
          flex={1}
          size="xs"
          focusBorderColor="verde.main"
        />
      </VStack>
      <VStack flex={1} alignItems="stretch">
        <HStack fontSize="sm">
          <Icon as={IoPeopleOutline} color="verde.main" />
          <Text>Taxa de administração</Text>
        </HStack>
        <Textarea
          value={taxaAdministracao}
          onChange={(ev) => setTaxaAdministracao(ev.currentTarget.value)}
          isDisabled={!editando}
          rows={1}
          flex={1}
          size="xs"
          focusBorderColor="verde.main"
        />
      </VStack>
    </VStack>
  );
}
