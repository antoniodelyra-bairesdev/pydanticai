import { Metadata } from "next";
import { pathMetadata } from "../path.metadata";
import Dashboard from "./_components/Dashboard";

export const metadata: Metadata = pathMetadata["/dashboard"];

export default function Page() {
  return <Dashboard />;
}
