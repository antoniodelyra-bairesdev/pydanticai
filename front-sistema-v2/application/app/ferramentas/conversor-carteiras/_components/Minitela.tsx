import {
  Box,
  Card,
  HStack,
  Icon,
  keyframes,
  Progress,
  VStack,
} from "@chakra-ui/react";
import {
  IoCheckmarkOutline,
  IoCloseOutline,
  IoCloudDownloadOutline,
  IoCloudUploadOutline,
  IoDocumentOutline,
} from "react-icons/io5";

const Xml401 = ({ status }: { status: "4" | "5" | "D" }) => (
  <HStack
    h="10px"
    bgColor={
      {
        "4": "verde.50",
        "5": "verde.50",
        D: "rosa.50",
      }[status]
    }
    p="0 4px"
    borderBottom="1px solid"
    borderColor={
      {
        "4": "verde.100",
        "5": "verde.100",
        D: "rosa.100",
      }[status]
    }
    alignItems="stretch"
  >
    <Icon
      as={IoDocumentOutline}
      w="8px"
      h="8px"
      color={
        {
          "4": "verde.main",
          "5": "roxo.main",
          D: "rosa.main",
        }[status]
      }
    />
    <HStack flex={3} p="2px" alignItems="stretch">
      <Box flex={1} bgColor="cinza.400" />
    </HStack>
    <HStack flex={1} p="2px" alignItems="stretch" gap="2px">
      <Box
        w="6px"
        bgColor={
          {
            "4": "verde.main",
            "5": "roxo.main",
            D: "rosa.main",
          }[status]
        }
      />
      <Box flex={1} bgColor="cinza.400" />
    </HStack>
  </HStack>
);

const frames = () => keyframes`
    0% { outline-width: 0px; }
    50% { outline-width: 4px; }
    100% { outline-width: 0px; }
`;

const animation = `${frames()} 1s ease-in-out infinite`;

const highlight = (passo: number, valor: number) => ({
  animation: passo === valor ? animation : "none",
  outline: "0px solid",
  outlineColor: "azul_4.main",
  zIndex: passo === valor ? 1 : 0,
});

