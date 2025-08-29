export type Notification = {
  id: number;
  created_at: string;
  text: string;
  link: string | null;
};

export type SelectOption = {
  label: string;
  value: number | string;
};
