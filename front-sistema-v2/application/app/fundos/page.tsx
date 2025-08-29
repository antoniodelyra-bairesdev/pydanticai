import IVServerHTTPClient from "@/lib/util/http/vanguarda/IVServerHTTPClient";
import { pathMetadata } from "../path.metadata";
import Fundos, { FundosProps } from "./_components/Fundos";

export const metadata = pathMetadata["/fundos"];

type ExtractFn = <T>(response: Response) => Promise<T[]>;

export default async function FundosPage() {
  const http = new IVServerHTTPClient({ withCredentials: true });

  const [custodiantes, fundos] = await Promise.all([
    http.fetch("v1/fundos/custodiantes"),
    http.fetch("v1/fundos"),
  ]);

  const extract: ExtractFn = (response) =>
    response.ok ? response.json() : Promise.resolve([]);

  const infos: FundosProps = {
    data: {
      custodiantes: await extract(custodiantes),
      fundos: await extract(fundos),
    },
  };

  return <Fundos {...infos} />;
}
