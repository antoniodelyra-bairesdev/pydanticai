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
  Box,
  Button,
  HStack,
  Heading,
  Icon,
  Progress,
  Text,
  useDisclosure,
} from "@chakra-ui/react";
import { GridApi, ICellRendererParams } from "ag-grid-community";
import { useEffect, useMemo, useRef, useState } from "react";
import * as AllIcons from "react-icons/io5";
import { useEmissoresPageData } from "../provider";
import ModalSetor from "./AdicionarSetor";
import { EmissorSetor } from "@/lib/types/api/iv/v1";
import { IconType } from "react-icons";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import Comment from "@/app/_components/misc/Comment";
import { getColorHex } from "@/app/theme";
import { ValidatorFn, unique } from "@/lib/util/validation";
import { pluralOrSingular } from "@/lib/util/string";

export const getIcon = (name: string) => {
  const fullName = "Io" + name + "Outline";
  const icon = (AllIcons as Record<string, IconType>)[
    fullName
  ] as IconType | null;
  return icon ?? null;
};

export default function SetoresGrid() {
  const [editing, setEditing] = useState(false);
  const httpClient = useHTTP({ withCredentials: true });

  const { setores, setSetores } = useEmissoresPageData();
  const [setorSelecionado, setSetorSelecionado] = useState<
    EmissorSetor | undefined
  >();

  const { icon, color, text } = editing
    ? {
        icon: <SmallCloseIcon />,
        color: "rosa",
        text: "Desabilitar modo de edição",
      }
    : { icon: <EditIcon />, color: "azul_1", text: "Habilitar modo de edição" };

  const colDefs = useMemo(
    () =>
      [
        {
          width: 16,
          editable: false,
          valueGetter() {
            return;
          },
          field: "sistema_icone",
          headerName: "",
          cellRenderer(params: ICellRendererParams) {
            const icon = getIcon(params.data.sistema_icone ?? "");
            if (!params.data || !icon) return <></>;
            return (
              <Icon
                as={icon}
                color="verde.main"
                verticalAlign="center"
                mr="8px"
              />
            );
          },
        },
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
                      setSetorSelecionado(params.data);
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
      ] as ValidationGridColDef[],
    [editing],
  );

  const apiRef = useRef<GridApi>();
  const divRef = useRef<HTMLDivElement>(null);
  const ro = new ResizeObserver(() => autofit());
  const autofit = () => apiRef.current?.sizeColumnsToFit();

  const methodsRef = useRef<ValidationGridMethods<EmissorSetor>>();

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
      Object.values(setores).sort((sa, sb) => sa.nome.localeCompare(sb.nome)),
    [setores],
  );

  const [loading, load] = useAsync();
  const [added, setAdded] = useState<EmissorSetor[]>([]);
  const [edited, setEdited] = useState<EmissorSetor[]>([]);

  const confirm = () =>
    load(async () => {
      {
        const response = await httpClient.fetch("v1/ativos/setores/transacao", {
          method: "PUT",
          body: JSON.stringify({ modified: edited, added }),
        });
        if (!response.ok) return;
      }
      {
        const response = await httpClient.fetch(
          "v1/ativos/setores?with_sys_data=true",
        );
        if (!response.ok) return;

        const todosSetores: EmissorSetor[] = await response.json();
        setEditing(false);
        setSetores(
          todosSetores.reduce(
            (map, setor) => ((map[setor.nome] = setor), map),
            {} as Record<string, EmissorSetor>,
          ),
        );
      }
    });

  const [validators, setValidators] = useState<
    Partial<Record<keyof EmissorSetor, ValidatorFn[]>>
  >({});

  useEffect(() => {
    const set = new Set(Object.values(setores).map((s) => s.nome));
    if (setorSelecionado) {
      set.delete(setores[setorSelecionado.nome]?.nome);
    }
    setValidators({
      nome: [unique(set, "O nome do setor já existe!")],
    });
  }, [setores, setorSelecionado]);

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
        Setores
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
            <Button
              key="salvar"
              isDisabled={
                (added.length === 0 && edited.length === 0) || erros > 0
              }
              size="xs"
              leftIcon={<AllIcons.IoSaveOutline />}
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
              .map((mod) => mod.data.new) as EmissorSetor[],
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
          setSetorSelecionado(undefined);
          onAddOpen();
        }}
      >
        Adicionar setor
      </Button>
      <ModalSetor
        setor={setorSelecionado}
        isOpen={isAddOpen}
        onClose={onAddClose}
        onConfirm={(setor, action) => {
          if (action === "add") {
            methodsRef.current?.insertRows([setor]);
          } else {
            methodsRef.current?.updateRows([setor]);
          }
        }}
      />
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
            Após criar um setor você não poderá excluí-lo. Caso queira apagá-lo
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
