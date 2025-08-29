"use client";

import { useHTTP, useUser } from "@/lib/hooks";
import {
  Box,
  Button,
  Icon,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import React, { MutableRefObject, useState, useMemo } from "react";
import { IoEyeOffOutline, IoGlobeOutline } from "react-icons/io5";
import ModalPublicacaoFundo from "./ModalPublicacaoFundo";
import { ColDef, ICellRendererParams } from "ag-grid-community";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "ag-grid-enterprise";
import "@/app/_components/grid/Grid.css";
import { AgGridReact } from "ag-grid-react";
import { EditIcon } from "@chakra-ui/icons";
import { fmtCNPJ } from "@/lib/util/string";
import ModalMateriaisMassa from "./ModalMateriaisMassa";
import {
  Fundo,
  FundoCaracteristicaExtra,
  FundoSiteInstitucionalClassificacao,
  FundoSiteInstitucionalTipo,
  IndiceBenchmark,
  Mesa,
} from "@/lib/types/api/iv/v1";

export type ListagemProdutosProps = {
  fundos: Fundo[];
  mesas: Mesa[];
  classificacoes: FundoSiteInstitucionalClassificacao[];
  tipos: FundoSiteInstitucionalTipo[];
  fundoCaracteristicasExtras: FundoCaracteristicaExtra[];
  indicesBenchmark: IndiceBenchmark[];
  resizeRef: MutableRefObject<(() => void) | undefined>;
};

const round = {
  border: "1px solid",
  borderColor: "cinza.main",
  borderRadius: "8px",
  overflow: "hidden",
};

export function TabListagemProdutos({
  fundos,
  mesas,
  classificacoes,
  tipos,
  fundoCaracteristicasExtras,
  indicesBenchmark,
}: ListagemProdutosProps) {
  const [todosOsFundos, setTodosOsFundos] = useState<Fundo[]>(fundos);
  const [fundoSelecionado, setFundoSelecionado] = useState<Fundo>();

  const { user } = useUser();
  const httpClient = useHTTP({ withCredentials: true });

  const onFundosUpdateCallback = async (): Promise<void> => {
    const response = await httpClient.fetch("v1/fundos");

    if (!response.ok) {
      return;
    }

    const fundos = (await response.json()) as Fundo[];
    setTodosOsFundos(
      fundos.sort((fundoA, fundoB) => {
        return fundoA.nome.localeCompare(fundoB.nome);
      }),
    );
  };

  const podeAlterarFundosSiteInstitucional = user?.roles.some(
    (r) => r.nome === "Site Institucional - Alterar fundos",
  );

  const defaultColDef = {
    resizable: true,
    sortable: true,
  };

  const [columnDefs] = useState<ColDef[]>([
    {
      field: "status",
      headerName: "Status",
      filter: true,
      cellRenderer: ({ value }: ICellRendererParams) =>
        value === "Publicado" ? (
          <Text color="verde.main" textAlign="center">
            <Icon as={IoGlobeOutline} /> Publicado
          </Text>
        ) : (
          <Text color="rosa.main" textAlign="center">
            <Icon as={IoEyeOffOutline} /> Oculto
          </Text>
        ),
      width: 100,
    },
    {
      field: "pertence_a_classe",
      headerName: "Tipo",
      valueGetter({ data }) {
        return data["pertence_a_classe"] ? "Subclasse" : "Classe";
      },
    },
    {
      field: "cnpj",
      headerName: "CNPJ",
      filter: true,
      valueFormatter: ({ value }) => (value ? fmtCNPJ(value) : "---"),
    },
    {
      field: "isin",
      headerName: "ISIN",
      filter: true,
    },
    {
      field: "nome",
      headerName: "Nome",
      filter: true,
      resizable: true,
      flex: 1,
    },
    {
      headerName: "",
      width: 84,
      cellRenderer: ({ data }: ICellRendererParams) =>
        podeAlterarFundosSiteInstitucional && (
          <Button
            colorScheme="azul_3"
            borderRadius="full"
            leftIcon={<EditIcon />}
            size="xs"
            onClick={() => setFundoSelecionado(data)}
          >
            Editar
          </Button>
        ),
    },
  ]);

  const fs = useMemo(
    () =>
      todosOsFundos
        .sort((fundoA, fundoB) => fundoA.nome.localeCompare(fundoB.nome))
        .map((f) => ({ ...f, status: f.publicado ? "Publicado" : "Oculto" })),
    [todosOsFundos],
  );

  const { isOpen, onClose, onOpen } = useDisclosure();

  return (
    <>
      <VStack
        w="100%"
        h="100%"
        alignItems="stretch"
        {...{ ...round, overflow: "auto" }}
      >
        <Button size="sm" colorScheme="azul_3" onClick={onOpen}>
          Carregar materiais publicitários em massa
        </Button>
        <Box h="100%" className="ag-theme-alpine">
          <AgGridReact
            defaultColDef={defaultColDef}
            rowData={fs}
            columnDefs={columnDefs}
            animateRows={true}
            rowSelection="multiple"
          />
        </Box>
      </VStack>
      <ModalPublicacaoFundo
        fundo={fundoSelecionado}
        setFundo={setFundoSelecionado}
        mesas={mesas}
        classificacoes={classificacoes}
        tipos={tipos}
        caracteristicasExtras={fundoCaracteristicasExtras}
        indicesBenchmark={indicesBenchmark}
        onFundosUpdateCallback={onFundosUpdateCallback}
      />
      <ModalMateriaisMassa fundos={fundos} onClose={onClose} isOpen={isOpen} />
    </>
  );
}
