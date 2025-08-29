import Hint from "@/app/_components/texto/Hint";
import { Fundo, Mesa } from "@/lib/types/api/iv/v1";
import {
  Button,
  HStack,
  Icon,
  StackDivider,
  Tab,
  TabList,
  Tabs,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react";
import { useMemo, useState } from "react";
import { IoStar } from "react-icons/io5";
import ListaFundosArrastaveis, {
  ControleArrasto,
} from "./ListaFundosArrastaveis";

export type TabMesasProps = {
  fundos: Fundo[];
  mesas: Mesa[];
};

export default function TabMesas({ fundos, mesas }: TabMesasProps) {
  const [controleArrasto, setControleArrasto] = useState<ControleArrasto>();
  const [idMesaSelecionada, setIdMesaSelecionada] = useState(mesas[0].id);
  const [mesasState, setMesasState] = useState(
    mesas.reduce((r, m) => ((r[m.id] = m), r), {} as Record<number, Mesa>),
  );

  const mesa = mesasState[idMesaSelecionada];

  const sob = useMemo(
    () => (
      <VStack flex={1} alignItems="stretch">
        <Hint color="cinza.600">
          <Icon color="amarelo.main" as={IoStar} /> Responsável (
          {mesa.fundos_responsavel.length})
        </Hint>
        <ListaFundosArrastaveis
          fundos={mesa.fundos_responsavel}
          setFundos={(fs) => {
            mesa.fundos_responsavel = fs;
            setMesasState({ ...mesasState, [mesa.id]: mesa });
          }}
          controleArrasto={controleArrasto}
          setControleArrasto={setControleArrasto}
          flex={1}
        />
      </VStack>
    ),
    [mesasState, idMesaSelecionada, controleArrasto],
  );

  const cog = useMemo(
    () => (
      <VStack flex={1} alignItems="stretch">
        <Hint color="cinza.600">
          Outras contribuições ({mesa.fundos_contribuidora.length})
        </Hint>
        <ListaFundosArrastaveis
          fundos={mesa.fundos_contribuidora}
          setFundos={(fs) => {
            mesa.fundos_contribuidora = fs;
            setMesasState({ ...mesasState, [mesa.id]: mesa });
          }}
          controleArrasto={controleArrasto}
          setControleArrasto={setControleArrasto}
          flex={1}
        />
      </VStack>
    ),
    [mesasState, idMesaSelecionada, controleArrasto],
  );

  const sem = useMemo(() => {
    const sg = fundos.filter(
      (f) =>
        !mesa.fundos_responsavel.map((f) => f.id).includes(f.id) &&
        !mesa.fundos_contribuidora.map((f) => f.id).includes(f.id),
    );
    return (
      <VStack flex={1} alignItems="stretch">
        <Hint>Sem interferência ({sg.length})</Hint>
        <ListaFundosArrastaveis
          fundos={sg}
          setFundos={() => {}}
          controleArrasto={controleArrasto}
          setControleArrasto={setControleArrasto}
          flex={1}
        />
      </VStack>
    );
  }, [mesasState, idMesaSelecionada, controleArrasto]);

  return (
    <VStack
      alignItems="stretch"
      onDragEnd={() => setControleArrasto(undefined)}
    >
      <Tabs
        variant="enclosed-colored"
        defaultValue={0}
        onChange={(i) => setIdMesaSelecionada(mesas[i].id)}
      >
        <TabList
          display="flex"
          flexDirection="row"
          justifyContent="space-between"
          mb="2px"
          alignItems="stretch"
        >
          <HStack
            alignItems="stretch"
            flex={1}
            overflowX="auto"
            overflowY="hidden"
            gap={0}
          >
            {mesas.map((m) => (
              <Tab key={m.id}>{m.nome}</Tab>
            ))}
          </HStack>
          <Button h="auto" borderBottomRadius="none">
            Adicionar
          </Button>
        </TabList>
      </Tabs>
      <VStack alignItems="flex-start">
        <Text>Sobre a mesa:</Text>
        <Textarea rows={10} size="sm" value={mesa.sobre} />
        <Button>Atualizar</Button>
      </VStack>
      <HStack alignItems="stretch">
        <HStack
          flex={2}
          alignItems="stretch"
          borderRadius="8px"
          p="8px"
          border="1px solid"
          borderColor="cinza.main"
          bgColor="cinza.50"
          divider={<StackDivider />}
        >
          {sob}
          {cog}
        </HStack>
        <HStack
          flex={1}
          alignItems="stretch"
          borderRadius="8px"
          p="8px"
          border="1px solid"
          borderColor="cinza.main"
          bgColor="azul_1.50"
        >
          {sem}
        </HStack>
      </HStack>
    </VStack>
  );
}
