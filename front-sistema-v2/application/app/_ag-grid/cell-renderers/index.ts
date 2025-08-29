import { ICellRendererParams } from "ag-grid-community";

import {
  getFormattedRentabilidade,
  getFormattedPL,
  getFormattedPrecoCota,
  getFormattedPrecoGenerico,
  getTexto,
  getFormattedNumeroGenerico,
  getFormattedPrecoPreciso,
  getFormattedCnpj,
} from "./helpers";

export function rentabilidadeCellRenderer(params: ICellRendererParams) {
  return getFormattedRentabilidade(params.value);
}

export function plCellRenderer(params: ICellRendererParams) {
  return getFormattedPL(params.value);
}

export function precoCotaCellRenderer(params: ICellRendererParams) {
  return getFormattedPrecoCota(params.value);
}

export function precoGenericoCellRenderer(params: ICellRendererParams) {
  return getFormattedPrecoGenerico(params.value);
}

export function precoPrecisoCellRenderer(params: ICellRendererParams) {
  return getFormattedPrecoPreciso(params.value);
}

export function numeroGenericoCellRenderer(params: ICellRendererParams) {
  return getFormattedNumeroGenerico(params.value);
}

export function textoCellRenderer(params: ICellRendererParams) {
  return getTexto(params.value);
}

export function cnpjCellRenderer(params: ICellRendererParams) {
  return getFormattedCnpj(params.value);
}
