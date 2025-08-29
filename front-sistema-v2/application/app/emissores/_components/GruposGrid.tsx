import ValidationGrid, {
  ValidationGridColDef,
  ValidationGridMethods,
} from "@/app/_components/grid/ValidationGrid";
import { useAsync, useHTTP } from "@/lib/hooks";
import {
  AddIcon,
  EditIcon,
  SmallCloseIcon,
  WarningIcon,
} from "@chakra-ui/icons";
import {
  AlertIcon,
  Box,
  Button,
  HStack,
  Heading,
  Input,
  Progress,
  Text,
  useDisclosure,
} from "@chakra-ui/react";
import { useEffect, useMemo, useRef, useState } from "react";
import { useEmissoresPageData } from "../provider";
import { GridApi, ICellRendererParams } from "ag-grid-community";
import { EmissorGrupo } from "@/lib/types/api/iv/v1";
import { IoSaveOutline } from "react-icons/io5";
import { getColorHex } from "@/app/theme";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import Comment from "@/app/_components/misc/Comment";
import { ValidatorFn, unique } from "@/lib/util/validation";
import { pluralOrSingular } from "@/lib/util/string";

export default function GruposGrid() {
  const [editing, setEditing] = useState(false);
  const httpClient = useHTTP({ withCredentials: true });

  const { grupos, setGrupos } = useEmissoresPageData();
  const [grupoSelecionado, setGrupoSelecionado] = useState<
    EmissorGrupo | undefined
  >();

  const { icon, color, text } = editing
    ? {
        icon: <SmallCloseIcon />,
        color: "rosa",
        text: "Desabilitar modo de edição",
      }
    : { icon: <EditIcon />, color: "azul_1", text: "Habilitar modo de edição" };

  const colDefs: ValidationGridColDef[] = [
    {
      field: "nome",
      editable: false,
      comparator: (va: string, vb: string) => va.localeCompare(vb),
      cellRenderer(params: ICellRendererParams) {
        if (!params.data) return;
        return (
          <HStack w="100%" justifyContent="space-between">
            <Text>{params.value}</Text>
            {editing && (
              <Button
                size="xs"
                onClick={() => {
                  setGrupoSelecionado(params.data);
                  onAddOpen();
                }}
              >
                <EditIcon />
              </Button>
            )}
          </HStack>
        );
      },
    },
  ];

  const apiRef = useRef<GridApi>();
  const divRef = useRef<HTMLDivElement>(null);
  const ro = new ResizeObserver(() => autofit());
  const autofit = () => apiRef.current?.sizeColumnsToFit();

  const methodsRef = useRef<ValidationGridMethods<EmissorGrupo>>();

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

  const data = useMemo(
    () =>
      Object.values(grupos).sort((ga, gb) => ga.nome.localeCompare(gb.nome)),
    [grupos],
  );

  const [loading, load] = useAsync();
  const [added, setAdded] = useState<EmissorGrupo[]>([]);
  const [edited, setEdited] = useState<EmissorGrupo[]>([]);

  const confirm = () =>
    load(async () => {
      {
        const response = await httpClient.fetch("v1/ativos/grupos/transacao", {
          method: "PUT",
          body: JSON.stringify({ modified: edited, added }),
        });
        if (!response.ok) return;
      }
      {
        const response = await httpClient.fetch("v1/ativos/grupos");
        if (!response.ok) return;

        const todosGrupos: EmissorGrupo[] = await response.json();
        setEditing(false);
        setGrupos(
          todosGrupos.reduce(
            (map, setor) => ((map[setor.nome] = setor), map),
            {} as Record<string, EmissorGrupo>,
          ),
        );
      }
    });

  const [nome, setNome] = useState(grupoSelecionado?.nome ?? "");

  useEffect(() => {
    if (isAddOpen === true) {
      setNome(grupoSelecionado?.nome ?? "");
    }
  }, [isAddOpen]);

  const [validators, setValidators] = useState<
    Partial<Record<keyof EmissorGrupo, ValidatorFn[]>>
  >({});

  useEffect(() => {
    const set = new Set(Object.values(grupos).map((g) => g.nome));
    if (grupoSelecionado) {
      set.delete(grupos[grupoSelecionado.nome]?.nome);
    }
    setValidators({
      nome: [unique(set, "O nome do setor já existe!")],
    });
  }, [grupos, grupoSelecionado]);

  const [erros, setErros] = useState(0);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        alignSelf: "stretch",
        gap: "8px",
      }}
      ref={divRef}
    >
      <Heading size="md" fontWeight="normal">
        Grupos
      </Heading>
      <HStack justifyContent="space-between">
        <HStack gap="4px">
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
        <HStack gap="4px">
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
      </HStack>
      <ValidationGrid
        colDefs={colDefs}
        data={structuredClone(data)}
        editable={editing}
        identifier="id"
        onReady={(ev) => {
          apiRef.current = ev.api;
          if (divRef.current) {
            ro.observe(divRef.current);
          }
          autofit();
        }}
        methodsRef={methodsRef}
        onClientDataChanged={({ added, modified }) => {
          setAdded(added);
          setEdited(
            Object.values(modified)
              .filter((mod) => mod.data.new !== null)
              .map((mod) => mod.data.new) as EmissorGrupo[],
          );
        }}
        onCellValidationError={(err) => setErros(Object.keys(err).length)}
        cellValidators={validators}
      />
      <Button
        isDisabled={!editing}
        size="sm"
        fontSize="xs"
        leftIcon={<AddIcon />}
        colorScheme="verde"
        onClick={() => {
          setGrupoSelecionado(undefined);
          onAddOpen();
        }}
      >
        Adicionar grupo
      </Button>
      <ConfirmModal
        title={
          grupoSelecionado
            ? `Editar ${grupoSelecionado.nome}`
            : "Adicionar grupo"
        }
        isOpen={isAddOpen}
        onClose={onAddClose}
        onConfirmAction={() => {
          if (grupoSelecionado) {
            methodsRef.current?.updateRows([
              { ...grupoSelecionado, nome: nome.trim() },
            ]);
          } else {
            methodsRef.current?.insertRows([
              { id: Math.random(), nome: nome.trim() },
            ]);
          }
        }}
        size="2xl"
        confirmEnabled={nome.trim().length > 0}
      >
        <Text fontSize="xs" mt="12px">
          Nome do grupo
        </Text>
        <Input
          size="sm"
          placeholder="Digite o nome do grupo..."
          value={nome}
          onChange={(ev) => setNome(ev.target.value)}
        />
      </ConfirmModal>
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
            Após criar um grupo você não poderá excluí-lo. Caso queira apagá-lo
            você precisará entrar em contato com o time de tecnologia.
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
