import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { Radio, RadioGroup, Text, VStack } from "@chakra-ui/react";

export type ModalCarregarFluxoProps = {
  isOpen: boolean;
  onClose: () => void;
};

export default function ModalCarregarFluxo({
  isOpen,
  onClose,
}: ModalCarregarFluxoProps) {
  return (
    <ConfirmModal
      title="Novo cálculo"
      isOpen={isOpen}
      onClose={onClose}
      size="3xl"
    >
      <Text>Características iniciais:</Text>
      <RadioGroup size="sm" mt="12px">
        <VStack alignItems="stretch" gap={0}>
          <Radio value="ativo">Carregar de ativo</Radio>
          <Radio value="duplicar">Duplicar de cálculo existente</Radio>
          <Radio value="vazio">Inserir manualmente</Radio>
        </VStack>
      </RadioGroup>
    </ConfirmModal>
  );
}
