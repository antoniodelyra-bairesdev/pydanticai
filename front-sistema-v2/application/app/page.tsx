import Home from "./_components/home/Home";
import { pathMetadata } from "./path.metadata";

export const metadata = pathMetadata["/"];

export default async function AppPage() {
  return <Home />;
}
