import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import {
  Box,
  Button,
  HStack,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import FluxoNegociacao, { FluxoNegociacaoMethods } from "./FluxoNegociacao";
import TabelaAlocacoes from "./TabelaAlocacoes";
import EventoOperacaoItem, { EstadoSelecao } from "./EventoOperacaoItem";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  Alocacao,
  Erro,
  EventoAlocacaoOperador,
  EventoAprovacaoBackoffice,
  EventoOperacao,
  OperacaoType,
} from "@/lib/types/api/iv/v1";
import {
  IoPlayBack,
  IoPlayForward,
  IoPlaySkipBack,
  IoPlaySkipForward,
} from "react-icons/io5";
import ModalInteracaoAlocacao from "./ModalInteracaoAlocacao";
import { fmtNumber } from "@/lib/util/string";
import ModalRealocacao from "./ModalRealocacao";
import ModalDetalhesErro from "./ModalDetalhesErro";

export type ModalOperacaoProps = {
  operacao: OperacaoType;
  isOpen: boolean;
  onClose: () => void;
};

export default function ModalOperacao({
  operacao,
  isOpen,
  onClose,
}: ModalOperacaoProps) {
  const eventos: EventoOperacao[] = operacao.eventos;

  const {
    isOpen: isAlocacoesOpen,
    onClose: onAlocacoesClose,
    onOpen: onAlocacoesOpen,
  } = useDisclosure();
  const {
    isOpen: isRealocacaoOpen,
    onClose: onRealocacaoClose,
    onOpen: onRealocacaoOpen,
  } = useDisclosure();
  const {
    isOpen: isErroOpen,
    onClose: onErroClose,
    onOpen: onErroOpen,
  } = useDisclosure();

  const [eventoAlocacaoSelecionado, setEventoAlocacaoSelecionado] = useState<{
    eventoAlocacao: EventoAlocacaoOperador;
    habilitarControles: boolean;
    eventoAprovacao?: EventoAprovacaoBackoffice;
  } | null>(null);

  const [eventoRealocacaoSelecionado, setEventoRealocacaoSelecionado] =
    useState<{
      pos: "backoffice" | "custodiante";
      idEvento: number;
    } | null>(null);

  const [erroSelecionado, setErroSelecionado] = useState<Erro | null>(null);

  const selectAlocacaoInterna = (
    eventoAlocacao: EventoAlocacaoOperador,
    habilitarControles: boolean,
    eventoAprovacao?: EventoAprovacaoBackoffice,
  ) => {
    setEventoAlocacaoSelecionado({
      eventoAlocacao,
      habilitarControles,
      eventoAprovacao,
    });
    onAlocacoesOpen();
  };

  const deselectAlocacaoInterna = () => {
    setEventoAlocacaoSelecionado(null);
    onAlocacoesClose();
  };

  const abrirMenuAlocacao = (
    pos: "backoffice" | "custodiante",
    idEvento: number,
  ) => {
    setEventoRealocacaoSelecionado({ pos, idEvento });
    onRealocacaoOpen();
  };

  const deselectRealocacao = () => {
    setEventoRealocacaoSelecionado(null);
    onRealocacaoClose();
  };

  const abrirErro = (erro: Erro) => {
    setErroSelecionado(erro);
    onErroOpen();
  };

  // const [grafo, setGrafo] = useState(construirGrafoAPartirDeEventos([], false, { selectAlocacaoInterna, abrirMenuAlocacao, abrirErro }))
  const [eventoSelecionado, setEventoSelecionado] = useState(
    eventos.length - 1,
  );

  // const tabela = useMemo(() => construirTabelaAPartirDeEventos(eventos.slice(0, eventoSelecionado + 1)), [operacao.eventos, eventoSelecionado])

  // const flowMethods = useRef<FluxoNegociacaoMethods>()

  const elementsRef = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    setEventoAlocacaoSelecionado(null);
    onAlocacoesClose();
    const qtdEventos = operacao.eventos.length;
    if (eventoSelecionado > qtdEventos - 1) {
      setEventoSelecionado(qtdEventos - 1);
    } else if (qtdEventos - 2 === eventoSelecionado) {
      setEventoSelecionado(qtdEventos - 1);
    }
  }, [operacao.eventos.length]);

  useEffect(() => {
    elementsRef?.current[eventoSelecionado]?.scrollIntoView({
      block: "nearest",
    });
    // const dominioSelecionado = operacao.eventos.slice(0, eventoSelecionado + 1) ?? []
    // setGrafo(construirGrafoAPartirDeEventos(dominioSelecionado, dominioSelecionado.length !== operacao.eventos.length, { selectAlocacaoInterna, abrirMenuAlocacao, abrirErro }))
  }, [eventoSelecionado]);

  // useEffect(() => {
  //     if (!flowMethods.current) return;
  //     const { setNodes, setEdges, foco } = flowMethods.current
  //     setNodes(grafo.nodes)
  //     setEdges(grafo.edges)
  //     if (grafo.foco.length) {
  //         foco(...grafo.foco)
  //     }
  // }, [grafo])

  // useEffect(() => {
  //     if (isOpen) requestAnimationFrame(() => setGrafo(construirGrafoAPartirDeEventos(eventos, false, { selectAlocacaoInterna, abrirMenuAlocacao, abrirErro })))
  // }, [isOpen])

  return (
    <ConfirmModal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalhes da operação"
      size="full"
      overflow="auto"
      hideCancelButton={true}
      confirmContent="Voltar para listagem de operações"
    >
      <VStack flex={1} justifyContent="stretch">
        <HStack w="100%" flex={1} alignItems="stretch">
          <VStack minW="240px" alignItems="stretch" gap={0}>
            <VStack flex={1} gap={0} alignItems="stretch">
              <HStack h="30px" alignItems="flex-end" p={0}>
                <Box
                  h="14px"
                  w="12px"
                  borderTopLeftRadius="4px"
                  borderTop="1px solid"
                  borderLeft="1px solid"
                  borderColor="cinza.main"
                />
                <HStack>
                  <Text fontSize="xl" fontWeight="bold">
                    {operacao.codigo_ativo ?? "---"}
                  </Text>
                  {operacao.cadastro_ativo && (
                    <Text
                      fontSize="xs"
                      border="2px solid"
                      borderRadius="4px"
                      fontWeight={900}
                      color={
                        operacao.vanguarda_compra ? "azul_3.main" : "rosa.main"
                      }
                      borderColor={
                        operacao.vanguarda_compra ? "azul_3.main" : "rosa.main"
                      }
                      p="1px 4px 2px 4px"
                      lineHeight={1.1}
                    >
                      {operacao.vanguarda_compra ? "COMPRA" : "VENDA"}
                    </Text>
                  )}
                </HStack>
                <Box
                  h="14px"
                  flex={1}
                  borderTopRightRadius="4px"
                  borderTop="1px solid"
                  borderRight="1px solid"
                  borderColor="cinza.main"
                />
              </HStack>
              <VStack
                p="6px"
                flex={1}
                alignItems="stretch"
                gap={0}
                fontSize="sm"
                border="1px solid"
                borderColor="cinza.main"
                borderTop="none"
                borderBottomLeftRadius="4px"
                borderBottomRightRadius="4px"
              >
                {operacao.cadastro_ativo ? (
                  <>
                    <HStack justifyContent="space-between">
                      <Text>Tipo:</Text>
                      <Text>{operacao.cadastro_ativo.tipo}</Text>
                    </HStack>
                    <HStack justifyContent="space-between">
                      <Text>Emissor:</Text>
                      <Text>{operacao.cadastro_ativo.emissor}</Text>
                    </HStack>
                    {/* <HStack justifyContent='space-between'>
                                        <Text>Vencimento:</Text>
                                        <Text>{operacao.cadastro_ativo.data_vencimento}</Text>
                                    </HStack> */}
                    <HStack justifyContent="space-between">
                      <Text>Índice:</Text>
                      <Text>{operacao.cadastro_ativo.indice}</Text>
                    </HStack>
                    {/* <HStack justifyContent='space-between'>
                                        <Text>Taxa:</Text>
                                        <Text>{(operacao.cadastro_ativo.taxa ?? 0) * 100}</Text>
                                    </HStack> */}
                    <HStack justifyContent="space-between">
                      <Text>Preço unitário:</Text>
                      <Text>R$ {fmtNumber(operacao.preco_unitario, 6)}</Text>
                    </HStack>
                    <HStack justifyContent="space-between">
                      <Text>Quantidade:</Text>
                      <Text>{fmtNumber(operacao.quantidade, 6)}</Text>
                    </HStack>
                    <HStack justifyContent="space-between">
                      <Text>Total negociado:</Text>
                      <Text>
                        R${" "}
                        {fmtNumber(
                          operacao.quantidade * operacao.preco_unitario,
                          6,
                        )}
                      </Text>
                    </HStack>
                  </>
                ) : (
                  <Text>Ativo não cadastrado</Text>
                )}
              </VStack>
            </VStack>
            <VStack>
              <VStack w="100%" flex={1} alignItems="stretch" gap={0}>
                <HStack h="30px" alignItems="flex-end" p={0}>
                  <Box
                    h="14px"
                    w="12px"
                    borderTopLeftRadius="4px"
                    borderTop="1px solid"
                    borderLeft="1px solid"
                    borderColor="cinza.main"
                  />
                  <Text fontSize="xl">Contraparte</Text>
                  <Box
                    h="14px"
                    flex={1}
                    borderTopRightRadius="4px"
                    borderTop="1px solid"
                    borderRight="1px solid"
                    borderColor="cinza.main"
                  />
                </HStack>
                <VStack
                  p="6px"
                  flex={1}
                  alignItems="stretch"
                  gap={0}
                  fontSize="sm"
                  border="1px solid"
                  borderColor="cinza.main"
                  borderTop="none"
                  borderBottomLeftRadius="4px"
                  borderBottomRightRadius="4px"
                >
                  <HStack justifyContent="space-between">
                    <Text>Nome:</Text>
                    <Text>{operacao.contraparte_nome}</Text>
                  </HStack>
                  <HStack justifyContent="space-between">
                    <Text>Conta trader negociada:</Text>
                    <Text>{operacao.contraparte_conta ?? "---"}</Text>
                  </HStack>
                </VStack>
              </VStack>
            </VStack>
          </VStack>
          <VStack w="100%" flex={1} alignItems="stretch" gap={0}>
            <HStack h="30px" alignItems="flex-end" p={0}>
              <Box
                h="14px"
                w="12px"
                borderTopLeftRadius="4px"
                borderTop="1px solid"
                borderLeft="1px solid"
                borderColor="cinza.main"
              />
              <Text color="cinza.500" fontSize="xl">
                Fluxo de negociação
              </Text>
              <Box
                h="14px"
                flex={1}
                borderTopRightRadius="4px"
                borderTop="1px solid"
                borderRight="1px solid"
                borderColor="cinza.main"
              />
            </HStack>
            <VStack
              flex={1}
              minH="480px"
              p="6px"
              alignItems="stretch"
              gap={0}
              fontSize="sm"
              border="1px solid"
              borderColor="cinza.main"
              borderTop="none"
              borderBottomLeftRadius="4px"
              borderBottomRightRadius="4px"
            >
              <FluxoNegociacao
                operacao={operacao}
                eventoSelecionado={eventoSelecionado}
              />
            </VStack>
          </VStack>
          <VStack w="320px" alignItems="stretch" gap={0} overflow="auto">
            <HStack h="30px" alignItems="flex-end" p={0}>
              <Box
                h="14px"
                w="12px"
                borderTopLeftRadius="4px"
                borderTop="1px solid"
                borderLeft="1px solid"
                borderColor="cinza.main"
              />
              <Text color="cinza.500" fontSize="xl">
                Histórico de eventos
              </Text>
              <Box
                h="14px"
                flex={1}
                borderTopRightRadius="4px"
                borderTop="1px solid"
                borderRight="1px solid"
                borderColor="cinza.main"
              />
            </HStack>
            <VStack
              flex={1}
              p={0}
              fontSize="sm"
              border="1px solid"
              borderColor="cinza.main"
              borderTop="none"
              borderBottomLeftRadius="4px"
              borderBottomRightRadius="4px"
            >
              <VStack
                flex={1}
                w="100%"
                alignItems="stretch"
                overflowY="auto"
                gap={0}
              >
                {eventos.map((e, i) => (
                  <EventoOperacaoItem
                    elementRef={(el) => (elementsRef.current[i] = el)}
                    key={i}
                    evento={e}
                    visual={
                      eventoSelecionado === i
                        ? EstadoSelecao.PRESENTE
                        : eventoSelecionado < i
                          ? EstadoSelecao.FUTURO
                          : EstadoSelecao.PASSADO
                    }
                    onClick={() => setEventoSelecionado(i)}
                  />
                ))}
              </VStack>
              <HStack w="100%" gap="2px">
                <Button
                  flex={1}
                  onClick={() => setEventoSelecionado(-1)}
                  colorScheme="azul_1"
                  size="xs"
                >
                  <IoPlaySkipBack />
                </Button>
                <Button
                  flex={2}
                  onClick={() =>
                    setEventoSelecionado(Math.max(eventoSelecionado - 1, -1))
                  }
                  colorScheme="azul_3"
                  size="xs"
                >
                  <IoPlayBack />
                </Button>
                <Button
                  flex={2}
                  onClick={() =>
                    setEventoSelecionado(
                      Math.min(eventoSelecionado + 1, eventos.length - 1),
                    )
                  }
                  colorScheme="azul_3"
                  size="xs"
                >
                  <IoPlayForward />
                </Button>
                <Button
                  flex={1}
                  onClick={() => setEventoSelecionado(eventos.length - 1)}
                  colorScheme="azul_1"
                  size="xs"
                >
                  <IoPlaySkipForward />
                </Button>
              </HStack>
            </VStack>
          </VStack>
        </HStack>
        {/* <VStack w='100%' gap={0} alignItems='stretch'>
                <HStack h='30px' alignItems='flex-end' p={0}>
                    <Box h='14px' w='12px' borderTopLeftRadius='4px' borderTop='1px solid' borderLeft='1px solid' borderColor='cinza.main' />
                    <Text fontSize='xl'>Estado das alocações</Text>
                    <Box h='14px' flex={1} borderTopRightRadius='4px' borderTop='1px solid' borderRight='1px solid' borderColor='cinza.main' />
                </HStack>
                <VStack alignItems='stretch' gap={0} fontSize='sm' border='1px solid' borderColor='cinza.main' borderTop='none' borderBottomLeftRadius='4px' borderBottomRightRadius='4px'>
                    <TabelaAlocacoes
                        alocacoes={tabela}
                        ladoVanguarda="COMPRA"
                        precoUnitarioReais={operacao.preco_unitario}
                            />
                </VStack>
            </VStack> */}
      </VStack>
      {eventoAlocacaoSelecionado && (
        <ModalInteracaoAlocacao
          habilitar_controles={eventoAlocacaoSelecionado.habilitarControles}
          resposta_backoffice={
            eventoAlocacaoSelecionado.eventoAprovacao
              ? {
                  aprovacao:
                    eventoAlocacaoSelecionado.eventoAprovacao.aprovacao,
                  data: eventoAlocacaoSelecionado.eventoAprovacao.criado_em,
                  motivo: eventoAlocacaoSelecionado.eventoAprovacao.motivo,
                  usuario: {
                    ...eventoAlocacaoSelecionado.eventoAprovacao.usuario,
                    devices: [],
                  },
                }
              : undefined
          }
          alocacao_referente={{
            id_operacao_interna:
              eventoAlocacaoSelecionado.eventoAlocacao.operacao.id,
            alocacoes:
              eventoAlocacaoSelecionado.eventoAlocacao.operacao.alocacoes.map(
                (f) => ({ ...f, registro_fundo: null }),
              ),
            usuario: eventoAlocacaoSelecionado.eventoAlocacao.operacao.usuario
              ? {
                  ...eventoAlocacaoSelecionado.eventoAlocacao.operacao.usuario,
                  devices: [],
                }
              : null,
            data: eventoAlocacaoSelecionado.eventoAlocacao.operacao.criado_em,
          }}
          isOpen={isAlocacoesOpen}
          onClose={deselectAlocacaoInterna}
        />
      )}
      {eventoRealocacaoSelecionado && (
        <ModalRealocacao
          isOpen={isRealocacaoOpen}
          onClose={deselectRealocacao}
          pos={eventoRealocacaoSelecionado.pos}
          idEvento={eventoRealocacaoSelecionado.idEvento}
          operacao={operacao}
        />
      )}
      {erroSelecionado && (
        <ModalDetalhesErro
          isOpen={isErroOpen}
          onClose={onErroClose}
          erro={erroSelecionado}
        />
      )}
    </ConfirmModal>
  );
}
