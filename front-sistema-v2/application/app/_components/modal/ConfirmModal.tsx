import {
  AlertDialog,
  AlertDialogBody,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogOverlay,
  BoxProps,
  Button,
  ResponsiveValue,
} from "@chakra-ui/react";
import React, { useRef } from "react";

export type ConfirmModalProps = {
  isOpen: boolean;
  onClose(): void;
  children?: React.ReactNode;
  onConfirmAction?(): void;
  onCancelAction?(): void;
  title?: React.ReactNode;
  size?:
    | ResponsiveValue<
        | "sm"
        | "md"
        | "lg"
        | "xl"
        | "2xl"
        | (string & {})
        | "xs"
        | "3xl"
        | "4xl"
        | "5xl"
        | "6xl"
        | "full"
      >
    | undefined;
  confirmEnabled?: boolean;
  confirmContent?: React.ReactNode;
  cancelContent?: React.ReactNode;
  overflow?: BoxProps["overflow"];
  hideCancelButton?: boolean;
  hideConfirmButton?: boolean;
  position?: "start" | "center" | "end";
  mb?: string | number;
};

export default function ConfirmModal({
  title = "Confirmar ação",
  isOpen,
  onClose,
  onCancelAction,
  onConfirmAction,
  children,
  size,
  overflow,
  hideCancelButton,
  hideConfirmButton,
  confirmEnabled = true,
  cancelContent = "Cancelar",
  confirmContent = "Confirmar",
  position,
  mb = 0,
}: ConfirmModalProps) {
  const cancelRef = useRef<HTMLButtonElement>(null);
  const close = () => {
    onCancelAction?.();
    onClose();
  };
  const confirm = () => {
    onConfirmAction?.();
    onClose();
  };
  return (
    <AlertDialog
      isOpen={isOpen}
      onClose={close}
      leastDestructiveRef={cancelRef}
      size={size}
    >
      <AlertDialogOverlay>
        <AlertDialogContent
          ml={0}
          mr={0}
          mb={mb}
          maxH="90vh"
          overflow="hidden"
          alignSelf={position}
        >
          <AlertDialogHeader bgColor="azul_1.600" color="white">
            {title}
          </AlertDialogHeader>
          <AlertDialogBody
            display="flex"
            flexDirection="column"
            overflow="auto"
          >
            {children}
          </AlertDialogBody>
          <AlertDialogFooter gap={2}>
            {!hideCancelButton && (
              <Button size="sm" ref={cancelRef} onClick={close}>
                {cancelContent}
              </Button>
            )}
            {!hideConfirmButton && (
              <Button
                isDisabled={!confirmEnabled}
                size="sm"
                colorScheme="azul_1"
                onClick={confirm}
              >
                {confirmContent}
              </Button>
            )}
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialogOverlay>
    </AlertDialog>
  );
}
