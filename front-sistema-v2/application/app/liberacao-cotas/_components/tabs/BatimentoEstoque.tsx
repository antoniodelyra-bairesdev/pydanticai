import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "ag-grid-enterprise";
import "@/app/_components/grid/Grid.css";

import type IVBrowserHTTPClient from "@/lib/util/http/vanguarda/IVBrowserHTTPClient";

import { AgGridReact } from "ag-grid-react";
import {
  ColDef,
  GridReadyEvent,
  ICellRendererParams,
  ProcessCellForExportParams,
  ValueGetterParams,
} from "ag-grid-community";
import { Dispatch, SetStateAction, useCallback, useRef, useState } from "react";
import {
  Box,
  Button,
  Divider,
  Heading,
  HStack,
  Icon,
  Input,
  Progress,
  StackDivider,
  Text,
  VStack,
} from "@chakra-ui/react";

import InputElement from "../common/InputElement";
import inputElementData from "../../_utils/inputElementData";
import getFilesInputDisplay from "../../_utils/getFilesInputDisplay";
import { useHTTP } from "@/lib/hooks";
import getFileName from "../../_utils/getFileName";
import {
  AtivoCarteira,
  CampoRequestLiberacaoCotas,
  TipoAtivo,
} from "@/lib/types/api/iv/liberacao-cotas";
import { ComparacaoAtivo } from "@/lib/types/api/iv/liberacao-cotas";
import { dateFormatter } from "@/app/_ag-grid/formatters";
import {
  cnpjCellRenderer,
  numeroGenericoCellRenderer,
  precoGenericoCellRenderer,
  textoCellRenderer,
} from "@/app/_ag-grid/cell-renderers";
import ErroInfo from "../common/ErroInfo";
import {
  IoCaretDown,
  IoCaretUp,
  IoCheckmark,
  IoWarning,
} from "react-icons/io5";
import HResize from "@/app/_components/misc/HResize";
import Hint from "@/app/_components/texto/Hint";
import { APIWarning } from "@/lib/types/api/iv/v1";
import VResize from "@/app/_components/misc/VResize";

