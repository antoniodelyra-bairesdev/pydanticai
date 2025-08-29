"use client";

import {
  Dispatch,
  ReactNode,
  SetStateAction,
  createContext,
  useEffect,
  useState,
} from "react";
import {
  Alocacao,
  MercadoEnum,
  ResultadoBuscaBoleta,
  ResultadoBuscaBoleta_Alocacao,
  TipoOperacaoEnum,
  TipoTituloPrivadoEnum,
} from "../types/api/iv/operacoes/processamento";

export type BoletaClient = {
  boleta: ResultadoBuscaBoleta;
  client_id: number;
};

export type AlocacaoComInfosDaBoleta = ResultadoBuscaBoleta_Alocacao & {
  tipo_ativo_id: TipoTituloPrivadoEnum;
  natureza_operacao_id: TipoOperacaoEnum;
  mercado_negociado_id: MercadoEnum;
};

export function AlocacoesProvider({ children }: { children: ReactNode }) {
  const [boletas, setBoletas] = useState<BoletaClient[]>([]);
  const [alocacaoDetalhes, setAlocacaoDetalhes] =
    useState<AlocacaoComInfosDaBoleta | null>(null);

  useEffect(() => {
    setAlocacaoDetalhes((ad) => {
      if (!ad) return null;
      outer: for (const {
        boleta: {
          alocacoes,
          tipo_ativo_id,
          mercado_negociado_id,
          natureza_operacao_id,
        },
      } of boletas) {
        for (const alocacao of alocacoes) {
          if (alocacao.id === ad?.id) {
            ad = {
              ...alocacao,
              tipo_ativo_id,
              mercado_negociado_id,
              natureza_operacao_id,
            };
            break outer;
          }
        }
      }
      return { ...ad };
    });
  }, [boletas]);

  return (
    <AlocacoesContext.Provider
      value={{ boletas, setBoletas, alocacaoDetalhes, setAlocacaoDetalhes }}
    >
      {children}
    </AlocacoesContext.Provider>
  );
}

type Setter<T> = Dispatch<SetStateAction<T>>;

export const AlocacoesContext = createContext<{
  boletas: BoletaClient[];
  setBoletas: Setter<BoletaClient[]>;
  alocacaoDetalhes: AlocacaoComInfosDaBoleta | null;
  setAlocacaoDetalhes: Setter<AlocacaoComInfosDaBoleta | null>;
}>({
  boletas: [],
  setBoletas: () => {},
  alocacaoDetalhes: null,
  setAlocacaoDetalhes: () => {},
});
