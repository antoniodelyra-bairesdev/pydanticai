import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { RegistroNoMe } from "@/lib/types/api/iv/v1";
import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Heading,
  Icon,
  VStack,
} from "@chakra-ui/react";
import { IoCloudDownloadOutline } from "react-icons/io5";
import { useAsync, useHTTP } from "@/lib/hooks";
import { downloadBlob } from "@/lib/util/http";
import TabelaQuebras from "../../../TabelaQuebras";

export type ModalInteracaoEmissoesProps = {
  preco_unitario: number;
  registros: RegistroNoMe[];
  isOpen: boolean;
  onClose: () => void;
};

export function BotaoDownloadEmissoes({
  registros,
}: {
  registros: RegistroNoMe[];
}) {
  const [carregando, iniciarCarregamento] = useAsync();
  const httpClient = useHTTP({ withCredentials: true });

  const download = (registros: RegistroNoMe[]) => {
    iniciarCarregamento(async () => {
      const params = new URLSearchParams();
      registros.forEach((registro) =>
        params.append("registros", String(registro.id)),
      );
      const response = await httpClient.fetch(
        "v1/operacoes/alocacoes/registros/download?" + params.toString(),
        { method: "GET", hideToast: { success: true } },
      );
      if (!response.ok) return;
      const file = await response.blob();
      downloadBlob(file, "quebras.xlsx");
    });
  };

  return (
    <Button
      isLoading={carregando}
      size="xs"
      onClick={() => download(registros)}
      leftIcon={<Icon as={IoCloudDownloadOutline} />}
      colorScheme="verde"
    >
      Baixar planilha de quebras
    </Button>
  );
}

export default function ModalInteracaoEmissoes({
  preco_unitario,
  registros,
  isOpen,
  onClose,
}: ModalInteracaoEmissoesProps) {
  const agrupados = registros.reduce(
    (map, registro) => (
      (map[registro.fundo.nome_custodiante] ??= []),
      map[registro.fundo.nome_custodiante].push(registro),
      map
    ),
    {} as Record<string, RegistroNoMe[]>,
  );

  return (
    <ConfirmModal
      isOpen={isOpen}
      onClose={onClose}
      title="Emissões por custodiantes"
      size="6xl"
      overflow="auto"
      hideCancelButton={true}
      confirmContent="Fechar"
    >
      <VStack alignItems="stretch">
        {Object.entries(agrupados).map(([nome_custodiante, registros]) => (
          <Card key={nome_custodiante} variant="outline">
            <CardHeader p="12px">
              <Heading size="md">{nome_custodiante}</Heading>
            </CardHeader>
            <CardBody p="12px">
              <TabelaQuebras
                alocacoes={registros.map((r) => ({
                  fundo: r.fundo,
                  quantidade: r.quantidade,
                  registro_fundo: r.fundo as any,
                  total: r.quantidade * preco_unitario,
                }))}
                verificarFundos={false}
              />
            </CardBody>
            <CardFooter p="12px">
              <BotaoDownloadEmissoes registros={registros} />
            </CardFooter>
          </Card>
        ))}
      </VStack>
    </ConfirmModal>
  );
}
