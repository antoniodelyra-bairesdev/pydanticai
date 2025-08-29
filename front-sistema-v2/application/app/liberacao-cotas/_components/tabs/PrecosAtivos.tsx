"use client";

import { useState } from "react";

import {
  Divider,
  Heading,
  HStack,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react";
import InputElement from "../common/InputElement";
import OutputCard from "../common/OutputCard";
import inputElementData from "../../_utils/inputElementData";
import getFileName from "../../_utils/getFileName";
import getExportCallback from "../../_utils/getExportCallback";
import { useHTTP } from "@/lib/hooks";
import { CampoRequestLiberacaoCotas } from "@/lib/types/api/iv/liberacao-cotas";
import TabPanelLayout from "../TabPanelLayout";
import AvisoAccordion from "../common/AvisoAccordion";
import ErroInfo from "../common/ErroInfo";
import getFilesInputDisplay from "../../_utils/getFilesInputDisplay";

export function PrecosAtivos() {
  const [usdbrl, setUsdbrl] = useState<number | null>(null);
  if (Number.isNaN(usdbrl) == true) {
    setUsdbrl(null);
  }

  const [filesInputXmlsAnbima401, setFilesInputXmlsAnbima401] =
    useState<FileList | null>(null);
  const [fileInputDeparaDerivativos, setFileInputDeparaDerivativos] =
    useState<FileList | null>(null);
  const [fileInputDeparaBondsOffshore, setFileInputDeparaBondsOffshore] =
    useState<FileList | null>(null);
  const [
    fileInputDeparaCreditoPrivado,
    setFileInputDeparaCreditoPrivadoNaoPrecificadoAnbima,
  ] = useState<FileList | null>(null);
  const [
    fileInputDeparaAtivosMarcadosNaCurva,
    setFileInputDeparaAtivosMarcadosNaCurva,
  ] = useState<FileList | null>(null);
  const [fileInputDeparaCotasFundos, setFileInputDeparaCotasFundos] =
    useState<FileList | null>(null);
  const [fileInputCaracteristicasFundos, setFileInputCaracteristicasFundos] =
    useState<FileList | null>(null);

  const [isLoadingBolsaBmf, setIsLoadingBolsaBmf] = useState<boolean>(false);
  const [avisosBolsaBmf, setAvisosBolsaBmf] = useState<any>(null);
  const [erroMensagemBolsaBmf, setErroMensagemBolsaBmf] = useState<
    string | null
  >(null);

  const [isLoadingBonds, setIsLoadingBonds] = useState<boolean>(false);
  const [avisosBonds, setAvisosBonds] = useState<any>(null);
  const [erroMensagemBonds, setErroMensagemBonds] = useState<string | null>(
    null,
  );

  const [
    isLoadingRendaFixaNaoPrecificadoAnbima,
    setIsLoadingRendaFixaNaoPrecificadoAnbima,
  ] = useState<boolean>(false);
  const [
    avisosRendaFixaNaoPrecificadoAnbima,
    setAvisosRendaFixaNaoPrecificadoAnbima,
  ] = useState<any>(null);
  const [
    erroMensagemRendaFixaNaoPrecificadoAnbima,
    setErroMensagemRendaFixaNaoPrecificadoAnima,
  ] = useState<string | null>(null);

  const [
    isLoadingCreditoPrivadoMarcacaoAMercado,
    setIsLoadingCreditoPrivadoMarcacaoAMercado,
  ] = useState<boolean>(false);
  const [
    avisosCreditoPrivadoMarcacaoAMercado,
    setAvisosCreditoPrivadoMarcacaoAMercado,
  ] = useState<any>(null);
  const [
    erroMensagemCreditoPrivadoMarcacaoAMercado,
    setErroMensagemCreditoPrivadoMarcacaoAMercado,
  ] = useState<string | null>(null);

  const [isLoadingCotasFundos, setIsLoadingCotasFundos] =
    useState<boolean>(false);
  const [avisosCotasFundos, setAvisosCotasFundos] = useState<any>(null);
  const [erroMensagemCotasFundos, setErroMensagemCotasFundos] = useState<
    string | null
  >(null);

  const httpClient = useHTTP({ withCredentials: true });

  const cardsData = [
    {
      cardTitle: "Bolsa e BMF",
      isLoading: isLoadingBolsaBmf,
      hasWarning: avisosBolsaBmf !== null,
      hasError: erroMensagemBolsaBmf !== null,
      inputsStatuses: [
        {
          label: inputElementData.deparaDerivativos.label,
          isOk: fileInputDeparaDerivativos !== null,
        },
        {
          label: inputElementData.xmlsAnbima401.label,
          isOk: filesInputXmlsAnbima401 !== null,
        },
        {
          label: inputElementData.dolarCupomLimpo.label,
          isOk: usdbrl !== null,
        },
      ],
      exportCallback: async () => {
        getExportCallback({
          httpClient: httpClient,
          url: `v1/liberacao-cotas/precos/bolsa-bmf?usdbrl=${usdbrl}`,
          isExportLoading: isLoadingBolsaBmf,
          setIsExportLoading: setIsLoadingBolsaBmf,
          setAvisos: setAvisosBolsaBmf,
          setErroMensagem: setErroMensagemBolsaBmf,
          requestBodyFieldsInputs: [
            {
              field: CampoRequestLiberacaoCotas.Xlsm_Depara_Derivativos,
              fileList: fileInputDeparaDerivativos,
            },
            {
              field: CampoRequestLiberacaoCotas.Zip_Arqs_Xml_Anbima_401,
              fileList: filesInputXmlsAnbima401,
            },
          ],
        });
      },
    },
    {
      cardTitle: "Bonds Offshore",
      isLoading: isLoadingBonds,
      hasWarning: avisosBonds !== null,
      hasError: erroMensagemBonds !== null,
      inputsStatuses: [
        {
          label: inputElementData.deparaBondsOffshore.label,
          isOk: fileInputDeparaBondsOffshore !== null,
        },
        {
          label: inputElementData.xmlsAnbima401.label,
          isOk: filesInputXmlsAnbima401 !== null,
        },
        {
          label: inputElementData.dolarCupomLimpo.label,
          isOk: usdbrl !== null,
        },
      ],
      exportCallback: async () => {
        getExportCallback({
          httpClient: httpClient,
          url: `v1/liberacao-cotas/precos/bonds-offshore?usdbrl=${usdbrl}`,
          isExportLoading: isLoadingBonds,
          setIsExportLoading: setIsLoadingBonds,
          setAvisos: setAvisosBonds,
          setErroMensagem: setErroMensagemBonds,
          requestBodyFieldsInputs: [
            {
              field: CampoRequestLiberacaoCotas.Xlsx_Depara_Bonds,
              fileList: fileInputDeparaBondsOffshore,
            },
            {
              field: CampoRequestLiberacaoCotas.Zip_Arqs_Xml_Anbima_401,
              fileList: filesInputXmlsAnbima401,
            },
          ],
        });
      },
    },
    {
      cardTitle: "Renda Fixa não precificada pela ANBIMA",
      isLoading: isLoadingRendaFixaNaoPrecificadoAnbima,
      hasWarning: avisosRendaFixaNaoPrecificadoAnbima !== null,
      hasError: erroMensagemRendaFixaNaoPrecificadoAnbima !== null,
      inputsStatuses: [
        {
          label: inputElementData.deparaCreditoPrivado.label,
          isOk: fileInputDeparaCreditoPrivado !== null,
        },
        {
          label: inputElementData.deparaAtivosMarcadosNaCurva.label,
          isOk: fileInputDeparaAtivosMarcadosNaCurva !== null,
        },
        {
          label: inputElementData.xmlsAnbima401.label,
          isOk: filesInputXmlsAnbima401 !== null,
        },
        {
          label: inputElementData.caracteristicasFundos.label,
          isOk: fileInputCaracteristicasFundos !== null,
        },
      ],
      exportCallback: async () => {
        getExportCallback({
          httpClient: httpClient,
          url: "v1/liberacao-cotas/precos/renda-fixa/nao-precificados-anbima-fundos-bradesco",
          isExportLoading: isLoadingRendaFixaNaoPrecificadoAnbima,
          setIsExportLoading: setIsLoadingRendaFixaNaoPrecificadoAnbima,
          setAvisos: setAvisosRendaFixaNaoPrecificadoAnbima,
          setErroMensagem: setErroMensagemRendaFixaNaoPrecificadoAnima,
          requestBodyFieldsInputs: [
            {
              field: CampoRequestLiberacaoCotas.Xlsx_Depara_Credito_Privado,
              fileList: fileInputDeparaCreditoPrivado,
            },
            {
              field:
                CampoRequestLiberacaoCotas.Xlsx_Depara_Ativos_Marcados_Na_Curva,
              fileList: fileInputDeparaAtivosMarcadosNaCurva,
            },
            {
              field: CampoRequestLiberacaoCotas.Zip_Arqs_Xml_Anbima_401,
              fileList: filesInputXmlsAnbima401,
            },
            {
              field: CampoRequestLiberacaoCotas.Xls_Caracteristicas_Fundos,
              fileList: fileInputCaracteristicasFundos,
            },
          ],
        });
      },
    },
    {
      cardTitle: "Crédito Privado marcação a mercado",
      isLoading: isLoadingCreditoPrivadoMarcacaoAMercado,
      hasWarning: avisosCreditoPrivadoMarcacaoAMercado !== null,
      hasError: erroMensagemCreditoPrivadoMarcacaoAMercado !== null,
      inputsStatuses: [
        {
          label: inputElementData.deparaCreditoPrivado.label,
          isOk: fileInputDeparaCreditoPrivado !== null,
        },
        {
          label: inputElementData.xmlsAnbima401.label,
          isOk: filesInputXmlsAnbima401 !== null,
        },
        {
          label: inputElementData.caracteristicasFundos.label,
          isOk: fileInputCaracteristicasFundos !== null,
        },
      ],
      exportCallback: async () => {
        getExportCallback({
          httpClient: httpClient,
          url: "v1/liberacao-cotas/precos/credito-privado/marcacao-mercado-em-fundos-nao-bradesco",
          isExportLoading: isLoadingCreditoPrivadoMarcacaoAMercado,
          setIsExportLoading: setIsLoadingCreditoPrivadoMarcacaoAMercado,
          setAvisos: setAvisosCreditoPrivadoMarcacaoAMercado,
          setErroMensagem: setErroMensagemCreditoPrivadoMarcacaoAMercado,
          requestBodyFieldsInputs: [
            {
              field: CampoRequestLiberacaoCotas.Xlsx_Depara_Credito_Privado,
              fileList: fileInputDeparaCreditoPrivado,
            },
            {
              field: CampoRequestLiberacaoCotas.Zip_Arqs_Xml_Anbima_401,
              fileList: filesInputXmlsAnbima401,
            },
            {
              field: CampoRequestLiberacaoCotas.Xls_Caracteristicas_Fundos,
              fileList: fileInputCaracteristicasFundos,
            },
          ],
        });
      },
    },
    {
      cardTitle: "Cotas de Fundos (abert. incluso)",
      isLoading: isLoadingCotasFundos,
      hasWarning: avisosCotasFundos !== null,
      hasError: erroMensagemCotasFundos !== null,
      inputsStatuses: [
        {
          label: inputElementData.deparaCotasFundos.label,
          isOk: fileInputDeparaCotasFundos !== null,
        },
        {
          label: inputElementData.xmlsAnbima401.label,
          isOk: filesInputXmlsAnbima401 !== null,
        },
        {
          label: inputElementData.caracteristicasFundos.label,
          isOk: fileInputCaracteristicasFundos !== null,
        },
      ],
      exportCallback: async () => {
        getExportCallback({
          httpClient: httpClient,
          url: "v1/liberacao-cotas/precos/cotas-fundos",
          isExportLoading: isLoadingCotasFundos,
          setIsExportLoading: setIsLoadingCotasFundos,
          setAvisos: setAvisosCotasFundos,
          setErroMensagem: setErroMensagemCotasFundos,
          requestBodyFieldsInputs: [
            {
              field: CampoRequestLiberacaoCotas.Xlsx_Depara_Cotas_Fundos,
              fileList: fileInputDeparaCotasFundos,
            },
            {
              field: CampoRequestLiberacaoCotas.Zip_Arqs_Xml_Anbima_401,
              fileList: filesInputXmlsAnbima401,
            },
            {
              field: CampoRequestLiberacaoCotas.Xls_Caracteristicas_Fundos,
              fileList: fileInputCaracteristicasFundos,
            },
          ],
        });
      },
    },
  ];

  return (
    <TabPanelLayout
      topComponent={
        <>
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
        </>
      }
      leftComponent={
        <>
          <VStack>
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
                  stateValue={getFileName(fileInputCaracteristicasFundos)}
                  setState={setFileInputCaracteristicasFundos}
                />
                <InputElement
                  hint={inputElementData.deparaDerivativos.hint}
                  label={inputElementData.deparaDerivativos.label}
                  stateValue={getFileName(fileInputDeparaDerivativos)}
                  setState={setFileInputDeparaDerivativos}
                />
                <InputElement
                  hint={inputElementData.deparaBondsOffshore.hint}
                  label={inputElementData.deparaBondsOffshore.label}
                  stateValue={getFileName(fileInputDeparaBondsOffshore)}
                  setState={setFileInputDeparaBondsOffshore}
                />
                <InputElement
                  hint={inputElementData.deparaCreditoPrivado.hint}
                  label={inputElementData.deparaCreditoPrivado.label}
                  stateValue={getFileName(fileInputDeparaCreditoPrivado)}
                  setState={
                    setFileInputDeparaCreditoPrivadoNaoPrecificadoAnbima
                  }
                />
                <InputElement
                  hint={inputElementData.deparaAtivosMarcadosNaCurva.hint}
                  label={inputElementData.deparaAtivosMarcadosNaCurva.label}
                  stateValue={getFileName(fileInputDeparaAtivosMarcadosNaCurva)}
                  setState={setFileInputDeparaAtivosMarcadosNaCurva}
                />
                <InputElement
                  hint={inputElementData.deparaCotasFundos.hint}
                  label={inputElementData.deparaCotasFundos.label}
                  stateValue={getFileName(fileInputDeparaCotasFundos)}
                  setState={setFileInputDeparaCotasFundos}
                />
              </VStack>
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
              {cardsData.map((card, index) => {
                return (
                  <OutputCard
                    key={index}
                    width="400px"
                    cardTitle={card.cardTitle}
                    inputsStatuses={card.inputsStatuses}
                    isLoading={card.isLoading}
                    hasWarning={card.hasWarning}
                    hasError={card.hasError}
                    requestCallback={card.exportCallback}
                  />
                );
              })}
            </HStack>
            {(avisosBolsaBmf ||
              avisosBonds ||
              avisosRendaFixaNaoPrecificadoAnbima ||
              avisosCreditoPrivadoMarcacaoAMercado ||
              avisosCotasFundos) && (
              <VStack width="100%" gap="12px">
                {avisosBolsaBmf && (
                  <AvisoAccordion
                    titulo="Bolsa e BMF"
                    avisos={avisosBolsaBmf}
                  />
                )}
                {avisosBonds && (
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
                )}
              </VStack>
            )}
            {(erroMensagemBolsaBmf ||
              erroMensagemBonds ||
              erroMensagemRendaFixaNaoPrecificadoAnbima ||
              erroMensagemCreditoPrivadoMarcacaoAMercado ||
              erroMensagemCotasFundos) && (
              <VStack width="100%" gap="12px">
                {erroMensagemBolsaBmf && (
                  <ErroInfo
                    cardTitulo="Bolsa e BMF"
                    erroMensagem={erroMensagemBolsaBmf}
                  />
                )}
                {erroMensagemBonds && (
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
                )}
              </VStack>
            )}
          </VStack>
        </>
      }
    />
  );
}
