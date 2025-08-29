import React, { useState, useMemo } from "react";
import {
  Chart as ChartJS,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from "chart.js";
import { Chart, ChartProps } from "react-chartjs-2";
import dayjs from "dayjs";
import "chartjs-adapter-dayjs-4";
import annotationPlugin from "chartjs-plugin-annotation";
import { strHSL } from "@/lib/util/string";

ChartJS.register(
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
  annotationPlugin,
);

interface DataPoint {
  label: string;
  value: number;
  date: Date;
}

interface TemporalChartProps {
  dados: DataPoint[];

  showNetByDate?: boolean;
  setShowNetByDate?: React.Dispatch<React.SetStateAction<boolean>>;

  showAggregatedValues?: boolean;
  setShowAggregatedValues?: React.Dispatch<React.SetStateAction<boolean>>;

  labelMode?: "AGREGADO" | "INDIVIDUAL";
  setLabelMode?: React.Dispatch<
    React.SetStateAction<"AGREGADO" | "INDIVIDUAL">
  >;
}

const lerp = (start: number, end: number, t: number) =>
  start + (end - start) * t;

export default function Net({
  dados,
  showNetByDate = true,
  setShowNetByDate = () => {},
  showAggregatedValues = true,
  setShowAggregatedValues = () => {},
  labelMode = "AGREGADO",
  setLabelMode = () => {},
}: TemporalChartProps) {
  const labelColors = useMemo<Record<string, string>>(() => {
    const uniqueLabels = Array.from(new Set(dados.map((item) => item.label)));
    const colors: Record<string, string> = {};

    uniqueLabels.forEach((label) => {
      const [h, s, l] = strHSL(label);
      colors[label] = `hsla(${lerp(45, 240, h / 360)},${s}%,${l}%,0.7)`;
    });

    return colors;
  }, [dados]);

  // Process data
  const { dates, groupedData, aggregatedValues, uniqueLabels } = useMemo(() => {
    // Sort data by date
    const sortedData = [...dados].sort(
      (a, b) => a.date.getTime() - b.date.getTime(),
    );

    // Get unique dates
    const dates = Array.from(
      new Set(sortedData.map((item) => item.date.getTime())),
    )
      .map((time) => new Date(time))
      .sort((a, b) => a.getTime() - b.getTime());

    // Group data by date
    const groupedData = new Map<number, DataPoint[]>();
    sortedData.forEach((item) => {
      const time = item.date.getTime();
      if (!groupedData.has(time)) {
        groupedData.set(time, []);
      }
      groupedData.get(time)?.push(item);
    });

    // Get unique labels
    const uniqueLabels = Array.from(
      new Set(sortedData.map((item) => item.label)),
    );

    // Calculate aggregated values
    const aggregatedValues: {
      date: Date;
      sum: number;
      cumulativeSum: number;
    }[] = [];
    let cumulativeSum = 0;

    dates.forEach((date) => {
      const time = date.getTime();
      const items = groupedData.get(time) || [];
      const sum = items.reduce((acc, curr) => acc + curr.value, 0);
      cumulativeSum += sum;

      aggregatedValues.push({
        date,
        sum,
        cumulativeSum,
      });
    });

    return { dates, groupedData, aggregatedValues, uniqueLabels };
  }, [dados]);

  // Estado para rastrear a visibilidade de cada dataset
  const [datasetVisibility, setDatasetVisibility] = useState<
    Record<string, boolean>
  >({
    "Valores a receber": true,
    "Valores a pagar": true,
    Diferença: true,
    Acumulado: true,
    ...Object.fromEntries(uniqueLabels.map((label) => [label, true])),
  });

  // Calcular min e max baseado apenas nos dados visíveis
  const { min, max } = useMemo(() => {
    const allVisibleValues: number[] = [];

    // Coletar valores de barras visíveis
    if (showNetByDate) {
      if (labelMode === "AGREGADO") {
        // Valores a receber (se visível)
        if (datasetVisibility["Valores a receber"]) {
          dates.forEach((date) => {
            const items = groupedData.get(date.getTime()) || [];
            const positiveSum = items.reduce(
              (sum, item) => sum + (item.value > 0 ? item.value : 0),
              0,
            );
            if (positiveSum > 0) allVisibleValues.push(positiveSum);
          });
        }

        // Valores a pagar (se visível)
        if (datasetVisibility["Valores a pagar"]) {
          dates.forEach((date) => {
            const items = groupedData.get(date.getTime()) || [];
            const negativeSum = items.reduce(
              (sum, item) => sum + (item.value < 0 ? item.value : 0),
              0,
            );
            if (negativeSum < 0) allVisibleValues.push(negativeSum);
          });
        }

        // Diferença (se visível)
        if (datasetVisibility["Diferença"]) {
          dates.forEach((date) => {
            const items = groupedData.get(date.getTime()) || [];
            const net = items.reduce((sum, item) => sum + item.value, 0);
            allVisibleValues.push(net);
          });
        }
      } else {
        // Modo INDIVIDUAL
        uniqueLabels.forEach((label) => {
          if (datasetVisibility[label]) {
            dates.forEach((date) => {
              const items = groupedData.get(date.getTime()) || [];
              const matchingItems = items.filter(
                (item) => item.label === label,
              );
              if (matchingItems.length) {
                const sum = matchingItems.reduce(
                  (soma, valor) => soma + valor.value,
                  0,
                );
                allVisibleValues.push(sum);
              }
            });
          }
        });
      }
    }

    // Coletar valores acumulados se visíveis
    if (showAggregatedValues && datasetVisibility["Acumulado"]) {
      aggregatedValues.forEach((item) => {
        allVisibleValues.push(item.cumulativeSum);
      });
    }

    // Calcular min e max apenas com dados visíveis
    if (allVisibleValues.length === 0) {
      return { min: 0, max: 1 };
    }

    const minVisible = Math.min(...allVisibleValues);
    const maxVisible = Math.max(...allVisibleValues);
    const margin = Math.abs(maxVisible - minVisible) * 0.1;

    return {
      min: minVisible - margin,
      max: maxVisible + margin,
    };
  }, [
    dates,
    groupedData,
    aggregatedValues,
    showNetByDate,
    showAggregatedValues,
    labelMode,
    uniqueLabels,
    datasetVisibility,
  ]);

  // Handler para atualizar a visibilidade ao clicar na legenda
  const handleLegendClick = (e: any, legendItem: any) => {
    const label = legendItem.text;
    setDatasetVisibility((prev) => ({
      ...prev,
      [label]: !prev[label],
    }));
  };

  // Prepare chart data - SEMPRE incluir todos os datasets
  const chartData = useMemo(() => {
    if (labelMode === "AGREGADO") {
      return {
        labels: dates.map((date) => date),
        datasets: [
          // Valores a receber (sempre presente)
          {
            type: "bar" as const,
            label: "Valores a receber",
            data: dates.map((date) => {
              const items = groupedData.get(date.getTime()) || [];
              const positiveSum = items.reduce(
                (sum, item) => sum + (item.value > 0 ? item.value : 0),
                0,
              );
              return positiveSum > 0 ? positiveSum : null;
            }),
            backgroundColor: "rgba(95, 187, 71, 0.3)",
            borderColor: "rgba(95, 187, 71, 0.6)",
            borderWidth: 1,
            stack: "stack1",
            grouped: false,
            categoryPercentage: 0.75,
            order: 0,
            hidden: !datasetVisibility["Valores a receber"],
          },

          // Valores a pagar (sempre presente)
          {
            type: "bar" as const,
            label: "Valores a pagar",
            data: dates.map((date) => {
              const items = groupedData.get(date.getTime()) || [];
              const negativeSum = items.reduce(
                (sum, item) => sum + (item.value < 0 ? item.value : 0),
                0,
              );
              return negativeSum < 0 ? negativeSum : null;
            }),
            backgroundColor: "rgba(240, 79, 110, 0.3)",
            borderColor: "rgba(240, 79, 110, 0.6)",
            borderWidth: 1,
            stack: "stack1",
            grouped: false,
            categoryPercentage: 0.75,
            order: 0,
            hidden: !datasetVisibility["Valores a pagar"],
          },

          // Diferença (sempre presente)
          {
            type: "bar" as const,
            label: "Diferença",
            data: dates.map((date) => {
              const items = groupedData.get(date.getTime()) || [];
              return items.reduce((sum, item) => sum + item.value, 0);
            }),
            backgroundColor: "rgba(46, 150, 191, 1)",
            borderColor: "rgba(46, 150, 191, 1)",
            borderWidth: 1,
            grouped: false,
            categoryPercentage: 0.5,
            order: -1,
            hidden: !datasetVisibility["Diferença"],
          },

          // Acumulado (sempre presente)
          {
            type: "line" as const,
            label: "Acumulado",
            data: aggregatedValues.map((item) => item.cumulativeSum),
            backgroundColor: "rgba(13, 102, 150, 1)",
            borderColor: "rgba(13, 102, 150, 1)",
            borderWidth: 2,
            fill: false,
            tension: 0.1,
            pointRadius: 5,
            pointHoverRadius: 7,
            yAxisID: "y1",
            order: -2,
            hidden: !datasetVisibility["Acumulado"],
          },
        ],
      };
    } else {
      // Individual mode
      return {
        labels: dates.map((date) => date),
        datasets: [
          // Barras individuais para cada label (sempre presentes)
          ...uniqueLabels.map((label) => ({
            type: "bar" as const,
            label: label,
            data: dates.map((date) => {
              const items = groupedData.get(date.getTime()) || [];
              const matchingItems = items.filter(
                (item) => item.label === label,
              );
              if (!matchingItems.length) return null;
              return matchingItems.reduce(
                (soma, valor) => soma + valor.value,
                0,
              );
            }),
            backgroundColor: labelColors[label] || "rgba(169, 169, 169, 0.6)",
            borderColor: labelColors[label]
              ? labelColors[label].replace("0.7", "1")
              : "rgba(169, 169, 169, 1)",
            borderWidth: 1,
            stack: "stack1",
            hidden: !datasetVisibility[label],
          })),

          // Acumulado (sempre presente)
          {
            type: "line" as const,
            label: "Acumulado",
            data: aggregatedValues.map((item) => item.cumulativeSum),
            backgroundColor: "rgba(13, 102, 150, 1)",
            borderColor: "rgba(13, 102, 150, 1)",
            borderWidth: 2,
            fill: false,
            tension: 0.1,
            pointRadius: 5,
            pointHoverRadius: 7,
            yAxisID: "y1",
            order: -2,
            hidden: !datasetVisibility["Acumulado"],
          },
        ],
      };
    }
  }, [
    dates,
    groupedData,
    aggregatedValues,
    showNetByDate,
    showAggregatedValues,
    labelMode,
    uniqueLabels,
    labelColors,
    datasetVisibility,
  ]);

  // Chart options com geração customizada de legendas
  const options: ChartProps<
    "bar" | "line",
    (number | null)[],
    Date
  >["options"] = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        type: "category" as const,
        labels: dates.map((date) => dayjs(date).format("DD/MM/YYYY")),
      },
      y: {
        title: {
          display: true,
          text: "Valor (R$)",
        },
        beginAtZero: false,
        min,
        max,
      },
      y1: {
        position: "right" as const,
        title: {
          display: true,
          text: "Acumulado",
        },
        beginAtZero: false,
        min,
        max,
        grid: {
          drawOnChartArea: false,
        },
      },
    },
    plugins: {
      tooltip: {
        callbacks: {
          title: (context: any) => {
            const date = new Date(context[0].parsed.x);
            return dayjs(date).format("MMM D, YYYY");
          },
        },
      },
      legend: {
        onClick: handleLegendClick,
        labels: {
          generateLabels: (chart) => {
            const visibility = datasetVisibility;
            return chart.data.datasets.map((dataset) => {
              const isHidden = dataset.hidden ?? false;
              return {
                text: dataset.label as string,
                fillStyle:
                  dataset.type === "line"
                    ? (dataset.borderColor as string)
                    : (dataset.backgroundColor as string),
                strokeStyle: dataset.borderColor as string,
                fontColor: isHidden ? "#999" : "#666",
                // textDecoration: isHidden ? "line-through" : "none",
              };
            });
          },
        },
      },
      annotation: {
        annotations: {
          yZeroLine: {
            type: "line",
            yMin: 0,
            yMax: 0,
            borderColor: "rgba(175, 175, 175, 0.7)", // Cor cinza
            borderWidth: 1,
            borderDash: [5, 5], // Linha tracejada (opcional)
          },
        },
      },
    },
  };

  return <Chart type="bar" data={chartData} options={options} />;
}
