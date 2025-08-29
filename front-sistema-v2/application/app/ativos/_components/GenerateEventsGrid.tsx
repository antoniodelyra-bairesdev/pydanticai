import ValidationGrid, {
  ValidationGridColDef,
  ValidationGridMethods,
} from "@/app/_components/grid/ValidationGrid";
import { Evento } from "@/lib/types/api/iv/v1";
import { inList, required } from "@/lib/util/validation";
import { ColumnApi, GridApi } from "ag-grid-community";
import { MutableRefObject, useEffect, useRef } from "react";

export type StagedEvent = {
  uuid: number;
  data: string;
  tipo_evento: string;
  percentual: number;
};

export type GenerateEventsGrid = {
  colDefs: ValidationGridColDef[];
  eventos: StagedEvent[];
  tipoEventos: string[];
  methodsRef: MutableRefObject<ValidationGridMethods<Evento> | undefined>;
  colApiRef: MutableRefObject<ColumnApi | null>;
  apiRef: MutableRefObject<GridApi | null>;
  onPercentageChange: (percentage: number) => void;
  onDueCountChange: (dueCount: number) => void;
  onLastEventChange: (correctLastEvent: boolean) => void;
  onError: (errorCount: number) => void;
  onDuePays100: (dueIs100: boolean) => void;
};

export default function GenerateEventsGrid({
  colDefs,
  eventos,
  tipoEventos,
  apiRef: _outerApiRef,
  colApiRef,
  methodsRef,
  onPercentageChange,
  onDueCountChange,
  onError,
  onLastEventChange,
  onDuePays100,
}: GenerateEventsGrid) {
  const apiRef = useRef<GridApi | null>();
  const validate = () => {
    let porcentagemAcumulada = 0;
    let vencimentosContabilizados = 0;
    let tipoUltimaDataEhVencimento = false;
    let maiorData = -Infinity;
    let ultimoVencimentoPagaTudo = false;
    apiRef.current?.forEachNode(
      ({ data: { percentual = 0, tipo_evento, data } }) => {
        if (typeof percentual === "number" && !isNaN(percentual)) {
          porcentagemAcumulada += +percentual.toFixed(8);
        }
        const dataAtual = data ? Number(new Date(data + "T00:00")) : -1;
        if (tipo_evento === "Vencimento") {
          vencimentosContabilizados++;
          ultimoVencimentoPagaTudo = Number(+percentual.toFixed(8)) === 1;
        }
        if (dataAtual >= maiorData) {
          tipoUltimaDataEhVencimento =
            dataAtual === maiorData && tipoUltimaDataEhVencimento
              ? true
              : tipo_evento === "Vencimento";
          maiorData = dataAtual;
        }
      },
    );
    onPercentageChange(porcentagemAcumulada * 100);
    onDueCountChange(vencimentosContabilizados);
    onLastEventChange(tipoUltimaDataEhVencimento);
    onDuePays100(ultimoVencimentoPagaTudo);
  };
  useEffect(() => {
    validate();
  }, [eventos]);
  return (
    <ValidationGrid
      getContextMenuItems={(params) => {
        const selected = params.api.getSelectedNodes();
        return [
          {
            icon: "🗑️",
            name: `Apagar ${selected.length} eventos selecionados`,
            action() {
              if (!params.node) return;
              methodsRef.current?.deleteRows(
                selected.map((node) => node.data.uuid),
              );
            },
          },
          ...(params.defaultItems ?? []),
        ];
      }}
      colDefs={colDefs}
      data={eventos}
      editable={true}
      identifier="uuid"
      onReady={(ev) => {
        ev.api.sizeColumnsToFit();
        colApiRef.current = ev.columnApi;
        apiRef.current = ev.api;
        _outerApiRef.current = ev.api;
      }}
      methodsRef={methodsRef as any}
      paintAddedCells={false}
      paintModifiedCells={false}
      deletedCellBehaviour={{
        show: false,
      }}
      cellValidators={{
        data: [required],
        tipo_evento: [required, inList(tipoEventos, "Tipo de evento inválido")],
      }}
      onClientDataChanged={validate}
      onCellValidationError={(errors) => onError(Object.keys(errors).length)}
    />
  );
}
