import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { ResultadoBuscaBoleta_Alocacao } from "@/lib/types/api/iv/operacoes/processamento";
import { fmtCETIP, fmtDate, fmtCNPJ } from "@/lib/util/string";
import { Box, Divider, HStack, Text, VStack } from "@chakra-ui/react";
import { banner } from "../../tabs/triagem-b3/fluxo/dados/companies";
import AcaoUsuario from "./AcaoUsuario";
import LinhaFluxoII from "./LinhaFluxoII";
import { ehFluxoII } from "@/lib/util/operacoes";
import { AlocacaoComInfosDaBoleta } from "@/lib/providers/AlocacoesProvider";

const dropShadow = {
  borderRadius: "8px",
  p: "8px",
  boxShadow: "0px 0px 4px lightgray",
};

export type ModalAlocacaoProps = {
  alocacao: AlocacaoComInfosDaBoleta | null;
  onClose: () => void;
};

export default function ModalAlocacao({
  alocacao,
  onClose,
}: ModalAlocacaoProps) {
  if (!alocacao) {
    return <></>;
  }

  const envios_pre_trade = alocacao.casamento?.voice.envios_pre_trade.sort(
    (a, b) => a.enviado_em.localeCompare(b.enviado_em),
  );
  const envios_post_trade = alocacao.casamento?.voice.envios_post_trade.sort(
    (a, b) => a.enviado_em.localeCompare(b.enviado_em),
  );
  const sucesso = envios_post_trade?.find((e) => e.sucesso_em)?.sucesso_em;

  return (
    <ConfirmModal
      isOpen={true}
      onClose={onClose}
      title="Detalhes da alocação"
      cancelContent="Fechar"
      hideConfirmButton
      size="6xl"
    >
      <HStack alignItems="stretch">
        <VStack w="256px" h="72.5vh" alignItems="stretch" p="4px">
          <VStack {...dropShadow} alignItems="stretch">
            <HStack justifyContent="space-between">
              <Text fontSize="13px" fontWeight="600">
                {alocacao.codigo_ativo}
              </Text>
              <Text
                border="2px solid"
                borderRadius="8px"
                borderColor={
                  alocacao.vanguarda_compra ? "azul_3.main" : "rosa.main"
                }
                color={alocacao.vanguarda_compra ? "azul_3.main" : "rosa.main"}
                p="0 2px"
                fontWeight="900"
                fontSize="10px"
              >
                {alocacao.vanguarda_compra ? "COMPRA" : "VENDA"}
              </Text>
            </HStack>
            <Divider />
            <VStack alignItems="stretch" fontSize="xs" gap={0}>
              <HStack justifyContent="space-between">
                <Text>Negociado em:</Text>
                <Text>{fmtDate(alocacao.data_negociacao)}</Text>
              </HStack>
              <HStack justifyContent="space-between">
                <Text>Data de liquidação:</Text>
                <Text>{fmtDate(alocacao.data_liquidacao)}</Text>
              </HStack>
            </VStack>
            <Divider />
            <VStack alignItems="stretch" fontSize="xs" gap={0}>
              <HStack justifyContent="space-between">
                <Text>Preço unitário:</Text>
                <Text>
                  R${" "}
                  {Number(alocacao.preco_unitario).toLocaleString("pt-BR", {
                    minimumFractionDigits: 8,
                    maximumFractionDigits: 8,
                  })}
                </Text>
              </HStack>
              <HStack justifyContent="space-between">
                <Text>Quantidade:</Text>
                <Text>
                  {Number(alocacao.quantidade).toLocaleString("pt-BR", {
                    maximumFractionDigits: 8,
                  })}
                </Text>
              </HStack>
              <HStack justifyContent="space-between">
                <Text>Total:</Text>
                <Text>
                  R${" "}
                  {(
                    Number(alocacao.preco_unitario) *
                    Number(alocacao.quantidade)
                  ).toLocaleString("pt-BR", {
                    minimumFractionDigits: 8,
                    maximumFractionDigits: 8,
                  })}
                </Text>
              </HStack>
            </VStack>
          </VStack>
          <VStack {...dropShadow} alignItems="stretch" flex={1}>
            <Text fontWeight="600" fontSize="xs">
              {alocacao.fundo.nome}
            </Text>
            <Divider />
            <VStack alignItems="stretch" fontSize="xs" gap={0}>
              <HStack justifyContent="space-between">
                <Text>Administrador</Text>
                {banner(alocacao.fundo.administrador?.nome ?? "", 16, 16, {
                  hstackProps: { alignItems: "center", gap: "4px" },
                  textProps: {
                    fontSize: "xs",
                  },
                })}
              </HStack>
              <HStack justifyContent="space-between">
                <Text>CNPJ:</Text>
                <Text>{fmtCNPJ(alocacao.fundo.cnpj)}</Text>
              </HStack>
              <HStack justifyContent="space-between">
                <Text>Conta CETIP:</Text>
                <Text>{fmtCETIP(alocacao.fundo.conta_cetip)}</Text>
              </HStack>
              <HStack justifyContent="space-between">
                <Text>ID Sistema Vanguarda:</Text>
                <Text>{alocacao.fundo.id}</Text>
              </HStack>
            </VStack>
          </VStack>
        </VStack>
        <VStack
          flex={1}
          h="72.5vh"
          alignItems="stretch"
          overflow="hidden"
          p="4px"
        >
          <HStack alignItems="stretch">
            <VStack flex={1} {...dropShadow} alignItems="stretch">
              <Text fontSize="sm" fontWeight="600">
                Alocação interna
              </Text>
              <Divider />
              {alocacao.alocacao_usuario && alocacao.alocado_em ? (
                <AcaoUsuario
                  usuario={{
                    nome: alocacao.alocacao_usuario,
                    email: "---",
                  }}
                  horario={alocacao.alocado_em}
                />
              ) : (
                <Text fontSize="xs" color="cinza.500">
                  Pendente alocação interna
                </Text>
              )}
            </VStack>
            <VStack flex={1} {...dropShadow} alignItems="stretch">
              <Text fontSize="sm" fontWeight="600">
                Aprovação interna
              </Text>
              <Divider />
              {alocacao.aprovacao_usuario && alocacao.aprovado_em ? (
                <AcaoUsuario
                  usuario={{
                    nome: alocacao.aprovacao_usuario,
                    email: "---",
                  }}
                  horario={alocacao.aprovado_em}
                />
              ) : (
                <Text fontSize="xs" color="cinza.500">
                  Pendente aprovação interna
                </Text>
              )}
            </VStack>
            <VStack flex={1} {...dropShadow} alignItems="stretch">
              <Text fontSize="sm" fontWeight="600">
                Solicitação cancelamento
              </Text>
              <Divider />
              {alocacao.cancelamento ? (
                <VStack alignItems="stretch">
                  <AcaoUsuario
                    usuario={{
                      nome: "Usuário ID " + alocacao.cancelamento.usuario_id,
                      email: "---",
                    }}
                    horario={alocacao.cancelamento.cancelado_em}
                  />
                  <Divider />
                  <Text fontSize="xs">
                    <Text as="span" fontWeight="bold">
                      Motivo:
                    </Text>{" "}
                    {alocacao.cancelamento.motivo || "Não informado"}
                  </Text>
                </VStack>
              ) : (
                <Text fontSize="xs" color="cinza.500">
                  Não há solicitação de cancelamento
                </Text>
              )}
            </VStack>
          </HStack>
          {!ehFluxoII(alocacao.tipo_ativo_id, alocacao.mercado_negociado_id) ? (
            <Box flex={1} />
          ) : (
            <VStack
              flex={1}
              {...dropShadow}
              alignItems="stretch"
              overflowY="scroll"
            >
              <VStack
                position="sticky"
                top={0}
                alignItems="stretch"
                bgColor="white"
              >
                <Text fontSize="sm" fontWeight="600">
                  Fluxo II
                </Text>
                <Divider />
              </VStack>
              <VStack fontSize="xs" alignItems="stretch">
                {alocacao.alocacao_anterior_id ? (
                  <>
                    <Text
                      textAlign="center"
                      color="laranja.main"
                      p="16px"
                      bgColor="amarelo.50"
                      borderRadius="8px"
                    >
                      As informações anteriores às quebras podem ser consultadas
                      na alocação original
                    </Text>
                    <Divider />
                  </>
                ) : (
                  <>
                    <LinhaFluxoII
                      titulo="Casamento Voice"
                      informacoes={
                        alocacao.casamento
                          ? {
                              cor: "verde.100",
                              texto:
                                "ID Voice: " +
                                alocacao.casamento.voice.id_trader,
                              horario: alocacao.casamento.casado_em,
                            }
                          : undefined
                      }
                    />
                    <VStack {...dropShadow} alignItems="stretch" p="8px">
                      <Text>Tentativas de acato do voice</Text>
                      <Divider />
                      {envios_pre_trade?.length ? (
                        envios_pre_trade.map((e, i) => (
                          <LinhaFluxoII
                            key={e.id + "-pos"}
                            titulo={`${i + 1}º envio`}
                            informacoes={
                              envios_pre_trade.length
                                ? {
                                    cor: e.erro ? "rosa.100" : "cinza.100",
                                    texto: e.erro || "Enviado",
                                    horario: e.enviado_em,
                                  }
                                : undefined
                            }
                          />
                        ))
                      ) : (
                        <Text color="cinza.500">Não há acatos</Text>
                      )}
                    </VStack>
                    <LinhaFluxoII
                      titulo="Informações para alocação"
                      informacoes={
                        alocacao.casamento?.voice.horario_recebimento_post_trade
                          ? {
                              cor: "verde.100",
                              texto: "Recebidas",
                              horario:
                                alocacao.casamento.voice
                                  .horario_recebimento_post_trade,
                            }
                          : undefined
                      }
                    />
                    <VStack {...dropShadow} alignItems="stretch" p="8px">
                      <Text>Tentativas de alocação na [B]³</Text>
                      <Divider />
                      {envios_post_trade?.length ? (
                        envios_post_trade.map((e, i) => (
                          <LinhaFluxoII
                            titulo={`${i + 1}º envio`}
                            informacoes={{
                              cor: e.erro
                                ? "rosa.100"
                                : e.sucesso_em
                                  ? "verde.100"
                                  : "cinza.100",
                              texto:
                                e.erro ||
                                (e.sucesso_em ? "Sucesso" : "Enviado"),
                              horario: e.enviado_em,
                            }}
                          />
                        ))
                      ) : (
                        <Text color="cinza.500">Não há envios</Text>
                      )}
                    </VStack>
                    <LinhaFluxoII
                      titulo="Confirmação das alocações"
                      informacoes={
                        sucesso
                          ? {
                              cor: "verde.100",
                              texto: "Alocado",
                              horario: sucesso,
                            }
                          : undefined
                      }
                    />
                    <LinhaFluxoII
                      titulo="Alocação contraparte"
                      informacoes={
                        alocacao.registro_NoMe || alocacao.quebras.length
                          ? {
                              cor: "verde.100",
                              texto: "Alocado",
                              horario:
                                alocacao.registro_NoMe?.recebido_em ||
                                alocacao.quebras[0].alocado_em,
                            }
                          : undefined
                      }
                    />
                  </>
                )}
                <LinhaFluxoII
                  titulo="Emissão registros depositária"
                  informacoes={
                    alocacao.registro_NoMe || alocacao.quebras.length
                      ? {
                          cor: alocacao.quebras.length
                            ? "rosa.100"
                            : "verde.100",
                          texto: alocacao.quebras.length
                            ? "Quebra na alocação"
                            : `Registro ${alocacao.registro_NoMe?.numero_controle} emitido`,
                          horario:
                            alocacao.registro_NoMe?.recebido_em ||
                            alocacao.quebras[0].alocado_em,
                        }
                      : undefined
                  }
                />
                {alocacao.quebras.length ? (
                  <>
                    <Divider />
                    <Text
                      textAlign="center"
                      color="rosa.main"
                      p="16px"
                      bgColor="rosa.50"
                      borderRadius="8px"
                    >
                      {alocacao.quebras.length} registros foram emitidos.
                      Acompanhe o progresso pelas outras alocações
                    </Text>
                  </>
                ) : (
                  <>
                    <LinhaFluxoII
                      titulo="Posicionamento custódia"
                      informacoes={
                        alocacao.registro_NoMe &&
                        alocacao.registro_NoMe.posicao_custodia_em
                          ? {
                              cor: alocacao.registro_NoMe.posicao_custodia
                                ? "verde.100"
                                : "rosa.100",
                              texto: alocacao.registro_NoMe.posicao_custodia
                                ? "Aprovado"
                                : "Rejeitado",
                              horario:
                                alocacao.registro_NoMe.posicao_custodia_em,
                            }
                          : undefined
                      }
                    />
                    <LinhaFluxoII
                      titulo="Posicionamento custódia contraparte"
                      informacoes={
                        alocacao.registro_NoMe &&
                        alocacao.registro_NoMe.posicao_custodia_contraparte_em
                          ? {
                              cor: alocacao.registro_NoMe
                                .posicao_custodia_contraparte
                                ? "verde.100"
                                : "rosa.100",
                              texto: alocacao.registro_NoMe
                                .posicao_custodia_contraparte
                                ? "Aprovado"
                                : "Rejeitado",
                              horario:
                                alocacao.registro_NoMe
                                  .posicao_custodia_contraparte_em,
                            }
                          : undefined
                      }
                    />
                  </>
                )}
              </VStack>
            </VStack>
          )}
          <HStack alignItems="stretch">
            <VStack flex={1} {...dropShadow} alignItems="stretch">
              <Text fontSize="sm" fontWeight="600">
                Alocação no administrador
              </Text>
              <Divider />
              {alocacao.alocacao_administrador ? (
                <AcaoUsuario
                  usuario={{
                    nome:
                      "Usuário ID " +
                      alocacao.alocacao_administrador.alocacao_usuario_id,
                    email: "---",
                  }}
                  horario={alocacao.alocacao_administrador.alocado_em}
                />
              ) : (
                <Text fontSize="xs" color="cinza.500">
                  Pendente alocação no administrador
                </Text>
              )}
            </VStack>
            <VStack
              flex={1}
              {...dropShadow}
              alignItems="stretch"
              visibility={
                alocacao.alocacao_administrador ? "visible" : "hidden"
              }
            >
              <Text fontSize="sm" fontWeight="600">
                Liquidação
              </Text>
              <Divider />
              {alocacao.alocacao_administrador?.liquidacao ? (
                <AcaoUsuario
                  usuario={{
                    nome:
                      "Usuário ID " +
                      alocacao.alocacao_administrador.liquidacao.usuario_id,
                    email: "---",
                  }}
                  horario={new Date(Date.now()).toISOString()}
                />
              ) : (
                <Text fontSize="xs" color="cinza.500">
                  Aguardando sinalização de liquidação
                </Text>
              )}
            </VStack>
            <VStack
              flex={1}
              {...dropShadow}
              alignItems="stretch"
              visibility={
                alocacao.alocacao_administrador ? "visible" : "hidden"
              }
            >
              <Text fontSize="sm" fontWeight="600">
                Cancelamento no administrador
              </Text>
              <Divider />
              {alocacao.alocacao_administrador?.cancelamento ? (
                <VStack alignItems="stretch">
                  <AcaoUsuario
                    usuario={{
                      nome:
                        "Usuário ID " +
                        alocacao.alocacao_administrador.cancelamento.usuario_id,
                      email: "---",
                    }}
                    horario={new Date(Date.now()).toISOString()}
                  />
                  <Divider />
                  <Text fontSize="xs">
                    <Text as="span" fontWeight="bold">
                      Motivo:
                    </Text>{" "}
                    {alocacao.alocacao_administrador.cancelamento.motivo ||
                      "Não informado"}
                  </Text>
                </VStack>
              ) : (
                <Text fontSize="xs" color="cinza.500">
                  Não há sinalização de cancelamento no administrador
                </Text>
              )}
            </VStack>
          </HStack>
        </VStack>
        {/* <VStack w='240px' h='72.5vh' {...dropShadow}>
                <Text fontSize='sm' fontWeight='600'>Eventos</Text>
                <Divider />
            </VStack> */}
      </HStack>
    </ConfirmModal>
  );
}
