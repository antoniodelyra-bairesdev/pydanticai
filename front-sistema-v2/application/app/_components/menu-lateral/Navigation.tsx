"use client";

import {
  Avatar,
  AvatarBadge,
  Box,
  Divider,
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerHeader,
  DrawerOverlay,
  Flex,
  HStack,
  Heading,
  Icon,
  Spacer,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import { usePathname } from "next/navigation";
import { ReactNode, useEffect, useRef, useState } from "react";

import IVLogo from "@/app/_components/images/IVLogo";
import { useSettings } from "@/lib/hooks";
import { printLogo } from "@/lib/util/misc";
import { Metadata } from "next";

import { authPathsMetadata } from "../../path.metadata";
import NavigationActions from "./NavigationActions";
import NavigationLink from "./NavigationLink";
import NavigationOpenZone from "./NavigationOpenZone";
import { IoChatbox, IoNotifications } from "react-icons/io5";
import Link from "next/link";

export type NavigationProps = { children: ReactNode };

const showRoutes = [
  "/",
  "/ferramentas",
  "/dashboard",
  "/liberacao-cotas",
  "/enquadramento",
  "/operacoes",
  "/locacoes",
  "/fundos",
  "/site-institucional",
];

export default function Navigation({ children }: NavigationProps) {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { closeDrawerOnLeave, closeDrawerOnLinkClick } = useSettings().settings;

  const pathname = usePathname();

  const firstFragment = (path: string) => "/" + path.split("/")[1];
  const getPageName = () =>
    String(
      (authPathsMetadata as Record<string, Metadata>)[firstFragment(pathname)]
        ?.title ?? "",
    );

  const links = showRoutes
    .filter((path) => Object.keys(authPathsMetadata).includes(path))
    .map((path) => ({
      path,
      title: (authPathsMetadata as Record<string, Metadata>)[path].title,
    }));

  const onLinkClick = () => {
    if (closeDrawerOnLinkClick) onClose();
  };

  useEffect(() => {
    printLogo();
  }, []);

  const [messages] = useState(0);
  const [notifications] = useState(0);

  return (
    <VStack
      minH="100vh"
      maxW="100vw"
      alignItems="stretch"
      justifyContent="stretch"
      gap={0}
    >
      {pathname.startsWith("/login") || (
        <>
          <NavigationOpenZone onOpen={onOpen} />
          <Drawer
            autoFocus={false}
            isOpen={isOpen}
            onClose={onClose}
            placement="left"
          >
            <DrawerOverlay />
            <DrawerContent
              onMouseLeave={closeDrawerOnLeave ? onClose : undefined}
            >
              {closeDrawerOnLeave || <DrawerCloseButton />}
              <DrawerHeader>
                <IVLogo />
              </DrawerHeader>
              <DrawerBody p={0}>
                <Flex direction="column" h="100%">
                  <HStack justifyContent="center" pb="12px">
                    <Link href="/mensagens">
                      <Avatar icon={<Icon as={IoChatbox} />} bg="azul_2.main">
                        {messages > 0 && (
                          <AvatarBadge
                            boxSize="28px"
                            fontWeight="bold"
                            bg="verde.main"
                            fontSize="xs"
                          >
                            {messages > 99 ? "99+" : messages}
                          </AvatarBadge>
                        )}
                      </Avatar>
                    </Link>
                    <Box w="24px" />
                    <Link href="/notificacoes">
                      <Avatar
                        icon={<Icon as={IoNotifications} />}
                        bg="azul_4.main"
                      >
                        {notifications > 0 && (
                          <AvatarBadge
                            boxSize="28px"
                            fontWeight="bold"
                            bg="verde.main"
                            fontSize="xs"
                          >
                            {notifications > 99 ? "99+" : notifications}
                          </AvatarBadge>
                        )}
                      </Avatar>
                    </Link>
                  </HStack>
                  <Flex direction="column">
                    {links.map(({ path, title }) => (
                      <Box key={path}>
                        <NavigationLink
                          onClick={onLinkClick}
                          href={path}
                          text={String(title)}
                        />
                        <Divider />
                      </Box>
                    ))}
                  </Flex>
                  <Spacer />
                  <NavigationActions />
                </Flex>
              </DrawerBody>
            </DrawerContent>
          </Drawer>
        </>
      )}
      {!pathname.startsWith("/login") && (
        <HStack
          alignItems="center"
          justifyContent="space-between"
          bgColor="azul_1.main"
          key="heading"
          h="56px"
          w="100%"
          overflow="hidden"
        >
          <HStack>
            <Link href="/">
              <Box w="280px" pb="8px" onClick={() => (window as any).fix?.()}>
                <IVLogo forceColorMode="dark" />
              </Box>
            </Link>
            <Heading color="white" size="sm" ml="16px">
              {getPageName()}
            </Heading>
          </HStack>
          <HStack w="40%" h="56px" mr="-40px" gap={0} overflow="hidden">
            <Box w="25%"></Box>
            <Box
              bgColor="azul_2.main"
              w="27.5%"
              h="1000px"
              transform="rotate(45deg)"
            />
            <Box
              bgColor="azul_3.main"
              w="27.5%"
              h="1000px"
              transform="rotate(45deg)"
            />
            <Box
              bgColor="azul_4.main"
              w="22%"
              h="1000px"
              transform="rotate(45deg)"
            />
          </HStack>
        </HStack>
      )}
      <Box h="calc(100vh - 56px)" key="content" overflow="auto">
        {children}
      </Box>
    </VStack>
  );
}
