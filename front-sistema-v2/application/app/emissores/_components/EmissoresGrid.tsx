import ValidationGrid, {
  ValidationGridColDef,
  ValidationGridMethods,
} from "@/app/_components/grid/ValidationGrid";
import { getColorHex } from "@/app/theme";
import { useAsync, useHTTP } from "@/lib/hooks";
import { Emissor, EmissorGrupo } from "@/lib/types/api/iv/v1";
import {
  AddIcon,
  EditIcon,
  SmallCloseIcon,
  WarningIcon,
} from "@chakra-ui/icons";
import {
  Box,
  Button,
  HStack,
  Heading,
  Icon,
  Progress,
  Tag,
  Text,
  useDisclosure,
} from "@chakra-ui/react";
import {
  GridApi,
  ICellRendererParams,
  IServerSideDatasource,
  RowClassParams,
  RowStyle,
} from "ag-grid-community";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  IoCaretDown,
  IoCaretForward,
  IoCaretUp,
  IoLink,
  IoPerson,
  IoPersonCircleOutline,
  IoPersonOutline,
  IoSaveOutline,
} from "react-icons/io5";
import { useEmissoresPageData } from "../provider";
import { getIcon } from "./SetoresGrid";
import Link from "next/link";
import { listColDef } from "@/app/_components/grid/colDefs";
import { inList, required } from "@/lib/util/validation";
import { pluralOrSingular } from "@/lib/util/string";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import Comment from "@/app/_components/misc/Comment";

export type EmissoresGridRow = {
  id: number;
  cnpj: string;
  nome: string;

  grupo_nome?: string;
  setor_nome?: string;
  analista_credito_nome?: string;

  codigo_cvm?: string;
  tier?: string;
};

export type UpdateEmissorBody = {
  id: number;
  nome: string;
  cnpj: string;

  codigo_cvm: number | null;
  tier: number | null;

  grupo_id: number | null;
  setor_id: number | null;
  analista_credito_id: number | null;
};

export type InsertEmissorBody = Omit<UpdateEmissorBody, "id">;

const DISABLED_COLOR = getColorHex("cinza.main") + "D6";

