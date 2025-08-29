import { HStack, Input, InputProps, StackProps, Text } from "@chakra-ui/react";

export type InputEditavelProps = {
  editando?: boolean;
  placeholder?: string;
  textoValorVazio?: string;
  valor?: string;
  onValorChange?: (novoValor: string) => void;
} & StackProps;

export default function InputEditavel({
  editando,
  placeholder,
  textoValorVazio = "Não cadastrado",
  valor = "",
  onValorChange,
  ...props
}: InputEditavelProps) {
  return (
    <HStack h="24px" {...props}>
      {editando ? (
        <Input
          bgColor="white"
          placeholder={placeholder}
          focusBorderColor="verde.main"
          flex={1}
          size="xs"
          value={valor}
          onChange={(ev) => onValorChange?.(ev.target.value)}
        />
      ) : (
        <Text color={valor ? "azul_2.main" : "cinza.400"}>
          {valor || textoValorVazio}
        </Text>
      )}
    </HStack>
  );
}
