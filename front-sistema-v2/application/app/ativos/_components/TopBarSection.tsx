"use client";

import { Card, CardBody, Heading, VStack } from "@chakra-ui/react";
import React from "react";

export type TopBarSectionProps = {
  title: string;
  children: React.ReactNode;
  flexGrow?: number;
  minW?: string;
  maxW?: string;
};

export default function TopBarSection({
  title,
  children,
  flexGrow,
  minW,
  maxW,
}: TopBarSectionProps) {
  return (
    <Card flexGrow={flexGrow} minW={minW} maxW={maxW} variant="outline">
      <CardBody p="10px">
        <VStack h="100%" gap="4px" alignItems="stretch">
          <Heading size="xs" mb="12px">
            {title}
          </Heading>
          {children}
        </VStack>
      </CardBody>
    </Card>
  );
}
