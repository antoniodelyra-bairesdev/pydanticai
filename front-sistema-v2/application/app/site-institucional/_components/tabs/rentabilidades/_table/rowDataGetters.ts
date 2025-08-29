import type {
  Fundo,
  FundoPL,
  FundoRentabilidade,
  IndiceBenchmark,
  IndiceBenchmarkRentabilidade,
} from "@/lib/types/api/iv/v1";

export type FundoRowData = {
  fundo?: Fundo;
  rentabilidade?: FundoRentabilidade;
  pl?: FundoPL;
};

export type IndiceBenchmarkRowData = {
  indiceBenchmark?: IndiceBenchmark;
  rentabilidade?: IndiceBenchmarkRentabilidade;
};

export function getFundosRowData({
  fundos,
  fundosCotasRentabilidades,
  fundosPLsRentabilidades,
}: {
  fundos: Fundo[];
  fundosCotasRentabilidades: FundoRentabilidade[];
  fundosPLsRentabilidades: FundoPL[];
}): FundoRowData[] {
  const linhasFundo: FundoRowData[] = [];

  for (let i = 0; i < fundos.length; ++i) {
    const fundo = fundos[i];
    const fundoCotaRentabilidade = fundosCotasRentabilidades.find(
      (fundoCotaRentabilidade) => fundoCotaRentabilidade.fundo_id === fundo.id,
    );
    const fundoPLRentabilidade = fundosPLsRentabilidades.find(
      (fundoPLRentabilidade) => fundoPLRentabilidade.fundo_id === fundo.id,
    );

    const linha: FundoRowData = {
      fundo: fundo,
      rentabilidade: fundoCotaRentabilidade,
      pl: fundoPLRentabilidade,
    };

    linhasFundo.push(linha);
  }

  return linhasFundo;
}

export function getLinhasIndicesBenchmarkRowData({
  indicesBenchmark,
  indicesBenchmarkRentabilidades,
}: {
  indicesBenchmark: IndiceBenchmark[];
  indicesBenchmarkRentabilidades: IndiceBenchmarkRentabilidade[];
}): IndiceBenchmarkRowData[] {
  const linhasIndicesBenchmark: IndiceBenchmarkRowData[] = [];

  for (let i = 0; i < indicesBenchmark.length; ++i) {
    const indiceBenchmark = indicesBenchmark[i];
    const indiceBenchmarkRentabilidade = indicesBenchmarkRentabilidades.find(
      (indiceBenchmarkRentabilidade) =>
        indiceBenchmarkRentabilidade.indice_benchmark_id === indiceBenchmark.id,
    );

    const linha: IndiceBenchmarkRowData = {
      indiceBenchmark: indiceBenchmark,
      rentabilidade: indiceBenchmarkRentabilidade,
    };

    linhasIndicesBenchmark.push(linha);
  }

  return linhasIndicesBenchmark;
}
