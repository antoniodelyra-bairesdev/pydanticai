import { getColorHex } from "@/app/theme";
import { HStack, Icon, Text } from "@chakra-ui/react";
import {
  GroupBase,
  Select,
  SelectComponentsConfig,
  chakraComponents,
} from "chakra-react-select";
import Image, { StaticImageData } from "next/image";
import { useEffect, useState } from "react";

type Opcao = {
  label: string;
  src?: StaticImageData;
};

export type SelectXSProps = {
  editando?: boolean;
  isMulti?: boolean;
  placeholder?: string;
  opcoes: Opcao[];
  valor: null | Opcao | readonly Opcao[];
  onValorChange: (escolha: null | Opcao | readonly Opcao[]) => void;
};

const customComponents: SelectComponentsConfig<
  Opcao,
  true,
  GroupBase<Opcao>
> = {
  Option: ({ children, ...props }) => (
    <chakraComponents.Option {...props}>
      {props.data.src && (
        <Image
          alt={props.data.src.src}
          src={props.data.src}
          style={{
            marginRight: "8px",
          }}
          height={16}
          width={16}
        />
      )}
      {children}
    </chakraComponents.Option>
  ),
  MultiValueContainer: ({ children, ...props }) => (
    <chakraComponents.MultiValueContainer {...props}>
      <HStack gap={0} pr="8px" pl="8px">
        {props.data.src && (
          <Image
            alt={props.data.src.src}
            src={props.data.src}
            style={{
              marginRight: "8px",
            }}
            height={16}
            width={16}
          />
        )}
        {children}
      </HStack>
    </chakraComponents.MultiValueContainer>
  ),
  SingleValue: ({ children, ...props }) => (
    <chakraComponents.SingleValue {...props}>
      <HStack gap={0} pr="8px">
        {props.data.src && (
          <Image
            alt={props.data.src.src}
            src={props.data.src}
            style={{
              marginRight: "8px",
            }}
            height={16}
            width={16}
          />
        )}
        <Text fontSize="xs">{props.data.label}</Text>
      </HStack>
    </chakraComponents.SingleValue>
  ),
};

export default function SelectXS({
  editando,
  opcoes,
  valor,
  onValorChange,
  isMulti,
  placeholder = "Selecionar...",
}: SelectXSProps) {
  return (
    <Select
      isMulti={isMulti}
      options={opcoes}
      value={valor}
      onChange={onValorChange}
      isDisabled={!editando}
      chakraStyles={{
        inputContainer: (provided) => ({ ...provided, padding: 0 }),
        control: (provided) => ({
          ...provided,
          _focusVisible: {
            borderColor: "verde.main",
            boxShadow: "0 0 0 1px " + getColorHex("verde.main"),
          },
        }),
      }}
      size={"xs" as any}
      useBasicStyles
      components={customComponents as any}
      closeMenuOnSelect={!isMulti}
      placeholder={placeholder}
    />
  );
}
