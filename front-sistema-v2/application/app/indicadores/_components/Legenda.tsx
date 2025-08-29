import { Box, HStack, Text } from "@chakra-ui/react";
import React from "react";

export type LegendaProps = {
  text: string;
  colorScheme?: string;
  size?: string;
  border?: string;
  background?: string;
};

export default function Legenda({
  text,
  size = "8px",
  background,
  border,
  colorScheme,
}: LegendaProps) {
  const bd = colorScheme ? colorScheme + ".900" : (border ?? "cinza.900");
  const bg = colorScheme ? colorScheme + ".main" : (background ?? "cinza.main");
  return (
    <HStack
      border="1px solid"
      borderColor="cinza.main"
      overflow="hidden"
      borderRadius="8px"
      p="2px 4px 2px 4px"
      gap="4px"
    >
      <Box
        w={size}
        h={size}
        borderRadius="50%"
        border="1px solid"
        borderColor={bd}
        bgColor={bg}
      />
      <Text color={bd} fontSize="xs">
        {text}
      </Text>
    </HStack>
  );
}
