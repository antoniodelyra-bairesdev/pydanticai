import { AlocacoesContext } from "@/lib/providers/AlocacoesProvider";
import {
  Box,
  Button,
  Divider,
  HStack,
  Icon,
  Input,
  ListItem,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tooltip,
  Tr,
  UnorderedList,
  useDisclosure,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useContext, useEffect, useMemo, useState } from "react";
import {
  IoCheckmarkCircle,
  IoCheckmarkOutline,
  IoCloseCircle,
  IoCloseOutline,
  IoCubeOutline,
} from "react-icons/io5";
import BoletaComponent from "../../boletas/BoletaComponent";
import { useHTTP, useUser } from "@/lib/hooks";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { ResultadoBuscaBoleta_Alocacao } from "@/lib/types/api/iv/operacoes/processamento";
import { selecao, selecionadasPertencentesA } from "../_helper";
import ModalSelecionadas from "../ModalSelecionadas";
import Hint from "@/app/_components/texto/Hint";

const problemasParaAprovar = (alocacao: ResultadoBuscaBoleta_Alocacao) => {
  const problemas: string[] = [];
  if (alocacao.cancelamento) {
    problemas.push("A alocação foi cancelada");
  }
  if (alocacao.aprovado_em) {
    problemas.push("A alocação já foi aprovada");
  }
  return problemas;
};

const problemasParaCancelar = (alocacao: ResultadoBuscaBoleta_Alocacao) =>
  alocacao.cancelamento ? ["A alocação já foi cancelada"] : [];

export default function AbaTriagem() {
  const { boletas } = useContext(AlocacoesContext);

  const boletasComPeloMenosUmaAlocacaoSemAprovacao = useMemo(
    () => boletas.filter((b) => b.boleta.alocacoes.some((a) => !a.aprovado_em)),
    [boletas],
  );

  const { isOpen: isDisabled, onToggle } = useDisclosure({
    defaultIsOpen: true,
  });

  const [selecionadas, setSelecionadas] = useState<
    Record<number, ResultadoBuscaBoleta_Alocacao>
  >({});

  useEffect(() => {
    setSelecionadas(
      selecionadasPertencentesA(boletasComPeloMenosUmaAlocacaoSemAprovacao),
    );
  }, [boletasComPeloMenosUmaAlocacaoSemAprovacao]);

  const httpClient = useHTTP({ withCredentials: true });

  const [intencao, setIntencao] = useState<"aprovar" | "cancelar" | null>(null);
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

  const aprovar = () => setIntencao("aprovar");
  const cancelar = () => setIntencao("cancelar");

  const { user } = useUser();

  const permissoes = new Set(
    user?.roles
      .filter((r) =>
        ["operacoes.cancelar", "operacoes.aprovar"].includes(r.nome),
      )
      .map((r) => r.nome),
  );

  return (
    <>
      <HStack
        h="100%"
        alignItems="stretch"
        p="8px"
        bgColor="cinza.main"
        overflowX="auto"
      >
        {permissoes.size && (
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
            <Divider />
            {permissoes.has("operacoes.aprovar") && (
              <Button
                isDisabled={isDisabled}
                size="xs"
                colorScheme="verde"
                leftIcon={<Icon as={IoCheckmarkOutline} />}
                onClick={aprovar}
              >
                Aprovar alocações
              </Button>
            )}
            {permissoes.has("operacoes.cancelar") && (
              <Button
                isDisabled={isDisabled}
                size="xs"
                colorScheme="rosa"
                leftIcon={<Icon as={IoCloseOutline} />}
                onClick={cancelar}
              >
                Cancelar alocações
              </Button>
            )}
          </VStack>
        )}
        <VStack minW="512px" flex={1} alignItems="stretch" overflowY="auto">
          <VStack
            p="8px"
            borderRadius="8px"
            bgColor="white"
            alignItems="stretch"
          >
            {boletasComPeloMenosUmaAlocacaoSemAprovacao.length === 0 ? (
              <Text textAlign="center" color="cinza.400" fontSize="sm">
                Não há alocações aguardando aprovação.
              </Text>
            ) : (
              boletasComPeloMenosUmaAlocacaoSemAprovacao.map((b) => (
                <BoletaComponent
                  key={b.client_id}
                  passo="TRIAGEM"
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
      <ModalSelecionadas<"aprovar" | "cancelar">
        intencao={intencao}
        acao={(intencao) => acao(intencao)}
        problemasIntencao={{
          aprovar: problemasParaAprovar,
          cancelar: problemasParaCancelar,
        }}
        selecionadas={selecionadas}
        setIntencao={setIntencao}
        titulos={{
          aprovar: "Aprovar operações",
          cancelar: "Cancelar operações",
        }}
      >
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
