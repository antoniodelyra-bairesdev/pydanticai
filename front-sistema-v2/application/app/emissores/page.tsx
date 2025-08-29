import IVServerHTTPClient from "@/lib/util/http/vanguarda/IVServerHTTPClient";
import { pathMetadata } from "../path.metadata";
import Emissores from "./_components/Emissores";
import {
  AnalistaCredito,
  EmissorGrupo,
  EmissorSetor,
} from "@/lib/types/api/iv/v1";
import { EmissoresPageProvider } from "./provider";

export const metadata = pathMetadata["/emissores"];

const toMap = <T extends { nome: string }>(
  r: Response,
): Promise<Record<string, T>> | Record<string, T> =>
  r.ok
    ? r
        .json()
        .then((obj: T[]) =>
          obj.reduce(
            (map, value) => ((map[value.nome] = value), map),
            {} as Record<string, T>,
          ),
        )
    : ({} as Record<string, T>);

export default async function Page() {
  const http = new IVServerHTTPClient({ withCredentials: true });
  const [analistas, grupos, setores] = await Promise.all([
    http
      .fetch("v1/ativos/analistas")
      .then((r) =>
        r.ok
          ? r
              .json()
              .then((obj: AnalistaCredito[]) =>
                obj.reduce(
                  (map, value) => ((map[value.user.nome] = value), map),
                  {} as Record<string, AnalistaCredito>,
                ),
              )
          : ({} as Record<string, AnalistaCredito>),
      ),
    http.fetch("v1/ativos/grupos").then(toMap<EmissorGrupo>),
    http
      .fetch("v1/ativos/setores?with_sys_data=true")
      .then(toMap<EmissorSetor>),
  ] as const);
  return (
    <EmissoresPageProvider>
      <Emissores {...{ analistas, grupos, setores }} />
    </EmissoresPageProvider>
  );
}
