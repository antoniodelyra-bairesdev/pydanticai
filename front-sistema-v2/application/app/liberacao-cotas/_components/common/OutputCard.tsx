import {
  Button,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Icon,
  Text,
  Spinner,
  HStack,
  VStack,
} from "@chakra-ui/react";
import { IoCheckmarkSharp, IoCloseSharp, IoWarning } from "react-icons/io5";

type InputStatus = {
  label: string;
  isOk: boolean;
};

type OutputCardProps = {
  width: string;
  cardTitle: string;
  inputsStatuses: InputStatus[];
  isLoading: boolean;
  isButtonDisabled?: boolean;
  hasWarning: boolean;
  hasError: boolean;
  requestCallback: () => Promise<void>;
};

export default function OutputCard({
  width,
  cardTitle,
  inputsStatuses,
  isLoading,
  isButtonDisabled = false,
  hasWarning,
  hasError,
  requestCallback,
}: OutputCardProps) {
  const isButtonEnabled = inputsStatuses.reduce((accumulator, currentValue) => {
    return accumulator && currentValue.isOk;
  }, true);

  return (
    <Card overflow="hidden" width={width} minH="256px">
      <CardHeader bgColor="azul_1.main">
        <Heading color="white" size="sm">
          {cardTitle}
        </Heading>
      </CardHeader>
      <CardBody
        p="12px 16px"
        display="flex"
        flexDirection="column"
        justifyContent="space-between"
      >
        <VStack alignItems="start">
          {inputsStatuses.map((inputStatus: InputStatus) => {
            return (
              <HStack justifyContent="space-between" width="100%">
                <Text>{inputStatus.label}</Text>
                <Text color={inputStatus.isOk ? "verde.main" : "rosa.main"}>
                  <Icon
                    as={inputStatus.isOk ? IoCheckmarkSharp : IoCloseSharp}
                  />
                </Text>
              </HStack>
            );
          })}
        </VStack>
        <HStack alignSelf="flex-end">
          {hasError && <Icon color="rosa.main" boxSize={6} as={IoWarning} />}
          {hasWarning && (
            <Icon color="amarelo.main" boxSize={6} as={IoWarning} />
          )}
          <Button
            colorScheme="verde"
            isDisabled={isLoading || !isButtonEnabled || isButtonDisabled}
            onClick={async () => {
              if (isLoading || !isButtonEnabled || isButtonDisabled) {
                return;
              }

              await requestCallback();
            }}
          >
            Exportar {isLoading && <Spinner width="10px" height="10px" />}
          </Button>
        </HStack>
      </CardBody>
    </Card>
  );
}
