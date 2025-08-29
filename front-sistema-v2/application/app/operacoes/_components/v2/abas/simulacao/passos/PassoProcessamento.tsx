import Hint from "@/app/_components/texto/Hint";
import { useAsync, useHTTP } from "@/lib/hooks";
import {
  Button,
  HStack,
  Icon,
  Input,
  Select,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useRef, useState } from "react";
import {
  IoClose,
  IoCloudUpload,
  IoDownloadOutline,
  IoWarning,
} from "react-icons/io5";

import { ResultadoProcessamento } from "@/lib/types/api/iv/operacoes/processamento";
import { SugestaoAlocacao } from "@/lib/types/api/iv/operacoes/processamento";
import Aviso from "./Aviso";

export type PassoProcessamentoProps = {
  onAlocacoesChange: (alocacoes: SugestaoAlocacao[]) => void;
};

export default function PassoProcessamento({
  onAlocacoesChange,
}: PassoProcessamentoProps) {
  const [arquivo, setArquivo] = useState<File | null>(null);
  const arquivoInputRef = useRef<HTMLInputElement | null>(null);

  const [resultadoProcessamento, setResultadoProcessamento] = useState<
    ResultadoProcessamento[] | null
  >(null);

  const [processando, processar] = useAsync();
  const httpClient = useHTTP({ withCredentials: true });

  const enviar = () => {
    if (processando) return;
    setResultadoProcessamento(null);
    processar(async () => {
      if (!arquivo) return;
      const body = new FormData();
      body.append("file", arquivo);
      const response = await httpClient.fetch(
        "v1/operacoes/alocacoes/processamento?formato=titpriv",
        {
          method: "POST",
          multipart: true,
          body,
        },
      );
      if (!response.ok) return;
      const dados: ResultadoProcessamento[] = await response.json();
      setResultadoProcessamento(dados);
      onAlocacoesChange(
        (dados
          .filter((r) => r.dados)
          .map((d) => d.dados) as SugestaoAlocacao[]) ?? [],
      );
    });
  };

  const limpar = useCallback(() => {
    setArquivo(null);
    setResultadoProcessamento(null);
    onAlocacoesChange([]);
    if (arquivoInputRef.current) {
      (arquivoInputRef.current as any).value = null;
    }
  }, []);

  return (
    <VStack alignItems="stretch">
      <HStack alignItems="flex-start">
        <VStack flex={3} gap={0} alignItems="stretch">
          <Hint>Formato de boleta</Hint>
          <HStack>
            <Select
              flex={2}
              isDisabled={Boolean(resultadoProcessamento)}
              size="xs"
            >
              <option> Títulos Privados</option>
            </Select>
            <Button
              isDisabled
              flex={1}
              size="xs"
              colorScheme="azul_4"
              leftIcon={<Icon as={IoDownloadOutline} />}
            >
              Baixar template
            </Button>
          </HStack>
        </VStack>
        <VStack flex={4} gap={0} alignItems="stretch">
          <Hint>Arquivo</Hint>
          <HStack gap="4px">
            <Input
              isDisabled={Boolean(resultadoProcessamento)}
              ref={arquivoInputRef}
              flex={3}
              size="xs"
              type="file"
              accept=".xlsx"
              onChange={(ev) =>
                setArquivo(ev.target.files?.length ? ev.target.files[0] : null)
              }
            />
            <Button
              flex={1}
              colorScheme="rosa"
              size="xs"
              leftIcon={<Icon as={IoClose} />}
              onClick={limpar}
            >
              Limpar
            </Button>
            <Button
              flex={1}
              isDisabled={!arquivo}
              isLoading={processando}
              colorScheme="verde"
              size="xs"
              leftIcon={<Icon as={IoCloudUpload} />}
              onClick={enviar}
            >
              Processar
            </Button>
          </HStack>
        </VStack>
      </HStack>
      <HStack
        borderRadius="8px"
        border="1px solid"
        borderColor="azul_1.100"
        p="8px"
        fontSize="xs"
      >
        {resultadoProcessamento ? (
          <>
            <Text>{resultadoProcessamento.length} linhas processadas</Text>
            <Text color="verde.main" fontWeight="bold">
              {
                resultadoProcessamento.filter((r) =>
                  ["OK", "AVISO"].includes(r.status),
                ).length
              }{" "}
              linhas válidas
            </Text>
            <Text color="amarelo.main">
              (
              {
                resultadoProcessamento.filter((r) => "AVISO" === r.status)
                  .length
              }{" "}
              com aviso)
            </Text>
          </>
        ) : arquivo ? (
          processando ? (
            <Text>(...) Aguardando processamento do arquivo</Text>
          ) : (
            <Text>↑ Processe o arquivo</Text>
          )
        ) : (
          <Text>(?) Escolha um arquivo</Text>
        )}
      </HStack>
      <HStack>
        <VStack
          borderRadius="8px"
          flex={1}
          alignItems="stretch"
          bgColor="azul_1.50"
          h="60vh"
          border="1px solid"
          borderColor="azul_1.100"
          overflowY="auto"
        >
          <HStack
            borderTopRadius="8px"
            bgColor="azul_1.600"
            p="4px 8px"
            gap="4px"
            color="laranja.main"
            position="sticky"
            top={0}
            zIndex={2}
          >
            <Icon as={IoWarning} />
            <Text color="white">Avisos</Text>
          </HStack>
          {resultadoProcessamento
            ?.filter((r) => r.status === "AVISO")
            .map((a, i) => <Aviso key={i} alerta={a} />)}
        </VStack>
        <VStack
          borderRadius="8px"
          flex={1}
          alignItems="stretch"
          bgColor="azul_1.50"
          h="60vh"
          border="1px solid"
          borderColor="azul_1.100"
          overflowY="auto"
        >
          <HStack
            borderTopRadius="8px"
            bgColor="azul_1.600"
            p="4px 8px"
            gap="4px"
            color="rosa.main"
            position="sticky"
            top={0}
            zIndex={2}
          >
            <Icon as={IoClose} />
            <Text color="white">Erros</Text>
          </HStack>
          {resultadoProcessamento
            ?.filter((r) => r.status === "ERRO")
            .map((a, i) => <Aviso key={i} alerta={a} />)}
        </VStack>
      </HStack>
    </VStack>
  );
}
