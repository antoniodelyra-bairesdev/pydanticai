import { SetFilterParams } from "ag-grid-community";

export const numberFilter = {
  filter: "agNumberColumnFilter",
  filterParams: { maxNumConditions: 1 },
};
export const textFilter = {
  filter: "agTextColumnFilter",
  filterParams: { maxNumConditions: 1 },
};
export const dateFilter = {
  filter: "agDateColumnFilter",
  filterParams: { maxNumConditions: 1 },
};
export const listFilter = <T>(data: T[]) => ({
  filter: "agSetColumnFilter",
  filterParams: { values: ({ success }) => success(data) } as SetFilterParams<
    any,
    T
  >,
});

export const inOrNotInSerialize = (
  filter: { filterType: string; values: string[] } | undefined,
  defaultSet: string[],
) => {
  if (!filter) return;
  const notInSize = defaultSet.length - filter.values.length;
  if (notInSize < defaultSet.length / 2) {
    const notIn = new Set(defaultSet);
    filter.values.forEach((value) => notIn.delete(value));
    return { notInSet: [...notIn] };
  }
  return { set: [...filter.values] };
};

export const dateFilterSerialize = (filter?: {
  filterType: string;
  type: string;
  dateFrom: string | null;
  dateTo: string | null;
}) => {
  if (!filter) return;
  const { filterType, type, dateFrom, dateTo } = filter;
  if (filterType != "date") return;
  if (["blank", "notBlank"].includes(type)) {
    return type;
  }
  if (type === "inRange" && dateFrom && dateTo) {
    return {
      inRange: [dateFrom.split(" ")[0], dateTo.split(" ")[0]],
    };
  }
  if (dateFrom) {
    return {
      [type]: dateFrom.split(" ")[0],
    };
  }
};

export const textFilterSerialize = (filter?: {
  filterType: string;
  type: string;
  filter?: string | null;
}) => {
  if (!filter) return;
  const { filterType, type, filter: value } = filter;
  if (filterType != "text") return;
  if (["blank", "notBlank"].includes(type)) {
    return type;
  }
  if (value) {
    return {
      [type]: value,
    };
  }
};

export const numberFilterSerialize = (filter?: {
  filterType: string;
  type: string;
  filter: string | null;
  filterTo: string | null;
}) => {
  if (!filter) return;
  const { filterType, type, filter: filterFrom, filterTo } = filter;
  if (filterType != "number") return;
  if (["blank", "notBlank"].includes(type)) {
    return type;
  }
  if (type === "inRange" && filterFrom && filterTo) {
    return {
      inRange: [String(filterFrom), String(filterTo)],
    };
  }
  if (filterFrom) {
    return {
      [type]: String(filterFrom),
    };
  }
};

export const percentageFilterSerialize = (filter?: {
  filterType: string;
  type: string;
  filter?: number | null;
  filterTo?: number | null;
}) => {
  if (!filter) return;
  let { filter: filterFrom, filterTo } = filter;
  filterFrom &&=
    typeof filterFrom === "number" ? Number(filterFrom) / 100 : filterFrom;
  filterTo &&= typeof filterTo === "number" ? Number(filterTo) / 100 : filterTo;
  return numberFilterSerialize({
    ...filter,
    filter: String(filterFrom),
    filterTo: String(filterTo),
  });
};
