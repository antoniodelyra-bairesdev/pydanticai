"use client";

import { useAsync, useHTTP, useWebSockets } from "@/lib/hooks";
import { MSG_STATUS } from "@/lib/types/api/iv/messaging";
import {
  HStack,
  Icon,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Tag,
  Text,
  Tooltip,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useEffect, useRef, useState } from "react";
import { IoEllipse, IoReloadCircleOutline } from "react-icons/io5";
import HistoryTab from "./tabs/historico/HistoryTab";
import WorkingDayTab from "./tabs/operacoes-dia/WorkingDayTab";
import {
  CasamentoOperacaoVoice,
  CorretoraResumo,
  EventoOperacao,
  Fundo,
  OperacaoType,
  Voice,
} from "@/lib/types/api/iv/v1";
import TriagemB3 from "./tabs/triagem-b3/TriagemB3";
import {
  WSJSONMessage,
  WSMessage,
  WSMessageType,
} from "@/lib/types/api/iv/websockets";

import dynamic from "next/dynamic";

import "chartjs-adapter-dayjs-4";

const ResumoDiarioTab = dynamic(
  () => import("./tabs/resumo-diario/ResumoDiarioTab").then((m) => m.default),
  { ssr: false },
);

enum ConnectionStatus {
  UNKNOWN,
  CONNECTED,
  FAILED,
}

const colorMap: Record<number, string> = {
  [ConnectionStatus.CONNECTED]: "verde",
  [ConnectionStatus.FAILED]: "rosa",
};

export type MsgType = {
  id: number;
  status: MSG_STATUS;
  content: string;
  original?: string;
};

export type ComprasVendasProps = {
  fundos: Fundo[];
  ativos_codigos: string[];
};

export const processarNegocios = (
  operacoes: CasamentoOperacaoVoice[],
): OperacaoType[] => {
  return operacoes.map((co) => {
    const op = co.operacoes.find(
      (o) =>
        o.aprovacao_anterior_backoffice_id === null &&
        o.registro_nome_id == null,
    );
    const voice = co.voices.at(0);
    if (!op) throw Error("Falha no processamento");
    const eventos: EventoOperacao[] = [
      ...co.operacoes.map(
        (o) =>
          ({
            criado_em: o.criado_em,
            casamento_operacao_voice_id: o.casamento_operacao_voice_id,
            informacoes: {
              tipo: "alocacao-operador",
              operacao: o,
            },
          }) as EventoOperacao,
      ),
      ...co.aprovacoes_backoffice.map(
        (a) =>
          ({
            casamento_operacao_voice_id: a.casamento_operacao_voice_id,
            criado_em: a.criado_em,
            informacoes: {
              tipo: "aprovacao-backoffice",
              id: a.id,
              criado_em: a.criado_em,
              aprovacao: a.aprovacao,
              motivo: a.motivo,
              usuario: a.usuario,
              numero_controle_nome: a.registro_nome_id
                ? String(a.registro_nome_id)
                : null,
            },
          }) as EventoOperacao,
      ),
      ...co.envios_alocacao.flatMap((e) => {
        const eventos: EventoOperacao[] = [
          {
            casamento_operacao_voice_id: e.casamento_operacao_voice_id,
            criado_em: e.criado_em,
            informacoes: {
              tipo: "envio-alocacao",
              mensagem: { ...e, erro: null },
            },
          },
        ];
        if (e.erro) {
          eventos.push({
            casamento_operacao_voice_id: e.casamento_operacao_voice_id,
            criado_em: e.atualizado_em,
            informacoes: {
              tipo: "erro-mensagem",
              id_mensagem: e.id,
              erro: e.erro,
            },
          });
        }
        return eventos;
      }),
      ...co.atualizacoes_custodiante.map(
        (a) =>
          ({
            casamento_operacao_voice_id: a.casamento_operacao_voice_id,
            criado_em: a.criado_em,
            informacoes: {
              ...a,
              tipo: "atualizacao-custodiante",
            },
          }) as EventoOperacao,
      ),
    ];
    if (co.registros_nome.length > 0) {
      const primeiro = co.registros_nome.reduce(
        (min, reg) =>
          reg.criado_em.localeCompare(min) < 0 ? reg.criado_em : min,
        "9999-12-31T23:59:59",
      );
      const idsRealocacoes = new Set(
        co.registros_nome
          .map((r) => r.registro_nome_novo_id)
          .filter((r) => r !== null) as number[],
      );
      const originais = co.registros_nome.filter(
        (r) => !idsRealocacoes.has(r.id),
      );
      eventos.push({
        casamento_operacao_voice_id: null,
        criado_em: primeiro,
        informacoes: {
          tipo: "emissao-numeros-controle",
          quebras: originais,
        },
      } as EventoOperacao);
    }
    if (voice) {
      eventos.push({
        criado_em: voice.criado_em,
        casamento_operacao_voice_id: op.casamento_operacao_voice_id,
        informacoes: {
          tipo: "acato-voice",
          voice,
        },
      });
    }
    eventos.sort((e1, e2) => e1.criado_em.localeCompare(e2.criado_em));
    const processado: OperacaoType = {
      id: op.id,
      casamento_operacao_voice_id: op.casamento_operacao_voice_id,
      criado_em: op.criado_em,
      codigo_ativo: op.codigo_ativo,
      contraparte_nome: op.nome_contraparte,
      preco_unitario: op.preco_unitario,
      quantidade: op.quantidade,
      taxa: op.taxa,
      vanguarda_compra: op.vanguarda_compra,
      cadastro_ativo: op.registro_ativo,
      contraparte_conta: voice?.nome_contraparte ?? null,
      negocio_b3_id: voice?.id_trader ?? null,
      eventos,
    };
    return processado;
  });
};

