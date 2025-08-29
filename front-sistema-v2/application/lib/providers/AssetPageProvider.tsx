"use client";

import { ModificationMap } from "@/app/_components/grid/ValidationGrid";
import {
  Dispatch,
  MutableRefObject,
  SetStateAction,
  createContext,
  useRef,
  useState,
} from "react";
import { Ativo, Evento } from "../types/api/iv/v1";

export enum DataFlow {
  ASSETS_DEFINE_EVENTS,
  EVENTS_DEFINE_ASSETS,
  SEPARATE,
}

export type AssetPageContextState = {
  dataFlow: DataFlow;
  setDataFlow: Dispatch<SetStateAction<DataFlow>>;
  clientSideAssets: Ativo[];
  setClientSideAssets: Dispatch<SetStateAction<Ativo[]>>;
  clientSideAssetsCellErrors: number;
  setClientSideAssetsCellErrors: Dispatch<SetStateAction<number>>;
  clientSideEvents: Evento[];
  setClientSideEvents: Dispatch<SetStateAction<Evento[]>>;
  clientSideEventsCellErrors: number;
  setClientSideEventsCellErrors: Dispatch<SetStateAction<number>>;
  clientSideNoDueDateErrors: Record<string, number>;
  setClientSideNoDueDateErrors: Dispatch<
    SetStateAction<Record<string, number>>
  >;
  clientSideDueDateIsNotLastDateErrors: string[];
  setClientSideDueDateIsNotLastDateErrors: Dispatch<SetStateAction<string[]>>;

  loadedAssetsRef: MutableRefObject<Record<string, Ativo>>;
  loadedEventsRef: MutableRefObject<Record<string, Evento>>;

  addedAssets: Ativo[];
  setAddedAssets: Dispatch<SetStateAction<Ativo[]>>;
  deletedAssets: Ativo[];
  setDeletedAssets: Dispatch<SetStateAction<Ativo[]>>;
  modifiedAssets: ModificationMap<Ativo>;
  setModifiedAssets: Dispatch<SetStateAction<ModificationMap<Ativo>>>;

  addedEvents: Evento[];
  setAddedEvents: Dispatch<SetStateAction<Evento[]>>;
  deletedEvents: Evento[];
  setDeletedEvents: Dispatch<SetStateAction<Evento[]>>;
  modifiedEvents: ModificationMap<Evento>;
  setModifiedEvents: Dispatch<SetStateAction<ModificationMap<Evento>>>;
};

export function AssetPageProvider({ children }: { children: React.ReactNode }) {
  const [dataFlow, setDataFlow] = useState<DataFlow>(
    DataFlow.ASSETS_DEFINE_EVENTS,
  );
  const [clientSideAssets, setClientSideAssets] = useState<Ativo[]>([]);
  const [clientSideAssetsCellErrors, setClientSideAssetsCellErrors] =
    useState(0);
  const [clientSideEvents, setClientSideEvents] = useState<Evento[]>([]);
  const [clientSideEventsCellErrors, setClientSideEventsCellErrors] =
    useState(0);
  const [clientSideNoDueDateErrors, setClientSideNoDueDateErrors] = useState<
    Record<string, number>
  >({});
  const [
    clientSideDueDateIsNotLastDateErrors,
    setClientSideDueDateIsNotLastDateErrors,
  ] = useState<string[]>([]);

  const loadedAssetsRef = useRef<Record<string, Ativo>>({});
  const loadedEventsRef = useRef<Record<string, Evento>>({});

  const [addedAssets, setAddedAssets] = useState<Ativo[]>([]);
  const [deletedAssets, setDeletedAssets] = useState<Ativo[]>([]);
  const [modifiedAssets, setModifiedAssets] = useState<ModificationMap<Ativo>>(
    {},
  );

  const [addedEvents, setAddedEvents] = useState<Evento[]>([]);
  const [deletedEvents, setDeletedEvents] = useState<Evento[]>([]);
  const [modifiedEvents, setModifiedEvents] = useState<ModificationMap<Evento>>(
    {},
  );

  return (
    <AssetPageContext.Provider
      value={{
        addedAssets,
        addedEvents,
        clientSideAssets,
        clientSideAssetsCellErrors,
        clientSideEvents,
        clientSideEventsCellErrors,
        clientSideNoDueDateErrors,
        clientSideDueDateIsNotLastDateErrors,
        loadedAssetsRef,
        loadedEventsRef,
        dataFlow,
        deletedAssets,
        deletedEvents,
        modifiedAssets,
        modifiedEvents,
        setAddedAssets,
        setAddedEvents,
        setClientSideAssets,
        setClientSideAssetsCellErrors,
        setClientSideEvents,
        setClientSideEventsCellErrors,
        setClientSideNoDueDateErrors,
        setClientSideDueDateIsNotLastDateErrors,
        setDataFlow,
        setDeletedAssets,
        setDeletedEvents,
        setModifiedAssets,
        setModifiedEvents,
      }}
    >
      {children}
    </AssetPageContext.Provider>
  );
}

const noop = () => {};

export const AssetPageContext = createContext<AssetPageContextState>({
  addedAssets: [],
  addedEvents: [],
  clientSideAssets: [],
  clientSideAssetsCellErrors: 0,
  clientSideEvents: [],
  clientSideEventsCellErrors: 0,
  clientSideNoDueDateErrors: {},
  clientSideDueDateIsNotLastDateErrors: [],
  loadedAssetsRef: { current: {} },
  loadedEventsRef: { current: {} },
  dataFlow: DataFlow.ASSETS_DEFINE_EVENTS,
  deletedAssets: [],
  deletedEvents: [],
  modifiedAssets: {},
  modifiedEvents: {},
  setAddedAssets: noop,
  setAddedEvents: noop,
  setClientSideAssets: noop,
  setClientSideAssetsCellErrors: noop,
  setClientSideEvents: noop,
  setClientSideEventsCellErrors: noop,
  setClientSideNoDueDateErrors: noop,
  setClientSideDueDateIsNotLastDateErrors: noop,
  setDataFlow: noop,
  setDeletedAssets: noop,
  setDeletedEvents: noop,
  setModifiedAssets: noop,
  setModifiedEvents: noop,
});
