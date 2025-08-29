import { Tabela, TabelaProps } from "@/app/_components/grid/Tabela";
import { getColorHex } from "@/app/theme";
import {
  Ativo,
  AtivoCarteira,
  CarteiraAdministrada,
  Compromissada,
  EmprestimoEquity,
  Futuro,
  OpcaoAcao,
  OpcaoDerivativo,
  Posicao,
  TermoEquity,
  TermoRendaFixa,
} from "@/lib/types/leitor-carteiras-fundos/types";
import { fmtDate, fmtNumber } from "@/lib/util/string";
import { HStack, Icon, Text } from "@chakra-ui/react";
import {
  ColDef,
  ColGroupDef,
  ICellRendererParams,
  ValueFormatterParams,
  ValueGetterParams,
} from "ag-grid-community";
import { valueOrDefault } from "chart.js/dist/helpers/helpers.core";
import { param } from "cypress/types/jquery";
import {
  IoAttachOutline,
  IoCaretDown,
  IoCaretUp,
  IoCheckmark,
  IoCubeOutline,
  IoDocumentAttachOutline,
  IoDocumentOutline,
  IoDocumentTextOutline,
  IoIdCardOutline,
} from "react-icons/io5";

export type TabelaAtivosProps = {
  posicoes: Posicao[];
  focoPosicao: number;
  mostrarDiferencaOuValorTotal?: "DIFERENCA" | "TOTAL";
  mostrarBaseComparacao?: boolean;
} & TabelaProps["boxProps"];

const isinSubjacente = (atv: Ativo | undefined): string | undefined =>
  (atv as Compromissada | Futuro)?.isin_ativo_base?.valor ??
  (atv as TermoRendaFixa | TermoEquity | EmprestimoEquity)?.isin_ativo_objeto
    ?.valor ??
  undefined;

const ticker = (atv: Ativo | undefined): string | undefined =>
  atv?.ticker?.valor ??
  atv?.identificadores.find((i) =>
    ["BVMF", "B3", "TICKER"].includes(i.tipo.toUpperCase()),
  )?.valor;

const tickerSubjacente = (atv: Ativo | undefined): string | undefined =>
  (((atv as TermoEquity)?.ticker_ativo_objeto?.valor ??
  ((atv as OpcaoAcao)?.identificador_ativo_objeto?.tipo !== "ISIN"
    ? (atv as OpcaoAcao)?.identificador_ativo_objeto?.valor
    : undefined) ??
  (atv as OpcaoDerivativo)?.identificador_derivativo_objeto?.tipo !== "ISIN")
    ? (atv as OpcaoDerivativo)?.identificador_derivativo_objeto?.valor
    : undefined) ?? undefined;

const idAtivo = (atv: Ativo): string => {
  const base = (() => {
    if (
      [
        "EmprestimoEquity",
        "Compromissada",
        "Termo",
        "TermoRendaFixa",
        "TermoEquity",
      ].includes(atv.tipo)
    ) {
      return isinSubjacente(atv) ?? "SEMISIN";
    } else {
      return atv.isin?.valor ?? "SEMISIN";
    }
  })();
  return `${atv.tipo}-${base}`;
};

const idPosicao = (pos: Posicao): string => {
  return `${pos.data}-${pos.fonte?.tipo ?? "???"}-${pos.produto_investimento?.isin?.valor ?? (pos.produto_investimento as CarteiraAdministrada)?.identificador_titular.valor}`;
};

const financeiroPosicao = (posAtivo: AtivoCarteira) =>
  posAtivo.ativo.tipo === "Futuro"
    ? Number((posAtivo.ativo as Futuro).valor_de_ajuste)
    : Number(posAtivo.preco.preco_mercado ?? posAtivo.preco.preco_curva) *
      Number(posAtivo.quantidade.total) *
      (posAtivo.vendido ? -1 : 1);

