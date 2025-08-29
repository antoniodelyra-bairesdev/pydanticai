"use client";

import { useSettings } from "@/lib/hooks";
import { ChevronRightIcon } from "@chakra-ui/icons";
import { Box } from "@chakra-ui/react";

export type NavigationOpenZoneProps = {
  onOpen: () => void;
};

export default function NavigationOpenZone({
  onOpen,
}: NavigationOpenZoneProps) {
  const { openDrawerOnHover } = useSettings().settings;

  return (
    <Box
      data-test-id="navigation-open-zone"
      zIndex={1000}
      onMouseEnter={openDrawerOnHover ? onOpen : undefined}
      position="fixed"
      top={0}
      left={0}
      width={`${openDrawerOnHover ? 12 : 0}px`}
      height="100vh"
      display="flex"
      flexDir="column"
      justifyContent="center"
    >
      <Box
        onClick={openDrawerOnHover ? undefined : onOpen}
        cursor="pointer"
        mt="8px"
        ml="-20px"
        display="flex"
        borderRadius="50%"
        boxShadow="md"
        alignItems="center"
        justifyContent="center"
        w="44px"
        h="44px"
        bgColor="verde.main"
      >
        <ChevronRightIcon ml="12px" color="white" boxSize="28px" />
      </Box>
    </Box>
  );
}
