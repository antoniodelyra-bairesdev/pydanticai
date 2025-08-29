import ValidationGrid, {
  ValidationGridMethods,
} from "@/app/_components/grid/ValidationGrid";
import { dateColDef, percentageColDef } from "@/app/_components/grid/colDefs";
import { getColorHex } from "@/app/theme";
import { useAsync, useColors, useHTTP } from "@/lib/hooks";
import { Ativo, Evento } from "@/lib/types/api/iv/v1";
import { wait } from "@/lib/util/misc";
import { SingularPluralMapping, pluralOrSingular } from "@/lib/util/string";
import {
  Box,
  Card,
  CardBody,
  HStack,
  Icon,
  Progress,
  Stat,
  StatHelpText,
  StatNumber,
  Tag,
  Text,
  VStack,
} from "@chakra-ui/react";
import { ICellRendererParams } from "ag-grid-community";
import { useEffect, useRef, useState } from "react";
import { IoBarChart, IoCalendar } from "react-icons/io5";
import { StagedEvent } from "./GenerateEventsGrid";

export type GenerateEventsModalConfirmContentsProps = {
  ativo: Ativo;
  tipoPorcentagem: "Base100" | "RelativoVNA";
  fluxos: (Partial<Evento> & { uuid: number })[];
  onRelativesReady: (
    relatives: (StagedEvent & { percentual_relativoVNA: number })[],
  ) => void;
};

const s: SingularPluralMapping = {
  $: { plural: "s", singular: "" },
  "@": { plural: "ão", singular: "á" },
};

const getCellRenderer =
  (colored: boolean) =>
  ({ value }: ICellRendererParams) => {
    const { hover, text } = useColors();
    const num = value;
    return (
      <HStack
        borderRadius="4px"
        justifyContent="center"
        w="100%"
        h="100%"
        bgColor={
          colored
            ? num !== ""
              ? getColorHex("verde.main") + "2f"
              : getColorHex("cinza.main")
            : "none"
        }
      >
        <Text color={num || num === 0 ? text : "blackAlpha.500"}>
          {typeof num === "number" ? num : num || "Calculando..."}
        </Text>
        {num !== "" && (
          <Tag opacity={0.5} bgColor={hover} borderRadius="full" fontSize="xs">
            %
          </Tag>
        )}
      </HStack>
    );
  };

