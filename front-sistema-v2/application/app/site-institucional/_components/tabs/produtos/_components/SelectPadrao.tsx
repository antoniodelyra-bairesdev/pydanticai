import { Select } from "@chakra-ui/react";
import { Dispatch, SetStateAction } from "react";

export type SelectReadOnlyPadraoProps = {
  statePropValue: boolean | null;
  corTexto: string;
};

export function SelectReadOnlyPadrao({
  statePropValue,
  corTexto,
}: SelectReadOnlyPadraoProps) {
  const selectValue = String(statePropValue);

  const getOptionLabel = (selectValue: string) => {
    switch (selectValue) {
      case "null":
        return "---";
      case "true":
        return "Sim";
      case "false":
        return "Não";
      default:
        return "???";
    }
  };

  return (
    <Select
      isDisabled
      cursor="not-allowed"
      fontSize="16px"
      _disabled={{
        color: corTexto,
        opacity: 1,
        cursor: "not-allowed",
      }}
    >
      <option style={{ color: "black" }} value={selectValue}>
        {getOptionLabel(selectValue)}
      </option>
    </Select>
  );
}

export type SelectPadraoProps<T> = {
  state: T;
  setState: Dispatch<SetStateAction<T>>;
  propriedade: keyof T;
  obrigatorio?: boolean;
};

export function SelectPadrao<T>({
  state,
  obrigatorio,
  setState,
  propriedade,
}: SelectPadraoProps<T>) {
  const selectValue = String(state[propriedade]);

  return (
    <Select
      fontSize="16px"
      value={selectValue}
      onChange={(ev) => {
        switch (ev.target.value) {
          case "null":
            setState((prevState: T) => ({
              ...prevState,
              [propriedade]: null,
            }));
            break;
          case "true":
            setState((prevState: T) => ({
              ...prevState,
              [propriedade]: true,
            }));
            break;
          case "false":
            setState((prevState: T) => ({
              ...prevState,
              [propriedade]: false,
            }));
            break;
          default:
            console.warn(
              `Era esperado um boolean ou null para state[propriedade].\nValor recebido de state[propriedade]:\n\t${state[propriedade]}`,
            );
        }
      }}
    >
      <option disabled={obrigatorio} hidden={obrigatorio} value="null">
        ---
      </option>
      <option value="true">Sim</option>
      <option value="false">Não</option>
    </Select>
  );
}