export default function MiniTela({ passo = 0 }: { passo?: number }) {
  return (
    <VStack alignItems="stretch" bgColor="cinza.main" p="4px" gap="4px">
      <HStack h="64px" alignItems="stretch" gap="4px">
        <Card w="96px" borderLeft="3px solid" borderColor="azul_1.main">
          <VStack
            flex={1}
            alignSelf="stretch"
            alignItems="stretch"
            justifyContent="center"
            gap="2px"
            p="4px"
          >
            <HStack>
              <Icon
                as={IoDocumentOutline}
                color="verde.main"
                w="12px"
                h="12px"
              />
              <Box h="8px" flex={1} bgColor="cinza.400" />
            </HStack>
            <HStack gap="2px">
              <HStack
                flex={1}
                h="8px"
                bgColor="cinza.100"
                justifyContent="center"
              ></HStack>
              <HStack
                flex={1}
                h="8px"
                bgColor="cinza.100"
                justifyContent="center"
              ></HStack>
            </HStack>
          </VStack>
        </Card>
        <Card flex={1} {...highlight(passo, 0)}>
          <HStack
            justifyContent="space-around"
            alignItems="center"
            w="100%"
            h="100%"
          >
            <HStack
              borderRadius="2px"
              border="1px solid"
              borderColor="cinza.main"
              w="20%"
              h="75%"
              alignItems="center"
              justifyContent="center"
              p="4px"
              gap="4px"
              {...highlight(passo, 2)}
            >
              <Box w="8px" h="8px" borderRadius="4px" bgColor="verde.main" />
              <VStack
                flex={1}
                alignSelf="stretch"
                alignItems="stretch"
                justifyContent="center"
                gap="2px"
              >
                <Box h="8px" w="60%" bgColor="cinza.400" />
                <Box h="8px" bgColor="cinza.main" {...highlight(passo, 3)} />
                <HStack gap="2px">
                  <HStack
                    flex={1}
                    h="8px"
                    bgColor="cinza.100"
                    justifyContent="center"
                  >
                    <Icon
                      w="10px"
                      h="10px"
                      as={IoCloseOutline}
                      color="rosa.main"
                    />
                  </HStack>
                  <HStack
                    flex={1}
                    h="8px"
                    bgColor="cinza.100"
                    justifyContent="center"
                    {...highlight(passo, 3)}
                  >
                    <Icon
                      w="10px"
                      h="10px"
                      as={IoCheckmarkOutline}
                      color="verde.main"
                    />
                  </HStack>
                </HStack>
              </VStack>
            </HStack>
            <HStack
              borderRadius="2px"
              border="1px solid"
              borderColor="cinza.main"
              w="20%"
              h="75%"
              alignItems="center"
              justifyContent="center"
              p="4px"
              gap="4px"
            >
              <Box w="8px" h="8px" borderRadius="4px" bgColor="verde.main" />
              <VStack
                flex={1}
                alignSelf="stretch"
                alignItems="stretch"
                justifyContent="center"
                gap="2px"
              >
                <Box h="8px" w="60%" bgColor="cinza.400" />
                <Box h="8px" w="40%" bgColor="cinza.400" />
                <HStack gap="2px" {...highlight(passo, 8)}>
                  <HStack
                    flex={1}
                    h="8px"
                    bgColor="cinza.100"
                    justifyContent="center"
                  >
                    <Icon
                      w="10px"
                      h="10px"
                      as={IoCloudUploadOutline}
                      color="roxo.main"
                    />
                  </HStack>
                </HStack>
              </VStack>
            </HStack>
            <HStack
              borderRadius="2px"
              border="1px solid"
              borderColor="cinza.main"
              w="20%"
              h="75%"
              alignItems="center"
              justifyContent="center"
              p="4px"
              gap="4px"
            >
              <Box w="8px" h="8px" borderRadius="4px" bgColor="verde.main" />
              <VStack
                flex={1}
                alignSelf="stretch"
                alignItems="stretch"
                justifyContent="center"
                gap="2px"
              >
                <Box h="8px" w="80%" bgColor="cinza.400" />
                <Box h="8px" w="60%" bgColor="cinza.400" />
                <Progress
                  isIndeterminate={passo === 9 ? true : false}
                  colorScheme="verde"
                  h="8px"
                  bgColor="cinza.100"
                  {...highlight(passo, 9)}
                  value={passo <= 9 ? 0 : 100}
                />
              </VStack>
            </HStack>
            <HStack
              borderRadius="2px"
              border="1px solid"
              borderColor="cinza.main"
              w="20%"
              h="75%"
              alignItems="center"
              justifyContent="center"
              p="4px"
              gap="4px"
            >
              <Box w="8px" h="8px" borderRadius="4px" bgColor="verde.main" />
              <VStack
                flex={1}
                alignSelf="stretch"
                alignItems="stretch"
                justifyContent="center"
                gap="2px"
              >
                <Box h="8px" w="60%" bgColor="cinza.400" />
                <Box h="8px" w="40%" bgColor="cinza.400" />
                <HStack gap="2px" {...highlight(passo, 12)}>
                  <HStack
                    flex={1}
                    h="8px"
                    bgColor="azul_1.500"
                    justifyContent="center"
                  >
                    <Icon
                      w="10px"
                      h="10px"
                      as={IoCloudDownloadOutline}
                      color="verde.main"
                    />
                  </HStack>
                </HStack>
              </VStack>
            </HStack>
          </HStack>
        </Card>
      </HStack>
      <HStack
        flex={1}
        minH="128px"
        alignItems="stretch"
        gap="4px"
        borderRadius="4px"
        {...highlight(passo, 1)}
      >
        <Card flex={1} p="4px">
          {passo >= 4 && (
            <VStack
              w="100%"
              alignItems="stretch"
              gap={0}
              {...highlight(passo, 4)}
            >
              <VStack alignItems="stretch" gap={0} {...highlight(passo, 5)}>
                {Array(3)
                  .fill(0)
                  .map((_, i) => (
                    <Xml401 key={i + "_4"} status="4" />
                  ))}
              </VStack>
              <VStack
                alignItems="stretch"
                gap={0}
                {...(passo === 6 ? highlight(passo, 6) : highlight(passo, 11))}
              >
                {Array(5)
                  .fill(0)
                  .map((_, i) => (
                    <Xml401 key={i + "_5"} status="5" />
                  ))}
              </VStack>
              <VStack alignItems="stretch" gap={0} {...highlight(passo, 7)}>
                {Array(2)
                  .fill(0)
                  .map((_, i) => (
                    <Xml401 key={i + "_D"} status="D" />
                  ))}
              </VStack>
            </VStack>
          )}
        </Card>
        <Card flex={1} p="4px">
          {passo >= 10 && (
            <VStack
              w="100%"
              alignItems="stretch"
              gap={0}
              {...highlight(passo, 10)}
            >
              <VStack alignItems="stretch" gap={0}>
                {Array(3)
                  .fill(0)
                  .map((_, i) => (
                    <Xml401 key={i + "_4"} status="4" />
                  ))}
              </VStack>
              <VStack alignItems="stretch" gap={0} {...highlight(passo, 11)}>
                {Array(7)
                  .fill(0)
                  .map((_, i) => (
                    <Xml401 key={i + "_5"} status="4" />
                  ))}
              </VStack>
              <VStack alignItems="stretch" gap={0}>
                {Array(2)
                  .fill(0)
                  .map((_, i) => (
                    <Xml401 key={i + "_D"} status="D" />
                  ))}
              </VStack>
            </VStack>
          )}
        </Card>
      </HStack>
    </VStack>
  );
}
