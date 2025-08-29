import Hint from "@/app/_components/texto/Hint";
import {
  Checkbox,
  Divider,
  HStack,
  Radio,
  RadioGroup,
  StackProps,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Text,
  VStack,
} from "@chakra-ui/react";

export type ControlesCarteirasProps = {} & StackProps;

export default function ControlesCarteiras({
  ...stackProps
}: ControlesCarteirasProps) {
  return (
    <VStack alignItems="stretch" {...stackProps}>
      <Tabs flex={1} size="sm">
        <TabList w="100%">
          <HStack w="100%" gap={0}>
            <Tab flex={1}>
              <Text>Filtros</Text>
            </Tab>
            <Tab flex={1}>
              <Text>Visualização</Text>
            </Tab>
            <Tab flex={1}>
              <Text>Validações</Text>
            </Tab>
          </HStack>
        </TabList>
        <TabPanels>
          <TabPanel>
            <Text>Controle 1A</Text>
            <Text>Controle 1B</Text>
          </TabPanel>
          <TabPanel>
            <VStack w="100%" alignItems="stretch">
              <VStack alignItems="stretch">
                <Hint>Comparação por colunas</Hint>
                <RadioGroup size="sm" defaultValue="DIFERENCA">
                  <VStack gap={0} alignItems="stretch">
                    <Radio value="DIFERENCA">
                      <Text fontSize="xs">Mostrar diferença</Text>
                    </Radio>
                    <Radio value="TOTAL">
                      <Text fontSize="xs">Mostrar valor total</Text>
                    </Radio>
                  </VStack>
                </RadioGroup>
                <Divider />
              </VStack>
              <VStack w="100%" alignItems="stretch">
                <Checkbox size="sm">
                  <Text fontSize="xs">Mostrar valor base de comparação</Text>
                </Checkbox>
                <Divider />
              </VStack>
            </VStack>
          </TabPanel>
          <TabPanel>
            <Text>Controle 3A</Text>
            <Text>Controle 3B</Text>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </VStack>
  );
}
