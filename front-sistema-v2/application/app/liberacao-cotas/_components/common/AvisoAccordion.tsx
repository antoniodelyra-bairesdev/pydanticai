import { APIWarning } from "@/lib/types/api/iv/v1";
import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box,
  Heading,
  HStack,
  Icon,
  Text,
  VStack,
} from "@chakra-ui/react";
import { IoWarning } from "react-icons/io5";

type AvisoAccordionProps = {
  titulo: string;
  avisos: APIWarning[];
};

export default function AvisoAccordion({
  titulo,
  avisos,
}: AvisoAccordionProps) {
  return (
    <Box width="100%">
      <HStack alignItems="center">
        <Heading size="md">{titulo}</Heading>
        <Text>{<Icon color="amarelo.main" as={IoWarning} boxSize={6} />}</Text>
      </HStack>
      <Accordion
        allowMultiple
        width="100%"
        maxHeight="450px"
        overflowY="scroll"
      >
        {avisos.map((aviso, index) => {
          return (
            <AccordionItem key={index}>
              <h2>
                <AccordionButton>
                  <HStack
                    flex="1"
                    textAlign="left"
                    justifyContent="space-between"
                  >
                    <Text as="span">{aviso.id}</Text>
                    <AccordionIcon />
                  </HStack>
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4}>
                <VStack alignItems="flex-start">
                  {aviso.mensagens.map((mensagem, index) => {
                    return (
                      <Box key={index}>
                        <Text as="span">{mensagem}</Text>
                      </Box>
                    );
                  })}
                </VStack>
              </AccordionPanel>
            </AccordionItem>
          );
        })}
      </Accordion>
    </Box>
  );
}
