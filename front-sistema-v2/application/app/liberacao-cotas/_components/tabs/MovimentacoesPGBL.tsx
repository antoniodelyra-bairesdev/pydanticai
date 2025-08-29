import { useState } from "react";

import { getDataFormatadaFromDate } from "@/lib/util/dates";
import { Divider, Heading, HStack, VStack } from "@chakra-ui/react";
import DataReferente from "../common/DataReferente";
import InputElement from "../common/InputElement";
import inputElementData from "../../_utils/inputElementData";
import getFileName from "../../_utils/getFileName";
import OutputCard from "../common/OutputCard";
import { CampoRequestLiberacaoCotas } from "@/lib/types/api/iv/liberacao-cotas";
import { useHTTP } from "@/lib/hooks";
import TabPanelLayout from "../TabPanelLayout";
import AvisoAccordion from "../common/AvisoAccordion";
import ErroInfo from "../common/ErroInfo";
import getFilesInputDisplay from "../../_utils/getFilesInputDisplay";
import getExportCallback from "../../_utils/getExportCallback";

export function MovimentacoesPGBL() {
  const [dataReferente, setDataReferente] = useState<string>(
    getDataFormatadaFromDate(new Date()),
  );

  const [fileInputCaracteristicasFundos, setFileInputCaracteristicasFundos] =
    useState<FileList | null>(null);
  const [filesInputXmlsAnbima401, setFilesInputXmlsAnbima401] =
    useState<FileList | null>(null);
  const [filesInputMovimentacoesPGBL, setFilesInputMovimentacoesPGBL] =
    useState<FileList | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(false);

  const [avisos, setAvisos] = useState<any>(null);
  const [erroMensagem, setErroMensagem] = useState<string | null>(null);

  const httpClient = useHTTP({ withCredentials: true });
  const cardsData = [
    {
      cardTitle: "Movimentações PGBL",
      isLoading: isLoading,
      hasWarning: avisos !== null,
      hasError: erroMensagem !== null,
      inputsStatuses: [
        {
          label: inputElementData.relatorioMovimentacoesPgbl.label,
          isOk: filesInputMovimentacoesPGBL !== null,
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
          url: `v1/liberacao-cotas/movimentacoes-pgbl?data_referente=${dataReferente}`,
          isExportLoading: isLoading,
          setIsExportLoading: setIsLoading,
          setAvisos: setAvisos,
          setErroMensagem: setErroMensagem,
          requestBodyFieldsInputs: [
            {
              field:
                CampoRequestLiberacaoCotas.Xlsxs_Relatorios_Movimentacoes_Pgbl,
              fileList: filesInputMovimentacoesPGBL,
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
                hint={inputElementData.relatorioMovimentacoesPgbl.hint}
                label={inputElementData.relatorioMovimentacoesPgbl.label}
                isMultiFile={true}
                stateValue={getFilesInputDisplay(filesInputMovimentacoesPGBL)}
                setState={setFilesInputMovimentacoesPGBL}
              />
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
                <AvisoAccordion titulo="Movimentações PGBL" avisos={avisos} />
              </VStack>
            )}
            {erroMensagem && (
              <VStack width="100%" gap="12px">
                <ErroInfo
                  cardTitulo="Movimentações PGBL"
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
