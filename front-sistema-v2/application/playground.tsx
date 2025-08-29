import { Edge } from "reactflow";
import {
  EventoOperacao,
  QuebraRTC,
  EventoAlocacaoOperador,
  EventoAprovacaoBackoffice,
  Erro,
  AlocacaoStatus,
} from "./lib/types/api/iv/v1";
import { getColorHex } from "./app/theme";
import {
  IoDocumentText,
  IoPersonCircleOutline,
  IoSearchOutline,
} from "react-icons/io5";
import React from "react";
import { Button, HStack, Text } from "@chakra-ui/react";
import { companies } from "./app/operacoes/_components/tabs/triagem-b3/fluxo/dados/companies";
import { No } from "./app/operacoes/_components/tabs/triagem-b3/fluxo/dados/tipos";
import {
  ok,
  realocacao,
  aguardando,
  recusado,
} from "./app/operacoes/_components/tabs/triagem-b3/nodes";

const makePos = () => ({ x: 0, y: 0 });

const active = (edge: Edge, isActive: boolean) => {
  edge.animated = !isActive;
  edge.style = { stroke: getColorHex(isActive ? "verde.main" : "cinza.500") };
};

export type Grafo = {
  eventos: EventoOperacao[];
  nodes: No[];
  edges: Edge[];
  foco: No[];
};

export type GrafoCallbacks = {
  selectAlocacaoInterna: (
    eventoAlocacao: EventoAlocacaoOperador,
    habilitarControles: boolean,
    eventoAprovacao?: EventoAprovacaoBackoffice,
  ) => void;
  abrirMenuAlocacao: (
    pos: "backoffice" | "custodiante",
    idEvento: number,
  ) => void;
  abrirErro: (erro: Erro) => void;
};

