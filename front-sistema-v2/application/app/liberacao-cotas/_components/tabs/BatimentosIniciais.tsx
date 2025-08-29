import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "ag-grid-enterprise";
import "@/app/_components/grid/Grid.css";

import type { ReactNode } from "react";

import { Dispatch, SetStateAction, useState } from "react";
import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box,
  Divider,
  Heading,
  HStack,
  Icon,
  Text,
  VStack,
} from "@chakra-ui/react";
import TabPanelLayout from "../TabPanelLayout";
import InputElement from "../common/InputElement";
import inputElementData from "../../_utils/inputElementData";
import getFilesInputDisplay from "../../_utils/getFilesInputDisplay";
import {
  PrecoCreditoPrivado,
  CampoRequestLiberacaoCotas,
  ComparacaoPl,
  FundoInfo,
  FundoInfoComXml,
} from "@/lib/types/api/iv/liberacao-cotas";
import IVBrowserHTTPClient from "@/lib/util/http/vanguarda/IVBrowserHTTPClient";
import { useHTTP } from "@/lib/hooks";
import OutputCard from "../common/OutputCard";
import { AgGridReact } from "ag-grid-react";
import {
  cnpjCellRenderer,
  plCellRenderer,
  precoGenericoCellRenderer,
  textoCellRenderer,
} from "@/app/_ag-grid/cell-renderers";
import { ColDef, ValueGetterParams } from "ag-grid-enterprise";
import getFileName from "../../_utils/getFileName";
import { IoWarning } from "react-icons/io5";
import { APIWarning } from "@/lib/types/api/iv/v1";
import { dateFormatter } from "@/app/_ag-grid/formatters";

