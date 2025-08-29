"use client";

import Hint from "@/app/_components/texto/Hint";
import { useAsync, useColors, useHTTP, useUser } from "@/lib/hooks";
import { CheckIcon, ExternalLinkIcon, RepeatIcon } from "@chakra-ui/icons";
import {
  Box,
  Button,
  Card,
  CardBody,
  CardFooter,
  Divider,
  HStack,
  Skeleton,
  Text,
  VStack,
  keyframes,
} from "@chakra-ui/react";
import Device, { DeviceLoading } from "./Device";
import { User } from "@/lib/types/api/iv/auth";

const frames = keyframes`
    0% { transform: rotate(0turn); }
    100% { transform: rotate(1turn); }
`;

const animation = `${frames} 1s linear infinite`;

export default function AccountTab() {
  const { user, setUser } = useUser();
  const { hover } = useColors();
  const [loadingProfile, loadProfile] = useAsync();
  const httpClient = useHTTP({ withCredentials: true });

  const reloadProfile = () =>
    loadProfile(async () => {
      const response = await httpClient.fetch("/auth/eu");
      if (!response.ok) return;

      const usr = (await response.json()) as User;
      setUser(usr);
    });

  return (
    <>
      <Box
        height="0px"
        display="flex"
        flexDirection="row"
        justifyContent="flex-end"
      >
        <Box
          borderRadius="50%"
          height="24px"
          width="24px"
          display="flex"
          flexDirection="row"
          justifyContent="center"
          alignItems="center"
          cursor={loadingProfile ? "not-allowed" : "pointer"}
          _hover={
            loadingProfile ? {} : { backgroundColor: hover, color: "verde.800" }
          }
          color={loadingProfile ? "verde.main" : "cinza.700"}
          animation={loadingProfile ? animation : "none"}
          boxShadow={loadingProfile ? "none" : "md"}
          onClick={loadingProfile ? undefined : reloadProfile}
        >
          <RepeatIcon width="80%" height="80%" />
        </Box>
      </Box>
      <Box mt="16px">
        <Hint>Informações pessoais</Hint>
        <Card variant="outline">
          <CardBody pt="12px">
            <Hint> Nome </Hint>
            {loadingProfile ? (
              <Skeleton width="120px" height="20px" mt="2px" mb="2px" />
            ) : (
              <Text>{user?.nome}</Text>
            )}
            <Hint> E-mail </Hint>
            {loadingProfile ? (
              <Skeleton width="200px" height="20px" mt="2px" mb="2px" />
            ) : (
              <Text>{user?.email}</Text>
            )}
          </CardBody>
        </Card>
        <Box>
          <Hint> Permissões </Hint>
          <Card variant="outline">
            <CardBody>
              <VStack align="flex-start" divider={<Divider />}>
                {loadingProfile
                  ? [
                      <HStack>
                        <Skeleton
                          width="20px"
                          height="20px"
                          mt="2px"
                          mb="2px"
                        />
                        <Skeleton
                          width="200px"
                          height="20px"
                          mt="2px"
                          mb="2px"
                        />
                      </HStack>,
                      <HStack>
                        <Skeleton
                          width="20px"
                          height="20px"
                          mt="2px"
                          mb="2px"
                        />
                        <Skeleton
                          width="200px"
                          height="20px"
                          mt="2px"
                          mb="2px"
                        />
                      </HStack>,
                    ]
                  : user?.roles.map((p) => (
                      <HStack key={p.id + "p"}>
                        <CheckIcon color="verde.main" />
                        <Text fontSize="sm" key={p.id}>
                          {p.nome}
                        </Text>
                      </HStack>
                    ))}
              </VStack>
            </CardBody>
          </Card>
        </Box>
        <Box>
          <Hint> Sessões ativas </Hint>
          <Card variant="outline" overflow="hidden">
            <CardBody maxHeight="30vh" overflowY="auto">
              <VStack align="flex-start" divider={<Divider />}>
                {loadingProfile
                  ? [<DeviceLoading />, <DeviceLoading />]
                  : user?.devices
                      .sort(
                        (d1, d2) =>
                          Number(new Date(d2.last_active)) -
                          Number(new Date(d1.last_active)),
                      )
                      .map((d) => <Device key={d.id + "dev"} device={d} />)}
              </VStack>
            </CardBody>
            <CardFooter padding="0" overflow="hidden">
              <Button
                width="100%"
                variant="ghost"
                color="rosa.main"
                onClick={() => alert("#TODO desconectar sessões")}
                leftIcon={<ExternalLinkIcon boxSize="24px" />}
              >
                Desconectar todos os dispositivos
              </Button>
            </CardFooter>
          </Card>
        </Box>
      </Box>
    </>
  );
}
