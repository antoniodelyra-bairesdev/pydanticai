import { ChangeEvent, useEffect, useRef } from "react";
import { IoCloseCircleOutline } from "react-icons/io5";

import {
  Input,
  Text,
  Icon,
  HStack,
  TextProps,
  InputProps,
} from "@chakra-ui/react";

type FileInputProps = {
  label: string | undefined;
  placeholder: string | undefined;
  isMultiFile?: boolean;
  inputValue: string | undefined | null;
  isClearable?: boolean;
  onChangeCallback: (event: ChangeEvent<HTMLInputElement>) => void;
  onClearCallback: () => void;
  inputProps?: InputProps;
  labelProps?: TextProps;
};

export default function FileInput({
  label,
  placeholder,
  isMultiFile = false,
  inputValue,
  isClearable = true,
  onChangeCallback,
  onClearCallback,
  inputProps,
  labelProps,
}: FileInputProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!inputValue) {
      (fileInputRef.current as any).value = null;
    }
  }, [inputValue]);

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  if (inputValue == null || inputValue == undefined) {
    inputValue = "";
  }

  return (
    <HStack>
      <Text fontSize="xs" {...labelProps}>
        {label}:
      </Text>
      <Input
        flex={1}
        width="200px"
        height="30px"
        py="0px"
        px="6px"
        placeholder={placeholder ? placeholder : ""}
        fontSize="xs"
        value={inputValue}
        onClick={handleButtonClick}
        isReadOnly={true}
        cursor="pointer"
      />
      <Input
        type="file"
        display="none"
        ref={fileInputRef}
        onChange={onChangeCallback}
        multiple={isMultiFile}
        {...inputProps}
      />
      {isClearable && (
        <Icon
          w="20px"
          h="20px"
          as={IoCloseCircleOutline}
          onClick={onClearCallback}
          cursor="pointer"
          _hover={{
            color: "azul_4.main",
          }}
          transition="0.25s all"
        />
      )}
    </HStack>
  );
}
