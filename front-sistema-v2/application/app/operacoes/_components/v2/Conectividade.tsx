import { useHTTP } from "@/lib/hooks";
import {
  Button,
  HStack,
  Icon,
  Tag,
  Text,
  Tooltip,
  VStack,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { IoEllipse, IoReload } from "react-icons/io5";

const getColor = (bools: (boolean | undefined)[]) => {
  let allTrue = true;
  let allFalse = true;
  let allUndefined = true;
  for (const boolOrUndefined of bools) {
    if (typeof boolOrUndefined === "undefined") {
      allTrue = false;
      allFalse = false;
      continue;
    }
    if (boolOrUndefined) {
      allUndefined = false;
      allFalse = false;
    } else {
      allUndefined = false;
      allTrue = false;
    }
  }
  if (allUndefined) return "cinza";
  if (allTrue) return "verde";
  if (allFalse) return "rosa";
  return "amarelo";
};

export type B3ReachabilityType = {
  reachable: boolean | undefined;
  session: boolean | undefined;
};

export type B3ConnectivityType = {
  ORDER_ENTRY: B3ReachabilityType;
  POST_TRADE: B3ReachabilityType;
};

const defaultReachability = () =>
  ({
    ORDER_ENTRY: {
      reachable: undefined,
      session: undefined,
    },
    POST_TRADE: {
      reachable: undefined,
      session: undefined,
    },
  }) as B3ConnectivityType;

export default function Conectividade() {
  const [b3, setB3Conn] = useState<B3ConnectivityType>(defaultReachability());

  const httpClient = useHTTP({ withCredentials: true });

  const b3Reload = async () => {
    setB3Conn(defaultReachability());
    const response = await httpClient.fetch("/v1/b3/connected", {
      hideToast: { success: true, clientError: true },
    });
    if (!response.ok) return;
    setB3Conn(await response.json());
  };

  const reload = () => {
    b3Reload();
  };

  useEffect(() => reload(), []);

  return (
    <HStack
      alignItems="center"
      p="3px 12px"
      h="30px"
      bgColor="cinza.200"
      zIndex={99}
    >
      <Button size="xs" leftIcon={<Icon as={IoReload} />} onClick={reload}>
        Conectividade
      </Button>
      {/* <Tooltip
            m={0}
            bgColor='cinza.200'
            p='4px'
            borderRadius='8px'
            hasArrow
            label={<VStack alignItems='stretch' gap='4px'>
                <Tag fontSize='xs' colorScheme='verde'>
                    <Text><Icon pt='2px' as={IoEllipse} /> Serviço de Autenticação</Text>
                </Tag>
                <Tag fontSize='xs' colorScheme='verde'>
                    <Text><Icon pt='2px' as={IoEllipse} /> API Principal</Text>
                </Tag>
                <Tag fontSize='xs' colorScheme='verde'>
                    <Text><Icon pt='2px' as={IoEllipse} /> Atualizações em tempo real</Text>
                </Tag>
            </VStack>}
        >
            <Tag cursor='pointer' fontSize='xs' colorScheme='verde'>
                <Text><Icon pt='2px' as={IoEllipse} /> Sistema Vanguarda</Text>
            </Tag>
        </Tooltip>
        <Tooltip
            m={0}
            bgColor='cinza.200'
            p='4px'
            borderRadius='8px'
            hasArrow
            label={<VStack alignItems='stretch' gap='4px'>
                <Tag fontSize='xs' colorScheme='verde'>
                    <Text><Icon pt='2px' as={IoEllipse} /> Bradesco (SFTP)</Text>
                </Tag>
                <Tag fontSize='xs' colorScheme='rosa'>
                    <Text><Icon pt='2px' as={IoEllipse} /> BTG (API)</Text>
                </Tag>
                <Tag fontSize='xs' colorScheme='rosa'>
                    <Text><Icon pt='2px' as={IoEllipse} /> Daycoval (API)</Text>
                </Tag>
                <Tag fontSize='xs' colorScheme='rosa'>
                    <Text><Icon pt='2px' as={IoEllipse} /> Itaú (API)</Text>
                </Tag>
            </VStack>}
        >
            <Tag cursor='pointer' fontSize='xs' colorScheme='amarelo'>
                <Text><Icon pt='2px' as={IoEllipse} /> Administradores</Text>
            </Tag>
        </Tooltip> */}
      <Tooltip
        m={0}
        bgColor="cinza.200"
        p="4px"
        borderRadius="8px"
        hasArrow
        label={
          <VStack alignItems="stretch" gap="4px">
            <HStack gap="4px">
              <Text flex={1} color="black" fontSize="xs">
                Order Entry:
              </Text>
              <Tag
                fontSize="xs"
                colorScheme={getColor([b3.ORDER_ENTRY.reachable])}
              >
                <Text>
                  <Icon pt="2px" as={IoEllipse} /> Mensageria
                </Text>
              </Tag>
              <Tag
                fontSize="xs"
                colorScheme={getColor([b3.ORDER_ENTRY.session])}
              >
                <Text>
                  <Icon pt="2px" as={IoEllipse} /> Sessão FIX
                </Text>
              </Tag>
            </HStack>
            <HStack gap="4px">
              <Text flex={1} color="black" fontSize="xs">
                Post Trade:
              </Text>
              <Tag
                fontSize="xs"
                colorScheme={getColor([b3.POST_TRADE.reachable])}
              >
                <Text>
                  <Icon pt="2px" as={IoEllipse} /> Mensageria
                </Text>
              </Tag>
              <Tag
                fontSize="xs"
                colorScheme={getColor([b3.POST_TRADE.session])}
              >
                <Text>
                  <Icon pt="2px" as={IoEllipse} /> Sessão FIX
                </Text>
              </Tag>
            </HStack>
          </VStack>
        }
      >
        <Tag
          cursor="pointer"
          fontSize="xs"
          colorScheme={getColor([
            b3.ORDER_ENTRY.reachable,
            b3.ORDER_ENTRY.session,
            b3.POST_TRADE.reachable,
            b3.POST_TRADE.session,
          ])}
        >
          <Text>
            <Icon pt="2px" as={IoEllipse} /> Sistemas [B]³
          </Text>
        </Tag>
      </Tooltip>
    </HStack>
  );
}
