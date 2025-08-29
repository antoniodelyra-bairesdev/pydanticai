import JSONText from "@/app/_components/misc/JSONText";
import { Emissor } from "@/lib/types/api/iv/v1";
import IVServerHTTPClient from "@/lib/util/http/vanguarda/IVServerHTTPClient";
import { notFound } from "next/navigation";

export default async function Page({
  params: { id },
}: {
  params: { id: string };
}) {
  const http = new IVServerHTTPClient({ withCredentials: true });

  const response = await http.fetch("v1/ativos/emissores/" + id);
  if (response.status === 404) {
    notFound();
  } else if (!response.ok) {
    throw Error("Falha ao carregar ativo.");
  }

  const ativo = (await response.json()) as Emissor;

  return (
    <div>
      <p>Emissor de ID {id}</p>
      <JSONText json={ativo} />
    </div>
  );
}