export default function GenerateEventsModalConfirmContents({
  ativo,
  tipoPorcentagem,
  fluxos,
  onRelativesReady,
}: GenerateEventsModalConfirmContentsProps) {
  const httpClient = useHTTP({ withCredentials: true });

  const [fluxosAlterados, setFluxosAlterados] = useState(
    fluxos
      .map((f) => ({
        ...f,
        percentual_base100: tipoPorcentagem === "Base100" ? f.percentual : null,
        percentual_relativoVNA:
          tipoPorcentagem === "RelativoVNA" ? f.percentual : null,
      }))
      .sort((f1: any, f2: any) => f1.data?.localeCompare(f2.data)),
  );
  const [loading, load] = useAsync();

  const [hasChangedDates, setHasChangedDates] = useState(false);

  const methodsRef = useRef<ValidationGridMethods<any>>();

  const gerarProporcional = (fs: typeof fluxos) =>
    load(async () => {
      const q = new URLSearchParams("");
      fs.forEach((f) =>
        q.append(
          tipoPorcentagem === "Base100" ? "absolutas" : "relativas",
          String(f.percentual || 0),
        ),
      );
      await wait(500);
      const response = await httpClient.fetch(
        `v1/calculos/porcentagem/${
          tipoPorcentagem === "Base100"
            ? "absoluta-para-relativa"
            : "relativa-para-absoluta"
        }?${q.toString()}`,
        { hideToast: { success: true } },
      );
      if (!response.ok) return onRelativesReady([]);
      const proporcionais = (await response.json()) as number[];
      const fluxosCompletos = [] as any[];
      for (let i = 0; i < proporcionais.length; i++) {
        fluxosCompletos.push({
          ...fs[i],
          [tipoPorcentagem === "Base100"
            ? "percentual_relativoVNA"
            : "percentual_base100"]:
            (fs[i] as any).tipo_evento === "Vencimento" &&
            tipoPorcentagem === "Base100"
              ? 1
              : proporcionais[i],
        });
      }
      setFluxosAlterados(fluxosCompletos);

      const dq = new URLSearchParams("");
      fs.forEach((f) => dq.append("dias", (f as any).data));

      const datesResponse = await httpClient.fetch(
        `v1/calculos/data/proximos-dias-uteis?${dq.toString()}`,
        { hideToast: { success: true } },
      );
      if (!datesResponse.ok) return onRelativesReady([]);
      const dates = (await datesResponse.json()) as string[];

      const updated = fluxosCompletos.map((f, i) => ({ ...f, data: dates[i] }));
      methodsRef.current?.updateRows(updated);

      setHasChangedDates(
        fluxosCompletos.map((f) => f.data).join(",") !==
          updated.map((f) => f.data).join(","),
      );
      onRelativesReady(updated);
    });

  useEffect(() => {
    gerarProporcional(fluxosAlterados);
  }, []);

  return (
    <VStack alignItems="stretch">
      <HStack justify="space-around" pt="18px">
        <Card variant="outline">
          <CardBody p="12px">
            <Stat>
              <StatNumber
                color="verde.main"
                display="flex"
                flexDirection="row"
                gap="2px"
              >
                {fluxos.length
                  .toString()
                  .padStart(4, "0")
                  .split("")
                  .map((l, i, word) => (
                    <Text
                      color={
                        Number(word.join("").substring(i + 1)) === fluxos.length
                          ? "cinza.main"
                          : "verde.main"
                      }
                      as="span"
                      border="1px solid lightgray"
                      borderRadius="4px"
                      pl="4px"
                      pr="4px"
                    >
                      {l}
                    </Text>
                  ))}
              </StatNumber>
              <StatHelpText>
                {pluralOrSingular(`Evento$ ser@ gerado$`, s, fluxos.length)}
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        <Card variant="outline">
          <CardBody p="12px">
            <Stat>
              <StatNumber display="flex" flexDirection="row" gap="2px">
                {ativo.fluxos.length
                  .toString()
                  .padStart(4, "0")
                  .split("")
                  .map((l, i, word) => (
                    <Text
                      color={
                        Number(word.join("").substring(i + 1)) ===
                        ativo.fluxos.length
                          ? "cinza.main"
                          : "rosa.main"
                      }
                      as="span"
                      border="1px solid lightgray"
                      borderRadius="4px"
                      pl="4px"
                      pr="4px"
                    >
                      {l}
                    </Text>
                  ))}
              </StatNumber>
              <StatHelpText>
                {pluralOrSingular(`Evento$ ser@ apagado$`, s, fluxos.length)}
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
      </HStack>
      <Progress
        borderRadius="full"
        size="sm"
        visibility={loading ? "visible" : "hidden"}
        colorScheme="verde"
        isIndeterminate={true}
      />
      <Box borderRadius="4px" overflow="hidden">
        <Text
          borderLeft={"4px solid " + getColorHex("verde.main")}
          bgColor={getColorHex("verde.main") + "2f"}
          fontSize="sm"
          p="4px"
        >
          <Icon
            as={IoBarChart}
            m="4px"
            mr="8px"
            color="verde.main"
            verticalAlign="bottom"
          />
          Os eventos abaixo serão armazenados com as porcentagens{" "}
          <strong>relativas ao saldo devedor</strong>!
        </Text>
      </Box>
      {hasChangedDates && (
        <Box key="hasChangedDates" borderRadius="4px" overflow="hidden">
          <Text
            borderLeft={"4px solid " + getColorHex("amarelo.main")}
            bgColor={getColorHex("amarelo.main") + "2f"}
            fontSize="sm"
            p="4px"
          >
            <Icon
              as={IoCalendar}
              m="4px"
              mr="8px"
              color="amarelo.main"
              verticalAlign="bottom"
            />
            Algumas datas foram alteradas para{" "}
            <strong>o próximo dia útil</strong>.
          </Text>
        </Box>
      )}
      <Box h="480px" w="100%">
        <ValidationGrid
          editable={false}
          data={fluxosAlterados}
          identifier="uuid"
          colDefs={[
            { field: "data", ...dateColDef, sortable: false },
            {
              field: "tipo_evento",
              headerName: "Tipo Evento",
              sortable: false,
            },
            {
              field: "percentual_base100",
              headerName: "(%) Base 100",
              ...percentageColDef,
              sortable: false,
              cellRenderer: getCellRenderer(false),
            },
            {
              field: "percentual_relativoVNA",
              headerName: "(%) Saldo devedor",
              ...percentageColDef,
              sortable: false,
              cellRenderer: getCellRenderer(true),
            },
          ]}
          onReady={(ev) => {
            ev.api.sizeColumnsToFit();
          }}
          methodsRef={methodsRef}
        />
      </Box>
    </VStack>
  );
}
