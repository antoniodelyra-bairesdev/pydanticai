import JSONText from "@/app/_components/misc/JSONText";
import { Ativo } from "@/lib/types/api/iv/v1";
import IVServerHTTPClient from "@/lib/util/http/vanguarda/IVServerHTTPClient";
import { notFound } from "next/navigation";

export default async function Page({
  params: { codigo },
}: {
  params: { codigo: string };
}) {
  const http = new IVServerHTTPClient({ withCredentials: true });

  const response = await http.fetch("v1/ativos/" + codigo);
  if (response.status === 404) {
    notFound();
  } else if (!response.ok) {
    throw Error("Falha ao carregar ativo.");
  }

  const ativo = (await response.json()) as Ativo;

  return (
    <div>
      <p>Ativo {codigo}</p>
      <JSONText json={ativo} />
    </div>
  );
}