export default function TabelaAtivos({
  posicoes,
  focoPosicao,
  mostrarDiferencaOuValorTotal = "DIFERENCA",
  mostrarBaseComparacao = true,
  ...boxProps
}: TabelaAtivosProps) {
  const todasPosicoesAtivos: AtivoCarteira[] = [];
  const mapaIdAtivo: Record<string, Ativo> = {};
  const financeiroPosicaoTipoAtivo: Record<string, Record<string, number>> = {};
  const mapaTodasPosicoesAtivos = posicoes.reduce(
    (ativoParaPosicao, posicao) => {
      const pi = posicao.produto_investimento;
      if (!pi || !("ativos" in pi)) return ativoParaPosicao;
      for (let i = 0; i < pi.ativos.length; i++) {
        const posAtivo = pi.ativos[i];
        posAtivo.codigos_internos ??= {};
        const ida = idAtivo(posAtivo.ativo);
        const idp = idPosicao(posicao);
        const tipoAtivo = posAtivo.ativo.tipo;
        financeiroPosicaoTipoAtivo[idp] ??= {};
        financeiroPosicaoTipoAtivo[idp][tipoAtivo] ??= 0;
        financeiroPosicaoTipoAtivo[idp][tipoAtivo] +=
          financeiroPosicao(posAtivo);

        posAtivo.codigos_internos._ID_LEITURA = `${idp}-${i + 1}`;

        mapaIdAtivo[ida] ??= posAtivo.ativo;
        ativoParaPosicao[ida] ??= {};

        const mapaAtivo = ativoParaPosicao[idAtivo(posAtivo.ativo)];
        mapaAtivo[idp] ??= {};
        mapaAtivo[idp][posAtivo.codigos_internos._ID_LEITURA] = posAtivo;
        todasPosicoesAtivos.push(posAtivo);
      }
      return ativoParaPosicao;
    },
    {} as Record<string, Record<string, Record<string, AtivoCarteira>>>,
  );

  console.log({ mapaTodasPosicoesAtivos });

  return (
    <Tabela
      gridProps={{
        columnDefs: [
          {
            headerName: "Tipo",
            field: "ativo.tipo",
            valueGetter: ({ data, node }) =>
              node?.group
                ? (node.key ?? "") in mapaIdAtivo
                  ? (mapaIdAtivo[node.key ?? ""].tipo ?? "---")
                  : ""
                : (data?.ativo?.tipo ?? "---"),
            cellRenderer: ({ node, value }: ICellRendererParams) => (
              <HStack w="100%" alignItems="center">
                <Icon as={IoDocumentTextOutline} color="verde.700" />
                <Text textAlign="right">{value}</Text>
              </HStack>
            ),
            width: 144,
            rowGroup: true,
            rowGroupIndex: 0,
            hide: true,
          },
          {
            keyCreator(params) {
              return idAtivo(params.data?.ativo);
            },
            rowGroup: true,
            rowGroupIndex: 1,
            hide: true,
          },
          {
            headerName: "Posição",
            valueGetter: ({ data }: ValueGetterParams<AtivoCarteira>) =>
              data ? (data.vendido ? "V" : "C") : "",
            cellRenderer: ({ value, node, data }: ICellRendererParams) => (
              <Text
                w="100%"
                textAlign="center"
                fontWeight={600}
                color={value === "C" ? "azul_3.main" : "rosa.main"}
              >
                {value}
              </Text>
            ),
            width: 100,
          },
          {
            headerName: "ISIN",
            children: [
              {
                headerName: "Ativo",
                valueGetter: ({ data, node }) =>
                  node?.group
                    ? (node.key ?? "") in mapaIdAtivo
                      ? (mapaIdAtivo[node.key ?? ""].isin?.valor ?? "---")
                      : ""
                    : (data?.ativo?.isin?.valor ?? "---"),
                cellRenderer: ({ value, data, node }: ICellRendererParams) =>
                  !value ? (
                    <></>
                  ) : (
                    <HStack>
                      <Icon
                        as={
                          isinSubjacente(
                            node.group
                              ? mapaIdAtivo[node.key ?? ""]
                              : data?.ativo,
                          )
                            ? IoDocumentAttachOutline
                            : IoDocumentOutline
                        }
                        color={
                          isinSubjacente(
                            node.group
                              ? mapaIdAtivo[node.key ?? ""]
                              : data?.ativo,
                          )
                            ? "roxo.main"
                            : "azul_2.main"
                        }
                        w="20px"
                        h="20px"
                      />
                      <Text>{value}</Text>
                    </HStack>
                  ),
                width: 160,
              },
              {
                headerName: "Subjacente",
                columnGroupShow: "open",
                valueGetter({ data, node }) {
                  return node?.group
                    ? (node.key ?? "") in mapaIdAtivo
                      ? isinSubjacente(mapaIdAtivo[node.key ?? ""])
                      : ""
                    : isinSubjacente(data?.ativo);
                },
                cellRenderer: ({ value, node }: ICellRendererParams) =>
                  !value ? (
                    <></>
                  ) : (
                    value && (
                      <HStack>
                        <Icon
                          as={IoAttachOutline}
                          color="azul_2.main"
                          w="20px"
                          h="20px"
                        />
                        <Text>{value}</Text>
                      </HStack>
                    )
                  ),
                width: 160,
              },
            ],
          },
          {
            headerName: "Ticker",
            children: [
              {
                headerName: "Ativo",
                valueGetter: ({
                  data,
                  node,
                }: ValueGetterParams<AtivoCarteira>) =>
                  node?.group
                    ? (node.key ?? "") in mapaIdAtivo
                      ? (ticker(mapaIdAtivo[node.key ?? ""]) ?? "---")
                      : ""
                    : (ticker(data?.ativo) ?? "---"),
                cellRenderer: ({ value, data, node }: ICellRendererParams) =>
                  !value ? (
                    <></>
                  ) : (
                    <HStack>
                      <Icon
                        as={
                          tickerSubjacente(
                            node.group
                              ? mapaIdAtivo[node.key ?? ""]
                              : data?.ativo,
                          )
                            ? IoDocumentAttachOutline
                            : IoDocumentOutline
                        }
                        color={
                          tickerSubjacente(
                            node.group
                              ? mapaIdAtivo[node.key ?? ""]
                              : data?.ativo,
                          )
                            ? "roxo.main"
                            : "azul_2.main"
                        }
                        w="20px"
                        h="20px"
                      />
                      <Text>{value}</Text>
                    </HStack>
                  ),
                width: 160,
              },
              {
                headerName: "Subjacente",
                columnGroupShow: "open",
                valueGetter: ({
                  data,
                  node,
                }: ValueGetterParams<AtivoCarteira>) =>
                  node?.group
                    ? (node.key ?? "") in mapaIdAtivo
                      ? tickerSubjacente(mapaIdAtivo[node.key ?? ""])
                      : ""
                    : tickerSubjacente(data?.ativo),
                cellRenderer: ({ value, node }: ICellRendererParams) =>
                  !value ? (
                    <></>
                  ) : (
                    value && (
                      <HStack>
                        <Icon
                          as={IoAttachOutline}
                          color="azul_2.main"
                          w="20px"
                          h="20px"
                        />
                        <Text>{value}</Text>
                      </HStack>
                    )
                  ),
                width: 160,
              },
            ],
            width: 144,
          },
          getColunasDiff({
            posicoes,
            focoPosicao,
            modoDiferenca: "DIFERENCA",
            mostrarBaseComparacao: true,
            nomeColuna: "Quantidade",
            valor(idGrupo, idPos, idPosAtivo) {
              if (idPosAtivo) {
                const n =
                  mapaTodasPosicoesAtivos[idGrupo]?.[idPos]?.[idPosAtivo]
                    ?.quantidade.total;
                return n ? Number(n) : undefined;
              } else if (mapaTodasPosicoesAtivos[idGrupo]?.[idPos]) {
                return Object.values(
                  mapaTodasPosicoesAtivos[idGrupo][idPos],
                )?.reduce((soma, posAtivo) => {
                  return soma + Number(posAtivo.quantidade.total);
                }, 0);
              }
            },
            valueFormatter({ value }) {
              return value
                ? Number(value).toLocaleString("pt-BR", {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 8,
                  })
                : "";
            },
            cellRenderer: ({
              value,
              valueFormatted,
              isFirst,
            }: ICellRendererParams & { isFirst?: boolean }) => {
              return (
                <HStack
                  w="100%"
                  alignItems="center"
                  justifyContent="space-between"
                >
                  {isFirst && <Icon as={IoCubeOutline} color="verde.main" />}
                  <Text flex={1} textAlign="right">
                    {valueFormatted}
                  </Text>
                </HStack>
              );
            },
          }),
          getColunasDiff({
            posicoes,
            focoPosicao,
            modoDiferenca: "TOTAL",
            mostrarBaseComparacao: true,
            nomeColuna: "Financeiro",
            valor(idGrupo, idPos, idPosAtivo) {
              if (financeiroPosicaoTipoAtivo?.[idPos]?.[idGrupo]) {
                return financeiroPosicaoTipoAtivo[idPos][idGrupo];
              }
              if (idPosAtivo) {
                const pos = mapaTodasPosicoesAtivos[idGrupo]?.[idPos]?.[
                  idPosAtivo
                ] as AtivoCarteira | undefined;
                return pos ? financeiroPosicao(pos) : 0;
              }
              if (mapaTodasPosicoesAtivos[idGrupo]?.[idPos]) {
                return Object.values(
                  mapaTodasPosicoesAtivos[idGrupo][idPos],
                )?.reduce((soma, posAtivo) => financeiroPosicao(posAtivo), 0);
              }
            },
            flex: 1,
            minWidth: 180,
            valueFormatter({ value }) {
              return value ? fmtNumber(value) : "";
            },
            cellRenderer: ({
              value,
              valueFormatted,
              isFirst,
            }: ICellRendererParams & { isFirst?: boolean }) => {
              return (
                <HStack
                  w="100%"
                  alignItems="center"
                  justifyContent="space-between"
                >
                  {isFirst && (
                    <HStack
                      w="24px"
                      h="20px"
                      pb="2px"
                      justifyContent="center"
                      alignItems="center"
                      bgColor={
                        {
                          [1]: "verde.50",
                          [0]: "cinza.100",
                          [-1]: "rosa.50",
                        }[Math.sign(value ?? 0)]
                      }
                      borderRadius="4px"
                    >
                      <Text
                        color={
                          {
                            [1]: "verde.main",
                            [0]: "cinza.500",
                            [-1]: "rosa.main",
                          }[Math.sign(value ?? 0)]
                        }
                      >
                        R$
                      </Text>
                    </HStack>
                  )}
                  <Text flex={1} textAlign="right">
                    {valueFormatted}
                  </Text>
                </HStack>
              );
            },
          }),
        ],
        autoGroupColumnDef: {
          pinned: "left",
          headerName: "Agrupado",
          cellRendererParams: {
            innerRenderer: ({ value, node }: ICellRendererParams) => {
              return (
                <HStack>
                  {!(value in mapaIdAtivo) && node.group && (
                    <Icon as={IoDocumentTextOutline} color="verde.main" />
                  )}
                  <Text>{value in mapaIdAtivo ? "Operações" : value}</Text>;
                </HStack>
              );
            },
          },
        },
        getRowStyle({ node }) {
          return {
            fontSize: "13px",
            backgroundColor: node.group
              ? (node.key ?? "") in mapaIdAtivo
                ? "none"
                : getColorHex("azul_1.50") + "AF"
              : getColorHex("cinza.100"),
          };
        },
        rowData: todasPosicoesAtivos,
        tooltipShowDelay: 0,
        headerHeight: 29,
        rowHeight: 28,
      }}
      boxProps={{ ...boxProps }}
    />
  );
}

