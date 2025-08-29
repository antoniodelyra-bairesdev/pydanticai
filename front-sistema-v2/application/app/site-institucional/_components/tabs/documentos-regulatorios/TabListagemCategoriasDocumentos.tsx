"use client";

import { CategoriaRelatorio, PlanoDeFundo } from "@/lib/types/api/iv/v1";
import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box,
  Button,
  HStack,
  Heading,
  Input,
  Progress,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import { Fragment, MouseEvent, useState } from "react";
import CategoriaDocumentos from "./CategoriaDocumentos";
import { AddIcon } from "@chakra-ui/icons";
import { IoCamera, IoCheckmark, IoMenu, IoTrash } from "react-icons/io5";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { useAsync, useHTTP, useUser } from "@/lib/hooks";
import Hint from "@/app/_components/texto/Hint";

export type ListagemCategoriasDocumentosProps = {
  categoriasIniciais: CategoriaRelatorio[];
  listaPlanosDeFundo: PlanoDeFundo[];
};

export default function TabListagemCategoriasDocumentos({
  categoriasIniciais,
  listaPlanosDeFundo,
}: ListagemCategoriasDocumentosProps) {
  const [categorias, setCategorias] = useState(categoriasIniciais);

  const [marcadaParaDelecao, setMarcadaParaDelecao] =
    useState<CategoriaRelatorio | null>(null);
  const [novoNome, setNovoNome] = useState("");

  const [criando, iniciarCriacao] = useAsync();
  const [deletando, iniciarDelecao] = useAsync();
  const httpClient = useHTTP({ withCredentials: true });

  const {
    isOpen: isAdicionarOpen,
    onOpen: onAdicionarOpen,
    onClose: onAdicionarClose,
  } = useDisclosure();

  const {
    isOpen: isPlanoDeFundoOpen,
    onOpen: _onPlanoDeFundoOpen,
    onClose: _onPlanoDeFundoClose,
  } = useDisclosure();

  const criar = () => {
    if (criando || !novoNome.trim()) return;
    iniciarCriacao(async () => {
      const body = JSON.stringify({ nome: novoNome });
      const response = await httpClient.fetch("v1/regulatorio/categoria", {
        method: "POST",
        body,
      });
      if (!response.ok) return;
      const categoria = (await response.json()) as CategoriaRelatorio;
      setNovoNome("");
      setCategorias([...categorias, categoria]);
    });
  };

  const [reordenando, iniciarReordenacao] = useAsync();

  const salvarOrdem = (novaOrdem: { id: number; ordem: number }[]) => {
    if (reordenando) return;
    iniciarReordenacao(async () => {
      const body = JSON.stringify(
        novaOrdem.map((c) => ({ id: c.id, ordem: c.ordem })),
      );
      await httpClient.fetch("v1/regulatorio/categoria", {
        method: "PUT",
        body,
      });
    });
  };

  const [dragging, setDragging] = useState(-1);

  const reorder = (newPos: number) => () => {
    categorias.splice(newPos, 0, categorias[dragging]);
    categorias.splice(dragging + Number(dragging > newPos), 1);
    const novaOrdem = categorias.map((c, i) => ({ ...c, ordem: i + 1 }));
    salvarOrdem(novaOrdem);
    setCategorias(novaOrdem);
  };

  const [categoriaSelecionada, setCategoriaSelecionada] = useState(-1);

  const onPlanoDeFundoOpen = (i: number) => {
    setCategoriaSelecionada(i);
    setPfSelecionado(categorias[i].plano_de_fundo?.id ?? -1);
    _onPlanoDeFundoOpen();
  };

  const onPlanoDeFundoClose = () => {
    setCategoriaSelecionada(-1);
    setPfSelecionado(-1);
    _onPlanoDeFundoClose();
  };

  const alterarPlanoDeFundo = (i: number) => (ev: MouseEvent) => {
    ev.preventDefault();
    onPlanoDeFundoOpen(i);
  };

  const [alterandoPlanoDeFundo, iniciarAlteracaoPlanoDeFundo] = useAsync();
  const [pfSelecionado, setPfSelecionado] = useState(-1);

  const { user } = useUser();
  const podeAlterarDocs = user?.roles.some(
    (r) => r.nome === "Site Institucional - Alterar documentos regulatórios",
  );

  return (
    <Accordion allowMultiple defaultIndex={categorias.map((_, i) => i)}>
      {categorias.map((categoria, i) => (
        <Fragment key={i}>
          <Box
            transition="0.25s all"
            h={dragging !== -1 ? "12px" : 0}
            opacity={+(dragging !== -1)}
            onDragOver={(ev) => ev.preventDefault()}
            onDrop={reorder(i)}
            w="100%"
            borderRadius="4px"
            border="1px dashed"
            borderColor="azul_3.main"
            bgColor="azul_3.50"
            mb="8px"
          />
          <AccordionItem border="none" mb="8px">
            <AccordionButton
              borderTopRadius="8px"
              draggable
              onDragStart={() => setDragging(i)}
              onDragEnd={() => setDragging(-1)}
              p={0}
              overflow="hidden"
              bgSize="cover"
              bgImage={categoria.plano_de_fundo?.conteudo_b64 ?? ""}
              _hover={{}}
            >
              <Box
                w="100%"
                p="8px 16px"
                position="relative"
                bgColor={
                  categoria.plano_de_fundo?.conteudo_b64
                    ? "blackAlpha.400"
                    : "azul_1.50"
                }
                color={
                  categoria.plano_de_fundo?.conteudo_b64 ? "white" : "black"
                }
              >
                <HStack justifyContent="space-between" w="100%">
                  <HStack gap="12px">
                    <IoMenu />
                    <Heading size="md">
                      {i + 1} - {categoria.nome}
                    </Heading>
                  </HStack>
                  <HStack>
                    {podeAlterarDocs && (
                      <Button
                        onClick={alterarPlanoDeFundo(i)}
                        size="xs"
                        leftIcon={<IoCamera />}
                      >
                        Alterar plano de fundo
                      </Button>
                    )}
                    <AccordionIcon />
                  </HStack>
                </HStack>
              </Box>
            </AccordionButton>
            <AccordionPanel bgColor="cinza.100" borderBottomRadius="8px">
              <CategoriaDocumentos categoria={categoria} />
              {podeAlterarDocs && (
                <HStack justifyContent="flex-end">
                  <Button
                    colorScheme="rosa"
                    mt="12px"
                    size="sm"
                    leftIcon={<IoTrash />}
                    onClick={() => setMarcadaParaDelecao(categoria)}
                  >
                    Excluir categoria
                  </Button>
                </HStack>
              )}
            </AccordionPanel>
          </AccordionItem>
        </Fragment>
      ))}
      <Box
        transition="0.25s all"
        h={dragging !== -1 ? "12px" : 0}
        opacity={+(dragging !== -1)}
        onDragOver={(ev) => ev.preventDefault()}
        onDrop={reorder(categorias.length)}
        w="100%"
        borderRadius="4px"
        border="1px dashed"
        borderColor="azul_3.main"
        bgColor="azul_3.50"
        mb="8px"
      />
      {podeAlterarDocs && (
        <Button
          colorScheme="verde"
          mt="12px"
          size="sm"
          leftIcon={<AddIcon />}
          onClick={onAdicionarOpen}
        >
          Adicionar categoria
        </Button>
      )}
      <ConfirmModal
        title="Adicionar nova categoria?"
        isOpen={isAdicionarOpen}
        onClose={() => {
          if (criando) return;
          onAdicionarClose();
        }}
        confirmEnabled={!criando}
        confirmContent="Criar"
        onConfirmAction={criar}
      >
        <VStack gap={0} alignItems="flex-start">
          <Hint>Nome da categoria</Hint>
          <Input
            onChange={(ev) => setNovoNome(ev.target.value)}
            value={novoNome}
          />
        </VStack>
      </ConfirmModal>
      <ConfirmModal
        isOpen={!!marcadaParaDelecao || deletando}
        onClose={() => {
          if (deletando) return;
          setMarcadaParaDelecao(null);
        }}
        title={
          marcadaParaDelecao
            ? `Deseja remover a categoria "${marcadaParaDelecao.nome}"?`
            : "Removendo..."
        }
        onConfirmAction={() => {
          if (deletando || !marcadaParaDelecao) return;
          iniciarDelecao(async () => {
            const response = await httpClient.fetch(
              "v1/regulatorio/categoria/" + marcadaParaDelecao.id,
              { method: "DELETE" },
            );
            if (!response.ok) return;
            const pos = categorias.findIndex(
              (c) => c.id === marcadaParaDelecao.id,
            );
            if (pos === -1) return;
            categorias.splice(pos, 1);
            setCategorias([...categorias]);
          });
        }}
        confirmEnabled={!!marcadaParaDelecao && !deletando}
        size="3xl"
      >
        {deletando ? (
          <Progress
            isIndeterminate
            colorScheme="verde"
            visibility={deletando ? "visible" : "hidden"}
          />
        ) : (
          <>
            <Text>
              Todos os documentos relacionados a esta categoria serão apagados.
              Você tem certeza que quer continuar?
            </Text>
            <Text mt="12px" fontWeight={600}>
              Esta ação não poderá ser desfeita.
            </Text>
          </>
        )}
      </ConfirmModal>
      <ConfirmModal
        title="Trocar plano de fundo"
        isOpen={isPlanoDeFundoOpen}
        onClose={() => {}}
        onConfirmAction={() => {
          if (alterandoPlanoDeFundo) return;
          iniciarAlteracaoPlanoDeFundo(async () => {
            const response = await httpClient.fetch(
              `v1/regulatorio/categoria/plano-de-fundo?categoria_id=${categorias[categoriaSelecionada].id}&plano_de_fundo_id=${pfSelecionado > 0 ? pfSelecionado : ""}`,
              { method: "PUT" },
            );
            if (!response.ok) return;
            categorias[categoriaSelecionada].plano_de_fundo =
              listaPlanosDeFundo.find((pf) => pf.id === pfSelecionado) ?? null;
            setCategorias([...categorias]);
            onPlanoDeFundoClose();
          });
        }}
        size="4xl"
        confirmEnabled={!alterandoPlanoDeFundo}
        onCancelAction={() => {
          if (alterandoPlanoDeFundo) return;
          onPlanoDeFundoClose();
        }}
      >
        <HStack flexWrap="wrap">
          {listaPlanosDeFundo.map((pf) => (
            <Box
              key={pf.id}
              onClick={() =>
                setPfSelecionado(pf.id === pfSelecionado ? -1 : pf.id)
              }
              bgImage={pf.conteudo_b64}
              cursor="pointer"
              w="192px"
              h="192px"
              borderRadius="12px"
              overflow="hidden"
              bgSize="cover"
            >
              {pf.id === pfSelecionado && (
                <VStack
                  justifyContent="center"
                  w="100%"
                  h="100%"
                  bgColor="blackAlpha.600"
                  color="white"
                >
                  <IoCheckmark size="32px" />
                </VStack>
              )}
            </Box>
          ))}
        </HStack>
      </ConfirmModal>
    </Accordion>
  );
}