export function BatimentoEstoque() {
  const [usdbrl, setUsdbrl] = useState<number | null>(null);
  if (Number.isNaN(usdbrl) == true) {
    setUsdbrl(null);
  }

  const [filesInputXmlsAnbima401, setFilesInputXmlsAnbima401] =
    useState<FileList | null>(null);
  const [fileInputEstoqueRendaFixa, setFileInputEstoqueRendaFixa] =
    useState<FileList | null>(null);
  const [fileInputEstoqueRendaVariavel, setFileInputEstoqueRendaVariavel] =
    useState<FileList | null>(null);
  const [fileInputEstoqueFuturo, setFileInputEstoqueFuturo] =
    useState<FileList | null>(null);
  const [fileInputEstoqueCota, setFileInputEstoqueCota] =
    useState<FileList | null>(null);
  const [fileInputDeparaDerivativos, setFileInputDeparaDerivativos] =
    useState<FileList | null>(null);
  const [fileInputDeparaCotas, setFileInputDeparaCotas] =
    useState<FileList | null>(null);
  const [fileInputCaracteristicasFundos, setFileInputCaracteristicasFundos] =
    useState<FileList | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [erroMensagem, setErroMensagem] = useState<any>(null);

  const httpClient: IVBrowserHTTPClient = useHTTP({ withCredentials: true });
  const [estoque, setEstoque] = useState<ComparacaoAtivo[]>([]);

  const [avisos, setAvisos] = useState<APIWarning[]>([]);

  const estoqueExCotasGridRef = useRef<AgGridReact<ComparacaoAtivo>>(null);
  const estoqueCotasGridRef = useRef<AgGridReact<ComparacaoAtivo>>(null);

  const processCellForClipboard: (
    colA: (data: any) => number,
    colB: (data: any) => number,
  ) => (params: ProcessCellForExportParams) => any =
    (colA, colB) => (params) => {
      return colA(params.node?.data) - colB(params.node?.data);
    };

  const estoqueExCotasInitialFilterModel = {
    diferenca_quantidade: {
      filterType: "number",
      operator: "OR",
      condition1: {
        filterType: "number",
        type: "blank",
      },
      condition2: {
        filterType: "number",
        type: "greaterThan",
        filter: 0.01,
      },
    },
  };

  const estoqueCotasInitialFilterModel = {
    diferenca_financeiro: {
      filterType: "number",
      operator: "OR",
      condition1: {
        filterType: "number",
        type: "blank",
      },
      condition2: {
        filterType: "number",
        type: "greaterThan",
        filter: 0.01,
      },
    },
  };

  const onBatimentoExCotasGridReady = useCallback((params: GridReadyEvent) => {
    params.api.setFilterModel(estoqueExCotasInitialFilterModel);
  }, []);

  const onBatimentoCotasGridReady = useCallback((params: GridReadyEvent) => {
    params.api.setFilterModel(estoqueCotasInitialFilterModel);
  }, []);

  const clearFiltersBatimentoExCotas = useCallback(() => {
    estoqueExCotasGridRef.current!.api.setFilterModel(null);
  }, []);
  const resetFiltersBatimentoExCotas = useCallback(() => {
    estoqueExCotasGridRef.current!.api.setFilterModel(
      estoqueExCotasInitialFilterModel,
    );
  }, []);

  const clearFiltersBatimentoCotas = useCallback(() => {
    estoqueCotasGridRef.current!.api.setFilterModel(null);
  }, []);
  const resetFiltersBatimentoCotas = useCallback(() => {
    estoqueCotasGridRef.current!.api.setFilterModel(
      estoqueCotasInitialFilterModel,
    );
  }, []);

  const defaultColumnDef = {
    resizable: true,
    sortable: true,
    filter: true,
  };

  const commonTableColDefsArr: ColDef[] = [
    {
      field: "fundo_codigo_britech",
      headerName: "Fundo Brit.",
      width: 90,
      cellRenderer: textoCellRenderer,
    },
    {
      field: "fundo_nome",
      headerName: "Nome",
      width: 256,
      cellRenderer: textoCellRenderer,
    },
    {
      field: "fundo_cnpj",
      headerName: "CNPJ",
      width: 160,
      cellRenderer: cnpjCellRenderer,
      hide: true,
    },
    {
      field: "fundo_codigo_administrador",
      headerName: "Cód. Adm.",
      width: 160,
      cellRenderer: textoCellRenderer,
      hide: true,
    },
    {
      field: "data_referente",
      headerName: "Data Referente",
      width: 128,
      valueFormatter: dateFormatter,
    },
    {
      headerName: "Tipo",
      width: 100,
      cellRenderer: textoCellRenderer,
      valueGetter: (params: ValueGetterParams) => {
        switch (params.data.tipo_ativo) {
          case TipoAtivo.Renda_Fixa:
            return "Renda Fixa";
          case TipoAtivo.Renda_Variavel:
            return "Renda Variável";
          case TipoAtivo.Futuro:
            return "Futuro";
          case TipoAtivo.Cota:
            return "Cota Fundo";
          default:
            return params.data.tipo_ativo;
        }
      },
    },
    {
      field: "ativo_xml.codigo",
      headerName: "Cód. (XML)",
      width: 144,
      cellRenderer: textoCellRenderer,
    },
    {
      field: "ativo_britech.codigo",
      headerName: "Cód. (Brit.)",
      width: 144,
      cellRenderer: textoCellRenderer,
    },
    {
      field: "ativo_xml.vencimento",
      headerName: "Vencimento (XML)",
      width: 144,
      valueFormatter: dateFormatter,
    },
    {
      field: "ativo_xml.isin",
      headerName: "ISIN (XML)",
      width: 130,
      hide: true,
      cellRenderer: textoCellRenderer,
    },
    {
      field: "ativo_britech.isin",
      headerName: "ISIN (Brit.)",
      width: 150,
      hide: true,
      cellRenderer: textoCellRenderer,
    },
    {
      field: "diferenca_quantidade",
      headerName: "Dif. Qtd",
      width: 140,
      cellRenderer: (params: ICellRendererParams) => {
        const dif = Math.sign(
          (params.data?.ativo_xml?.quantidade ?? 0) -
            (params.data?.ativo_britech?.quantidade ?? 0),
        );
        const ico = {
          [-1]: IoCaretDown,
          [0]: IoCheckmark,
          [1]: IoCaretUp,
        }[dif];

        const col = {
          [-1]: "rosa.main",
          [0]: "cinza.main",
          [1]: "verde.main",
        }[dif];
        return (
          <HStack>
            {params.value && <Icon as={ico} w="8px" h="8px" color={col} />}
            {numeroGenericoCellRenderer(params)}
          </HStack>
        );
      },
      filter: "agNumberColumnFilter",
    },
    {
      field: "ativo_xml.quantidade",
      headerName: "Qtd. (XML)",
      width: 140,
      cellRenderer: numeroGenericoCellRenderer,
    },
    {
      field: "ativo_britech.quantidade",
      headerName: "Qtd. (Brit.)",
      width: 140,
      cellRenderer: numeroGenericoCellRenderer,
    },
  ];

  const estoqueExCotasTableColDefsArr: ColDef[] = [
    ...commonTableColDefsArr,
    {
      field: "diferenca_financeiro",
      headerName: "Dif. Financeiro",
      width: 140,
      hide: true,
      cellRenderer: precoGenericoCellRenderer,
      filter: "agNumberColumnFilter",
      sort: "desc",
    },
    {
      field: "ativo_xml.financeiro",
      headerName: "Financeiro (XML)",
      width: 160,
      hide: true,
      cellRenderer: precoGenericoCellRenderer,
    },
    {
      field: "ativo_britech.financeiro",
      headerName: "Financeiro (Brit.)",
      width: 160,
      hide: true,
      cellRenderer: precoGenericoCellRenderer,
    },
    {
      field: "diferenca_pu",
      headerName: "Dif. Preço",
      width: 140,
      hide: true,
      cellRenderer: precoGenericoCellRenderer,
      filter: "agNumberColumnFilter",
    },
    {
      field: "ativo_xml.preco_unitario_posicao",
      headerName: "PU (XML)",
      width: 120,
      hide: true,
      cellRenderer: precoGenericoCellRenderer,
    },
    {
      field: "ativo_britech.preco_unitario_posicao",
      headerName: "PU (Brit.)",
      width: 125,
      hide: true,
      cellRenderer: precoGenericoCellRenderer,
    },
  ];

  const cotas = commonTableColDefsArr.reduce(
    (map, colDef) => {
      map[colDef?.field ?? "---"] ??= { ...colDef };
      return map;
    },
    {} as Record<string, ColDef>,
  );

  cotas["ativo_xml.codigo"].hide = true;
  cotas["ativo_xml.isin"].hide = false;
  cotas["diferenca_quantidade"].hide = true;
  cotas["ativo_xml.quantidade"].hide = true;
  cotas["ativo_britech.quantidade"].hide = true;
  cotas["ativo_xml.vencimento"].hide = true;

  const estoqueCotasTableColDefsArr: ColDef[] = [
    ...Object.values(cotas),
    {
      field: "diferenca_financeiro",
      headerName: "Dif. Financeiro",
      width: 140,
      cellRenderer: (params: ICellRendererParams) => {
        const dif = Math.sign(
          (params.data?.ativo_xml?.financeiro ?? 0) -
            (params.data?.ativo_britech?.financeiro ?? 0),
        );
        const ico = {
          [-1]: IoCaretDown,
          [0]: IoCheckmark,
          [1]: IoCaretUp,
        }[dif];

        const col = {
          [-1]: "rosa.main",
          [0]: "cinza.main",
          [1]: "verde.main",
        }[dif];
        return (
          <HStack>
            {params.value && <Icon as={ico} w="8px" h="8px" color={col} />}
            {precoGenericoCellRenderer(params)}
          </HStack>
        );
      },
      filter: "agNumberColumnFilter",
      sort: "desc",
    },
    {
      field: "ativo_xml.financeiro",
      headerName: "Financeiro (XML)",
      width: 160,
      cellRenderer: precoGenericoCellRenderer,
    },
    {
      field: "ativo_britech.financeiro",
      headerName: "Financeiro (Brit.)",
      width: 160,
      cellRenderer: precoGenericoCellRenderer,
    },
    {
      field: "diferenca_pu",
      headerName: "Dif. Preço",
      width: 140,
      cellRenderer: precoGenericoCellRenderer,
      filter: "agNumberColumnFilter",
    },
    {
      field: "ativo_britech.preco_unitario_posicao",
      headerName: "PU (Brit.)",
      width: 125,
      cellRenderer: precoGenericoCellRenderer,
    },
    {
      field: "ativo_xml.preco_unitario_posicao",
      headerName: "PU (XML)",
      width: 120,
      cellRenderer: precoGenericoCellRenderer,
    },
  ];

  const avisosTableColDefsArr: ColDef[] = [
    {
      field: "tipo_id",
      headerName: "Tipo ID",
      width: 335,
      cellRenderer: textoCellRenderer,
    },
    {
      field: "id",
      headerName: "ID",
      width: 320,
      cellRenderer: textoCellRenderer,
    },
    {
      valueGetter: (params: ValueGetterParams) => {
        return params.data.mensagens[0];
      },
      headerName: "mensagem",
      flex: 1,
      cellRenderer: textoCellRenderer,
    },
  ];

  const [estoqueExCotasTableColDefs] = useState<ColDef[]>(
    estoqueExCotasTableColDefsArr,
  );
  const [estoqueCotasTableColDefs] = useState<ColDef[]>(
    estoqueCotasTableColDefsArr,
  );
  const [avisosTableColDefs] = useState<ColDef[]>(avisosTableColDefsArr);

  return (
    <HResize
      width="100%"
      height="100%"
      startingLeftWidth={450}
      leftElement={
        <VStack alignItems="flex-start" height="100%" userSelect="text">
          <HStack>
            <Text fontSize="md">USD Cupom Limpo:</Text>
            <Input
              height="40px"
              fontSize="md"
              width="180px"
              type="number"
              onChange={(ev) => {
                setUsdbrl(parseFloat(ev.target.value));
              }}
              value={usdbrl ?? undefined}
            />
          </HStack>
          <VStack width="100%" alignItems="flex-start">
            <Heading size="md" alignSelf="flex-start" fontWeight="normal">
              Importações
            </Heading>
            <Divider />
            <InputElement
              hint={inputElementData.xmlsAnbima401.hint}
              label={inputElementData.xmlsAnbima401.label}
              isMultiFile={true}
              stateValue={getFilesInputDisplay(filesInputXmlsAnbima401)}
              setState={setFilesInputXmlsAnbima401}
            />
            <InputElement
              hint={inputElementData.caracteristicasFundos.hint}
              label={inputElementData.caracteristicasFundos.label}
              isMultiFile={false}
              stateValue={getFileName(fileInputCaracteristicasFundos)}
              setState={setFileInputCaracteristicasFundos}
            />
            <InputElement
              hint={inputElementData.estoqueRendaFixa.hint}
              label={inputElementData.estoqueRendaFixa.label}
              isMultiFile={false}
              stateValue={getFileName(fileInputEstoqueRendaFixa)}
              setState={setFileInputEstoqueRendaFixa}
            />
            <InputElement
              hint={inputElementData.estoqueRendaVariavel.hint}
              label={inputElementData.estoqueRendaVariavel.label}
              isMultiFile={false}
              stateValue={getFileName(fileInputEstoqueRendaVariavel)}
              setState={setFileInputEstoqueRendaVariavel}
            />
            <InputElement
              hint={inputElementData.estoqueFuturo.hint}
              label={inputElementData.estoqueFuturo.label}
              isMultiFile={false}
              stateValue={getFileName(fileInputEstoqueFuturo)}
              setState={setFileInputEstoqueFuturo}
            />
            <InputElement
              hint={inputElementData.estoqueCota.hint}
              label={inputElementData.estoqueCota.label}
              isMultiFile={false}
              stateValue={getFileName(fileInputEstoqueCota)}
              setState={setFileInputEstoqueCota}
            />
            <InputElement
              hint={inputElementData.deparaCotasFundos.hint}
              label={inputElementData.deparaCotasFundos.label}
              isMultiFile={false}
              stateValue={getFileName(fileInputDeparaCotas)}
              setState={setFileInputDeparaCotas}
            />
            <InputElement
              hint={inputElementData.deparaDerivativos.hint}
              label={inputElementData.deparaDerivativos.label}
              isMultiFile={false}
              stateValue={getFileName(fileInputDeparaDerivativos)}
              setState={setFileInputDeparaDerivativos}
            />
            <Button
              width="450px"
              colorScheme="verde"
              isDisabled={
                !isButtonEnabled(isLoading, usdbrl, [
                  filesInputXmlsAnbima401,
                  fileInputEstoqueRendaFixa,
                  fileInputEstoqueRendaVariavel,
                  fileInputEstoqueFuturo,
                  fileInputEstoqueCota,
                  fileInputDeparaCotas,
                  fileInputDeparaDerivativos,
                  fileInputCaracteristicasFundos,
                ])
              }
              onClick={() => {
                handleOnClick({
                  httpClient: httpClient,
                  url: `v1/liberacao-cotas/batimento/estoque?usdbrl=${usdbrl}`,
                  requestBodyFieldsInputs: [
                    {
                      field: CampoRequestLiberacaoCotas.Zip_Arqs_Xml_Anbima_401,
                      fileList: filesInputXmlsAnbima401,
                    },
                    {
                      field: CampoRequestLiberacaoCotas.Xlsx_Estoque_Renda_Fixa,
                      fileList: fileInputEstoqueRendaFixa,
                    },
                    {
                      field:
                        CampoRequestLiberacaoCotas.Xlsx_Estoque_Renda_Variavel,
                      fileList: fileInputEstoqueRendaVariavel,
                    },
                    {
                      field: CampoRequestLiberacaoCotas.Xlsx_Estoque_Futuro,
                      fileList: fileInputEstoqueFuturo,
                    },
                    {
                      field: CampoRequestLiberacaoCotas.Xlsx_Estoque_Cota,
                      fileList: fileInputEstoqueCota,
                    },
                    {
                      field:
                        CampoRequestLiberacaoCotas.Xlsx_Depara_Cotas_Fundos,
                      fileList: fileInputDeparaCotas,
                    },
                    {
                      field: CampoRequestLiberacaoCotas.Xlsm_Depara_Derivativos,
                      fileList: fileInputDeparaDerivativos,
                    },
                    {
                      field:
                        CampoRequestLiberacaoCotas.Xls_Caracteristicas_Fundos,
                      fileList: fileInputCaracteristicasFundos,
                    },
                  ],
                  isLoading: isLoading,
                  setIsLoading: setIsLoading,
                  setEstoque: setEstoque,
                  setAvisos: setAvisos,
                  setErroMensagem: setErroMensagem,
                });
              }}
            >
              Gerar Estoque
            </Button>
          </VStack>
        </VStack>
      }
      rightElement={
        <VStack alignItems="flex-start" userSelect="text">
          <VStack flex={1} width="100%" alignItems="flex-start">
            <VStack width="100%" alignContent="flex-start">
              <Heading
                size="md"
                alignSelf="flex-start"
                gap="24px"
                fontWeight="normal"
              >
                <Text>
                  Estoque{" "}
                  {erroMensagem && (
                    <Icon color="rosa.main" as={IoWarning} boxSize={6} />
                  )}
                </Text>
              </Heading>
              <Divider />
            </VStack>
            {erroMensagem ? (
              <Text>{erroMensagem}</Text>
            ) : (
              <>
                {isLoading ? (
                  <Box width="100%">
                    <Progress isIndeterminate colorScheme="verde" />
                  </Box>
                ) : (
                  <>
                    {estoque.length > 0 && (
                      <VStack width="100%" gap="24px">
                        <VStack
                          width="100%"
                          alignSelf="flex-start"
                          alignItems="flex-start"
                          gap="0px"
                        >
                          <Hint>Controles</Hint>
                          <HStack
                            justifyContent="flex-end"
                            w="100%"
                            border="1px solid"
                            borderColor="cinza.main"
                            borderRadius="8px"
                            p="6px"
                            gap="12px"
                          >
                            <HStack
                              divider={<StackDivider />}
                              justifyContent="space-between"
                              alignItems="center"
                              border="1px solid"
                              borderColor="cinza.main"
                              overflow="hidden"
                              borderRadius="8px"
                              p="6px"
                            >
                              <Text fontSize="xs" flex={1}>
                                Ex-cotas
                              </Text>
                              <HStack gap="5px">
                                <Button
                                  colorScheme="azul_4"
                                  size="xs"
                                  onClick={() => resetFiltersBatimentoExCotas()}
                                >
                                  Redefinir filtros
                                </Button>
                                <Button
                                  colorScheme="verde"
                                  size="xs"
                                  onClick={() => clearFiltersBatimentoExCotas()}
                                >
                                  Limpar filtros
                                </Button>
                              </HStack>
                            </HStack>
                            <HStack
                              divider={<StackDivider />}
                              justifyContent="space-between"
                              alignItems="center"
                              border="1px solid"
                              borderColor="cinza.main"
                              overflow="hidden"
                              borderRadius="8px"
                              p="6px"
                            >
                              <Text fontSize="xs" flex={1}>
                                Cotas
                              </Text>
                              <HStack gap="5px">
                                <Button
                                  colorScheme="azul_4"
                                  size="xs"
                                  onClick={() => resetFiltersBatimentoCotas()}
                                >
                                  Redefinir filtros
                                </Button>
                                <Button
                                  colorScheme="verde"
                                  size="xs"
                                  onClick={() => clearFiltersBatimentoCotas()}
                                >
                                  Limpar filtros
                                </Button>
                              </HStack>
                            </HStack>
                          </HStack>
                        </VStack>
                        <VResize
                          minHeight="1200px"
                          width="100%"
                          topElement={
                            <>
                              <Hint>Estoque ex-cotas</Hint>
                              <Box
                                userSelect="text"
                                className="ag-theme-alpine"
                                h="100%"
                                overflowX="scroll"
                                overflowY="auto"
                                borderRadius="8px"
                                w="100%"
                              >
                                <AgGridReact
                                  ref={estoqueExCotasGridRef}
                                  onGridReady={onBatimentoExCotasGridReady}
                                  defaultColDef={defaultColumnDef}
                                  columnDefs={estoqueExCotasTableColDefs}
                                  rowData={getEstoqueExCotas(estoque)}
                                  animateRows={true}
                                  enableRangeSelection
                                  processCellForClipboard={processCellForClipboard(
                                    (data) =>
                                      Number(data?.ativo_xml?.quantidade ?? 0),
                                    (data) =>
                                      Number(
                                        data?.ativo_britech?.quantidade ?? 0,
                                      ),
                                  )}
                                />
                              </Box>
                            </>
                          }
                          bottomElement={
                            <>
                              <Hint>Estoque cotas</Hint>
                              <Box
                                userSelect="text"
                                className="ag-theme-alpine"
                                h="100%"
                                overflowX="scroll"
                                overflowY="auto"
                                borderRadius="8px"
                                w="100%"
                              >
                                <AgGridReact
                                  ref={estoqueCotasGridRef}
                                  onGridReady={onBatimentoCotasGridReady}
                                  defaultColDef={defaultColumnDef}
                                  columnDefs={estoqueCotasTableColDefs}
                                  rowData={getEstoqueCotas(estoque)}
                                  animateRows={true}
                                  enableRangeSelection
                                  processCellForClipboard={processCellForClipboard(
                                    (data) =>
                                      Number(data?.ativo_xml?.financeiro ?? 0),
                                    (data) =>
                                      Number(
                                        data?.ativo_britech?.financeiro ?? 0,
                                      ),
                                  )}
                                />
                              </Box>
                            </>
                          }
                        />
                        <>
                          {avisos.length > 0 && (
                            <VStack
                              width="100%"
                              alignItems="flex-start"
                              gap="0px"
                            >
                              <Hint>Avisos</Hint>
                              <Box
                                userSelect="text"
                                className="ag-theme-alpine"
                                h="400px"
                                overflowX="auto"
                                overflowY="auto"
                                borderRadius="8px"
                                w="100%"
                              >
                                <AgGridReact
                                  defaultColDef={defaultColumnDef}
                                  columnDefs={avisosTableColDefs}
                                  rowData={avisos}
                                  animateRows={true}
                                  enableRangeSelection
                                />
                              </Box>
                            </VStack>
                          )}
                        </>
                        {erroMensagem && (
                          <ErroInfo
                            cardTitulo="Erros"
                            erroMensagem={erroMensagem}
                          />
                        )}
                      </VStack>
                    )}
                  </>
                )}
              </>
            )}
          </VStack>
        </VStack>
      }
    />
  );
}

