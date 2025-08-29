import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import Hint from "@/app/_components/texto/Hint";
import { Erro } from "@/lib/types/api/iv/v1";
import {
  Button,
  Card,
  CardBody,
  HStack,
  ListItem,
  Text,
  UnorderedList,
  VStack,
} from "@chakra-ui/react";

export type ModalDetalhesErroProps = {
  isOpen: boolean;
  onClose: () => void;

  erro: Erro | null;
};

export default function ModalDetalhesErro({
  isOpen,
  onClose,
  erro,
}: ModalDetalhesErroProps) {
  return (
    <ConfirmModal
      isOpen={isOpen}
      onClose={onClose}
      title="Realocar"
      size="6xl"
      hideCancelButton={true}
      confirmContent="Fechar"
    >
      <VStack alignItems="stretch">
        <VStack gap={0} alignItems="stretch">
          <Hint>Erros</Hint>
          <Card variant="outline">
            <CardBody p="12px">
              {erro && (
                <>
                  <Text fontSize="sm" color="rosa.main">
                    {erro.resumo}
                  </Text>
                  <UnorderedList>
                    {erro.detalhes.map((err, i) => (
                      <ListItem key={i}>{err}</ListItem>
                    ))}
                  </UnorderedList>
                </>
              )}
            </CardBody>
          </Card>
        </VStack>
        <VStack gap={0} alignItems="stretch">
          <Hint>Ações</Hint>
          <Card variant="outline">
            <CardBody p="12px">
              <HStack>
                <Button size="xs" colorScheme="azul_3">
                  Reenviar mensagem
                </Button>
                <Button size="xs" colorScheme="azul_3">
                  Solicitar realocação do operador
                </Button>
              </HStack>
            </CardBody>
          </Card>
        </VStack>
      </VStack>
    </ConfirmModal>
  );
}
