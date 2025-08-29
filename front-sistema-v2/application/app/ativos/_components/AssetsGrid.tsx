"use client";

import ValidationGrid, {
  ModificationMap,
  ValidationGridColDef,
  ValidationGridMethods,
} from "@/app/_components/grid/ValidationGrid";
import {
  dateColDef,
  listColDef,
  moneyColDef,
  percentageColDef,
} from "@/app/_components/grid/colDefs";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { getColorHex } from "@/app/theme";
import { useColors, useHTTP } from "@/lib/hooks";
import { AssetPageContext, DataFlow } from "@/lib/providers/AssetPageProvider";
import { Ativo, Emissor, Evento } from "@/lib/types/api/iv/v1";
import {
  dateFilter,
  dateFilterSerialize,
  inOrNotInSerialize,
  listFilter,
  numberFilter,
  numberFilterSerialize,
  percentageFilterSerialize,
  textFilter,
  textFilterSerialize,
} from "@/lib/util/grid";
import { parseIndiceFromCell, strFromIndice } from "@/lib/util/misc";
import {
  SingularPluralMapping,
  pluralOrSingular,
  strCSSColor,
} from "@/lib/util/string";
import { inList, required } from "@/lib/util/validation";
import { CalendarIcon } from "@chakra-ui/icons";
import {
  Box,
  Checkbox,
  HStack,
  Icon,
  NumberDecrementStepper,
  NumberIncrementStepper,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  Tag,
  Text,
  Tooltip,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import {
  GridApi,
  ICellRendererParams,
  IRowNode,
  IServerSideDatasource,
  IServerSideGetRowsParams,
  ValueSetterParams,
} from "ag-grid-community";
import {
  MouseEventHandler,
  MutableRefObject,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import GenerateEventsModal from "./GenerateEventsModal";
import InserirAtivoModal from "./InserirAtivoModal";
import InserirLinhasModal from "./InserirLinhasModal";
import Link from "next/link";
import { IoLink } from "react-icons/io5";

export type AssetGridMethods = {
  openInsertModal: () => void;
};

export type AssetsGridProps = {
  colDefRef: MutableRefObject<ValidationGridColDef[]>;
  editable: boolean;
  codigos: string[];
  emissores: Emissor[];
  indices: string[];
  tipos: string[];
  tiposEventosSuportados: string[];
  methodsRef?: MutableRefObject<AssetGridMethods | undefined>;
  eventsGridMethodsRef: MutableRefObject<
    ValidationGridMethods<Evento> | undefined
  >;
  onNewAssetsFetched?: (ativos: Ativo[], total: number) => void;
};

export default function AssetsGrid({
  colDefRef,
  codigos,
  emissores,
  indices,
  tipos,
  tiposEventosSuportados,
  editable,
  methodsRef,
  eventsGridMethodsRef,
  onNewAssetsFetched,
}: AssetsGridProps) {
  const emissoresStr = emissores.map((e) => e.nome);
  const colDefs = useMemo<ValidationGridColDef[]>(
    () => [
      {
        headerName: "Código",
        field: "codigo",
        pinned: true,
        resizable: false,
        ...listColDef(codigos),
        ...listFilter(codigos),
        cellRenderer: ({ value }: ICellRendererParams) => {
          const { hover } = useColors();
          const color = strCSSColor(value ?? "");
          return (
            <HStack
              w="100%"
              h="100%"
              justifyContent="space-between"
              role="group"
              alignItems="center"
            >
              <Tag key="codigo" bgColor={hover} color={color}>
                {value}
              </Tag>
              <Tag
                display={editable ? "none" : "block"}
                visibility="hidden"
                _groupHover={{ visibility: "visible" }}
                key="abrir"
                bgColor="cinza.100"
                color="cinza.600"
              >
                <Link href={"/ativos/" + value} role="group">
                  <Icon
                    verticalAlign="bottom"
                    transform="rotate(45deg)"
                    as={IoLink}
                    color="cinza.700"
                    mr="4px"
                  />
                  Abrir
                </Link>
              </Tag>
            </HStack>
          );
        },
        primary: true,
      },
      {
        headerName: "Emissor",
        field: "emissor",
        ...listColDef(emissoresStr),
        ...listFilter(emissoresStr),
        cellRenderer: ({ value }: ICellRendererParams) => {
          return (
            <HStack w="100%" role="group" position="relative">
              <Text>{value}</Text>
              <Tag
                position="absolute"
                right={0}
                display={editable ? "none" : "block"}
                visibility="hidden"
                _groupHover={{ visibility: "visible" }}
                key="abrir"
                bgColor="cinza.100"
                color="cinza.600"
              >
                <Link
                  href={
                    "/emissores/" +
                      emissores.find((e) => e.nome === value)?.id ?? "invalido"
                  }
                  role="group"
                >
                  <Icon
                    verticalAlign="bottom"
                    transform="rotate(45deg)"
                    as={IoLink}
                    color="cinza.700"
                    mr="4px"
                  />
                  Abrir
                </Link>
              </Tag>
            </HStack>
          );
        },
      },
      {
        headerName: "Índice",
        field: "indice",
        ...listColDef(indices),
        ...listFilter(indices),
        valueSetter(params: ValueSetterParams) {
          params.data.indice = null;
          params.data.ativo_ipca = null;

          const data = parseIndiceFromCell(params.newValue);
          if (!data) {
            return true;
          }

          params.data.indice = params.newValue;

          return true;
        },
        cellRenderer({ value, api, node }: ICellRendererParams) {
          const { hover } = useColors();
          const ind = parseIndiceFromCell(value);

          const onClick: MouseEventHandler = (ev) => {
            if (!editable || !ev.ctrlKey) return;
            setSelectedAtivoIPCA({ ativo: node.data, value });
            onIPCAOpen();
          };

          return !ind?.nome ? (
            <Text color={hover}>Vazio</Text>
          ) : ind?.ativo_ipca ? (
            <Tooltip
              isDisabled={!editable}
              bgColor="azul_1.700"
              color="white"
              label="Editar: ⌨️ Ctrl + 🖱️ Esq."
              placement="top"
              hasArrow
            >
              <HStack
                cursor={editable ? "pointer" : "auto"}
                transition="background-color 0.25s"
                onClick={onClick}
                gap={0}
                justifyContent="space-between"
                alignItems="center"
                _hover={editable ? { backgroundColor: hover } : {}}
                w="100%"
                h="100%"
                p="0 4px"
              >
                <VStack
                  flex={3}
                  h="100%"
                  gap={0}
                  justifyContent="center"
                  alignItems="flex-start"
                >
                  <VStack h="50%" justifyContent="center">
                    <Text as="span">{ind?.nome}</Text>
                  </VStack>
                  <HStack h="30%" gap="2px" fontSize="9px">
                    <CalendarIcon color="cinza.500" fontSize="8px" mr="1px" />
                    <Text as="span" color="cinza.600" lineHeight="100%">
                      {ind.ativo_ipca?.mesversario
                        .toString()
                        .padStart(2, "0") ?? "--"}
                    </Text>
                  </HStack>
                </VStack>
                <VStack flex={2} h="100%" gap={1} justifyContent="center">
                  <VStack
                    opacity={ind.ativo_ipca?.ipca_2_meses ? 1 : 0}
                    borderRadius="4px"
                    backgroundColor={hover}
                    w="80%"
                    h="30%"
                    justifyContent="center"
                  >
                    <Text p={0} as="span" fontSize="10px" color="verde.500">
                      2MA
                    </Text>
                  </VStack>
                  <VStack
                    opacity={ind.ativo_ipca?.ipca_negativo ? 1 : 0}
                    borderRadius="4px"
                    backgroundColor={hover}
                    w="80%"
                    h="30%"
                    justifyContent="center"
                  >
                    <Text p={0} as="span" fontSize="10px" color="laranja.main">
                      POS
                    </Text>
                  </VStack>
                </VStack>
              </HStack>
            </Tooltip>
          ) : (
            <Text>{ind?.nome}</Text>
          );
        },
      },
      {
        headerName: "Taxa (%)",
        field: "taxa",
        ...numberFilter,
        ...percentageColDef,
      },
      {
        headerName: "Tipo",
        field: "tipo",
        ...listColDef(tipos),
        ...listFilter(tipos),
      },
      {
        headerName: "Valor de emissão (R$)",
        field: "valor_emissao",
        ...numberFilter,
        ...moneyColDef("R$"),
      },
      {
        headerName: "Data da emissão",
        field: "data_emissao",
        ...dateFilter,
        ...dateColDef,
      },
      {
        headerName: "Início da rentabilidade",
        field: "inicio_rentabilidade",
        ...dateFilter,
        ...dateColDef,
      },
      {
        headerName: "Data de vencimento",
        field: "data_vencimento",
        ...dateFilter,
        ...dateColDef,
      },
      { headerName: "Apelido", field: "apelido", ...textFilter },
      { headerName: "ISIN", field: "isin", ...textFilter },
      { headerName: "Série", field: "serie", ...numberFilter },
      { headerName: "Emissão", field: "emissao", ...numberFilter },
    ],
    [editable],
  );

  const [selectedAtivoIPCA, setSelectedAtivoIPCA] = useState<{
    ativo: Ativo;
    value: string;
  } | null>(null);

  colDefRef.current = colDefs;

  const { hover } = useColors();

  const {
    isOpen: isInsertAtivosOpen,
    onOpen: onInsertAtivosOpen,
    onClose: onInsertAtivosClose,
  } = useDisclosure();

  const {
    isOpen: isDeleteAssetsConfirmOpen,
    onOpen: onDeleteAssetsConfirmOpen,
    onClose: onDeleteAssetsConfirmClose,
  } = useDisclosure();

  const {
    isOpen: isGenerateEventsOpen,
    onOpen: onGenerateEventsOpen,
    onClose: onGenerateEventsClose,
  } = useDisclosure();

  const {
    isOpen: isInsertEventsModalOpen,
    onOpen: onInsertEventsModalOpen,
    onClose: onInsertEventsModalClose,
  } = useDisclosure();

  const {
    isOpen: isIPCAOpen,
    onOpen: onIPCAOpen,
    onClose: onIPCAClose,
  } = useDisclosure();

  const [selectedAsset, setSelected] = useState<Ativo | undefined>(undefined);

  const gridApiRef = useRef<GridApi>();
  const gridMethodsRef = useRef<ValidationGridMethods<Ativo>>();

  if (methodsRef) {
    methodsRef.current = {
      openInsertModal() {
        setSelected(undefined);
        onInsertAtivosOpen();
      },
    };
  }

  const s: SingularPluralMapping = {
    $: { singular: "", plural: "s" },
  };

  const [willDeleteAssets, setWillDeleteAssets] = useState<string[]>([]);

  const getDeleteItem = (node: IRowNode | null) => {
    const selected = new Set(
      gridApiRef.current?.getSelectedRows().map((row) => row.codigo) ?? [],
    );
    let detailsStr = "";
    if (node) {
      const codigoClicado = node.data.codigo;
      const numSelecionados = selected.has(codigoClicado)
        ? selected.size - 1
        : selected.size;
      const strSelecionados = pluralOrSingular(
        `mais ${numSelecionados} ativo$`,
        s,
        numSelecionados,
      );
      detailsStr = numSelecionados
        ? `${codigoClicado} e ${strSelecionados}`
        : codigoClicado;

      selected.add(codigoClicado);
    }
    return {
      icon: "🗑️",
      name: `<span style='color: ${getColorHex("rosa")}'>Apagar</span> ${detailsStr}`,
      disabled: !selected.size,
      action() {
        setWillDeleteAssets([...selected]);
        onDeleteAssetsConfirmOpen();
      },
    };
  };

  const getColoredName = (codigo: string) =>
    `<span style='
            display: inline-block;
            padding: 3px 2px 3px 2px;
            border-radius: 4px;
            background-color: ${getColorHex(hover)};
            color: ${strCSSColor(codigo)}
        '>
            ${codigo}
        </span>`;

  const {
    dataFlow,

    clientSideAssets,
    setClientSideEvents,

    loadedAssetsRef,
    loadedEventsRef,

    addedAssets,
    setAddedAssets,
    deletedAssets,
    setDeletedAssets,
    setModifiedAssets,

    setClientSideAssetsCellErrors,
  } = useContext(AssetPageContext);

  const eventDataRef = useRef([] as Evento[]);
  const searchRef = useRef("");

  const httpClient = useHTTP({ withCredentials: true });

  const dataSource: IServerSideDatasource = {
    async getRows(params: IServerSideGetRowsParams) {
      const {
        filterModel,
        sortModel,
        startRow = 0,
        endRow = 0,
      } = params.request;

      const filters = {
        codigo: inOrNotInSerialize(filterModel.codigo, codigos),
        emissor: inOrNotInSerialize(filterModel.emissor, emissoresStr),
        indice: inOrNotInSerialize(filterModel.indice, indices),
        taxa: percentageFilterSerialize(filterModel.taxa),
        tipo: inOrNotInSerialize(filterModel.tipo, tipos),
        valor_emissao: numberFilterSerialize(filterModel.valor_emissao),
        data_emissao: dateFilterSerialize(filterModel.data_emissao),
        inicio_rentabilidade: dateFilterSerialize(
          filterModel.inicio_rentabilidade,
        ),
        data_vencimento: dateFilterSerialize(filterModel.data_vencimento),
        apelido: textFilterSerialize(filterModel.apelido),
        isin: textFilterSerialize(filterModel.isin),
        serie: numberFilterSerialize(filterModel.serie),
        emissao: numberFilterSerialize(filterModel.emissao),
      };

      const serializedSort = JSON.stringify(sortModel);
      const serializedFilters = JSON.stringify(filters);

      const q = new URLSearchParams("");
      q.append("deslocamento", String(startRow));
      q.append("quantidade", String(endRow - startRow));
      q.append("ordenacao_ativos", serializedSort);
      q.append("filtros_ativos", serializedFilters);
      const response = await httpClient.fetch(`v1/ativos?${q.toString()}`, {
        hideToast: { success: true },
      });
      if (!response) return params.fail();

      const { ativos, total } = (await response.json()) as {
        ativos: Ativo[];
        total: number;
      };

      params.success({
        rowData: ativos.map((a) => ({
          ...a,
          emissor: a.emissor.nome,
          tipo: a.tipo.nome,
          indice: strFromIndice({
            nome: a.indice.nome,
            ativo_ipca: a.ativo_ipca ?? null,
          }),
        })),
        rowCount: total,
      });

      if (startRow === 0) {
        eventDataRef.current = [];
        loadedAssetsRef.current = {};
        loadedEventsRef.current = {};
      }
      eventDataRef.current.push(...ativos.flatMap((a) => a.fluxos));
      setClientSideEvents([...eventDataRef.current]);
      ativos.forEach((a) => {
        loadedAssetsRef.current[a.codigo] = {
          ...a,
          emissor: a.emissor.nome,
          tipo: a.tipo.nome,
          indice: strFromIndice({
            nome: a.indice.nome,
            ativo_ipca: a.ativo_ipca ?? null,
          }),
        } as any;
        a.fluxos.forEach((e) => {
          loadedEventsRef.current[e.id] = {
            ...e,
            tipo_evento: e.tipo.nome,
          } as any;
        });
      });
      onNewAssetsFetched?.(ativos, total);
    },
  };

  useEffect(() => {
    if (!editable) {
      eventDataRef.current = [];
      setClientSideEvents([]);
    }
  }, [editable]);

  useEffect(() => {
    eventDataRef.current = [];
    setClientSideEvents([]);
  }, [dataFlow]);

  const data = useMemo(() => {
    return [DataFlow.SEPARATE, DataFlow.ASSETS_DEFINE_EVENTS].includes(dataFlow)
      ? dataSource
      : clientSideAssets.map(
          (a) =>
            ({
              ...a,
              emissor: a.emissor.nome,
              tipo: a.tipo.nome,
              indice: a.indice.nome,
            }) as any,
        );
  }, [dataFlow, clientSideAssets]);

  return (
    <>
      <ValidationGrid
        colDefs={colDefs}
        data={data}
        editable={editable}
        identifier="codigo"
        cellValidators={{
          codigo: [required],
          emissor: [required, inList(emissoresStr, "Emissor inexistente")],
          indice: [
            required,
            (value) => {
              const errMsg = "Índice inválido";
              const data = parseIndiceFromCell(value ?? null);
              return !data ? errMsg : inList(indices, errMsg)(data.nome);
            },
          ],
          taxa: [required],
          tipo: [required, inList(tipos, "Tipo inválido")],
          valor_emissao: [required],
          data_emissao: [required],
          inicio_rentabilidade: [required],
          data_vencimento: [required],
        }}
        getContextMenuItems={({ defaultItems, node }) => {
          const codigo = node?.data.codigo;
          const defaultOptions = defaultItems ?? [];
          const custom = deletedAssets.find(
            (a) => a.codigo === node?.data.codigo,
          )
            ? []
            : [
                {
                  icon: "🖨️",
                  name: `${getColoredName(codigo)}: Duplicar ativo`,
                  action() {
                    setSelected(node?.data);
                    onInsertAtivosOpen();
                  },
                },
                {
                  icon: "🕒",
                  name: `${getColoredName(
                    codigo,
                  )}: <span style="color: ${getColorHex(node?.data.fluxos.length ? "laranja.main" : "verde.main")}">${
                    node?.data.fluxos.length ? "Recriar" : "Gerar"
                  }</span> eventos`,
                  action() {
                    setSelected(node?.data);
                    onGenerateEventsOpen();
                  },
                },
                {
                  icon: "➕",
                  name: `${getColoredName(codigo)}: Adicionar novos eventos`,
                  action() {
                    setSelected(node?.data);
                    onInsertEventsModalOpen();
                  },
                },
                getDeleteItem(node),
              ];
          return editable ? [...custom, ...defaultOptions] : defaultOptions;
        }}
        onReady={(ev) => {
          gridApiRef.current = ev.api;
        }}
        methodsRef={gridMethodsRef}
        onCellValidationError={(errors) =>
          setClientSideAssetsCellErrors(Object.keys(errors).length)
        }
        onClientDataChanged={(data) => {
          setAddedAssets(data.added as Ativo[]);
          setDeletedAssets(data.deleted as Ativo[]);
          setModifiedAssets(data.modified as ModificationMap<Ativo>);
        }}
      />
      <InserirAtivoModal
        ativo={selectedAsset}
        isOpen={isInsertAtivosOpen}
        ativosExistentes={codigos}
        onClose={(inserted) => {
          if (inserted.length) {
            gridMethodsRef.current?.insertRows(inserted);
            eventsGridMethodsRef.current?.insertRows(
              inserted.flatMap((a) =>
                a.fluxos.map((f) => ({
                  ...f,
                  tipo_evento: f?.tipo?.nome ?? (f as any).tipo_evento,
                })),
              ),
            );
          }
          onInsertAtivosClose();
        }}
      />
      <ConfirmModal
        isOpen={isDeleteAssetsConfirmOpen}
        onClose={onDeleteAssetsConfirmClose}
        onConfirmAction={() => {
          gridMethodsRef.current?.deleteRows([...willDeleteAssets]);
          const assets = willDeleteAssets.map(
            (a) =>
              gridApiRef.current?.getRowNode(a)?.data ??
              addedAssets.find((aa) => aa.codigo === a),
          );
          const ids = assets.flatMap((a) => a.fluxos.map((f: Evento) => f.id));
          eventsGridMethodsRef.current?.deleteRows(ids);
          setWillDeleteAssets([]);
        }}
      >
        <Text mb="12px">Deseja apagar os ativos selecionados?</Text>
        <HStack wrap="wrap">
          {willDeleteAssets.map((codigo) => {
            const color = strCSSColor(codigo);
            return (
              <Tag bgColor={hover} color={color}>
                {codigo}
              </Tag>
            );
          })}
        </HStack>
      </ConfirmModal>
      {selectedAsset && (
        <GenerateEventsModal
          ativo={selectedAsset}
          isOpen={isGenerateEventsOpen}
          onClose={onGenerateEventsClose}
          tipoEventos={tiposEventosSuportados}
          eventsGridMethodsRef={eventsGridMethodsRef}
        />
      )}
      <InserirLinhasModal
        isOpen={isInsertEventsModalOpen}
        onClose={onInsertEventsModalClose}
        title={
          selectedAsset ? (
            <Text>
              Adicionar novos eventos para o ativo{" "}
              <Text
                p="2px 4px"
                borderRadius="4px"
                as="span"
                color={strCSSColor(selectedAsset.codigo)}
              >
                {selectedAsset.codigo}
              </Text>
            </Text>
          ) : (
            ""
          )
        }
        insertAction={(amount) => {
          if (!selectedAsset) return;
          const novosEventos: Partial<Evento>[] = [];
          for (let i = 0; i < amount; i++) {
            novosEventos.push({
              id: Math.random(),
              ativo_codigo: selectedAsset.codigo,
            });
          }
          eventsGridMethodsRef.current?.insertRows(novosEventos);
        }}
      />
      {selectedAtivoIPCA &&
        (() => {
          const { ativo, value } = selectedAtivoIPCA;

          const indice = parseIndiceFromCell(value);

          if (!indice?.ativo_ipca) {
            onIPCAClose();
            return <></>;
          }

          const { ativo_ipca } = indice;

          return (
            <ConfirmModal
              title="Editar detalhes de IPCA"
              size="xs"
              isOpen={isIPCAOpen}
              onClose={onIPCAClose}
              onConfirmAction={() => {
                const newData = {
                  ...ativo,
                  indice: strFromIndice(indice) as any,
                };
                gridMethodsRef.current?.updateRows([newData]);
                onIPCAClose();
              }}
            >
              <VStack gap={0} alignItems="flex-start">
                <Text fontSize="xs" color="cinza.500">
                  Aniversário
                </Text>
                <NumberInput
                  w="100%"
                  mb="12px"
                  focusBorderColor="verde.main"
                  size="sm"
                  defaultValue={1}
                  min={1}
                  max={31}
                  step={1}
                  keepWithinRange={true}
                  clampValueOnBlur={true}
                  onChange={(_, n) => {
                    indice.ativo_ipca!.mesversario = isNaN(n) ? 15 : n;
                    const value = strFromIndice(indice);
                    setSelectedAtivoIPCA({ ativo, value });
                  }}
                  value={ativo_ipca.mesversario}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
                <VStack alignItems="stretch">
                  <Checkbox
                    size="md"
                    colorScheme="verde"
                    isChecked={ativo_ipca.ipca_2_meses}
                    onChange={({ target: { checked } }) => {
                      indice.ativo_ipca!.ipca_2_meses = checked;
                      const value = strFromIndice(indice);
                      setSelectedAtivoIPCA({ ativo, value });
                    }}
                  >
                    Segundo mês anterior
                  </Checkbox>
                  <Checkbox
                    colorScheme="verde"
                    isChecked={ativo_ipca.ipca_negativo}
                    onChange={({ target: { checked } }) => {
                      indice.ativo_ipca!.ipca_negativo = checked;
                      const value = strFromIndice(indice);
                      setSelectedAtivoIPCA({ ativo, value });
                    }}
                  >
                    Variação positiva
                  </Checkbox>
                </VStack>
              </VStack>
            </ConfirmModal>
          );
        })()}
    </>
  );
}
