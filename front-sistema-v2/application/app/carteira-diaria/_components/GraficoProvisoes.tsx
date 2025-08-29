import FluxoCaixa from "../../_components/graficos/FluxoCaixa";
import { Posicao } from "@/lib/types/leitor-carteiras-fundos/types";

export type GraficoProvisoesProps = {
  posicoes: Posicao[];
  focoPosicao: number;
  detalharFluxoCaixa?: boolean;
};

export default function GraficoProvisoes({
  posicoes,
  focoPosicao,
  detalharFluxoCaixa,
}: GraficoProvisoesProps) {
  const p = posicoes[focoPosicao];
  const pagar = p
    ? (p.produto_investimento?.financeiro.valores_a_pagar.map((v) => ({
        date: new Date(`${v.data_pagamento}T00:00:00`),
        label: v.nome,
        value: -Number(v.valor),
      })) ?? [])
    : [];
  const receber = p
    ? (p.produto_investimento?.financeiro.valores_a_receber.map((v) => ({
        date: new Date(`${v.data_pagamento}T00:00:00`),
        label: v.nome,
        value: Number(v.valor),
      })) ?? [])
    : [];
  return (
    <FluxoCaixa
      labelMode={detalharFluxoCaixa ? "INDIVIDUAL" : "AGREGADO"}
      dados={[...pagar, ...receber]}
    />
  );
}
