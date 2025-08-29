import FormField from "@/app/_components/forms/FormField";
import TextInput from "@/app/_components/forms/TextInput";
import Hint from "@/app/_components/texto/Hint";
import { useAsync, useHTTP } from "@/lib/hooks";
import {
  fieldValidators,
  makeInitialValues,
  password,
  required,
  sameAs,
} from "@/lib/util/validation";
import { LockIcon, RepeatClockIcon } from "@chakra-ui/icons";
import { Button, Card, CardBody, Text, VStack } from "@chakra-ui/react";
import { Formik, FormikHelpers } from "formik";
import { useState } from "react";

export default function ResetPasswordTab() {
  const [error, setError] = useState("");

  const initialValues = makeInitialValues(
    "oldPassword",
    "newPassword",
    "confirmNewPassword",
  );

  const [loading, load] = useAsync();

  const httpClient = useHTTP({ withCredentials: true });

  const submit = (
    {
      newPassword: senha_nova,
      oldPassword: senha_antiga,
    }: typeof initialValues,
    form: FormikHelpers<typeof initialValues>,
  ) =>
    load(async () => {
      const body = JSON.stringify({ senha_antiga, senha_nova });
      const response = await httpClient.fetch("auth/redefinir-senha", {
        method: "PATCH",
        body,
      });
      if (response.ok) {
        form.resetForm();
      }
    });

  return (
    <>
      <Formik
        initialValues={initialValues}
        validate={fieldValidators<typeof initialValues>({
          oldPassword: [required],
          newPassword: [required, password],
          confirmNewPassword: [
            required,
            sameAs(
              "newPassword",
              "A confirmação não coincide com a nova senha",
            ),
          ],
        })}
        onSubmit={submit}
      >
        {(form) => (
          <form onSubmit={form.handleSubmit}>
            <VStack align="flex-start">
              <Card variant="outline" width="100%">
                <CardBody>
                  <Text mb="8px">Confirmar identidade</Text>
                  <FormField
                    form={form}
                    field="oldPassword"
                    label={
                      <Hint>
                        {" "}
                        <RepeatClockIcon /> Senha antiga{" "}
                      </Hint>
                    }
                  >
                    <TextInput type="password" />
                  </FormField>
                  <Text mt="16px" mb="8px">
                    Novas credenciais
                  </Text>
                  <FormField
                    form={form}
                    field="newPassword"
                    label={
                      <Hint>
                        {" "}
                        <LockIcon /> Nova senha{" "}
                      </Hint>
                    }
                  >
                    <TextInput type="password" />
                  </FormField>
                  <FormField
                    form={form}
                    field="confirmNewPassword"
                    label={
                      <Hint>
                        {" "}
                        <LockIcon /> Confirmar nova senha{" "}
                      </Hint>
                    }
                  >
                    <TextInput type="password" />
                  </FormField>
                  <Button
                    mt="16px"
                    size="sm"
                    colorScheme="azul_1"
                    isDisabled={!form.isValid}
                    isLoading={loading}
                    type="submit"
                  >
                    Alterar senha
                  </Button>
                  <Text color="rosa.main">{error}</Text>
                </CardBody>
              </Card>
            </VStack>
          </form>
        )}
      </Formik>
    </>
  );
}
