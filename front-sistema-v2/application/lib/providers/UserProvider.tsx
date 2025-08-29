"use client";

import {
  Dispatch,
  ReactNode,
  SetStateAction,
  createContext,
  useState,
} from "react";
import { User } from "../types/api/iv/auth";

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState(defaultSettings());

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}

export type SetUser = Dispatch<SetStateAction<User | null>>;

export const defaultSettings = (): User | null => {
  const userStr =
    typeof localStorage !== "undefined"
      ? localStorage.getItem("iv.user")
      : null;
  if (!userStr) return null;
  return JSON.parse(userStr);
};

export const UserContext = createContext<{
  user: User | null;
  setUser: SetUser;
}>({
  user: defaultSettings(),
  setUser: () => {},
});
