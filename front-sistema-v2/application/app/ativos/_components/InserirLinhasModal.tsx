import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import {
  NumberDecrementStepper,
  NumberIncrementStepper,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
} from "@chakra-ui/react";
import React, { useState } from "react";

export type InserirEventoModalProps = {
  isOpen: boolean;
  onClose(): void;
  insertAction(amount: number): void;
  title?: React.ReactNode;
};

export default function InserirLinhasModal({
  insertAction,
  isOpen,
  onClose,
  title,
}: InserirEventoModalProps) {
  const [newRowsAmount, setNewRowsAmount] = useState(1);
  const getNum = (setter: (n: number) => void) => (_: unknown, num: number) =>
    setter(isNaN(num) ? 1 : num);

  return (
    <ConfirmModal
      isOpen={isOpen}
      onClose={onClose}
      onConfirmAction={() => {
        insertAction(newRowsAmount);
      }}
      title={title ?? "Quantas linhas deseja inserir?"}
    >
      <NumberInput
        focusBorderColor="verde.main"
        size="sm"
        defaultValue={1}
        min={1}
        step={1}
        keepWithinRange={true}
        clampValueOnBlur={true}
        onChange={getNum(setNewRowsAmount)}
        value={newRowsAmount}
      >
        <NumberInputField />
        <NumberInputStepper>
          <NumberIncrementStepper />
          <NumberDecrementStepper />
        </NumberInputStepper>
      </NumberInput>
    </ConfirmModal>
  );
}
