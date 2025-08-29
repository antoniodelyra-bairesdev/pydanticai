"use client";

import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons";
import {
  IconButton,
  Input,
  InputGroup,
  InputProps,
  InputRightElement,
} from "@chakra-ui/react";
import { useState } from "react";
import MaskedInput, { MaskedInputProps } from "react-text-mask";

export default function TextInput(
  props: Omit<InputProps, "type"> & {
    type?: InputProps["type"] | "masked";
    mask?: MaskedInputProps["mask"];
  },
) {
  const [hidden, setHidden] = useState(true);

  const { type, mask } = props;

  return type !== "password" ? (
    <Input
      size="sm"
      as={mask ? MaskedInput : Input}
      mask={mask}
      focusBorderColor="verde.main"
      errorBorderColor="rosa.main"
      {...props}
    />
  ) : (
    <InputGroup>
      <Input
        size="sm"
        focusBorderColor="verde.main"
        errorBorderColor="rosa.main"
        {...props}
        type={hidden ? "password" : "text"}
      />
      <InputRightElement mt="1px" mr="1px" height="calc(100% - 2px)">
        <IconButton
          onClick={() => setHidden(!hidden)}
          aria-label={hidden ? "Mostrar senha" : "Ocultar senha"}
          h="100%"
          icon={hidden ? <ViewIcon /> : <ViewOffIcon />}
        />
      </InputRightElement>
    </InputGroup>
  );
}
