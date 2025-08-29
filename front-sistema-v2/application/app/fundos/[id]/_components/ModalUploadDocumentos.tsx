"use client";

import Arquivo from "@/app/_components/misc/Arquivo";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import Hint from "@/app/_components/texto/Hint";
import { useAsync, useHTTP } from "@/lib/hooks";
import { CategoriaRelatorio, DocumentoRelatorio } from "@/lib/types/api/iv/v1";
import { dateToStr } from "@/lib/util/string";
import { AddIcon } from "@chakra-ui/icons";
import {
  Button,
  Card,
  CardBody,
  HStack,
  Input,
  Progress,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import { DragEventHandler, useEffect, useState } from "react";
import { IoAdd } from "react-icons/io5";

export type ArquivoComTitulo = {
  arquivoLocal: File;
  data_referencia: string;
  titulo: string;
};

export type ModalUploadDocumentosProps = {
  categoria: string;
  onDocumentosAdicionados?: (documentos: ArquivoComTitulo[]) => void;
};

export default function ModalUploadDocumentos({
  onDocumentosAdicionados,
  categoria,
}: ModalUploadDocumentosProps) {
  const [arquivos, setArquivos] = useState<File[]>([]);
  const [nomeArquivos, setNomeArquivos] = useState<string[]>([]);
  const [datasReferencia, setDatasReferencia] = useState<string[]>([]);

  const { isOpen, onOpen, onClose } = useDisclosure();

  const processarArquivos: DragEventHandler<HTMLDivElement> = (ev) => {
    ev.preventDefault();
    const { files } = ev.dataTransfer;
    setArquivos([...arquivos, ...[...files].filter((f) => f.type)]);
    setDatasReferencia([
      ...datasReferencia,
      ...Array(files.length).fill(dateToStr(new Date())),
    ]);
    setNomeArquivos([...nomeArquivos, ...Array(files.length).fill("")]);
  };

  const confirmar = () => {
    onDocumentosAdicionados?.(
      arquivos.map((a, i) => ({
        arquivoLocal: a,
        data_referencia: datasReferencia[i],
        titulo: nomeArquivos[i],
      })),
    );
  };

  useEffect(() => {
    if (!isOpen) {
      setArquivos([]);
      setNomeArquivos([]);
      setDatasReferencia([]);
    }
  }, [isOpen]);

  return (
    <>
      <Button
        bgColor="cinza.200"
        h="100%"
        size="xs"
        key={-1}
        leftIcon={<AddIcon />}
        onClick={onOpen}
      >
        <Text as="span">Adicionar</Text>
      </Button>
      <ConfirmModal
        isOpen={isOpen}
        onClose={onClose}
        size="3xl"
        title={`Inserir documentos na categoria "${categoria}"`}
        confirmEnabled={
          !nomeArquivos.some((nome) => !nome.trim()) &&
          !datasReferencia.some((data) => !data.trim())
        }
        onConfirmAction={confirmar}
      >
        <Card
          mt="12px"
          variant="outline"
          fontWeight={600}
          borderColor="cinza.400"
          borderStyle="dashed"
          borderWidth="2px"
          bgColor="cinza.200"
          onDragOver={(ev) => ev.preventDefault()}
          onDrop={processarArquivos}
        >
          <CardBody>
            <VStack alignItems="stretch">
              {arquivos.length === 0 ? (
                <VStack minH="144px" flex={1} justifyContent="center">
                  <Text fontSize="lg" color="cinza.400">
                    Arraste os arquivos aqui
                  </Text>
                </VStack>
              ) : (
                arquivos.map((arquivo, i) => (
                  <HStack key={i} bgColor="cinza.50" p="4px 8px">
                    <VStack alignItems="flex-start" gap={0}>
                      <Hint>Data referência</Hint>
                      <Input
                        isInvalid={!datasReferencia[i].trim()}
                        onChange={(ev) => {
                          datasReferencia[i] = ev.target.value;
                          setDatasReferencia([...datasReferencia]);
                        }}
                        bgColor="white"
                        value={datasReferencia[i]}
                        type="date"
                      />
                    </VStack>
                    <VStack alignItems="flex-start" flex={1} gap={0}>
                      <Hint>Nome do documento</Hint>
                      <Input
                        isInvalid={!nomeArquivos[i].trim()}
                        onChange={(ev) => {
                          nomeArquivos[i] = ev.target.value;
                          setNomeArquivos([...nomeArquivos]);
                        }}
                        bgColor="white"
                        value={nomeArquivos[i]}
                      />
                    </VStack>
                    <Arquivo
                      arquivo={{
                        id: String(Math.random()),
                        nome: arquivo.name,
                        extensao: arquivo.type,
                      }}
                      permitirDownload={false}
                      onDelete={() => {
                        arquivos.splice(i, 1);
                        nomeArquivos.splice(i, 1);
                        datasReferencia.splice(i, 1);
                        setArquivos([...arquivos]);
                        setNomeArquivos([...nomeArquivos]);
                        setDatasReferencia([...datasReferencia]);
                      }}
                    />
                  </HStack>
                ))
              )}
            </VStack>
          </CardBody>
        </Card>
      </ConfirmModal>
    </>
  );
}
