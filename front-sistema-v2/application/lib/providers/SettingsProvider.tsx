"use client";

import { useUser } from "@/lib/hooks";
import {
  Dispatch,
  ReactNode,
  SetStateAction,
  createContext,
  useState,
} from "react";
import { User } from "../types/api/iv/auth";

export type Settings = {
  openDrawerOnHover: boolean;
  closeDrawerOnLeave: boolean;
  closeDrawerOnLinkClick: boolean;
};
export function SettingsProvider({ children }: { children: ReactNode }) {
  const { user } = useUser();
  const [settings, setSettings] = useState(loadSettings(user));

  return (
    <SettingsContext.Provider value={{ settings, setSettings }}>
      {children}
    </SettingsContext.Provider>
  );
}

export const loadSettings = (user: User | null): Settings => {
  const settingsStr = user
    ? localStorage.getItem(`iv.${user.id}.settings`)
    : null;
  return settingsStr ? JSON.parse(settingsStr) : defaultSettings();
};

export type SetSettings = Dispatch<SetStateAction<Settings>>;

export const defaultSettings = (): Settings => ({
  openDrawerOnHover: true,
  closeDrawerOnLeave: true,
  closeDrawerOnLinkClick: true,
});

export const SettingsContext = createContext<{
  settings: Settings;
  setSettings: SetSettings;
}>({
  settings: defaultSettings(),
  setSettings: () => {},
});
