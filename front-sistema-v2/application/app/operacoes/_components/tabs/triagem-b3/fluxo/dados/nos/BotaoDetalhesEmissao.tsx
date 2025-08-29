import { RegistroNoMe } from "@/lib/types/api/iv/v1";
import { Button, HStack, Icon, useDisclosure } from "@chakra-ui/react";
import { IoSearchOutline } from "react-icons/io5";
import ModalInteracaoEmissoes from "./ModalInteracaoEmissoes";

export type BotaoDetalhesEmissaoProps = {
  preco_unitario: number;
  registros: RegistroNoMe[];
};

export function BotaoDetalhesEmissao({
  preco_unitario,
  registros,
}: BotaoDetalhesEmissaoProps) {
  const { isOpen, onOpen, onClose } = useDisclosure();

  return (
    <HStack justifyContent="flex-end">
      {registros.length > 0 && (
        <Button
          onClick={onOpen}
          size="xs"
          colorScheme="azul_3"
          leftIcon={<Icon as={IoSearchOutline} />}
        >
          Detalhes
        </Button>
      )}
      <ModalInteracaoEmissoes
        preco_unitario={preco_unitario}
        registros={registros}
        isOpen={isOpen}
        onClose={onClose}
      />
    </HStack>
  );
}
