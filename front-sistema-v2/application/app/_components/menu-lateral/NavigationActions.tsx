"use client";

import Hint from "@/app/_components/texto/Hint";
import { useAsync, useColors, useHTTP, useUser } from "@/lib/hooks";
import {
  ChevronUpIcon,
  ExternalLinkIcon,
  SettingsIcon,
} from "@chakra-ui/icons";
import {
  Box,
  Button,
  Card,
  CardBody,
  HStack,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Popover,
  PopoverArrow,
  PopoverContent,
  PopoverTrigger,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import { useRouter } from "next/navigation";
import Settings from "./preferencias/Settings";

export default function NavigationActions() {
  const [loading, load] = useAsync();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const router = useRouter();
  const { user, setUser } = useUser();
  const { hover } = useColors();
  const httpClient = useHTTP({ withCredentials: true });

  const sair = () =>
    load(async () => {
      const response = await httpClient.fetch("/auth/logout", {
        method: "DELETE",
      });
      if (response.ok) {
        setUser(null);
      }
    });

  return (
    <>
      <Popover>
        <PopoverTrigger>
          <Card
            cursor="pointer"
            variant="elevated"
            _hover={{ backgroundColor: hover }}
            margin="8px"
          >
            <CardBody p="8px">
              <HStack>
                <ChevronUpIcon m="8px" color="cinza.500" boxSize="24px" />
                <Box>
                  <Hint>Usuário:</Hint>
                  <Text fontSize="md" data-test-id="side-menu-user-name">
                    {user?.nome}
                  </Text>
                </Box>
              </HStack>
            </CardBody>
          </Card>
        </PopoverTrigger>
        <PopoverContent minW={{ base: "30%", lg: "max-content" }} p="8px">
          <PopoverArrow />
          <VStack alignItems="stretch">
            <Button
              onClick={onOpen}
              variant="ghost"
              leftIcon={<SettingsIcon boxSize="24px" />}
              colorScheme="azul_1"
            >
              Preferências
            </Button>
            <Button
              isLoading={loading}
              colorScheme="rosa"
              onClick={sair}
              leftIcon={<ExternalLinkIcon boxSize="24px" />}
            >
              Sair
            </Button>
          </VStack>
        </PopoverContent>
      </Popover>
      <Modal
        size="4xl"
        isOpen={isOpen}
        onClose={onClose}
        scrollBehavior="inside"
      >
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Preferências</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Settings />
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
}
