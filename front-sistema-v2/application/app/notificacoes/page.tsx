import { Metadata } from "next";
import { pathMetadata } from "../path.metadata";
import Notifications from "./_components/Notifications";

export const metadata: Metadata = pathMetadata["/notificacoes"];

export default async function Page() {
  return <Notifications />;
}
