"use client";

import { OperacaoType, Voice } from "@/lib/types/api/iv/v1";
import { Divider, VStack } from "@chakra-ui/react";
import ResumoLadoOperacao from "./ResumoLadoOperacao";

export type ResumoDiarioTabProps = {
  negocios: OperacaoType[];
  voices: Voice[];
};

import {
  ArcElement,
  Chart,
  Filler,
  Tooltip as ChartTooltip,
  TimeScale,
  LinearScale,
  PointElement,
  LineElement,
  DoughnutController,
  LineController,
} from "chart.js";
Chart.register(
  ArcElement,
  TimeScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  ChartTooltip,
  DoughnutController,
  LineController,
);

export default function ResumoDiarioTab({
  negocios,
  voices,
}: ResumoDiarioTabProps) {
  return (
    <VStack w="100%" h="100%" alignItems="stretch">
      <VStack alignItems="stretch" h="100%" gap={0}>
        <ResumoLadoOperacao
          lado="Compra"
          negocios={negocios.filter((n) => n.vanguarda_compra)}
          voices={voices.filter((v) => v.vanguarda_compra)}
          flex={1}
        />
        <Divider />
        <ResumoLadoOperacao
          lado="Venda"
          negocios={negocios.filter((n) => !n.vanguarda_compra)}
          voices={voices.filter((v) => !v.vanguarda_compra)}
          flex={1}
        />
      </VStack>
    </VStack>
  );
}