export function alterarGrafoAPartirDeEventos(
  grafo: Grafo,
  evento: EventoOperacao,
  passado: boolean,
  opcoes: GrafoCallbacks,
) {
  grafo.foco = [];
  switch (evento.informacoes.tipo) {
    case "acato-voice":
      {
        const node = grafo.nodes.find((n) => n.id === "ac-voice");
        if (!node) break;
        node.data.status = { ...ok("Voice capturado"), pending: false };
        grafo.foco = [node];
        const edge = grafo.edges.find(
          (e) => e.id === "ac-voice|envio-alocacao-final",
        );
        if (!edge) break;
        active(edge, true);
      }
      break;

    case "alocacao-operador":
      {
        const ncn = evento.informacoes.operacao.registro_nome;
        const prefixoAlocacao = `aloc-op-${ncn ?? "inicial"}`;
        const alocacoes = grafo.nodes.filter((n) =>
          n.id.startsWith(`${prefixoAlocacao}-`),
        );
        const numAlocacao = alocacoes.length - 1;
        const idAlocacao = `${prefixoAlocacao}-${numAlocacao}`;
        const ultimaAlocacao = alocacoes.find((a) => a.id === idAlocacao);
        if (!ultimaAlocacao) break;

        ultimaAlocacao.data.metadata = {
          ...ultimaAlocacao.data.metadata,
          eventoAlocacao: evento.informacoes,
        };
        ultimaAlocacao.data.details = React.createElement(HStack, {
          fontSize: "xs",
          fontWeight: "thin",
          justifyContent: "space-between",
          alignItems: "flex-end",
          flex: 1,
          children: [
            React.createElement(HStack, {
              gap: "2px",
              children: [
                React.createElement(IoPersonCircleOutline),
                React.createElement(Text, {
                  fontSize: "xs",
                  fontWeight: "thin",
                  children: [evento.informacoes.operacao.usuario?.nome],
                }),
              ],
            }),
            React.createElement(Button, {
              colorScheme: "verde",
              onClick: () => {
                if (evento.informacoes.tipo !== "alocacao-operador") return;
                const ev = evento.informacoes;
                opcoes?.selectAlocacaoInterna?.(ev, false);
              },
              size: "xs",
              leftIcon: React.createElement(IoDocumentText),
              children: ["Detalhes"],
            }),
          ],
        });

        const alvoArestaSaidaId = `ap-bo-${ncn ?? "inicial"}-${numAlocacao}`;
        const arestaSaida = grafo.edges.find(
          (e) => e.id === `${idAlocacao}|${alvoArestaSaidaId}`,
        );
        if (!arestaSaida) break;
        ultimaAlocacao.data.status = ok("Alocado");
        grafo.foco = [ultimaAlocacao];
        active(arestaSaida, true);

        const alvoArestaSaida = grafo.nodes.find(
          (n) => n.id === alvoArestaSaidaId,
        );
        if (!alvoArestaSaida) break;

        alvoArestaSaida.data.status.pending = true;
        alvoArestaSaida.data.metadata = {
          ...alvoArestaSaida.data.metadata,
          eventoAlocacao: evento.informacoes,
        };
        alvoArestaSaida.data.details = React.createElement(HStack, {
          fontSize: "xs",
          fontWeight: "thin",
          justifyContent: "space-between",
          alignItems: "flex-end",
          flex: 1,
          children: [
            React.createElement(HStack),
            React.createElement(Button, {
              isDisabled: Boolean(passado),
              onClick: () => {
                if (evento.informacoes.tipo !== "alocacao-operador") return;
                const ev = evento.informacoes;
                opcoes?.selectAlocacaoInterna?.(ev, true);
              },
              colorScheme: "azul_4",
              size: "xs",
              leftIcon: React.createElement(IoSearchOutline),
              children: ["Revisar"],
            }),
          ],
        });
      }
      break;

    case "aprovacao-backoffice":
      {
        const ncn = evento.informacoes.numero_controle_nome;
        const prefixoAprovacao = `ap-bo-${ncn ?? "inicial"}`;
        const aprovacoes = grafo.nodes.filter((n) =>
          n.id.startsWith(`${prefixoAprovacao}-`),
        );
        const numAprovacao = aprovacoes.length - 1;
        const idAprovacao = `${prefixoAprovacao}-${numAprovacao}`;
        const ultimaAprovacao = aprovacoes.find((a) => a.id === idAprovacao);
        if (!ultimaAprovacao) break;
        const alvoArestaSaidaId = ncn
          ? `envio-realocacao-${ncn}-${numAprovacao}`
          : "envio-alocacao-final";
        const arestaSaida = grafo.edges.find(
          (e) => e.id === `${idAprovacao}|${alvoArestaSaidaId}`,
        );
        if (!arestaSaida) break;
        grafo.foco = [ultimaAprovacao];

        ultimaAprovacao.data.status.pending = false;
        ultimaAprovacao.data.metadata = {
          ...ultimaAprovacao.data.metadata,
          eventoAprovacao: evento.informacoes,
        };
        ultimaAprovacao.data.details = React.createElement(HStack, {
          fontSize: "xs",
          fontWeight: "thin",
          justifyContent: "space-between",
          alignItems: "flex-end",
          flex: 1,
          children: [
            React.createElement(HStack, {
              gap: "2px",
              children: [
                React.createElement(IoPersonCircleOutline),
                React.createElement(Text, {
                  fontSize: "xs",
                  fontWeight: "thin",
                  children: [evento.informacoes.usuario.nome],
                }),
              ],
            }),
            React.createElement(Button, {
              onClick: () => {
                if (evento.informacoes.tipo !== "aprovacao-backoffice") return;
                const ev = evento.informacoes;
                if (!ultimaAprovacao.data.metadata) return;
                opcoes?.selectAlocacaoInterna?.(
                  ultimaAprovacao.data.metadata.eventoAlocacao,
                  true,
                  ev,
                );
              },
              colorScheme: evento.informacoes.aprovacao ? "verde" : "amarelo",
              bgColor: "amarelo.700",
              size: "xs",
              leftIcon: React.createElement(IoDocumentText),
              children: ["Detalhes"],
            }),
          ],
        });

        if (evento.informacoes.aprovacao) {
          ultimaAprovacao.data.status = ok("Aprovado");
          active(arestaSaida, true);
          break;
        }
        ultimaAprovacao.data.status = realocacao();
        const posArestaSaida = grafo.edges.findIndex(
          (e) => e.id === arestaSaida?.id,
        );
        if (posArestaSaida !== -1) {
          grafo.edges.splice(posArestaSaida, 1);
        }
        const prefixoAlocacao = `aloc-op-${ncn ?? "inicial"}`;
        const novoNumAlocacao = grafo.nodes.filter((n) =>
          n.id.startsWith(`${prefixoAlocacao}-`),
        ).length;
        const novoIdAlocacao = `${prefixoAlocacao}-${novoNumAlocacao}`;
        const novoPedidoAlocacaoInterno: No = {
          id: novoIdAlocacao,
          type: "company-in-out",
          position: makePos(),
          data: {
            label: "Realocação interna",
            company: companies.vanguarda,
            status: { ...aguardando(), pending: true },
            details: React.createElement(HStack, {
              fontSize: "xs",
              fontWeight: "thin",
              justifyContent: "space-between",
              alignItems: "flex-end",
              flex: 1,
              children: [
                React.createElement(HStack),
                React.createElement(Button, {
                  isDisabled: Boolean(passado),
                  colorScheme: "verde",
                  onClick: () => {
                    if (evento.informacoes.tipo !== "aprovacao-backoffice")
                      return;
                    opcoes.abrirMenuAlocacao(
                      "backoffice",
                      evento.informacoes.id,
                    );
                  },
                  size: "xs",
                  leftIcon: React.createElement(IoDocumentText),
                  children: ["Realocar"],
                }),
              ],
            }),
            metadata: { eventoAprovacao: evento.informacoes },
          },
        };
        const novoIdAprovacao = `${prefixoAprovacao}-${numAprovacao + 1}`;
        const novaAprovacaoBackoffice: No = {
          id: novoIdAprovacao,
          type: "company-in-out",
          position: makePos(),
          data: {
            label: "Aprovação Backoffice",
            company: companies.vanguarda,
            status: aguardando(),
          },
        };
        const novaArestaAprovacaoAlocacao: Edge = {
          id: `${idAprovacao}|${novoIdAlocacao}`,
          source: idAprovacao,
          target: novoIdAlocacao,
          animated: false,
          style: { stroke: getColorHex("amarelo.main") },
        };
        const novaArestaAlocacaoAprovacao: Edge = {
          id: `${novoIdAlocacao}|${novoIdAprovacao}`,
          source: novoIdAlocacao,
          target: novoIdAprovacao,
          animated: true,
        };
        const novaArestaAprovacaoEnvio: Edge = {
          id: `${novoIdAprovacao}|${alvoArestaSaidaId}`,
          source: novoIdAprovacao,
          target: alvoArestaSaidaId,
          animated: true,
        };
        grafo.nodes.push(novoPedidoAlocacaoInterno, novaAprovacaoBackoffice);
        grafo.edges.push(
          novaArestaAprovacaoAlocacao,
          novaArestaAlocacaoAprovacao,
          novaArestaAprovacaoEnvio,
        );
      }
      break;

    case "envio-alocacao":
      {
        const ncn =
          evento.informacoes.mensagem.registro_nome?.numero_controle_nome;

        const prefixoRealocacao = `envio-realocacao-${ncn}`;
        const numRealocacoes = grafo.nodes.filter((n) =>
          n.id.startsWith(prefixoRealocacao),
        ).length;

        const idAloc = ncn
          ? `${prefixoRealocacao}-${numRealocacoes - 1}`
          : "envio-alocacao-final";
        const noAloc = grafo.nodes.find((n) => n.id === idAloc);
        const arestaSaida = grafo.edges.find((e) =>
          e.id.startsWith(`${idAloc}|`),
        );
        if (!noAloc || !arestaSaida) break;
        noAloc.data.status = ok("Enviado para B3");
        noAloc.data.metadata = { eventoEnvio: evento.informacoes };
        grafo.foco = [noAloc];
        active(arestaSaida, true);

        // if (!evento.informacoes.realocacao) break;

        // const nums = grafo.eventos.find(ev => ev.informacoes.tipo === 'emissao-numeros-controle')?.informacoes as EventoEmissaoNumerosControle | undefined
        // const qtd = nums?.quebras.find(q => q.numero_controle_nome)?.quantidade
        // if (!qtd) break;

        // const { fundo_nome } = evento.informacoes.realocacao

        // const posArestaSaida = grafo.edges.findIndex(e => e.id === arestaSaida.id)
        // if (posArestaSaida !== -1) {
        //     grafo.edges.splice(posArestaSaida, 1)
        // }

        // const idCustodiante = `cst-${ncn}-${numRealocacoes}`
        // const noCustodiante: No = {
        //     id: idCustodiante, type: 'company-in-out', position: makePos(),
        //     data: {
        //         label: 'Aprovação',
        //         details: React.createElement(React.Fragment, {
        //             children: [
        //                 React.createElement(Text, { fontWeight: 'bold', children: fundo_nome }),
        //                 React.createElement(Text, { children: 'Quantidade: ' + qtd }),
        //             ]
        //         }),
        //         company: custodiantes[fundo_nome] ?? { name: 'Não registrado no sistema' },
        //         status: aguardando()
        //     },
        // }

        // const idResumo = `resumo-${ncn}`
        // const noResumo = grafo.nodes.find(n => n.id === idResumo)
        // if (!noResumo) break;
        // atualizarResumo(noResumo, ncn ?? '', [...grafo.eventos, evento])

        // const e1: Edge = { id: `${idAloc}|${idCustodiante}`, source: idAloc, target: idCustodiante }
        // active(e1, true)
        // const e2: Edge = { id: `${idCustodiante}|${idResumo}`, source: idCustodiante, target: idResumo, animated: true }
        // grafo.nodes.push(noCustodiante)
        // grafo.edges.push(e1, e2)
      }
      break;

    case "erro-mensagem":
      {
        const ev = evento.informacoes;
        const noEnvio = grafo.nodes.find((n) => {
          return n.data.metadata?.eventoEnvio?.mensagem.id === ev.id_mensagem;
        });
        if (!noEnvio) break;
        const idNoErro = "erro-mensagem";
        const noErro: No = {
          id: idNoErro,
          type: "company-in-out",
          position: makePos(),
          data: {
            label: "Erro de processamento",
            details: React.createElement(React.Fragment, {
              children: [
                React.createElement(
                  Button,
                  {
                    size: "xs",
                    colorScheme: "rosa",
                    onClick: () => {
                      opcoes.abrirErro(ev.erro);
                    },
                  },
                  "Detalhes",
                ),
              ],
            }),
            company: companies.b3,
            status: recusado(),
          },
        };
        const indexSaidaAntiga = grafo.edges.findIndex((e) =>
          e.id.startsWith(noEnvio.id),
        );
        if (indexSaidaAntiga !== -1) {
          grafo.edges.splice(indexSaidaAntiga, 1);
        }
        grafo.edges.push({
          id: `${noEnvio.id}|${idNoErro}`,
          source: noEnvio.id,
          target: idNoErro,
          animated: false,
          style: { stroke: getColorHex("verde.main") },
        });
        grafo.edges.push({
          id: `${idNoErro}|emite-numeros-controle`,
          source: idNoErro,
          target: "emite-numeros-controle",
          animated: true,
        });
        grafo.nodes.push(noErro);
      }
      break;

    case "alocacao-contraparte":
      {
        const noAlocacaoContraparte = grafo.nodes.find(
          (n) => n.id === "alocacao-contraparte",
        );
        const arestaSaida = grafo.edges.find((e) =>
          e.id.startsWith("alocacao-contraparte|"),
        );
        if (!noAlocacaoContraparte || !arestaSaida) break;
        grafo.foco = [noAlocacaoContraparte];
        if (evento.informacoes.final) {
          noAlocacaoContraparte.data.status = ok("Alocação realizada");
          active(arestaSaida, true);
          break;
        }
        noAlocacaoContraparte.data.status = aguardando(
          "Aguardando confirmação",
        );
      }
      break;

    case "emissao-numeros-controle":
      {
        // const noEmiteNums = grafo.nodes.find(n => n.id === 'emite-numeros-controle')
        // if (!noEmiteNums) break;
        // noEmiteNums.data.status = ok('Números emitidos')
        // evento.informacoes.quebras.forEach(quebra => {
        //     const idNumControle = `num-NoMe-${quebra.numero_controle_nome}`
        //     const noNumControle: No = {
        //         id: idNumControle, type: 'company-in-out', position: makePos(),
        //         data: {
        //             label: 'Registro NoMe',
        //             details: quebra.numero_controle_nome,
        //             company: companies.b3,
        //             status: ok('')
        //         }
        //     }
        //     const idCustodiante = `cst-${quebra.numero_controle_nome}-0`
        //     const noCustodiante: No = {
        //         id: idCustodiante, type: 'company-in-out', position: makePos(),
        //         data: {
        //             label: 'Aprovação',
        //             details: React.createElement(React.Fragment, {
        //                 children: [
        //                     React.createElement(Text, { fontWeight: 'bold', children: quebra.fundo_nome }),
        //                     React.createElement(Text, { children: 'Quantidade: ' + quebra.quantidade }),
        //                 ]
        //             }),
        //             company: companies[quebra.custodiante.toLowerCase().split(' ')[0]]
        //                 ?? companies[quebra.custodiante.toLowerCase().split(' ')[1]]
        //                 ?? { name: 'Não registrado no sistema' },
        //             status: aguardando()
        //         },
        //     }
        //     const idCustodianteContraparte = `ctp-cst-${quebra.numero_controle_nome}`
        //     const noCustodianteContraparte: No = {
        //         id: idCustodianteContraparte, type: 'company-in-out', position: makePos(),
        //         data: {
        //             label: 'Aprovação',
        //             details: 'Quantidade: ' + quebra.quantidade,
        //             company: companies.custodiante_contraparte,
        //             status: aguardando()
        //         },
        //     }
        //     grafo.foco.push(noCustodiante, noCustodianteContraparte)
        //     const idResumo = `resumo-${quebra.numero_controle_nome}`
        //     const noResumo: No = {
        //         id: idResumo, type: 'in', position: makePos(),
        //         data: {
        //             label: 'Aguardando',
        //             status: { ...aguardando(), bgColor: 'cinza.100' }
        //         }
        //     }
        //     const arestaAlocacaoFinalNumControle: Edge = { id: `emite-numeros-controle|${idNumControle}`, source: 'emite-numeros-controle', target: idNumControle }
        //     active(arestaAlocacaoFinalNumControle, true)
        //     const arestaNumControleCustodiante: Edge = { id: `${idNumControle}|${idCustodiante}`, source: idNumControle, target: idCustodiante }
        //     active(arestaNumControleCustodiante, true)
        //     const arestaNumControleCustodianteContraparte: Edge = { id: `${idNumControle}|${idCustodianteContraparte}`, source: idNumControle, target: idCustodianteContraparte }
        //     active(arestaNumControleCustodianteContraparte, true)
        //     const arestaCustodianteResumo: Edge = { id: `${idCustodiante}|${idResumo}`, source: idCustodiante, target: idResumo, animated: true }
        //     const arestaCustodianteContraparteResumo: Edge = { id: `${idCustodianteContraparte}|${idResumo}`, source: idCustodianteContraparte, target: idResumo, animated: true }
        //     grafo.nodes.push(noNumControle, noCustodiante, noCustodianteContraparte, noResumo)
        //     grafo.edges.push(arestaAlocacaoFinalNumControle, arestaNumControleCustodianteContraparte, arestaNumControleCustodiante, arestaCustodianteContraparteResumo, arestaCustodianteResumo)
        // })
      }
      break;

    case "atualizacao-custodiante":
      {
        const ncn = evento.informacoes.registro_nome.numero_controle_nome;
        const sts = evento.informacoes.status;

        const ultimoIdCustodiante =
          grafo.nodes.filter((n) => n.id.startsWith(`cst-${ncn}`)).length - 1;

        const idNoAtualizacaoCst = `cst-${ncn}-${ultimoIdCustodiante}`;
        const idNoAtualizacaoCtpCst = `ctp-cst-${ncn}`;

        const noAtualizacaoCst = grafo.nodes.find(
          (n) => n.id === idNoAtualizacaoCst,
        );
        const noAtualizacaoCtpCst = grafo.nodes.find(
          (n) => n.id === idNoAtualizacaoCtpCst,
        );
        const arestaSaidaAtualizacaoCst = grafo.edges.find((e) =>
          e.id.startsWith(`${idNoAtualizacaoCst}|`),
        );
        const arestaSaidaAtualizacaoCtpCst = grafo.edges.find((e) =>
          e.id.startsWith(`${idNoAtualizacaoCtpCst}|`),
        );
        if (
          !noAtualizacaoCst ||
          !arestaSaidaAtualizacaoCst ||
          !noAtualizacaoCtpCst ||
          !arestaSaidaAtualizacaoCtpCst
        )
          break;

        grafo.foco = [noAtualizacaoCst, noAtualizacaoCtpCst];

        const noResumo = grafo.nodes.find((n) => n.id === `resumo-${ncn}`);
        if (!noResumo) break;

        let noFoco: No | undefined;
        let arestaFoco: Edge | undefined;
        let noSecundario: No | undefined;
        let arestaSecundario: Edge | undefined;
        status: switch (sts) {
          case AlocacaoStatus.Pendente_Confirmação_Custodiante:
            break status;
          case AlocacaoStatus.Pendente_Confirmação_Contraparte_Custodiante:
          case AlocacaoStatus.Confirmado_pelo_Custodiante:
            {
              noAtualizacaoCst.data.status = ok("Aprovado");
              active(arestaSaidaAtualizacaoCst, true);
            }
            break status;
          case AlocacaoStatus.Disponível_para_Registro:
            {
              noAtualizacaoCst.data.status = ok("Aprovado");
              active(arestaSaidaAtualizacaoCst, true);
              noAtualizacaoCtpCst.data.status = ok("Aprovado");
              active(arestaSaidaAtualizacaoCtpCst, true);
            }
            break status;
          case AlocacaoStatus.Rejeitado_pelo_Custodiante:
            noFoco ??= noAtualizacaoCst;
            arestaFoco ??= arestaSaidaAtualizacaoCst;
            noSecundario ??= noAtualizacaoCtpCst;
            arestaSecundario ??= arestaSaidaAtualizacaoCtpCst;
          case AlocacaoStatus.Rejeitado_pela_Contraparte_Custodiante:
            noFoco ??= noAtualizacaoCtpCst;
            arestaFoco ??= arestaSaidaAtualizacaoCtpCst;
            noSecundario ??= noAtualizacaoCst;
            arestaSecundario ??= arestaSaidaAtualizacaoCst;
            {
              noFoco.data.status = recusado("Recusado");
              arestaFoco.animated = false;
              arestaFoco.style = { stroke: getColorHex("rosa.main") };
              noSecundario.data.status = {
                ...aguardando("Aprovação descartada"),
                bgColor: "cinza.main",
              };
              active(arestaSecundario, false);

              const prefixoAlocacao = `aloc-op-${ncn}`;
              const novoNumAlocacao = grafo.nodes.filter((n) =>
                n.id.startsWith(`${prefixoAlocacao}-`),
              ).length;
              const novoIdAlocacao = `${prefixoAlocacao}-${novoNumAlocacao}`;
              const novoPedidoAlocacaoInterno: No = {
                id: novoIdAlocacao,
                type: "company-in-out",
                position: makePos(),
                data: {
                  label: "Realocação interna",
                  company: companies.vanguarda,
                  status: { ...aguardando(), pending: true },
                  details: React.createElement(HStack, {
                    fontSize: "xs",
                    fontWeight: "thin",
                    justifyContent: "space-between",
                    alignItems: "flex-end",
                    flex: 1,
                    children: [
                      React.createElement(HStack),
                      React.createElement(Button, {
                        isDisabled: Boolean(passado),
                        colorScheme: "verde",
                        onClick: () => {
                          if (
                            evento.informacoes.tipo !==
                            "atualizacao-custodiante"
                          )
                            return;
                          opcoes.abrirMenuAlocacao(
                            "custodiante",
                            evento.informacoes.registro_nome.id,
                          );
                        },
                        size: "xs",
                        leftIcon: React.createElement(IoDocumentText),
                        children: ["Realocar"],
                      }),
                    ],
                  }),
                },
              };
              const prefixoAprovacao = `ap-bo-${ncn}`;
              const aprovacoes = grafo.nodes.filter((n) =>
                n.id.startsWith(`${prefixoAprovacao}-`),
              );
              const numAprovacao = aprovacoes.length;
              const novoIdAprovacao = `${prefixoAprovacao}-${numAprovacao}`;
              const novaAprovacaoBackoffice: No = {
                id: novoIdAprovacao,
                type: "company-in-out",
                position: makePos(),
                data: {
                  label: "Aprovação Backoffice",
                  company: companies.vanguarda,
                  status: aguardando(),
                },
              };

              const novoIdEnvioRealocacao = `envio-realocacao-${ncn}-${numAprovacao}`;
              const novoEnvioRealocacao: No = {
                id: novoIdEnvioRealocacao,
                type: "company-in-out",
                position: makePos(),
                data: {
                  label: "Sistema envia pedido de realocação",
                  company: companies.vanguarda,
                  status: aguardando(),
                },
              };

              const e1: Edge = {
                id: `${noFoco.id}|${novoIdAlocacao}`,
                source: noFoco.id,
                target: novoIdAlocacao,
                animated: false,
                style: { stroke: getColorHex("rosa.main") },
              };
              const e2: Edge = {
                id: `${novoIdAlocacao}|${novoIdAprovacao}`,
                source: novoIdAlocacao,
                target: novoIdAprovacao,
                animated: true,
              };
              const e3: Edge = {
                id: `${novoIdAprovacao}|${novoIdEnvioRealocacao}`,
                source: novoIdAprovacao,
                target: novoIdEnvioRealocacao,
                animated: true,
              };
              const e4: Edge = {
                id: `${novoIdEnvioRealocacao}|resumo-${ncn}`,
                source: novoIdEnvioRealocacao,
                target: `resumo-${ncn}`,
                animated: true,
              };

              const indexSaidaAntiga = grafo.edges.findIndex(
                (e) => e.id === arestaFoco?.id,
              );
              if (indexSaidaAntiga !== -1) {
                grafo.edges.splice(indexSaidaAntiga, 1);
              }
              grafo.nodes.push(
                novoPedidoAlocacaoInterno,
                novaAprovacaoBackoffice,
                novoEnvioRealocacao,
              );
              grafo.edges.push(e1, e2, e3, e4);
            }
            break status;
          default:
            break status;
        }
      }
      break;

    default:
      return;
  }
  grafo.eventos.push(evento);
}