export default function ComprasVendas({
  fundos,
  ativos_codigos,
}: ComprasVendasProps) {
  const [apiResult, setApiResult] = useState(ConnectionStatus.UNKNOWN);
  const [b3Result, setB3Result] = useState(ConnectionStatus.UNKNOWN);
  const [b3Session, setB3Session] = useState(ConnectionStatus.UNKNOWN);

  const voicesRef = useRef<Voice[]>([]);
  const negociosRef = useRef<OperacaoType[]>([]);
  const [voicesSemCasamento, setVoicesSemCasamento] = useState<Voice[]>([]);
  const [negocios, setNegocios] = useState<OperacaoType[]>([]);

  const apiColor = colorMap[apiResult] ?? "cinza";
  const b3Color = colorMap[b3Result] ?? "cinza";
  const b3SessionColor = colorMap[b3Session] ?? "cinza";

  const httpClient = useHTTP({ withCredentials: true });

  const apihc = async () => {
    setApiResult(ConnectionStatus.UNKNOWN);
    const { ok } = await httpClient.fetch("/healthcheck", {
      hideToast: { success: true },
    });
    setApiResult(ok ? ConnectionStatus.CONNECTED : ConnectionStatus.FAILED);
  };

  const b3hc = async () => {
    setB3Result(ConnectionStatus.UNKNOWN);
    const { ok } = await httpClient.fetch("/v1/b3/reachable", {
      hideToast: { success: true, clientError: true },
    });
    setB3Result(ok ? ConnectionStatus.CONNECTED : ConnectionStatus.FAILED);
  };

  const b3ss = async () => {
    setB3Session(ConnectionStatus.UNKNOWN);
    const { ok } = await httpClient.fetch("/v1/b3/connected", {
      hideToast: { success: true, clientError: true },
    });
    setB3Session(ok ? ConnectionStatus.CONNECTED : ConnectionStatus.FAILED);
  };

  const [pinging, startPing] = useAsync();

  const tabs = [
    [
      "Operações do dia",
      <WorkingDayTab
        voicesSemCasamento={voicesSemCasamento}
        fundos={fundos}
        ativos_codigos={ativos_codigos}
      />,
    ],
    ["Fluxo de operações", <TriagemB3 negocios={negocios} />],
    [
      "Resumo diário",
      <ResumoDiarioTab voices={voicesSemCasamento} negocios={negocios} />,
    ],
    ["Histórico", <HistoryTab />],
  ] as const;

  const { connection } = useWebSockets();

  const onMessage = useCallback(
    (ev: MessageEvent) => {
      const data = JSON.parse(ev.data) as WSMessage;
      const type = data.type;
      if (type !== WSMessageType.JSON) return;
      const msg = data.content as WSJSONMessage;
      const body = msg.body as EventoOperacao;

      if (body.informacoes.tipo === "listar-tudo") {
        voicesRef.current = body.informacoes.voices;
        setVoicesSemCasamento(voicesRef.current);
        negociosRef.current = processarNegocios(body.informacoes.operacoes);
        setNegocios(negociosRef.current);
      } else if (body.informacoes.tipo === "acato-voice") {
        const voice = body.informacoes.voice;
        const voiceIndex = voicesRef.current.findIndex(
          (v) => v.id === voice.id,
        );
        if (voiceIndex !== -1) {
          voicesRef.current.splice(voiceIndex, 1);
          setVoicesSemCasamento([...voicesRef.current]);
        }
        const negocio = negociosRef.current.find(
          (n) =>
            n.casamento_operacao_voice_id === body.casamento_operacao_voice_id,
        );
        if (negocio) {
          negocio.eventos.push(body);
          setNegocios([...negociosRef.current]);
        } else {
          voicesRef.current.push(body.informacoes.voice);
          setVoicesSemCasamento([...voicesRef.current]);
        }
      } else if (body.informacoes.tipo === "aprovacao-backoffice") {
        const negocio = negociosRef.current.find(
          (n) =>
            n.casamento_operacao_voice_id === body.casamento_operacao_voice_id,
        );
        if (!negocio) return;
        negocio.eventos.push(body);
        setNegocios([...negociosRef.current]);
      } else if (body.informacoes.tipo === "alocacao-operador") {
        const negocio = negociosRef.current.find(
          (n) =>
            n.casamento_operacao_voice_id === body.casamento_operacao_voice_id,
        );
        if (!negocio) {
          // Primeira alocação
          const op = body.informacoes.operacao;
          const voice = voicesRef.current.find(
            (v) =>
              v.vanguarda_compra === op.vanguarda_compra &&
              v.codigo_ativo === op.codigo_ativo &&
              v.data_operacao === op.data_operacao &&
              v.quantidade.toFixed(6) === op.quantidade.toFixed(6) &&
              v.preco_unitario.toFixed(6) === op.preco_unitario.toFixed(6) &&
              v.registro_contraparte?.nome === op.nome_contraparte,
          );
          const processado: OperacaoType = {
            id: op.id,
            casamento_operacao_voice_id: op.casamento_operacao_voice_id,
            criado_em: op.criado_em,
            codigo_ativo: op.codigo_ativo,
            contraparte_nome: op.nome_contraparte,
            preco_unitario: op.preco_unitario,
            quantidade: op.quantidade,
            taxa: op.taxa,
            vanguarda_compra: op.vanguarda_compra,
            cadastro_ativo: op.registro_ativo,
            contraparte_conta: voice?.nome_contraparte ?? null,
            negocio_b3_id: voice?.id_trader ?? null,
            eventos: [body],
          };
          if (voice) {
            processado.eventos.push({
              casamento_operacao_voice_id: op.casamento_operacao_voice_id,
              criado_em: voice.criado_em,
              informacoes: {
                tipo: "acato-voice",
                voice,
              },
            });
            const voiceIndex = voicesRef.current.findIndex(
              (v) => voice.id === v.id,
            );
            if (voiceIndex === -1) return;
            voicesRef.current.splice(voiceIndex, 1);
            setVoicesSemCasamento([...voicesRef.current]);
          }
          negociosRef.current.push(processado);
          setNegocios([...negociosRef.current]);
        } else {
          // Realocação
          negocio.eventos.push(body);
          setNegocios([...negociosRef.current]);
        }
      } else if (body.informacoes.tipo === "envio-alocacao") {
        const negocio = negociosRef.current.find(
          (n) =>
            n.casamento_operacao_voice_id === body.casamento_operacao_voice_id,
        );
        if (!negocio) return;
        negocio.eventos.push(body);
        setNegocios([...negociosRef.current]);
      } else if (body.informacoes.tipo === "corretoras") {
        const idParaCorretora = body.informacoes.corretoras.reduce(
          (map, c) => {
            c.contas.forEach((conta) => (map[conta] = c));
            return map;
          },
          {} as Record<string, CorretoraResumo>,
        );
        voicesRef.current.forEach((v) => {
          if (v.registro_contraparte) return;
          if (!(v.nome_contraparte in idParaCorretora)) return;
          const corretora = idParaCorretora[v.nome_contraparte];
          v.registro_contraparte = {
            id: -1,
            nome: corretora.nome,
            ids_b3: corretora.contas.map((c) => ({
              id: -1,
              id_b3: c,
            })),
          };
        });
        setVoicesSemCasamento([...voicesRef.current]);
      } else if (body.informacoes.tipo === "emissao-numeros-controle") {
        const cid = body.informacoes.quebras[0].casamento_operacao_voice_id;
        const negocio = negociosRef.current.find(
          (n) => n.casamento_operacao_voice_id === cid,
        );
        if (!negocio) return;
        negocio.eventos.push(body);
        setNegocios([...negociosRef.current]);
      } else if (body.informacoes.tipo === "atualizacao-custodiante") {
        const cid = body.informacoes.casamento_operacao_voice_id;
        const negocio = negociosRef.current.find(
          (n) => n.casamento_operacao_voice_id === cid,
        );
        if (!negocio) return;
        negocio.eventos.push(body);
        setNegocios([...negociosRef.current]);
      }
    },
    [connection],
  );

  useEffect(() => {
    startPing(async () => {
      await Promise.all([apihc(), b3hc(), b3ss()]);
    });
    if (connection) {
      connection.addEventListener("message", onMessage);
      httpClient.fetch("v1/operacoes/listar-tudo");
    }
    return () => {
      if (connection) {
        connection.removeEventListener("message", onMessage);
      }
    };
  }, [connection]);

  return (
    <VStack h="100%" alignItems="stretch" gap={0}>
      <Tabs
        colorScheme="verde"
        display="flex"
        flexDirection="column"
        h="calc(100% - 32px)"
        isLazy
      >
        <TabList>
          {tabs.map(([name]) => (
            <Tab key={name}>{name}</Tab>
          ))}
        </TabList>
        <TabPanels flex={1} overflow="auto">
          {tabs.map(([name, tab]) => (
            <TabPanel h="100%" overflow="auto" key={name} p={0}>
              {tab}
            </TabPanel>
          ))}
        </TabPanels>
      </Tabs>
      <HStack h="32px" bgColor="cinza.main" p="4px">
        <Icon
          cursor={pinging ? "not-allowed" : "pointer"}
          color={pinging ? "cinza.main" : "verde.main"}
          ml="24px"
          as={IoReloadCircleOutline}
        />
        <Tooltip>
          <Tag fontSize="xs" colorScheme={apiColor}>
            <Text>
              <Icon as={IoEllipse} /> API Vanguarda
            </Text>
          </Tag>
        </Tooltip>
        <Tooltip>
          <Tag fontSize="xs" colorScheme={b3Color}>
            <Text>
              <Icon as={IoEllipse} /> Mensageria B3
            </Text>
          </Tag>
        </Tooltip>
        <Tooltip>
          <Tag fontSize="xs" colorScheme={b3SessionColor}>
            <Text>
              <Icon as={IoEllipse} /> Sessão B3
            </Text>
          </Tag>
        </Tooltip>
      </HStack>
    </VStack>
  );
}
