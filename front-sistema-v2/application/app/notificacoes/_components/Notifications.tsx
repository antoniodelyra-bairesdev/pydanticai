"use client";

import { useHTTP, useWebSockets } from "@/lib/hooks";
import { Notification } from "@/lib/types/api/iv/sistema";
import {
  WSMessage,
  WSMessageType,
  WSNotification,
} from "@/lib/types/api/iv/websockets";
import { fmtDatetime } from "@/lib/util/string";
import {
  Box,
  Button,
  Card,
  CardBody,
  CardFooter,
  Icon,
  Text,
  VStack,
} from "@chakra-ui/react";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { IoLinkOutline } from "react-icons/io5";

export default function Notifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const notificationsRef = useRef<Notification[]>([]);

  const httpClient = useHTTP({ withCredentials: true });

  const { connection } = useWebSockets();

  const onMessage = useCallback(
    (ev: MessageEvent) => {
      const data: WSMessage = JSON.parse(ev.data);
      if (data.type === WSMessageType.NOTIFICATION) {
        const notification = data.content as WSNotification;
        notificationsRef.current.unshift({
          id: Math.random(),
          created_at: new Date().toISOString(),
          link: notification.link,
          text: notification.text,
        });
        setNotifications([...notificationsRef.current]);
      }
    },
    [connection, notifications],
  );

  useEffect(() => {
    connection?.addEventListener("message", onMessage);
    return () => {
      connection?.removeEventListener("message", onMessage);
    };
  }, [connection]);

  useEffect(() => {
    (async () => {
      const response = await httpClient.fetch("/sistema/notificacoes", {
        hideToast: { success: true },
      });
      if (!response.ok) return;
      notificationsRef.current = await response.json();
      setNotifications([...notificationsRef.current]);
    })();
  }, []);

  return (
    <VStack w="512px" alignItems="stretch" p="24px">
      {notifications.map((n) => (
        <Card key={n.id} overflow="hidden">
          <Box
            borderLeft="8px solid"
            borderColor="azul_1.main"
            w="100%"
            h="100%"
          >
            <CardBody p="12px">
              <VStack alignItems="flex-start" fontSize="sm">
                <Text>{n.text}</Text>
                {n.link && (
                  <Link href={n.link}>
                    <Button
                      size="xs"
                      colorScheme="azul_2"
                      leftIcon={<Icon as={IoLinkOutline} />}
                    >
                      Acessar
                    </Button>
                  </Link>
                )}
              </VStack>
            </CardBody>
            <CardFooter p="12px">
              <Text fontSize="xs">{fmtDatetime(n.created_at)}</Text>
            </CardFooter>
          </Box>
        </Card>
      ))}
    </VStack>
  );
}
