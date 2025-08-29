import React, { useEffect, useMemo, useRef } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
  Title,
} from "chart.js";
import { Chart } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
  Title,
);

interface DataPoint {
  nome: string;
  valor: number;
}

interface BarrasHorizontaisProps {
  datasets: { nomeDataset: string; dados: DataPoint[] }[];
  mainDatasetIndex: number;
  maxHeight?: number;
}

export default function BarrasHorizontais({
  datasets,
  mainDatasetIndex,
  maxHeight = 400,
}: BarrasHorizontaisProps) {
  if (!datasets.length) return <></>;
  const chartRef = useRef<any>(null);

  // Processa os dados para o formato necessário
  const { labels, chartDatasets, categoryHeights } = useMemo(() => {
    // Processa o NOVO dataset principal
    const mainDataset = datasets[mainDatasetIndex];

    // Agrupa e soma valores por nome no NOVO dataset principal
    const groupedMainData = mainDataset.dados.reduce(
      (acc, item) => {
        acc[item.nome] = (acc[item.nome] || 0) + item.valor;
        return acc;
      },
      {} as Record<string, number>,
    );

    // Ordena do maior para o menor baseado no NOVO dataset principal
    const sortedEntries = Object.entries(groupedMainData).sort(
      (a, b) => b[1] - a[1],
    );

    const labels = sortedEntries.map(([nome]) => nome);

    // Prepara todos os datasets para o gráfico
    const chartDatasets = datasets.map((dataset, index) => {
      const dataByLabel = dataset.dados.reduce(
        (acc, item) => {
          acc[item.nome] = (acc[item.nome] || 0) + item.valor;
          return acc;
        },
        {} as Record<string, number>,
      );

      const data = labels.map((label) => dataByLabel[label] || 0);

      return {
        label: dataset.nomeDataset,
        data,
        backgroundColor:
          index === mainDatasetIndex
            ? "rgba(54, 162, 235, 0.8)"
            : `hsl(${index * 60}, 70%, 60%)`,
        borderColor:
          index === mainDatasetIndex
            ? "rgba(54, 162, 235, 1)"
            : `hsl(${index * 60}, 70%, 40%)`,
        borderWidth: 1,
        barThickness: index === mainDatasetIndex ? 20 : 6, // Ajusta dinamicamente
        type: "bar" as const,
        datasetName: dataset.nomeDataset,
        order: dataset === mainDataset ? 0 : index + 1,
        stack:
          "stack" +
          (dataset === mainDataset
            ? "000"
            : String(index + 1).padStart(3, "0")),
      };
    });

    // Calcula altura necessária para cada categoria
    const categoryHeights = 30 + (datasets.length - 1) * 10;

    return {
      labels,
      categoryHeights,
      chartDatasets,
    };
  }, [datasets, mainDatasetIndex]);

  const data = {
    labels,
    datasets: chartDatasets,
  };

  // Configurações do gráfico
  const options = {
    indexAxis: "y" as const,
    responsive: true,
    maintainAspectRatio: false,

    // Configurações melhoradas de interação
    interaction: {
      mode: "index" as const, // Mostra tooltip para todos os itens na mesma linha
      intersect: false, // Ativa mesmo quando não está diretamente sobre o elemento
    },

    plugins: {
      // Configurações da legenda
      legend: {
        position: "bottom" as const, // Move a legenda para baixo
        align: "start" as const, // Alinha à esquerda
        labels: {
          boxWidth: 12,
          usePointStyle: true,
          font: {
            size: 10, // Tamanho de fonte reduzido
          },
          padding: 8,
        },
        // Configura para exibição vertical
        rtl: false,
        fullSize: true,
        maxHeight: 200,
      },

      //   title: {
      //     display: true,
      //     text: "Comparação de Datasets",
      //     font: {
      //       size: 16,
      //     },
      //   },

      // Configurações melhoradas do tooltip
      tooltip: {
        callbacks: {
          title: (context: any) => {
            return context[0].label;
          },
          label: (context: any) => {
            const datasetName = String(
              context.dataset.datasetName || context.dataset.label || "",
            );
            const dsnPequeno = `${datasetName.substring(0, 30)}${datasetName.length > 30 ? "..." : ""}`;
            return dsnPequeno;
          },
          afterLabel: (context: any) => {
            return `Valor: ${context.raw.toLocaleString()}`;
          },
        },
        displayColors: true,
        backgroundColor: "rgba(0, 0, 0, 0.75)",
        titleColor: "#FFF",
        bodyColor: "#FFF",
        borderColor: "#ddd",
        borderWidth: 1,
        padding: 12,
        bodyFont: {
          size: 12,
        },
        titleFont: {
          size: 12,
        },
        // Posicionamento inteligente do tooltip
        position: "nearest" as const,
        caretPadding: 10,
        caretSize: 8,
        cornerRadius: 6,
        // Melhor comportamento para barras pequenas
        axis: "y" as const,
        xAlign: "center" as const,
        yAlign: "top" as const,
      },
    },

    scales: {
      x: {
        beginAtZero: true,
        title: {
          display: true,
          text: "Valor",
          font: {
            weight: "bold" as const,
          },
        },
        grid: {
          color: "rgba(0, 0, 0, 0.05)",
        },
      },
      y: {
        // title: {
        //   display: true,
        //   text: "Categoria",
        //   font: {
        //     weight: "bold" as const,
        //   },
        // },
        grid: {
          color: "rgba(0, 0, 0, 0.05)",
        },
      },
    },

    datasets: {
      bar: {
        categoryPercentage: 0.8,
        barPercentage: 0.9,
      },
    },
  };

  // Efeito para melhorar a detecção de tooltip para barras pequenas
  useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;

    const canvas = chart.canvas;

    const handleMouseMove = (e: MouseEvent) => {
      if (!chartRef.current) return;

      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      // Atualiza o estado de hover do gráfico
      chartRef.current.update();
    };

    canvas.addEventListener("mousemove", handleMouseMove);

    return () => {
      canvas.removeEventListener("mousemove", handleMouseMove);
    };
  }, []);

  return (
    <div
      style={{
        maxHeight: `${maxHeight}px`,
        overflowY:
          maxHeight && labels.length * categoryHeights > maxHeight
            ? "auto"
            : "hidden",
        width: "100%",
        // border: "1px solid #e0e0e0",
        // borderRadius: "8px",
        // padding: "16px",
        // backgroundColor: "#fff",
        // boxShadow: "0 2px 10px rgba(0, 0, 0, 0.05)",
      }}
    >
      <div
        style={{
          height: `${labels.length * categoryHeights}px`,
          minHeight: "400px",
          width: "100%",
          position: "relative",
        }}
      >
        <Chart ref={chartRef} type="bar" data={data} options={options} />
      </div>

      {/* Legenda adicional abaixo do gráfico */}
      {/* <div
        style={{
          marginTop: "20px",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          fontSize: "10px",
          lineHeight: "1.6",
        }}
      >
        {chartDatasets.map((dataset, index) => (
          <div
            key={index}
            style={{
              display: "flex",
              alignItems: "center",
              marginBottom: "4px",
              width: "100%",
              textAlign: "left",
            }}
          >
            <div
              style={{
                width: "12px",
                height: "12px",
                backgroundColor: dataset.backgroundColor as string,
                border: `1px solid ${dataset.borderColor as string}`,
                marginRight: "8px",
                borderRadius: "2px",
              }}
            ></div>
            <span>{dataset.label}</span>
          </div>
        ))}
      </div> */}
    </div>
  );
}
