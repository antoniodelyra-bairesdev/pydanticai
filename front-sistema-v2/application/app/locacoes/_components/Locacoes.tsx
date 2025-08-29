"use client";

import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box,
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Checkbox,
  CheckboxGroup,
  Divider,
  HStack,
  Icon,
  Input,
  keyframes,
  Select,
  Tab,
  Table,
  TableContainer,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Tbody,
  Td,
  Text,
  Th,
  Tooltip,
  Tr,
  useDisclosure,
  VStack,
} from "@chakra-ui/react";
import HResize from "@/app/_components/misc/HResize";
import {
  IoBusinessOutline,
  IoCalendarOutline,
  IoCheckmark,
  IoCheckmarkCircle,
  IoCloseCircle,
  IoCogOutline,
  IoDocumentOutline,
  IoDownloadOutline,
  IoEllipseOutline,
  IoFlag,
  IoFlagOutline,
  IoHelpCircleOutline,
  IoPersonCircleOutline,
  IoSyncCircleOutline,
  IoTimeOutline,
  IoTrashBin,
} from "react-icons/io5";
import Image, { StaticImageData } from "next/image";

import { useHTTP, useWebSockets } from "@/lib/hooks";
import { downloadBlob } from "@/lib/util/http";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { WSMessage, WSMessageType } from "@/lib/types/api/iv/websockets";
import { Inquilino } from "@/lib/types/api/iv/cobranca";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { mes } from "@/lib/util/dates";

import ImgAzul from "@/public/logoazul.png";
import ImgEbazar from "@/public/mercado_livre_comprar.jpg";
import ImgPower from "@/public/powersource.jpg";
import ImgTam from "@/public/tam.png";
import ImgTex from "@/public/tex_courrier_sa_logo.jpg";
import ImgTfk from "@/public/anjun.png";
import { fmtDate, fmtDatetime } from "@/lib/util/string";
import Passos, { PassoEstado } from "@/app/_components/carregamento/Passos";
import Hint from "@/app/_components/texto/Hint";
import {
  DadosExecucao,
  Execucao,
  PassoExecucao,
} from "@/lib/types/api/iv/financeiro";
import Arquivo from "@/app/_components/misc/Arquivo";

const frames = keyframes`
    0% { transform: rotate(0turn); }
    100% { transform: rotate(1turn); }
`;

const animation = `${frames} 1s linear infinite`;

enum StatusBoletoEnum {
  AGUARDANDO_PAGAMENTO,
  PAGO,
  ATRASADO,
  PAGO_COM_ATRASO,
}

const cnpj_imagens: Record<string, StaticImageData> = {
  "09296295000160": ImgAzul,
  "03007331000141": ImgEbazar,
  "26474286000130": ImgPower,
  "02012862000160": ImgTam,
  "73939449000193": ImgTex,
  "49526505000183": ImgTfk,
};
const fundo = { id: 362 };

