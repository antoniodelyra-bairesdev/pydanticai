import { pathMetadata } from "../path.metadata";
import Calculadora from "./_components/Calculadora";

export const metadata = pathMetadata["/calculadora"];

export default async function CalculadoraPage() {
  return <Calculadora />;
}
