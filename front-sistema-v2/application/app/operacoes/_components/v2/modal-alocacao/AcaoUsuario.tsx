import { Box, HStack, Icon, StackProps, Text, VStack } from "@chakra-ui/react";
import { IoPersonCircleOutline } from "react-icons/io5";
import Usuario from "./Usuario";
import Horario from "./Horario";

interface InfosUsuario {
  nome: string;
  email: string;
}

export type AcaoUsuarioProps = {
  usuario: InfosUsuario;
  horario: string;
} & StackProps;

export default function AcaoUsuario({
  usuario,
  horario,
  ...props
}: AcaoUsuarioProps) {
  return (
    <VStack alignItems="stretch" gap="4px" {...props}>
      <Usuario usuario={usuario} />
      <Box ml="32px">
        <Horario horario={horario} />
      </Box>
    </VStack>
  );
}
