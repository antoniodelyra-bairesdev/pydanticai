import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "ag-grid-enterprise";
import "@/app/_components/grid/Grid.css";

import { useState } from "react";
import { Box, Divider, Heading, HStack, Text, VStack } from "@chakra-ui/react";
import TabPanelLayout from "../TabPanelLayout";
import InputElement from "../common/InputElement";
import inputElementData from "../../_utils/inputElementData";
import getFilesInputDisplay from "../../_utils/getFilesInputDisplay";
import IVBrowserHTTPClient from "@/lib/util/http/vanguarda/IVBrowserHTTPClient";
import { useAsync, useHTTP } from "@/lib/hooks";
import OutputCard from "../common/OutputCard";
import getFileName from "../../_utils/getFileName";
import { wait } from "@/lib/util/misc";
import getExportCallback from "../../_utils/getExportCallback";
import { CampoRequestLiberacaoCotas } from "@/lib/types/api/iv/liberacao-cotas";
import ErroInfo from "../common/ErroInfo";
import AvisoAccordion from "../common/AvisoAccordion";
import { AgGridReact } from "ag-grid-react";

type FundoInvestido = {
  cnpj: string;
  nome: string | null;
  gestor: string | null;
};

type FundoInvestidoPosicao = FundoInvestido & { data_posicao: string };

