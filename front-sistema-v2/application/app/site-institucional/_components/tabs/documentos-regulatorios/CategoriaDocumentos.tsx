"use client";

import ArquivoComponent from "@/app/_components/misc/Arquivo";
import {
  Arquivo,
  CategoriaRelatorio,
  DocumentoRelatorio,
} from "@/lib/types/api/iv/v1";
import {
  Box,
  HStack,
  Progress,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import AdicionarRelatorio from "./AdicionarRelatorio";
import { useState } from "react";
import { useAsync, useHTTP, useUser } from "@/lib/hooks";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { downloadBlob } from "@/lib/util/http";

export default function CategoriaDocumentos({
  categoria,
}: {
  categoria: CategoriaRelatorio;
}) {
  const [documentos, setDocumentos] = useState(categoria.documentos);
  const [aDeletar, setADeletar] = useState<DocumentoRelatorio | null>(null);

  const [deletando, iniciarDelecao] = useAsync();
  const httpClient = useHTTP({ withCredentials: true });

  const deletarDocumento = (arquivo: Arquivo) => {
    if (deletando) return;
    const posDocumento = documentos.findIndex((doc) => doc.arquivo === arquivo);
    if (posDocumento === -1) return;
    const documento = documentos[posDocumento];
    setADeletar(documento);
  };

  const { user } = useUser();
  const podeAlterarDocs = user?.roles.some(
    (r) => r.nome === "Site Institucional - Alterar documentos regulatórios",
  );

  return (
    <HStack alignItems="stretch" flexWrap="wrap">
      {documentos.map((documento) => (
        <VStack key={documento.id}>
          <ArquivoComponent
            arquivo={documento.arquivo}
            rotulo={documento.nome}
            onDelete={podeAlterarDocs ? deletarDocumento : undefined}
            permitirDownload={async () => {
              const response = await httpClient.fetch(
                "v1/regulatorio/relatorio/" + documento.id,
                { method: "GET", hideToast: { success: true } },
              );
              if (!response.ok) return;
              const blob = await response.blob();
              downloadBlob(blob, documento.nome);
            }}
          />
        </VStack>
      ))}
      {podeAlterarDocs && (
        <AdicionarRelatorio
          categoria={categoria}
          onDocumentosAdicionados={(novos) =>
            setDocumentos([...documentos, ...novos])
          }
        />
      )}
      <ConfirmModal
        isOpen={!!aDeletar || deletando}
        onClose={() => {
          if (deletando) return;
          setADeletar(null);
        }}
        onConfirmAction={() =>
          iniciarDelecao(async () => {
            if (!aDeletar) return;
            const response = await httpClient.fetch(
              `v1/regulatorio/relatorio/${aDeletar.id}`,
              { method: "DELETE" },
            );
            if (!response.ok) return;

            const posDocumento = documentos.findIndex(
              (doc) => doc.id === aDeletar.id,
            );
            if (posDocumento === -1) return;
            documentos.splice(posDocumento, 1);
            setDocumentos([...documentos]);
          })
        }
        confirmEnabled={!deletando}
        title={
          aDeletar
            ? `Deseja remover o relatório ${aDeletar.nome}?`
            : "Removendo..."
        }
      >
        {deletando ? (
          <Progress isIndeterminate colorScheme="verde" h="8px" />
        ) : (
          <Text fontWeight={600}>Esta ação não poderá ser desfeita.</Text>
        )}
      </ConfirmModal>
    </HStack>
  );
}