export default function Locacoes() {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const [inquilinos, setInquilinos] = useState([] as Inquilino[]);
  const [execucoes, setExecucoes] = useState<Execucao[]>([]);

  const cobrancas = useMemo<Execucao[]>(
    () =>
      execucoes.filter((e) => e.tipo_execucao.nome === "Criação de cobrança"),
    [execucoes],
  );
  const capturas = useMemo<Execucao[]>(
    () => execucoes.filter((e) => e.tipo_execucao.nome === "Coleta de boletos"),
    [execucoes],
  );
  // const atualizacoes = useMemo<Execucao[]>(
  //   () => execucoes.filter(e => e.tipo_execucao.nome === 'Acompanhamento'),
  //   [execucoes]
  // )

  const httpClient = useHTTP({ withCredentials: true });

  const botaoDownloadRemessa = useCallback(
    (boleto: DadosExecucao, inquilino: Inquilino) => {
      const nome = `Remessa_${boleto.vencimento}_${inquilino.razao_social.split(" ").join("_")}_${boleto.execucao_daycoval_id}.txt`;
      return (
        <Arquivo
          arquivo={{
            id: "",
            extensao: "txt",
            nome,
          }}
          permitirDownload={async () => {
            if (!boleto.conteudo_arquivo_remessa) return;
            const blob = new Blob([boleto.conteudo_arquivo_remessa], {
              type: "text/plain",
            });
            downloadBlob(blob, nome);
          }}
          rotulo="Arquivo remessa"
        />
      );
    },
    [],
  );

  const botaoDownloadParcial = useCallback(
    (boleto: DadosExecucao, inquilino: Inquilino) => {
      return (
        <Arquivo
          arquivo={{
            id: boleto.arquivo_id_boleto_parcial_pdf ?? "",
            nome: `Boleto_Parcial_${boleto.vencimento}_${inquilino.razao_social.split(" ").join("_")}_${boleto.execucao_daycoval_id}.pdf`,
            extensao: "pdf",
          }}
          permitirDownload
          rotulo="Boleto parcial"
        />
      );
    },
    [],
  );

  const botaoDownloadRetorno = useCallback(
    (boleto: DadosExecucao, inquilino: Inquilino) => {
      const nome = `Retorno_${boleto.vencimento}_${inquilino.razao_social.split(" ").join("_")}_${boleto.execucao_daycoval_id}.txt`;
      return (
        <Arquivo
          arquivo={{
            id: "",
            extensao: "txt",
            nome,
          }}
          permitirDownload={async () => {
            if (!boleto.conteudo_arquivo_retorno) return;
            const blob = new Blob([boleto.conteudo_arquivo_retorno], {
              type: "text/plain",
            });
            downloadBlob(blob, nome);
          }}
          rotulo="Arquivo retorno"
        />
      );
    },
    [],
  );

  const botaoDownloadCompleto = useCallback(
    (boleto: DadosExecucao, inquilino: Inquilino) => {
      return (
        <Arquivo
          arquivo={{
            id: boleto.arquivo_id_boleto_completo_pdf ?? "",
            nome: `Boleto_Completo_${boleto.vencimento}_${inquilino.razao_social.split(" ").join("_")}_${boleto.execucao_daycoval_id}.pdf`,
            extensao: "pdf",
          }}
          permitirDownload
          rotulo="Boleto completo"
        />
      );
    },
    [],
  );

  const listarTudo = useCallback(() => {
    httpClient.fetch("v1/cobranca/boletos/ws", { method: "GET" });
  }, []);

  const [boletos, setBoletos] = useState([] as DadosExecucao[]);

  const onListarBoletos = useCallback((boletos: DadosExecucao[]) => {
    setBoletos(boletos);
  }, []);

  const onListarExecucoes = useCallback(
    (execucoes: Execucao[]) =>
      setExecucoes(
        execucoes.sort((e1, e2) => e2.inicio.localeCompare(e1.inicio)),
      ),
    [],
  );

  const onAtualizacaoExecucao = useCallback((execucao: Execucao) => {
    setExecucoes((prev) => {
      const execPos = prev.findIndex((exec) => exec.id === execucao.id);
      if (execPos !== -1) {
        prev[execPos] = execucao;
      } else {
        prev.unshift(execucao);
      }
      return [...prev];
    });
  }, []);

  const onAtualizacaoPasso = useCallback((passo: PassoExecucao) => {
    setExecucoes((prev) => {
      const execucao = prev.find(
        (exec) => exec.id === passo.execucao_daycoval_id,
      );
      if (!execucao) return [...prev];
      const passoPos = execucao.passos.findIndex((p) => p.id === passo.id);
      if (passoPos !== -1) {
        execucao.passos[passoPos] = { ...passo };
      } else {
        execucao.passos.push(passo);
      }
      return [...prev];
    });
  }, []);

  const onAtualizacaoDados = useCallback((dados: DadosExecucao[]) => {
    setExecucoes((prev) => {
      const execucao = prev.find(
        (exec) => exec.id === dados[0]?.execucao_daycoval_id,
      );
      if (!execucao) return [...prev];
      for (const dado of dados) {
        const dadoPos = execucao.dados.findIndex((d) => d.id === dado.id);
        if (dadoPos !== -1) {
          execucao.dados[dadoPos] = dado;
        } else {
          execucao.dados.push(dado);
        }
      }
      return [...prev];
    });
    setBoletos((prev) => {
      const ids = new Set(prev.map((b) => b.id));
      dados.forEach((dado) => {
        if (!ids.has(dado.id)) {
          prev.push(dado);
        }
      });
      return [...prev];
    });
  }, []);

  const ws = useWebSockets();
  const onMessage = useCallback(
    (ev: MessageEvent) => {
      try {
        const msg = JSON.parse(ev.data) as WSMessage;
        const body = (msg.content as any)?.body;
        if (
          msg.type !== WSMessageType.JSON ||
          !body ||
          body.canal !== "locacoes.boletos" ||
          !("tipo" in body) ||
          typeof body.tipo !== "string"
        ) {
          return;
        }
        const tipo: string = body.tipo;

        const acoes: Record<string, Function> = {
          "boletos.todos": () => onListarBoletos(body.dados),
          "execucoes_daycoval.todas": () => onListarExecucoes(body.dados),
          "execucoes_daycoval.atualizacao": () =>
            onAtualizacaoExecucao(body.dados),
          "execucoes_daycoval.passos.atualizacao": () =>
            onAtualizacaoPasso(body.dados),
          "execucoes_daycoval.dados.atualizacao": () =>
            onAtualizacaoDados(body.dados),
        };
        acoes[tipo]?.();
      } catch (err) {
        console.log("Falha ao processar mensagem.", err);
      }
    },
    [ws.connection],
  );

  useEffect(() => {
    if (ws.connection) {
      console.log("Iniciando conexão...");
      if (ws.connection.readyState !== WebSocket.OPEN) {
        console.log("Aguardando abertura do canal de comunicação...");
        ws.connection.addEventListener("open", listarTudo);
      } else {
        console.log("Canal de comunicação já estabelecido!");
        listarTudo();
      }
      ws.connection.addEventListener("message", onMessage);
    }
    return () => {
      if (ws.connection) {
        console.log("Removendo listeners de eventos...");
        ws.connection.removeEventListener("message", onMessage);
        ws.connection.removeEventListener("open", listarTudo);
      }
    };
  }, [ws.connection]);

  useEffect(() => {
    (async () => {
      const response = await httpClient.fetch("v1/cobranca/inquilinos/362");
      if (!response.ok) return;
      setInquilinos(await response.json());
    })();
  }, []);

  const meses = useMemo(() => {
    const agora = new Date();
    const anoAgora = agora.getFullYear();
    const mesAgora = agora.getMonth() + 1;

    const proxAno = [11, 12].includes(mesAgora) ? anoAgora + 1 : anoAgora;
    let proxMes = [11, 12].includes(mesAgora)
      ? (mesAgora + 2) % 12
      : mesAgora + 2;

    const [anoInferior, mesInferior] = [2025, 6];

    const meses: string[] = [];

    end: for (let ano = proxAno; ano >= anoInferior; ano--) {
      for (let mes = proxMes; mes >= 1; mes--) {
        meses.push(`${ano}-${String(mes).padStart(2, "0")}`);
        if (ano === anoInferior && mes === mesInferior) {
          break end;
        }
      }
      proxMes = 12;
    }

    return meses;
  }, [inquilinos]);

  const [inquilinosSelecionados, setInquilinosSelecionados] = useState<
    Inquilino[]
  >([]);
  const [yyyymm, setYYYYMM] = useState("");

  const [valorInputs, setValorInputs] = useState({} as Record<number, string>);
  const [vctoInputs, setVctoInputs] = useState({} as Record<number, string>);
  const [jurosInputs, setJurosInputs] = useState({} as Record<number, string>);
  const [multaInputs, setMultaInputs] = useState({} as Record<number, string>);

  useEffect(() => {
    setValorInputs((prev) => ({ ...prev }));
    setVctoInputs((prev) => ({
      ...prev,
      ...inquilinos.reduce(
        (map, i) => ({ ...map, [i.id]: i.contrato.dia_vencimento + "" }),
        {} as Record<number, string>,
      ),
    }));
    setJurosInputs((prev) => ({
      ...prev,
      ...inquilinos.reduce(
        (map, i) => ({
          ...map,
          [i.id]: i.contrato.percentual_juros_mora_ao_mes + "",
        }),
        {} as Record<number, string>,
      ),
    }));
    setMultaInputs((prev) => ({
      ...prev,
      ...inquilinos.reduce(
        (map, i) => ({
          ...map,
          [i.id]:
            i.contrato.faixas_cobranca_multa_mora.sort(
              (f1, f2) =>
                f1.dias_a_partir_vencimento - f2.dias_a_partir_vencimento,
            )[0].dias_a_partir_vencimento + "",
        }),
        {} as Record<number, string>,
      ),
    }));
  }, [inquilinos]);

  const abrirModalGerarArquivos = useCallback(
    (inquilinos: Inquilino[], yyyymm: string) => {
      setInquilinosSelecionados(inquilinos);
      setYYYYMM(yyyymm);
      setInquilinos((inq) => [...inq]);
      onOpen();
    },
    [],
  );

  useEffect(
    () =>
      console.log(
        Object.values(valorInputs),
        Object.values(valorInputs).every((v) => v.trim()),
      ),
    [valorInputs],
  );

  const iniciarExecucao = (
    yyyymm: string,
    selecionados: Inquilino[],
    inputs: {
      valores: Record<number, string>;
      vencimento: Record<number, string>;
      juros: Record<number, string>;
      multa: Record<number, string>;
    },
  ) => {
    const body = selecionados.map((i) => ({
      contrato_id: i.contrato.id,
      valor: Number(inputs.valores[i.id]),
      vencimento: `${yyyymm}-${inputs.vencimento[i.id].padStart(2, "0")}`,
      percentual_juros_mora_ao_mes: Number(inputs.juros[i.id]),
      percentual_sobre_valor_multa_mora:
        i.contrato.faixas_cobranca_multa_mora.find(
          (f) => f.dias_a_partir_vencimento === Number(inputs.multa[i.id]),
        )?.percentual_sobre_valor,
    }));
    httpClient.fetch(
      `v1/cobranca/execucoes/daycoval/criacao-cobranca?tipo_execucao_id=1`,
      {
        method: "POST",
        body: JSON.stringify(body),
        hideToast: { success: true },
      },
    );
  };

  const iniciarColeta = () => {
    httpClient.fetch(
      `v1/cobranca/execucoes/daycoval/criacao-cobranca?tipo_execucao_id=2`,
      {
        method: "POST",
        body: "[]",
        hideToast: { success: true },
      },
    );
  };

  const {
    onClose: onExecClose,
    isOpen: isExecOpen,
    onOpen: onExecOpen,
  } = useDisclosure();

  return (
    <HResize
      startingProportion={0.575}
      gap={0}
      h="calc(100vh - 56px)"
      alignItems="stretch"
      leftElement={
        <VStack flex={1} h="100%" alignItems="stretch" bgColor="cinza.main">
          <Text fontSize="2xl" p="8px 12px 0px 12px" bgColor="white" pb="4px">
            Informações dos contratos
          </Text>
          <HStack
            borderRadius="12px"
            p="12px 24px"
            flex={1}
            alignItems="stretch"
            alignContent="flex-start"
            flexWrap="wrap"
            overflowY="auto"
          >
            {inquilinos.map((inq) => (
              <Card
                key={inq.cnpj}
                w="256px"
                _hover={{ bgColor: "cinza.100" }}
                transition="background-color .25s"
              >
                <CardBody p={0} overflow="hidden" borderRadius="6px" h="100%">
                  <VStack
                    alignItems="stretch"
                    justifyContent="space-between"
                    h="100%"
                  >
                    <VStack alignItems="stretch" flex={1}>
                      <HStack
                        alignItems="stretch"
                        justifyContent="center"
                        bgColor="azul_1.50"
                        borderBottom="1px solid"
                        borderBottomColor="cinza.main"
                      >
                        {inq.cnpj in cnpj_imagens ? (
                          <Image
                            alt="Imagem"
                            src={cnpj_imagens[inq.cnpj]}
                            style={{
                              width: "100%",
                              height: 92,
                              objectFit: "cover",
                            }}
                          />
                        ) : (
                          <Icon
                            as={IoBusinessOutline}
                            color="white"
                            w="84px"
                            h="84px"
                            m="4px"
                          />
                        )}
                      </HStack>
                      <VStack alignItems="stretch" p="12px" flex={1}>
                        <Tooltip
                          label={inq.razao_social}
                          hasArrow
                          borderRadius="4px"
                        >
                          <Text
                            fontWeight="bold"
                            overflow="hidden"
                            whiteSpace="nowrap"
                            textOverflow="ellipsis"
                          >
                            {inq.razao_social}
                          </Text>
                        </Tooltip>
                        <HStack justifyContent="space-between">
                          <Text fontSize="sm" lineHeight={1.25}>
                            Juros Mora ao mês:
                          </Text>
                          <Text
                            color="cinza.500"
                            fontSize="xs"
                            lineHeight={1.25}
                          >
                            {(
                              inq.contrato.percentual_juros_mora_ao_mes ?? 0
                            ).toLocaleString("pt-BR", {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })}
                            %
                          </Text>
                        </HStack>
                        <HStack justifyContent="space-between">
                          <Text fontSize="sm">Vencimento dos boletos</Text>
                          <Text
                            color="cinza.500"
                            fontSize="xs"
                            lineHeight={1.25}
                          >
                            Dia {inq.contrato.dia_vencimento}
                          </Text>
                        </HStack>
                        <Text fontSize="sm" lineHeight={1.25}>
                          Faixas de Multa Mora:
                        </Text>
                        <VStack gap={0} alignItems="stretch">
                          {inq.contrato.faixas_cobranca_multa_mora
                            .sort(
                              (f1, f2) =>
                                f1.dias_a_partir_vencimento -
                                f2.dias_a_partir_vencimento,
                            )
                            .map((f, i) => (
                              <Text
                                key={i}
                                color="cinza.500"
                                fontSize="xs"
                                lineHeight={1.25}
                              >
                                - A partir de {f.dias_a_partir_vencimento}{" "}
                                dia(s):{" "}
                                {f.percentual_sobre_valor.toLocaleString(
                                  "pt-BR",
                                  {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2,
                                  },
                                )}
                                %
                              </Text>
                            ))}
                        </VStack>
                      </VStack>
                      {/* <HStack gap="4px" p="12px">
                        <Icon as={IoCheckmark} color="verde.main" />
                        <Text color="verde.900" fontSize="xs">
                          Boletos em dia
                        </Text>
                      </HStack> */}
                    </VStack>
                  </VStack>
                </CardBody>
                {/* <CardFooter flexDirection="row-reverse" p="12px">
                  <Button colorScheme="verde" size="xs">
                    Detalhes
                  </Button>
                </CardFooter> */}
              </Card>
            ))}
          </HStack>
        </VStack>
      }
      rightElement={
        <VStack alignItems="stretch" bgColor="cinza.main" h="100%" gap={0}>
          <HStack
            position="sticky"
            top={0}
            bgColor="white"
            justifyContent="space-between"
            p="8px 12px 4px 12px"
          >
            <Text fontSize="2xl">Boletos</Text>
          </HStack>
          <Accordion flex={1} bgColor="white" allowMultiple defaultIndex={[]}>
            {meses.map((yyyymm) => {
              const [y, m] = yyyymm.split("-");
              return (
                <AccordionItem
                  m="8px"
                  key={yyyymm}
                  border="none"
                  boxShadow="0 0 6px lightgray"
                >
                  {({ isExpanded }) => (
                    <>
                      <AccordionButton p="4px">
                        <HStack
                          justifyContent="space-between"
                          w="100%"
                          flexWrap="wrap"
                        >
                          <HStack>
                            <AccordionIcon />
                            <Text>
                              {mes(Number(m))} - {y}
                            </Text>
                          </HStack>
                          {isExpanded && (
                            <HStack
                              onClick={(ev) => {
                                ev.stopPropagation();
                              }}
                              flexWrap="wrap"
                            >
                              <Button
                                h="20px"
                                colorScheme="azul_1"
                                size="xs"
                                leftIcon={<Icon as={IoCogOutline} />}
                                onClick={() => {
                                  abrirModalGerarArquivos(inquilinos, yyyymm);
                                }}
                              >
                                Gerar arquivos
                              </Button>
                            </HStack>
                          )}
                        </HStack>
                      </AccordionButton>
                      <AccordionPanel p={0}>
                        <TableContainer w="100%">
                          <Table>
                            <Tbody>
                              {inquilinos.map((i) => {
                                const temBoletos =
                                  boletos.filter(
                                    (b) =>
                                      b.contrato_id === i.contrato.id &&
                                      b.vencimento
                                        .split("-")
                                        .slice(0, 2)
                                        .join("-") === yyyymm,
                                  ).length > 0;
                                return (
                                  <React.Fragment key={i.cnpj}>
                                    <Tr
                                      transition="background-color 0.125s"
                                      _hover={{ bgColor: "cinza.main" }}
                                      bgColor="azul_1.50"
                                    >
                                      <Td
                                        colSpan={6}
                                        p="4px 16px 4px 16px"
                                        bgColor={
                                          temBoletos
                                            ? "cinza.200"
                                            : "laranja.50"
                                        }
                                      >
                                        <HStack
                                          w="100%"
                                          justifyContent="space-between"
                                        >
                                          <Text fontSize="sm" fontWeight={600}>
                                            {i.razao_social}
                                          </Text>
                                          <Button
                                            leftIcon={
                                              <Icon as={IoCogOutline} />
                                            }
                                            h="20px"
                                            size="xs"
                                            colorScheme="azul_1"
                                            onClick={() => {
                                              abrirModalGerarArquivos(
                                                [i],
                                                yyyymm,
                                              );
                                            }}
                                          >
                                            Gerar
                                          </Button>
                                        </HStack>
                                      </Td>
                                    </Tr>
                                    {temBoletos && (
                                      <Tr bgColor="white">
                                        <Th p="2px 6px" fontSize="11px">
                                          Vencimento
                                        </Th>
                                        <Th p="2px" fontSize="11px">
                                          Arq. Remessa
                                        </Th>
                                        <Th p="2px" fontSize="11px">
                                          Boleto parcial
                                        </Th>
                                        <Th p="2px" fontSize="11px">
                                          Arq. Retorno
                                        </Th>
                                        <Th p="2px" fontSize="11px">
                                          Boleto final
                                        </Th>
                                        {/* <Th p="2px" fontSize="11px">
                                          Gerado em
                                        </Th> */}
                                      </Tr>
                                    )}
                                    {boletos
                                      .filter(
                                        (b) =>
                                          b.contrato_id === i.contrato.id &&
                                          b.vencimento
                                            .split("-")
                                            .slice(0, 2)
                                            .join("-") === yyyymm,
                                      )
                                      .map((boleto) => (
                                        <Tr
                                          key={boleto.id}
                                          bgColor="cinza.50"
                                          transition="background-color 0.125s"
                                          _hover={{ bgColor: "cinza.100" }}
                                        >
                                          <Td fontSize="xs" p="0">
                                            <HStack gap={0} p="4px">
                                              <Icon
                                                as={IoCalendarOutline}
                                                color="verde.main"
                                              />
                                              <Text p="4px">
                                                {fmtDate(boleto.vencimento)}
                                              </Text>
                                            </HStack>
                                          </Td>
                                          <Td p={0}>
                                            <Box maxW="144px">
                                              {boleto.conteudo_arquivo_remessa &&
                                                botaoDownloadRemessa(boleto, i)}
                                            </Box>
                                          </Td>
                                          <Td p={0}>
                                            <Box maxW="144px">
                                              {boleto.arquivo_id_boleto_parcial_pdf &&
                                                botaoDownloadParcial(boleto, i)}
                                            </Box>
                                          </Td>
                                          <Td p={0}>
                                            <Box maxW="144px">
                                              {boleto.conteudo_arquivo_retorno &&
                                                botaoDownloadRetorno(boleto, i)}
                                            </Box>
                                          </Td>
                                          <Td p={0}>
                                            <Box maxW="144px">
                                              {boleto.arquivo_id_boleto_completo_pdf &&
                                                botaoDownloadCompleto(
                                                  boleto,
                                                  i,
                                                )}
                                            </Box>
                                          </Td>
                                        </Tr>
                                      ))}
                                    {!temBoletos && (
                                      <Tr bgColor="laranja.50" opacity={0.325}>
                                        <Td h="24px" colSpan={5}>
                                          <HStack
                                            w="100%"
                                            h="100%"
                                            justifyContent="center"
                                          >
                                            <Text fontSize="xs">
                                              Nenhum arquivo encontrado
                                            </Text>
                                          </HStack>
                                        </Td>
                                      </Tr>
                                    )}
                                  </React.Fragment>
                                );
                              })}
                            </Tbody>
                          </Table>
                        </TableContainer>
                      </AccordionPanel>
                    </>
                  )}
                </AccordionItem>
              );
            })}
          </Accordion>
          <ConfirmModal
            isOpen={isOpen}
            onClose={onClose}
            size="6xl"
            hideConfirmButton
            cancelContent="Fechar"
          >
            <Tabs w="100%" size="sm" colorScheme="verde">
              <TabList>
                <Tab>Criação de cobrança</Tab>
                <Tab>Coleta de boletos</Tab>
                {/* <Tab>Acompanhamento</Tab> */}
              </TabList>
              <TabPanels>
                <TabPanel p={0}>
                  <HStack
                    w="100%"
                    h="70vh"
                    alignItems="stretch"
                    gap={0}
                    overflow="hidden"
                  >
                    <VStack
                      alignItems="stretch"
                      flex={1}
                      pl="12px"
                      overflow="auto"
                    >
                      <VStack
                        alignItems="stretch"
                        position="sticky"
                        top={0}
                        zIndex={4}
                        bgColor="white"
                      >
                        <HStack justifyContent="space-between">
                          <Text pt="8px" fontWeight="bold">
                            Execuções
                          </Text>
                          <Button
                            mt="8px"
                            size="xs"
                            colorScheme="verde"
                            onClick={onExecOpen}
                          >
                            Iniciar nova execução
                          </Button>
                        </HStack>
                        <Divider />
                      </VStack>
                      <Accordion allowMultiple allowToggle h="100%">
                        {cobrancas.length ? (
                          cobrancas.map((execucao) => {
                            const estado = (obj?: {
                              inicio: string;
                              erro: string | null;
                              fim: string | null;
                            }) => {
                              if (!obj) return PassoEstado.AGUARDANDO;
                              if (obj.erro) return PassoEstado.ERRO;
                              if (obj.fim) return PassoEstado.CONCLUIDO;
                              if (obj.inicio) return PassoEstado.EM_ANDAMENTO;
                              return PassoEstado.DESCONHECIDO;
                            };
                            const estadoPasso = (nomePasso: string) => {
                              const passo = execucao.passos.find(
                                (p) => p.nome === nomePasso,
                              );
                              return estado(passo);
                            };
                            return (
                              <AccordionItem key={execucao.id}>
                                <AccordionButton>
                                  <HStack
                                    justifyContent="space-between"
                                    w="100%"
                                    fontSize="xs"
                                  >
                                    <HStack>
                                      <AccordionIcon />
                                      <Box
                                        w="32px"
                                        h="32px"
                                        bgColor="white"
                                        borderRadius="full"
                                        zIndex={3}
                                      >
                                        <Tooltip
                                          label={execucao.erro ?? ""}
                                          fontSize="xs"
                                          borderRadius="4px"
                                          hasArrow
                                          bgColor="rosa.main"
                                          placement="top"
                                        >
                                          <Box>
                                            <Icon
                                              w="100%"
                                              h="100%"
                                              as={
                                                {
                                                  [PassoEstado.AGUARDANDO]:
                                                    IoEllipseOutline,
                                                  [PassoEstado.EM_ANDAMENTO]:
                                                    IoSyncCircleOutline,
                                                  [PassoEstado.CONCLUIDO]:
                                                    IoCheckmarkCircle,
                                                  [PassoEstado.ERRO]:
                                                    IoCloseCircle,
                                                  [PassoEstado.DESCONHECIDO]:
                                                    IoHelpCircleOutline,
                                                }[estado(execucao)]
                                              }
                                              color={
                                                {
                                                  [PassoEstado.AGUARDANDO]:
                                                    "cinza.main",
                                                  [PassoEstado.EM_ANDAMENTO]:
                                                    "azul_4.main",
                                                  [PassoEstado.CONCLUIDO]:
                                                    "verde.main",
                                                  [PassoEstado.ERRO]:
                                                    "rosa.main",
                                                  [PassoEstado.DESCONHECIDO]:
                                                    "cinza.main",
                                                }[estado(execucao)]
                                              }
                                              animation={
                                                estado(execucao) ===
                                                PassoEstado.EM_ANDAMENTO
                                                  ? animation
                                                  : undefined
                                              }
                                            />
                                          </Box>
                                        </Tooltip>
                                      </Box>
                                      <VStack
                                        gap={0}
                                        alignItems="stretch"
                                        fontSize="11px"
                                      >
                                        <HStack h="16px">
                                          <Icon
                                            as={IoTimeOutline}
                                            color="verde.main"
                                          />
                                          <Text>
                                            {fmtDatetime(execucao.inicio)}
                                          </Text>
                                        </HStack>
                                        <HStack h="16px">
                                          <Icon
                                            as={IoFlagOutline}
                                            color="roxo.main"
                                          />
                                          <Text>
                                            {execucao.fim
                                              ? fmtDatetime(execucao.fim)
                                              : "---"}
                                          </Text>
                                        </HStack>
                                      </VStack>
                                    </HStack>
                                    <HStack h="16px">
                                      <Icon
                                        as={IoPersonCircleOutline}
                                        color="azul_3.main"
                                      />
                                      <Text>
                                        {execucao.usuario.nome ?? "---"}
                                      </Text>
                                    </HStack>
                                  </HStack>
                                </AccordionButton>
                                <AccordionPanel p={0} bgColor="cinza.100">
                                  {execucao.erro && (
                                    <Button
                                      m="16px 0 0 16px"
                                      colorScheme="rosa"
                                      size="xs"
                                      onClick={() => {
                                        httpClient.fetch(
                                          `v1/cobranca/execucoes/daycoval/criacao-cobranca?tipo_execucao_id=1`,
                                          {
                                            method: "POST",
                                            body: String(execucao.id),
                                            hideToast: { success: true },
                                          },
                                        );
                                      }}
                                    >
                                      Tentar novamente
                                    </Button>
                                  )}
                                  <Passos
                                    borderRadius="12px"
                                    p="12px"
                                    tituloProps={{ fontWeight: 600 }}
                                    passos={[
                                      {
                                        titulo: "Validação de dados",
                                        estado: estadoPasso(
                                          "locacoes.boletos.arquivos.remessa.validacao",
                                        ),
                                      },
                                      {
                                        titulo: "Criação de arquivo de remessa",
                                        estado: estadoPasso(
                                          "locacoes.boletos.arquivos.remessa.criacao",
                                        ),
                                      },
                                      {
                                        titulo:
                                          "Armazenamento e disponibilização de arquivos de remessa",
                                        estado: estadoPasso(
                                          "locacoes.boletos.arquivos.remessa.armazenamento",
                                        ),
                                        conteudo: (
                                          <VStack
                                            borderRadius="12px"
                                            border="1px solid"
                                            bgColor="cinza.50"
                                            borderColor="cinza.main"
                                            p="12px"
                                            alignItems="stretch"
                                          >
                                            {execucao.dados.map((d) => {
                                              const inquilino = inquilinos.find(
                                                (i) =>
                                                  i.contrato.id ===
                                                  d.contrato_id,
                                              );
                                              if (!inquilino)
                                                return (
                                                  <Text>
                                                    Inquilino de contrato{" "}
                                                    {d.contrato_id} não
                                                    encontrado.
                                                  </Text>
                                                );
                                              return (
                                                <HStack>
                                                  <Text fontSize="xs" flex={1}>
                                                    {inquilino.razao_social}
                                                  </Text>
                                                  {d.conteudo_arquivo_remessa &&
                                                    botaoDownloadRemessa(
                                                      d,
                                                      inquilino,
                                                    )}
                                                </HStack>
                                              );
                                            })}
                                          </VStack>
                                        ),
                                      },
                                      {
                                        titulo: "Acesso site Daycoval",
                                        estado: estadoPasso(
                                          "locacoes.boletos.arquivos.webdriver.boleto.armazenamento",
                                        ),
                                        conteudo: (
                                          <Passos
                                            borderRadius="12px"
                                            border="1px solid"
                                            bgColor="cinza.50"
                                            borderColor="cinza.main"
                                            p="12px"
                                            tituloProps={{
                                              fontSize: "xs",
                                              textAlign: "center",
                                            }}
                                            passos={[
                                              {
                                                titulo: "Acesso tela de login",
                                                estado: estadoPasso(
                                                  "locacoes.boletos.arquivos.webdriver.credenciais.id",
                                                ),
                                              },
                                              {
                                                titulo:
                                                  "Detecção de desafio de senha",
                                                estado: estadoPasso(
                                                  "locacoes.boletos.arquivos.webdriver.credenciais.leitura",
                                                ),
                                              },
                                              {
                                                titulo: "Tentativa de login",
                                                estado: estadoPasso(
                                                  "locacoes.boletos.arquivos.webdriver.credenciais.envio",
                                                ),
                                              },
                                              {
                                                titulo:
                                                  "Upload de arquivos de remessa",
                                                estado: estadoPasso(
                                                  "locacoes.boletos.arquivos.webdriver.remessa.upload",
                                                ),
                                              },
                                            ]}
                                            orientacao="H"
                                          />
                                        ),
                                      },
                                      {
                                        titulo:
                                          "Criação e armazenamento de boletos parciais",
                                        estado: estadoPasso(
                                          "locacoes.boletos.arquivos.parcial.criacao",
                                        ),
                                        conteudo: (
                                          <VStack
                                            borderRadius="12px"
                                            border="1px solid"
                                            bgColor="cinza.50"
                                            borderColor="cinza.main"
                                            p="12px"
                                            alignItems="stretch"
                                          >
                                            {execucao.dados.map((d) => {
                                              const inquilino = inquilinos.find(
                                                (i) =>
                                                  i.contrato.id ===
                                                  d.contrato_id,
                                              );
                                              if (!inquilino)
                                                return (
                                                  <Text>
                                                    Inquilino de contrato{" "}
                                                    {d.contrato_id} não
                                                    encontrado.
                                                  </Text>
                                                );
                                              return (
                                                <HStack>
                                                  <Text fontSize="xs" flex={1}>
                                                    {inquilino.razao_social}
                                                  </Text>
                                                  {d.arquivo_id_boleto_parcial_pdf &&
                                                    botaoDownloadParcial(
                                                      d,
                                                      inquilino,
                                                    )}
                                                </HStack>
                                              );
                                            })}
                                          </VStack>
                                        ),
                                      },
                                    ]}
                                    orientacao="V"
                                  />
                                </AccordionPanel>
                              </AccordionItem>
                            );
                          })
                        ) : (
                          <VStack
                            h="100%"
                            borderRadius="12px"
                            bgColor="cinza.50"
                            justifyContent="center"
                          >
                            <Text color="cinza.500">
                              Nenhuma execução no histórico
                            </Text>
                          </VStack>
                        )}
                      </Accordion>
                    </VStack>
                    <ConfirmModal
                      isOpen={isExecOpen}
                      onClose={onExecClose}
                      onConfirmAction={() => {
                        onExecClose();
                        iniciarExecucao(yyyymm, inquilinosSelecionados, {
                          valores: valorInputs,
                          juros: jurosInputs,
                          multa: multaInputs,
                          vencimento: vctoInputs,
                        });
                      }}
                      confirmEnabled={(() => {
                        const idsSelecionados = inquilinosSelecionados.map(
                          (inq) => inq.id,
                        );
                        return Boolean(
                          inquilinosSelecionados.length &&
                            Object.entries(valorInputs).length &&
                            Object.entries(valorInputs)
                              .filter(([id]) =>
                                idsSelecionados.includes(Number(id)),
                              )
                              .every(
                                ([_, v]) => v.trim() && !isNaN(Number(v)),
                              ) &&
                            Object.entries(vctoInputs)
                              .filter(([id]) =>
                                idsSelecionados.includes(Number(id)),
                              )
                              .every(
                                ([_, v]) => v.trim() && !isNaN(Number(v)),
                              ) &&
                            Object.entries(jurosInputs)
                              .filter(([id]) =>
                                idsSelecionados.includes(Number(id)),
                              )
                              .every(([_, v]) => v.trim() && !isNaN(Number(v))),
                        );
                      })()}
                      size="2xl"
                    >
                      <VStack
                        pb="8px"
                        w="100%"
                        alignItems="stretch"
                        borderColor="cinza.main"
                        pr="12px"
                        overflowY="auto"
                      >
                        <VStack
                          alignItems="stretch"
                          position="sticky"
                          top={0}
                          zIndex={1}
                          bgColor="white"
                        >
                          <HStack justifyContent="space-between" pt="8px">
                            <Text fontWeight="bold">
                              Dados para nova execução
                            </Text>
                          </HStack>
                          <Divider />
                        </VStack>
                        <CheckboxGroup
                          colorScheme="verde"
                          value={inquilinosSelecionados.map((i) => i.id)}
                          onChange={(state) => {
                            console.log(state);
                            setInquilinosSelecionados(
                              inquilinos.filter((i) =>
                                state
                                  .map((s) => String(s))
                                  .includes(String(i.id)),
                              ),
                            );
                          }}
                        >
                          {inquilinos.map((inq) => {
                            const disabled = !inquilinosSelecionados
                              .map((i) => i.id)
                              .includes(inq.id);
                            return (
                              <Card key={inq.id} overflow="hidden" minH="84px">
                                <CardHeader p={0}>
                                  <HStack p="4px" w="100%" bgColor="azul_1.50">
                                    <Checkbox bgColor="white" value={inq.id} />
                                    <Text
                                      fontWeight="bold"
                                      fontSize="sm"
                                      overflow="hidden"
                                      textOverflow="ellipsis"
                                      whiteSpace="nowrap"
                                      color={disabled ? "cinza.500" : "black"}
                                    >
                                      {inq.razao_social}
                                    </Text>
                                  </HStack>
                                  <Divider />
                                </CardHeader>
                                <CardBody p="4px 8px 8px 8px">
                                  <VStack alignItems="stretch">
                                    <HStack>
                                      <VStack
                                        gap={0}
                                        alignItems="stretch"
                                        flex={2}
                                      >
                                        <Hint>Valor (R$)</Hint>
                                        <Input
                                          size="xs"
                                          isDisabled={disabled}
                                          value={valorInputs[inq.id]}
                                          onChange={(ev) =>
                                            setValorInputs({
                                              ...valorInputs,
                                              [inq.id]: ev.target.value,
                                            })
                                          }
                                          isInvalid={
                                            !disabled &&
                                            (!(inq.id in valorInputs) ||
                                              !valorInputs[inq.id].trim() ||
                                              isNaN(
                                                Number(valorInputs[inq.id]),
                                              ))
                                          }
                                        />
                                      </VStack>
                                      <VStack
                                        gap={0}
                                        alignItems="stretch"
                                        flex={1}
                                      >
                                        <Hint>Dia Vcto.</Hint>
                                        <Input
                                          size="xs"
                                          isDisabled={disabled}
                                          value={vctoInputs[inq.id]}
                                          onChange={(ev) =>
                                            setVctoInputs({
                                              ...vctoInputs,
                                              [inq.id]: ev.target.value,
                                            })
                                          }
                                          isInvalid={
                                            !disabled &&
                                            (!(inq.id in vctoInputs) ||
                                              !vctoInputs[inq.id].trim() ||
                                              isNaN(Number(vctoInputs[inq.id])))
                                          }
                                        />
                                      </VStack>
                                      <VStack
                                        gap={0}
                                        alignItems="stretch"
                                        flex={2}
                                      >
                                        <Hint>Juros a.m. (%)</Hint>
                                        <Input
                                          size="xs"
                                          isDisabled={disabled}
                                          value={jurosInputs[inq.id]}
                                          onChange={(ev) =>
                                            setJurosInputs({
                                              ...jurosInputs,
                                              [inq.id]: ev.target.value,
                                            })
                                          }
                                          isInvalid={
                                            !disabled &&
                                            (!(inq.id in jurosInputs) ||
                                              !jurosInputs[inq.id].trim() ||
                                              isNaN(
                                                Number(jurosInputs[inq.id]),
                                              ))
                                          }
                                        />
                                      </VStack>
                                      <VStack
                                        gap={0}
                                        alignItems="stretch"
                                        flex={3}
                                      >
                                        <Hint>Faixa de multa (%)</Hint>
                                        <Select
                                          size="xs"
                                          isDisabled={disabled}
                                          value={multaInputs[inq.id]}
                                          onChange={(ev) =>
                                            setMultaInputs({
                                              ...multaInputs,
                                              [inq.id]: ev.target.value,
                                            })
                                          }
                                          isInvalid={
                                            !disabled &&
                                            (!(inq.id in multaInputs) ||
                                              !multaInputs[inq.id].trim() ||
                                              isNaN(
                                                Number(multaInputs[inq.id]),
                                              ))
                                          }
                                        >
                                          {inq.contrato.faixas_cobranca_multa_mora
                                            .sort(
                                              (f1, f2) =>
                                                f1.dias_a_partir_vencimento -
                                                f2.dias_a_partir_vencimento,
                                            )
                                            .map((f) => (
                                              <option
                                                value={
                                                  f.dias_a_partir_vencimento
                                                }
                                              >
                                                {f.dias_a_partir_vencimento}{" "}
                                                dia(s) atraso -{" "}
                                                {f.percentual_sobre_valor}%
                                              </option>
                                            ))}
                                        </Select>
                                      </VStack>
                                    </HStack>
                                  </VStack>
                                </CardBody>
                              </Card>
                            );
                          })}
                        </CheckboxGroup>
                      </VStack>
                    </ConfirmModal>
                  </HStack>
                </TabPanel>
                <TabPanel p={0}>
                  <VStack alignItems="stretch">
                    <HStack pt="8px" justifyContent="space-between">
                      <Text fontWeight="bold">Execuções</Text>
                      <Button
                        size="xs"
                        colorScheme="verde"
                        onClick={iniciarColeta}
                      >
                        Iniciar nova coleta
                      </Button>
                    </HStack>
                    <Divider />
                    <Accordion allowMultiple allowToggle h="100%">
                      {capturas.length ? (
                        capturas.map((execucao) => {
                          const estado = (obj?: {
                            inicio: string;
                            erro: string | null;
                            fim: string | null;
                          }) => {
                            if (!obj) return PassoEstado.AGUARDANDO;
                            if (obj.erro) return PassoEstado.ERRO;
                            if (obj.fim) return PassoEstado.CONCLUIDO;
                            if (obj.inicio) return PassoEstado.EM_ANDAMENTO;
                            return PassoEstado.DESCONHECIDO;
                          };
                          const estadoPasso = (nomePasso: string) => {
                            const passo = execucao.passos.find(
                              (p) => p.nome === nomePasso,
                            );
                            return estado(passo);
                          };
                          return (
                            <AccordionItem key={execucao.id}>
                              <AccordionButton>
                                <HStack
                                  justifyContent="space-between"
                                  w="100%"
                                  fontSize="xs"
                                >
                                  <HStack>
                                    <AccordionIcon />
                                    <Box
                                      w="32px"
                                      h="32px"
                                      bgColor="white"
                                      borderRadius="full"
                                      zIndex={3}
                                    >
                                      <Tooltip
                                        label={execucao.erro ?? ""}
                                        fontSize="xs"
                                        borderRadius="4px"
                                        hasArrow
                                        bgColor="rosa.main"
                                        placement="top"
                                      >
                                        <Box>
                                          <Icon
                                            w="100%"
                                            h="100%"
                                            as={
                                              {
                                                [PassoEstado.AGUARDANDO]:
                                                  IoEllipseOutline,
                                                [PassoEstado.EM_ANDAMENTO]:
                                                  IoSyncCircleOutline,
                                                [PassoEstado.CONCLUIDO]:
                                                  IoCheckmarkCircle,
                                                [PassoEstado.ERRO]:
                                                  IoCloseCircle,
                                                [PassoEstado.DESCONHECIDO]:
                                                  IoHelpCircleOutline,
                                              }[estado(execucao)]
                                            }
                                            color={
                                              {
                                                [PassoEstado.AGUARDANDO]:
                                                  "cinza.main",
                                                [PassoEstado.EM_ANDAMENTO]:
                                                  "azul_4.main",
                                                [PassoEstado.CONCLUIDO]:
                                                  "verde.main",
                                                [PassoEstado.ERRO]: "rosa.main",
                                                [PassoEstado.DESCONHECIDO]:
                                                  "cinza.main",
                                              }[estado(execucao)]
                                            }
                                            animation={
                                              estado(execucao) ===
                                              PassoEstado.EM_ANDAMENTO
                                                ? animation
                                                : undefined
                                            }
                                          />
                                        </Box>
                                      </Tooltip>
                                    </Box>
                                    <VStack
                                      gap={0}
                                      alignItems="stretch"
                                      fontSize="11px"
                                    >
                                      <HStack h="16px">
                                        <Icon
                                          as={IoTimeOutline}
                                          color="verde.main"
                                        />
                                        <Text>
                                          {fmtDatetime(execucao.inicio)}
                                        </Text>
                                      </HStack>
                                      <HStack h="16px">
                                        <Icon
                                          as={IoFlagOutline}
                                          color="roxo.main"
                                        />
                                        <Text>
                                          {execucao.fim
                                            ? fmtDatetime(execucao.fim)
                                            : "---"}
                                        </Text>
                                      </HStack>
                                    </VStack>
                                  </HStack>
                                  <HStack h="16px">
                                    <Icon
                                      as={IoPersonCircleOutline}
                                      color="azul_3.main"
                                    />
                                    <Text>
                                      {execucao.usuario.nome ?? "---"}
                                    </Text>
                                  </HStack>
                                </HStack>
                              </AccordionButton>
                              <AccordionPanel p={0} bgColor="cinza.100">
                                {execucao.erro && (
                                  <Button
                                    m="16px 0 0 16px"
                                    colorScheme="rosa"
                                    size="xs"
                                    onClick={() => {
                                      httpClient.fetch(
                                        `v1/cobranca/execucoes/daycoval/criacao-cobranca?tipo_execucao_id=2`,
                                        {
                                          method: "POST",
                                          body: String(execucao.id),
                                          hideToast: { success: true },
                                        },
                                      );
                                    }}
                                  >
                                    Tentar novamente
                                  </Button>
                                )}
                                <Passos
                                  borderRadius="12px"
                                  bgColor="cinza.100"
                                  p="12px"
                                  tituloProps={{ fontWeight: 600 }}
                                  passos={[
                                    {
                                      titulo: "Acesso site Daycoval",
                                      estado: estadoPasso(
                                        "locacoes.boletos.arquivos.webdriver.boleto.armazenamento",
                                      ),
                                      conteudo: (
                                        <Passos
                                          borderRadius="12px"
                                          border="1px solid"
                                          bgColor="cinza.50"
                                          borderColor="cinza.main"
                                          p="12px"
                                          tituloProps={{
                                            fontSize: "xs",
                                            textAlign: "center",
                                          }}
                                          passos={[
                                            {
                                              titulo: "Acesso tela de login",
                                              estado: estadoPasso(
                                                "locacoes.boletos.arquivos.webdriver.credenciais.id",
                                              ),
                                            },
                                            {
                                              titulo:
                                                "Detecção de desafio de senha",
                                              estado: estadoPasso(
                                                "locacoes.boletos.arquivos.webdriver.credenciais.leitura",
                                              ),
                                            },
                                            {
                                              titulo: "Tentativa de login",
                                              estado: estadoPasso(
                                                "locacoes.boletos.arquivos.webdriver.credenciais.envio",
                                              ),
                                            },
                                            {
                                              titulo:
                                                "Download de arquivos de retorno",
                                              estado: estadoPasso(
                                                "locacoes.boletos.arquivos.webdriver.retorno.download",
                                              ),
                                            },
                                          ]}
                                          orientacao="H"
                                        />
                                      ),
                                    },
                                    {
                                      titulo:
                                        "Criação e armazenamento de boletos",
                                      estado: estadoPasso(
                                        "locacoes.boletos.arquivos.completo.criacao",
                                      ),
                                    },
                                  ]}
                                  orientacao="V"
                                />
                              </AccordionPanel>
                            </AccordionItem>
                          );
                        })
                      ) : (
                        <VStack
                          h="100%"
                          borderRadius="12px"
                          bgColor="cinza.50"
                          justifyContent="center"
                        >
                          <Text color="cinza.500">
                            Nenhuma execução no histórico
                          </Text>
                        </VStack>
                      )}
                    </Accordion>
                  </VStack>
                </TabPanel>
              </TabPanels>
            </Tabs>
          </ConfirmModal>
        </VStack>
      }
    />
  );
}
