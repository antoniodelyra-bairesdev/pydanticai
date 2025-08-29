import { ValidationGridColDef } from "@/app/_components/grid/ValidationGrid";
import { getColorHex } from "@/app/theme";
import { CloseIcon, InfoOutlineIcon } from "@chakra-ui/icons";
import { Box, Td, Text, Tr } from "@chakra-ui/react";
import React from "react";

export type DiffRowProps = {
  colDef: ValidationGridColDef;
  index: number;
  originalData: any;
  newData: any;
  colRowsCount: number;
};

export default function DiffRow({
  originalData,
  newData,
  colDef,
  index,
  colRowsCount,
}: DiffRowProps) {
  const defaultGetValue = (data: any, column: string) => String(data[column]);

  const {
    field: key = "",
    headerName,
    valueToString: getValue = defaultGetValue,
    colDefs: innerColDefs,
  } = colDef;

  const getCell = (
    data: any,
    compareWith: any,
    colorScheme: string,
    missingContent: React.ReactNode,
  ) => {
    return !data ? (
      index === 0 ? (
        <Td
          wordBreak="break-word"
          whiteSpace="normal"
          p="8px"
          fontWeight="normal"
          width="50%"
          rowSpan={colRowsCount}
        >
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            w="100%"
            h="100%"
            gap="8px"
          >
            {missingContent}
          </Box>
        </Td>
      ) : (
        <></>
      )
    ) : (
      <Td
        p="8px"
        wordBreak="break-word"
        whiteSpace="normal"
        width="50%"
        color={
          data?.[key]
            ? data?.[key] !== compareWith?.[key]
              ? colorScheme + ".main"
              : "black"
            : "cinza.300"
        }
        bgColor={
          data?.[key] !== compareWith?.[key] ? colorScheme + ".50" : "white"
        }
      >
        {getValue(data, key ?? "") ?? "Vazio"}
      </Td>
    );
  };

  return (
    <Tr
      fontSize="xs"
      fontWeight={originalData?.[key] !== newData?.[key] ? "bold" : "normal"}
    >
      <Td
        p="8px"
        textAlign="right"
        fontWeight="bold"
        borderRight={`1px solid ${getColorHex("cinza.main")}`}
      >
        {headerName}
      </Td>
      {getCell(
        originalData,
        newData,
        "rosa",
        <>
          <InfoOutlineIcon color="cinza.400" fontSize="2xl" />
          <Text color="cinza.400">Sem informação anterior</Text>
        </>,
      )}
      {getCell(
        newData,
        originalData,
        "verde",
        <>
          <CloseIcon color="cinza.400" fontSize="2xl" />
          <Text color="cinza.400">Dado removido</Text>
        </>,
      )}
    </Tr>
  );
}
