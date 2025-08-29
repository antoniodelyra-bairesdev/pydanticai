"use client";

import { getColorHex } from "@/app/theme";
import { EditIcon, SmallCloseIcon } from "@chakra-ui/icons";
import { Button, HStack, Text } from "@chakra-ui/react";
import { IoSaveOutline } from "react-icons/io5";

export type GridEditBarProps = {
  editing: boolean;
  setEditing: (value: boolean) => void;
  editedCount: number;
  onSave: () => void;
};

export default function GridEditBar({
  editing,
  setEditing,
  editedCount,
  onSave,
}: GridEditBarProps) {
  const { icon, color, text } = editing
    ? {
        icon: <SmallCloseIcon />,
        color: "rosa",
        text: "Desabilitar modo de edição",
      }
    : { icon: <EditIcon />, color: "azul_1", text: "Habilitar modo de edição" };

  return (
    <HStack justifyContent="space-between" w="100%" p="8px" wrap="wrap">
      <HStack wrap="wrap">
        <Button
          key="editar"
          size="xs"
          leftIcon={icon}
          colorScheme={color}
          onClick={() => setEditing(!editing)}
        >
          {text}
        </Button>
        {editing && (
          <Button
            key="salvar"
            isDisabled={editedCount === 0}
            size="xs"
            leftIcon={<IoSaveOutline />}
            colorScheme="azul_1"
            onClick={onSave}
          >
            Salvar
          </Button>
        )}
      </HStack>
      {editedCount > 0 && (
        <HStack
          wrap="wrap"
          key="edited"
          w="36px"
          h="24px"
          border="1px solid"
          borderColor="cinza.main"
          borderRadius="4px"
          bgColor={getColorHex("amarelo.50")}
          color="amarelo.900"
          fontSize="12px"
          justifyContent="center"
          gap={0}
        >
          <EditIcon fontSize="8px" mr="2px" />
          <Text as="span">{editedCount}</Text>
        </HStack>
      )}
    </HStack>
  );
}
