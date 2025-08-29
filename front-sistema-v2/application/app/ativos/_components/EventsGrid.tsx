import ValidationGrid, {
  ModificationMap,
  ValidationGridColDef,
  ValidationGridMethods,
} from "@/app/_components/grid/ValidationGrid";
import {
  dateColDef,
  listColDef,
  moneyColDef,
  percentageColDef,
} from "@/app/_components/grid/colDefs";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { getColorHex } from "@/app/theme";
import { useColors, useHTTP } from "@/lib/hooks";
import { AssetPageContext, DataFlow } from "@/lib/providers/AssetPageProvider";
import { Ativo, Evento } from "@/lib/types/api/iv/v1";
import {
  dateFilter,
  dateFilterSerialize,
  inOrNotInSerialize,
  listFilter,
  numberFilter,
  numberFilterSerialize,
  percentageFilterSerialize,
} from "@/lib/util/grid";
import { strFromIndice } from "@/lib/util/misc";
import {
  SingularPluralMapping,
  pluralOrSingular,
  strCSSColor,
} from "@/lib/util/string";
import { inList, required } from "@/lib/util/validation";
import { HStack, Tag, Text, useDisclosure } from "@chakra-ui/react";
import {
  GridApi,
  ICellRendererParams,
  IRowNode,
  IServerSideDatasource,
} from "ag-grid-community";
import {
  MutableRefObject,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import InserirLinhasModal from "./InserirLinhasModal";

export type EventsGridProps = {
  colDefRef: MutableRefObject<ValidationGridColDef[]>;
  codigos: string[];
  tipos: string[];
  tiposSuportados: string[];
  editable: boolean;
  methodsRef: MutableRefObject<ValidationGridMethods<Evento> | undefined>;
  modalOpenRef: MutableRefObject<(() => void) | null>;

  onNewEventsFetched?: (eventos: Evento[], total: number) => void;
};

export default function EventsGrid({
  colDefRef,
  codigos,
  editable,
  tipos,
  tiposSuportados,
  methodsRef,
  modalOpenRef,
  onNewEventsFetched,
}: EventsGridProps) {
  const {
    dataFlow,

    setClientSideEventsCellErrors,
    setClientSideNoDueDateErrors,
    setClientSideDueDateIsNotLastDateErrors,

    loadedAssetsRef,
    loadedEventsRef,

    setAddedEvents,
    setModifiedEvents,
    deletedEvents,
    setDeletedEvents,

    clientSideEvents,
    setClientSideAssets,
  } = useContext(AssetPageContext);

  const gridApiRef = useRef<GridApi | null>(null);
  const addedRef = useRef<Evento[]>([]);
  const deleteNextFrameRef = useRef<string[]>([]);
  const [deleteNextFrame, setDeleteNextFrame] = useState<string[]>([]);
  const insertNextFrameRef = useRef<{ id: number; ativo_codigo: string }[]>([]);
  const [insertNextFrame, setInsertNextFrame] = useState<
    { id: number; ativo_codigo: string }[]
  >([]);

  const ativosRef = useRef<Record<string, Evento[]>>({});

  useEffect(() => {
    const methods = methodsRef.current;
    if (!methods) return;
    methods.deleteRows(deleteNextFrame);
    deleteNextFrameRef.current = [];
  }, [deleteNextFrame]);

  useEffect(() => {
    const methods = methodsRef.current;
    if (!methods) return;
    methods.insertRows(insertNextFrame);
    insertNextFrameRef.current = [];
  }, [insertNextFrame]);

  const modifiedRef = useRef<ModificationMap<Evento>>({});

  const fluxoColumnDefs = useMemo<ValidationGridColDef[]>(
    () => [
      {
        headerName: "Papel Relacionado",
        field: "ativo_codigo",
        pinned: true,
        resizable: false,
        valueSetter(params) {
          const { data, newValue, oldValue, node } = params;
          const eventoAdicionado = addedRef.current.find(
            (e) => e.id === data.id,
          );
          if (eventoAdicionado) {
            data.ativo_codigo = newValue;
            return true;
          }
          if (newValue === oldValue) {
            data.ativo_codigo = newValue;
            return true;
          }

          const methods = methodsRef.current;
          if (!methods) return false;

          deleteNextFrameRef.current.push(data.id);
          insertNextFrameRef.current.push({
            ...data,
            id: Math.random(),
            ativo_codigo: newValue,
          });
          setDeleteNextFrame(deleteNextFrameRef.current);
          setInsertNextFrame(insertNextFrameRef.current);

          return true;
        },
        cellRenderer: ({ value }: ICellRendererParams) => {
          const { hover } = useColors();
          const color = strCSSColor(value ?? "");
          return (
            <HStack h="100%">
              <Tag bgColor={hover} color={color}>
                {value}
              </Tag>
            </HStack>
          );
        },
        ...listFilter(codigos),
      },
      {
        headerName: "Data pagamento",
        field: "data_pagamento",
        ...dateColDef,
        ...dateFilter,
      },
      {
        headerName: "Tipo Evento",
        field: "tipo_evento",
        ...listColDef(tiposSuportados),
        ...listFilter(tipos),
      },
      {
        headerName: "(%) Saldo devedor",
        field: "percentual",
        ...percentageColDef,
        ...numberFilter,
      },
      {
        headerName: "PU Evento",
        field: "pu_evento",
        ...moneyColDef("R$"),
        ...numberFilter,
      },
      {
        headerName: "PU Calculado",
        field: "pu_calculado",
        ...moneyColDef("R$"),
        ...numberFilter,
      },
    ],
    [editable],
  );

  colDefRef.current = fluxoColumnDefs;

  const assetDataExistsRef = useRef(new Set<string>());
  const assetDataRef = useRef([] as Ativo[]);
  const searchRef = useRef("");
  const httpClient = useHTTP({ withCredentials: true });

  const dataSource: IServerSideDatasource = {
    async getRows(params) {
      const {
        filterModel,
        sortModel,
        startRow = 0,
        endRow = 0,
      } = params.request;

      const filters = {
        ativo_codigo: inOrNotInSerialize(filterModel.ativo_codigo, codigos),
        data_pagamento: dateFilterSerialize(filterModel.data_pagamento),
        tipo_evento: inOrNotInSerialize(filterModel.tipo_evento, tipos),
        percentual: percentageFilterSerialize(filterModel.percentual),
        pu_evento: numberFilterSerialize(filterModel.pu_evento),
        pu_calculado: numberFilterSerialize(filterModel.pu_calculado),
      };

      const serializedSort = JSON.stringify(sortModel);
      const serializedFilters = JSON.stringify(filterModel);

      const newSearchRef = serializedSort + serializedFilters;

      if (newSearchRef != searchRef.current) {
        ativosRef.current = {};
        assetDataExistsRef.current.clear();
        assetDataRef.current = [];
      }
      searchRef.current = newSearchRef;

      const q = new URLSearchParams("");
      q.append("deslocamento", String(startRow));
      q.append("quantidade", String(endRow - startRow));
      q.append("ordenacao_eventos", serializedSort);
      q.append("filtros_eventos", JSON.stringify(filters));

      const response = await httpClient.fetch(
        `v1/ativos/eventos?${q.toString()}`,
        { hideToast: { success: true } },
      );
      if (!response.ok) return params.fail();

      const { ativos, eventos, total } = (await response.json()) as {
        ativos: Ativo[];
        eventos: Evento[];
        total: number;
      };
      params.success({
        rowData: eventos.map((e) => ({ ...e, tipo_evento: e.tipo.nome })),
        rowCount: total,
      });

      if (startRow === 0) {
        assetDataRef.current = [];
        loadedAssetsRef.current = {};
        loadedEventsRef.current = {};
      }

      assetDataRef.current.push(
        ...ativos.filter((a) => {
          const doesNotHave = !assetDataExistsRef.current.has(a.codigo);
          assetDataExistsRef.current.add(a.codigo);
          return doesNotHave;
        }),
      );
      setClientSideAssets([...assetDataRef.current]);
      eventos.forEach((e) => {
        loadedEventsRef.current[e.id] = {
          ...e,
          tipo_evento: e.tipo.nome,
        } as any;
        const a = ativos.find((a) => a.codigo === e.ativo_codigo);
        if (a) {
          loadedAssetsRef.current[a.codigo] = {
            ...a,
            emissor: a.emissor.nome,
            tipo: a.tipo.nome,
            indice: strFromIndice({
              nome: a.indice.nome,
              ativo_ipca: a.ativo_ipca ?? null,
            }),
          } as any;
        }
      });
      onNewEventsFetched?.(eventos, total);
    },
  };

  useEffect(() => {
    assetDataExistsRef.current.clear();
    assetDataRef.current = [];
    setClientSideAssets([]);
  }, [dataFlow, editable]);

  const s: SingularPluralMapping = {
    $: { singular: "", plural: "s" },
  };

  const {
    isOpen: isDeleteEventsConfirmOpen,
    onOpen: onDeleteEventsConfirmOpen,
    onClose: onDeleteEventsConfirmClose,
  } = useDisclosure();

  const {
    isOpen: isInsertEventsOpen,
    onOpen: onInsertEventsOpen,
    onClose: onInsertEventsClose,
  } = useDisclosure();

  if (modalOpenRef) {
    modalOpenRef.current = onInsertEventsOpen;
  }

  const [willDeleteEvents, setWillDeleteEvents] = useState<
    Record<string, Evento[]>
  >({});

  const getDeleteItem = (node: IRowNode | null) => {
    const deleteSummary: Record<string, Evento[]> = {};
    const add = (row: Evento) => {
      if (!deleteSummary[row.ativo_codigo]) {
        deleteSummary[row.ativo_codigo] = [];
      }
      if (!deleteSummary[row.ativo_codigo].find((e) => e.id === row.id)) {
        deleteSummary[row.ativo_codigo].push(row);
      }
    };
    const selected = new Set(
      gridApiRef.current?.getSelectedRows().map((row) => {
        add(row);
        return row.id;
      }) ?? [],
    );
    let detailsStr = "";
    if (node) {
      const codigoClicado = node.data.id;
      const numSelecionados = selected.has(codigoClicado)
        ? selected.size - 1
        : selected.size;
      const strSelecionados = pluralOrSingular(
        `mais ${numSelecionados} evento$`,
        s,
        numSelecionados,
      );
      detailsStr = numSelecionados
        ? `este evento e ${strSelecionados}`
        : "este evento";

      selected.add(codigoClicado);
      add(node.data);
      deleteSummary;
    }
    return {
      icon: "🗑️",
      name: `Apagar ${detailsStr}`,
      disabled: !selected.size,
      action() {
        setWillDeleteEvents(deleteSummary);
        onDeleteEventsConfirmOpen();
      },
    };
  };

  const { hover } = useColors();

  const data = useMemo(() => {
    if ([DataFlow.SEPARATE, DataFlow.EVENTS_DEFINE_ASSETS].includes(dataFlow)) {
      return dataSource;
    }
    ativosRef.current = {};
    const events = clientSideEvents.map((e) => {
      let eGrid = { ...e, tipo_evento: e.tipo?.nome ?? (e as any).tipo_evento };
      if (!(eGrid.ativo_codigo in ativosRef.current)) {
        ativosRef.current[eGrid.ativo_codigo] = [];
      }
      const modifiedEvent = modifiedRef.current[eGrid.id]?.data.new;
      if (modifiedEvent) {
        eGrid = modifiedEvent as any;
      }
      if (!deletedEvents.find((ev) => ev.id === eGrid.id)) {
        ativosRef.current[eGrid.ativo_codigo].push(eGrid);
      }
      return eGrid;
    });
    return events;
  }, [dataFlow, clientSideEvents]);

  const verifyDueDateErrors = (assetIds: string[]) => {
    const withoutDueDate: Record<string, number> = {};
    const dueDateNotLastDate: string[] = [];
    assetIds.forEach((assetId) => {
      const eventos = ativosRef.current[assetId];
      if (!eventos) return;
      let ddCount = 0;
      let maiorData = -Infinity;
      let tipoUltimaDataEhVencimento = false;
      eventos.forEach((e) => {
        const ehVencimento =
          (e as any).tipo_evento?.toLowerCase() === "vencimento";
        if (ehVencimento) {
          ddCount++;
        }
        const dataAtual = e.data_pagamento
          ? Number(new Date(e.data_pagamento + "T00:00"))
          : -1;
        if (dataAtual >= maiorData) {
          tipoUltimaDataEhVencimento =
            (dataAtual === maiorData && tipoUltimaDataEhVencimento) ||
            ehVencimento;
          maiorData = dataAtual;
        }
      });
      if (ddCount != 1) {
        withoutDueDate[assetId] = ddCount;
      }
      if (!tipoUltimaDataEhVencimento) {
        dueDateNotLastDate.push(assetId);
      }
    });
    setClientSideNoDueDateErrors(withoutDueDate);
    setClientSideDueDateIsNotLastDateErrors(dueDateNotLastDate);
  };

  return (
    <>
      <ValidationGrid
        colDefs={fluxoColumnDefs}
        data={data}
        editable={editable}
        identifier="id"
        getContextMenuItems={(params) => {
          const defaultItems = params.defaultItems ?? [];
          const deleted = deletedEvents.find(
            (e) => e.id === params.node?.data.id,
          );
          return editable && !deleted
            ? [getDeleteItem(params.node), ...defaultItems]
            : defaultItems;
        }}
        cellValidators={
          {
            data_pagamento: [required],
            tipo_evento: [
              required,
              inList(tiposSuportados, "O evento informado não é suportado"),
            ],
          } as any
        }
        onCellValidationError={(errors) => {
          setClientSideEventsCellErrors(Object.keys(errors).length);
        }}
        onClientDataChanged={(data) => {
          const check = new Set<string>();

          addedRef.current = data.added;
          addedRef.current.forEach((added) => {
            if (!ativosRef.current[added.ativo_codigo]) {
              ativosRef.current[added.ativo_codigo] = [];
            }
            if (
              !ativosRef.current[added.ativo_codigo].find(
                (e) => e.id === added.id,
              )
            ) {
              const e = {
                ...added,
                tipo_evento: added.tipo?.nome ?? (added as any).tipo_evento,
              };
              ativosRef.current[added.ativo_codigo].push(e);
            }
            check.add(added.ativo_codigo);
          });
          setAddedEvents(data.added);

          modifiedRef.current = data.modified;
          Object.entries(modifiedRef.current).forEach(([id, diff]) => {
            const codigo = diff.data.original?.ativo_codigo;
            const eventoNovo = diff.data.new;
            if (!codigo || !eventoNovo || !ativosRef.current[codigo]) return;
            const position = ativosRef.current[codigo].findIndex(
              (e) => String(e.id) === String(id),
            );
            if (position === -1) return;
            ativosRef.current[codigo][position] = eventoNovo;
            check.add(eventoNovo.ativo_codigo);
          });
          setModifiedEvents(data.modified);

          data.deleted.forEach((deleted) => {
            if (!ativosRef.current[deleted.ativo_codigo]) return;
            const position = ativosRef.current[deleted.ativo_codigo].findIndex(
              (e) => e.id === deleted.id,
            );
            if (position === -1) return;
            ativosRef.current[deleted.ativo_codigo].splice(position, 1);
            check.add(deleted.ativo_codigo);
          });
          setDeletedEvents(data.deleted);

          verifyDueDateErrors([...check]);
        }}
        onReady={({ api }) => {
          gridApiRef.current = api;
        }}
        methodsRef={methodsRef}
      />
      <InserirLinhasModal
        isOpen={isInsertEventsOpen}
        onClose={onInsertEventsClose}
        insertAction={(amount) => {
          const newEvents = [] as Partial<Evento>[];
          for (let i = 0; i < amount; i++) {
            newEvents.push({ id: Math.random() });
          }
          methodsRef.current?.insertRows(newEvents);
        }}
      />
      <ConfirmModal
        isOpen={isDeleteEventsConfirmOpen}
        onClose={onDeleteEventsConfirmClose}
        onConfirmAction={() => {
          methodsRef.current?.deleteRows(
            Object.values(willDeleteEvents).flatMap((es) =>
              es.map((e) => e.id as any),
            ),
          );
          setWillDeleteEvents({});
        }}
      >
        <Text mb="12px">
          Deseja apagar o seguinte número de eventos para os ativos abaixo?
        </Text>
        <HStack wrap="wrap">
          {Object.entries(willDeleteEvents).map(([ativo_codigo, eventos]) => {
            const color = strCSSColor(ativo_codigo);
            return (
              <HStack gap={0} border={`1px solid ${getColorHex(hover)}`}>
                <Tag borderRadius={0} bgColor={hover} color={color}>
                  {ativo_codigo}
                </Tag>
                <Text fontSize="sm" pl="4px" pr="4px">
                  <Text as="span" fontWeight="600">
                    {eventos.length}{" "}
                  </Text>
                  {pluralOrSingular(`evento$`, s, eventos.length)}
                </Text>
              </HStack>
            );
          })}
        </HStack>
      </ConfirmModal>
    </>
  );
}
