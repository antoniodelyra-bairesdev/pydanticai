"use client";

import {
  Box,
  HStack,
  LightMode,
  Progress,
  Text,
  Tooltip,
  useColorMode,
} from "@chakra-ui/react";
import {
  CellValueChangedEvent,
  ColDef,
  EditableCallbackParams,
  GetContextMenuItems,
  GridApi,
  GridReadyEvent,
  ICellRendererParams,
  IRowNode,
  IServerSideDatasource,
  IServerSideGetRowsParams,
  LoadSuccessParams,
  RowClassParams,
  RowDataTransaction,
  RowStyle,
  ServerSideTransaction,
  ValueGetterParams,
  ValueSetterParams,
} from "ag-grid-community";
import {
  MutableRefObject,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import { getColorHex } from "@/app/theme";
import { useColors } from "@/lib/hooks";
import { ValidatorFn } from "@/lib/util/validation";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "ag-grid-enterprise";
import { AgGridReact, AgGridReactProps } from "ag-grid-react";
import "./Grid.css";

export type ValidationGridColDef = ColDef & {
  primary?: boolean;
  validator?: (params: ValueSetterParams) => string[];
  valueToString?: (rowData: any, field: string) => string;
  colDefs?: ValidationGridColDef[];
};

export type ValidationGridMethods<T> = {
  getRowData(): Partial<T>[];
  insertRows(rows: Partial<T>[]): void;
  updateRows(rows: Partial<T>[]): void;
  deleteRows(rowIds: string[]): void;
  resetClientSideData(): void;
};

export type ModificationMap<T> = Record<
  string,
  {
    data: { original: T | null; new: T | null };
    fields: Record<string, { original: any; new: any }>;
  }
>;

export type ClientSideData<T> = {
  deleted: T[];
  modified: ModificationMap<T>;
  added: T[];
};

export type ValidationGridProps<T> = {
  /** Se a tabela está ou não no modo de edição */
  editable: boolean;
  /** Definições de colunas do AgGrid + função de validação de dados */
  colDefs: ValidationGridColDef[];
  /**
   * Fonte de dados da tabela, disponível em dois formatos.
   * - Client-side: Um array de objetos é fornecido
   * - Server-side: Um objeto implementa a interface IServerSideDatasource
   */
  data: T[] | IServerSideDatasource;
  /** Nome da propriedade utilizada para identificar unicamente cada linha */
  identifier: string;
  /** Caso verdadeiro, pinta as células adicionadas com uma cor esverdeada */
  paintAddedCells?: boolean;
  /** Caso verdadeiro, pinta as células adicionadas com uma cor amarelada */
  paintModifiedCells?: boolean;
  /** Define o comportamento das células deletadas. */
  deletedCellBehaviour?: {
    /** Caso verdadeiro, pinta as células adicionadas com uma cor alaranjada */
    paint?: boolean;
    /** Caso verdadeiro, mantém as células deletadas na tabela. Propriedade **ignorada** caso a fonte de dados venha do servidor: neste caso, ela sempre será mostrada */
    show?: boolean;
  };
  /** A altura em pixels de cada linha do grid */
  rowHeight?: number;
  /** Regra de padding para cada célula*/
  cellPadding?: string;
  /** Funções de validação de cada célula */
  cellValidators?: Partial<Record<keyof T, ValidatorFn[]>>;
  methodsRef?: MutableRefObject<ValidationGridMethods<T> | undefined>;
  /** Método utilizado para sobrescrever o comportamento do menu de opções quando o usuário clica com o botão direito em uma célula */
  getContextMenuItems?: GetContextMenuItems<any>;
  /** Método utilizado para sobrescrever o estilo de cada linha do grid */
  getRowStyle?: (params: RowClassParams<T>) => RowStyle | undefined;
  /** Callback disparada quando a tabela está com os métodos disponíveis */
  onReady?: (event: GridReadyEvent) => void;
  /** Callback disparada quando a tabela atualiza os quais células possuem erros de validação, informando todos os erros existentes */
  onCellValidationError?: (
    cellValidationErrors: Record<string, string[]>,
  ) => void;
  /** Callback disparada quando a tabela sofre alguma alteração, informando todas as alterações já feitas */
  onClientDataChanged?: (data: ClientSideData<T>) => void;
};

const valueToString = (rowData: any, field: string): string => {
  const value = rowData[field];
  if (value === null || value === undefined) return "";
  return String(value);
};

export default function ValidationGrid<T>({
  editable,
  colDefs,
  data,
  identifier,
  getContextMenuItems,
  getRowStyle,
  onReady,
  onCellValidationError,
  onClientDataChanged,
  methodsRef,
  paintAddedCells = true,
  paintModifiedCells = true,
  deletedCellBehaviour = {},
  rowHeight = 36,
  cellPadding,
  cellValidators = {} as Record<keyof T, ValidatorFn[]>,
}: ValidationGridProps<T>) {
  const { paint: paintDeletedCells = true, show: showDeletedCells = true } =
    deletedCellBehaviour;

  const { colorMode } = useColorMode();

  const [editedCells, setEditedCells] = useState<CellValueChangedEvent[]>([]);
  const editedCellsRef = useRef<CellValueChangedEvent[]>([]);

  const removedRows = useRef<Map<string, T>>(new Map());
  const modifiedRows = useRef<ModificationMap<T>>({});
  const addedRows = useRef<Map<string, T>>(new Map());

  const cellValidationErrors = useRef<Record<string, string[]>>({});

  const emitClientDataChanges = () => {
    const added = [...addedRows.current.entries()].map(([_, row]) => row);
    const modified = { ...modifiedRows.current };
    const deleted = [...removedRows.current.entries()].map(([_, row]) => row);
    onClientDataChanged?.({ added, deleted, modified });
  };

  const resetClientSideData = () => {
    const api = apiRef.current;
    if (!api) return;

    if (!Array.isArray(data)) {
      api.refreshServerSide();
      lastRowFetched.current = 0;
      api.setRowCount(0);
      api.setCacheBlockSize(35);
    } else {
      api.setRowData(data);
    }

    cellValidationErrors.current = {};
    onCellValidationError?.({});

    removedRows.current.clear();
    modifiedRows.current = {};
    addedRows.current.clear();
    emitClientDataChanges();
  };

  useEffect(() => {
    if (!editable) {
      resetClientSideData();
      apiRef.current?.stopEditing();
    }
  }, [editable]);

  type CellChange = {
    rowId: string;
    colId: string;
    oldValue: any;
    newValue: any;
    node: IRowNode;
  };

  const triggerValidators = (cells: CellChange[]) => {
    const shouldUpdate: { force: boolean; rowNodes: IRowNode[] } = {
      force: true,
      rowNodes: [],
    };

    for (const cell of cells) {
      const id = cell.rowId;
      const col = cell.colId;

      const validators = cellValidators[col as keyof T] ?? [];
      const errors = getValidationErrors(validators, cell.newValue);

      const errorKey = `${id}.${col}`;
      if (!errors.length) {
        delete cellValidationErrors.current[errorKey];
      } else {
        cellValidationErrors.current[errorKey] = errors;
      }
      shouldUpdate.rowNodes.push(cell.node);
    }

    if (shouldUpdate.rowNodes.length) {
      apiRef.current?.refreshCells(shouldUpdate);
    }

    onCellValidationError?.(cellValidationErrors.current);
  };

  const getValidationErrors = (validators: ValidatorFn[], value: string) => {
    const errors = [];
    for (const validator of validators) {
      const error = validator(value);
      if (error) {
        errors.push(error);
      }
    }
    return errors;
  };

  const onCellValueChanged = (event: CellValueChangedEvent) => {
    editedCellsRef.current.push(event);
    setEditedCells(editedCellsRef.current);
  };

  const modifyCell = (
    rowId: typeof identifier,
    colId: keyof T,
    oldData: T,
    newData: T,
  ) => {
    let rowChangeInfo = modifiedRows.current[rowId];
    let cellHistoryData = rowChangeInfo?.fields[String(colId)];

    const originalValue = cellHistoryData
      ? cellHistoryData.original
      : oldData[colId];

    if (originalValue === newData[colId]) {
      if (!rowChangeInfo) return;

      if (rowChangeInfo.data.new && rowChangeInfo.data.original) {
        rowChangeInfo.data.new[colId as keyof T] =
          rowChangeInfo.data.original[colId as keyof T];
      }
      delete rowChangeInfo.fields[String(colId)];

      if (Object.keys(rowChangeInfo.fields).length === 0) {
        delete modifiedRows.current[rowId];
      }
    } else {
      if (!rowChangeInfo) {
        rowChangeInfo = {
          data: { original: structuredClone(oldData), new: null },
          fields: {},
        };
        modifiedRows.current[rowId] = rowChangeInfo;
      }
      rowChangeInfo.data.new = structuredClone(newData);
      rowChangeInfo.fields[String(colId)] = {
        original: originalValue,
        new: newData[colId],
      };
    }
  };

  const columnDefs = useMemo(
    () =>
      colDefs.map((cd) => ({
        sortable: true,
        ...cd,
        editable: (params: EditableCallbackParams) => {
          if (
            cd.primary ||
            removedRows.current.has(params.data[identifier]) ||
            !editable
          )
            return false;
          return (
            (typeof cd.editable === "function"
              ? cd.editable(params)
              : cd.editable) ?? true
          );
        },
        valueSetter(params: ValueSetterParams) {
          if (removedRows.current.has(params.data[identifier])) {
            return false;
          }

          const oldData = structuredClone(params.data);

          let changed: boolean;
          if (typeof cd.valueSetter !== "function") {
            params.data[params.column.getId()] = params.newValue;
            changed = true;
          } else {
            changed = cd.valueSetter(params);
          }

          const rowId = params.data[identifier];

          if (addedRows.current.has(rowId)) {
            return changed;
          }

          modifyCell(
            rowId,
            params.column.getId() as keyof T,
            oldData,
            params.data,
          );

          return changed;
        },
        valueToString,
        valueGetter(params: ValueGetterParams) {
          const vts = cd.valueToString ? cd.valueToString : valueToString;
          const column = params.column.getId();
          const value =
            typeof cd.valueGetter === "function"
              ? cd.valueGetter(params)
              : vts(params.data, column);
          return value;
        },
        cellRenderer(params: ICellRendererParams) {
          const { bgError, bgWarn, bgDeleted, hover } = useColors();
          const { value, data } = params;
          const rowId = data[identifier];
          const colId = cd.field;
          const errorKey = `${rowId}.${colId}`;
          const validationErrors: string[] =
            cellValidationErrors.current[errorKey] ?? [];

          const hasBeenDeleted = removedRows.current.has(rowId);
          const hasErrors = Boolean(validationErrors.length);
          const hasBeenAdded = addedRows.current.has(rowId);
          const hasChanged = Boolean(
            (colId ?? "") in (modifiedRows.current[rowId]?.fields ?? {}),
          );

          let statusColor: string;

          if (hasBeenDeleted)
            statusColor = paintDeletedCells ? getColorHex(bgDeleted) : "none";
          else if (hasErrors) statusColor = getColorHex(bgError);
          else if (hasBeenAdded)
            statusColor = paintAddedCells ? getColorHex("verde.200") : "none";
          else if (hasChanged)
            statusColor = paintModifiedCells ? getColorHex(bgWarn) : "none";
          else statusColor = "none";

          statusColor += "7f";

          return (
            <Tooltip
              hasArrow
              isDisabled={validationErrors.length === 0}
              label={validationErrors.join(", ")}
            >
              <HStack
                w="100%"
                h="100%"
                p={cellPadding}
                backgroundColor={statusColor}
                cursor={editable ? "cell" : "auto"}
                pointerEvents={hasBeenDeleted ? "none" : "all"}
                opacity={hasBeenDeleted ? 0.325 : 1}
                overflow="hidden"
              >
                {cd.cellRenderer ? (
                  (cd.cellRenderer({ ...params, validationErrors }) ??
                  (editable ? <Text color={hover}>Vazio</Text> : null))
                ) : (
                  <Text>{value}</Text>
                )}
              </HStack>
            </Tooltip>
          );
        },
      })),
    [editable, data],
  );

  const apiRef = useRef<GridApi | null>(null);

  useEffect(() => {
    if (editedCells.length) {
      triggerValidators(
        editedCells.map((cell) => ({
          colId: cell.column.getId(),
          rowId: cell.data[identifier],
          newValue: cell.newValue,
          oldValue: cell.oldValue,
          node: cell.node,
        })),
      );
      editedCellsRef.current = [];
      emitClientDataChanges();
      setEditedCells([]);
    }
  }, [editedCells]);

  const lastRowFetched = useRef(0);

  const [gridFetching, setGridFetching] = useState(false);

  const applyClientSideDiff = (
    applyTransaction:
      | ((rowDataTransaction: RowDataTransaction) => any)
      | ((serverSideTransaction: ServerSideTransaction) => any),
    rdata: T[],
  ) => {
    const add = [...addedRows.current].map(([_, data]) => data);
    const update: T[] = [];
    Object.entries(modifiedRows.current).forEach(([key, changes]) => {
      const row = rdata.find((row) => row[identifier as keyof T] == key);
      if (!row) return;
      const modified = structuredClone(row) as T;
      Object.entries(changes.fields ?? {}).forEach(([field, change]) => {
        modified[field as keyof T] = change.new;
      });
      update.push(modified);
    });
    applyTransaction({
      addIndex: 0,
      add,
      update,
    });
  };

  const configureDataSource = (api: GridApi) => {
    if (Array.isArray(data)) {
      return;
    }
    const originalGetRows = data.getRows;
    data.getRows = (ssParams: IServerSideGetRowsParams) => {
      setGridFetching(true);
      const originalFailure = ssParams.fail;
      ssParams.fail = () => {
        setGridFetching(false);
        originalFailure();
      };
      const originalSuccess = ssParams.success;
      ssParams.success = (sucParams: LoadSuccessParams) => {
        setGridFetching(false);
        lastRowFetched.current = Math.max(
          lastRowFetched.current,
          ssParams.request.endRow ?? 0,
        );
        sucParams.rowCount = Math.min(
          sucParams.rowCount ?? 0,
          lastRowFetched.current + 1,
        );
        originalSuccess(sucParams);
        applyClientSideDiff(
          api.applyServerSideTransaction.bind(api),
          sucParams.rowData,
        );
      };
      originalGetRows(ssParams);
    };
    api.setServerSideDatasource(data);
  };

  const rowData: { rowData: T[] } = useMemo(
    () => ({ rowData: Array.isArray(data) ? data : [] }),
    [editable, data],
  );

  useEffect(() => {
    const api = apiRef.current;
    if (!Array.isArray(data) || !api) return;
    applyClientSideDiff(api.applyTransaction.bind(api), data);
  }, [data]);

  const insertRows: ValidationGridMethods<T>["insertRows"] = (rows) => {
    const api = apiRef.current;
    if (!api) return;
    const applyTransaction = (
      Array.isArray(data)
        ? api.applyTransaction
        : api.applyServerSideTransaction
    ).bind(api);
    const result = applyTransaction({
      addIndex: 0,
      add: rows,
    });
    triggerValidators(
      result?.add?.flatMap((row) => {
        const id = row.data[identifier];
        addedRows.current.set(id, row.data);
        return colDefs.map((col) => ({
          colId: col.field ?? "",
          rowId: row.data[identifier],
          newValue: api.getValue(col.field ?? "", row),
          oldValue: undefined,
          node: row,
        }));
      }) ?? [],
    );
    emitClientDataChanges();
  };

  const updateRows: ValidationGridMethods<T>["updateRows"] = (rows) => {
    const api = apiRef.current;
    if (!api) return;
    const applyTransaction = (
      Array.isArray(data)
        ? api.applyTransaction
        : api.applyServerSideTransaction
    ).bind(api);
    const oldData: Record<string, T> = {};
    for (const updatedRow of rows) {
      if (!(identifier in updatedRow)) continue;
      const codigo = String(updatedRow[identifier as keyof T]);
      const original = api.getRowNode(codigo);
      if (!original) continue;
      oldData[codigo] = structuredClone(original.data);
    }
    const result = applyTransaction({
      update: rows,
    });
    const changes =
      result?.update?.flatMap((row) =>
        colDefs.map((col) => {
          const colId = col.field ?? "";
          const rowId = row.data[identifier];
          modifyCell(rowId, colId as keyof T, oldData[rowId], row.data);
          return {
            colId,
            rowId,
            newValue: api.getValue(col.field ?? "", row),
            oldValue: oldData[row.data[identifier]],
            node: row,
          };
        }),
      ) ?? [];
    triggerValidators(changes);
    emitClientDataChanges();
  };

  const deleteRows: ValidationGridMethods<T>["deleteRows"] = (rowIds) => {
    const api = apiRef.current;
    if (!api) return;
    const applyTransaction = (
      Array.isArray(data)
        ? api.applyTransaction
        : api.applyServerSideTransaction
    ).bind(api);
    const rowNodes: IRowNode[] = [];
    rowIds.forEach((id) => {
      const row = api.getRowNode(id);
      if (!row) return;
      rowNodes.push(row);
      if (!addedRows.current.has(id)) {
        removedRows.current.set(id, row.data);
      } else {
        addedRows.current.delete(id);
        applyTransaction({
          remove: [{ [identifier]: id }],
        });
      }
      if (id in modifiedRows.current) {
        delete modifiedRows.current[id];
      }
      for (const colDef of colDefs) {
        const col = colDef.field ?? "";

        const validators = cellValidators[col as keyof T] ?? [];
        const value = api.getValue(col, row);
        const errors = getValidationErrors(validators, value);

        const errorKey = `${id}.${col}`;
        if (errors.length) {
          delete cellValidationErrors.current[errorKey];
        }
      }
    });
    if (Array.isArray(data) && !showDeletedCells) {
      applyTransaction({
        remove: rowIds.map((id) => ({ [identifier]: id })),
      });
    }
    api.refreshCells({ force: true, rowNodes });
    api.deselectAll();
    api.clearRangeSelection();
    onCellValidationError?.(cellValidationErrors.current);
    emitClientDataChanges();
  };

  const getRowData = () => {
    const rows: Partial<T>[] = [];
    apiRef.current?.forEachNode((node) => rows.push(node.data));
    return rows;
  };

  if (methodsRef) {
    methodsRef.current = {
      getRowData,
      resetClientSideData,
      insertRows,
      updateRows,
      deleteRows,
    };
  }

  const commonProps = {
    suppressLastEmptyLineOnPaste: true,
    columnDefs,
    onCellValueChanged,
    getContextMenuItems,
    rowSelection: "multiple",
    enableRangeSelection: true,
    enableGroupEdit: true,
    onGridReady: (ev) => {
      configureDataSource(ev.api);
      apiRef.current = ev.api;
      onReady?.(ev);
      ev.api.ensureIndexVisible(0, "top");
    },
    getRowId: (params) => params.data[identifier],
    suppressColumnVirtualisation: true,
    gridOptions: { undoRedoCellEditing: true, undoRedoCellEditingLimit: 100 },
    rowHeight,
    onSortChanged: (params) => {
      lastRowFetched.current = 0;
      if (!Array.isArray(data)) {
        params.api.setRowCount(1);
      }
      params.api.ensureIndexVisible(0, "top");
    },
    getRowStyle(params) {
      return getRowStyle?.(params);
    },
  } as AgGridReactProps;

  return (
    <Box
      w="100%"
      h="100%"
      className={`ag-theme-alpine${colorMode === "dark" ? "-dark" : ""}`}
      position="relative"
    >
      {gridFetching && (
        <LightMode>
          <Progress
            zIndex={2}
            bgColor={getColorHex("azul_1.main") + "F7"}
            position="absolute"
            w="100%"
            h="49px"
            isIndeterminate={true}
            colorScheme="verde"
          />
        </LightMode>
      )}
      {Array.isArray(data) ? (
        <AgGridReact key="client-side" {...rowData} {...commonProps} />
      ) : (
        <AgGridReact
          key="server-side"
          {...commonProps}
          rowModelType="serverSide"
          rowBuffer={0}
          cacheBlockSize={35}
        />
      )}
    </Box>
  );
}