function isButtonEnabled(
  isLoading: boolean,
  usdbrl: number | null,
  filesInputs: (FileList | null)[],
): boolean {
  if (isLoading) {
    return false;
  }

  if (!usdbrl) {
    return false;
  }

  for (let fileInput of filesInputs) {
    if (fileInput == null) {
      return false;
    }
  }

  return true;
}

function getEstoqueExCotas(estoque: ComparacaoAtivo[]): ComparacaoAtivo[] {
  return estoque.filter((item) => item.tipo_ativo !== TipoAtivo.Cota);
}

function getEstoqueCotas(estoque: ComparacaoAtivo[]): ComparacaoAtivo[] {
  return estoque.filter((item) => item.tipo_ativo == TipoAtivo.Cota);
}

async function handleOnClick({
  httpClient,
  url,
  requestBodyFieldsInputs,
  isLoading,
  setEstoque,
  setAvisos,
  setErroMensagem,
  setIsLoading,
}: {
  httpClient: IVBrowserHTTPClient;
  url: string;
  requestBodyFieldsInputs: {
    field: CampoRequestLiberacaoCotas;
    fileList: FileList | null;
  }[];
  isLoading: boolean;
  setEstoque: Dispatch<SetStateAction<ComparacaoAtivo[]>>;
  setAvisos: Dispatch<SetStateAction<APIWarning[]>>;
  setErroMensagem: Dispatch<SetStateAction<any>>;
  setIsLoading: Dispatch<SetStateAction<boolean>>;
}) {
  if (isLoading) {
    return;
  }

  setErroMensagem(null);
  setIsLoading(true);

  const body = new FormData();
  for (const { field, fileList } of requestBodyFieldsInputs) {
    if (!fileList) {
      setIsLoading(false);
      return;
    }

    for (let i = 0; i < fileList.length; ++i) {
      const file: File = fileList[i];
      body.append(field, file);
    }
  }

  const response = await httpClient.fetch(url, {
    method: "POST",
    body: body,
    multipart: true,
    hideToast: {
      clientError: true,
      serverError: true,
    },
  });

  if (!response.ok) {
    const responseJSON = (await response.json()) as
      | {
          detail: { request_id: string; message: string };
        }
      | {
          detail: string;
        };

    if (typeof responseJSON.detail == "string") {
      setErroMensagem(responseJSON.detail);
      setIsLoading(false);
      return;
    }

    const errorId = (
      responseJSON as { detail: { request_id: string; message: string } }
    ).detail.request_id;
    const message = (
      responseJSON as { detail: { request_id: string; message: string } }
    ).detail.message;

    setErroMensagem(message + " Código do erro: " + errorId);
    setIsLoading(false);
    return;
  }

  const responseJSON = (await response.json()) as any;
  const comparacoesNaoTratadas: any[] = responseJSON.estoque;
  const warnings: APIWarning[] = responseJSON.warnings as APIWarning[];

  const comparacoes: ComparacaoAtivo[] = getComparacoesTratadas(
    comparacoesNaoTratadas,
  ).sort((a: ComparacaoAtivo, b: ComparacaoAtivo) => {
    if (!a.diferenca_quantidade) {
      return -1;
    }
    if (!b.diferenca_quantidade) {
      return 1;
    }

    return b.diferenca_quantidade - a.diferenca_quantidade;
  });

  setEstoque(comparacoes);
  setAvisos(warnings);
  setIsLoading(false);
  return;
}

