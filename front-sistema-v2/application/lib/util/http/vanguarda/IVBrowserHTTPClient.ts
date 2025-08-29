"use client";

import React from "react";
import HTTPClient from "../HTTPClient";

import { Box, Button, CreateToastFnReturn, Icon, Text } from "@chakra-ui/react";
import {
  IoAddCircle,
  IoAlertCircle,
  IoBug,
  IoCheckmarkCircle,
  IoDocumentLock,
  IoIdCard,
  IoOpenOutline,
  IoSearch,
} from "react-icons/io5";
import Link from "next/link";

const toastMessages = (status: number): string =>
  ({
    200: "Sucesso.",
    201: "Dados armazenados.",
    401: "Acesso negado.",
    403: "Credenciais insuficientes.",
    404: "Não encontrado.",
    422: "Pedido inválido.",
    500: "Falha do servidor.",
  })[status] ??
  {
    200: "OK.",
    400: "Falha no pedido.",
    500: "Erro de servidor.",
  }[Math.floor(status / 100) * 100] ??
  "Falha.";

const toastIcons = (status: number) =>
  ({
    200: IoCheckmarkCircle,
    201: IoAddCircle,
    401: IoIdCard,
    403: IoDocumentLock,
    404: IoSearch,
    422: IoAlertCircle,
    500: IoBug,
  })[status] ??
  {
    200: IoCheckmarkCircle,
    400: IoDocumentLock,
    500: IoBug,
  }[Math.floor(status / 100) * 100] ??
  IoAlertCircle;

const toastColors = (range: number) =>
  (
    ({
      200: "verde",
      400: "laranja",
      500: "rosa",
    }) as const
  )[range] ?? "roxo";

const rangeToProperty = {
  200: "success",
  400: "clientError",
  500: "serverError",
} as const;

export default class IVBrowserHTTPClient extends HTTPClient {
  constructor(
    private toastControl?: CreateToastFnReturn,
    private onUnauthorized?: () => void,
  ) {
    super(process.env.NEXT_PUBLIC_IV_API_URL ?? "URL_NAO_DEFINIDA");
  }

  public async fetch(
    url: RequestInfo | URL,
    options?: RequestInit & {
      hideToast?: {
        success?: boolean;
        clientError?: boolean;
        serverError?: boolean;
      };
      multipart?: boolean;
    },
  ): Promise<Response> {
    const result = await super.fetch(url, options);
    const cloned = result.clone();
    if (!result.ok && 401 === result.status) {
      this.onUnauthorized?.();
    }
    const range = Math.floor(result.status / 100) * 100;
    if (!options?.hideToast?.[rangeToProperty[range as 200 | 400 | 500]]) {
      const text: React.ReactNode[] = [
        React.createElement(Text, {}, toastMessages(result.status)),
      ];
      let data: {
        detail?: string | { request_id?: string };
      } | null = null;
      if (
        !options?.hideToast?.clientError ||
        !options?.hideToast?.serverError
      ) {
        if (!options?.multipart) {
          data = (await result.json()) as {
            detail?: string | { request_id?: string };
          } | null;
        }
      }
      const { detail } = data ?? { detail: null };
      if (detail) {
        if (typeof detail === "string") {
          text.push(
            React.createElement(
              Text,
              { fontSize: "sm" },
              "Mensagem do servidor: " + detail,
            ),
          );
        } else if (detail?.request_id) {
          text.push(
            React.createElement(
              Text,
              { fontSize: "xs" },
              "Identificador: " + detail.request_id,
            ),
          );
          text.push(
            React.createElement(
              Link,
              {
                target: "_blank",
                rel: "noopener noreferrer",
                href: `https://teams.microsoft.com/l/chat/0/0?message=${encodeURIComponent(
                  "Aconteceu um erro no sistema.",
                )}&users=${encodeURIComponent(
                  [
                    "gioliveira@icatuvanguarda.com.br",
                    "moribeiro@icatuvanguarda.com.br",
                    "dvaz@icatuvanguarda.com.br",
                    "avsouza@icatuvanguarda.com.br",
                  ].join(","),
                )}&topicName=${encodeURIComponent("Erro " + detail.request_id)}`,
              },
              React.createElement(
                Button,
                {
                  colorScheme: "rosa",
                  size: "xs",
                  leftIcon: React.createElement(Icon, { as: IoOpenOutline }),
                },
                "Abrir no Teams",
              ),
            ),
          );
        }
      }
      React.createElement(Text, {}, toastMessages(result.status));
      this.toastControl?.({
        colorScheme: toastColors(range),
        icon: React.createElement(toastIcons(result.status), { size: "md" }),
        variant: "left-accent",
        description: React.createElement(Box, {}, ...text),
        position: "bottom-right",
        isClosable: Boolean(typeof detail === "object" && detail?.request_id),
        duration: range === 500 ? null : 5000,
      });
    }
    return cloned;
  }

  protected getCredentials(
    url: RequestInfo | URL,
    options?: RequestInit | undefined,
  ): { newUrl: RequestInfo | URL; newOptions: RequestInit } {
    const headers = { ...options?.headers } as Record<string, string>;
    const [_, token] =
      document.cookie
        .split(";")
        .map((c) => c.trim().split("="))
        .find(([name]) => name === "user_token") ?? [];
    if (token) {
      headers["X-User-Token"] = token;
    }
    return { newUrl: url, newOptions: { ...options, headers } };
  }
}
