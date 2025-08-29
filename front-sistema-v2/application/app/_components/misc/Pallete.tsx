import { colorsVanguarda } from "@/app/theme";
import { Box, HStack, Text, VStack } from "@chakra-ui/react";

export default function Pallete() {
  return (
    <HStack>
      <VStack gap={0}>
        {Object.keys(colorsVanguarda).map((name) => (
          <HStack w="100px" justifyContent="space-between">
            <Text>{name}</Text>
            <Box
              bgColor={
                colorsVanguarda[name as keyof typeof colorsVanguarda].main
              }
              w="24px"
              h="24px"
            />
          </HStack>
        ))}
      </VStack>
      <VStack gap={0}>
        {Object.values(colorsVanguarda).map((pallete) => (
          <HStack gap={0}>
            {Object.entries(pallete)
              .filter(([k]) => !isNaN(Number(k)))
              .map(([_, color]) => (
                <Box
                  bgColor={color}
                  border={
                    color === pallete["main"] ? "1px solid black" : undefined
                  }
                  w="24px"
                  h="24px"
                />
              ))}
          </HStack>
        ))}
      </VStack>
    </HStack>
  );
}