export default function RelatoriosD2() {
  const httpClient: IVBrowserHTTPClient = useHTTP({ withCredentials: true });

  const [filesInputXmlsAnbima401Mes, setFilesInputXmlsAnbima401Mes] =
    useState<FileList | null>(null);
  const [filesInputXmlsAnbima401, setFilesInputXmlsAnbima401] =
    useState<FileList | null>(null);
  const [
    fileInputCadastroFundosInvestidos,
    setFileInputCadastroFundosInvestidos,
  ] = useState<FileList | null>(null);

  const [
    carregandoCotasInvestidosFaltantes,
    setCarregandoCotasInvestidosFaltantes,
  ] = useState(false);
  const [
    avisosCotasFundosInvestidosFaltantes,
    setAvisosCotasFundosInvestidosFaltantes,
  ] = useState<any>(null);
  const [
    erroCotasFundosInvestidosFaltantes,
    setErroCotasFundosInvestidosFaltantes,
  ] = useState<string | null>(null);
  const [cotasFundosInvestidosFaltantes, setCotasFundosInvestidosFaltantes] =
    useState<FundoInvestidoPosicao[]>([]);

  const [carregandoMiddleFundosInvGest, setCarregandoMiddleFundosInvGest] =
    useState(false);
  const [avisosMiddleFundosInvGest, setAvisosMiddleFundosInvGest] =
    useState<any>(null);
  const [erroMiddleFundosInvGest, setErroMiddleFundosInvGest] =
    useState<any>(null);

  const [carregandoMiddlePosFundosInv, setCarregandoMiddlePosFundosInv] =
    useState(false);
  const [avisosMiddlePosFundosInv, setAvisosMiddlePosFundosInv] =
    useState<any>(null);
  const [erroMiddlePosFundosInv, setErroMiddlePosFundosInv] = useState<
    string | null
  >(null);

  const cardsData = [
    {
      cardTitle: "Cotas de fundos investidos faltantes",
      isLoading: carregandoCotasInvestidosFaltantes,
      hasWarning: false,
      hasError: false,
      inputsStatuses: [
        {
          label: inputElementData.fundosInvestidosD2.label,
          isOk: fileInputCadastroFundosInvestidos !== null,
        },
        {
          label: inputElementData.xmlsAnbima401.label,
          isOk: filesInputXmlsAnbima401 !== null,
        },
      ],
      requestCallback: async () => {
        try {
          setCarregandoCotasInvestidosFaltantes(true);
          if (!fileInputCadastroFundosInvestidos || !filesInputXmlsAnbima401)
            return;
          const body = new FormData();
          for (const file of filesInputXmlsAnbima401) {
            body.append(
              CampoRequestLiberacaoCotas.Zip_Arqs_Xml_Anbima_401,
              file,
            );
          }
          for (const file of fileInputCadastroFundosInvestidos) {
            body.append(
              CampoRequestLiberacaoCotas.Xlsx_Fundos_Investidos,
              file,
            );
          }
          const response = await httpClient.fetch(
            "v1/liberacao-cotas/precos/cotas-fundos-investidos-faltantes",
            {
              method: "POST",
              body,
              multipart: true,
              hideToast: {
                clientError: true,
                serverError: true,
              },
            },
          );
          if (!response.ok) {
            const responseJSON = (await response.json()) as
              | {
                  detail: { request_id: string; message: string };
                }
              | {
                  detail: string;
                };

            if (typeof responseJSON.detail == "string") {
              setErroCotasFundosInvestidosFaltantes(responseJSON.detail);
              return;
            }

            const errorId = (
              responseJSON as {
                detail: { request_id: string; message: string };
              }
            ).detail.request_id;
            const message = (
              responseJSON as {
                detail: { request_id: string; message: string };
              }
            ).detail.message;

            setErroCotasFundosInvestidosFaltantes(
              message + " Código do erro: " + errorId,
            );
            return;
          }
          const { avisos, faltantes } = (await response.json()) as {
            avisos: any;
            faltantes: Record<string, FundoInvestido[]>;
          };
          const pos: FundoInvestidoPosicao[] = [];
          for (const [data_pos, fundos] of Object.entries(faltantes)) {
            for (const fundo of fundos) {
              pos.push({
                data_posicao: data_pos,
                cnpj: fundo.cnpj,
                nome: fundo.nome,
                gestor: fundo.gestor,
              });
            }
          }

          setAvisosCotasFundosInvestidosFaltantes(avisos);
          setCotasFundosInvestidosFaltantes(pos);
        } catch (e) {
          setErroCotasFundosInvestidosFaltantes(String(e));
        } finally {
          setCarregandoCotasInvestidosFaltantes(false);
        }
      },
    },
    {
      cardTitle: "Middle - Fundos investidos + Gestoras",
      isLoading: carregandoMiddleFundosInvGest,
      hasWarning: false,
      hasError: false,
      inputsStatuses: [
        {
          label: inputElementData.fundosInvestidosD2.label,
          isOk: fileInputCadastroFundosInvestidos !== null,
        },
        {
          label: inputElementData.xmlsAnbima401.label,
          isOk: filesInputXmlsAnbima401 !== null,
        },
      ],
      requestCallback: async () => {
        getExportCallback({
          httpClient,
          url: "v1/liberacao-cotas/relatorios/middle/fundos-investidos-gestoras",
          isExportLoading: carregandoMiddleFundosInvGest,
          requestBodyFieldsInputs: [
            {
              field: CampoRequestLiberacaoCotas.Xlsx_Fundos_Investidos,
              fileList: fileInputCadastroFundosInvestidos,
            },
            {
              field: CampoRequestLiberacaoCotas.Zip_Arqs_Xml_Anbima_401,
              fileList: filesInputXmlsAnbima401,
            },
          ],
          setAvisos: setAvisosMiddleFundosInvGest,
          setErroMensagem: setErroMiddleFundosInvGest,
          setIsExportLoading: setCarregandoMiddleFundosInvGest,
        });
      },
    },
    {
      cardTitle: "Middle - Posições de fundos investidos",
      isLoading: carregandoMiddlePosFundosInv,
      hasWarning: false,
      hasError: false,
      inputsStatuses: [
        {
          label: inputElementData.fundosInvestidosD2.label,
          isOk: fileInputCadastroFundosInvestidos !== null,
        },
        {
          label: inputElementData.xmlsAnbima401Mes.label,
          isOk: filesInputXmlsAnbima401Mes !== null,
        },
      ],
      requestCallback: async () => {
        getExportCallback({
          httpClient,
          url: "v1/liberacao-cotas/relatorios/middle/posicao-fundos-investidos",
          isExportLoading: carregandoMiddlePosFundosInv,
          requestBodyFieldsInputs: [
            {
              field: CampoRequestLiberacaoCotas.Xlsx_Fundos_Investidos,
              fileList: fileInputCadastroFundosInvestidos,
            },
            {
              field: CampoRequestLiberacaoCotas.Zip_Arqs_Xml_Anbima_401,
              fileList: filesInputXmlsAnbima401Mes,
            },
          ],
          setAvisos: setAvisosMiddlePosFundosInv,
          setErroMensagem: setErroMiddlePosFundosInv,
          setIsExportLoading: setCarregandoMiddlePosFundosInv,
        });
      },
    },
  ];

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
                  hint={inputElementData.fundosInvestidosD2.hint}
                  label={inputElementData.fundosInvestidosD2.label}
                  isMultiFile={true}
                  stateValue={getFileName(fileInputCadastroFundosInvestidos)}
                  setState={setFileInputCadastroFundosInvestidos}
                />
                <InputElement
                  hint={inputElementData.xmlsAnbima401.hint}
                  label={inputElementData.xmlsAnbima401.label}
                  isMultiFile={true}
                  stateValue={getFilesInputDisplay(filesInputXmlsAnbima401)}
                  setState={setFilesInputXmlsAnbima401}
                />
                <InputElement
                  hint={inputElementData.xmlsAnbima401Mes.hint}
                  label={inputElementData.xmlsAnbima401Mes.label}
                  isMultiFile={true}
                  stateValue={getFileName(filesInputXmlsAnbima401Mes)}
                  setState={setFilesInputXmlsAnbima401Mes}
                />
              </VStack>
            </VStack>
          </>
        }
        rightComponent={
          <>
            <Heading size="md" alignSelf="flex-start" fontWeight="normal">
              Exportações
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
              {avisosCotasFundosInvestidosFaltantes /*||
                avisosBonds ||
                avisosRendaFixaNaoPrecificadoAnbima ||
                avisosCreditoPrivadoMarcacaoAMercado ||
                avisosCotasFundos*/ && (
                <VStack alignItems="stretch" width="100%" gap="12px">
                  {cotasFundosInvestidosFaltantes && (
                    <Box h="512px" className="ag-theme-alpine">
                      <Heading size="md" mb="12px">
                        Cotas de fundos investidos faltantes
                      </Heading>
                      <GridInvestidosFaltantes
                        dados={cotasFundosInvestidosFaltantes}
                      />
                    </Box>
                  )}
                  {avisosCotasFundosInvestidosFaltantes?.length && (
                    <AvisoAccordion
                      titulo="Cotas de fundos investidos faltantes"
                      avisos={avisosCotasFundosInvestidosFaltantes}
                    />
                  )}
                  {/* {avisosBonds && (
                    <AvisoAccordion
                      titulo="Bonds Offshore"
                      avisos={avisosBonds}
                    />
                  )}
                  {avisosRendaFixaNaoPrecificadoAnbima && (
                    <AvisoAccordion
                      titulo="Crédito Privado"
                      avisos={avisosRendaFixaNaoPrecificadoAnbima}
                    />
                  )}
                  {avisosCreditoPrivadoMarcacaoAMercado && (
                    <AvisoAccordion
                      titulo="Crédito Privado marcação a mercado"
                      avisos={avisosCreditoPrivadoMarcacaoAMercado}
                    />
                  )}
                  {avisosCotasFundos && (
                    <AvisoAccordion
                      titulo="Cotas de Fundos"
                      avisos={avisosCotasFundos}
                    />
                  )} */}
                </VStack>
              )}
              {erroCotasFundosInvestidosFaltantes /* ||
                erroMensagemBonds ||
                erroMensagemRendaFixaNaoPrecificadoAnbima ||
                erroMensagemCreditoPrivadoMarcacaoAMercado ||
                erroMensagemCotasFundos*/ && (
                <VStack width="100%" gap="12px">
                  {erroCotasFundosInvestidosFaltantes && (
                    <ErroInfo
                      cardTitulo="Bolsa e BMF"
                      erroMensagem={erroCotasFundosInvestidosFaltantes}
                    />
                  )}
                  {/* {erroMensagemBonds && (
                    <ErroInfo
                      cardTitulo="Bonds Offshore"
                      erroMensagem={erroMensagemBonds}
                    />
                  )}
                  {erroMensagemRendaFixaNaoPrecificadoAnbima && (
                    <ErroInfo
                      cardTitulo="Renda Fixa não precificada pela ANBIMA"
                      erroMensagem={erroMensagemRendaFixaNaoPrecificadoAnbima}
                    />
                  )}
                  {erroMensagemCreditoPrivadoMarcacaoAMercado && (
                    <ErroInfo
                      cardTitulo="Crédito Privado marcação a mercado"
                      erroMensagem={erroMensagemCreditoPrivadoMarcacaoAMercado}
                    />
                  )}
                  {erroMensagemCotasFundos && (
                    <ErroInfo
                      cardTitulo="Cotas de Fundos"
                      erroMensagem={erroMensagemCotasFundos}
                    />
                  )} */}
                </VStack>
              )}
            </VStack>
          </>
        }
      />
    </>
  );
}

const GridInvestidosFaltantes = ({
  dados,
}: {
  dados: FundoInvestidoPosicao[];
}) => {
  return (
    <AgGridReact
      defaultColDef={{
        resizable: true,
        sortable: true,
        filter: true,
      }}
      columnDefs={[
        {
          headerName: "Data posição",
          field: "data_posicao",
        },
        {
          headerName: "CNPJ",
          field: "cnpj",
        },
        {
          headerName: "Fundo",
          field: "nome",
          flex: 1,
        },
        {
          headerName: "Gestor",
          field: "gestor",
        },
      ]}
      rowData={dados}
      animateRows={true}
    />
  );
};
