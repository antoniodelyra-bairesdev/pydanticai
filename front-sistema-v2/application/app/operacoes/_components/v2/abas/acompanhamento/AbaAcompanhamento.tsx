"use client";

import {
  Box,
  Button,
  Divider,
  HStack,
  Icon,
  Input,
  ListItem,
  Text,
  UnorderedList,
  useDisclosure,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useContext, useEffect, useMemo, useState } from "react";
import { AlocacoesContext } from "@/lib/providers/AlocacoesProvider";
import BoletaComponent from "../../boletas/BoletaComponent";
import { useHTTP, useUser } from "@/lib/hooks";
import {
  IoArrowUpCircleOutline,
  IoBusinessOutline,
  IoCashOutline,
  IoCloseCircleOutline,
  IoCloseOutline,
  IoWarning,
} from "react-icons/io5";
import Hint from "@/app/_components/texto/Hint";
import ModalSelecionadas from "../ModalSelecionadas";
import { ResultadoBuscaBoleta_Alocacao } from "@/lib/types/api/iv/operacoes/processamento";
import { selecao, selecionadasPertencentesA } from "../_helper";
import Comment from "@/app/_components/misc/Comment";

const problemasParaCancelar = (alocacao: ResultadoBuscaBoleta_Alocacao) =>
  alocacao.cancelamento ? ["A alocação já foi cancelada"] : [];

