"use client";

import { Box, keyframes } from "@chakra-ui/react";

const frames = (depth: number) => keyframes`
    0% { transform: translate(0%, 0%) }
    50% { transform: translate(0%, -${100 / depth / 4}%) }
    100% { transform: translate(0%, 0%) }
`;

const animation = (depth: number) =>
  `${frames(depth)} ${(2 + depth / 5) * 2}s ease-in-out infinite`;

type WaveProps = {
  color: string;
  depth: number;
};

export function Wave({ color, depth }: WaveProps) {
  return (
    <Box
      width="100%"
      height={`${15 - depth * 2}%`}
      display="flex"
      flexDirection="row"
      justifyContent="stretch"
      animation={animation(depth)}
      position="relative"
      zIndex={-1000 - depth}
    >
      <Box bgColor={color} width="100%" height="200%" position="absolute" />
    </Box>
  );
}

export default function Waves() {
  return (
    <Box
      bgColor="cinza.main"
      width="100vw"
      height="100vh"
      position="absolute"
      top={0}
      left={0}
      display="flex"
      flexDirection="column-reverse"
      overflow="hidden"
      zIndex={-1000}
    >
      <Wave color="azul_1.main" depth={1} />
      <Wave color="azul_2.main" depth={2} />
      <Wave color="azul_3.main" depth={3} />
      <Wave color="azul_4.main" depth={4} />
    </Box>
  );
}
