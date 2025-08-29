export type ListedUser = {
  id: number;
  nome: string;
  email: string;
  conectado: boolean;
};

export enum WSMessageType {
  CONNECTION = 0,
  CHAT = 1,
  NOTIFICATION = 2,
  JSON = 255,
}

export type WSConnectionMessage = {
  user: ListedUser;
  online: boolean;
};

export type WSChatMessageTo = {
  to_user_id: string;
  message: string;
};

export type WSChatMessageFrom = {
  from_user: Omit<ListedUser, "conectado">;
  message: string;
};

export type WSNotification = {
  text: string;
  link: string | null;
};

export type WSJSONMessage = {
  body: Record<any, any>;
};

export type WSMessage = {
  type: WSMessageType;
  content:
    | WSConnectionMessage
    | WSChatMessageTo
    | WSChatMessageFrom
    | WSNotification
    | WSJSONMessage;
};