export default function EmissoresGrid() {
  const [editing, setEditing] = useState(false);
  const httpClient = useHTTP({ withCredentials: true });

  const { icon, color, text } = editing
    ? {
        icon: <SmallCloseIcon />,
        color: "rosa",
        text: "Desabilitar modo de edição",
      }
    : { icon: <EditIcon />, color: "azul_1", text: "Habilitar modo de edição" };

  const { analistas, grupos, setores } = useEmissoresPageData();

  const setorRenderer = useCallback(
    (params: ICellRendererParams) => {
      const setor_nome = params.value;
      if (!params.value) return;
      const icon = getIcon(setores[setor_nome ?? 0]?.sistema_icone ?? "");
      return (
        <Text>
          {icon && (
            <Icon
              as={icon}
              color="verde.main"
              verticalAlign="center"
              mr="8px"
            />
          )}
          {String(params.value)}
        </Text>
      );
    },
    [setores],
  );

  const analistaRenderer = useCallback(
    (params: ICellRendererParams) => {
      if (!params.value) return;
      return (
        <HStack gap="4px" p={0}>
          <Icon as={IoPersonCircleOutline} verticalAlign="center" />
          <Text>{params.value}</Text>
        </HStack>
      );
    },
    [analistas],
  );

  const tierRenderer = useCallback((params: ICellRendererParams) => {
    if (!params.value) return;
    const tier = Number(params.value);
    const [icon, color] =
      tier && tier >= 1 && tier <= 3
        ? ((
            {
              1: [IoCaretUp, "rosa.main"],
              2: [IoCaretForward, "amarelo.main"],
              3: [IoCaretDown, "verde.main"],
            } as const
          )[tier] ?? [])
        : [];
    return (
      <Text>
        {icon && color && (
          <Icon as={icon} color={color} verticalAlign="center" />
        )}
        {params.value}
      </Text>
    );
  }, []);

  const colDefs = useMemo(
    () =>
      [
        { field: "cnpj", headerName: "CNPJ", width: 120 },
        {
          field: "nome",
          cellRenderer: ({ value, data }: ICellRendererParams) => {
            return (
              <HStack w="100%" role="group" position="relative">
                <Text>{value}</Text>
                <Tag
                  position="absolute"
                  right={0}
                  display={editing ? "none" : "block"}
                  visibility="hidden"
                  _groupHover={{ visibility: "visible" }}
                  key="abrir"
                  bgColor="cinza.100"
                  color="cinza.600"
                >
                  <Link
                    href={"/emissores/" + data.id ?? "invalido"}
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
          field: "grupo_nome",
          headerName: "Grupo",
          valueToString: ({ grupo_nome }: EmissoresGridRow) => grupo_nome ?? "",
          ...listColDef(Object.keys(grupos)),
        },
        {
          field: "setor_nome",
          headerName: "Setor",
          valueToString: ({ setor_nome }: EmissoresGridRow) => setor_nome ?? "",
          ...listColDef(Object.keys(setores), { cellRenderer: setorRenderer }),
          cellRenderer: setorRenderer,
        },
        {
          field: "analista_credito_nome",
          headerName: "Analista alocado(a)",
          valueToString: ({ analista_credito_nome }: EmissoresGridRow) =>
            analistas[analista_credito_nome ?? ""]?.user.nome ?? "",
          ...listColDef(Object.keys(analistas), {
            cellRenderer: analistaRenderer,
          }),
          cellRenderer: analistaRenderer,
        },
        {
          field: "tier",
          headerName: "Tier",
          ...listColDef(["1", "2", "3"], { cellRenderer: tierRenderer }),
          cellRenderer: tierRenderer,
          width: 74,
        },
        { field: "codigo_cvm", headerName: "Código CVM", width: 120 },
      ] as ValidationGridColDef[],
    [analistas, grupos, setores, editing],
  );

  const dataSource: IServerSideDatasource = {
    async getRows(params) {
      const { startRow = 0, endRow = 0 } = params.request;
      const q = new URLSearchParams("");
      q.append("deslocamento", String(startRow));
      q.append("quantidade", String(endRow - startRow));
      const response = await httpClient.fetch(
        `v1/ativos/emissores?${q.toString()}`,
        { hideToast: { success: true } },
      );
      if (!response.ok) return params.fail();
      const { emissores, total } = (await response.json()) as {
        emissores: Emissor[];
        total: number;
      };
      params.success({
        rowData: emissores.map((emissor) => {
          const { id, cnpj, nome } = emissor;
          const emissorRow: EmissoresGridRow = {
            id,
            cnpj,
            nome,
            grupo_nome: emissor.grupo?.nome,
            setor_nome: emissor.setor?.nome,
            analista_credito_nome: emissor.analista_credito?.user.nome,
            codigo_cvm: String(emissor.codigo_cvm ?? ""),
            tier: String(emissor.tier ?? ""),
          };
          return emissorRow;
        }),
        rowCount: total,
      });
    },
  };

  const getRowStyle = ({ data }: RowClassParams<EmissoresGridRow>) => {
    if (!data) return;
    const { grupo_nome, setor_nome } = data as EmissoresGridRow;
    if (grupo_nome && setor_nome) return;
    return {
      "background-color": DISABLED_COLOR,
    };
  };

  const apiRef = useRef<GridApi>();
  const divRef = useRef<HTMLDivElement>(null);
  const ro = new ResizeObserver(() => autofit());
  const autofit = () => apiRef.current?.sizeColumnsToFit();

  const methodsRef = useRef<ValidationGridMethods<EmissoresGridRow>>();

  const {
    isOpen: isAddOpen,
    onOpen: onAddOpen,
    onClose: onAddClose,
  } = useDisclosure();
  const {
    isOpen: isSaveOpen,
    onOpen: onSaveOpen,
    onClose: onSaveClose,
  } = useDisclosure();

  const [loading, load] = useAsync();
  const [added, setAdded] = useState<EmissoresGridRow[]>([]);
  const [edited, setEdited] = useState<EmissoresGridRow[]>([]);

  const confirm = () =>
    load(async () => {
      const modifiedBody: UpdateEmissorBody[] = edited.map(
        ({
          id,
          cnpj,
          nome,
          codigo_cvm,
          tier,
          grupo_nome,
          setor_nome,
          analista_credito_nome,
        }) => ({
          id,
          cnpj,
          nome,

          codigo_cvm:
            codigo_cvm || isNaN(Number(codigo_cvm)) ? null : Number(codigo_cvm),
          tier: tier || isNaN(Number(tier)) ? null : Number(tier),

          grupo_id: grupos[grupo_nome ?? ""]?.id ?? null,
          setor_id: setores[setor_nome ?? ""]?.id ?? null,
          analista_credito_id:
            analistas[analista_credito_nome ?? ""]?.id ?? null,
        }),
      );
      const addedBody: InsertEmissorBody[] = added.map(
        ({
          cnpj,
          nome,
          codigo_cvm,
          tier,
          grupo_nome,
          setor_nome,
          analista_credito_nome,
        }) => ({
          cnpj,
          nome,
          codigo_cvm:
            codigo_cvm || isNaN(Number(codigo_cvm)) ? null : Number(codigo_cvm),
          tier: tier || isNaN(Number(tier)) ? null : Number(tier),
          grupo_id: grupos[grupo_nome ?? ""]?.id ?? null,
          setor_id: setores[setor_nome ?? ""]?.id ?? null,
          analista_credito_id:
            analistas[analista_credito_nome ?? ""]?.id ?? null,
        }),
      );
      const response = await httpClient.fetch("v1/ativos/emissores/transacao", {
        method: "PUT",
        body: JSON.stringify({
          modified: modifiedBody,
          added: addedBody,
        }),
      });
      if (!response.ok) return;
      setEditing(false);
      methodsRef.current?.resetClientSideData();
    });

  const [erros, setErros] = useState(0);

  const add = () => {
    methodsRef.current?.insertRows([{ id: Math.random() }]);
  };

  const grid = useMemo(
    () => (
      <ValidationGrid
        colDefs={colDefs}
        data={dataSource}
        editable={editing}
        identifier="id"
        getRowStyle={getRowStyle}
        onReady={(ev) => {
          apiRef.current = ev.api;
          if (divRef.current) {
            ro.observe(divRef.current);
          }
          autofit();
        }}
        cellValidators={{
          cnpj: [required],
          nome: [required],
          grupo_nome: [
            inList(
              [...Object.values(grupos).map((g) => g.nome), ""],
              "O grupo selecionado não existe",
            ),
          ],
          setor_nome: [
            inList(
              [...Object.values(setores).map((s) => s.nome), ""],
              "O setor selecionado não existe",
            ),
          ],
          tier: [inList(["1", "2", "3", ""], "Tier inválido")],
        }}
        onCellValidationError={(err) => setErros(Object.keys(err).length)}
        onClientDataChanged={({ added, modified }) => {
          setAdded(added);
          setEdited(
            Object.values(modified)
              .filter((mod) => mod.data.new !== null)
              .map((mod) => mod.data.new) as EmissoresGridRow[],
          );
        }}
        methodsRef={methodsRef}
      />
    ),
    [analistas, grupos, setores, editing],
  );

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        alignSelf: "stretch",
        gap: "8px",
        width: "100%",
      }}
      ref={divRef}
    >
      <Heading size="md" fontWeight="normal">
        Emissores cadastrados
      </Heading>
      <HStack justifyContent="space-between">
        <HStack>
          <Button
            key="editar"
            size="xs"
            leftIcon={icon}
            colorScheme={color}
            onClick={() => setEditing(!editing)}
          >
            {text}
          </Button>
          {editing && (
            <>
              <Button
                key="salvar"
                isDisabled={
                  (added.length === 0 && edited.length === 0) || erros > 0
                }
                size="xs"
                leftIcon={<IoSaveOutline />}
                colorScheme="azul_1"
                onClick={onSaveOpen}
              >
                Salvar
              </Button>
              <Button
                key="novo"
                size="xs"
                leftIcon={<AddIcon />}
                onClick={add}
                colorScheme="verde"
              >
                Adicionar emissor
              </Button>
            </>
          )}
        </HStack>
        {erros > 0 && (
          <Text color="rosa.main" fontSize="12px">
            <WarningIcon />{" "}
            {pluralOrSingular(
              `${erros} erro$`,
              { $: { plural: "s", singular: "" } },
              erros,
            )}
          </Text>
        )}
        <HStack>
          {added.length > 0 && (
            <HStack
              key="added"
              w="36px"
              h="24px"
              border="1px solid"
              borderColor="cinza.main"
              borderRadius="4px"
              bgColor={getColorHex("verde.50")}
              color="verde.main"
              fontSize="12px"
              justifyContent="center"
              gap={0}
            >
              <Text as="span">+{added.length}</Text>
            </HStack>
          )}
          {edited.length > 0 && (
            <HStack
              key="edited"
              w="36px"
              h="24px"
              border="1px solid"
              borderColor="cinza.main"
              borderRadius="4px"
              bgColor={getColorHex("amarelo.50")}
              color="amarelo.900"
              fontSize="12px"
              justifyContent="center"
              gap={0}
            >
              <EditIcon fontSize="8px" mr="2px" />
              <Text as="span">{edited.length}</Text>
            </HStack>
          )}
        </HStack>
        <HStack gap="16px">
          <HStack>
            <Box
              borderWidth="1px"
              borderStyle="solid"
              borderColor="cinza.400"
              w="30px"
              h="14px"
            />
            <Text fontSize="xs">Emissor cadastrado</Text>
          </HStack>
          <HStack>
            <Box
              borderWidth="1px"
              borderStyle="solid"
              borderColor="cinza.400"
              bgColor={DISABLED_COLOR}
              w="30px"
              h="14px"
            />
            <Text fontSize="xs">Emissor sem grupo ou setor</Text>
          </HStack>
        </HStack>
      </HStack>
      {grid}
      <ConfirmModal
        isOpen={loading ? true : isSaveOpen}
        onClose={onSaveClose}
        title="Salvar alterações?"
        onConfirmAction={confirm}
        confirmEnabled={!loading}
      >
        <Box>
          <Comment fontSize="sm">
            <strong>Aviso: </strong>
            Após cadastrar um novo emissor você não poderá excluí-lo. Caso
            queira apagá-lo você precisará entrar em contato com o time de
            tecnologia.
          </Comment>
          <Text mt="12px" fontSize="sm">
            Deseja prosseguir?
          </Text>
        </Box>
        <Progress
          visibility={loading ? "visible" : "hidden"}
          isIndeterminate={true}
          colorScheme="verde"
        />
      </ConfirmModal>
    </div>
  );
}
