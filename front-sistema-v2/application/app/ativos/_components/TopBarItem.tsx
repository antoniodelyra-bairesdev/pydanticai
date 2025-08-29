"use client";

import { getColorHex } from "@/app/theme";
import { useColors } from "@/lib/hooks";
import { ChevronRightIcon } from "@chakra-ui/icons";
import {
  HStack,
  Popover,
  PopoverArrow,
  PopoverBody,
  PopoverContent,
  PopoverTrigger,
  Text,
} from "@chakra-ui/react";
import React from "react";

export type TopBarIconProps = {
  txt: string;
  icon?: React.ReactElement;
  color?: string;
  alignSelf?: string;
  menu?: React.ReactNode[];
};

export default function TopBarItem({
  icon,
  txt,
  color,
  alignSelf = "flex-start",
  menu = [],
}: TopBarIconProps) {
  const { hover, text } = useColors();
  const item = (
    <HStack
      transition="background-color 0.25s"
      p="2px"
      borderRadius="4px"
      justify="space-between"
      alignSelf={alignSelf}
      {...(menu.length
        ? {
            cursor: "pointer",
            border: `1px solid ${getColorHex(hover)}`,
            _hover: { backgroundColor: hover },
          }
        : {})}
    >
      <Text fontSize="xs" userSelect="none" color={color ?? text}>
        {icon} {txt}
      </Text>{" "}
      {menu.length && <ChevronRightIcon ml="12px" />}
    </HStack>
  );

  return menu.length ? (
    <Popover placement="right">
      <PopoverTrigger>{item}</PopoverTrigger>
      <PopoverContent w="auto" boxShadow="dark-lg">
        <PopoverArrow />
        <PopoverBody maxW="512px" lineHeight="2em">
          {menu}
        </PopoverBody>
      </PopoverContent>
    </Popover>
  ) : (
    item
  );
}
