"use client";

import { Box, Skeleton, VStack } from "@chakra-ui/react";

export default function FundosLoading() {
  return (
    <Box p="36px 48px">
      <VStack align="flex-start">
        {Array(8)
          .fill("")
          .map((_, i) => (
            <Skeleton key={i} width="100%" height="30px" />
          ))}
        <Skeleton mt="24px" key="btn" width="174px" height="40px" />
      </VStack>
    </Box>
  );
}
