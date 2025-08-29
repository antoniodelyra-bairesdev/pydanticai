import TextInput from "@/app/_components/forms/TextInput";
import { Dispatch, SetStateAction } from "react";

export type InputReadOnlyProps = {
  type?: "text" | "number";
  state?: string | number;
  corTexto: string;
};

export function InputReadOnlyTextoPadrao({
  type,
  state,
  corTexto,
}: InputReadOnlyProps) {
  return (
    <TextInput
      border="solid"
      borderWidth="1px"
      borderColor="cinza.main"
      color={corTexto}
      borderRadius="6px"
      fontSize="16px"
      height="40px"
      cursor="not-allowed"
      isReadOnly
      type={type ?? "text"}
      value={state ?? "---"}
    />
  );
}

type InputTextoPadraoProps<T> = {
  type?: "text" | "number";
  state: T;
  setState: Dispatch<SetStateAction<T>>;
  propriedade: keyof T;
};

export function InputTextoPadrao<T>({
  type,
  state,
  setState,
  propriedade,
}: InputTextoPadraoProps<T>) {
  const textInputValue = state[propriedade];

  if (
    typeof textInputValue !== "string" &&
    typeof textInputValue !== "number" &&
    textInputValue !== null
  ) {
    console.warn("state[propriedade] deve ser do tipo string ou number");
    return;
  }

  return (
    <TextInput
      border="solid"
      borderWidth="1px"
      borderColor="cinza.main"
      borderRadius="6px"
      fontSize="16px"
      height="40px"
      type={type ?? "text"}
      placeholder="---"
      value={(textInputValue as string) ?? ""}
      onChange={(ev) => {
        if (ev.target.value == "") {
          setState((prevState: T) => ({
            ...prevState,
            [propriedade]: null,
          }));

          return;
        }

        setState((prevState: T) => ({
          ...prevState,
          [propriedade]: ev.target.value,
        }));
      }}
    />
  );
}
