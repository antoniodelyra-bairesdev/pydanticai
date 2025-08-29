"use client";

import { getColorHex } from "@/app/theme";
import { Box, HStack, VStack, keyframes } from "@chakra-ui/react";
import IVLogo from "../images/IVLogo";

const frames = (depth: number) => keyframes`
    0% { transform: translate(0%, 0%) }
    50% { transform: translate(0%, -${100 / depth / 4}%) }
    100% { transform: translate(0%, 0%) }
`;

const animation = (depth: number) =>
  `${frames(depth)} ${(2 + depth / 5) * 2}s ease-in-out infinite`;

export default function Boat() {
  return (
    <VStack
      animation={animation(3)}
      zIndex={-1003}
      w="144px"
      h="192px"
      marginLeft="15vw"
      marginBottom="30vh"
      position="absolute"
      justifyContent="flex-end"
      gap={0}
    >
      <HStack
        gap={0}
        w="100%"
        justifyContent="flex-end"
        alignItems="flex-start"
        flex={1}
      >
        <Box w="5%" h="100%" bgColor="azul_1.main" />
        <HStack
          w="60%"
          h="90%"
          clipPath="polygon(0 0, 0% 100%, 100% 100%)"
          bgColor="white"
          alignItems="flex-end"
        >
          <Box w="66%" aspectRatio={1}>
            <IVLogo variant="icon" />
          </Box>
        </HStack>
      </HStack>
      <Box
        clipPath="polygon(0 0, 100% 0, 87.5% 100%, 12.5% 100%)"
        w="100%"
        h="20%"
        bgColor="white"
      />
    </VStack>
  );
}
