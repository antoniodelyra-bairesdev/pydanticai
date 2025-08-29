import { fmtDatetime } from "@/lib/util/string";
import { HStack, Icon, Text, VStack } from "@chakra-ui/react";
import { IoCalendarOutline, IoTimeOutline } from "react-icons/io5";

export type HorarioProps = {
  horario: string;
};

export default function Horario({ horario }: HorarioProps) {
  const [date, time] = fmtDatetime(horario).split(" ");
  return (
    <HStack alignItems="center" gap="12px">
      <HStack alignItems="center" gap="3px">
        <Icon w="11px" h="11px" color="verde.main" as={IoTimeOutline} />
        <Text fontSize="11px" color="cinza.700">
          {time}
        </Text>
      </HStack>
      <HStack alignItems="center" gap="4px">
        <Icon w="11px" h="11px" color="verde.main" as={IoCalendarOutline} />
        <Text fontSize="11px" color="cinza.700">
          {date}
        </Text>
      </HStack>
    </HStack>
  );
}