function getComparacoesTratadas(
  comparacoesNaoTratadas: any[],
): ComparacaoAtivo[] {
  return comparacoesNaoTratadas.map((comparacao) => {
    const fundoCodigoBritech: string = comparacao.fundo_codigo_britech;
    const fundoNome: string = comparacao.fundo_nome;
    const fundoCnpj: string = comparacao.fundo_cnpj;
    const fundoCodigoAdministrador: string =
      comparacao.fundo_codigo_administrador;
    const dataReferente: string = comparacao.data_referente;
    const tipoAtivo: TipoAtivo = comparacao.tipo_ativo as TipoAtivo;

    let diferencaPu: number | null = null;
    if (
      comparacao.diferenca_pu !== null &&
      comparacao.diferenca_pu !== undefined
    ) {
      diferencaPu = parseFloat(comparacao.diferenca_pu);
    }
    let diferencaQuantidade: number | null = null;
    if (
      comparacao.diferenca_quantidade !== null &&
      comparacao.diferenca_quantidade !== undefined
    ) {
      diferencaQuantidade = parseFloat(comparacao.diferenca_quantidade);
    }
    let diferencaFinanceiro: number | null = null;
    if (
      comparacao.diferenca_financeiro !== null &&
      comparacao.diferenca_financeiro !== undefined
    ) {
      diferencaFinanceiro = parseFloat(comparacao.diferenca_financeiro);
    }

    let ativoXml: AtivoCarteira | null = null;
    if (comparacao.ativo_xml !== null && comparacao.ativo_xml !== undefined) {
      ativoXml = {
        isin: comparacao.ativo_xml?.isin!,
        codigo: comparacao.ativo_xml?.codigo!,
        quantidade: parseFloat(comparacao.ativo_xml?.quantidade!),
        preco_unitario_posicao: parseFloat(
          comparacao.ativo_xml?.preco_unitario_posicao!,
        ),
        financeiro: parseFloat(comparacao.ativo_xml?.financeiro),
        tipo: comparacao.ativo_xml?.tipo!,
        vencimento: comparacao.ativo_xml?.vencimento,
      } as AtivoCarteira;
    }

    let ativoBritech: AtivoCarteira | null = null;
    if (
      comparacao.ativo_britech !== null &&
      comparacao.ativo_britech !== undefined
    ) {
      ativoBritech = {
        isin: comparacao.ativo_britech?.isin!,
        codigo: comparacao.ativo_britech?.codigo!,
        quantidade: parseFloat(comparacao.ativo_britech?.quantidade!),
        preco_unitario_posicao: parseFloat(
          comparacao.ativo_britech?.preco_unitario_posicao!,
        ),
        financeiro: parseFloat(comparacao.ativo_britech?.financeiro),
        tipo: comparacao.ativo_britech?.tipo!,
        vencimento: comparacao.ativo_britech?.vencimento,
      } as AtivoCarteira;
    }

    return {
      fundo_codigo_britech: fundoCodigoBritech,
      fundo_nome: fundoNome,
      fundo_cnpj: fundoCnpj,
      fundo_codigo_administrador: fundoCodigoAdministrador,
      data_referente: dataReferente,
      diferenca_pu: diferencaPu,
      diferenca_quantidade: diferencaQuantidade,
      diferenca_financeiro: diferencaFinanceiro,
      ativo_xml: ativoXml,
      ativo_britech: ativoBritech,
      tipo_ativo: tipoAtivo,
    } as ComparacaoAtivo;
  });
}
