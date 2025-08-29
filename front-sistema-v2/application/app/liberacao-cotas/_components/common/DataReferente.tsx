import { HStack, Text, Input } from "@chakra-ui/react";
import { Dispatch, SetStateAction } from "react";

type DataReferenteProps = {
  value: string;
  setValue: Dispatch<SetStateAction<string>>;
};

export default function DataReferente({ value, setValue }: DataReferenteProps) {
  return (
    <HStack>
      <Text fontSize="md">Data Referente:</Text>
      <Input
        height="40px"
        fontSize="md"
        width="180px"
        type="date"
        onChange={(ev) => {
          setValue(ev.target.value);
        }}
        value={value}
      />
    </HStack>
  );
}
