"use client";

import {
  Divider,
  HStack,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Text,
  VStack,
} from "@chakra-ui/react";
import Conectividade from "./Conectividade";
import AbaAcompanhamento from "./abas/acompanhamento/AbaAcompanhamento";
import AbaSimulacao from "./abas/simulacao/AbaSimulacao";
import AbaDadosNegociacao from "./abas/dados-negociacao/AbaDadosNegociacao";
import AbaTriagem from "./abas/triagem/AbaTriagem";
import { useHTTP, useWebSockets } from "@/lib/hooks";
import { useCallback, useContext, useEffect, useState } from "react";
import { WSMessage, WSMessageType } from "@/lib/types/api/iv/websockets";
import { AlocacoesContext } from "@/lib/providers/AlocacoesProvider";
import {
  CasamentoAlocacaoB3Voice,
  ResultadoBuscaBoleta,
  ResultadoBuscaBoleta_Alocacao,
} from "@/lib/types/api/iv/operacoes/processamento";
import ModalAlocacao from "./modal-alocacao/ModalAlocacao";

const alocacoesEQuebras = (as: ResultadoBuscaBoleta_Alocacao[]) => [
  ...as,
  ...as.flatMap((a) => a.quebras),
];

export default function Operacoes() {
  const { boletas, setBoletas, alocacaoDetalhes, setAlocacaoDetalhes } =
    useContext(AlocacoesContext);

  const ws = useWebSockets();

  const onListarAlocacoes = useCallback((boletas: ResultadoBuscaBoleta[]) => {
    setBoletas(
      boletas.map((boleta) => ({
        boleta,
        client_id: Math.random(),
      })),
    );
  }, []);

  const onNovaAlocacao = useCallback(
    (novaBoleta: ResultadoBuscaBoleta, clientId: number) => {
      setBoletas((boletas) => [
        {
          boleta: novaBoleta,
          client_id: clientId,
        },
        ...boletas,
      ]);
    },
    [],
  );

  const onAprovacao = useCallback(
    (alocacao_id: number, aprovado_em: string, aprovado_por: string) => {
      setBoletas((boletas) => {
        const boleta = boletas.find((b) =>
          alocacoesEQuebras(b.boleta.alocacoes).find(
            (a) => a.id === alocacao_id,
          ),
        );
        if (!boleta) return boletas;
        const alocacao = alocacoesEQuebras(boleta.boleta.alocacoes).find(
          (a) => a.id === alocacao_id,
        );
        if (!alocacao) return boletas;
        alocacao.aprovacao_usuario = aprovado_por;
        alocacao.aprovado_em = aprovado_em;
        return [...boletas];
      });
    },
    [],
  );

  const onAlocacaoAdministrador = useCallback(
    (
      alocacao_id: number,
      alocado_em: string,
      codigo_administrador: string | null,
      alocacao_usuario_id: number,
    ) => {
      setBoletas((boletas) => {
        const boleta = boletas.find((b) =>
          alocacoesEQuebras(b.boleta.alocacoes).find(
            (a) => a.id === alocacao_id,
          ),
        );
        if (!boleta) return boletas;
        const alocacao = alocacoesEQuebras(boleta.boleta.alocacoes).find(
          (a) => a.id === alocacao_id,
        );
        if (!alocacao) return boletas;
        if (alocacao.alocacao_administrador) return boletas;
        alocacao.alocacao_administrador = {
          alocacao_id,
          alocado_em,
          codigo_administrador,
          alocacao_usuario_id,
          cancelamento: null,
          liquidacao: null,
        };
        return [...boletas];
      });
    },
    [],
  );

  const onCancelamento = useCallback(
    (
      alocacao_id: number,
      motivo: string | null,
      cancelado_em: string,
      usuario_id: number,
    ) => {
      setBoletas((boletas) => {
        const boleta = boletas.find((b) =>
          alocacoesEQuebras(b.boleta.alocacoes).find(
            (a) => a.id === alocacao_id,
          ),
        );
        if (!boleta) return boletas;
        const alocacao = alocacoesEQuebras(boleta.boleta.alocacoes).find(
          (a) => a.id === alocacao_id,
        );
        if (!alocacao) return boletas;
        if (alocacao.cancelamento) return boletas;
        alocacao.cancelamento = {
          alocacao_id,
          motivo,
          cancelado_em,
          usuario_id,
        };
        return [...boletas];
      });
    },
    [],
  );

  const onCancelamentoAdministrador = useCallback(
    (
      alocacao_administrador_id: number,
      motivo: string | null,
      cancelado_em: string,
      usuario_id: number,
    ) => {
      setBoletas((boletas) => {
        const boleta = boletas.find((b) =>
          alocacoesEQuebras(b.boleta.alocacoes).find(
            (a) => a.id === alocacao_administrador_id,
          ),
        );
        if (!boleta) return boletas;
        const alocacao = alocacoesEQuebras(boleta.boleta.alocacoes).find(
          (a) =>
            a.alocacao_administrador?.alocacao_id === alocacao_administrador_id,
        );
        if (!alocacao) return boletas;
        if (
          !alocacao.alocacao_administrador ||
          alocacao.alocacao_administrador.cancelamento
        )
          return boletas;
        alocacao.alocacao_administrador.cancelamento = {
          alocacao_administrador_id,
          motivo,
          cancelado_em,
          usuario_id,
        };
        return [...boletas];
      });
    },
    [],
  );

  const onLiquidacao = useCallback(
    (
      alocacao_administrador_id: number,
      liquidado_em: string,
      usuario_id: number,
    ) => {
      setBoletas((boletas) => {
        const boleta = boletas.find((b) =>
          alocacoesEQuebras(b.boleta.alocacoes).find(
            (a) => a.id === alocacao_administrador_id,
          ),
        );
        if (!boleta) return boletas;
        const alocacao = alocacoesEQuebras(boleta.boleta.alocacoes).find(
          (a) =>
            a.alocacao_administrador?.alocacao_id === alocacao_administrador_id,
        );
        if (!alocacao) return boletas;
        if (
          !alocacao.alocacao_administrador ||
          alocacao.alocacao_administrador.liquidacao
        )
          return boletas;
        alocacao.alocacao_administrador.liquidacao = {
          alocacao_administrador_id,
          liquidado_em,
          usuario_id,
        };
        return [...boletas];
      });
    },
    [],
  );

  const onCasamento = useCallback(
    (casamento: CasamentoAlocacaoB3Voice, alocacoes_ids: number[]) => {
      setBoletas((boletas) => {
        const boleta = boletas.find((b) =>
          alocacoesEQuebras(b.boleta.alocacoes).find((a) =>
            alocacoes_ids.includes(a.id),
          ),
        );
        if (!boleta) return boletas;
        const alocacoes = alocacoesEQuebras(boleta.boleta.alocacoes).filter(
          (a) => alocacoes_ids.includes(a.id),
        );
        alocacoes.forEach((a) => (a.casamento = structuredClone(casamento)));
        return [...boletas];
      });
    },
    [],
  );

  const onEnvioPreTrade = useCallback(
    (id_trader: string, id_envio: number, enviado_em: string) => {
      setBoletas((boletas) => {
        const voices = boletas
          .flatMap((b) =>
            (
              alocacoesEQuebras(b.boleta.alocacoes)
                .map((a) => a.casamento)
                .filter((c) => c) as CasamentoAlocacaoB3Voice[]
            ).map((c) => c.voice),
          )
          .filter((v) => v.id_trader === id_trader);
        voices.forEach((v) => {
          const envio = v.envios_pre_trade.find((e) => e.id === id_envio);
          if (envio) return;
          v.envios_pre_trade.push({
            id: id_envio,
            enviado_em,
            erro: null,
          });
        });
        return [...boletas];
      });
    },
    [],
  );

  const onErroPreTrade = useCallback(
    (id_trader: string, id_envio: number, erro: string) => {
      setBoletas((boletas) => {
        const voices = boletas
          .flatMap((b) =>
            (
              alocacoesEQuebras(b.boleta.alocacoes)
                .map((a) => a.casamento)
                .filter((c) => c) as CasamentoAlocacaoB3Voice[]
            ).map((c) => c.voice),
          )
          .filter((v) => v.id_trader === id_trader);
        voices.forEach((v) => {
          const envio = v.envios_pre_trade.find((e) => e.id === id_envio);
          if (!envio) return;
          envio.erro = erro;
        });
        return [...boletas];
      });
    },
    [],
  );

  const onRecebimentoPostTrade = useCallback(
    (id_trader: string, horario_recebimento_post_trade: string) => {
      setBoletas((boletas) => {
        const voices = boletas
          .flatMap((b) =>
            (
              alocacoesEQuebras(b.boleta.alocacoes)
                .map((a) => a.casamento)
                .filter((c) => c) as CasamentoAlocacaoB3Voice[]
            ).map((c) => c.voice),
          )
          .filter((v) => v.id_trader === id_trader);
        voices.forEach(
          (v) =>
            (v.horario_recebimento_post_trade = horario_recebimento_post_trade),
        );
        return [...boletas];
      });
    },
    [],
  );

  const onEnvioPostTrade = useCallback(
    (id_trader: string, id_envio: string, enviado_em: string) => {
      setBoletas((boletas) => {
        const voices = boletas
          .flatMap((b) =>
            (
              alocacoesEQuebras(b.boleta.alocacoes)
                .map((a) => a.casamento)
                .filter((c) => c) as CasamentoAlocacaoB3Voice[]
            ).map((c) => c.voice),
          )
          .filter((v) => v.id_trader === id_trader);
        voices.forEach((v) => {
          const envio = v.envios_post_trade.find((e) => e.id === id_envio);
          if (envio) return;
          v.horario_recebimento_post_trade ??= enviado_em;
          v.envios_post_trade.push({
            id: id_envio,
            enviado_em,
            erro: null,
            sucesso_em: null,
          });
        });
        return [...boletas];
      });
    },
    [],
  );

  const onErroPostTrade = useCallback(
    (id_trader: string, id_envio: string, erro: string) => {
      setBoletas((boletas) => {
        const voices = boletas
          .flatMap((b) =>
            (
              alocacoesEQuebras(b.boleta.alocacoes)
                .map((a) => a.casamento)
                .filter((c) => c) as CasamentoAlocacaoB3Voice[]
            ).map((c) => c.voice),
          )
          .filter((v) => v.id_trader === id_trader);
        voices.forEach((v) => {
          const envio = v.envios_post_trade.find((e) => e.id === id_envio);
          if (!envio) return;
          v.horario_recebimento_post_trade ??= new Date().toISOString();
          envio.erro = erro;
        });
        return [...boletas];
      });
    },
    [],
  );

  const onSucessoPostTrade = useCallback(
    (id_trader: string, id_envio: string, sucesso_em: string) => {
      setBoletas((boletas) => {
        const voices = boletas
          .flatMap((b) =>
            (
              alocacoesEQuebras(b.boleta.alocacoes)
                .map((a) => a.casamento)
                .filter((c) => c) as CasamentoAlocacaoB3Voice[]
            ).map((c) => c.voice),
          )
          .filter((v) => v.id_trader === id_trader);
        voices.forEach((v) => {
          const envio = v.envios_post_trade.find((e) => e.id === id_envio);
          if (!envio) return;
          v.horario_recebimento_post_trade ??= new Date().toISOString();
          envio.sucesso_em = sucesso_em;
        });
        return [...boletas];
      });
    },
    [],
  );

  const onRegistrosNoMesNovos = useCallback(
    (
      registros: {
        alocacao_id: number;
        numero_controle: string;
        quantidade: string;
      }[],
    ) => {
      setBoletas((boletas) => {
        for (const { alocacao_id, numero_controle, quantidade } of registros) {
          const alocacao = alocacoesEQuebras(
            boletas.flatMap((b) => b.boleta.alocacoes),
          ).find((a) => a.id === alocacao_id);
          if (!alocacao) continue;
          alocacao.registro_NoMe = {
            alocacao_id,
            numero_controle,
            posicao_custodia: null,
            posicao_custodia_contraparte: null,
            posicao_custodia_contraparte_em: null,
            posicao_custodia_em: null,
            recebido_em: new Date().toISOString(),
            data: new Date().toISOString().split("T")[0],
          };
        }
        return [...boletas];
      });
    },
    [],
  );

  const onRegistroNoMeAtualizacao = ({
    alocacao_id,
    posicao_custodia,
    posicao_custodia_em,
    posicao_custodia_contraparte,
    posicao_custodia_contraparte_em,
  }: {
    alocacao_id: number;
    posicao_custodia?: boolean | null;
    posicao_custodia_em?: string | null;
    posicao_custodia_contraparte?: boolean | null;
    posicao_custodia_contraparte_em?: string | null;
  }) => {
    setBoletas((boletas) => {
      const alocacao = alocacoesEQuebras(
        boletas.flatMap((b) => b.boleta.alocacoes),
      ).find((a) => a.id === alocacao_id);
      if (!alocacao) return boletas;
      if (!alocacao.registro_NoMe) return boletas;
      if (posicao_custodia !== undefined && posicao_custodia_em !== undefined) {
        alocacao.registro_NoMe.posicao_custodia = posicao_custodia;
        alocacao.registro_NoMe.posicao_custodia_em = posicao_custodia_em;
      }
      if (
        posicao_custodia_contraparte !== undefined &&
        posicao_custodia_contraparte_em !== undefined
      ) {
        alocacao.registro_NoMe.posicao_custodia_contraparte =
          posicao_custodia_contraparte;
        alocacao.registro_NoMe.posicao_custodia_contraparte_em =
          posicao_custodia_contraparte_em;
      }
      return [...boletas];
    });
  };

  const onQuebras = useCallback(
    (
      alocacoesQuebradas: {
        alocacao_anterior_id: number;
        quebras: { alocacao_id: number; quantidade: string }[];
      }[],
    ) => {
      setBoletas((boletas) => {
        for (const { alocacao_anterior_id, quebras } of alocacoesQuebradas) {
          const alocacao = boletas
            .flatMap((b) => b.boleta.alocacoes)
            .find((a) => a.id === alocacao_anterior_id);
          if (!alocacao || alocacao.quebras.length) continue;
          alocacao.quebras = quebras.map(({ alocacao_id: id, quantidade }) => ({
            ...alocacao,
            alocacao_anterior_id: alocacao.id,
            id,
            quantidade,
            quebras: [],
          }));
        }
        return [...boletas];
      });
    },
    [],
  );

  const onMessage = useCallback(
    (ev: MessageEvent) => {
      try {
        const msg = JSON.parse(ev.data) as WSMessage;
        const body = (msg.content as any)?.body;
        if (
          msg.type !== WSMessageType.JSON ||
          !body ||
          body.canal !== "operacoes.alocacao" ||
          !("tipo" in body) ||
          typeof body.tipo !== "string"
        ) {
          return;
        }
        const tipo: string = body.tipo;

        const acoes: Record<string, Function> = {
          "alocacao.todas": () => onListarAlocacoes(body.dados),
          "alocacao.nova": () =>
            onNovaAlocacao(body.dados, body.client_request_id),
          "alocacao.aprovacao": () =>
            onAprovacao(
              body.dados.alocacao_id,
              body.dados.aprovado_em,
              body.dados.aprovado_por,
            ),
          "alocacao.nova.administrador": () =>
            onAlocacaoAdministrador(
              body.dados.alocacao_id,
              body.dados.alocado_em,
              body.dados.codigo_administrador,
              body.dados.alocacao_usuario_id,
            ),
          "alocacao.cancelamento": () =>
            onCancelamento(
              body.dados.alocacao_id,
              body.dados.motivo,
              body.dados.cancelado_em,
              body.dados.usuario_id,
            ),
          "alocacao.cancelamento.administrador": () =>
            onCancelamentoAdministrador(
              body.dados.alocacao_administrador_id,
              body.dados.motivo,
              body.dados.cancelado_em,
              body.dados.usuario_id,
            ),
          "alocacao.liquidacao": () =>
            onLiquidacao(
              body.dados.alocacao_administrador_id,
              body.dados.liquidado_em,
              body.dados.usuario_id,
            ),
          "voice.casamento": () =>
            onCasamento(body.dados.casamento, body.dados.alocacoes_ids),
          "voice.orderentry.envio": () =>
            onEnvioPreTrade(
              body.dados.id_trader,
              body.dados.id_envio,
              body.dados.enviado_em,
            ),
          "voice.orderentry.erro": () =>
            onErroPreTrade(
              body.dados.id_trader,
              body.dados.id_envio,
              body.dados.erro,
            ),
          "voice.posttrade.recebido": () =>
            onRecebimentoPostTrade(
              body.dados.id_trader,
              body.dados.horario_recebimento_post_trade,
            ),
          "voice.posttrade.envio": () =>
            onEnvioPostTrade(
              body.dados.id_trader,
              body.dados.id_envio,
              body.dados.enviado_em,
            ),
          "voice.posttrade.erro": () =>
            onErroPostTrade(
              body.dados.id_trader,
              body.dados.id_envio,
              body.dados.erro,
            ),
          "voice.posttrade.alocado": () =>
            onSucessoPostTrade(
              body.dados.id_trader,
              body.dados.id_envio,
              body.dados.sucesso_em,
            ),
          "voice.registro_nome.novos": () => onRegistrosNoMesNovos(body.dados),
          "voice.registro_nome.atualizacao": () =>
            onRegistroNoMeAtualizacao(body.dados),
          "alocacoes.quebras": () => onQuebras(body.dados),
        };
        acoes[tipo]?.();
      } catch (err) {
        console.log("Falha ao processar mensagem.", err);
      }
    },
    [ws.connection],
  );

  const httpClient = useHTTP({ withCredentials: true });

  const listarTudo = useCallback(() => {
    httpClient.fetch("v1/operacoes/alocacoes/boleta/ws", { method: "GET" });
  }, []);

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

  const [contagem, setContagem] = useState<{ s: number; t: number; a: number }>(
    { s: 0, t: 0, a: 0 },
  );

  const boletasComPeloMenosUmaAlocacaoSemAprovacao = boletas.filter((b) =>
    b.boleta.alocacoes.some((a) => !a.aprovado_em),
  );
  const boletasComPeloMenosUmaAlocacaoAprovada = boletas.filter((b) =>
    b.boleta.alocacoes.some((a) => a.aprovado_em),
  );

  return (
    <>
      <VStack gap={0} h="calc(100vh - 56px)" alignItems="stretch">
        <Tabs
          overflow="hidden"
          flex={1}
          size="sm"
          variant="soft-rounded"
          colorScheme="verde"
          p={0}
        >
          <TabList p="4px 8px" h="37px">
            <HStack w="100%" justifyContent="space-between">
              <HStack gap={0}>
                <Tab>Simulação ({contagem.s})</Tab>
                <Tab>
                  Triagem ({boletasComPeloMenosUmaAlocacaoSemAprovacao.length})
                </Tab>
                <Tab>
                  Acompanhamento (
                  {boletasComPeloMenosUmaAlocacaoAprovada.length})
                </Tab>
              </HStack>
              <HStack>
                {/* <Tab>Histórico</Tab>
              <Tab>Relatórios</Tab> */}
                <Tab>Dados de negociação</Tab>
              </HStack>
            </HStack>
          </TabList>
          <TabPanels h="calc(100% - 37px)" p={0}>
            <TabPanel h="100%" p={0}>
              <AbaSimulacao
                onContagemChange={(s) => setContagem({ ...contagem, s })}
              />
            </TabPanel>
            <TabPanel h="100%" p={0}>
              <AbaTriagem />
            </TabPanel>
            <TabPanel h="100%" p={0}>
              <AbaAcompanhamento />
            </TabPanel>
            <TabPanel h="100%" p={0}>
              <AbaDadosNegociacao />
            </TabPanel>
          </TabPanels>
        </Tabs>
        <Conectividade />
      </VStack>
      <ModalAlocacao
        alocacao={alocacaoDetalhes}
        onClose={() => setAlocacaoDetalhes(null)}
      />
    </>
  );
}
