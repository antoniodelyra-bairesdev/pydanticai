"use client";

import React, { useMemo } from "react";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  ChartData,
  ChartOptions,
  ChartEvent,
  ActiveElement,
  TooltipItem,
} from "chart.js";
import { Doughnut } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);

export type DonutProps = {
  dados: {
    rotulo: string;
    dados: { rotulo: string; valor: number }[];
  }[];
  selecionados: string[];
  setSelecionados: React.Dispatch<React.SetStateAction<string[]>>;
  formatador?: (contexto: TooltipItem<"doughnut">) => string[];
  cores?: {
    background: string[];
    border: string[];
  };
};

const magia = (n: number, m: number) =>
  n < m ? n : n - (m - 1) * Math.floor((n - 1) / (m - 1));

export default function Donut({
  dados,
  selecionados,
  setSelecionados,
  formatador,
  cores = {
    background: [
      "rgba(27, 49, 87, 0.7)",
      "rgba(13, 102, 150, 0.7)",
      "rgba(46, 150, 191, 0.7)",
      "rgba(0, 186, 219, 0.7)",
      "rgba(95, 187, 71, 0.7)",
      "rgba(230, 231, 232, 0.7)",
      "rgba(150, 59, 130, 0.7)",
      "rgba(240, 79, 110, 0.7)",
      "rgba(245, 140, 46, 0.7)",
      "rgba(255, 194, 79, 0.7)",
    ],
    border: [
      "rgba(27, 49, 87, 1)",
      "rgba(13, 102, 150, 1)",
      "rgba(46, 150, 191, 1)",
      "rgba(0, 186, 219, 1)",
      "rgba(95, 187, 71, 1)",
      "rgba(230, 231, 232, 1)",
      "rgba(150, 59, 130, 1)",
      "rgba(240, 79, 110, 1)",
      "rgba(245, 140, 46, 1)",
      "rgba(255, 194, 79, 1)",
    ],
  },
}: DonutProps) {
  // 1. Ordenar anéis por valor total original (maior primeiro)
  const aneisOrdenados = useMemo(() => {
    return dados
      .map((anel, index) => ({
        indexOriginal: index,
        rotulo: anel.rotulo,
        dados: anel.dados,
        totalOriginal: anel.dados.reduce(
          (total, item) => total + Math.abs(item.valor),
          0,
        ),
      }))
      .sort((a, b) => b.totalOriginal - a.totalOriginal);
  }, [dados]);

  // 2. Coleta todos os rótulos únicos
  const rotulosUnicos = useMemo(() => {
    const todosRotulos = dados.flatMap((anel) =>
      anel.dados.map((item) => item.rotulo),
    );
    return Array.from(new Set(todosRotulos));
  }, [dados]);

  // 3. Gerar cores baseadas nos rótulos únicos
  const coresPorRotulo = useMemo(() => {
    return rotulosUnicos.map((_, index) => ({
      background: cores.background[magia(index, cores.background.length)],
      border: cores.border[magia(index, cores.border.length)],
    }));
  }, [rotulosUnicos]);

  // 4. Construção dos datasets com espaçamento e ângulo proporcional
  const { datasets, totaisFiltrados } = useMemo(() => {
    // Calcular totais filtrados por anel (apenas selecionados)
    const totaisFiltrados = aneisOrdenados.map((anelOrdenado) => {
      return anelOrdenado.dados.reduce(
        (total, item) =>
          selecionados.includes(item.rotulo)
            ? total + Math.abs(item.valor)
            : total,
        0,
      );
    });

    // Encontrar o maior total filtrado
    const maxTotalFiltrado = Math.max(...totaisFiltrados, 1);

    const datasets = aneisOrdenados.map((anelOrdenado, index) => {
      // Calcular circunferência proporcional ao total filtrado
      const circunferencia = (totaisFiltrados[index] / maxTotalFiltrado) * 360;

      // Mapear valores para rótulos únicos
      const valores = rotulosUnicos.map((rotulo) => {
        const item = anelOrdenado.dados.find((i) => i.rotulo === rotulo);
        return selecionados.includes(rotulo) ? item?.valor || 0 : 0;
      });

      return {
        label: `Anel ${anelOrdenado.indexOriginal + 1}`,
        data: valores,
        backgroundColor: rotulosUnicos.map(
          (rotulo) =>
            coresPorRotulo[rotulosUnicos.indexOf(rotulo)]?.background || "#CCC",
        ),
        borderColor: rotulosUnicos.map(
          (rotulo) =>
            coresPorRotulo[rotulosUnicos.indexOf(rotulo)]?.border || "#999",
        ),
        borderWidth: 1,
        circumference: circunferencia,
      };
    });

    return { datasets, totaisFiltrados };
  }, [aneisOrdenados, rotulosUnicos, selecionados, coresPorRotulo]);

  const data: ChartData<"doughnut"> = {
    labels: rotulosUnicos,
    datasets: datasets,
  };

  // 5. Handlers de interação
  const handleLegendClick = (e: ChartEvent, legendItem: any) => {
    const rotulo = legendItem.text;
    setSelecionados((prev) =>
      prev.includes(rotulo)
        ? prev.filter((l) => l !== rotulo)
        : [...prev, rotulo],
    );
  };

  const handleChartClick = (
    e: ChartEvent,
    elements: ActiveElement[],
    chart: any,
  ) => {
    if (elements.length > 0) {
      const clickedIndex = elements[0].index;
      const clickedLabel = chart.data.labels[clickedIndex];
      const shift =
        e.native && "shiftKey" in e.native ? Boolean(e.native.shiftKey) : false;

      setSelecionados((prev) =>
        prev.includes(clickedLabel)
          ? prev.filter((l) =>
              shift ? l === clickedLabel : l !== clickedLabel,
            )
          : [...prev, clickedLabel],
      );
    }
  };

  // 6. Configurações do gráfico
  const options: ChartOptions<"doughnut"> = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: "50%",
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          boxWidth: 10,
          padding: 10,
          font: { size: 12 },
          usePointStyle: true,
          pointStyle: "circle",
          generateLabels: (chart) => {
            return rotulosUnicos.map((rotulo, index) => ({
              text: rotulo,
              fillStyle: coresPorRotulo[index]?.background,
              strokeStyle: coresPorRotulo[index]?.border,
              hidden: !selecionados.includes(rotulo),
              fontColor: selecionados.includes(rotulo) ? "#666" : "#999",
              textDecoration: selecionados.includes(rotulo)
                ? "none"
                : "line-through",
            }));
          },
        },
        onClick: handleLegendClick,
      },
      tooltip: {
        callbacks: {
          title: (context) =>
            aneisOrdenados[context[0].datasetIndex]?.rotulo ?? "Sem rótulo",
          label: (context) => {
            const label = context.label || "";
            const valor = Number(context.raw);
            const anelIndex = context.datasetIndex;
            const totalAnel = totaisFiltrados[anelIndex] || 1;
            const percentual =
              totalAnel > 0 ? ((valor / totalAnel) * 100).toFixed(0) : "0";

            return (
              formatador?.(context) ?? [
                `${label}:`,
                `Valor: R$ ${valor.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
                `Percentual: ${percentual}%`,
              ]
            );
          },
        },
      },
    },
    onClick: handleChartClick,
  };

  return <Doughnut data={data} options={options} />;
}
