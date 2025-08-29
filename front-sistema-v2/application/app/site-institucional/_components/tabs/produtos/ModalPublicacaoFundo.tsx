import Comment from "@/app/_components/misc/Comment";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { useAsync, useHTTP } from "@/lib/hooks";
import { fmtDate, fmtDatetime } from "@/lib/util/string";
import { useEffect, useRef, useState } from "react";
import {
  InputTextoPadrao,
  InputReadOnlyTextoPadrao,
} from "./_components/InputTextoPadrao";
import { SelectPadrao, SelectReadOnlyPadrao } from "./_components/SelectPadrao";
import {
  SelectDinamico,
  SelectDinamicoReadOnly,
} from "./_components/SelectDinamico";
import {
  IoArrowForward,
  IoCalendarOutline,
  IoDocumentOutline,
  IoEyeOffOutline,
  IoGlobeOutline,
  IoTimeOutline,
  IoWarning,
} from "react-icons/io5";
import {
  Fundo,
  FundoCaracteristicaExtra,
  FundoDetalhes,
  FundoDetalhesSiteInstitucional,
  FundoSiteInstitucionalClassificacao,
  FundoSiteInstitucionalTipo,
  IndiceBenchmark,
  Mesa,
} from "@/lib/types/api/iv/v1";
import {
  Button,
  Card,
  CardBody,
  CardHeader,
  Checkbox,
  Divider,
  HStack,
  Icon,
  Progress,
  Switch,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  VStack,
} from "@chakra-ui/react";
import { SelectOption } from "@/lib/types/api/iv/sistema";
import { MultiSelect, MultiSelectReadOnly } from "./_components/MultiSelect";

type _FundoDetalhesSiteInstitucional = Omit<
  FundoDetalhesSiteInstitucional,
  | "cnpj"
  | "tipo"
  | "mesa"
  | "publico_alvo"
  | "indices_benchmark"
  | "caracteristicas_extras"
  | "benchmark"
> & {
  classificacao_id: number | null;
  tipo_id: number | null;
  mesa_id: number | null;
  caracteristicas_extras_ids: number[];
  indices_benchmark_ids: number[];
};
type _FundoDetalhes = Omit<FundoDetalhes, "indices"> & {
  indices: IndiceBenchmark[];
};

enum OperacaoEnum {
  Publicacao,
  Despublicacao,
  Atualizacao,
}

export type ModalPublicacaoFundoProps = {
  fundo?: Fundo;
  setFundo: (fundo: Fundo | undefined) => void;
  mesas: Mesa[];
  classificacoes: FundoSiteInstitucionalClassificacao[];
  tipos: FundoSiteInstitucionalTipo[];
  caracteristicasExtras: FundoCaracteristicaExtra[];
  indicesBenchmark: IndiceBenchmark[];
  onFundosUpdateCallback: () => Promise<void>;
};

