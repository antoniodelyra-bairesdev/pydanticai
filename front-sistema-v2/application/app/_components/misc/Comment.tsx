import { getColorHex } from "@/app/theme";
import { Text, TextProps } from "@chakra-ui/react";
import React from "react";

export type CommentProps = {
  bgColor?: string;
  fontSize?: string;
  children?: React.ReactNode;
} & TextProps;

export default function Comment({
  bgColor = getColorHex("amarelo.main"),
  fontSize,
  children,
  ...props
}: CommentProps) {
  return (
    <Text
      fontSize={fontSize}
      borderRadius="4px"
      overflow="hidden"
      borderLeft={"4px solid " + bgColor}
      bgColor={bgColor + "2f"}
      p="4px"
      pl="8px"
      {...props}
    >
      {children}
    </Text>
  );
}