const atualizarResumo = (
  noResumo: No,
  ncn: string,
  eventos: EventoOperacao[],
) => {
  // const ultimoStatusCust = eventos
  //     .filter(ev => (ev.informacoes.tipo === 'atualizacao-custodiante' && ev.informacoes.numero_controle_nome === ncn && ev.informacoes.custodiante !== undefined)
  //         || (ev.informacoes.tipo === 'envio-alocacao' && ev.informacoes.mensagem.registro_nome?.numero_controle_nome === ncn)
  //     )
  //     .map(ev => (ev.informacoes as { status?: number }))
  //     .at(-1)?.status ?? 0
  // const ultimoStatusCustContraparte = eventos
  //     .filter(ev => ev.informacoes.tipo === 'atualizacao-custodiante' && ev.informacoes.numero_controle_nome === ncn && !ev.informacoes.custodiante)
  //     .map(ev => (ev.informacoes as EventoAtualizacaoCustodiante).status)
  //     .at(-1) ?? 0
  // noResumo.data.status = resumo(ultimoStatusCust, ultimoStatusCustContraparte)
};

const resumo = (stsCust: number, stsCustCtp: number) => {
  if (stsCust === 0 && (stsCustCtp === 0 || stsCustCtp === 1))
    return { ...aguardando("Aguardando Custodiante"), bgColor: "cinza.100" };
  if ((stsCust === 0 || stsCust === 1) && stsCustCtp === 2)
    return {
      ...aguardando("Aguardando Realocação Contraparte"),
      bgColor: "cinza.100",
    };
  if (stsCust === 1 && stsCustCtp === 0)
    return {
      ...aguardando("Aguardando Custodiante Contraparte"),
      bgColor: "cinza.100",
    };
  if (stsCust === 1 && stsCustCtp === 1)
    return { ...ok("Encaminhado para liquidação"), bgColor: "verde.100" };
  if (stsCust === 2)
    return { ...recusado("Pendente envio de realocação"), bgColor: "rosa.100" };
  return { ...aguardando(), bgColor: "cinza.100" };
};

