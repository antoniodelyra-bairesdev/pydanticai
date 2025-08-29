"use client";

import {
  Box,
  Button,
  Checkbox,
  CheckboxGroup,
  Divider,
  HStack,
  Heading,
  Icon,
  Input,
  Progress,
  Radio,
  RadioGroup,
  Select,
  TagLeftIcon,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import React, { useEffect, useMemo, useRef, useState } from "react";

import {
  EstrategiaAgrupamentoOperacoes,
  OperacaoType,
} from "@/lib/types/api/iv/v1";
import OperacaoItemColuna, { pendencias, quebras } from "./OperacaoItemColuna";
import ModalOperacao from "./ModalOperacao";
import Hint from "@/app/_components/texto/Hint";

import {
  GroupBase,
  Select as MultiSelect,
  SelectComponentsConfig,
  chakraComponents,
} from "chakra-react-select";
import {
  IoArrowDown,
  IoArrowUp,
  IoCheckmarkCircleOutline,
  IoCloseCircleOutline,
  IoCloudDownload,
  IoCloudUpload,
  IoContrastOutline,
  IoDesktopOutline,
  IoDocumentsOutline,
  IoEllipse,
  IoEllipseOutline,
  IoEyeOffOutline,
} from "react-icons/io5";
import { IconType } from "react-icons";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { useAsync, useHTTP } from "@/lib/hooks";

export type TriagemB3Props = {
  negocios: OperacaoType[];
  historico?: boolean;
  onDataConsultaChange?: (novaData: string) => void;
};

type OpcaoPendencia = {
  label: string;
  value: string;
  cor: string;
  icone: IconType;
  corTexto?: string;
};

const customComponents: SelectComponentsConfig<
  OpcaoPendencia,
  true,
  GroupBase<OpcaoPendencia>
> = {
  Option: ({ children, ...props }) => (
    <chakraComponents.Option {...props}>
      <Icon as={props.data.icone} color={props.data.cor} mr={2} h={5} w={5} />
      {children}
    </chakraComponents.Option>
  ),
  MultiValueContainer: ({ children, ...props }) => (
    <chakraComponents.MultiValueContainer {...props}>
      <TagLeftIcon as={props.data.icone} color={props.data.cor} />
      {children}
    </chakraComponents.MultiValueContainer>
  ),
};

export default function TriagemB3({
  negocios,
  historico,
  onDataConsultaChange,
}: TriagemB3Props) {
  const [idNegocioSelecionado, setIdNegocioSelecionado] = useState<number>();
  const {
    isOpen: isNegocioOpen,
    onOpen: onNegocioOpen,
    onClose: onNegocioClose,
  } = useDisclosure();

  const defaultValue = "Nome ativo";
  const [propriedadeOrdenacao, setPropriedadeOrdenacao] =
    useState(defaultValue);
  const [crescente, setCrescente] = useState(true);

  const [filtroSide, setFiltroSide] = useState<string[]>([]);
  const [filtroAtivo, setFiltroAtivo] = useState<string[]>([]);
  const [filtroEncaminhamento, setFiltroEncaminhamento] = useState<string[]>(
    [],
  );
  const [filtroPendencias, setFiltroPendencias] = useState<string[]>([]);

  const opSelecionada = negocios.find((n) => n.id === idNegocioSelecionado);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const filtrados = useMemo(
    () =>
      negocios.filter((n) => {
        if (filtroSide.length) {
          const side = n.vanguarda_compra ? "Compra" : "Venda";
          if (!filtroSide.includes(side)) return;
        }
        if (filtroAtivo.length) {
          const ativo = n.cadastro_ativo?.tipo ?? "Não registrado";
          if (!filtroAtivo.includes(ativo)) return;
        }
        if (filtroEncaminhamento.length) {
          const { encaminhadas_liquidacao, total } = quebras(n.eventos);
          const enc =
            total === 0
              ? "Pendente emissão de registros"
              : encaminhadas_liquidacao === 0
                ? "Nenhum registro encaminhado"
                : encaminhadas_liquidacao !== total
                  ? "Registros parcialmente encaminhados"
                  : "Todos os registros encaminhados";
          if (!filtroEncaminhamento.includes(enc)) return;
        }
        if (filtroPendencias.length) {
          const ps = pendencias(n.eventos).map((p) => p.nome);
          if (ps.length === 0) ps.push("Sem pendências");
          if (ps.every((p) => !filtroPendencias.includes(p))) return;
        }
        return true;
      }),
    [negocios, filtroSide, filtroAtivo, filtroEncaminhamento, filtroPendencias],
  );

  const filtradosEOrdenados = useMemo(
    () => [
      ...filtrados.sort((n1, n2) => {
        const nA = crescente ? n1 : n2;
        const nB = crescente ? n2 : n1;
        switch (propriedadeOrdenacao) {
          case "Nome ativo":
            return nA.codigo_ativo.localeCompare(nB.codigo_ativo);
          case "Nome corretora":
            return (nA.contraparte_nome ?? "").localeCompare(
              nB.contraparte_nome ?? "",
            );
          case "Hora registrada":
            return nA.criado_em.localeCompare(nB.criado_em);
          default:
            return 0;
        }
      }),
    ],
    [propriedadeOrdenacao, crescente, filtrados],
  );

  const { isOpen, onOpen, onClose } = useDisclosure();

  const [aprovacao, setAprovacao] = useState("0");
  const [motivo, setMotivo] = useState("");

  const httpClient = useHTTP({ withCredentials: true });

  const [loadingSheet, loadSheet] = useAsync();
  const [pendentes, setPendentes] = useState<OperacaoType[]>([]);
  const [selecionados, setSelecionados] = useState<number[]>([]);

  const [estrategia, setEstrategia] = useState<EstrategiaAgrupamentoOperacoes>(
    EstrategiaAgrupamentoOperacoes.Todas,
  );

  useEffect(() => {
    if (selectedFile === null) return;
    loadSheet(async () => {
      if (selectedFile === null) return;
      const body = new FormData();
      body.append("file", selectedFile);
      const response = await httpClient.fetch(
        "v1/operacoes/encontrar?estrategia=" + estrategia,
        {
          hideToast: { success: true },
          method: "POST",
          body,
          multipart: true,
        },
      );
      if (!response.ok) return;
      const selecionadas = ((await response.json()) as OperacaoType[]).map(
        (op) => op.id,
      );
      const candidatas = new Set(selecionadas);
      setPendentes(negocios.filter((n) => candidatas.has(n.id)));
      setSelecionados(selecionadas);
    });
  }, [selectedFile, negocios, estrategia]);

  const limpar = () => {
    if (fileInputRef.current) {
      (fileInputRef.current as any).value = null;
    }
    setSelectedFile(null);
    setPendentes([]);
    setSelecionados([]);
  };

  return (
    <VStack alignItems="stretch" p="8px 24px">
      <Box bgColor="white" top={0} position="sticky" zIndex={2}>
        <HStack alignItems="stretch" p="8px 0px">
          <VStack alignItems="stretch" gap={0}>
            <Hint>Ordenação:</Hint>
            <VStack
              alignItems="stretch"
              border="1px solid"
              borderColor="cinza.main"
              borderRadius="8px"
              flex={1}
              p="8px 16px"
              gap={0}
            >
              <Hint>Propriedade</Hint>
              <HStack>
                <Select
                  size="sm"
                  bgColor="white"
                  onChange={(ev) => setPropriedadeOrdenacao(ev.target.value)}
                  defaultValue={defaultValue}
                >
                  {["Nome ativo", "Hora registrada", "Nome corretora"].map(
                    (o, i) => (
                      <option key={i} value={o}>
                        {o}
                      </option>
                    ),
                  )}
                </Select>
                <Button
                  onClick={() => setCrescente(!crescente)}
                  w="144px"
                  colorScheme="azul_2"
                  size="xs"
                  leftIcon={crescente ? <IoArrowDown /> : <IoArrowUp />}
                >
                  {crescente ? "Crescente" : "Decrescente"}
                </Button>
              </HStack>
            </VStack>
          </VStack>
          <VStack alignItems="stretch" gap={0} minW="256px" flex={1}>
            <Hint>Filtros:</Hint>
            <HStack
              alignItems="flex-start"
              border="1px solid"
              borderColor="cinza.main"
              borderRadius="8px"
              p="8px 16px"
            >
              <VStack flex={2} alignItems="stretch" gap={0}>
                <Hint>Lado da operação - Vanguarda</Hint>
                <MultiSelect
                  size="sm"
                  placeholder="Todos"
                  options={[
                    {
                      value: "Compra",
                      icone: IoCloudDownload,
                      cor: "azul_2.main",
                      corTexto: "azul_2.main",
                    },
                    {
                      value: "Venda",
                      icone: IoCloudUpload,
                      cor: "rosa.main",
                      corTexto: "rosa.main",
                    },
                  ].map(({ value, ...rest }) => ({
                    ...rest,
                    value,
                    label: value,
                  }))}
                  onChange={(values) =>
                    setFiltroSide(values.map((v) => v.value))
                  }
                  isMulti
                  useBasicStyles
                  closeMenuOnSelect={false}
                  components={customComponents}
                />
              </VStack>
              <VStack flex={3} alignItems="stretch" gap={0}>
                <Hint>Tipo de ativo</Hint>
                <MultiSelect
                  size="sm"
                  placeholder="Todos"
                  options={[
                    "Debênture",
                    "CRI",
                    "CRA",
                    "FIDC",
                    "Não registrado",
                  ].map((value) => ({ value, label: value }))}
                  onChange={(values) =>
                    setFiltroAtivo(values.map((v) => v.value))
                  }
                  isMulti
                  useBasicStyles
                  closeMenuOnSelect={false}
                />
              </VStack>
              <VStack flex={4} alignItems="stretch" gap={0}>
                <Hint>Encaminhamento para liquidação</Hint>
                <MultiSelect
                  size="sm"
                  placeholder="Todos"
                  options={[
                    {
                      value: "Pendente emissão de registros",
                      icone: IoCloseCircleOutline,
                      cor: "cinza.500",
                    },
                    {
                      value: "Nenhum registro encaminhado",
                      icone: IoEllipseOutline,
                      cor: "verde.main",
                    },
                    {
                      value: "Registros parcialmente encaminhados",
                      icone: IoContrastOutline,
                      cor: "verde.main",
                    },
                    {
                      value: "Todos os registros encaminhados",
                      icone: IoEllipse,
                      cor: "verde.main",
                    },
                  ].map(({ value, ...rest }) => ({
                    ...rest,
                    value,
                    label: value,
                  }))}
                  onChange={(values) =>
                    setFiltroEncaminhamento(values.map((v) => v.value))
                  }
                  isMulti
                  useBasicStyles
                  closeMenuOnSelect={false}
                  components={customComponents}
                />
              </VStack>
              <VStack flex={2} alignItems="stretch" gap={0}>
                <Hint>Pendências:</Hint>
                <MultiSelect
                  size="sm"
                  placeholder="Todos"
                  options={[
                    {
                      value: "Sem pendências",
                      icone: IoCheckmarkCircleOutline,
                      cor: "verde.main",
                    },
                    {
                      value: "Pendente acato voice",
                      icone: IoDesktopOutline,
                      cor: "azul_4.main",
                    },
                    {
                      value: "Pendente alocação",
                      icone: IoDocumentsOutline,
                      cor: "azul_4.main",
                    },
                    {
                      value: "Pendente revisão",
                      icone: IoEyeOffOutline,
                      cor: "azul_4.main",
                    },
                  ].map(({ value, ...rest }) => ({
                    ...rest,
                    value,
                    label: value,
                  }))}
                  onChange={(values) =>
                    setFiltroPendencias(values.map((v) => v.value))
                  }
                  isMulti
                  useBasicStyles
                  closeMenuOnSelect={false}
                  components={customComponents}
                />
              </VStack>
            </HStack>
          </VStack>
          <VStack alignItems="stretch" gap={0}>
            <Hint>Ações</Hint>
            {historico ? (
              <>
                <VStack
                  justifyContent="flex-end"
                  alignItems="stretch"
                  border="1px solid"
                  borderColor="cinza.main"
                  borderRadius="8px"
                  flex={1}
                  p="8px"
                  gap={0}
                >
                  <Hint>Data da consulta:</Hint>
                  <Input
                    size="sm"
                    type="date"
                    onChange={(ev) => onDataConsultaChange?.(ev.target.value)}
                  />
                </VStack>
              </>
            ) : (
              <>
                <VStack
                  justifyContent="center"
                  alignItems="stretch"
                  border="1px solid"
                  borderColor="cinza.main"
                  borderRadius="8px"
                  flex={1}
                  p="8px"
                  gap={0}
                >
                  <Button onClick={onOpen} size="xs">
                    Revisão a partir de boleta
                  </Button>
                </VStack>
              </>
            )}
          </VStack>
        </HStack>
      </Box>
      <VStack flex={1}>
        {filtradosEOrdenados.map((n, i) => (
          <OperacaoItemColuna
            w="100%"
            key={i}
            operacao={n}
            onClick={() => {
              onNegocioOpen();
              setIdNegocioSelecionado(n.id);
            }}
          />
        ))}
      </VStack>
      {opSelecionada && (
        <ModalOperacao
          operacao={opSelecionada}
          isOpen={isNegocioOpen}
          onClose={() => {
            onNegocioClose();
            setIdNegocioSelecionado(undefined);
          }}
        />
      )}
      <ConfirmModal
        isOpen={isOpen}
        onClose={() => {
          limpar();
          onClose();
        }}
        size="5xl"
      >
        <VStack alignItems="stretch">
          <VStack alignItems="stretch" gap={0}>
            <HStack alignItems="flex-start">
              <VStack alignItems="stretch" flex={1} gap={0}>
                <Text fontSize="sm" fontWeight="bold" mb="12px">
                  Carregar Arquivo
                </Text>
                <HStack flex={1}>
                  <Input
                    size="sm"
                    type="file"
                    p="4px"
                    accept=".xlsx"
                    ref={fileInputRef}
                    onChange={(ev) =>
                      setSelectedFile(ev.target.files?.item(0) ?? null)
                    }
                  />
                  <Button onClick={limpar} size="sm" colorScheme="rosa">
                    Limpar
                  </Button>
                </HStack>
              </VStack>
              <RadioGroup
                ml="24px"
                defaultValue={EstrategiaAgrupamentoOperacoes.Todas}
                size="sm"
                colorScheme="verde"
                value={estrategia}
                onChange={(valor: EstrategiaAgrupamentoOperacoes) =>
                  setEstrategia(valor)
                }
              >
                <VStack alignItems="flex-start" gap={0}>
                  <Text fontSize="sm" fontWeight="bold" mb="8px">
                    Critério de separação de operações
                  </Text>
                  <Radio value={EstrategiaAgrupamentoOperacoes.Todas}>
                    Agrupar todas as operações iguais, independente de posição.
                  </Radio>
                  <Radio value={EstrategiaAgrupamentoOperacoes.Bloco}>
                    Agrupar blocos de operações separados em operações
                    individuais.
                  </Radio>
                  <Radio value={EstrategiaAgrupamentoOperacoes.Linha}>
                    Considerar cada linha como uma operação.
                  </Radio>
                </VStack>
              </RadioGroup>
            </HStack>
            <Progress
              size="sm"
              colorScheme="verde"
              isIndeterminate
              visibility={loadingSheet ? "visible" : "hidden"}
            />
            <Divider />
          </VStack>
          {pendentes.length > 0 ? (
            <>
              <VStack alignItems="stretch" gap={0}>
                <Hint>Operações pendentes encontradas:</Hint>
                <VStack
                  maxH="50vh"
                  alignItems="stretch"
                  border="1px solid"
                  borderRadius="4px"
                  borderColor="cinza.main"
                  p="8px"
                  overflow="auto"
                >
                  <CheckboxGroup
                    defaultValue={selecionados}
                    colorScheme="verde"
                    value={selecionados}
                    onChange={(values) => {
                      console.log(values);
                      setSelecionados(
                        values.map((v) => Number(v)).filter((v) => !isNaN(v)),
                      );
                    }}
                  >
                    {pendentes.map((op) => (
                      <HStack key={op.id}>
                        <Checkbox value={op.id} />
                        <OperacaoItemColuna
                          flex={1}
                          operacao={op}
                          cursor="auto"
                        />
                      </HStack>
                    ))}
                  </CheckboxGroup>
                </VStack>
              </VStack>
              <VStack alignItems="stretch" gap={0}>
                <Hint>Ações</Hint>
                <HStack
                  alignItems="flex-end"
                  justifyContent="space-between"
                  border="1px solid"
                  borderRadius="4px"
                  borderColor="cinza.main"
                  p="8px"
                >
                  <RadioGroup
                    size="sm"
                    onChange={setAprovacao}
                    value={aprovacao}
                  >
                    <VStack gap={0} alignItems="flex-start">
                      <Radio value={"1"} colorScheme="verde">
                        <Text
                          fontSize="sm"
                          color={aprovacao === "1" ? "verde.700" : undefined}
                        >
                          Aprovar
                        </Text>
                      </Radio>
                      <Radio value={"0"} colorScheme="rosa">
                        <Text
                          fontSize="sm"
                          color={aprovacao === "0" ? "rosa.700" : undefined}
                        >
                          Reprovar
                        </Text>
                      </Radio>
                    </VStack>
                  </RadioGroup>
                  {aprovacao === "0" && (
                    <VStack gap={0} alignItems="flex-start" flex={1}>
                      <Hint>Motivo reprovação</Hint>
                      <Input
                        size="xs"
                        onChange={(ev) => setMotivo(ev.target.value)}
                        value={motivo}
                      />
                    </VStack>
                  )}
                  <Button
                    size="xs"
                    onClick={() => {
                      const body = JSON.stringify(
                        selecionados.map((s) => ({
                          id_operacao_interna: s,
                          aprovacao: aprovacao === "1",
                          motivo: aprovacao === "0" ? null : (motivo ?? ""),
                        })),
                      );
                      httpClient.fetch(
                        "v1/operacoes/aprovacao-backoffice/varias",
                        { method: "POST", body },
                      );
                      limpar();
                      onClose();
                    }}
                    colorScheme={aprovacao === "0" ? "rosa" : "verde"}
                  >
                    Enviar {aprovacao === "0" ? "reprovação" : "aprovação"}
                  </Button>
                </HStack>
              </VStack>
            </>
          ) : (
            <Heading textAlign="center" size="sm" color="cinza.main">
              Nenhuma operação encontrada
            </Heading>
          )}
        </VStack>
      </ConfirmModal>
    </VStack>
  );
}
