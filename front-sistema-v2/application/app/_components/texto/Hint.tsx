"use client";

import { Text, TextProps } from "@chakra-ui/react";

export default function Hint({
  children,
  ...other
}: { children: React.ReactNode } & TextProps) {
  return (
    <Text fontSize="xs" color="cinza.500" {...other}>
      {" "}
      {children}{" "}
    </Text>
  );
}
