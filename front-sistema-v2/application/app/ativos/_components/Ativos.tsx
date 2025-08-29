"use client";

import HResize from "@/app/_components/misc/HResize";
import { useColors } from "@/lib/hooks";
import {
  Emissor,
  Evento,
  IndicePapel,
  TipoEvento,
  TipoPapel,
} from "@/lib/types/api/iv/v1";
import { ArrowForwardIcon } from "@chakra-ui/icons";
import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box,
  HStack,
  Stat,
  StatHelpText,
  StatNumber,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useContext, useEffect, useMemo, useRef, useState } from "react";
import ActionsSection from "./ActionsSection";
import AssetsGrid, { AssetGridMethods } from "./AssetsGrid";
import DataSection from "./DataSection";
import ErrorSection from "./ErrorSection";
import EventsGrid from "./EventsGrid";
import InsertSection from "./InsertSection";
import SummarySection from "./SummarySection";
import TopBarItem from "./TopBarItem";
import TopBarSection from "./TopBarSection";

import {
  ValidationGridColDef,
  ValidationGridMethods,
} from "@/app/_components/grid/ValidationGrid";
import { AssetPageContext, DataFlow } from "@/lib/providers/AssetPageProvider";
import "./DataFlow.css";
import { fmtNumber } from "@/lib/util/string";

export type AtivosProps = {
  codigos: string[];
  emissores: Emissor[];
  indices: IndicePapel[];
  tipos_ativos: TipoPapel[];
  tipos_fluxos: TipoEvento[];
  tipos_fluxos_suportados: TipoEvento[];
  total_assets: number | null;
  total_events: number | null;
};

export default function Ativos({
  codigos,
  emissores,
  indices,
  tipos_ativos,
  tipos_fluxos,
  tipos_fluxos_suportados,
  total_assets,
  total_events,
}: AtivosProps) {
  const [editing, setEditing] = useState(false);
  const [totalAssets, setTotalAssets] = useState<number | null>(total_assets);
  const [totalEvents, setTotalEvents] = useState<number | null>(total_events);
  const assetsGridMethods = useRef<AssetGridMethods>();
  const insertEventsModal = useRef<(() => void) | null>(null);
  const eventsGridMethods = useRef<ValidationGridMethods<Evento>>();

  const { bgText, hover } = useColors();

  const { dataFlow } = useContext(AssetPageContext);
  const dataFlowRef = useRef(dataFlow);
  useEffect(() => {
    dataFlowRef.current = dataFlow;
  }, [dataFlow]);

  const dataFlowArrow = useRef<HTMLDivElement>(null);

  const triggerArrow = (_: unknown, total: number) => {
    if (dataFlowRef.current === DataFlow.ASSETS_DEFINE_EVENTS) {
      dataFlowArrow.current?.classList.add("ltr");
      setTotalAssets(total);
    } else if (dataFlowRef.current === DataFlow.EVENTS_DEFINE_ASSETS) {
      dataFlowArrow.current?.classList.add("rtl");
      setTotalEvents(total);
    }
  };

  const assetColDefRef = useRef<ValidationGridColDef[]>([]);
  const eventColDefRef = useRef<ValidationGridColDef[]>([]);

  const indicesStr = indices.map((i) => i.nome);
  const tiposAtivosStr = tipos_ativos.map((t) => t.nome);
  const tiposEventosStr = tipos_fluxos.map((t) => t.nome);
  const tiposEventosSuportadosStr = tipos_fluxos_suportados.map((t) => t.nome);

  const assetsGrid = useMemo(() => {
    return (
      <AssetsGrid
        editable={editing}
        methodsRef={assetsGridMethods}
        codigos={codigos}
        emissores={emissores}
        indices={indicesStr}
        tipos={tiposAtivosStr}
        tiposEventosSuportados={tiposEventosSuportadosStr}
        onNewAssetsFetched={triggerArrow}
        eventsGridMethodsRef={eventsGridMethods}
        colDefRef={assetColDefRef}
      />
    );
  }, [editing]);

  const eventsGrid = useMemo(() => {
    return (
      <EventsGrid
        codigos={codigos}
        editable={editing}
        tipos={tiposEventosStr}
        tiposSuportados={tiposEventosSuportadosStr}
        onNewEventsFetched={triggerArrow}
        methodsRef={eventsGridMethods}
        modalOpenRef={insertEventsModal}
        colDefRef={eventColDefRef}
      />
    );
  }, [editing]);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        alignSelf: "stretch",
      }}
    >
      <Accordion allowToggle defaultIndex={[0]}>
        <AccordionItem border="none">
          <AccordionButton>
            <AccordionIcon mr="4px" boxSize="16px" />
            <Text fontSize="xs">Detalhes e ações</Text>
          </AccordionButton>
          <AccordionPanel p={0}>
            <HStack alignItems="stretch" overflow="auto" mt="4px" pb="2px">
              <ActionsSection
                editing={editing}
                onEditToggle={(newEditing) => setEditing(newEditing)}
                assetColDefs={assetColDefRef.current}
                eventColDefs={eventColDefRef.current}
                emissores={emissores}
                indices={indices}
                tipos_ativos={tipos_ativos}
                tipos_fluxos={tipos_fluxos}
              />
              <DataSection editing={editing} />
              {editing ? (
                <>
                  <ErrorSection />
                  <InsertSection
                    onAddAtivosClicked={() =>
                      assetsGridMethods.current?.openInsertModal()
                    }
                    onAddFluxosClicked={() => insertEventsModal.current?.()}
                  />
                  <SummarySection />
                </>
              ) : (
                <TopBarSection title="" flexGrow={1}>
                  {/* <VStack h='100%' justify='center'>
                                    <TopBarItem txt='Clique em "Habilitar modo de edição" para mais opções' alignSelf="center" color={bgText} />
                                </VStack> */}
                  <HStack ml="12px">
                    <Stat maxW="144px">
                      <StatNumber>
                        {totalAssets === null
                          ? "---"
                          : fmtNumber(totalAssets, 0)}
                      </StatNumber>
                      <StatHelpText>Ativos cadastrados</StatHelpText>
                    </Stat>
                    <Stat maxW="144px">
                      <StatNumber>
                        {totalEvents === null
                          ? "---"
                          : fmtNumber(totalEvents, 0)}
                      </StatNumber>
                      <StatHelpText>Eventos mapeados</StatHelpText>
                    </Stat>
                  </HStack>
                </TopBarSection>
              )}
            </HStack>
          </AccordionPanel>
        </AccordionItem>
      </Accordion>
      <HResize
        mt="2px"
        flexGrow={1}
        leftElement={
          <Box w="100%" h="100%" position="relative">
            {assetsGrid}
            <Box
              ref={dataFlowArrow}
              pointerEvents="none"
              opacity="0%"
              right={0}
              onAnimationIteration={(ev) =>
                ev.currentTarget.classList.remove("ltr", "rtl")
              }
              bgColor={hover}
              borderRadius="full"
              w="64px"
              h="64px"
              position="absolute"
              top="calc(50% - 32px)"
              zIndex={90}
            >
              <ArrowForwardIcon
                borderRadius="full"
                bgColor={hover}
                w="100%"
                h="100%"
                color="verde.main"
              />
            </Box>
          </Box>
        }
        rightElement={eventsGrid}
      />
    </div>
  );
}