export default function ModalPublicacaoFundo({
  fundo,
  setFundo,
  mesas,
  classificacoes,
  tipos,
  caracteristicasExtras,
  indicesBenchmark,
  onFundosUpdateCallback,
}: ModalPublicacaoFundoProps) {
  const [isFundoPublicado, setIsFundoPublicado] = useState<boolean>(
    fundo?.publicado ?? false,
  );
  const [isSwitchPublicacaoOn, setIsSwitchPublicacaoOn] = useState<boolean>(
    fundo?.publicado ?? false,
  );
  const [
    areCamposObrigatoriosPreenchidos,
    setAreCamposObrigatoriosPreenchidos,
  ] = useState<boolean>(false);
  const [isModalConfirmacaoOpen, setIsModalConfirmacaoOpen] =
    useState<boolean>(false);
  const [textoModalConfirmacao, setTextoModalConfirmacao] =
    useState<string>("");
  const [operacao, setOperacao] = useState<OperacaoEnum | null>(null);

  const httpClient = useHTTP({ withCredentials: true });
  const [carregandoFundo, carregarFundo] = useAsync();
  const [salvando, salvar] = useAsync();

  const [fundoDetalhes, setFundoDetalhes] = useState<_FundoDetalhes>();
  const [fundoDetalhesSiteInstitucional, setFundoDetalhesSiteInstitucional] =
    useState<_FundoDetalhesSiteInstitucional>(
      fundoDetalhesSiteInstitucionalInitialState,
    );
  const [documentosSelecionadosIds, setDocumentosSelecionadosIds] = useState<
    number[]
  >([]);

  const documentosPublicadosIdsRef = useRef<number[]>([]);
  const caracteristicasExtrasIniciaisIdsRef = useRef<number[]>([]);
  const indicesBenchmarkIniciaisIdsRef = useRef<number[]>([]);

  const optionsMesas: SelectOption[] = mesas.map((mesa) => {
    return {
      label: mesa.nome,
      value: mesa.id,
    } as SelectOption;
  });
  const optionsClassificacoes: SelectOption[] = classificacoes.map(
    (classificacao) => {
      return {
        label: classificacao.nome,
        value: classificacao.id,
      } as SelectOption;
    },
  );
  const optionsTipos: SelectOption[] = tipos.map((tipo) => {
    return {
      label: tipo.nome,
      value: tipo.id,
    } as SelectOption;
  });
  const optionsPublicoAlvo: SelectOption[] = Object.entries(publicoAlvo).map(
    ([objectKey, objValue]) => {
      return {
        label: objValue,
        value: objectKey,
      } as SelectOption;
    },
  );
  const optionsIndicesBenchmarkIds: SelectOption[] = indicesBenchmark.map(
    (indiceBenchmark) => {
      return {
        label: indiceBenchmark.nome,
        value: indiceBenchmark.id,
      } as SelectOption;
    },
  );
  const optionsCaracteristicasExtras: SelectOption[] =
    caracteristicasExtras.map((caracteristicaExtra) => {
      return {
        label: caracteristicaExtra.nome,
        value: caracteristicaExtra.id,
      } as SelectOption;
    });

  const publicaFundo = (requestBody: object) => {
    salvar(async () => {
      const response = await httpClient.fetch("v1/fundos/institucionais", {
        method: "POST",
        body: JSON.stringify(getObjComNullsDeUndefineds(requestBody)),
      });
      if (!response.ok) {
        return;
      }

      await onFundosUpdateCallback();
      setIsModalConfirmacaoOpen(false);
      setFundo(undefined);
      return;
    });
  };

  const atualizaInfosPublicas = (
    siteInstitucionalFundoId: number,
    requestBody: object,
  ) => {
    salvar(async () => {
      const response = await httpClient.fetch(
        `v1/fundos/institucionais/${siteInstitucionalFundoId}`,
        {
          method: "PATCH",
          body: JSON.stringify(requestBody),
        },
      );
      if (!response.ok) {
        return;
      }

      await onFundosUpdateCallback();
      setIsModalConfirmacaoOpen(false);
      setFundo(undefined);
      return;
    });
  };

  const despublicaFundo = (siteInstitucionalFundoId: number) => {
    salvar(async () => {
      const response = await httpClient.fetch(
        `v1/fundos/institucionais/${siteInstitucionalFundoId}`,
        {
          method: "DELETE",
        },
      );
      if (!response.ok) {
        return;
      }

      await onFundosUpdateCallback();
      setIsModalConfirmacaoOpen(false);
      setFundo(undefined);
      return;
    });
  };

  const carregaDetalhesEInfosPublicas = (fundo_id: number) => {
    if (carregandoFundo) {
      return;
    }

    carregarFundo(async () => {
      const response = await httpClient.fetch("v1/fundos/" + fundo_id);
      if (!response.ok) {
        return;
      }

      const responseJSON = (await response.json()) as _FundoDetalhes;
      setFundoDetalhes(responseJSON);

      const _isFundoPublicado = !!fundo?.publicado;
      setIsFundoPublicado(_isFundoPublicado);
      setIsSwitchPublicacaoOn(_isFundoPublicado);

      if (!_isFundoPublicado || !responseJSON?.detalhes_infos_publicas) {
        setFundoDetalhesSiteInstitucional(
          fundoDetalhesSiteInstitucionalInitialState,
        );

        return;
      }

      const detalhesInfosPublicas = responseJSON.detalhes_infos_publicas;
      caracteristicasExtrasIniciaisIdsRef.current =
        detalhesInfosPublicas.caracteristicas_extras.map(
          (caracteristicaExtra) => caracteristicaExtra.id,
        );
      indicesBenchmarkIniciaisIdsRef.current =
        detalhesInfosPublicas.indices_benchmark
          .sort((indiceA, indiceB) => {
            return indiceA.ordenacao - indiceB.ordenacao;
          })
          .map((indiceBenchmark) => indiceBenchmark.id);

      setFundoDetalhesSiteInstitucional({
        ...detalhesInfosPublicas,
        classificacao_id: detalhesInfosPublicas.classificacao?.id ?? null,
        tipo_id: detalhesInfosPublicas.tipo?.id ?? null,
        mesa_id: detalhesInfosPublicas.mesa?.id ?? null,
        caracteristicas_extras_ids: caracteristicasExtrasIniciaisIdsRef.current,
        indices_benchmark_ids: indicesBenchmarkIniciaisIdsRef.current,
      });

      documentosPublicadosIdsRef.current =
        detalhesInfosPublicas.documentos.flatMap((documento) =>
          documento.arquivos.map((arquivo) => arquivo.id),
        );
      setDocumentosSelecionadosIds(documentosPublicadosIdsRef.current);
    });
  };

  useEffect(() => {
    setAreCamposObrigatoriosPreenchidos((_) => {
      for (let campo of camposObrigatorios) {
        const valor = fundoDetalhesSiteInstitucional[campo];
        if (typeof valor === "string") {
          if (valor.trim().length === 0) {
            return false;
          }
        }

        if (valor == null || valor == "undefined") {
          return false;
        }
      }

      return true;
    });
  }, [fundoDetalhesSiteInstitucional]);

  useEffect(() => {
    if (!fundo) {
      return;
    }
    carregaDetalhesEInfosPublicas(fundo.id);

    return () => {
      setFundoDetalhesSiteInstitucional(
        fundoDetalhesSiteInstitucionalInitialState,
      );
      setDocumentosSelecionadosIds([]);
      documentosPublicadosIdsRef.current = [];
      caracteristicasExtrasIniciaisIdsRef.current = [];
      indicesBenchmarkIniciaisIdsRef.current = [];
    };
  }, [fundo]);

  return (
    fundo &&
    fundoDetalhes && (
      <ConfirmModal
        isOpen={true}
        onClose={() => null}
        size="6xl"
        title={fundo.nome}
        onCancelAction={() => {
          if (salvando) return;
          setFundo(undefined);
        }}
        confirmContent="Salvar alterações"
        confirmEnabled={!salvando && areCamposObrigatoriosPreenchidos}
        onConfirmAction={() => {
          if (!isFundoPublicado) {
            setOperacao(OperacaoEnum.Publicacao);
            setTextoModalConfirmacao("Publicar fundo?");
          } else if (isFundoPublicado && !isSwitchPublicacaoOn) {
            setOperacao(OperacaoEnum.Despublicacao);
            setTextoModalConfirmacao("Despublicar fundo?");
          } else if (isFundoPublicado && isSwitchPublicacaoOn) {
            setOperacao(OperacaoEnum.Atualizacao);
            setTextoModalConfirmacao("Atualizar fundo?");
          } else {
            return;
          }

          setIsModalConfirmacaoOpen(true);
        }}
      >
        <VStack alignItems="stretch" gap="24px">
          {isFundoPublicado && (
            <HStack {...round} alignItems="stretch" fontSize="sm" gap={0}>
              <HStack
                justifyContent="center"
                w="100px"
                borderRight="1px solid"
                borderColor="cinza.main"
                p="8px"
                color={isSwitchPublicacaoOn ? "verde.main" : "rosa.main"}
              >
                <Icon
                  as={isSwitchPublicacaoOn ? IoGlobeOutline : IoEyeOffOutline}
                />
                <Text>{isSwitchPublicacaoOn ? "Publicado" : "Oculto"}</Text>
              </HStack>
              <HStack borderRight="1px solid" borderColor="cinza.main" p="8px">
                <Switch
                  colorScheme="verde"
                  isChecked={isSwitchPublicacaoOn}
                  onChange={(ev) => setIsSwitchPublicacaoOn(ev.target.checked)}
                />
              </HStack>
              <HStack p="8px">
                <Text color={isSwitchPublicacaoOn ? "verde.main" : "rosa.main"}>
                  {isSwitchPublicacaoOn
                    ? "As informações do fundo estão públicas e disponíveis pelo site institucional."
                    : "As informações do fundo estão privadas e não estão disponíveis pelo site institucional."}
                </Text>
              </HStack>
            </HStack>
          )}
          <VStack alignItems="stretch">
            <TableContainer>
              <Table>
                <Thead>
                  <Tr>
                    <Th></Th>
                    <Th
                      bgColor="cinza.200"
                      borderTopLeftRadius="8px"
                      p="10px 0 0 0"
                    >
                      <VStack h="100%">
                        <Text mb="10px">Interno</Text>
                      </VStack>
                    </Th>
                    <Th
                      bgColor="verde.100"
                      borderTopRightRadius="8px"
                      p="10px 0 0 0"
                    >
                      <VStack gap="2px">
                        <Text>Público</Text>
                        <Progress
                          alignSelf="stretch"
                          visibility={!carregandoFundo ? "hidden" : "visible"}
                          h="8px"
                          isIndeterminate
                          colorScheme="verde"
                        />
                      </VStack>
                    </Th>
                  </Tr>
                </Thead>
                <Tbody fontSize="xs">
                  {Linha({
                    nome: "CNPJ",
                    valor: (
                      <InputReadOnlyTextoPadrao
                        state={fundoDetalhes.cnpj}
                        corTexto={corTextoReadOnly}
                      />
                    ),
                    valor2: (
                      <InputReadOnlyTextoPadrao
                        state={fundoDetalhes.cnpj}
                        corTexto={corTextoReadOnly}
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Nome",
                    obrigatorio: true,
                    valor: (
                      <InputReadOnlyTextoPadrao
                        state={fundoDetalhes.nome}
                        corTexto={corTextoReadOnly}
                      />
                    ),
                    valor2: (
                      <InputTextoPadrao
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        propriedade="nome"
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Aberto para captação",
                    obrigatorio: true,
                    valor: (
                      <SelectReadOnlyPadrao
                        corTexto={corTextoReadOnly}
                        statePropValue={fundoDetalhes.aberto_para_captacao}
                      />
                    ),
                    valor2: (
                      <SelectPadrao
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        propriedade={"aberto_para_captacao"}
                        obrigatorio={true}
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Público alvo",
                    obrigatorio: true,
                    valor: (
                      <SelectDinamicoReadOnly
                        corTexto={corTextoReadOnly}
                        statePropValue={fundoDetalhes.publico_alvo_id}
                        options={optionsPublicoAlvo}
                      />
                    ),
                    valor2: (
                      <SelectDinamico
                        obrigatorio={true}
                        options={optionsPublicoAlvo}
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        stateProp="publico_alvo_id"
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Tipo do fundo",
                    obrigatorio: true,
                    valor: (
                      <SelectDinamicoReadOnly
                        corTexto={corTextoReadOnly}
                        statePropValue={null}
                        options={[naoAplicavelOption]}
                      />
                    ),
                    valor2: (
                      <SelectDinamico
                        obrigatorio={true}
                        options={optionsTipos}
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        stateProp={"tipo_id"}
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Classificação do fundo",
                    obrigatorio: true,
                    valor: (
                      <SelectDinamicoReadOnly
                        corTexto={corTextoReadOnly}
                        statePropValue={null}
                        options={[naoAplicavelOption]}
                      />
                    ),
                    valor2: (
                      <SelectDinamico
                        obrigatorio={true}
                        options={optionsClassificacoes}
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        stateProp={"classificacao_id"}
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Mesa responsável",
                    obrigatorio: true,
                    valor: (
                      <SelectDinamicoReadOnly
                        corTexto={corTextoReadOnly}
                        statePropValue={null}
                        options={[naoAplicavelOption]}
                      />
                    ),
                    valor2: (
                      <SelectDinamico
                        obrigatorio={true}
                        options={optionsMesas}
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        stateProp={"mesa_id"}
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Índices benchmark",
                    valor: (
                      <MultiSelectReadOnly
                        corTextoReadOnly={corTextoReadOnly}
                        placeholder="Não aplicável"
                      />
                    ),
                    valor2: (
                      <MultiSelect
                        options={optionsIndicesBenchmarkIds}
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        prop="indices_benchmark_ids"
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Características extras",
                    valor: (
                      <MultiSelectReadOnly
                        corTextoReadOnly={corTextoReadOnly}
                        placeholder="Não aplicável"
                      />
                    ),
                    valor2: (
                      <MultiSelect
                        options={optionsCaracteristicasExtras}
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        prop="caracteristicas_extras_ids"
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Ticker B3 (caso aplicável)",
                    valor: (
                      <InputReadOnlyTextoPadrao
                        state={fundoDetalhes.ticker_b3 ?? undefined}
                        corTexto={corTextoReadOnly}
                      />
                    ),
                    valor2: (
                      <InputTextoPadrao
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        propriedade="ticker_b3"
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Resgate: Cotização (D+)",
                    valor: (
                      <InputReadOnlyTextoPadrao
                        type="number"
                        corTexto={corTextoReadOnly}
                        state={fundoDetalhes.cotizacao_resgate ?? undefined}
                      />
                    ),
                    valor2: (
                      <InputTextoPadrao
                        type="number"
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        propriedade="cotizacao_resgate"
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Resgate: Cotização são dias úteis?",
                    valor: (
                      <SelectReadOnlyPadrao
                        corTexto={corTextoReadOnly}
                        statePropValue={
                          fundoDetalhes.cotizacao_resgate_sao_dias_uteis
                        }
                      />
                    ),
                    valor2: (
                      <SelectPadrao
                        setState={setFundoDetalhesSiteInstitucional}
                        state={fundoDetalhesSiteInstitucional}
                        propriedade={"cotizacao_resgate_sao_dias_uteis"}
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Resgate: Cotização detalhes adicionais",
                    valor: (
                      <InputReadOnlyTextoPadrao
                        corTexto={corTextoReadOnly}
                        state={
                          fundoDetalhes.cotizacao_resgate_detalhes ?? undefined
                        }
                      />
                    ),
                    valor2: (
                      <InputTextoPadrao
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        propriedade="cotizacao_resgate_detalhes"
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Resgate: Financeiro (D+)",
                    valor: (
                      <InputReadOnlyTextoPadrao
                        corTexto={corTextoReadOnly}
                        type="number"
                        state={fundoDetalhes.financeiro_resgate ?? undefined}
                      />
                    ),
                    valor2: (
                      <InputTextoPadrao
                        type="number"
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        propriedade="financeiro_resgate"
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Resgate: Financeiro são dias úteis?",
                    valor: (
                      <SelectReadOnlyPadrao
                        corTexto={corTextoReadOnly}
                        statePropValue={
                          fundoDetalhes.financeiro_resgate_sao_dias_uteis
                        }
                      />
                    ),
                    valor2: (
                      <SelectPadrao
                        setState={setFundoDetalhesSiteInstitucional}
                        state={fundoDetalhesSiteInstitucional}
                        propriedade={"financeiro_resgate_sao_dias_uteis"}
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Resgate: Financeiro detalhes adicionais",
                    valor: (
                      <InputReadOnlyTextoPadrao
                        corTexto={corTextoReadOnly}
                        state={
                          fundoDetalhes.financeiro_resgate_detalhes ?? undefined
                        }
                      />
                    ),
                    valor2: (
                      <InputTextoPadrao
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        propriedade="financeiro_resgate_detalhes"
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Taxa de administração",
                    valor: (
                      <InputReadOnlyTextoPadrao
                        corTexto={corTextoReadOnly}
                        state={fundoDetalhes.taxa_administracao ?? undefined}
                      />
                    ),
                    valor2: (
                      <InputTextoPadrao
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        propriedade="taxa_administracao"
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Taxa de administração máxima",
                    valor: (
                      <InputReadOnlyTextoPadrao
                        corTexto={corTextoReadOnly}
                        state={
                          fundoDetalhes.taxa_administracao_maxima ?? undefined
                        }
                      />
                    ),
                    valor2: (
                      <InputTextoPadrao
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        propriedade="taxa_administracao_maxima"
                      />
                    ),
                  })}
                  {Linha({
                    nome: "Taxa de performance",
                    valor: (
                      <InputReadOnlyTextoPadrao
                        corTexto={corTextoReadOnly}
                        state={fundoDetalhes.taxa_performance ?? undefined}
                      />
                    ),
                    valor2: (
                      <InputTextoPadrao
                        state={fundoDetalhesSiteInstitucional}
                        setState={setFundoDetalhesSiteInstitucional}
                        propriedade="taxa_performance"
                      />
                    ),
                  })}
                  <Tr>
                    <Th></Th>
                    <Td p="0">
                      <Button
                        borderTopRadius="none"
                        colorScheme="azul_3"
                        w="100%"
                        size="xs"
                        rightIcon={<Icon as={IoArrowForward} />}
                        onClick={() => {
                          setFundoDetalhesSiteInstitucional((prevState) => ({
                            ...prevState,
                            aberto_para_captacao:
                              fundoDetalhes.aberto_para_captacao,
                            indices_benchmark_ids: fundoDetalhes.indices.map(
                              (indiceBenchmark) => indiceBenchmark.id,
                            ),
                            cotizacao_resgate_detalhes:
                              fundoDetalhes.cotizacao_resgate_detalhes ?? null,
                            cotizacao_resgate_sao_dias_uteis:
                              fundoDetalhes.cotizacao_resgate_sao_dias_uteis ??
                              null,
                            cotizacao_resgate:
                              fundoDetalhes.cotizacao_resgate ?? null,
                            financeiro_resgate_detalhes:
                              fundoDetalhes.financeiro_resgate_detalhes ?? null,
                            financeiro_resgate_sao_dias_uteis:
                              fundoDetalhes.financeiro_resgate_sao_dias_uteis ??
                              null,
                            financeiro_resgate:
                              fundoDetalhes.financeiro_resgate ?? null,
                            nome: fundoDetalhes.nome,
                            resumo_estrategias:
                              fundoDetalhes.resumo_estrategias ?? null,
                            taxa_administracao:
                              fundoDetalhes.taxa_administracao ?? null,
                            taxa_performance:
                              fundoDetalhes.taxa_performance ?? null,
                            ticker_b3: fundoDetalhes.ticker_b3 ?? null,
                          }));
                        }}
                      >
                        Preencher dados públicos
                      </Button>
                    </Td>
                    <Td p="0 8px" color="cinza.500">
                      <Icon as={IoTimeOutline} /> Última atualização:{" "}
                      {!fundoDetalhesSiteInstitucional.atualizado_em
                        ? "--/--/-- --:--:--"
                        : fmtDatetime(
                            fundoDetalhesSiteInstitucional.atualizado_em,
                          )}
                    </Td>
                  </Tr>
                </Tbody>
              </Table>
            </TableContainer>
            {fundoDetalhes.documentos.length > 0 &&
              (carregandoFundo ? (
                <Progress isIndeterminate h="12px" colorScheme="verde" />
              ) : (
                <>
                  <Comment fontSize="sm">
                    <Icon mb="-1px" color="laranja.main" as={IoWarning} />
                    <Text as="strong" color="laranja.main">
                      Aviso:
                    </Text>{" "}
                    Os documentos precisam ser selecionados individualmente para
                    publicação:
                  </Comment>
                  <HStack
                    alignItems="stretch"
                    p="16px"
                    borderRadius="8px"
                    border="1px solid"
                    borderColor="cinza.main"
                    flexWrap="wrap"
                    overflow="auto"
                  >
                    {fundoDetalhes.documentos
                      .flatMap((d) =>
                        d.arquivos.map((a) => ({
                          classificacao: d.classificacao,
                          arquivo: a,
                        })),
                      )
                      .map((a) => (
                        <Card
                          key={a.arquivo.id}
                          fontSize="xs"
                          w="calc(33% - 3px)"
                        >
                          <CardHeader p="8px 12px">
                            <HStack>
                              <Checkbox
                                colorScheme="verde"
                                isChecked={documentosSelecionadosIds.includes(
                                  a.arquivo.id,
                                )}
                                onChange={(ev) => {
                                  if (ev.currentTarget.checked) {
                                    setDocumentosSelecionadosIds(
                                      (prevState) => [
                                        ...prevState,
                                        a.arquivo.id,
                                      ],
                                    );
                                  } else {
                                    setDocumentosSelecionadosIds((prevState) =>
                                      prevState.filter(
                                        (docId) => docId !== a.arquivo.id,
                                      ),
                                    );
                                  }
                                }}
                              />
                              <Text>Publicar?</Text>
                            </HStack>
                          </CardHeader>
                          <Divider borderColor="cinza.main" />
                          <CardBody p="8px 12px">
                            <VStack h="100%" alignItems="stretch">
                              <Text
                                fontWeight="bold"
                                color="azul_1.main"
                                lineHeight={1.25}
                                flex={1}
                                textAlign="justify"
                              >
                                <Icon
                                  color="azul_3.main"
                                  as={IoDocumentOutline}
                                />{" "}
                                {a.arquivo.arquivo.nome}
                              </Text>
                              <Text>
                                <Icon
                                  color="azul_3.main"
                                  as={IoCalendarOutline}
                                />{" "}
                                Data Referência:{" "}
                                {fmtDate(a.arquivo.data_referencia)}
                              </Text>
                              <Text>
                                <Icon color="azul_3.main" as={IoTimeOutline} />{" "}
                                Criado em: {fmtDatetime(a.arquivo.criado_em)}
                              </Text>
                              <Divider />
                              <Text
                                textAlign="center"
                                color="azul_1.500"
                                fontWeight="bold"
                              >
                                {a.classificacao.nome}
                              </Text>
                            </VStack>
                          </CardBody>
                        </Card>
                      ))}
                  </HStack>
                </>
              ))}
          </VStack>
        </VStack>
        <ConfirmModal
          position="center"
          mb="15%"
          isOpen={isModalConfirmacaoOpen}
          onClose={() => null}
          onCancelAction={() => setIsModalConfirmacaoOpen(false)}
          onConfirmAction={() => {
            if (!fundoDetalhes || !fundoDetalhes.id) {
              return;
            }

            let requestBody = getObjUndefinedTratados({
              detalhes: {
                aberto_para_captacao:
                  fundoDetalhesSiteInstitucional.aberto_para_captacao,
                cotizacao_resgate_detalhes: getTreatedTrimString(
                  fundoDetalhesSiteInstitucional.cotizacao_resgate_detalhes,
                ),
                cotizacao_resgate_sao_dias_uteis:
                  fundoDetalhesSiteInstitucional.cotizacao_resgate_sao_dias_uteis,
                cotizacao_resgate:
                  fundoDetalhesSiteInstitucional.cotizacao_resgate,
                financeiro_resgate_detalhes: getTreatedTrimString(
                  fundoDetalhesSiteInstitucional.financeiro_resgate_detalhes,
                ),
                financeiro_resgate_sao_dias_uteis:
                  fundoDetalhesSiteInstitucional.financeiro_resgate_sao_dias_uteis,
                financeiro_resgate:
                  fundoDetalhesSiteInstitucional.financeiro_resgate,
                mesa_id: fundoDetalhesSiteInstitucional.mesa_id,
                nome: getTreatedTrimString(fundoDetalhesSiteInstitucional.nome),
                publico_alvo_id: fundoDetalhesSiteInstitucional.publico_alvo_id,
                site_institucional_classificacao_id:
                  fundoDetalhesSiteInstitucional.classificacao_id,
                site_institucional_tipo_id:
                  fundoDetalhesSiteInstitucional.tipo_id,
                taxa_administracao: getTreatedTrimString(
                  fundoDetalhesSiteInstitucional.taxa_administracao,
                ),
                taxa_administracao_maxima: getTreatedTrimString(
                  fundoDetalhesSiteInstitucional.taxa_administracao_maxima,
                ),
                taxa_performance: getTreatedTrimString(
                  fundoDetalhesSiteInstitucional.taxa_performance,
                ),
                ticker_b3: getTreatedTrimString(
                  fundoDetalhesSiteInstitucional.ticker_b3,
                ),
              },
            });

            if (operacao === OperacaoEnum.Publicacao) {
              const caracteristicasExtrasIds: number[] =
                fundoDetalhesSiteInstitucional.caracteristicas_extras_ids;
              if (caracteristicasExtrasIds.length > 0) {
                requestBody.caracteristicas_extras_ids =
                  caracteristicasExtrasIds;
              }

              const documentosParaPublicacaoIds = documentosSelecionadosIds;
              if (
                documentosParaPublicacaoIds &&
                documentosParaPublicacaoIds.length > 0
              ) {
                requestBody.documentos_ids = documentosParaPublicacaoIds;
              }

              const indicesBenchmarkParaPublicacao: {
                indice_benchmark_id: number;
                ordenacao: number;
              }[] = [];
              for (
                let i = 0;
                i < fundoDetalhesSiteInstitucional.indices_benchmark_ids.length;
                ++i
              ) {
                indicesBenchmarkParaPublicacao.push({
                  indice_benchmark_id:
                    fundoDetalhesSiteInstitucional.indices_benchmark_ids[i],
                  ordenacao: i,
                });
              }

              if (indicesBenchmarkParaPublicacao.length > 0) {
                requestBody.indices_benchmark = indicesBenchmarkParaPublicacao;
              }

              requestBody.fundo_id = fundo.id;
              publicaFundo(requestBody);
            } else if (operacao === OperacaoEnum.Despublicacao) {
              if (!fundoDetalhesSiteInstitucional.id) {
                return;
              }

              despublicaFundo(fundoDetalhesSiteInstitucional.id);
            } else if (operacao === OperacaoEnum.Atualizacao) {
              if (!fundoDetalhes.detalhes_infos_publicas?.id) {
                return;
              }

              let caracteristicasExtrasParaPublicacaoIds: undefined | number[] =
                undefined;
              let caracteristicasExtrasParaDespublicacaoIds:
                | undefined
                | number[] = undefined;

              if (
                fundoDetalhesSiteInstitucional.caracteristicas_extras_ids
                  .length > 0
              ) {
                caracteristicasExtrasParaPublicacaoIds = getIdsParaPublicacao(
                  caracteristicasExtrasIniciaisIdsRef.current,
                  fundoDetalhesSiteInstitucional.caracteristicas_extras_ids,
                );
              }
              caracteristicasExtrasParaDespublicacaoIds =
                getIdsParaDespublicacao(
                  caracteristicasExtrasIniciaisIdsRef.current,
                  fundoDetalhesSiteInstitucional.caracteristicas_extras_ids,
                );

              let indicesBenchmarkParaPublicacao: {
                indice_benchmark_id: number;
                ordenacao: number;
              }[] = [];
              let indicesBenchmarkParaDespublicacao: {
                indice_benchmark_id: number;
                ordenacao: number;
              }[] = [];

              if (
                fundoDetalhesSiteInstitucional.indices_benchmark_ids.length > 0
              ) {
                indicesBenchmarkParaPublicacao =
                  fundoDetalhesSiteInstitucional.indices_benchmark_ids.map(
                    (indiceBenchmarkId, index) => {
                      return {
                        indice_benchmark_id: indiceBenchmarkId,
                        ordenacao: index,
                      };
                    },
                  );
                indicesBenchmarkParaDespublicacao =
                  indicesBenchmarkIniciaisIdsRef.current.map(
                    (indiceBenchmarkId, index) => ({
                      indice_benchmark_id: indiceBenchmarkId,
                      ordenacao: index,
                    }),
                  );
              } else {
                indicesBenchmarkParaDespublicacao = getIdsParaDespublicacao(
                  indicesBenchmarkIniciaisIdsRef.current,
                  fundoDetalhesSiteInstitucional.indices_benchmark_ids,
                ).map((indiceBenchmarkId, index) => {
                  return {
                    indice_benchmark_id: indiceBenchmarkId,
                    ordenacao: index,
                  };
                });
              }

              let documentosParaPublicacaoIds: undefined | number[] = undefined;
              let documentosParaDespublicacaoIds: undefined | number[] =
                undefined;

              if (documentosSelecionadosIds.length > 0) {
                documentosParaPublicacaoIds = getIdsParaPublicacao(
                  documentosPublicadosIdsRef.current,
                  documentosSelecionadosIds,
                );
              }

              documentosParaDespublicacaoIds = getIdsParaDespublicacao(
                documentosPublicadosIdsRef.current,
                documentosSelecionadosIds,
              );

              requestBody = {
                ...requestBody,
                caracteristicas_extras_para_publicacao_ids:
                  caracteristicasExtrasParaPublicacaoIds,
                caracteristicas_extras_para_despublicacao_ids:
                  caracteristicasExtrasParaDespublicacaoIds,
                indices_benchmark_para_publicacao:
                  indicesBenchmarkParaPublicacao,
                indices_benchmark_para_despublicacao:
                  indicesBenchmarkParaDespublicacao,
                documentos_para_publicacao_ids: documentosParaPublicacaoIds,
                documentos_para_despublicacao_ids:
                  documentosParaDespublicacaoIds,
              };

              atualizaInfosPublicas(
                fundoDetalhes.detalhes_infos_publicas.id,
                requestBody,
              );
            }

            return;
          }}
        >
          <Text as="p">{textoModalConfirmacao}</Text>
        </ConfirmModal>
      </ConfirmModal>
    )
  );
}

const round = {
  border: "1px solid",
  borderColor: "cinza.main",
  borderRadius: "8px",
  overflow: "hidden",
};

const corTextoReadOnly = "rgb(120, 120, 120)";

const Linha = ({
  nome,
  valor,
  valor2,
  obrigatorio,
}: {
  nome: string;
  valor: React.ReactNode;
  valor2?: React.ReactNode;
  obrigatorio?: boolean;
}) => (
  <Tr>
    <Th fontSize="xs" p="0 8px" m="2px" color="azul_1.700">
      {nome}
      {obrigatorio && (
        <Text as="span" fontSize="medium">
          *
        </Text>
      )}
    </Th>
    <Td
      width="50%"
      bgColor="cinza.100"
      fontSize="xs"
      p="0 8px"
      m="2px"
      height="50px"
    >
      {valor}
    </Td>
    <Td
      width="50%"
      bgColor="verde.50"
      fontSize="xs"
      p="0 8px"
      m="2px"
      height="50px"
    >
      {valor2}
    </Td>
  </Tr>
);

const publicoAlvo: Record<number, string> = {
  1: "Investidor em Geral",
  2: "Investidor Qualificado",
  3: "Investidor Profissional",
};

function getIdsParaPublicacao(
  idsIniciais: number[],
  idsSelecionados: number[],
): number[] {
  const idsParaPublicacao: number[] = [];

  for (let idSelecionado of idsSelecionados) {
    if (!idsIniciais.includes(idSelecionado)) {
      idsParaPublicacao.push(idSelecionado);
    }
  }

  return idsParaPublicacao;
}

function getIdsParaDespublicacao(
  idsIniciais: number[],
  idsSelecionados: number[] | undefined,
): number[] {
  const idsParaDespublicacao: number[] = [];

  if (!idsSelecionados) {
    return idsIniciais;
  }

  for (let idInicial of idsIniciais) {
    if (!idsSelecionados.includes(idInicial)) {
      idsParaDespublicacao.push(idInicial);
    }
  }

  return idsParaDespublicacao;
}

function getObjUndefinedTratados(obj: { [key: string]: any }): {
  [key: string]: any;
} {
  for (let key in obj) {
    if (obj[key] === "null") {
      obj[key] = null;
    } else if (typeof obj[key] === "object" && obj[key] !== null) {
      getObjUndefinedTratados(obj[key]);
    }
  }

  return obj;
}

function getObjComNullsDeUndefineds(obj: { [key: string]: any }): {
  [key: string]: any;
} {
  for (let key in obj) {
    if (obj[key] === undefined) {
      obj[key] = null;
    } else if (typeof obj[key] === "object" && obj[key] !== null) {
      getObjComNullsDeUndefineds(obj[key]);
    }
  }

  return obj;
}

const camposObrigatorios: Array<keyof _FundoDetalhesSiteInstitucional> = [
  "nome",
  "aberto_para_captacao",
  "publico_alvo_id",
  "tipo_id",
  "classificacao_id",
  "mesa_id",
];

const naoAplicavelOption: SelectOption = {
  label: "Não Aplicável",
  value: String(null),
};

function getTreatedTrimString(
  strValue: string | null | undefined,
): string | null {
  if (strValue === undefined || strValue === null) {
    return null;
  }

  const treatedStrValue = strValue.trim();
  return treatedStrValue.length === 0 ? null : treatedStrValue;
}

const fundoDetalhesSiteInstitucionalInitialState: _FundoDetalhesSiteInstitucional =
  {
    id: null,
    nome: null,
    aberto_para_captacao: null,
    atualizado_em: null,
    ticker_b3: null,
    cotizacao_resgate: null,
    cotizacao_resgate_sao_dias_uteis: null,
    cotizacao_resgate_detalhes: null,
    financeiro_resgate: null,
    financeiro_resgate_sao_dias_uteis: null,
    financeiro_resgate_detalhes: null,
    publico_alvo_id: null,
    taxa_performance: null,
    taxa_administracao: null,
    taxa_administracao_maxima: null,
    resumo_estrategias: null,
    documentos: [],
    classificacao: null,
    classificacao_id: null,
    tipo_id: null,
    mesa_id: null,
    caracteristicas_extras_ids: [],
    indices_benchmark_ids: [],
    pertence_a_classe: null,
  };
