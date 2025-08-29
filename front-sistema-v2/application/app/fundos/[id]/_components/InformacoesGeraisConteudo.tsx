import {
  Box,
  Card,
  CardBody,
  Checkbox,
  Divider,
  HStack,
  Radio,
  RadioGroup,
  Text,
  VStack,
} from "@chakra-ui/react";
import InputEditavel from "./InputEditavel";
import SelectXS from "./SelectXS";
import { buscar } from "@/app/operacoes/_components/tabs/triagem-b3/fluxo/dados/companies";
import { DisponibilidadeFundoEnum, GestorFundo } from "@/lib/types/api/iv/v1";
import { useFundoDetalhes } from "../_providers/FundoDetalhesProvider";
import Image from "next/image";

import IconeB3 from "@/public/b3.png";

export type InformacoesGeraisConteudoProps = {
  lista_gestores: GestorFundo[];
};

export default function InformacoesGeraisConteudo({
  lista_gestores,
}: InformacoesGeraisConteudoProps) {
  const {
    editando,
    nome,
    setNome,
    abertoCaptacao,
    setAbertoCaptacao,
    disponibilidade,
    setDisponibilidade,
    tickerB3,
    setTickerB3,
    cnpj,
    setCnpj,
    isin,
    setIsin,
    mnemonico,
    setMnemonico,
  } = useFundoDetalhes();

  return (
    <VStack h="100%" alignItems="stretch" fontSize="xs" p="8px">
      <HStack p="8px 8px 0 8px" alignItems="flex-start">
        <Text w="40px">Nome:</Text>
        <InputEditavel
          flex={1}
          editando={editando}
          valor={nome}
          onValorChange={setNome}
          textoValorVazio="Nome não cadastrado"
        />
      </HStack>
      <HStack p="0 8px" alignItems="flex-start">
        <HStack flex={1}>
          <Text w="40px">Gestor</Text>
          <Box flex={1}>
            <SelectXS
              valor={{ label: "" }}
              onValorChange={() => {}}
              editando={editando}
              opcoes={lista_gestores.map(({ nome }) => ({
                value: nome,
                src: buscar(nome).icon as any,
                label: nome,
              }))}
            />
          </Box>
        </HStack>
        <HStack flex={1}>
          <Text w="70px">Cogestor</Text>
          <Box flex={1}>
            <SelectXS
              valor={{ label: "" }}
              onValorChange={() => {}}
              editando={editando}
              opcoes={lista_gestores.map(({ nome }) => ({
                value: nome,
                src: buscar(nome).icon as any,
                label: nome,
              }))}
            />
          </Box>
        </HStack>
      </HStack>
      <HStack flex={1} alignItems="stretch" p="0 8px 8px 8px">
        <VStack
          alignItems="stretch"
          flex={2}
          border="1px solid"
          borderColor="cinza.main"
          borderRadius="8px"
          p="8px"
        >
          <Checkbox
            isDisabled={!editando}
            size="sm"
            isChecked={abertoCaptacao}
            onChange={(ev) => setAbertoCaptacao(ev.currentTarget.checked)}
            colorScheme="verde"
          >
            <Text as="span" fontSize="xs">
              Aberto para captação
            </Text>
          </Checkbox>
          <Divider />
          <HStack alignItems="stretch">
            <RadioGroup
              flex={1}
              size="sm"
              isDisabled={!editando}
              colorScheme="verde"
              value={disponibilidade as any}
              onChange={(v) => setDisponibilidade(Number(v) as any)}
            >
              <VStack alignItems="stretch">
                <Radio value={DisponibilidadeFundoEnum.Listado as any}>
                  <Text fontSize="xs">Listado</Text>
                </Radio>
                <Radio value={DisponibilidadeFundoEnum.Aberto as any}>
                  <Text fontSize="xs">Aberto</Text>
                </Radio>
                <Radio value={DisponibilidadeFundoEnum.Fechado as any}>
                  <Text fontSize="xs">Fechado</Text>
                </Radio>
                <Radio value={DisponibilidadeFundoEnum.Exclusivo as any}>
                  <Text fontSize="xs">Exclusivo</Text>
                </Radio>
              </VStack>
            </RadioGroup>
            {disponibilidade === DisponibilidadeFundoEnum.Listado && (
              <Card flex={3}>
                <CardBody>
                  <VStack justifyContent="center">
                    <HStack fontSize="sm">
                      <Image
                        alt="Ícone B3"
                        width={24}
                        height={24}
                        src={IconeB3}
                      />
                      <Text>Ticker</Text>
                    </HStack>
                    <InputEditavel
                      fontSize="lg"
                      fontWeight={600}
                      valor={tickerB3}
                      onValorChange={setTickerB3}
                      editando={editando}
                    />
                  </VStack>
                </CardBody>
              </Card>
            )}
          </HStack>
        </VStack>
        <VStack
          flex={2}
          alignItems="stretch"
          border="1px solid"
          borderColor="cinza.main"
          borderRadius="8px"
          p="8px"
        >
          <HStack>
            <Text w="80px">Tipo de fundo</Text>
            <InputEditavel
              flex={1}
              editando={editando}
              valor=""
              textoValorVazio="Não cadastrado"
            />
          </HStack>
          <Divider />
          <HStack>
            <Text w="80px">CNPJ:</Text>
            <InputEditavel
              flex={1}
              editando={editando}
              valor={cnpj}
              onValorChange={setCnpj}
              textoValorVazio="Não cadastrado"
            />
          </HStack>
          <HStack>
            <Text w="80px">ISIN:</Text>
            <InputEditavel
              flex={1}
              editando={editando}
              valor={isin}
              onValorChange={setIsin}
              textoValorVazio="Não cadastrado"
            />
          </HStack>
          <HStack>
            <Text w="80px">Mnemônico:</Text>
            <InputEditavel
              flex={1}
              editando={editando}
              valor={mnemonico}
              onValorChange={setMnemonico}
              textoValorVazio="Não cadastrado"
            />
          </HStack>
        </VStack>
      </HStack>
    </VStack>
  );
}
