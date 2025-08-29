import Comment from "@/app/_components/misc/Comment";
import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import Hint from "@/app/_components/texto/Hint";
import { useAsync, useHTTP } from "@/lib/hooks";
import { Fundo } from "@/lib/types/api/iv/v1";
import { fmtCNPJ } from "@/lib/util/string";
import {
  Box,
  Button,
  HStack,
  Icon,
  Input,
  Progress,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  VStack,
} from "@chakra-ui/react";
import { useEffect, useRef, useState } from "react";
import { IoEyeOffOutline, IoGlobeOutline } from "react-icons/io5";

export type ModalMateriaisMassaProps = {
  isOpen: boolean;
  onClose: () => void;
  fundos: Fundo[];
};

export type InformacaoMaterialSchema = {
  fundo_id: number;
  data_referencia: string;
  titulo_material: string;
  posicao_arquivo: number;
};

export type UploadMassa = {
  dataRef: string;
  isin: string;
  arquivo: File;
};

const dataValida = (str: string) => {
  if (str.length !== 6) return false;
  const num = Number(str);
  if (isNaN(num)) return false;
  const mes = num % 100;
  if (mes > 12 || mes <= 0) return false;
  return true;
};

const isinValido = (str: string) => {
  const tratado = str.replace(/[^A-Z0-9]/g, "");
  if (tratado != str) return false;
  if (str.length !== 12) return false;
  return true;
};

