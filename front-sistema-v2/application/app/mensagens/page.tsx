import { Metadata } from "next";
import { pathMetadata } from "../path.metadata";
import Usuarios from "./_components/Usuarios";
import SSRFlex from "../_components/ssr/SSRFlex";

export const metadata: Metadata = pathMetadata["/mensagens"];

export default async function Page() {
  return (
    <SSRFlex flexDirection="column" padding="12px" height="100%">
      <p style={{ fontSize: "24px", margin: "0px 0px 12px 0px" }}>Mensagens</p>
      <p>
        Atualmente as mensagens só podem ser enviadas para quem está online no
        momento.
      </p>
      <p>
        Futuramente elas poderão ser enviadas a qualquer momento e ficarão
        armazenadas para leitura.
      </p>
      <hr style={{ margin: "24px 0px 24px 0px" }} />
      <Usuarios />
    </SSRFlex>
  );
}
