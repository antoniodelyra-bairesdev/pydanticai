export type Role = {
  id: number;
  nome: string;
};
export type User = {
  id: number;
  nome: string;
  email: string;
  roles: Role[];
  devices: Device[];
};
export type Device = {
  id: number;
  address: string;
  user_agent: string;
  last_active: string;
  session_started: string;
  location: string | null;
};
export type Session = {
  user: User;
  token: string;
};
