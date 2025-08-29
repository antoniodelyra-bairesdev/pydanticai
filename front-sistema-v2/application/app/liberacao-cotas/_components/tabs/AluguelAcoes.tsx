"use client";

import { useState } from "react";

import { getDataFormatadaFromDate } from "@/lib/util/dates";
import { Divider, Heading, HStack, VStack } from "@chakra-ui/react";
import InputElement from "../common/InputElement";
import OutputCard from "../common/OutputCard";
import DataReferente from "../common/DataReferente";
import inputElementData from "../../_utils/inputElementData";
import getFileName from "../../_utils/getFileName";
import { useHTTP } from "@/lib/hooks";
import { CampoRequestLiberacaoCotas } from "@/lib/types/api/iv/liberacao-cotas";
import getExportCallback from "../../_utils/getExportCallback";
import TabPanelLayout from "../TabPanelLayout";
import AvisoAccordion from "../common/AvisoAccordion";
import ErroInfo from "../common/ErroInfo";

export function AluguelAcoes() {
  const [dataReferente, setDataReferente] = useState<string>(
    getDataFormatadaFromDate(new Date()),
  );

  const [fileInputCaracteristicasFundos, setFileInputCaracteristicasFundos] =
    useState<FileList | null>(null);
  const [fileInputRelatorioBip, setFileInputRelatorioBip] =
    useState<FileList | null>(null);
  const [fileInputRelatorioAntecipacoes, setFileInputRelatorioAntecipacoes] =
    useState<FileList | null>(null);

  const [isLoadingRenovacoes, setIsLoadingRenovacoes] =
    useState<boolean>(false);
  const [avisosRenovacoes, setAvisosRenovacoes] = useState<any>(null);
  const [erroMensagemRenovacoes, setErroMensagemRenovacoes] = useState<
    string | null
  >(null);

  const [isLoadingNovosContratos, setIsLoadingNovosContratos] =
    useState<boolean>(false);
  const [avisosNovosContratos, setAvisosNovosContratos] = useState<any>(null);
  const [erroMensagemNovosContratos, setErroMensagemNovosContratos] = useState<
    string | null
  >(null);

  const [isLoadingAntecipacoes, setIsLoadingAntecipacoes] =
    useState<boolean>(false);
  const [avisosAntecipacoes, setAvisosAntecipacoes] = useState<any>(null);
  const [erroMensagemAntecipacoes, setErroMensagemAntecipacoes] = useState<
    string | null
  >(null);

  const httpClient = useHTTP({ withCredentials: true });
  const cardsData = [
    {
      cardTitle: "Renovações",
      isLoading: isLoadingRenovacoes,
      hasWarning: avisosRenovacoes !== null,
      hasError: erroMensagemRenovacoes !== null,
      inputsStatuses: [
        {
          label: inputElementData.relatorioBip.label,
          isOk: fileInputRelatorioBip !== null,
        },
        {
          label: inputElementData.caracteristicasFundos.label,
          isOk: fileInputCaracteristicasFundos !== null,
        },
      ],
      exportCallback: async () => {
        getExportCallback({
          httpClient: httpClient,
          url: `v1/liberacao-cotas/aluguel-acoes/renovacoes?data_referente=${dataReferente}`,
          isExportLoading: isLoadingRenovacoes,
          setIsExportLoading: setIsLoadingRenovacoes,
          setAvisos: setAvisosRenovacoes,
          setErroMensagem: setErroMensagemRenovacoes,
          requestBodyFieldsInputs: [
            {
              field: CampoRequestLiberacaoCotas.Xls_Caracteristicas_Fundos,
              fileList: fileInputCaracteristicasFundos,
            },
            {
              field: CampoRequestLiberacaoCotas.Csv_Relatorio_Bip,
              fileList: fileInputRelatorioBip,
            },
          ],
        });
      },
    },
    {
      cardTitle: "Novos Contratos",
      isLoading: isLoadingNovosContratos,
      hasWarning: avisosNovosContratos !== null,
      hasError: erroMensagemNovosContratos !== null,
      inputsStatuses: [
        {
          label: inputElementData.relatorioBip.label,
          isOk: fileInputRelatorioBip !== null,
        },
        {
          label: inputElementData.caracteristicasFundos.label,
          isOk: fileInputCaracteristicasFundos !== null,
        },
      ],
      exportCallback: async () => {
        getExportCallback({
          httpClient: httpClient,
          url: `v1/liberacao-cotas/aluguel-acoes/novos_contratos?data_referente=${dataReferente}`,
          isExportLoading: isLoadingNovosContratos,
          setIsExportLoading: setIsLoadingNovosContratos,
          setAvisos: setAvisosNovosContratos,
          setErroMensagem: setErroMensagemNovosContratos,
          requestBodyFieldsInputs: [
            {
              field: CampoRequestLiberacaoCotas.Xls_Caracteristicas_Fundos,
              fileList: fileInputCaracteristicasFundos,
            },
            {
              field: CampoRequestLiberacaoCotas.Csv_Relatorio_Bip,
              fileList: fileInputRelatorioBip,
            },
          ],
        });
      },
    },
    {
      cardTitle: "Antecipações",
      isLoading: isLoadingAntecipacoes,
      hasWarning: avisosAntecipacoes !== null,
      hasError: erroMensagemAntecipacoes !== null,
      inputsStatuses: [
        {
          label: inputElementData.relatorioAntecipacoes.label,
          isOk: fileInputRelatorioAntecipacoes !== null,
        },
        {
          label: inputElementData.caracteristicasFundos.label,
          isOk: fileInputCaracteristicasFundos !== null,
        },
      ],
      exportCallback: async () => {
        getExportCallback({
          httpClient: httpClient,
          url: `v1/liberacao-cotas/aluguel-acoes/antecipacoes?data_referente=${dataReferente}`,
          isExportLoading: isLoadingAntecipacoes,
          setIsExportLoading: setIsLoadingAntecipacoes,
          setAvisos: setAvisosAntecipacoes,
          setErroMensagem: setErroMensagemAntecipacoes,
          requestBodyFieldsInputs: [
            {
              field: CampoRequestLiberacaoCotas.Xls_Caracteristicas_Fundos,
              fileList: fileInputCaracteristicasFundos,
            },
            {
              field: CampoRequestLiberacaoCotas.Xlsx_Relatorio_Antecipacao,
              fileList: fileInputRelatorioAntecipacoes,
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
          <DataReferente value={dataReferente} setValue={setDataReferente} />
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
              <InputElement
                hint={inputElementData.relatorioBip.hint}
                label={inputElementData.relatorioBip.label}
                stateValue={getFileName(fileInputRelatorioBip)}
                setState={setFileInputRelatorioBip}
              />
              <InputElement
                hint={inputElementData.caracteristicasFundos.hint}
                label={inputElementData.caracteristicasFundos.label}
                stateValue={getFileName(fileInputCaracteristicasFundos)}
                setState={setFileInputCaracteristicasFundos}
              />
              <InputElement
                hint={inputElementData.relatorioAntecipacoes.hint}
                label={inputElementData.relatorioAntecipacoes.label}
                stateValue={getFileName(fileInputRelatorioAntecipacoes)}
                setState={setFileInputRelatorioAntecipacoes}
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
            {(avisosRenovacoes ||
              avisosNovosContratos ||
              avisosAntecipacoes) && (
              <VStack width="100%" gap="12px">
                {avisosRenovacoes && (
                  <AvisoAccordion
                    titulo="Renovações"
                    avisos={avisosRenovacoes}
                  />
                )}
                {avisosNovosContratos && (
                  <AvisoAccordion
                    titulo="Novos Contratos"
                    avisos={avisosNovosContratos}
                  />
                )}
                {avisosAntecipacoes && (
                  <AvisoAccordion
                    titulo="Antecipações"
                    avisos={avisosAntecipacoes}
                  />
                )}
              </VStack>
            )}
            {(erroMensagemRenovacoes ||
              erroMensagemNovosContratos ||
              erroMensagemAntecipacoes) && (
              <VStack width="100%" gap="12px">
                {erroMensagemRenovacoes && (
                  <ErroInfo
                    cardTitulo="Renovações"
                    erroMensagem={erroMensagemRenovacoes}
                  />
                )}
                {erroMensagemNovosContratos && (
                  <ErroInfo
                    cardTitulo="Novos Contratos"
                    erroMensagem={erroMensagemNovosContratos}
                  />
                )}
                {erroMensagemAntecipacoes && (
                  <ErroInfo
                    cardTitulo="Antecipações"
                    erroMensagem={erroMensagemAntecipacoes}
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
