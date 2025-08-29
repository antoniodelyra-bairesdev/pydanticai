import { HStack, Tab, TabList, Tabs, VStack } from "@chakra-ui/react";
import { useFundoDetalhes } from "../_providers/FundoDetalhesProvider";
import {
  FundoClassificacaoDocumento,
  FundoDocumento,
} from "@/lib/types/api/iv/v1";
import { useCallback, useEffect, useState } from "react";
import WrapperArquivo, { EstadoArquivoEnum } from "./WrapperArquivo";
import ModalUploadDocumentos, {
  ArquivoComTitulo,
} from "./ModalUploadDocumentos";

export type DocumentosConteudoProps = {
  categorias_documentos: FundoClassificacaoDocumento[];
  onDocumentosChange: (docs: DocumentoComEstado[]) => void;
};

export type DocumentoComEstado = FundoDocumento & {
  estado: EstadoArquivoEnum;
  categoria: number;
  arquivoLocal?: File;
};

export default function DocumentosConteudo({
  categorias_documentos,
  onDocumentosChange,
}: DocumentosConteudoProps) {
  const { editando, fundoAtualizado } = useFundoDetalhes();

  const [tab, setTab] = useState(0);

  const iniciais = useCallback(
    () =>
      fundoAtualizado.documentos.flatMap(({ arquivos, classificacao }) =>
        arquivos.map(
          (a) =>
            ({
              ...a,
              categoria: classificacao.id,
              estado: EstadoArquivoEnum.normal,
            }) as DocumentoComEstado,
        ),
      ),
    [editando],
  );

  const [documentosFundo, setDocumentosFundo] = useState(iniciais());

  useEffect(() => {
    onDocumentosChange(documentosFundo);
  }, [documentosFundo]);

  useEffect(() => {
    if (editando) return;
    setDocumentosFundo(iniciais());
  }, [editando]);

  const reversaoDocumento = useCallback(
    (idDoc: number) => {
      const docIndex = documentosFundo.findIndex((d) => d.id === idDoc);
      if (docIndex === -1) return;
      const doc = documentosFundo[docIndex];
      if (doc.estado === EstadoArquivoEnum.normal) return;
      if (doc.estado === EstadoArquivoEnum.inserir) {
        documentosFundo.splice(docIndex, 1);
        setDocumentosFundo([...documentosFundo]);
        return;
      }
      if (doc.estado === EstadoArquivoEnum.remover) {
        doc.estado = EstadoArquivoEnum.normal;
        setDocumentosFundo([...documentosFundo]);
      }
    },
    [documentosFundo],
  );

  const insercaoDocumento = useCallback(
    (docs: ArquivoComTitulo[]) => {
      docs.forEach((doc) => {
        documentosFundo.push({
          ...doc,
          id: Math.random(),
          criado_em: new Date().toISOString(),
          arquivo: {
            extensao: doc.arquivoLocal.type,
            id: String(Math.random()),
            nome: doc.arquivoLocal.name,
          },
          estado: EstadoArquivoEnum.inserir,
          categoria: categorias_documentos[tab].id,
        });
      });
      setDocumentosFundo([...documentosFundo]);
    },
    [documentosFundo, tab],
  );

  const remocaoDocumento = useCallback(
    (idDoc: number) => {
      const doc = documentosFundo.find((d) => d.id === idDoc);
      if (!doc) return;
      doc.estado = EstadoArquivoEnum.remover;
      setDocumentosFundo([...documentosFundo]);
    },
    [documentosFundo],
  );

  return (
    <HStack gap={0} alignItems="stretch" minH="144px">
      <Tabs
        variant="enclosed-colored"
        size="sm"
        borderRight="1px solid"
        borderColor="cinza.main"
        bgColor="azul_1.50"
        overflow="hidden"
        onChange={setTab}
      >
        <TabList>
          <VStack ml="-1px" mr="-1px" gap={0} alignItems="stretch">
            {categorias_documentos.map(({ id, nome }) => (
              <Tab
                key={id}
                fontWeight={600}
                color="cinza.500"
                _selected={{
                  borderTop: "2px solid",
                  bgColor: "white",
                  color: "azul_3.main",
                }}
              >
                {nome} (
                {documentosFundo.filter((d) => d.categoria === id).length ?? 0})
              </Tab>
            ))}
          </VStack>
        </TabList>
      </Tabs>
      <HStack flex={1} alignItems="stretch" p="12px">
        {documentosFundo
          .filter((d) => d.categoria === categorias_documentos[tab].id)
          .map((d) => (
            <WrapperArquivo
              key={d.id}
              rotulo={d.titulo ?? undefined}
              arquivo={d.arquivo}
              onDelete={editando ? () => remocaoDocumento(d.id) : undefined}
              onReverse={() => reversaoDocumento(d.id)}
              estado={d.estado}
              permitirDownload
            />
          ))}
        {editando && (
          <ModalUploadDocumentos
            categoria={categorias_documentos[tab].nome}
            onDocumentosAdicionados={insercaoDocumento}
          />
        )}
      </HStack>
    </HStack>
  );
}
