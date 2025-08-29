import { Voice } from "@/lib/types/api/iv/v1";
import { fmtDate, fmtDatetime } from "@/lib/util/string";
import {
  Box,
  Button,
  Checkbox,
  HStack,
  Icon,
  Td as _Td,
  Text,
  Tr,
  TableCellProps,
} from "@chakra-ui/react";
import { color } from "framer-motion";
import { useState } from "react";
import {
  IoAlert,
  IoCube,
  IoCubeOutline,
  IoWarning,
  IoWarningOutline,
} from "react-icons/io5";

export enum EstadoVoiceEnum {
  AGUARDANDO,
  ACATADO,
  CANCELADO,
  ALOCADO,
}

const { AGUARDANDO, ACATADO, CANCELADO, ALOCADO } = EstadoVoiceEnum;

const cores: Record<number, string[]> = {
  [AGUARDANDO]: ["amarelo.50", "amarelo.main"],
  [ACATADO]: ["cinza.200", "cinza.400"],
  [CANCELADO]: ["rosa.50", "rosa.main"],
  [ALOCADO]: ["verde.50", "verde.main"],
};

const textos: Record<number, string> = {
  [AGUARDANDO]: "Aguardando ação",
  [ACATADO]: "Acatado",
  [CANCELADO]: "Rejeitado",
  [ALOCADO]: "Alocado",
};

export type VoiceOrderEntry = {
  id: number;
  id_trader: string;
  id_ordem: string | null;
  id_ordem_secundario: string | null;
  id_execucao: string | null;
  codigo_ativo: string;
  vanguarda_compra: boolean;
  quantidade: 10;
  preco_unitario: number;
  data_negociacao: string;
  data_liquidacao: string;
  id_instrumento: string | null;
  id_instrumento_subjacente: string | null;
  nome_contraparte_cadastrada: string | null;
  contraparte_b3_mesa_id: number | null;
  contraparte_b3_corretora_nome: string | null;

  horario_recebimento_order_entry: string | null;
  horario_recebimento_post_trade: string | null;

  aprovado_em: string | null;
  cancelado_em: string | null;

  casamento: number[] | null;

  envios_pre_trade: string[];
  envios_post_trade: string[];
};

export type VoiceComponentProps = {
  voice: VoiceOrderEntry;
  selecionavel?: boolean;
  selecionado?: boolean;
  onSelecionado?: (selecionado: boolean) => void;
};

const Td = ({ ...props }: TableCellProps) => <_Td {...props} fontSize="13px" />;

export default function VoiceComponent({
  selecionavel,
  selecionado,
  onSelecionado,
  voice,
}: VoiceComponentProps) {
  return (
    <Tr
      borderRadius="4px"
      alignItems="center"
      _hover={{ bgColor: "cinza.200" }}
    >
      <Td>{voice.id_trader}</Td>
      <Td fontWeight="bold">
        <HStack>
          {false && <Icon color="laranja.main" as={IoWarningOutline} />}
          <Text>{voice.codigo_ativo}</Text>
        </HStack>
      </Td>
      <Td
        color={voice.vanguarda_compra ? "azul_3.main" : "rosa.main"}
        fontWeight="bold"
      >
        {voice.vanguarda_compra ? "C" : "V"}
      </Td>
      <Td>
        R${" "}
        {voice.preco_unitario.toLocaleString("pt-BR", {
          maximumFractionDigits: 8,
          minimumFractionDigits: 8,
        })}
      </Td>
      <Td>
        <Icon as={IoCubeOutline} color="verde.main" /> {voice.quantidade}
      </Td>
      <Td>{fmtDate(voice.data_negociacao)}</Td>
      <Td>
        {voice.horario_recebimento_order_entry
          ? fmtDatetime(voice.horario_recebimento_order_entry)
          : "Não recebido"}
      </Td>
      <Td>
        {voice.casamento
          ? `Casado com ${voice.casamento.length} alocações`
          : "Não há alocações casadas"}
      </Td>
      <Td>
        {voice.envios_pre_trade.length
          ? voice.envios_pre_trade.length
          : "Não há"}{" "}
        envios
      </Td>
      <Td>
        {voice.horario_recebimento_post_trade
          ? fmtDatetime(voice.horario_recebimento_post_trade)
          : "Não recebido"}
      </Td>
      <Td>
        {voice.envios_post_trade.length
          ? voice.envios_post_trade.length
          : "Não há"}{" "}
        envios
      </Td>
      <Td>---</Td>
    </Tr>
  );
}
