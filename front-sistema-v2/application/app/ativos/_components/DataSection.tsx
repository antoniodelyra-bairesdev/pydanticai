import { useColors } from "@/lib/hooks";
import { AssetPageContext, DataFlow } from "@/lib/providers/AssetPageProvider";
import { ArrowForwardIcon, LockIcon } from "@chakra-ui/icons";
import { Button, HStack, Icon, Text, Tooltip, VStack } from "@chakra-ui/react";
import { useContext, useEffect, useRef } from "react";
import { IoDesktop, IoServer } from "react-icons/io5";
import TopBarSection from "./TopBarSection";

export type FilterSectionProps = {
  editing: boolean;
};

export default function DataSection({ editing }: FilterSectionProps) {
  const { text } = useColors();

  const arrowRef = useRef<SVGSVGElement>(null);

  const { dataFlow, setDataFlow } = useContext(AssetPageContext);
  const changeFlow = () => {
    if (dataFlow === DataFlow.ASSETS_DEFINE_EVENTS) {
      setDataFlow(DataFlow.EVENTS_DEFINE_ASSETS);
    } else if (dataFlow === DataFlow.EVENTS_DEFINE_ASSETS) {
      setDataFlow(DataFlow.ASSETS_DEFINE_EVENTS);
    }
  };
  useEffect(() => {
    if (!arrowRef.current) return;
    arrowRef.current.style.transform = `rotate(${dataFlow === DataFlow.ASSETS_DEFINE_EVENTS ? 0 : 180}deg)`;
  }, [dataFlow]);

  useEffect(() => {
    if (editing) {
      setDataFlow(DataFlow.ASSETS_DEFINE_EVENTS);
    }
  }, [editing]);

  return (
    <TopBarSection
      title="Fluxo de dados"
      flexGrow={2}
      minW="240px"
      maxW="240px"
    >
      <VStack h="100%" justifyContent="space-between" alignItems="stretch">
        <HStack h="100%" alignItems="center" justifyContent="center">
          <Text fontSize="md">
            <Icon
              as={
                editing || dataFlow === DataFlow.ASSETS_DEFINE_EVENTS
                  ? IoServer
                  : IoDesktop
              }
              fontSize="lg"
            />{" "}
            Ativos
          </Text>
          <VStack>
            <Tooltip
              isDisabled={!editing}
              hasArrow
              color="white"
              p="8px"
              borderRadius="8px"
              bgColor="azul_1.700"
              fontSize="xs"
              label="No modo de edição os fluxos sempre serão dependentes da tabela de ativos."
            >
              <Button
                isDisabled={editing}
                onClick={changeFlow}
                w="32px"
                h="32px"
                colorScheme="azul_1"
                borderRadius="full"
                position="relative"
              >
                <ArrowForwardIcon
                  fontSize="md"
                  ref={arrowRef}
                  transition="0.25s all"
                />
                <LockIcon
                  position="absolute"
                  right={0}
                  bottom={0}
                  color={text}
                  display={editing ? "block" : "none"}
                />
              </Button>
            </Tooltip>
          </VStack>
          <Text fontSize="md">
            <Icon
              as={
                editing || dataFlow === DataFlow.ASSETS_DEFINE_EVENTS
                  ? IoDesktop
                  : IoServer
              }
              mr="4px"
              fontSize="lg"
            />
            Eventos
          </Text>
        </HStack>
        {/* <HStack>
                <Button size='xs' w='calc(50% - 12px)'>Limpar filtros</Button>
                <Box w='64px' />
                <Button isDisabled={editing} size='xs' ml='6px' mr='6px' w='calc(50% - 12px)'>Limpar filtros</Button>
            </HStack> */}
      </VStack>
    </TopBarSection>
  );
}