export function construirGrafoAPartirDeEventos(
  eventos: EventoOperacao[],
  passado: boolean,
  opcoes: GrafoCallbacks,
): Grafo {
  const eventos_processados: EventoOperacao[] = [];
  const nodes: No[] = [
    {
      id: "ac-voice",
      type: "company-out",
      position: makePos(),
      data: {
        label: "Acato Voice",
        company: companies.vanguarda,
        status: { ...aguardando(), pending: true },
      },
    },
    {
      id: "aloc-op-inicial-0",
      type: "company-out",
      position: makePos(),
      data: {
        label: "Alocação interna",
        company: companies.vanguarda,
        status: { ...aguardando(), pending: true },
      },
    },
    {
      id: "ap-bo-inicial-0",
      type: "company-in-out",
      position: makePos(),
      data: {
        label: "Aprovação Backoffice",
        company: companies.vanguarda,
        status: aguardando(),
      },
    },
    {
      id: "envio-alocacao-final",
      type: "company-in-out",
      position: makePos(),
      data: {
        label: "Sistema envia alocação final",
        company: companies.vanguarda,
        status: aguardando(),
      },
    },
    {
      id: "alocacao-contraparte",
      type: "company-out",
      position: makePos(),
      data: {
        label: "Alocação final",
        company: companies.contraparte,
        status: aguardando(),
      },
    },
    {
      id: "emite-numeros-controle",
      type: "company-in-out",
      position: makePos(),
      data: {
        label: "Emite números de controle do NoMe",
        company: companies.b3,
        status: aguardando(),
      },
    },
  ];
  const edges: Edge[] = [
    {
      id: "ac-voice|envio-alocacao-final",
      source: "ac-voice",
      target: "envio-alocacao-final",
      animated: true,
    },
    {
      id: "aloc-op-inicial-0|ap-bo-inicial-0",
      source: "aloc-op-inicial-0",
      target: "ap-bo-inicial-0",
      animated: true,
    },
    {
      id: "ap-bo-inicial-0|envio-alocacao-final",
      source: "ap-bo-inicial-0",
      target: "envio-alocacao-final",
      animated: true,
    },
    {
      id: "envio-alocacao-final|emite-numeros-controle",
      source: "envio-alocacao-final",
      target: "emite-numeros-controle",
      animated: true,
    },
    {
      id: "alocacao-contraparte|emite-numeros-controle",
      source: "alocacao-contraparte",
      target: "emite-numeros-controle",
      animated: true,
    },
  ];
  const grafo = { eventos: eventos_processados, nodes, edges, foco: [] };
  for (const evento of eventos) {
    alterarGrafoAPartirDeEventos(grafo, evento, passado, opcoes);
  }
  return grafo;
}

