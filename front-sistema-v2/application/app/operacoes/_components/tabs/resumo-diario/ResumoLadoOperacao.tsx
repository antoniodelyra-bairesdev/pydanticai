"use client";

import {
  AlocacaoStatus,
  EventoAtualizacaoCustodiante,
  EventoEmissaoNumerosControle,
  OperacaoType,
  Voice,
} from "@/lib/types/api/iv/v1";
import { Box, HStack, StackProps, Text, VStack } from "@chakra-ui/react";
import { Chart } from "react-chartjs-2";
import { getColorHex } from "@/app/theme";
import { useEffect, useRef } from "react";
import { ChartJSOrUndefined } from "react-chartjs-2/dist/types";
import { pendencias } from "../triagem-b3/OperacaoItemColuna";

import { dateToStr, fmtNumber } from "@/lib/util/string";
import { ChartData } from "chart.js";

export type ResumoLadoOperacaoProps = {
  lado: "Compra" | "Venda";
  negocios: OperacaoType[];
  voices: Voice[];
} & StackProps;

export default function ResumoLadoOperacao({
  lado,
  negocios,
  voices,
  ...props
}: ResumoLadoOperacaoProps) {
  let pendenteReais = voices.reduce(
    (total, v) => (total += v.preco_unitario * v.quantidade),
    0,
  );
  let aguardandoReais = 0;
  let aprovadoReais = 0;

  for (const negocio of negocios) {
    const pendencias_negocio = pendencias(negocio.eventos);
    if (pendencias_negocio.length > 0) {
      pendenteReais += negocio.quantidade * negocio.preco_unitario;
      continue;
    }

    aguardandoReais += negocio.quantidade * negocio.preco_unitario;

    const emissaoNCN = negocio.eventos.find(
      (e) => e.informacoes.tipo === "emissao-numeros-controle",
    )?.informacoes as EventoEmissaoNumerosControle | undefined;
    if (!emissaoNCN) {
      continue;
    }

    const quantidadePorRegistroNome = emissaoNCN.quebras.reduce(
      (rcrd, { numero_controle_nome, quantidade }) => {
        rcrd[numero_controle_nome] = quantidade;
        return rcrd;
      },
      {} as Record<string, number>,
    );

    const atualizacoesCustodia = negocio.eventos
      .filter((e) => e.informacoes.tipo === "atualizacao-custodiante")
      .map((e) => e.informacoes as EventoAtualizacaoCustodiante);

    for (const atualizacao of atualizacoesCustodia) {
      if (atualizacao.status === AlocacaoStatus.Disponível_para_Registro) {
        const valor =
          quantidadePorRegistroNome[
            atualizacao.registro_nome.numero_controle_nome
          ] * negocio.preco_unitario;
        aprovadoReais += valor;
        aguardandoReais -= valor;
      }
    }
  }

  const data = {
    labels: [
      "Pendente ação",
      "Aguardando aprovação da custódia",
      "Aprovado para liquidação",
    ],
    datasets: [
      {
        data: [pendenteReais, aguardandoReais, aprovadoReais],
        backgroundColor: [
          getColorHex("azul_3.main"),
          getColorHex("cinza.main"),
          getColorHex("verde.main"),
        ],
        hoverOffset: 4,
      },
    ],
  } as ChartData;

  const options = {
    cutout: "70%",
    responsive: true,
    maintainAspectRatio: true,
  } as any;

  const intervalRef = useRef<number>();

  const doughnutChartRef = useRef<ChartJSOrUndefined<"doughnut">>();

  useEffect(() => {
    if (intervalRef.current === undefined) {
      intervalRef.current = window.setInterval(() => {
        if (!doughnutChartRef.current) return;
        const bgD = doughnutChartRef.current.data.datasets[0]
          ?.backgroundColor as string[] | undefined;
        if (!bgD) return;
        const azul_3_main = getColorHex("azul_3.main");
        const azul_3_100 = getColorHex("azul_3.200");
        bgD[0] = bgD[0] === azul_3_main ? azul_3_100 : azul_3_main;
        doughnutChartRef.current.update();
      }, 500);
    }

    return () => {
      if (intervalRef.current !== undefined) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = undefined;
      }
    };
  }, []);

  const eventos = negocios.flatMap((n) =>
    n.eventos.map((e) => ({ evento: e, negocio: n })),
  );
  for (const voice of voices) {
    eventos.push({
      evento: {
        informacoes: {
          tipo: "acato-voice",
          voice,
        },
        casamento_operacao_voice_id: null,
        criado_em: voice.criado_em,
      },
      negocio: null as any,
    });
  }
  eventos.sort((e1, e2) =>
    e1.evento.criado_em.localeCompare(e2.evento.criado_em),
  );

  type Ponto = { x: Date; y: number };

  const progressoPendenteAcao: Ponto[] = [];
  const progressoAguardandoCustodia: Ponto[] = [];
  const progressoAprovado: Ponto[] = [];

  for (const progresso of [
    progressoPendenteAcao,
    progressoAguardandoCustodia,
    progressoAprovado,
  ]) {
    progresso.push({ x: new Date(dateToStr(new Date()) + "T09:00:00"), y: 0 });
  }

  let valorAtualizadoPendenteAcao = 0;
  let valorAtualizadoAguardandoCustodia = 0;
  let valorAtualizadoAprovado = 0;
  for (const contexto of eventos) {
    const x = new Date(contexto.evento.criado_em);
    const tipo = contexto.evento.informacoes.tipo;
    if (tipo === "acato-voice") {
      valorAtualizadoPendenteAcao +=
        contexto.evento.informacoes.voice.preco_unitario *
        contexto.evento.informacoes.voice.quantidade;
      progressoPendenteAcao.push({ x, y: valorAtualizadoPendenteAcao });
    } else if (tipo === "aprovacao-backoffice") {
      if (!contexto.evento.informacoes.aprovacao) continue;
      const valorAprovado =
        contexto.negocio.preco_unitario * contexto.negocio.quantidade;
      valorAtualizadoPendenteAcao -= valorAprovado;
      valorAtualizadoAguardandoCustodia += valorAprovado;
      progressoPendenteAcao.push({ x, y: valorAtualizadoPendenteAcao });
      progressoAguardandoCustodia.push({
        x,
        y: valorAtualizadoAguardandoCustodia,
      });
    } else if (tipo === "atualizacao-custodiante") {
      if (
        contexto.evento.informacoes.status !==
        AlocacaoStatus.Disponível_para_Registro
      )
        continue;
      const valorDisponivel =
        contexto.negocio.preco_unitario *
        contexto.evento.informacoes.registro_nome.quantidade;
      valorAtualizadoAguardandoCustodia -= valorDisponivel;
      valorAtualizadoAprovado += valorDisponivel;
      progressoAguardandoCustodia.push({
        x,
        y: valorAtualizadoAguardandoCustodia,
      });
      progressoAprovado.push({ x, y: valorAtualizadoAprovado });
    }
  }

  for (const progresso of [
    progressoPendenteAcao,
    progressoAguardandoCustodia,
    progressoAprovado,
  ]) {
    const ultimoDado = progresso.at(-1);
    if (!ultimoDado) continue;
    progresso.push({ x: new Date(), y: ultimoDado.y });
  }

  return (
    <VStack alignItems="stretch" p="12px 24px" {...props}>
      <Box>
        <Text
          as="span"
          fontWeight={900}
          color={lado === "Compra" ? "azul_3.main" : "rosa.main"}
          size="md"
          border="2px solid"
          borderRadius="4px"
          borderColor={lado === "Compra" ? "azul_3.main" : "rosa.main"}
          p="1px 2px 0px 2px"
          lineHeight={1}
        >
          {lado.toUpperCase()}
        </Text>
      </Box>
      <HStack justifyContent="space-between" alignItems="stretch" p="12px 24px">
        <VStack flex={2} alignItems="stretch">
          <Box flex={1}>
            <Chart
              type="line"
              data={{
                datasets: [
                  {
                    label: "Aprovado para liquidação",
                    data: progressoAprovado,
                    backgroundColor: getColorHex("verde.main"),
                    fill: "origin",
                    stepped: "before",
                  },
                  {
                    label: "Aguardando aprovação da custódia",
                    data: progressoAguardandoCustodia,
                    backgroundColor: getColorHex("cinza.main"),
                    stepped: "before",
                  },
                  {
                    label: "Pendente Ação",
                    data: progressoPendenteAcao,
                    backgroundColor: getColorHex("azul_3.main"),
                    stepped: "before",
                  },
                ],
              }}
              options={{
                interaction: {
                  mode: "nearest",
                },
                elements: {
                  line: {
                    fill: "-1",
                  },
                },
                scales: {
                  x: {
                    type: "time",
                    ticks: {
                      source: "data",
                    },
                    display: true,
                    title: {
                      display: true,
                      text: "Horário",
                    },
                  },
                  y: {
                    min: 0,
                    stacked: true,
                    display: true,
                    title: {
                      display: true,
                      text: "Valor (R$)",
                    },
                  },
                },
                maintainAspectRatio: false,
                responsive: true,
              }}
            />
          </Box>
        </VStack>
        <VStack>
          <Box w="256px" h="256px" position="relative">
            <Chart
              ref={doughnutChartRef as any}
              type="doughnut"
              data={data}
              options={options}
            />
            <VStack
              gap={0}
              justifyContent="center"
              left={0}
              top={0}
              w="100%"
              h="100%"
              position="absolute"
              fontSize="md"
              fontWeight={600}
            >
              <Text
                p="2px 4px"
                borderRadius="4px"
                bgColor="verde.main"
                color="white"
              >
                R$ {fmtNumber(aprovadoReais)}
              </Text>
              <Text color="cinza.500">R$ {fmtNumber(aguardandoReais)}</Text>
              <Text color="azul_3.main">R$ {fmtNumber(pendenteReais)}</Text>
            </VStack>
          </Box>
          <VStack alignItems="stretch" gap={0} fontSize="sm">
            <HStack>
              <Box w="24px" h="16px" bgColor="verde.main" />
              <Text>Aprovado para liquidação</Text>
            </HStack>
            <HStack>
              <Box w="24px" h="16px" bgColor="cinza.main" />
              <Text>Aguardando aprovação da custódia</Text>
            </HStack>
            <HStack>
              <Box w="24px" h="16px" bgColor="azul_3.main" />
              <Text>Pendente ação</Text>
            </HStack>
          </VStack>
        </VStack>
      </HStack>
    </VStack>
  );
}
