"use client";

import { Box, HStack, Icon, useDisclosure, VStack } from "@chakra-ui/react";
import React from "react";
import { IoCloseOutline, IoExpandOutline } from "react-icons/io5";

export default function LayoutContent({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isOpen, onToggle } = useDisclosure();
  return (
    <VStack
      overflow="hidden"
      flex={1}
      borderRadius="8px"
      bgColor="cinza.main"
      zIndex={1}
      {...(isOpen
        ? {
            position: "absolute",
            top: "8px",
            left: "8px",
            right: "8px",
            bottom: "8px",
          }
        : {
            position: "relative",
          })}
    >
      <HStack
        position="absolute"
        top={0}
        left={0}
        boxShadow="0px 1px 1px lightgray"
        p="4px"
        borderRadius="full"
        w="28px"
        h="28px"
        color="cinza.500"
        bgColor="cinza.50"
        _hover={{
          bgColor: "cinza.200",
          cursor: "pointer",
          color: isOpen ? "rosa.main" : "verde.600",
        }}
        transition="all 0.125s"
        onClick={onToggle}
        zIndex={2}
      >
        <Icon
          as={isOpen ? IoCloseOutline : IoExpandOutline}
          w="20px"
          h="20px"
        />
      </HStack>
      {children}
    </VStack>
  );
}
