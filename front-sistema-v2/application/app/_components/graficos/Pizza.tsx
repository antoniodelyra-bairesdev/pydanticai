'use client'

import React, { useMemo, useState } from 'react';
import { Pie } from 'react-chartjs-2';
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
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

export type PizzaProps = {
    dados: {
        rotulo: string
        valor: number
    }[],
    selecionados: string[]
    setSelecionados: React.Dispatch<React.SetStateAction<string[]>>
    formatador?: (contexto: TooltipItem<"pie">) => string[]
}

const cores = {
    background: [
        'rgba(27, 49, 87, 0.7)',
        'rgba(13, 102, 150, 0.7)',
        'rgba(46, 150, 191, 0.7)',
        'rgba(0, 186, 219, 0.7)',
        'rgba(95, 187, 71, 0.7)',
        'rgba(230, 231, 232, 0.7)',
        'rgba(150, 59, 130, 0.7)',
        'rgba(240, 79, 110, 0.7)',
        'rgba(245, 140, 46, 0.7)',
        'rgba(255, 194, 79, 0.7)',
    ],
    border: [
        'rgba(27, 49, 87, 1)',
        'rgba(13, 102, 150, 1)',
        'rgba(46, 150, 191, 1)',
        'rgba(0, 186, 219, 1)',
        'rgba(95, 187, 71, 1)',
        'rgba(230, 231, 232, 1)',
        'rgba(150, 59, 130, 1)',
        'rgba(240, 79, 110, 1)',
        'rgba(245, 140, 46, 1)',
        'rgba(255, 194, 79, 1)',
    ]
}

const magia = (n:number,m:number) => n < m ? n : n - (m-1) * Math.floor((n-1)/(m-1))

export default function Pizza({ dados, selecionados, setSelecionados, formatador }: PizzaProps) {
    const rotulosOriginais = useMemo(() => dados.map(d => d.rotulo), [dados]);
    const bgsOriginais = useMemo(() => dados.map((_,i) => cores.background[magia(i,cores.background.length)]), [dados]);
    const bordasOriginais = useMemo(() => dados.map((_,i) => cores.border[magia(i,cores.border.length)]), [dados]);

    const dadosOriginais = useMemo(() => dados.map(d => d.valor), [dados]);
    const total = useMemo(() => dados.reduce((soma, dado) => soma + dado.valor, 0), [dados])
    
 
    const dadosFiltrados = useMemo(() => dadosOriginais.filter((_, index) => 
        selecionados.includes(rotulosOriginais[index])
    ), [dados, selecionados]);

    const rotulosFiltrados = useMemo(() => rotulosOriginais.filter(label => 
        selecionados.includes(label)
    ), [dados, selecionados]);

    const bgFiltrados = useMemo(() => bgsOriginais.filter((_, index) => 
        selecionados.includes(rotulosOriginais[index])
    ), [dados, selecionados]);

    const bordasFiltradas = useMemo(() => bordasOriginais.filter((_, index) => 
        selecionados.includes(rotulosOriginais[index])
    ), [dados, selecionados]);

    const data: ChartData<'pie'> = {
        labels: rotulosFiltrados,
        datasets: [
            {
                label: 'Sample Data',
                data: dadosFiltrados,
                backgroundColor: bgFiltrados,
                borderColor: bordasFiltradas,
                borderWidth: 1,
            },
        ],
    };

    const handleLegendClick = (e: ChartEvent, legendItem: any) => {
    const rotulo = legendItem.text;
        setSelecionados(prev => 
            prev.includes(rotulo) 
                ? prev.filter(l => l !== rotulo) 
                : [...prev, rotulo]
        );
    };

    const handleChartClick = (e: ChartEvent, elements: ActiveElement[], chart: any) => {
        if (elements.length > 0) {
            const clickedIndex = elements[0].index;
            const clickedLabel = chart.data.labels[clickedIndex];
            const shift = (e.native && ('shiftKey' in e.native))
                ? Boolean(e.native.shiftKey)
                : false

            setSelecionados(prev => 
                prev.includes(clickedLabel) 
                    ? prev.filter(l => shift ? l === clickedLabel : l !== clickedLabel) 
                    : [...prev, clickedLabel]
            );
        }
    };

    const options: ChartOptions<'pie'> = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    boxWidth: 10,
                    padding: 10,
                    font: {
                        size: 12,
                    },
                    usePointStyle: true,
                    pointStyle: 'circle',
                    generateLabels: () => {
                        return rotulosOriginais.map((label, index) => ({
                            text: label,
                            fillStyle: cores.background[magia(index, cores.background.length)],
                            strokeStyle: cores.border[magia(index,cores.border.length)],
                            hidden: !selecionados.includes(label),
                            fontColor: selecionados.includes(label) ? '#666' : '#999',
                            textDecoration: selecionados.includes(label) ? 'none' : 'line-through',
                        }));
                    },
                },
                onClick: handleLegendClick,
            },
            tooltip: {
                callbacks: {
                    label: (context) => {
                        const label = context.label || '';
                        const valor = Number(context.raw);
                        const percentual = ((valor / total) * 100).toFixed(0);
                        return formatador?.(context) ?? [
                            `${label}:`,
                            `Valor: ${valor}`,
                            `Percentual: ${percentual}%`
                        ];
                    },
                    afterLabel: () => ''
                }
            }
        },
        layout: {
            padding: {
                right: 20,
            },
        },
        onClick: handleChartClick
    };

    return <Pie data={data} options={options} />
}