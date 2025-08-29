import {
  Fundo,
  FundoCaracteristicaExtra,
  FundoClassificacaoDocumento,
  FundoDetalhes,
  InstituicaoFinanceira,
  Mesa,
} from "@/lib/types/api/iv/v1";
import IVServerHTTPClient from "@/lib/util/http/vanguarda/IVServerHTTPClient";
import { notFound } from "next/navigation";
import DetalhesFundo from "./_components/DetalhesFundo";
import { FundoDetalhesProvider } from "./_providers/FundoDetalhesProvider";

export type PageParams = {
  params: { id: string };
};

const toArray = <T,>(r: Response) => (r.ok ? (r.json() as Promise<T[]>) : []);

export default async function PaginaFundo({ params: { id } }: PageParams) {
  const httpClient = new IVServerHTTPClient({ withCredentials: true });
  const response = await httpClient.fetch("v1/fundos/" + id);
  if (response.status === 404) {
    notFound();
  }
  const fundo = response.ok
    ? ((await response.json()) as FundoDetalhes)
    : undefined;

  if (!fundo) {
    return <h1>Erro. {(await response.json())?.detail}</h1>;
  }

  const [
    lista_administradores,
    lista_controladores,
    lista_custodiantes,
    mesas,
    categorias_documentos,
    caracteristicas_extras,
  ] = await Promise.all([
    httpClient
      .fetch("v1/fundos/administradores")
      .then(toArray<InstituicaoFinanceira>),
    httpClient
      .fetch("v1/fundos/controladores")
      .then(toArray<InstituicaoFinanceira>),
    httpClient
      .fetch("v1/fundos/custodiantes")
      .then(toArray<InstituicaoFinanceira>),
    httpClient.fetch("v1/mesa/").then(toArray<Mesa>),
    httpClient
      .fetch("v1/fundos/documentos/categorias")
      .then(toArray<FundoClassificacaoDocumento>),
    httpClient
      .fetch("v1/fundos/caracteristicas-extras")
      .then(toArray<FundoCaracteristicaExtra>),
  ]);

  return (
    <FundoDetalhesProvider fundoInicial={fundo}>
      <DetalhesFundo
        fundo={fundo}
        lista_administradores={lista_administradores}
        lista_controladores={lista_controladores}
        lista_custodiantes={lista_custodiantes}
        lista_gestores={[
          { id: -1, nome: "Icatu Vanguarda" },
          { id: -2, nome: "Icatu Seguros" },
          { id: -3, nome: "Rio Grande Seguros" },
        ]}
        lista_mesas={mesas}
        caracteristicas_extras={caracteristicas_extras}
        categorias_documentos={categorias_documentos}
      />
    </FundoDetalhesProvider>
  );
}
