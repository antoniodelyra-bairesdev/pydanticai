"use client";

import { Device } from "@/lib/types/api/iv/auth";
import { fmtDatetime } from "@/lib/util/string";
import { CalendarIcon } from "@chakra-ui/icons";
import { Box, HStack, Skeleton, Text, VStack } from "@chakra-ui/react";
import { UAParser } from "ua-parser-js";

export type DeviceProps = {
  device: Device;
};

export function DeviceLoading() {
  return (
    <Box pt="8px" pb="8px">
      <HStack gap="16px">
        <Box
          width="32px"
          height="32px"
          display="flex"
          justifyContent="center"
          alignItems="center"
        >
          <Skeleton width="24px" height="24px" />
        </Box>
        <VStack gap="4px" align="flex-start" mb="4px">
          <Skeleton width="170px" height="16px" />
          <Skeleton width="120px" height="14px" />
          <Skeleton width="120px" height="14px" />
        </VStack>
      </HStack>
    </Box>
  );
}

export default function Device({ device }: DeviceProps) {
  const { user_agent, session_started, last_active, location } = device;

  const os = (ua: string) => {
    const details = new UAParser(ua).getResult();
    return `${details.os.name ?? ""} ${details.os.version ?? ""}`;
  };

  const browser = (ua: string) => {
    const details = new UAParser(ua).getResult();
    return `${details.browser.name ?? ""} ${details.browser.version ?? ""}`;
  };

  return (
    <Box pt="8px" pb="8px">
      <HStack gap="16px">
        <Box
          width="32px"
          height="32px"
          display="flex"
          justifyContent="center"
          alignItems="center"
        >
          <CalendarIcon color="azul_1.700" boxSize="24px" />
        </Box>
        <VStack gap="0" align="flex-start">
          <Text fontSize="sm">
            <Text mr="8px" as="span">
              {browser(user_agent)}
            </Text>
            <Text color="cinza.500" as="span">
              ({os(user_agent)})
            </Text>
          </Text>
          <Text fontSize="xs">Último Acesso: {fmtDatetime(last_active)}</Text>
          <Text fontSize="xs" color="cinza.500">
            Primeiro Acesso: {fmtDatetime(session_started)}{" "}
            {location ? `(${location})` : ""}
          </Text>
        </VStack>
      </HStack>
    </Box>
  );
}