export function BatimentosIniciais() {
  const httpClient: IVBrowserHTTPClient = useHTTP({ withCredentials: true });
  const [filesInputXmlsAnbima401, setFilesInputXmlsAnbima401] =
    useState<FileList | null>(null);
  const [fileInputCaracteristicasFundos, setFileInputCaracteristicasFundos] =
    useState<FileList | null>(null);

  const [isLoadingXmlsFaltantes, setIsLoadingXmlsFaltantes] =
    useState<boolean>(false);
  const [fundosSemXml, setFundosSemXml] = useState<FundoInfo[] | null>(null);
  const [erroMensagemXmlsFaltantes, setErroMensagemXmlsFaltantes] = useState<
    string | null
  >(null);

  const [
    isLoadingBatimentoPrecosCreditoPrivado,
    setIsLoadingBatimentoPrecosCreditoPrivado,
  ] = useState<boolean>(false);
  const [precosCreditoPrivado, setPrecosCreditoPrivado] = useState<
    PrecoCreditoPrivado[] | null
  >(null);
  const [
    avisosBatimentoPrecosCreditoPrivado,
    setAvisosBatimentoPrecosCreditoPrivado,
  ] = useState<APIWarning[] | null>(null);
  const [
    erroMensagemBatimentoPrecosCreditoPrivado,
    setErroMensagemBatimentoPrecosCreditoPrivado,
  ] = useState<string | null>(null);

  const [isLoadingBatimentoPl, setIsLoadingBatimentoPl] =
    useState<boolean>(false);
  const [comparacoesPl, setComparacoesPl] = useState<ComparacaoPl[] | null>(
    null,
  );
  const [avisosBatimentoPl, setAvisosBatimentoPl] = useState<
    APIWarning[] | null
  >(null);
  const [erroMensagemBatimentoPl, setErroMensagemBatimentoPl] = useState<
    string | null
  >(null);

  const cardsData = [
    {
      cardTitle: "XMLs faltantes (abert. incluso)",
      isLoading: isLoadingXmlsFaltantes,
      hasWarning: false,
      hasError: erroMensagemXmlsFaltantes !== null,
      inputsStatuses: [
        {
          label: inputElementData.xmlsAnbima401.label,
          isOk: filesInputXmlsAnbima401 !== null,
        },
        {
          label: inputElementData.caracteristicasFundos.label,
          isOk: fileInputCaracteristicasFundos !== null,
        },
      ],
      requestCallback: async () => {
        handleXMLsFaltantesOnClick({
          httpClient: httpClient,
          url: "v1/liberacao-cotas/batimento/xmls-faltantes",
          requestBodyFieldsInputs: [
            {
              field: CampoRequestLiberacaoCotas.Zip_Arqs_Xml_Anbima_401,
              fileList: filesInputXmlsAnbima401,
            },
            {
              field: CampoRequestLiberacaoCotas.Xls_Caracteristicas_Fundos,
              fileList: fileInputCaracteristicasFundos,
            },
          ],
          isLoading: isLoadingXmlsFaltantes,
          setFundosSemXml: setFundosSemXml,
          setIsLoading: setIsLoadingXmlsFaltantes,
          setErroMensagem: setErroMensagemXmlsFaltantes,
        });
      },
    },
    {
      cardTitle: "Batimento Preços Crédito Privado",
      isLoading: isLoadingBatimentoPrecosCreditoPrivado,
      hasWarning: false,
      hasError: erroMensagemBatimentoPrecosCreditoPrivado !== null,
      inputsStatuses: [
        {
          label: inputElementData.xmlsAnbima401.label,
          isOk: filesInputXmlsAnbima401 !== null,
        },
        {
          label: inputElementData.caracteristicasFundos.label,
          isOk: fileInputCaracteristicasFundos !== null,
        },
      ],
      requestCallback: async () => {
        handleBatimentoPrecosCreditoPrivadoOnClick({
          httpClient: httpClient,
          url: "v1/liberacao-cotas/batimento/precos/credito-privado",
          requestBodyFieldsInputs: [
            {
              field: CampoRequestLiberacaoCotas.Zip_Arqs_Xml_Anbima_401,
              fileList: filesInputXmlsAnbima401,
            },
            {
              field: CampoRequestLiberacaoCotas.Xls_Caracteristicas_Fundos,
              fileList: fileInputCaracteristicasFundos,
            },
          ],
          isLoading: isLoadingBatimentoPrecosCreditoPrivado,
          setPrecosCreditoPrivado: setPrecosCreditoPrivado,
          setIsLoading: setIsLoadingBatimentoPrecosCreditoPrivado,
          setAvisos: setAvisosBatimentoPrecosCreditoPrivado,
          setErroMensagem: setErroMensagemBatimentoPrecosCreditoPrivado,
        });
      },
    },
    {
      cardTitle: "Batimento PL",
      isLoading: isLoadingBatimentoPl,
      hasWarning: avisosBatimentoPl !== null,
      hasError: erroMensagemBatimentoPl !== null,
      inputsStatuses: [
        {
          label: inputElementData.xmlsAnbima401.label,
          isOk: filesInputXmlsAnbima401 !== null,
        },
        {
          label: inputElementData.caracteristicasFundos.label,
          isOk: fileInputCaracteristicasFundos !== null,
        },
      ],
      requestCallback: async () => {
        handleBatimentoPlOnClick({
          httpClient: httpClient,
          url: "v1/liberacao-cotas/batimento/patrimonio-liquido",
          requestBodyFieldsInputs: [
            {
              field: CampoRequestLiberacaoCotas.Zip_Arqs_Xml_Anbima_401,
              fileList: filesInputXmlsAnbima401,
            },
            {
              field: CampoRequestLiberacaoCotas.Xls_Caracteristicas_Fundos,
              fileList: fileInputCaracteristicasFundos,
            },
          ],
          isLoading: isLoadingBatimentoPl,
          setComparacoesPl: setComparacoesPl,
          setIsLoading: setIsLoadingBatimentoPl,
          setAvisos: setAvisosBatimentoPl,
          setErroMensagem: setErroMensagemBatimentoPl,
        });
      },
    },
  ];

  const defaultColumnDef = {
    resizable: true,
    sortable: true,
    filter: true,
  };

  const xmlsFaltantesColDefsArr: ColDef[] = [
    {
      field: "codigo_britech",
      headerName: "Fundo Cód. Brit.",
      cellRenderer: textoCellRenderer,
    },
    {
      field: "codigo_administrador",
      headerName: "Fundo Cód. Adm.",
      cellRenderer: textoCellRenderer,
    },
    {
      field: "cnpj",
      headerName: "CNPJ",
      cellRenderer: textoCellRenderer,
    },
    {
      field: "nome",
      headerName: "Nome",
      cellRenderer: textoCellRenderer,
      flex: 1,
    },
    {
      field: "tipo_cota",
      headerName: "Tipo de Cota",
      cellRenderer: textoCellRenderer,
    },
  ];

  const batimentoPrecosCreditoPrivadoColDefsArr: ColDef[] = [
    {
      field: "codigo",
      headerName: "Cód. Ativo",
      cellRenderer: textoCellRenderer,
    },
    {
      field: "isin",
      headerName: "Isin Ativo",
      cellRenderer: textoCellRenderer,
    },
    {
      field: "data_referente",
      headerName: "Data Referente",
      cellRenderer: dateFormatter,
    },
    {
      field: "preco_unitario_posicao",
      headerName: "Preço Ativo",
      cellRenderer: precoGenericoCellRenderer,
    },
    {
      field: "fundo_info.codigo_britech",
      headerName: "Fundo Cód. Brit.",
      cellRenderer: textoCellRenderer,
    },
    {
      field: "fundo_info.custodiante",
      headerName: "Fundo Custodiante",
      cellRenderer: textoCellRenderer,
    },
    {
      field: "fundo_info.nome",
      headerName: "Fundo Nome",
      cellRenderer: textoCellRenderer,
      width: 450,
    },
    {
      field: "fundo_info.tipo_cota",
      headerName: "Tipo de Cota",
      cellRenderer: textoCellRenderer,
    },
    {
      field: "fundo_info.codigo_administrador",
      headerName: "Fundo Cód. Adm.",
      cellRenderer: textoCellRenderer,
    },
    {
      field: "fundo_info.cnpj",
      headerName: "Fundo CNPJ",
      cellRenderer: textoCellRenderer,
    },
    {
      field: "fundo_info.nome_arq_xml_anbima_401",
      headerName: "Nome XML",
      cellRenderer: textoCellRenderer,
      width: 550,
    },
  ];

  const batimentoPlsColDefsArr: ColDef[] = [
    {
      field: "fundo_codigo_britech",
      headerName: "Cód. Brit.",
      cellRenderer: textoCellRenderer,
      width: 140,
    },
    {
      field: "fundo_codigo_administrador",
      headerName: "Cód. Adm.",
      cellRenderer: textoCellRenderer,
      width: 140,
    },
    {
      field: "fundo_cnpj",
      headerName: "CNPJ",
      cellRenderer: cnpjCellRenderer,
      width: 200,
    },
    {
      field: "fundo_nome",
      headerName: "Nome",
      cellRenderer: textoCellRenderer,
      width: 450,
    },
    {
      field: "data_referente",
      headerName: "Data Referente",
      cellRenderer: dateFormatter,
      width: 150,
    },
    {
      field: "pl_xml",
      headerName: "PL (XML)",
      cellRenderer: plCellRenderer,
      width: 120,
    },
    {
      field: "pl_calculado",
      headerName: "PL (Calc.)",
      cellRenderer: plCellRenderer,
      width: 120,
    },
    {
      field: "diferenca_pl",
      headerName: "Diferença",
      cellRenderer: precoGenericoCellRenderer,
      width: 120,
    },
  ];

  const avisosColDefsArr: ColDef[] = [
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

  const [xmlFaltantesColDefs] = useState<ColDef[]>(xmlsFaltantesColDefsArr);
  const [batimentoPrecosCreditoPrivadoColDefs] = useState<ColDef[]>(
    batimentoPrecosCreditoPrivadoColDefsArr,
  );
  const [batimentoPlsColDefs] = useState<ColDef[]>(batimentoPlsColDefsArr);
  const [avisosColDefs] = useState<ColDef[]>(avisosColDefsArr);

  return (
    <>
      <TabPanelLayout
        leftComponent={
          <>
            <VStack width="100%" alignItems="flex-start">
              <Heading size="md" alignSelf="flex-start" fontWeight="normal">
                Importações
              </Heading>
              <Divider />
              <VStack>
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
                  isMultiFile={true}
                  stateValue={getFileName(fileInputCaracteristicasFundos)}
                  setState={setFileInputCaracteristicasFundos}
                />
              </VStack>
            </VStack>
          </>
        }
        rightComponent={
          <>
            <Heading size="md" alignSelf="flex-start" fontWeight="normal">
              Batimentos
            </Heading>
            <Divider />
            <VStack width="100%" alignItems="flex-start" gap="24px">
              <HStack flexWrap="wrap" justifyContent="flex-start">
                {cardsData.map((card, index) => (
                  <OutputCard
                    key={index}
                    width="400px"
                    cardTitle={card.cardTitle}
                    inputsStatuses={card.inputsStatuses}
                    isLoading={card.isLoading}
                    hasWarning={card.hasWarning}
                    hasError={card.hasError}
                    requestCallback={card.requestCallback}
                  />
                ))}
              </HStack>
              <Accordion
                allowMultiple
                width="100%"
                style={{
                  display:
                    fundosSemXml !== null ||
                    precosCreditoPrivado !== null ||
                    comparacoesPl !== null ||
                    avisosBatimentoPrecosCreditoPrivado !== null ||
                    avisosBatimentoPl !== null ||
                    erroMensagemXmlsFaltantes !== null ||
                    erroMensagemBatimentoPrecosCreditoPrivado !== null ||
                    erroMensagemBatimentoPl !== null
                      ? "block"
                      : "none",
                }}
              >
                <BatimentoInicialAccordionItem
                  itemsInfo={[
                    {
                      titulo: "XMLs Faltantes",
                      erro: {
                        condicao: erroMensagemXmlsFaltantes !== null,
                        elemento: (
                          <Box placeSelf="flex-start">
                            <Divider />
                            <Text marginX="16px" marginY="8px">
                              {erroMensagemXmlsFaltantes}
                            </Text>
                          </Box>
                        ),
                      },
                      aviso: {
                        condicao: false,
                        elemento: null,
                      },
                      sucesso: {
                        condicao: fundosSemXml !== null,
                        elemento: (
                          <>
                            {fundosSemXml?.length == 0 ? (
                              <Box placeSelf="flex-start">
                                <Divider />
                                <Text marginX="16px" marginY="8px">
                                  <Text>Todos os XMLs estão presentes</Text>
                                </Text>
                              </Box>
                            ) : (
                              <Box
                                className="ag-theme-alpine"
                                h="600px"
                                overflowX="auto"
                                overflowY="auto"
                                borderRadius="8px"
                                w="100%"
                              >
                                <AgGridReact
                                  defaultColDef={defaultColumnDef}
                                  columnDefs={xmlFaltantesColDefs}
                                  rowData={fundosSemXml}
                                  animateRows={true}
                                />
                              </Box>
                            )}
                          </>
                        ),
                      },
                    },
                    {
                      titulo: "Batimento Preços Ativos Crédito Privado",
                      erro: {
                        condicao:
                          erroMensagemBatimentoPrecosCreditoPrivado !== null,
                        elemento: (
                          <Box placeSelf="flex-start">
                            <Divider />
                            <Text marginX="16px" marginY="8px">
                              {erroMensagemBatimentoPrecosCreditoPrivado}
                            </Text>
                          </Box>
                        ),
                      },
                      aviso: {
                        condicao: avisosBatimentoPrecosCreditoPrivado !== null,
                        elemento: (
                          <VStack
                            width="100%"
                            height="600px"
                            alignItems="flex-start"
                          >
                            <HStack alignItems="center">
                              <Heading as="h3" size="sm">
                                Avisos
                              </Heading>
                              <Text>
                                <Icon
                                  color="amarelo.main"
                                  as={IoWarning}
                                  boxSize={6}
                                />
                              </Text>
                            </HStack>
                            <Box
                              className="ag-theme-alpine"
                              h="600px"
                              overflowX="auto"
                              overflowY="auto"
                              borderRadius="8px"
                              w="100%"
                            >
                              <AgGridReact
                                defaultColDef={defaultColumnDef}
                                columnDefs={avisosColDefs}
                                rowData={avisosBatimentoPrecosCreditoPrivado}
                                animateRows={true}
                              />
                            </Box>
                          </VStack>
                        ),
                      },
                      sucesso: {
                        condicao: precosCreditoPrivado !== null,
                        elemento: (
                          <>
                            {precosCreditoPrivado?.length === 0 ? (
                              <Box placeSelf="flex-start">
                                <Divider />
                                <Text marginX="16px" marginY="8px">
                                  <Text>
                                    Não há ativos de crédito privado com preços
                                    diferentes
                                  </Text>
                                </Text>
                              </Box>
                            ) : (
                              <Box
                                className="ag-theme-alpine"
                                h="600px"
                                overflowX="auto"
                                overflowY="auto"
                                borderRadius="8px"
                                w="100%"
                              >
                                <AgGridReact
                                  defaultColDef={defaultColumnDef}
                                  columnDefs={
                                    batimentoPrecosCreditoPrivadoColDefs
                                  }
                                  rowData={precosCreditoPrivado}
                                  animateRows={true}
                                />
                              </Box>
                            )}
                          </>
                        ),
                      },
                    },
                    {
                      titulo: "Batimento PLs",
                      erro: {
                        condicao: erroMensagemBatimentoPl !== null,
                        elemento: (
                          <Box placeSelf="flex-start">
                            <Divider />
                            <Text marginX="16px" marginY="8px">
                              {erroMensagemBatimentoPl}
                            </Text>
                          </Box>
                        ),
                      },
                      aviso: {
                        condicao: avisosBatimentoPl !== null,
                        elemento: (
                          <VStack
                            width="100%"
                            height="600px"
                            alignItems="flex-start"
                          >
                            <HStack alignItems="center">
                              <Heading as="h3" size="sm">
                                Avisos
                              </Heading>
                              <Text>
                                <Icon
                                  color="amarelo.main"
                                  as={IoWarning}
                                  boxSize={6}
                                />
                              </Text>
                            </HStack>
                            <Box
                              className="ag-theme-alpine"
                              h="600px"
                              overflowX="auto"
                              overflowY="auto"
                              borderRadius="8px"
                              w="100%"
                            >
                              <AgGridReact
                                defaultColDef={defaultColumnDef}
                                columnDefs={avisosColDefs}
                                rowData={avisosBatimentoPl}
                                animateRows={true}
                              />
                            </Box>
                          </VStack>
                        ),
                      },
                      sucesso: {
                        condicao: comparacoesPl !== null,
                        elemento: (
                          <VStack width="100%" gap="12px">
                            <Box
                              className="ag-theme-alpine"
                              h="600px"
                              overflowX="auto"
                              overflowY="auto"
                              borderRadius="8px"
                              w="100%"
                            >
                              <AgGridReact
                                defaultColDef={defaultColumnDef}
                                columnDefs={batimentoPlsColDefs}
                                rowData={comparacoesPl}
                                animateRows={true}
                              />
                            </Box>
                          </VStack>
                        ),
                      },
                    },
                  ]}
                />
              </Accordion>
            </VStack>
          </>
        }
      />
    </>
  );
}

async function handleXMLsFaltantesOnClick({
  httpClient,
  url,
  requestBodyFieldsInputs,
  isLoading,
  setFundosSemXml,
  setIsLoading,
  setErroMensagem,
}: {
  httpClient: IVBrowserHTTPClient;
  url: string;
  requestBodyFieldsInputs: {
    field: CampoRequestLiberacaoCotas;
    fileList: FileList | null;
  }[];
  isLoading: boolean;
  setFundosSemXml: Dispatch<SetStateAction<FundoInfo[] | null>>;
  setIsLoading: Dispatch<SetStateAction<boolean>>;
  setErroMensagem: Dispatch<SetStateAction<any>>;
}) {
  if (isLoading) {
    return;
  }

  setFundosSemXml(null);
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

  const responseJSON = (await response.json()) as {
    fundos_sem_xml: FundoInfo[];
  };
  const fundosSemXml: FundoInfo[] = responseJSON.fundos_sem_xml;

  setFundosSemXml(fundosSemXml);
  setIsLoading(false);
  return;
}

async function handleBatimentoPlOnClick({
  httpClient,
  url,
  requestBodyFieldsInputs,
  isLoading,
  setComparacoesPl,
  setIsLoading,
  setAvisos,
  setErroMensagem,
}: {
  httpClient: IVBrowserHTTPClient;
  url: string;
  requestBodyFieldsInputs: {
    field: CampoRequestLiberacaoCotas;
    fileList: FileList | null;
  }[];
  isLoading: boolean;
  setComparacoesPl: Dispatch<SetStateAction<ComparacaoPl[] | null>>;
  setIsLoading: Dispatch<SetStateAction<boolean>>;
  setAvisos: Dispatch<SetStateAction<APIWarning[] | null>>;
  setErroMensagem: Dispatch<SetStateAction<any>>;
}) {
  if (isLoading) {
    return;
  }

  setComparacoesPl(null);
  setAvisos(null);
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
    setComparacoesPl(null);
    setAvisos(null);
    setErroMensagem(null);

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

  const responseJSON = (await response.json()) as {
    batimento_pls: any[];
    warnings: APIWarning[];
  };
  const batimentoPls: ComparacaoPl[] = responseJSON.batimento_pls
    .map((comparacao: any) => {
      const fundoCodigoBritech: string = comparacao.fundo_codigo_britech;
      const fundoCnpj: string = comparacao.fundo_cnpj;
      const fundoNome: string = comparacao.fundo_nome;
      const fundoCodigoAdministrador: string =
        comparacao.fundo_codigo_administrador;
      const dataReferente: string = comparacao.data_referente;
      const plXml: number = parseFloat(comparacao.pl_xml);
      const plCalculado: number = parseFloat(comparacao.pl_calculado);
      const diferencaPl: number = parseFloat(comparacao.diferenca_pl);

      const comparacaoPl: ComparacaoPl = {
        fundo_codigo_britech: fundoCodigoBritech,
        fundo_cnpj: fundoCnpj,
        fundo_nome: fundoNome,
        fundo_codigo_administrador: fundoCodigoAdministrador,
        data_referente: dataReferente,
        pl_xml: plXml,
        pl_calculado: plCalculado,
        diferenca_pl: diferencaPl,
      };

      return comparacaoPl;
    })
    .sort((a: ComparacaoPl, b: ComparacaoPl) => {
      return b.diferenca_pl - a.diferenca_pl;
    });

  setComparacoesPl(batimentoPls);
  if (responseJSON.warnings) {
    setAvisos(responseJSON.warnings);
  }

  setIsLoading(false);
}

async function handleBatimentoPrecosCreditoPrivadoOnClick({
  httpClient,
  url,
  requestBodyFieldsInputs,
  isLoading,
  setPrecosCreditoPrivado,
  setIsLoading,
  setAvisos,
  setErroMensagem,
}: {
  httpClient: IVBrowserHTTPClient;
  url: string;
  requestBodyFieldsInputs: {
    field: CampoRequestLiberacaoCotas;
    fileList: FileList | null;
  }[];
  isLoading: boolean;
  setPrecosCreditoPrivado: Dispatch<
    SetStateAction<PrecoCreditoPrivado[] | null>
  >;
  setIsLoading: Dispatch<SetStateAction<boolean>>;
  setAvisos: Dispatch<SetStateAction<APIWarning[] | null>>;
  setErroMensagem: Dispatch<SetStateAction<any>>;
}) {
  if (isLoading) {
    return;
  }

  setPrecosCreditoPrivado(null);
  setAvisos(null);
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
    setPrecosCreditoPrivado(null);
    setAvisos(null);

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

  const responseJSON = (await response.json()) as {
    ativos: any[];
    warnings: APIWarning[];
  };
  const ativosCreditoPrivado: PrecoCreditoPrivado[] = responseJSON.ativos
    .map((ativo: any) => {
      const ativoCodigo: string = ativo.codigo as string;
      const ativoIsin: string | undefined = ativo.isin as string | undefined;
      const preco: number = parseFloat(ativo.preco_unitario_posicao);
      const data: string = ativo.data_referente;
      const fundoInfo: FundoInfoComXml = ativo.fundo_info as FundoInfoComXml;

      const ativoCreditoPrivado: PrecoCreditoPrivado = {
        codigo: ativoCodigo,
        isin: ativoIsin,
        preco_unitario_posicao: preco,
        data_referente: data,
        fundo_info: fundoInfo,
      };

      return ativoCreditoPrivado;
    })
    .sort((a: PrecoCreditoPrivado, b: PrecoCreditoPrivado): number => {
      const codigoComparison = a.codigo.localeCompare(b.codigo);
      if (codigoComparison !== 0) {
        return codigoComparison;
      }

      return a.preco_unitario_posicao - b.preco_unitario_posicao;
    });

  setPrecosCreditoPrivado(ativosCreditoPrivado);
  if (responseJSON.warnings) {
    setAvisos(responseJSON.warnings);
  }

  setIsLoading(false);
}

function BatimentoInicialAccordionItem({
  itemsInfo,
}: {
  itemsInfo: {
    titulo: string;
    erro: { condicao: boolean; elemento: ReactNode };
    aviso: { condicao: boolean; elemento: ReactNode };
    sucesso: { condicao: boolean; elemento: ReactNode };
  }[];
}) {
  return itemsInfo.map(({ titulo, erro, aviso, sucesso }, index) => {
    if (erro.condicao || aviso.condicao || sucesso.condicao) {
      return (
        <AccordionItem key={index}>
          <Text>
            <AccordionButton>
              <HStack flex="1" justifyContent="space-between">
                <HStack alignItems="center">
                  <Heading size="md">{titulo}</Heading>
                  <Text>
                    {erro.condicao ? (
                      <Icon color="rosa.main" as={IoWarning} boxSize={6} />
                    ) : (
                      aviso.condicao && (
                        <Icon color="amarelo.main" as={IoWarning} boxSize={6} />
                      )
                    )}
                  </Text>
                </HStack>
                <AccordionIcon />
              </HStack>
            </AccordionButton>
          </Text>
          <AccordionPanel>
            <VStack width="100%" gap="12px">
              {erro.condicao ? (
                erro.elemento
              ) : (
                <>
                  {sucesso.condicao && sucesso.elemento}
                  {aviso.condicao && aviso.elemento}
                </>
              )}
            </VStack>
          </AccordionPanel>
        </AccordionItem>
      );
    }

    return <></>;
  });
}
