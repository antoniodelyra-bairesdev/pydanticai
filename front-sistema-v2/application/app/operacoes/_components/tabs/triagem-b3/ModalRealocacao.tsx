import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { useAsync, useHTTP } from "@/lib/hooks";
import { OperacaoProcessada, OperacaoType } from "@/lib/types/api/iv/v1";
import {
  Button,
  HStack,
  Input,
  Progress,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useEffect, useRef, useState } from "react";
import TabelaQuebras from "./TabelaQuebras";
import Comment from "@/app/_components/misc/Comment";
import { getColorHex } from "@/app/theme";
import { fmtDatetime } from "@/lib/util/string";

export type ModalRealocacaoProps = {
  isOpen: boolean;
  onClose: () => void;
  pos: "backoffice" | "custodiante";
  idEvento: number;
  operacao: OperacaoType;
};

const match = (alocacao: OperacaoProcessada, operacao: OperacaoType) =>
  alocacao.data_operacao.substring(0, 10) ===
    operacao.criado_em.substring(0, 10) &&
  alocacao.vanguarda_compra === operacao.vanguarda_compra &&
  alocacao.ativo === operacao.codigo_ativo &&
  alocacao.contraparte === operacao.contraparte_nome &&
  alocacao.preco_unitario.toFixed(6) === operacao.preco_unitario.toFixed(6) &&
  alocacao.taxa.toFixed(6) === operacao.taxa.toFixed(6);

export default function ModalRealocacao({
  isOpen,
  onClose,
  pos,
  idEvento,
  operacao,
}: ModalRealocacaoProps) {
  const [loading, load] = useAsync();

  const [realocacao, setRealocacao] = useState<OperacaoProcessada | null>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [erros, setErros] = useState<string[]>([
    "Nenhuma realocação detectada",
  ]);

  const limpar = () => {
    setErros(["Nenhuma realocação detectada"]);
    setRealocacao(null);
    setSelectedFile(null);
    if (fileInputRef.current) {
      (fileInputRef.current as any).value = null;
    }
  };

  useEffect(() => {
    if (selectedFile === null) return;
    limpar();
    load(async () => {
      if (selectedFile === null) return;
      const body = new FormData();
      body.append("file", selectedFile);
      const response = await httpClient.fetch("v1/operacoes/boleta-resumo", {
        hideToast: { success: true },
        method: "POST",
        body,
        multipart: true,
      });
      if (!response.ok) return;
      const alocacoes: OperacaoProcessada[] = await response.json();
      let realocacao: OperacaoProcessada | null = null;
      for (const alocacao of alocacoes) {
        if (match(alocacao, operacao)) {
          realocacao = alocacao;
          break;
        }
      }

      const erros: string[] = [];

      if (!realocacao) {
        erros.push("Nenhuma alocação bate com a operação a ser realocada.");
      }

      const fundosInexistentes =
        realocacao?.alocacoes.filter((a) => !a.registro_fundo) ?? [];
      if (fundosInexistentes.length) {
        erros.push(
          ...fundosInexistentes.map(
            (alc) =>
              `(${alc.fundo.conta_cetip}) ${alc.fundo.nome} não está registrado no sistema.`,
          ),
        );
      }

      const qtd =
        realocacao?.alocacoes.reduce((num, alc) => num + alc.quantidade, 0) ??
        0;
      if (qtd !== operacao.quantidade) {
        erros.push(
          `Quantidade total (${qtd}) não bate com a quantidade da operação (${operacao.quantidade})`,
        );
      }

      if (erros.length > 0) {
        setErros(erros);
        setRealocacao(null);
      } else {
        setErros([]);
        setRealocacao(realocacao);
      }
    });
  }, [selectedFile]);

  const httpClient = useHTTP({ withCredentials: true });

  const enviarDados = useCallback(() => {
    if (!realocacao) return;
    const body = JSON.stringify({
      ator: pos,
      id_reprovacao_ator: idEvento,
      alocacoes: realocacao.alocacoes.map((alc) => ({
        fundo_id: alc.registro_fundo?.id,
        quantidade: alc.quantidade,
      })),
    });
    httpClient.fetch("v1/operacoes/realocacao", {
      method: "POST",
      body,
    });
  }, [realocacao]);

  return (
    <ConfirmModal
      isOpen={isOpen}
      onClose={onClose}
      title="Realocar"
      size="6xl"
      confirmEnabled={erros.length === 0}
      onConfirmAction={enviarDados}
    >
      <HStack>
        <Input
          ref={fileInputRef}
          flex={1}
          p="4px"
          size="sm"
          type="file"
          accept=".xlsx"
          onChange={(ev) => setSelectedFile(ev.target.files?.item(0) ?? null)}
        />
        <Button size="sm" colorScheme="rosa" onClick={limpar}>
          Limpar
        </Button>
      </HStack>
      <Progress
        visibility={loading ? "visible" : "hidden"}
        colorScheme="verde"
        isIndeterminate
      />
      {realocacao && (
        <TabelaQuebras
          alocacoes={realocacao.alocacoes}
          verificarFundos={true}
        />
      )}
      <VStack alignItems="flex-start">
        {erros.map((erro, i) => (
          <Comment key={i} bgColor={getColorHex("rosa.main")}>
            <Text fontSize="xs" color="rosa.main">
              {erro}
            </Text>
          </Comment>
        ))}
      </VStack>
    </ConfirmModal>
  );
}