export default function AbaAcompanhamento() {
  const { boletas } = useContext(AlocacoesContext);

  const boletasComPeloMenosUmaAlocacaoAprovada = useMemo(
    () => boletas.filter((b) => b.boleta.alocacoes.some((a) => a.aprovado_em)),
    [boletas],
  );

  const [selecionadas, setSelecionadas] = useState<
    Record<number, ResultadoBuscaBoleta_Alocacao>
  >({});

  useEffect(() => {
    setSelecionadas(
      selecionadasPertencentesA(boletasComPeloMenosUmaAlocacaoAprovada),
    );
  }, [boletasComPeloMenosUmaAlocacaoAprovada]);

  const { isOpen: isDisabled, onToggle } = useDisclosure({
    defaultIsOpen: true,
  });

  const [intencao, setIntencao] = useState<
    | "liquidacao"
    | "cancelar"
    | "alocar-administrador"
    | "cancelar-administrador"
    | null
  >(null);

  const httpClient = useHTTP({ withCredentials: true });

  const [motivoCancelamento, setMotivoCancelamento] = useState("");

  const acao = useCallback(
    (rota: string) => {
      const ids = Object.entries(selecionadas)
        .filter((e) => e[1])
        .map((e) => e[0])
        .join(",");

      httpClient.fetch(
        `v1/operacoes/alocacoes/${rota}?ids=${ids}${motivoCancelamento ? `&motivo=${motivoCancelamento}` : ""}`,
        {
          method: "POST",
          hideToast: { success: true },
        },
      );
    },
    [selecionadas, motivoCancelamento],
  );

  const liquidar = () => setIntencao("liquidacao");
  const cancelar = () => setIntencao("cancelar");
  const alocarAdministrador = () => setIntencao("alocar-administrador");
  const cancelarAdministrador = () => setIntencao("cancelar-administrador");

  const { user } = useUser();

  const permissoesInternas = new Set(
    user?.roles
      .filter((r) =>
        ["operacoes.liquidacao", "operacoes.cancelar"].includes(r.nome),
      )
      .map((r) => r.nome),
  );

  const permissoesAdm = new Set(
    user?.roles
      .filter((r) =>
        [
          "operacoes.cancelar.administrador",
          "operacoes.alocar.administrador",
        ].includes(r.nome),
      )
      .map((r) => r.nome),
  );

  return (
    <>
      <HStack h="100%" alignItems="stretch" p="8px" bgColor="cinza.main">
        {permissoesInternas.size + permissoesAdm.size && (
          <VStack
            alignItems="stretch"
            p="8px"
            borderRadius="8px"
            minW="256px"
            bgColor="white"
          >
            <Button size="xs" onClick={onToggle}>
              {isDisabled ? "Habilitar ações" : "Desabilitar ações"}
            </Button>
            {permissoesInternas.size && (
              <>
                <Divider />
                <Hint>Ações internas</Hint>
                {permissoesInternas.has("operacoes.liquidacao") && (
                  <Button
                    isDisabled={isDisabled}
                    size="xs"
                    colorScheme="verde"
                    onClick={liquidar}
                    leftIcon={<Icon as={IoCashOutline} />}
                  >
                    Sinalizar liquidação
                  </Button>
                )}
                {permissoesInternas.has("operacoes.cancelar") && (
                  <Button
                    isDisabled={isDisabled}
                    size="xs"
                    colorScheme="rosa"
                    onClick={cancelar}
                    leftIcon={<Icon as={IoCloseOutline} />}
                  >
                    Cancelar/Solicitar cancelamento
                  </Button>
                )}
              </>
            )}
            {permissoesAdm.size && (
              <>
                <Divider />
                <Hint>Ações administrador</Hint>
                {permissoesAdm.has("operacoes.alocar.administrador") && (
                  <Button
                    isDisabled={isDisabled}
                    size="xs"
                    colorScheme="azul_1"
                    onClick={alocarAdministrador}
                    leftIcon={<Icon as={IoArrowUpCircleOutline} />}
                  >
                    Sinalizar alocação no adm.
                  </Button>
                )}
                {permissoesAdm.has("operacoes.cancelar.administrador") && (
                  <Button
                    isDisabled={isDisabled}
                    size="xs"
                    colorScheme="rosa"
                    onClick={cancelarAdministrador}
                    leftIcon={<Icon as={IoCloseCircleOutline} />}
                  >
                    Sinalizar cancelamento no adm.
                  </Button>
                )}
              </>
            )}
          </VStack>
        )}
        <VStack
          minW="512px"
          borderRadius="8px"
          flex={1}
          alignItems="stretch"
          overflowY="auto"
        >
          <VStack
            borderRadius="8px"
            p="8px"
            alignItems="stretch"
            bgColor="white"
            position="relative"
          >
            {boletasComPeloMenosUmaAlocacaoAprovada.length === 0 ? (
              <Text textAlign="center" color="cinza.400" fontSize="sm">
                Não há alocações na área de acompanhamento.
              </Text>
            ) : (
              boletasComPeloMenosUmaAlocacaoAprovada.map((b, i) => (
                <BoletaComponent
                  key={i}
                  passo="ACOMPANHAMENTO"
                  boleta={b}
                  selecionavel={!isDisabled}
                  onAlocacaoSelecionada={(sel, aloc) =>
                    setSelecionadas(selecao(sel, aloc, b))
                  }
                />
              ))
            )}
          </VStack>
        </VStack>
      </HStack>
      <ModalSelecionadas<
        | "liquidacao"
        | "cancelar"
        | "alocar-administrador"
        | "cancelar-administrador"
      >
        intencao={intencao}
        acao={(intencao) => acao(intencao)}
        problemasIntencao={{
          liquidacao: () => [],
          cancelar: problemasParaCancelar,
          "alocar-administrador": () => [],
          "cancelar-administrador": () => [],
        }}
        selecionadas={selecionadas}
        setIntencao={setIntencao}
        titulos={{
          liquidacao: "Sinalizar operações como liquidadas",
          cancelar: "Cancelar / Solicitar cancelamento",
          "alocar-administrador": "Sinalizar alocação no administrador",
          "cancelar-administrador": "Sinalizar cancelamento no administrador",
        }}
      >
        {intencao === "cancelar" && (
          <HStack
            bgColor="amarelo.50"
            alignItems="stretch"
            borderRadius="6px"
            overflow="hidden"
            minH="90px"
            mb="12px"
          >
            <Box w="6px" bgColor="amarelo.main" />
            <VStack
              p="16px"
              color="amarelo.900"
              fontSize="sm"
              alignItems="stretch"
            >
              <HStack gap="4px" mb="4px">
                <Icon as={IoWarning} w="20px" h="20px" />
                <Text as="strong" fontSize="lg" fontWeight={900}>
                  Aviso
                </Text>
              </HStack>
              <Comment p="12px">
                Diferente da etapa de triagem, dependendo do estado da alocação,
                a solicitação <strong>não garante cancelamento imediato</strong>
                .
              </Comment>
              <UnorderedList lineHeight={1.125}>
                <ListItem m="4px 0">
                  Caso as alocações tenham sido alocadas no administrador, é
                  necessário aguardar o time de BackOffice solicitar este
                  cancelamento para o administrador. Dependendo do horário,{" "}
                  <strong>existe a chance da operação já ter liquidado</strong>.
                </ListItem>
                <ListItem>
                  Caso as alocações selecionadas estejam atreladas a um voice e
                  o cancelamento delas represente o cancelamento{" "}
                  <strong>total</strong> do voice{" "}
                  <em>
                    (por exemplo, duas alocações de 150 quantidades atreladas a
                    um voice de 300 quantidades)
                  </em>
                  ,{" "}
                  <strong>
                    é necessário cancelá-lo manualmente via TradeMate
                  </strong>
                  .
                </ListItem>
              </UnorderedList>
            </VStack>
          </HStack>
        )}
        {intencao === "cancelar" && Object.keys(selecionadas).length > 0 && (
          <VStack gap={0} alignItems="stretch" mb="12px">
            <Hint>Motivo</Hint>
            <Input
              value={motivoCancelamento}
              onChange={(ev) => setMotivoCancelamento(ev.target.value)}
              placeholder="Informe o motivo..."
            />
          </VStack>
        )}
      </ModalSelecionadas>
    </>
  );
}
