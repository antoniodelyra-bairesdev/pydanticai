"use client";

import { useColorModeValue, useToast } from "@chakra-ui/react";
import { useContext, useState } from "react";

import {
  Settings,
  SettingsContext,
  loadSettings,
} from "@/lib/providers/SettingsProvider";
import { UserContext } from "@/lib/providers/UserProvider";
import { useRouter } from "next/navigation";
import { WebSocketsContext } from "../providers/WebSocketsProvider";
import { User } from "../types/api/iv/auth";
import IVBrowserHTTPClient from "../util/http/vanguarda/IVBrowserHTTPClient";

export function useColors() {
  return {
    bgError: "rosa.200",
    bgWarn: "amarelo.200",
    bgOk: "verde.200",
    bgDeleted: useColorModeValue("laranja.900", "laranja.main"),
    warnText: useColorModeValue("amarelo.main", "amarelo.300"),
    blue: useColorModeValue("azul_1.700", "azul_2.900"),
    blueHover: useColorModeValue("azul_1.main", "azul_2.800"),
    hover: useColorModeValue("blackAlpha.200", "whiteAlpha.200"),
    text: useColorModeValue("black", "white"),
    heading: useColorModeValue("azul_1.main", "cinza.main"),
    textOption: useColorModeValue("black", "cinza.main"),
    bgText: useColorModeValue("blackAlpha.500", "whiteAlpha.500"),
  };
}

export const useSettings = () => {
  const { settings, setSettings: setSettingsState } =
    useContext(SettingsContext);

  const setSettings = (user: User | null, newSettings: Partial<Settings>) => {
    if (!user) throw ReferenceError("User not registered in client storage!");
    const updatedSettings = { ...settings, ...newSettings };
    localStorage.setItem(
      `iv.${user.id}.settings`,
      JSON.stringify(updatedSettings),
    );
    setSettingsState(updatedSettings);
  };

  const setUserSettings = (user: User | null) => {
    setSettingsState(loadSettings(user));
  };

  return { settings, setSettings, loadSettings: setUserSettings };
};

export function useUser() {
  const { user, setUser: setUserState } = useContext(UserContext);
  const router = useRouter();

  const setUser = (newUser: User | null) => {
    const userKey = "iv.user";
    if (!newUser) {
      localStorage.removeItem(userKey);
      document.cookie = "user_token=; expires=Thu, 01 Jan 1970 00:00:00 GMT";
      router.replace("/login");
    } else {
      localStorage.setItem(userKey, JSON.stringify(newUser));
    }
    setUserState(newUser);
  };

  return { user, setUser };
}

export function useHTTP(options?: { withCredentials: boolean }) {
  const toast = useToast();
  const { setUser } = useUser();
  const httpClient = new IVBrowserHTTPClient(toast, () => setUser(null));
  httpClient.withCredentials = options?.withCredentials ?? false;
  return httpClient;
}

export function useWebSockets() {
  const { connection, connect, disconnect } = useContext(WebSocketsContext);
  return { connection, connect, disconnect };
}

export function useAsync() {
  const [loading, setLoading] = useState(false);
  const load = async (callback: () => Promise<void>) => {
    setLoading(true);
    try {
      await callback();
    } finally {
      setLoading(false);
    }
  };
  return [loading, load] as const;
}
