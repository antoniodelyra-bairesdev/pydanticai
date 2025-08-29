import { buscar } from "@/app/operacoes/_components/tabs/triagem-b3/fluxo/dados/companies";
import {
  Box,
  Divider,
  HStack,
  Icon,
  Radio,
  RadioGroup,
  Text,
  VStack,
} from "@chakra-ui/react";
import {
  IoBusinessOutline,
  IoPencilOutline,
  IoWalletOutline,
  IoCashOutline,
  IoArrowDownOutline,
  IoArrowUpOutline,
  IoSwapVerticalOutline,
  IoDocumentOutline,
} from "react-icons/io5";
import CardContaBancaria from "./CardContaBancaria";
import InputEditavel from "./InputEditavel";
import SelectXS from "./SelectXS";
import { useFundoDetalhes } from "../_providers/FundoDetalhesProvider";
import { InstituicaoFinanceira } from "@/lib/types/api/iv/v1";

export type AdministracaoConteudoProps = {
  lista_administradores: InstituicaoFinanceira[];
  lista_controladores: InstituicaoFinanceira[];
  lista_custodiantes: InstituicaoFinanceira[];
};

export default function AdministracaoConteudo({
  lista_administradores,
  lista_controladores,
  lista_custodiantes,
}: AdministracaoConteudoProps) {
  const {
    editando,
    fundoAtualizado,
    contaUnicaOuSegregada,
    setContaUnicaOuSegregada,
    contaAplicacao,
    setContaAplicacao,
    contaMovimentacao,
    setContaMovimentacao,
    contaResgate,
    setContaResgate,
    contaTributada,
    setContaTributada,
    contaUnica,
    setContaUnica,
  } = useFundoDetalhes();

  return (
    <VStack alignItems="stretch" fontSize="xs">
      <VStack p="8px 8px 0 8px" alignItems="stretch">
        <HStack gap="6px" fontSize="sm">
          <Icon color="verde.main" as={IoBusinessOutline} />
          <Text w="96px">Administrador</Text>
        </HStack>
        <HStack>
          <HStack flex={3}>
            <Box flex={1} p={0}>
              <SelectXS
                valor={{ label: "" }}
                onValorChange={() => {}}
                editando={editando}
                opcoes={lista_administradores.map(({ nome }) => ({
                  value: nome,
                  src: buscar(nome).icon as any,
                  label: nome,
                }))}
              />
            </Box>
          </HStack>
          <HStack flex={2}>
            <Text>Código da carteira:</Text>
            <InputEditavel
              flex={1}
              editando={editando}
              valor={fundoAtualizado.codigo_carteira ?? ""}
              textoValorVazio="Sem conta cadastrada"
            />
          </HStack>
        </HStack>
      </VStack>
      <Divider />
      <VStack p="0 8px" alignItems="stretch">
        <HStack gap="6px" fontSize="sm">
          <Icon color="verde.main" as={IoPencilOutline} />
          <Text w="96px">Controlador</Text>
        </HStack>
        <HStack>
          <HStack flex={3}>
            <Box flex={1} p={0}>
              <SelectXS
                valor={{ label: "" }}
                onValorChange={() => {}}
                editando={editando}
                opcoes={lista_controladores.map(({ nome }) => ({
                  value: nome,
                  src: buscar(nome).icon as any,
                  label: nome,
                }))}
              />
            </Box>
          </HStack>
        </HStack>
      </VStack>
      <Divider />
      <VStack p="0 8px" alignItems="stretch">
        <HStack gap="6px" fontSize="sm">
          <Icon color="verde.main" as={IoWalletOutline} />
          <Text w="96px">Custódia</Text>
        </HStack>
        <HStack>
          <HStack flex={3}>
            <Box flex={1} p={0}>
              <SelectXS
                valor={{ label: "" }}
                onValorChange={() => {}}
                editando={editando}
                opcoes={lista_custodiantes.map(({ nome }) => ({
                  value: nome,
                  src: buscar(nome).icon as any,
                  label: nome,
                }))}
              />
            </Box>
          </HStack>
          <HStack flex={2}>
            <HStack flex={1}>
              <Text>Banco:</Text>
              <InputEditavel
                editando={editando}
                valor={fundoAtualizado.codigo_carteira ?? ""}
              />
            </HStack>
            <HStack flex={1}>
              <Text>Agência:</Text>
              <InputEditavel
                editando={editando}
                valor={fundoAtualizado.codigo_carteira ?? ""}
                textoValorVazio="Sem conta cadastrada"
              />
            </HStack>
          </HStack>
        </HStack>
      </VStack>
      <VStack m="8px 8px 16px 8px" alignItems="stretch">
        <RadioGroup
          size="sm"
          colorScheme="verde"
          isDisabled={!editando}
          value={contaUnicaOuSegregada}
          onChange={(v) => setContaUnicaOuSegregada(v as any)}
        >
          <HStack>
            <Radio value="u">
              <Text fontSize="xs">Conta única</Text>
            </Radio>
            <Radio value="s">
              <Text fontSize="xs">Contas segregadas</Text>
            </Radio>
          </HStack>
        </RadioGroup>
        {contaUnicaOuSegregada === "s" ? (
          <HStack key={0} flexWrap="wrap" alignItems="stretch">
            {(editando || contaAplicacao) && (
              <CardContaBancaria
                editando={editando}
                titulo="Aplicação"
                valor={contaAplicacao}
                onValorChange={setContaAplicacao}
                icone={
                  <HStack fontSize="lg" gap={0} position="relative" w="14px">
                    <Icon
                      position="absolute"
                      color="cinza.400"
                      as={IoCashOutline}
                    />
                    <Icon
                      top="4px"
                      left="6px"
                      position="absolute"
                      color="verde.main"
                      as={IoArrowDownOutline}
                    />
                  </HStack>
                }
              />
            )}
            {(editando || contaResgate) && (
              <CardContaBancaria
                editando={editando}
                titulo="Resgate"
                valor={contaResgate}
                onValorChange={setContaResgate}
                icone={
                  <HStack fontSize="lg" gap={0} position="relative" w="14px">
                    <Icon
                      position="absolute"
                      color="cinza.400"
                      as={IoCashOutline}
                    />
                    <Icon
                      top="4px"
                      left="6px"
                      position="absolute"
                      color="rosa.main"
                      as={IoArrowUpOutline}
                    />
                  </HStack>
                }
              />
            )}
            {(editando || contaMovimentacao) && (
              <CardContaBancaria
                editando={editando}
                titulo="Movimentação"
                valor={contaMovimentacao}
                onValorChange={setContaMovimentacao}
                icone={
                  <Icon
                    mr="-6px"
                    as={IoSwapVerticalOutline}
                    color="azul_3.main"
                    fontSize="lg"
                  />
                }
              />
            )}
            {(editando || contaTributada) && (
              <CardContaBancaria
                editando={editando}
                titulo="Tributada"
                valor={contaTributada}
                onValorChange={setContaTributada}
                icone={
                  <HStack position="relative" fontSize="lg" gap={0} w="12px">
                    <Icon
                      position="absolute"
                      color="cinza.400"
                      as={IoDocumentOutline}
                    />
                    <Text
                      position="absolute"
                      color="rosa.main"
                      left="-1px"
                      fontWeight="bold"
                      fontSize="sm"
                    >
                      $
                    </Text>
                  </HStack>
                }
              />
            )}
          </HStack>
        ) : (
          <HStack>
            <CardContaBancaria
              editando={editando}
              valor={contaUnica}
              onValorChange={setContaUnica}
              titulo="Conta"
              icone={
                <Icon
                  mr="-6px"
                  fontSize="lg"
                  color="cinza.400"
                  as={IoWalletOutline}
                />
              }
            />
          </HStack>
        )}
      </VStack>
    </VStack>
  );
}
