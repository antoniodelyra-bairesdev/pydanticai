import { SelectOption } from "@/lib/types/api/iv/sistema";
import { Select } from "chakra-react-select";
import { Dispatch, SetStateAction } from "react";

type MultiSelectReadonlyProps = {
  corTextoReadOnly: string;
  placeholder?: string;
};

export function MultiSelectReadOnly({
  corTextoReadOnly,
  placeholder = "---",
}: MultiSelectReadonlyProps) {
  return (
    <Select
      isMulti
      isReadOnly
      placeholder={placeholder}
      useBasicStyles={true}
      chakraStyles={{
        container: (provided) => ({ ...provided, borderColor: "cinza.main" }),
        dropdownIndicator: (provided) => ({
          ...provided,
          color: corTextoReadOnly,
        }),
        inputContainer: (provided) => ({ ...provided, cursor: "not-allowed" }),
        multiValue: (provided) => ({
          ...provided,
          color: corTextoReadOnly,
          opacity: 1,
        }),
        placeholder: (provided) => ({
          ...provided,
          color: corTextoReadOnly,
          opacity: 1,
        }),
      }}
    />
  );
}

type MultiSelectProps<T> = {
  options: SelectOption[];
  state: T;
  setState: Dispatch<SetStateAction<T>>;
  prop: keyof T;
};

export function MultiSelect<T>({
  options,
  state,
  setState,
  prop,
}: MultiSelectProps<T>) {
  if (!Array.isArray(state[prop])) {
    console.warn("state[prop] deve retornar um array");
    return;
  }

  return (
    <Select
      isMulti
      useBasicStyles={true}
      options={options}
      placeholder={"---"}
      onChange={(selectedOptions) => {
        const ids = selectedOptions.map((option) => {
          if (typeof option.value === "string") {
            return parseInt(option.value);
          }

          return option.value;
        });

        setState((prevState: T) => {
          return {
            ...prevState,
            [prop]: ids,
          };
        });
      }}
      value={(state[prop] as number[]).map((elem) => {
        return options.find((option) => option.value === elem)!;
      })}
    />
  );
}
