"use client";

import {
  Box,
  BoxProps,
  Input,
  StackProps,
  Text,
  TextProps,
  VStack,
} from "@chakra-ui/react";
import { ChangeEvent, useEffect, useRef } from "react";

type FileDragAndDropProps = {
  placeholder?: string;
  isMultiFile?: boolean;
  shownText: string | null;
  state: FileList | null;
  onChangeCallback: (files: FileList) => void;
  width?: string;
  height?: string;
  containerProps?: BoxProps;
  textContainerProps?: StackProps;
  textProps?: TextProps;
};

export default function FileDragAndDrop({
  placeholder = "Arraste ou clique para selecionar",
  isMultiFile = false,
  shownText,
  state,
  onChangeCallback,
  containerProps,
  textContainerProps,
  textProps,
}: FileDragAndDropProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!state) {
      (fileInputRef.current as any).value = null;
    }
  }, [state]);

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <>
      <Input
        type="file"
        display="none"
        ref={fileInputRef}
        multiple={isMultiFile}
        onChange={(ev: ChangeEvent<HTMLInputElement>) => {
          if (!ev.target.files) {
            return;
          }
          onChangeCallback(ev.target.files);
        }}
      />
      <Box
        cursor="pointer"
        mt="12px"
        fontWeight={600}
        borderColor="cinza.400"
        borderStyle="dashed"
        borderWidth="2px"
        bgColor="cinza.200"
        onDragOver={(ev) => ev.preventDefault()}
        onClick={handleButtonClick}
        width="100%"
        height="144px"
        onDrop={(ev) => {
          ev.preventDefault();
          const { files }: { files: FileList } = ev.dataTransfer;
          onChangeCallback(files);
        }}
        {...containerProps}
      >
        <VStack
          h="100%"
          justifyContent="center"
          alignItems="center"
          {...textContainerProps}
        >
          <Text fontSize="lg" color="cinza.400" {...textProps}>
            {shownText ?? placeholder}
          </Text>
        </VStack>
      </Box>
    </>
  );
}
