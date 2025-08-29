import { ValueFormatterParams } from "ag-grid-community";

import { fmtDate, fmtCNPJ } from "@/lib/util/string";

export function dateFormatter(params: ValueFormatterParams) {
  return params.value ? fmtDate(params.value) : "--/--/----";
}

export function cnpjFormatter(params: ValueFormatterParams) {
  return fmtCNPJ(params.value);
}
