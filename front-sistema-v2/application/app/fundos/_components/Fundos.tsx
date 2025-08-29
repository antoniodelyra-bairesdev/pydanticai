"use client";
import type { Fundo, FundoCustodiante } from "@/lib/types/api/iv/v1";

import { EditIcon } from "@chakra-ui/icons";
import { Box, HStack, Image, Text } from "@chakra-ui/react";

import { fmtCNPJ } from "@/lib/util/string";
import { ColDef } from "ag-grid-community";
import { useState } from "react";

import LogoBradesco from "@/public/bradesco.png";
import LogoItau from "@/public/itau.png";
import LogoMellon from "@/public/mellon.png";
import LogoSantander from "@/public/santander.png";
import LogoDaycoval from "@/public/daycoval.png";

import { AgGridReact } from "ag-grid-react";

import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "ag-grid-enterprise";
import "@/app/_components/grid/Grid.css";
import { StaticImageData } from "next/image";
import Link from "next/link";

export type FundosProps = {
  data: {
    fundos: Fundo[];
    custodiantes: FundoCustodiante[];
  };
};

const imgs: Record<string, StaticImageData> = {
  bradesco: LogoBradesco,
  itaú: LogoItau,
  mellon: LogoMellon,
  santander: LogoSantander,
  daycoval: LogoDaycoval,
};

export default function Fundos({ data }: FundosProps) {
  const { fundos, custodiantes } = data;

  const defaultColDef = {
    resizable: true,
    sortable: true,
  };

  const [fundosState, setFundosState] = useState(fundos);

  const [columnDefs] = useState<ColDef[]>([
    { field: "CNPJ", filter: true },
    {
      field: "Nome",
      filter: true,
      pinned: true,
      cellRenderer: ({ valueFormatted, value, data }: any) => (
        <Link href={"/fundos/" + data.id}>
          <Text _hover={{ cursor: "pointer" }}>
            <EditIcon marginRight="8px" width="16px" height="16px" />
            {valueFormatted ?? value}
          </Text>
        </Link>
      ),
      resizable: true,
    },
    {
      field: "Custodiante",
      filter: "agMultiColumnFilter",
      cellRenderer: ({ value }: { value: string }) => {
        const cust = value.toLowerCase().split(" ");
        const img =
          imgs[cust[0]] ?? imgs[cust[1]] ?? imgs[cust[0] + " " + imgs[cust[1]]];
        return (
          <HStack overflow="hidden">
            {img && <Image h="16px" objectFit="contain" src={img.src} />}
            <Text>{value}</Text>
          </HStack>
        );
      },
    },
    { field: "ISIN", filter: true },
    { field: "Cód Cust", filter: true },
    { field: "Código Brit", filter: true },
    { field: "Conta Cetip", filter: true },
  ]);

  const filter = (fs: Fundo[]) =>
    fs
      .map((f) => ({
        id: f.id,
        Nome: f.nome,
        Custodiante: f.custodiante?.nome ?? "",
        "Cód Cust": f.codigo_carteira,
        ISIN: f.isin,
        CNPJ: fmtCNPJ(f.cnpj),
        "Código Brit": f.codigo_brit,
        "Conta Cetip": f.conta_cetip,
      }))
      .sort((fa, fb) => fa.Nome.localeCompare(fb.Nome));

  return (
    <Box p="24px" h="100%">
      <Box width="full" h="100%" minH="300px" className="ag-theme-alpine">
        <AgGridReact
          defaultColDef={defaultColDef}
          rowData={filter(fundosState)}
          columnDefs={columnDefs}
          animateRows={true}
          rowSelection="multiple"
          onGridReady={(ev) => ev.columnApi.autoSizeAllColumns()}
        />
      </Box>
      {/* <Button mt='32px' colorScheme={'azul_1'} onClick={onOpen} aria-label='Criar fundo' leftIcon={<AddIcon />}>
                Adicionar fundo
            </Button> */}
    </Box>
  );
}