const getColunasDiff = ({
  posicoes,
  focoPosicao,
  modoDiferenca,
  mostrarBaseComparacao,
  nomeColuna,
  valor,
  ...colDef
}: {
  posicoes: Posicao[];
  focoPosicao: number;
  modoDiferenca: "DIFERENCA" | "TOTAL" | "%PL";
  mostrarBaseComparacao: boolean;
  nomeColuna: string;
  valor: (
    idGrupo: string,
    idPosicao: string,
    idPosicaoAtivo: string | undefined,
  ) => number | undefined;
} & ColDef): ColGroupDef => {
  const base = posicoes[focoPosicao] as Posicao | undefined;
  const comparacoes = posicoes.filter((p) => p !== base);

  const vg =
    (idPos: string) =>
    ({
      node,
      data,
    }: {
      node: ValueGetterParams["node"];
      data: ValueGetterParams["data"];
    }) =>
      valor(
        node?.group
          ? (node?.key ?? "")
          : data?.ativo
            ? idAtivo(data.ativo)
            : "",
        idPos,
        (data as AtivoCarteira | undefined)?.codigos_internos?._ID_LEITURA,
      );
  const slug = (pos: Posicao) =>
    `${fmtDate(pos.data)} ${pos.fonte?.tipo ?? ""} ${pos?.produto_investimento?.nome ?? ""}`;

  return {
    headerName: nomeColuna,
    children: [
      {
        headerName: `${nomeColuna} ${base ? slug(base) : ""}`,
        headerTooltip: `${nomeColuna} ${base ? slug(base) : ""}`,
        valueGetter: vg(base ? idPosicao(base) : ""),
        suppressMovable: true,
        ...colDef,
        cellStyle: () => ({
          borderLeft: "1px solid " + getColorHex("cinza.main"),
        }),
        cellRenderer: (params: ICellRendererParams) => {
          if (!params.node.group) {
            return colDef.cellRenderer ? (
              colDef.cellRenderer?.({
                isFirst: true,
                ...params,
              })
            ) : (
              <Text>{params.valueFormatted ?? params.value}</Text>
            );
          }
          if ([undefined, null, ""].includes(params.value)) return;
          return colDef.cellRenderer ? (
            colDef.cellRenderer?.({
              isFirst: true,
              ...params,
            })
          ) : (
            <Text>{params.value}</Text>
          );
        },
      },
      ...comparacoes.map(
        (p, i) =>
          ({
            columnGroupShow: "open",
            headerName: `${modoDiferenca === "DIFERENCA" ? "Δ" : modoDiferenca === "%PL" ? "%PL" : "Total"} ${slug(p)}`,
            headerTooltip: `${modoDiferenca === "DIFERENCA" ? "Δ" : modoDiferenca === "%PL" ? "%PL" : "Total"} ${slug(p)}`,
            valueGetter: vg(idPosicao(p)),
            suppressMovable: true,
            ...colDef,
            cellRenderer: ({
              value,
              valueFormatted,
              node,
              data,
              formatValue,
              ...params
            }: ICellRendererParams) => {
              if (!node.group) {
                return colDef.cellRenderer ? (
                  colDef.cellRenderer?.({
                    value,
                    valueFormatted,
                    node,
                    data,
                    ...params,
                  })
                ) : (
                  <Text>{valueFormatted ?? value}</Text>
                );
              }
              if ([undefined, null, ""].includes(value)) return;
              const outroValor = base
                ? (vg(idPosicao(base))({ node, data }) ?? 0)
                : 0;
              const diferenca = Number(value) - Number(outroValor);
              const sinal = Math.sign(diferenca);
              const pl = Number(
                p.produto_investimento?.patrimonio_liquido ?? 0,
              );
              const percPl = (value / pl) * 100;
              const v =
                modoDiferenca === "TOTAL"
                  ? value
                  : modoDiferenca === "DIFERENCA"
                    ? diferenca
                    : percPl;
              const fv =
                modoDiferenca === "TOTAL"
                  ? valueFormatted
                  : modoDiferenca === "DIFERENCA"
                    ? formatValue?.(diferenca)
                    : formatValue?.(percPl);
              return (
                <HStack>
                  {["DIFERENCA", "TOTAL"].includes(modoDiferenca) && (
                    <Icon
                      as={
                        {
                          [1]: IoCaretUp,
                          [0]: IoCheckmark,
                          [-1]: IoCaretDown,
                        }[sinal]
                      }
                      color={
                        {
                          [1]: "verde.main",
                          [0]: "cinza.main",
                          [-1]: "rosa.main",
                        }[sinal]
                      }
                    />
                  )}
                  {colDef.cellRenderer ? (
                    colDef.cellRenderer?.({
                      value: v,
                      valueFormatted: fv,
                      node,
                      data,
                      ...params,
                    })
                  ) : (
                    <Text>{v}</Text>
                  )}
                </HStack>
              );
            },
            cellStyle:
              i === comparacoes.length - 1
                ? () => ({
                    borderRight: "1px solid " + getColorHex("cinza.main"),
                  })
                : undefined,
          }) as ColDef,
      ),
    ],
  };
};
