import {
  HStack,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  VStack,
} from "@chakra-ui/react";
import AbaVoices from "./voices/AbaVoices";
import AbaCorretoras from "./corretoras/AbaCorretoras";

export default function AbaDadosNegociacao() {
  return (
    <Tabs h="100%" size="sm" variant="soft-rounded" colorScheme="verde">
      <HStack h="100%" alignItems="stretch" p="8px" bgColor="cinza.main">
        <TabList minW="128px">
          <VStack w="100%" bgColor="white" alignItems="stretch" p="4px">
            <Tab>Voices [B]³</Tab>
            <Tab>Corretoras</Tab>
          </VStack>
        </TabList>
        <TabPanels flex={1} bgColor="white">
          <TabPanel w="100%" h="100%" p={0}>
            <AbaVoices />
          </TabPanel>
          <TabPanel w="100%" h="100%" p={0}>
            <AbaCorretoras />
          </TabPanel>
        </TabPanels>
      </HStack>
    </Tabs>
  );
}
