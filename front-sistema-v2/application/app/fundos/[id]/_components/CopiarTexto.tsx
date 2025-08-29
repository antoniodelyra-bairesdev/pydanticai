"use client";

import { CloseIcon, CopyIcon } from "@chakra-ui/icons";
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  Divider,
  HStack,
  Input,
  StackDivider,
  StackProps,
  Text,
  Tooltip,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import Image, { StaticImageData } from "next/image";
import { useRef } from "react";
import InputEditavel from "./InputEditavel";

export type CopiarTextoProps = {
  editando?: boolean;
  valor: string;
  onValorChange?: (v: string) => void;
} & StackProps;

export default function CopiarTexto({
  valor,
  editando,
  onValorChange,
  ...props
}: CopiarTextoProps) {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const timeoutRef = useRef(-1);

  const copiar = () => {
    if (!("clipboard" in navigator)) return;
    navigator.clipboard.writeText(valor);
    onOpen();
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
    timeoutRef.current = window.setTimeout(() => onClose(), 1500);
  };

  return (
    <HStack gap={0} alignItems="stretch" {...props}>
      <HStack flex={1} p={!editando ? "0 12px 0 4px" : undefined} h="24px">
        <InputEditavel
          flex={1}
          editando={editando}
          valor={valor}
          onValorChange={onValorChange}
        />
      </HStack>
      {!editando && (
        <Tooltip
          isOpen={isOpen}
          placement="bottom"
          borderRadius="full"
          pointerEvents="all"
          label={
            <HStack fontSize="xs" cursor="pointer" onClick={onClose}>
              <Text>Valor copiado para área de transferência</Text>
            </HStack>
          }
        >
          <HStack
            bgColor="cinza.50"
            onClick={copiar}
            cursor="pointer"
            borderLeft="1px solid"
            borderColor="cinza.main"
            justifyContent="center"
            w="24px"
            h="24px"
            _hover={{ bgColor: "cinza.main" }}
          >
            <CopyIcon />
          </HStack>
        </Tooltip>
      )}
    </HStack>
  );
}
