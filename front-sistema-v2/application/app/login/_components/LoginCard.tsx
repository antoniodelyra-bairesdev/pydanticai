"use client";

import {
  Box,
  Button,
  Card,
  CardBody,
  Heading,
  Stack,
  Text,
} from "@chakra-ui/react";
import { Formik } from "formik";
import { useState } from "react";

import FormField from "@/app/_components/forms/FormField";
import TextInput from "@/app/_components/forms/TextInput";
import IVLogo from "@/app/_components/images/IVLogo";
import {
  useColors,
  useHTTP,
  useAsync,
  useSettings,
  useUser,
} from "@/lib/hooks";
import { User } from "@/lib/types/api/iv/auth";
import { fieldValidators, required } from "@/lib/util/validation";
import { useRouter } from "next/navigation";

const maxCookieExpiryInDays = 400;
const dayInMs = 1000 * 60 * 60 * 24;

export default function LoginCard() {
  const initialValues = {
    email: "",
    password: "",
  };

  const [loading, load] = useAsync();
  const httpClient = useHTTP();
  const [error, setError] = useState("");

  const { heading } = useColors();
  const { setUser } = useUser();
  const { loadSettings } = useSettings();
  const router = useRouter();

  const send = ({ email, password }: typeof initialValues) => {
    load(async () => {
      const request = JSON.stringify({ email, password });
      const response = await httpClient.fetch("/auth/login", {
        method: "POST",
        body: request,
      });
      if (!response.ok) {
        const error = (await response.json()) as {
          detail: string | { message: string };
        };
        return setError(
          typeof error.detail === "string"
            ? error.detail
            : error.detail.message,
        );
      }
      const { user, token } = (await response.json()) as {
        user: User;
        token: string;
      };

      setUser(user);
      loadSettings(user);
      const maxCookieExpiryDate = new Date(
        Date.now() + maxCookieExpiryInDays * dayInMs,
      );
      document.cookie = `user_token=${token}; SameSite=Lax; Path=/; Expires=${maxCookieExpiryDate.toUTCString()}`;
      router.replace("/");
    });
  };

  return (
    <Card
      direction={{ base: "column", md: "row" }}
      maxW="600px"
      padding="12px"
      margin={{ base: "8px", sm: "48px" }}
    >
      <Box
        flex={2}
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
      >
        <IVLogo variant="vertical" />
      </Box>
      <Box flex={3}>
        <Formik
          initialValues={initialValues}
          validate={fieldValidators({
            email: [required],
            password: [required],
          })}
          onSubmit={send}
        >
          {(form) => (
            <form onSubmit={form.handleSubmit}>
              <Stack>
                <CardBody>
                  <Heading
                    data-test-id="login-heading"
                    size="md"
                    color={heading}
                    paddingBottom="24px"
                  >
                    Acessar sistema
                  </Heading>
                  <FormField form={form} field="email" label="E-mail">
                    <TextInput
                      type="email"
                      placeholder="email@icatuvanguarda.com.br"
                    />
                  </FormField>
                  <FormField form={form} field="password" label="Senha">
                    <TextInput type="password" placeholder="••••••••" />
                  </FormField>
                  <Text fontSize="xs" color="rosa.main">
                    {error}
                  </Text>
                  <Button
                    isDisabled={!form.isValid}
                    isLoading={loading}
                    colorScheme="azul_1"
                    type="submit"
                    width="100%"
                    size="lg"
                    marginTop="24px"
                    marginBottom="24px"
                  >
                    Entrar
                  </Button>
                </CardBody>
              </Stack>
            </form>
          )}
        </Formik>
      </Box>
    </Card>
  );
}
