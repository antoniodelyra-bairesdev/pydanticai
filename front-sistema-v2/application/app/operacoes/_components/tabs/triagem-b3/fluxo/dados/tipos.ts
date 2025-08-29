import { StaticImageData } from "next/image";
import { IconType } from "react-icons";
import { Node } from "reactflow";

export type WithStatus = {
  pending?: boolean;
  bgColor?: string;
  color: string;
  text: string;
  icon: IconType;
};

export type Company = {
  name: string;
  icon?: StaticImageData | IconType;
  detail?: React.ReactNode;
};

export type NoData = {
  label: string;
  status: WithStatus;
  company?: Company;
  details?: React.ReactNode;
  metadata?: any;
};

export type No = Node<NoData>;

export enum EstadoNo {
  AGUARDANDO,
  PENDENTE,
  SUCESSO,
  FALHA,
  DESATIVADO,
}
