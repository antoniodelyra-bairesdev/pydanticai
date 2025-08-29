import type { ChangeEvent, Dispatch, SetStateAction } from "react";
import { VStack, Text, StackProps } from "@chakra-ui/react";
import FileInput from "@/app/_components/files/FileInput";

type InputElementProps = {
  hint: string;
  label: string;
  isMultiFile?: boolean;
  stateValue: string;
  setState: Dispatch<SetStateAction<FileList | null>>;
  containerProps?: StackProps;
};

export default function InputElement({
  hint,
  label,
  isMultiFile = false,
  stateValue,
  setState,
  ...containerProps
}: InputElementProps) {
  return (
    <VStack
      alignItems="stretch"
      border="1px solid"
      borderColor="cinza.main"
      borderRadius="8px"
      py="5px"
      px="20px"
      width="450px"
      boxShadow="sm"
      {...containerProps}
    >
      <Text fontSize="xs">{hint}</Text>
      <FileInput
        label={label}
        placeholder={"Clique para inserir"}
        isMultiFile={isMultiFile}
        inputValue={stateValue}
        onChangeCallback={(event: ChangeEvent<HTMLInputElement>) => {
          if (!event.target.files || event.target.files.length === 0) {
            return;
          }
          setState(event.target.files);
        }}
        onClearCallback={() => setState(null)}
        labelProps={{
          fontWeight: "semibold",
        }}
      />
    </VStack>
  );
}
