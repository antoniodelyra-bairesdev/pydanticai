import { HStack, VStack } from "@chakra-ui/react";
import { ReactNode } from "react";

type TabPanelLayoutProps = {
  topComponent?: ReactNode;
  leftComponent: ReactNode;
  rightComponent: ReactNode;
};

export default function TabPanelLayout({
  topComponent,
  leftComponent,
  rightComponent,
}: TabPanelLayoutProps) {
  return (
    <VStack alignItems="stretch" gap="32px">
      {topComponent && <>{topComponent}</>}
      <VStack>
        <HStack width="100%" alignItems="flex-start" gap="50px">
          <VStack alignItems="flex-start" alignSelf="stretch">
            {leftComponent}
          </VStack>
          <VStack flex={1} minWidth="450px" alignItems="flex-start">
            {rightComponent}
          </VStack>
        </HStack>
      </VStack>
    </VStack>
  );
}
