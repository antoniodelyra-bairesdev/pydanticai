"use client";

import { useAsync, useHTTP, useUser, useWebSockets } from "@/lib/hooks";
import {
  ListedUser,
  WSChatMessageTo,
  WSConnectionMessage,
  WSMessage,
  WSMessageType,
} from "@/lib/types/api/iv/websockets";
import {
  Box,
  Button,
  Card,
  CardBody,
  HStack,
  Heading,
  Input,
  StackDivider,
  Text,
  VStack,
} from "@chakra-ui/react";
import {
  KeyboardEventHandler,
  MouseEventHandler,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

export default function Usuarios() {
  const [usuarios, _setUsuarios] = useState<ListedUser[]>([]);
  const usuariosRef = useRef<ListedUser[]>(usuarios);

  const setUsuarios = (users: ListedUser[]) => {
    usuariosRef.current = users;
    _setUsuarios(users);
  };

  const { user } = useUser();

  const [_, load] = useAsync();
  const httpClient = useHTTP({ withCredentials: true });

  const { connection } = useWebSockets();

  const sendMessage = (to_user_id: string, message: string) => {
    if (!user) return;
    const type = WSMessageType.CHAT;
    const content: WSChatMessageTo = { to_user_id, message };
    const msg: WSMessage = { type, content };
    connection?.send(JSON.stringify(msg));
  };

  useEffect(() => {
    load(async () => {
      const response = await httpClient.fetch("ws/users");
      if (!response.ok) return;
      setUsuarios((await response.json()) as ListedUser[]);
    });
  }, []);

  const onMessage = useCallback(
    (ev: MessageEvent) => {
      const data: WSMessage = JSON.parse(ev.data);
      const usuarios = usuariosRef.current;
      if (data.type === WSMessageType.CONNECTION) {
        const connectionMsg = data.content as WSConnectionMessage;
        const userIndex = usuarios.findIndex(
          (u) => u.id == connectionMsg.user.id,
        );
        if (userIndex === -1) return;
        usuarios[userIndex].conectado = connectionMsg.online;
        setUsuarios([...usuarios]);
      }
    },
    [connection],
  );

  const inputs = useRef<Record<number, HTMLInputElement | null>>({});

  const makeClickSendCallback =
    (user_id: number): MouseEventHandler<HTMLButtonElement> =>
    () => {
      const input = inputs.current[user_id];
      if (!input) return;
      const msg = input.value;
      sendMessage(String(user_id), msg);
      input.value = "";
    };

  const makeEnterSendCallback =
    (user_id: number): KeyboardEventHandler<HTMLInputElement> =>
    (ev) => {
      if (ev.key !== "Enter") return;
      const input = ev.target as HTMLInputElement;
      const msg = input.value;
      sendMessage(String(user_id), msg);
      input.value = "";
    };

  useEffect(() => {
    connection?.addEventListener("message", onMessage);

    return () => {
      connection?.removeEventListener("message", onMessage);
    };
  }, [connection]);

  return (
    <VStack alignItems="stretch" p="32px" pt="16px" overflow="auto">
      {usuarios.map((user) => (
        <Card key={user.id} variant="outline">
          <CardBody p={0} overflow="auto">
            <HStack w="100%" divider={<StackDivider />}>
              <Box
                ml="8px"
                minW="24px"
                minH="24px"
                borderRadius="full"
                bgColor={user.conectado ? "verde.main" : "cinza.main"}
              />
              <VStack p="12px" flex="1" alignItems="flex-start" gap={0}>
                <Text>{user.nome}</Text>
                <Text color="cinza.500" fontSize="sm" wordBreak="break-all">
                  {user.email}
                </Text>
              </VStack>
              <HStack p="12px" flex="1" minW="144px">
                <Input
                  size="sm"
                  ref={(input) => (inputs.current[user.id] = input)}
                  isDisabled={!user.conectado}
                  type="text"
                  onKeyDown={makeEnterSendCallback(user.id)}
                />
                <Button
                  size="sm"
                  colorScheme="azul_1"
                  isDisabled={!user.conectado}
                  onClick={makeClickSendCallback(user.id)}
                >
                  Enviar
                </Button>
              </HStack>
            </HStack>
          </CardBody>
        </Card>
      ))}
    </VStack>
  );
}