export default function ModalMateriaisMassa({
  isOpen,
  onClose,
  fundos,
}: ModalMateriaisMassaProps) {
  const [arquivos, setArquivos] = useState<UploadMassa[]>([]);

  const inputRef = useRef<HTMLInputElement | null>(null);

  const httpClient = useHTTP({ withCredentials: true });

  const [enviando, iniciarEnvio] = useAsync();
  const [erro, setErro] = useState(false);

  const enviar = () => {
    if (enviando) return;
    iniciarEnvio(async () => {
      const informacoes: InformacaoMaterialSchema[] = [];
      const novos_arquivos: File[] = [];
      arquivos.forEach((a) => {
        const fundo = fundos.find((f) => f.isin === a.isin);
        if (!fundo) return;
        const info: InformacaoMaterialSchema = {
          data_referencia: a.dataRef.split("/").reverse().join("-"),
          titulo_material: "Material Publicitário",
          fundo_id: fundo.id,
          posicao_arquivo: novos_arquivos.length,
        };
        informacoes.push(info);
        novos_arquivos.push(a.arquivo);
      });
      const body = new FormData();
      body.append("dados_serializados", JSON.stringify({ informacoes }));
      novos_arquivos.forEach((a) => body.append("novos_arquivos", a));
      const response = await httpClient.fetch(
        "/v1/fundos/institucionais/publicacao-massa",
        { method: "POST", body, multipart: true },
      );
      if (response.ok) {
        return onClose();
      }
      setErro(true);
    });
  };

  const limpar = () => {
    setArquivos([]);
    setErro(false);
    if (inputRef.current) (inputRef.current as any).value = null;
  };

  useEffect(() => {
    limpar();
  }, [isOpen]);

  return (
    <ConfirmModal
      isOpen={isOpen}
      onClose={() => {}}
      size="6xl"
      onConfirmAction={enviar}
      onCancelAction={() => {
        if (!enviando) {
          onClose();
        }
      }}
      confirmEnabled={arquivos.every(({ isin, dataRef }) => isin && dataRef)}
    >
      <VStack alignItems="stretch" gap="16px">
        <Text>Carregar materiais publicitários</Text>
        <Hint>
          OBS: O nome dos arquivos precisa respeitar o formato{" "}
          <kbd>
            lamina-AAAAMM-ISINCLASSEOUSUBCLASSE-NOME DA CLASSE OU SUBCLASSE.pdf
          </kbd>
        </Hint>
        <HStack>
          <Input
            ref={inputRef}
            size="sm"
            p="4px"
            type="file"
            multiple
            onChange={(ev) => {
              const arqs: UploadMassa[] = [];
              for (const arquivo of ev.currentTarget.files ?? []) {
                const [prefixo, dataRef, isin] = arquivo.name.split("-");
                const data = dataValida(dataRef)
                  ? new Date(
                      Number(dataRef.substring(0, 4)),
                      Number(dataRef.substring(4)),
                    )
                  : null;

                const ajustado = data
                  ? new Date(Number(data) - 1000 * 60 * 60 * 24)
                  : null;

                const formatado = !ajustado
                  ? ""
                  : ajustado
                      .toISOString()
                      .split("T")[0]
                      .split("-")
                      .reverse()
                      .join("/");

                if (prefixo === "lamina") {
                  arqs.push({
                    dataRef: formatado,
                    isin: isinValido(isin) ? isin : "",
                    arquivo,
                  });
                }
              }
              setArquivos(arqs);
            }}
          />
          <Button size="sm" colorScheme="rosa" onClick={limpar}>
            Limpar
          </Button>
        </HStack>
        <Comment>
          Os arquivos serão armazenados na categoria "Materiais Publicitários"
          para cada fundo.
          <br />
          <Text as="span" fontSize="sm">
            <Icon as={IoGlobeOutline} color="verde.main" /> Caso o fundo esteja
            publicado, os documentos serão{" "}
            <strong>
              imediatamente adicionados no site institucional e substituirão o
              material anterior
            </strong>
            .
          </Text>
          <br />
          <Text as="span" fontSize="sm">
            <Icon as={IoEyeOffOutline} color="rosa.main" /> Caso o fundo não
            esteja publicado, os documentos serão enviados internamente mas eles{" "}
            <strong>não serão publicados no site institucional</strong>.
          </Text>
        </Comment>
        <TableContainer overflowY="auto">
          <Table size="sm">
            <Thead>
              <Tr>
                <Th>Publicado?</Th>
                <Th>Data referência</Th>
                <Th>ISIN</Th>
                <Th>Fundo</Th>
                <Th>Arquivo</Th>
              </Tr>
            </Thead>
            <Tbody>
              {arquivos.map(({ arquivo, isin, dataRef }, i) => {
                const f = fundos.find((f) => f.isin === isin);
                return (
                  <Tr key={i}>
                    <Td fontSize="xs">
                      {f ? (
                        f.publicado ? (
                          <Text color="verde.main" textAlign="center">
                            <Icon as={IoGlobeOutline} /> Publicado
                          </Text>
                        ) : (
                          <Text color="rosa.main" textAlign="center">
                            <Icon as={IoEyeOffOutline} /> Oculto
                          </Text>
                        )
                      ) : (
                        "---"
                      )}
                    </Td>
                    <Td
                      fontSize="xs"
                      color={!dataRef ? "rosa.main" : undefined}
                      bgColor={!dataRef ? "rosa.200" : undefined}
                    >
                      {dataRef || "Data inválida"}
                    </Td>
                    <Td
                      fontSize="xs"
                      color={!isin ? "rosa.main" : undefined}
                      bgColor={!isin ? "rosa.200" : undefined}
                    >
                      {isin ? isin : "ISIN Inválido"}
                    </Td>
                    <Td fontSize="xs">{f?.nome ?? "---"}</Td>
                    <Td fontSize="xs">{arquivo.name}</Td>
                  </Tr>
                );
              })}
            </Tbody>
          </Table>
        </TableContainer>
        {erro && (
          <Text color="rosa.main">
            Falha de processamento. Entre em contato com o time de tecnologia.
          </Text>
        )}
        <Box position="sticky" bottom="-8px" bgColor="white">
          <Progress
            visibility={enviando ? "visible" : "hidden"}
            w="100%"
            h="12px"
            size="sm"
            colorScheme="verde"
            isIndeterminate
          />
        </Box>
      </VStack>
    </ConfirmModal>
  );
}
