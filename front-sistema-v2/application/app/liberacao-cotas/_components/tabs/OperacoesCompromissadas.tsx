"use client";

import { useState } from "react";
import { Divider, Heading, HStack, VStack } from "@chakra-ui/react";

import { useHTTP } from "@/lib/hooks";
import { CampoRequestLiberacaoCotas } from "@/lib/types/api/iv/liberacao-cotas";
import AvisoAccordion from "../common/AvisoAccordion";
import ErroInfo from "../common/ErroInfo";
import getExportCallback from "../../_utils/getExportCallback";
import getFileName from "../../_utils/getFileName";
import getFilesInputDisplay from "../../_utils/getFilesInputDisplay";
import InputElement from "../common/InputElement";
import inputElementData from "../../_utils/inputElementData";
import OutputCard from "../common/OutputCard";
import TabPanelLayout from "../TabPanelLayout";

export function OperacoesCompromissadas() {
  const [filesInputXmlsAnbima401, setFilesInputXmlsAnbima401] =
    useState<FileList | null>(null);
  const [fileInputCaracteristicasFundos, setFileInputCaracteristicasFundos] =
    useState<FileList | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [avisos, setAvisos] = useState<any>(null);
  const [erroMensagem, setErroMensagem] = useState<string | null>(null);

  const httpClient = useHTTP({ withCredentials: true });
  const cardsData = [
    {
      cardTitle: "Operações Compromissadas (abert. incluso)",
      isLoading: isLoading,
      hasWarning: avisos !== null,
      hasError: erroMensagem !== null,
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
      exportCallback: async () => {
        getExportCallback({
          httpClient: httpClient,
          url: `v1/liberacao-cotas/compromissadas`,
          isExportLoading: isLoading,
          setIsExportLoading: setIsLoading,
          setAvisos: setAvisos,
          setErroMensagem: setErroMensagem,
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
        });
      },
    },
  ];

  return (
    <TabPanelLayout
      leftComponent={
        <>
          <VStack>
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
            {avisos && (
              <VStack width="100%" gap="12px">
                <AvisoAccordion
                  titulo="Operações Compromissadas"
                  avisos={avisos}
                />
              </VStack>
            )}
            {erroMensagem && (
              <VStack width="100%" gap="12px">
                <ErroInfo
                  cardTitulo="Operações Compromissadas"
                  erroMensagem={erroMensagem}
                />
              </VStack>
            )}
          </VStack>
        </>
      }
    />
  );
}
