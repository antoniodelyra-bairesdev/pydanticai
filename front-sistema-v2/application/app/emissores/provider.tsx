"use client";

import {
  AnalistaCredito,
  Emissor,
  EmissorGrupo,
  EmissorSetor,
} from "@/lib/types/api/iv/v1";
import {
  createContext,
  useState,
  Dispatch,
  SetStateAction,
  ReactNode,
  useContext,
} from "react";

export type EmissoresPageProviderType = {
  analistas: Record<string, AnalistaCredito>;
  setAnalistas: Dispatch<SetStateAction<Record<string, AnalistaCredito>>>;
  grupos: Record<string, EmissorGrupo>;
  setGrupos: Dispatch<SetStateAction<Record<string, EmissorGrupo>>>;
  setores: Record<string, EmissorSetor>;
  setSetores: Dispatch<SetStateAction<Record<string, EmissorSetor>>>;
};

export function EmissoresPageProvider({ children }: { children: ReactNode }) {
  const [setores, setSetores] = useState<Record<string, EmissorSetor>>({});
  const [grupos, setGrupos] = useState<Record<string, EmissorGrupo>>({});
  const [analistas, setAnalistas] = useState<Record<string, AnalistaCredito>>(
    {},
  );

  return (
    <EmissoresPageContext.Provider
      value={{
        analistas,
        setAnalistas,
        grupos,
        setGrupos,
        setores,
        setSetores,
      }}
    >
      {children}
    </EmissoresPageContext.Provider>
  );
}

const noop = () => {};

export const EmissoresPageContext = createContext({
  analistas: {},
  setAnalistas: noop,
  grupos: {},
  setGrupos: noop,
  setores: {},
  setSetores: noop,
} as EmissoresPageProviderType);

export const useEmissoresPageData = () => useContext(EmissoresPageContext);
