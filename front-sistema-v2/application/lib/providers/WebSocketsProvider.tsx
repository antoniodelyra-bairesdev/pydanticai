"use client";

import {
  HStack,
  Icon,
  Text,
  ToastId,
  ToastProps,
  VStack,
  useToast,
} from "@chakra-ui/react";
import React, { createContext, useEffect, useRef, useState } from "react";
import { IoMail, IoNotifications } from "react-icons/io5";
import { useUser } from "../hooks";
import {
  WSChatMessageFrom,
  WSMessage,
  WSMessageType,
  WSNotification,
} from "../types/api/iv/websockets";
import { dateToStr, fmtDate } from "../util/string";
import Link from "next/link";

export const WebSocketsContext = createContext<{
  connection?: WebSocket;
  connect: () => void;
  disconnect: () => void;
}>({
  connect() {},
  disconnect() {},
});

const TIMEOUT_PROGRESSION = [5, 5, 10, 15, 30];
const basicToastConfig: (id: string) => ToastProps = (id: string) => ({
  colorScheme: "rosa",
  title: `(${id}) Atualizações em tempo real:`,
  description: (
    <>
      <Text fontSize="xs">Desconectado do serviço de mensagens!</Text>
      <Text fontSize="xs" fontWeight="bold">
        Tentando reconectar...
      </Text>
    </>
  ),
  duration: null,
  isClosable: false,
  position: "bottom-right",
});

