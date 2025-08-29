import { useColors } from "@/lib/hooks";
import {
  dateToStr,
  fmtDate,
  fmtNumber,
  fmtNumberComparator,
  getNumericDataFromValue,
  ptDateToYYYYMMDD,
} from "@/lib/util/string";
import { CalendarIcon } from "@chakra-ui/icons";
import { HStack, Tag, Text } from "@chakra-ui/react";
import { ICellRendererParams, ValueSetterParams } from "ag-grid-community";
import { ValidationGridColDef } from "./ValidationGrid";

export const moneyColDef = (currency: string): ValidationGridColDef => ({
  comparator: fmtNumberComparator,
  valueSetter(params: ValueSetterParams) {
    const saved = getNumericDataFromValue(params.newValue);
    params.data[params.column.getColId()] = saved;
    return true;
  },
  valueToString(row, column) {
    const data = row[column];
    return typeof data === "number" ? fmtNumber(data, 6) : (data ?? "");
  },
  cellRenderer({ value }: ICellRendererParams & { validationErrors?: string }) {
    const { hover, text } = useColors();
    const num = value;
    return num !== "" ? (
      <HStack>
        {num !== "" && (
          <Tag
            fontSize="xs"
            bgColor={hover}
            color={value.includes("-") ? "rosa.main" : "verde.main"}
          >
            {currency}
          </Tag>
        )}
        <Text color={num !== "" ? text : hover}>
          {typeof num === "number" ? fmtNumber(num, 6) : num || "Vazio"}
        </Text>
      </HStack>
    ) : null;
  },
  filterParams: {
    maxNumConditions: 1,
  },
});

export const percentageColDef: ValidationGridColDef = {
  comparator: fmtNumberComparator,
  valueSetter(params: ValueSetterParams) {
    const num = getNumericDataFromValue(params.newValue);
    const saved = typeof num === "number" ? num / 100 : num;
    params.data[params.column.getColId()] = saved;
    return true;
  },
  valueToString(row, column) {
    const data = row[column];
    return typeof data === "number" ? fmtNumber(data * 100, 6) : (data ?? "");
  },
  cellRenderer({
    value,
    validationErrors = [],
  }: ICellRendererParams & { validationErrors?: string[] }) {
    const { hover, text } = useColors();
    const num = value;
    return (
      <HStack>
        <Text color={num !== "" ? text : hover}>
          {typeof num === "number" ? num : num || "Vazio"}
        </Text>
        {!validationErrors.length && typeof num === "string" && (
          <Tag opacity={0.5} bgColor={hover} borderRadius="full" fontSize="xs">
            %
          </Tag>
        )}
      </HStack>
    );
  },
  filterParams: {
    maxNumConditions: 1,
  },
};

export const dateColDef: ValidationGridColDef = {
  comparator(dA, dB) {
    const dateA = new Date(ptDateToYYYYMMDD(dA));
    const dateB = new Date(ptDateToYYYYMMDD(dB));
    return Number(dateB) - Number(dateA);
  },
  valueSetter(params: ValueSetterParams) {
    let { newValue } = params;
    if (newValue instanceof Date) {
      newValue = dateToStr(newValue);
    }
    const dmy = (newValue?.split("/") ?? []) as string[];
    const ymd = (newValue?.split("-") ?? []) as string[];
    const parsed =
      dmy.length === 3 ? [...dmy].reverse() : ymd.length === 3 ? ymd : [];
    const dateCandidate = parsed.join("-");
    params.data[params.column.getColId()] = isNaN(
      Number(new Date(dateCandidate + "T00:00:00")),
    )
      ? ""
      : dateCandidate;
    return true;
  },
  valueToString(row, column) {
    const date = row[column];
    return date ? fmtDate(date) : "";
  },
  cellRenderer(params: ICellRendererParams) {
    const { hover, text } = useColors();
    const date = params.value;
    return (
      <HStack>
        {date && <CalendarIcon color={hover} />}
        <Text color={date ? text : hover}>{date || "Vazio"}</Text>
      </HStack>
    );
  },
  cellEditor: "agDateCellEditor",
  filterParams: {
    maxNumConditions: 1,
  },
};

export const listColDef = <T,>(
  data: T[],
  options?: {
    comparator?: (_1: T, _2: T) => number;
    cellRenderer?: ValidationGridColDef["cellRenderer"];
  },
) => {
  const {
    comparator = (first: T, second: T) =>
      String(first).localeCompare(String(second)),
    cellRenderer = ({ value }: ICellRendererParams) => (
      <Text>{String(value)}</Text>
    ),
  } = options ?? {};
  return {
    cellEditor: "agRichSelectCellEditor" as const,
    cellEditorPopup: true,
    cellEditorPopupPosition: "under" as const,
    cellEditorParams: {
      values: data.sort((ea, eb) => comparator(ea, eb)),
      cellRenderer,
      allowTyping: true,
      filterList: true,
      searchType: "fuzzy",
      cellHeight: 36,
    },
  } as ValidationGridColDef;
};
