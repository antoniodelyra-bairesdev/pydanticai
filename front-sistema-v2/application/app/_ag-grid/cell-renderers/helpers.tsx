import { Box, Text } from "@chakra-ui/react";

import { fmtCNPJ, fmtNumber } from "@/lib/util/string";

const colors: Record<number, string> = {
  [-1]: "rosa.main",
  0: "cinza.500",
  1: "verde.main",
};

export const getFormattedRentabilidade = (r: number | null | undefined) =>
  r === null || r === undefined ? (
    "---"
  ) : (
    <Text
      as="span"
      color={colors[Math.sign(r - 1)]}
      overflow="hidden"
      textOverflow="ellipsis"
      whiteSpace="nowrap"
    >
      {fmtNumber((r - 1) * 100, 2) + "%"}
    </Text>
  );

export const getFormattedPL = (r: number | null | undefined) =>
  r === null || r === undefined ? (
    "---"
  ) : (
    <Text
      as="span"
      overflow="hidden"
      textOverflow="ellipsis"
      whiteSpace="nowrap"
    >
      R$ {fmtNumber(r / 1_000_000, 2) + "M"}
    </Text>
  );

export const getFormattedPrecoCota = (sharePrice: number) => {
  return sharePrice.toLocaleString("pt-BR", {
    minimumFractionDigits: 7,
    maximumFractionDigits: 7,
  });
};

export const getFormattedPrecoGenerico = (price: number | null | undefined) =>
  price === null || price === undefined ? (
    "---"
  ) : (
    <Text overflow="hidden" textOverflow="ellipsis" whiteSpace="nowrap">
      R${" "}
      {price.toLocaleString("pt-BR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}
    </Text>
  );

export const getFormattedPrecoPreciso = (price: number | null | undefined) =>
  price === null || price === undefined ? (
    "---"
  ) : (
    <Text overflow="hidden" textOverflow="ellipsis" whiteSpace="nowrap">
      R${" "}
      {price.toLocaleString("pt-BR", {
        minimumFractionDigits: 8,
        maximumFractionDigits: 8,
      })}
    </Text>
  );

export const getFormattedNumeroGenerico = (
  numero: number | null | undefined,
) => (
  <Text overflow="hidden" textOverflow="ellipsis" whiteSpace="nowrap">
    {numero === null || numero === undefined
      ? "---"
      : numero.toLocaleString("pt-BR", {
          minimumFractionDigits: 0,
          maximumFractionDigits: 2,
        })}
  </Text>
);

export const getFormattedCnpj = (cnpj: string | null | undefined) =>
  cnpj === null || cnpj === undefined ? "---" : <Text>{fmtCNPJ(cnpj)}</Text>;

export const getTexto = (texto: string | null | undefined) =>
  texto === null || texto === undefined ? (
    "---"
  ) : (
    <Text overflow="hidden" textOverflow="ellipsis" whiteSpace="nowrap">
      {texto}
    </Text>
  );