export function construirTabelaAPartirDeEventos(
  eventos: EventoOperacao[],
): QuebraRTC[] {
  const quebras: QuebraRTC[] = [];
  for (const evento of eventos) {
    if (
      evento.informacoes.tipo === "alocacao-operador" &&
      evento.informacoes.operacao.registro_nome === null
    ) {
      quebras.splice(0, quebras.length);
      for (const quebra of evento.informacoes.operacao.alocacoes) {
        quebras.push({
          custodiante: quebra.fundo.nome_custodiante,
          fundo_nome: quebra.fundo.nome,
          hora: evento.criado_em,
          quantidade: quebra.quantidade,
        });
      }
    } else if (evento.informacoes.tipo === "emissao-numeros-controle") {
      quebras.splice(0, quebras.length);
      // quebras.push(...structuredClone(evento.informacoes.quebras))
    } else if (evento.informacoes.tipo === "atualizacao-custodiante") {
      // const ncn = evento.informacoes.numero_controle_nome
      // const realocacoes = quebras.filter(q => q.numero_controle_nome === ncn)
      // if (!realocacoes.length) continue;
      // if (evento.informacoes.custodiante) {
      //     realocacoes[realocacoes.length - 1].status_custodiante = evento.informacoes.status
      //     continue
      // }
      // for (const realocacao of realocacoes) {
      //     realocacao.status_custodiante_contraparte = evento.informacoes.status
      // }
    } else if (
      evento.informacoes.tipo === "alocacao-operador" &&
      evento.informacoes.operacao.registro_nome
    ) {
      const info = evento.informacoes;
      if (info.operacao.alocacoes.length !== 1) continue;
      const ncn = info.operacao.registro_nome;
      const anterior = quebras.find((q) => q.numero_controle_nome === ncn);
      if (!anterior) continue;
      quebras.push({
        ...anterior,
        custodiante: info.operacao.alocacoes[0].fundo.nome_custodiante,
        fundo_nome: info.operacao.alocacoes[0].fundo.nome,
        hora: evento.criado_em,
        status_custodiante: undefined,
      });
    } /*else if (evento.informacoes.tipo === 'envio-alocacao' && evento.informacoes.realocacao) {
            const ncn = evento.informacoes.realocacao.numero_controle_nome
            const ultimaAlocacao = quebras.findLast(q => q.numero_controle_nome === ncn)
            if (!ultimaAlocacao) continue;
            ultimaAlocacao.status_custodiante = 0
        }*/
  }
  return quebras;
}
