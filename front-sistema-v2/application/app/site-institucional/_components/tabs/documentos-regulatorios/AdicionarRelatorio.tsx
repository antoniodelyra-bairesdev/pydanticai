"use client";

import Arquivo from "@/app/_components/misc/Arquivo";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import Hint from "@/app/_components/texto/Hint";
import { useAsync, useHTTP } from "@/lib/hooks";
import { CategoriaRelatorio, DocumentoRelatorio } from "@/lib/types/api/iv/v1";
import {
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

export type AdicionarRelatorioProps = {
  categoria: CategoriaRelatorio;
  onDocumentosAdicionados?: (documentos: DocumentoRelatorio[]) => void;
};

export default function AdicionarRelatorio({
  categoria,
  onDocumentosAdicionados,
}: AdicionarRelatorioProps) {
  const [arquivos, setArquivos] = useState<File[]>([]);
  const [nomeArquivos, setNomeArquivos] = useState<string[]>([]);

  const [enviando, iniciarEnvio] = useAsync();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const httpClient = useHTTP({ withCredentials: true });

  const processarArquivos: DragEventHandler<HTMLDivElement> = (ev) => {
    ev.preventDefault();
    const { files } = ev.dataTransfer;
    setArquivos([...arquivos, ...[...files].filter((f) => f.type)]);
    setNomeArquivos([...nomeArquivos, ...Array(files.length).fill("")]);
  };

  const enviar = () => {
    if (enviando) return;
    iniciarEnvio(async () => {
      const body = new FormData();
      arquivos.forEach((arquivo) => body.append("arquivos", arquivo));
      body.append(
        "metadados",
        JSON.stringify({
          dados: nomeArquivos.map((nome, posicao_arquivo) => ({
            nome,
            posicao_arquivo,
          })),
        }),
      );
      const response = await httpClient.fetch(
        `v1/regulatorio/categoria/${categoria.id}/relatorio`,
        { method: "POST", multipart: true, body },
      );
      if (!response.ok) return;

      onDocumentosAdicionados?.(
        (await response.json()) as DocumentoRelatorio[],
      );
    });
  };

  useEffect(() => {
    if (!isOpen) {
      setArquivos([]);
      setNomeArquivos([]);
    }
  }, [isOpen]);

  return (
    <Card
      key="add"
      bgColor="verde.main"
      color="white"
      _hover={{ bgColor: "verde.100", color: "black", cursor: "pointer" }}
      transition="0.125s all"
      onClick={onOpen}
    >
      <CardBody>
        <VStack justifyContent="center" h="100%">
          <IoAdd size="36px" />
        </VStack>
      </CardBody>
      <ConfirmModal
        isOpen={isOpen || enviando}
        onClose={() => {
          if (enviando) return;
          onClose();
        }}
        size="3xl"
        title={`Adicionar documentos na categoria "${categoria.nome}"`}
        confirmEnabled={!enviando && !nomeArquivos.some((nome) => !nome.trim())}
        onConfirmAction={enviar}
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
                        setArquivos([...arquivos]);
                        setNomeArquivos([...nomeArquivos]);
                      }}
                    />
                  </HStack>
                ))
              )}
            </VStack>
          </CardBody>
        </Card>
        <Progress
          visibility={enviando ? "visible" : "hidden"}
          isIndeterminate
          colorScheme="verde"
          h="8px"
        />
      </ConfirmModal>
    </Card>
  );
}
