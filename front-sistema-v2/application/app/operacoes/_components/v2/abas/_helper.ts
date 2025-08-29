import { BoletaClient } from "@/lib/providers/AlocacoesProvider";
import { ResultadoBuscaBoleta_Alocacao } from "@/lib/types/api/iv/operacoes/processamento";

export const selecionadasPertencentesA =
  (boletas: BoletaClient[]) =>
  (ss: Record<number, ResultadoBuscaBoleta_Alocacao>) => {
    const as = new Set(
      boletas.flatMap((b) =>
        b.boleta.alocacoes.flatMap((a) =>
          a.quebras.length ? a.quebras.map((q) => q.id) : [a.id],
        ),
      ),
    );
    const validas = Object.keys(ss).filter((sid) => as.has(Number(sid)));
    const novasSelecionadas: Record<number, ResultadoBuscaBoleta_Alocacao> = {};
    for (const valida of validas) {
      const key = Number(valida);
      novasSelecionadas[key] = ss[key];
    }
    return novasSelecionadas;
  };

export const selecao =
  (
    selecionada: boolean,
    alocacao: ResultadoBuscaBoleta_Alocacao,
    boleta: BoletaClient,
  ) =>
  (prevSelecionada: Record<number, ResultadoBuscaBoleta_Alocacao>) => {
    if (selecionada) {
      const als = boleta.boleta.alocacoes.flatMap((a) =>
        a.quebras.length ? a.quebras : [a],
      );
      const al = als.find((a) => a.id === alocacao?.id);
      if (al) {
        prevSelecionada[alocacao.id] = al;
      }
    } else {
      delete prevSelecionada[alocacao.id];
    }
    return { ...prevSelecionada };
  };
