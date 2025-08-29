"use client";

import { CacheProvider } from "@chakra-ui/next-js";
import { ChakraProvider, localStorageManager } from "@chakra-ui/react";
import dynamic from "next/dynamic";

import { useUser } from "@/lib/hooks";
import { SettingsProvider } from "@/lib/providers/SettingsProvider";
// Evitando que o Next.JS tente processar estas providers do lado do servidor
const UserProvider = dynamic(
  () => import("@/lib/providers/UserProvider").then((m) => m.UserProvider),
  { ssr: false },
);
const WebSocketsProvider = dynamic(
  () =>
    import("@/lib/providers/WebSocketsProvider").then(
      (m) => m.WebSocketsProvider,
    ),
  { ssr: false },
);
import ivTheme from "./theme";

export function ClientProviders({ children }: { children: React.ReactNode }) {
  return (
    <CacheProvider>
      <UserProvider>
        <SettingsProvider>
          <WebSocketsProvider
            identificador="Global"
            url={process.env.NEXT_PUBLIC_WS_URL}
          >
            <Chakra>{children}</Chakra>
          </WebSocketsProvider>
        </SettingsProvider>
      </UserProvider>
    </CacheProvider>
  );
}

function Chakra({ children }: { children: React.ReactNode }) {
  const { user } = useUser();

  const colorModeManager: typeof localStorageManager = {
    type: "localStorage",
    get(init) {
      if (!user) return "light";
      const fromStorage = localStorage.getItem(
        `iv.${user.id}.chakra-ui-color-mode`,
      );
      if (fromStorage !== "light" && fromStorage !== "dark") return "light";
      return init;
    },
    set(value) {
      if (!user) return;
      if (value === "system") {
        value = "light";
      }
      localStorage.setItem(`iv.${user.id}.chakra-ui-color-mode`, value);
    },
  };

  return (
    <ChakraProvider colorModeManager={colorModeManager} theme={ivTheme}>
      {children}
    </ChakraProvider>
  );
}
