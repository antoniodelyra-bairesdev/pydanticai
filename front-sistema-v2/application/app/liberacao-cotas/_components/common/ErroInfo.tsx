import { Box, Divider, Heading, HStack, Icon, Text } from "@chakra-ui/react";
import { IoWarning } from "react-icons/io5";

type ErroInfoProps = {
  cardTitulo: string;
  erroMensagem: string;
};

export default function ErroInfo({ cardTitulo, erroMensagem }: ErroInfoProps) {
  return (
    <Box width="100%">
      <HStack alignItems="center">
        <Heading size="md">{cardTitulo}</Heading>
        <Text>{<Icon color="rosa.main" as={IoWarning} boxSize={6} />}</Text>
      </HStack>
      <Box>
        <Divider />
        <Text marginX="16px" marginY="8px">
          {erroMensagem}
        </Text>
        <Divider />
      </Box>
    </Box>
  );
}
