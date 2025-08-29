import { SelectOption } from "@/lib/types/api/iv/sistema";
import { Select } from "@chakra-ui/react";
import type { ChangeEvent, Dispatch, SetStateAction } from "react";

export type SelectDinamicoReadOnlyProps = {
  statePropValue: string | number | null;
  options: SelectOption[];
  corTexto: string;
};

export function SelectDinamicoReadOnly({
  statePropValue,
  options,
  corTexto,
}: SelectDinamicoReadOnlyProps) {
  const selectValue = String(statePropValue);
  const selectedOptionLabel: string =
    options.find((option) => String(option.value) === selectValue)?.label ??
    "---";

  return (
    <Select
      isDisabled
      value={selectValue}
      _disabled={{
        color: corTexto,
        opacity: 1,
        cursor: "not-allowed",
      }}
    >
      <option disabled value={selectValue}>
        {selectedOptionLabel}
      </option>
    </Select>
  );
}

export type SelectDinamicoProps<T> = {
  obrigatorio?: boolean;
  options: SelectOption[];
  state: T;
  setState: Dispatch<SetStateAction<T>>;
  stateProp: keyof T;
};

export function SelectDinamico<T>({
  obrigatorio,
  options,
  state,
  setState,
  stateProp,
}: SelectDinamicoProps<T>) {
  const selectValue = String(state[stateProp]);

  return (
    <Select
      value={selectValue}
      onChange={(ev: ChangeEvent<HTMLSelectElement>) => {
        if (ev.target.value === "null") {
          setState((prevState: T) => ({
            ...prevState,
            [stateProp]: null,
          }));

          return;
        }

        setState((prevState: T) => ({
          ...prevState,
          [stateProp]: parseInt(ev.target.value),
        }));
      }}
    >
      {obrigatorio && (
        <option disabled={obrigatorio} value={String(null)}>
          ---
        </option>
      )}
      {options.map((opcao, index) => {
        return (
          <option key={index} value={opcao.value}>
            {opcao.label}
          </option>
        );
      })}
    </Select>
  );
}
