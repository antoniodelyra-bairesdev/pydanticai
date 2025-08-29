import { Box, HStack, Icon, Text, Textarea, VStack } from "@chakra-ui/react";
import SelectXS from "./SelectXS";
import {
  IoBulbOutline,
  IoDocumentOutline,
  IoDocumentsOutline,
  IoLibraryOutline,
  IoPeopleOutline,
  IoPersonAdd,
  IoStar,
} from "react-icons/io5";
import { FundoCaracteristicaExtra, Mesa } from "@/lib/types/api/iv/v1";
import { useFundoDetalhes } from "../_providers/FundoDetalhesProvider";

export type GestaoConteudoProps = {
  lista_mesas: Mesa[];
  caracteristicas_extras: FundoCaracteristicaExtra[];
};

export default function GestaoConteudo({
  lista_mesas,
  caracteristicas_extras,
}: GestaoConteudoProps) {
  const {
    editando,
    mesaResponsavel,
    setMesaResponsavel,
    mesasContribuidoras,
    setMesasContribuidoras,
    resumoEstrategias,
    setResumoEstrategias,
    caracteristicasExtras,
    setCaracteristicasExtras,
  } = useFundoDetalhes();

  return (
    <HStack alignItems="stretch" p="8px">
      <VStack alignItems="stretch" fontSize="xs">
        <HStack gap="6px" fontSize="sm">
          <Icon color="verde.main" as={IoPeopleOutline} />
          <Text>Mesas envolvidas</Text>
        </HStack>
        <HStack>
          <Text w="128px">
            <Icon as={IoStar} color="amarelo.main" /> Responsável
          </Text>
          <Box flex={1} p={0}>
            <SelectXS
              valor={mesaResponsavel ? { label: mesaResponsavel?.nome } : null}
              onValorChange={(v: any) =>
                setMesaResponsavel(lista_mesas.find((m) => m.nome === v.label))
              }
              editando={editando}
              opcoes={lista_mesas.map(({ id, nome }) => ({
                value: id,
                label: nome,
              }))}
            />
          </Box>
        </HStack>
        <HStack>
          <Text w="128px">
            <Icon as={IoPersonAdd} color="azul_3.main" /> Contribuidoras
          </Text>
          <Box flex={1} p={0}>
            <SelectXS
              isMulti
              valor={mesasContribuidoras.map((m) => ({ label: m.nome }))}
              onValorChange={(vs: any) => {
                const ms = new Set<string>(vs.map((v: any) => v.label));
                setMesasContribuidoras(
                  lista_mesas.filter((m) => ms.has(m.nome)),
                );
              }}
              editando={editando}
              opcoes={lista_mesas.map(({ id, nome }) => ({
                value: id,
                label: nome,
              }))}
            />
          </Box>
        </HStack>
      </VStack>
      <VStack flex={1} alignItems="stretch">
        <HStack gap="6px" fontSize="sm">
          <Icon color="verde.main" as={IoLibraryOutline} />
          <Text>Resumo das estratégias</Text>
        </HStack>
        <Textarea
          value={resumoEstrategias}
          onChange={(ev) => setResumoEstrategias(ev.currentTarget.value)}
          isDisabled={!editando}
          rows={1}
          flex={1}
          size="xs"
          focusBorderColor="verde.main"
        />
      </VStack>
      <VStack fontSize="xs" flex={1} alignItems="stretch">
        <HStack gap="6px" fontSize="sm">
          <Icon color="verde.main" as={IoDocumentsOutline} />
          <Text>Características</Text>
        </HStack>
        <HStack>
          <Text w="128px">
            <Icon as={IoDocumentOutline} color="azul_2.main" /> Classificação
          </Text>
          <Box flex={1} p={0}>
            <SelectXS
              isMulti
              valor={caracteristicasExtras.map((m) => ({ label: m.nome }))}
              onValorChange={(vs: any) => {
                const cs = new Set<string>(vs.map((v: any) => v.label));
                setCaracteristicasExtras(
                  caracteristicas_extras.filter((c) => cs.has(c.nome)),
                );
              }}
              editando={editando}
              opcoes={caracteristicas_extras.map(({ id, nome }) => ({
                value: id,
                label: nome,
              }))}
            />
          </Box>
        </HStack>
        <HStack>
          <Text w="128px">
            <Icon as={IoBulbOutline} color="amarelo.main" /> Características
            extras
          </Text>
          <Box flex={1} p={0}>
            <SelectXS
              isMulti
              valor={caracteristicasExtras.map((m) => ({ label: m.nome }))}
              onValorChange={(vs: any) => {
                const cs = new Set<string>(vs.map((v: any) => v.label));
                setCaracteristicasExtras(
                  caracteristicas_extras.filter((c) => cs.has(c.nome)),
                );
              }}
              editando={editando}
              opcoes={caracteristicas_extras.map(({ id, nome }) => ({
                value: id,
                label: nome,
              }))}
            />
          </Box>
        </HStack>
      </VStack>
    </HStack>
  );
}