export function WebSocketsProvider({
  children,
  identificador,
  url,
}: {
  children: React.ReactNode;
  identificador: string;
  url?: string;
}) {
  const [_, token] =
    document.cookie
      .split(";")
      .map((c) => c.trim().split("="))
      .find(([name]) => name === "user_token") ?? [];

  const wsUrl = url + "/connect?token=" + (token ?? "");

  const [connection, setConnection] = useState<WebSocket | undefined>();

  const toast = useToast();
  const disconnectedToastRef = useRef<ToastId>();
  const timeoutRef = useRef<number>(-1);
  const retryTimeLeftRef = useRef<number>(0);
  const timeoutProgressionIndexRef = useRef<number>(0);
  const retryRef = useRef(true);
  const isReloadingRef = useRef(false);

  const { setUser } = useUser();

  useEffect(() => {
    window.addEventListener("beforeunload", () => {
      isReloadingRef.current = true;
    });
  }, []);

  const _disconnect = () => {
    console.log("Desconectando do serviço de notificações...");

    let ws: WebSocket | undefined =
      connection ?? (window as any)[`ws-${identificador}`];
    if (!ws) return;

    ws.close();
    setConnection(undefined);
    (window as any)[`ws-${identificador}`] = undefined;
  };

  const retry = () => {
    if (isReloadingRef.current) return;
    if (disconnectedToastRef.current === undefined) {
      disconnectedToastRef.current = toast({
        ...basicToastConfig(identificador),
      });
    }
    if (timeoutRef.current === -1) {
      retryTimeLeftRef.current =
        TIMEOUT_PROGRESSION[timeoutProgressionIndexRef.current];
      const timeout = () => {
        if (!disconnectedToastRef.current) return;
        toast.update(disconnectedToastRef.current, {
          ...basicToastConfig(identificador),
          description: (
            <>
              <Text fontSize="xs">Desconectado do serviço de mensagens!</Text>
              <Text fontSize="xs" fontWeight="bold">
                Nova tentativa de conexão em {retryTimeLeftRef.current--}s...
              </Text>
            </>
          ),
        });
        if (retryTimeLeftRef.current <= 0) {
          timeoutProgressionIndexRef.current = Math.min(
            timeoutProgressionIndexRef.current + 1,
            TIMEOUT_PROGRESSION.length - 1,
          );
          retryTimeLeftRef.current =
            TIMEOUT_PROGRESSION[timeoutProgressionIndexRef.current];
          if (timeoutRef.current !== -1)
            window.clearTimeout(timeoutRef.current);
          timeoutRef.current = -1;
          toast.update(disconnectedToastRef.current, {
            ...basicToastConfig(identificador),
          });
          _disconnect();
          requestAnimationFrame(_connect);
          return;
        }
        timeoutRef.current = window.setTimeout(timeout, 1000);
      };
      timeout();
    }
  };

  const _connect = () => {
    console.log("Conectando ao serviço de notificações...");

    let ws: WebSocket | undefined =
      connection ?? (window as any)[`ws-${identificador}`];
    if (ws) return;

    ws = new WebSocket(wsUrl);
    ws.onopen = () => {
      if (timeoutRef.current !== -1) {
        window.clearInterval(timeoutRef.current);
        timeoutRef.current = -1;
      }
      if (retryTimeLeftRef.current > 0) retryTimeLeftRef.current = 0;
      if (timeoutProgressionIndexRef.current > 0)
        timeoutProgressionIndexRef.current = 0;
      if (disconnectedToastRef.current === undefined) return;
      toast.update(disconnectedToastRef.current, {
        ...basicToastConfig(identificador),
        colorScheme: "verde",
        description: (
          <Text fontSize="xs" fontWeight="bold">
            Reconectado ao serviço de mensagens em tempo real!
          </Text>
        ),
        duration: 2000,
        isClosable: true,
        onCloseComplete() {
          disconnectedToastRef.current = undefined;
        },
      });
    };
    ws.onclose = (ev) => {
      if (ev.reason === "Unauthorized") {
        setUser(null);
        if (disconnectedToastRef.current !== undefined) {
          toast.close(disconnectedToastRef.current);
          disconnectedToastRef.current = undefined;
        }
        return;
      }
      if (retryRef.current) {
        retry();
      }
    };
    ws.onerror = () => {
      ws?.close();
    };
    ws.onmessage = (ev) => {
      const data = JSON.parse(ev.data) as WSMessage;
      if (data.type === WSMessageType.CONNECTION) return;
      if (data.type === WSMessageType.NOTIFICATION) {
        const content = data.content as WSNotification;
        const txt = (
          <Text fontSize="xs" lineHeight={1.1}>
            {content.text}
          </Text>
        );
        toast({
          colorScheme: "azul_2",
          title: "Notificação",
          description: content.link ? (
            <Link href={content.link}>{txt}</Link>
          ) : (
            txt
          ),
          position: "bottom-right",
          icon: <Icon as={IoNotifications} verticalAlign="bottom" />,
          isClosable: true,
          duration: null,
        });
        return;
      }
      if (data.type === WSMessageType.CHAT) {
        const content = data.content as WSChatMessageFrom;
        const now = new Date();
        toast({
          colorScheme: "azul_1",
          title: content.from_user.nome,
          description: (
            <VStack w="100%" alignItems="stretch" gap="4px">
              <Text>{content.message}</Text>
              <HStack justifyContent="space-between">
                <Text fontSize="xs">{fmtDate(dateToStr(now))}</Text>
                <Text fontSize="xs">
                  {String(now.getHours()).padStart(2, "0")}:
                  {String(now.getMinutes()).padStart(2, "0")}:
                  {String(now.getSeconds()).padStart(2, "0")}
                </Text>
              </HStack>
            </VStack>
          ),
          position: "bottom-right",
          icon: <Icon as={IoMail} verticalAlign="bottom" />,
          isClosable: true,
          duration: null,
        });
        return;
      }
    };

    (window as any)[`ws-${identificador}`] = ws;
    setConnection(ws);
  };

  const { user } = useUser();

  const connect = () => {
    retryRef.current = true;
    _connect();
  };

  const disconnect = () => {
    retryRef.current = false;
    _disconnect();
  };

  useEffect(() => {
    if (user && !connection) {
      connect();
    } else if (!user && connection) {
      disconnect();
    }
  }, [user, connection]);

  return (
    <WebSocketsContext.Provider value={{ connection, connect, disconnect }}>
      {children}
    </WebSocketsContext.Provider>
  );
}
