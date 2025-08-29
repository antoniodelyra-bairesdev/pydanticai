import { HStack, Icon, Text, VStack } from "@chakra-ui/react";
import { IoPersonCircleOutline } from "react-icons/io5";

interface InfosUsuario {
  nome: string;
  email: string;
}

export type UsuarioProps = {
  usuario: InfosUsuario;
};

export default function Usuario({ usuario }: UsuarioProps) {
  return (
    <HStack alignItems="center">
      <Icon w="24px" h="24px" color="azul_2.main" as={IoPersonCircleOutline} />
      <VStack alignItems="stretch" gap={0}>
        <Text fontSize="xs">{usuario.nome}</Text>
        <Text fontSize="11px" color="cinza.500">
          {usuario.email}
        </Text>
      </VStack>
    </HStack>
  );
}
