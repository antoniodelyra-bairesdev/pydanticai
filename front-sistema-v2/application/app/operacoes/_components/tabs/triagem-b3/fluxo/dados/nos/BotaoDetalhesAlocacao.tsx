import { OperacaoAlocadaInternamente } from "@/lib/types/api/iv/v1";
import {
  Box,
  Button,
  HStack,
  Icon,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import ModalInteracaoAlocacao from "../../../ModalInteracaoAlocacao";
import { IoSearchOutline } from "react-icons/io5";
import { User } from "@/lib/types/api/iv/auth";

export type BotaoDetalhesAlocacaoProps = {
  operacao: OperacaoAlocadaInternamente;
  mostrar_usuario: "alocacao" | "aprovacao";
  habilitar_controles: boolean;
  resposta_backoffice?: {
    aprovacao: boolean;
    motivo: string | null;
    usuario: User;
    data: string;
  };
};

export function BotaoDetalhesAlocacao({
  operacao,
  mostrar_usuario,
  habilitar_controles,
  resposta_backoffice,
}: BotaoDetalhesAlocacaoProps) {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const alocs = operacao.alocacoes;
  return (
    <HStack justifyContent="space-between" alignItems="flex-end">
      <Box flex={1}>
        {mostrar_usuario === "alocacao" ? (
          <VStack mt="6px" flex={1} gap={0} alignItems="stretch">
            <Text color="cinza.main" fontSize="10px">
              Alocado por:
            </Text>
            <Text color="cinza.500" fontSize="10px">
              {operacao.usuario?.nome ?? "Alocação externa"}
            </Text>
          </VStack>
        ) : (
          resposta_backoffice && (
            <VStack mt="6px" flex={1} gap={0} alignItems="stretch">
              <Text color="cinza.main" fontSize="10px">
                {resposta_backoffice.aprovacao ? "Aprovado" : "Reprovado"} por:
              </Text>
              <Text color="cinza.500" fontSize="10px">
                {resposta_backoffice.usuario.nome}
              </Text>
            </VStack>
          )
        )}
      </Box>
      <Box>
        <Button
          onClick={onOpen}
          size="xs"
          colorScheme="azul_3"
          leftIcon={<Icon as={IoSearchOutline} />}
        >
          Detalhes
        </Button>
        <ModalInteracaoAlocacao
          habilitar_controles={habilitar_controles}
          alocacao_referente={{
            alocacoes: alocs.map((aloc) => ({
              fundo: aloc.fundo,
              quantidade: aloc.quantidade,
              total: aloc.total,
              registro_fundo: null,
            })),
            data: operacao.criado_em,
            id_operacao_interna: operacao.id,
            usuario: operacao.usuario,
          }}
          resposta_backoffice={resposta_backoffice}
          externo={operacao.externa}
          isOpen={isOpen}
          onClose={onClose}
        />
      </Box>
    </HStack>
  );
}
