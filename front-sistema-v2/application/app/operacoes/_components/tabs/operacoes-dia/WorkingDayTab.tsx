import { Corretora, Fundo, Voice } from "@/lib/types/api/iv/v1";
import { Button, HStack, Icon, VStack, useDisclosure } from "@chakra-ui/react";
import {
  IoCloudDownloadOutline,
  IoCloudUploadOutline,
  IoServerOutline,
} from "react-icons/io5";
import ColunaFluxoOperacoes from "../triagem-b3/ColunaFluxoOperacoes";
import VoiceComponent from "./VoiceComponent";
import ModalEnvioBoleta from "./ModalEnvioBoleta";
import ModalCorretoras from "./ModalCorretoras";
import ModalConversaoCSV from "./ModalConversaoCSV";
import { useState } from "react";

export enum TipoOperacao {
  COMPRA,
  VENDA,
}

export enum EstadoOperacao {
  NAO_ENVIADO,
  AGUARDANDO_CONFIRMACAO_ALOCACAO,
  REALOCAR,
  AGUARDANDO_LIQUIDACAO,
  LIQUIDADO,
}

export type Operacao = {
  id: number;
  estado: EstadoOperacao;
  fundo_nome?: string;
  tipo?: TipoOperacao;
  quantidade?: number;
  ativo_codigo?: string;
  taxa?: number;
};

export type WorkingDayTabProps = {
  fundos: Fundo[];
  ativos_codigos: string[];
  voicesSemCasamento: Voice[];
};

export default function WorkingDayTab({
  voicesSemCasamento,
}: WorkingDayTabProps) {
  const voicesAguardando = voicesSemCasamento.filter(
    (v) => v.registro_contraparte,
  ) as (Omit<Voice, "registro_contraparte"> & {
    registro_contraparte: Corretora;
  })[];
  const voicesSemCorretora = voicesSemCasamento.filter(
    (v) => !v.registro_contraparte,
  ) as Omit<Voice, "registro_contraparte">[];

  const {
    isOpen: isUploadOpen,
    onOpen: onUploadOpen,
    onClose: onUploadClose,
  } = useDisclosure();

  const {
    isOpen: isBrokersOpen,
    onOpen: onBrokersOpen,
    onClose: onBrokersClose,
  } = useDisclosure();

  const {
    isOpen: isCSVOpen,
    onOpen: onCSVOpen,
    onClose: onCSVClose,
  } = useDisclosure();

  const [nomeContaARegistrar, setNomeContaARegistrar] = useState("");

  const onRegistrarCorretora = (contaB3Corretora: string) => {
    onBrokersOpen();
    setNomeContaARegistrar(contaB3Corretora);
  };

  return (
    <VStack w="100%" h="100%" p="24px" alignItems="stretch">
      <HStack
        border="1px solid"
        borderColor="cinza.main"
        borderRadius="4px"
        p="12px"
      >
        <Button
          colorScheme="azul_3"
          size="xs"
          leftIcon={<Icon as={IoServerOutline} />}
          onClick={() => {
            onBrokersOpen();
            setNomeContaARegistrar("");
          }}
        >
          Registro de corretoras
        </Button>
        <Button
          colorScheme="verde"
          size="xs"
          leftIcon={<Icon as={IoCloudUploadOutline} />}
          onClick={onUploadOpen}
        >
          Carregar boleta de operações
        </Button>
        <Button
          colorScheme="azul_1"
          size="xs"
          leftIcon={<Icon as={IoCloudDownloadOutline} />}
          onClick={onCSVOpen}
        >
          Converter para arquivo B3 (.csv)
        </Button>
      </HStack>
      <HStack
        gap={0}
        flex={1}
        alignItems="stretch"
        border="1px solid"
        borderColor="cinza.main"
        borderRadius="4px"
        p={0}
      >
        <ColunaFluxoOperacoes
          flex={1}
          title="Voices sem possibilidade de casamento"
        >
          {voicesSemCorretora
            .sort((v1, v2) => v2.criado_em.localeCompare(v1.criado_em))
            .map((v) => (
              <VoiceComponent
                onRegistrarCorretoraClick={onRegistrarCorretora}
                voice={v}
              />
            ))}
        </ColunaFluxoOperacoes>
        <ColunaFluxoOperacoes flex={1} title="Voices aguardando casamento">
          {voicesAguardando
            .sort((v1, v2) => v2.criado_em.localeCompare(v1.criado_em))
            .map((v) => (
              <VoiceComponent voice={v} />
            ))}
        </ColunaFluxoOperacoes>
      </HStack>
      <ModalEnvioBoleta isOpen={isUploadOpen} onClose={onUploadClose} />
      <ModalCorretoras
        isOpen={isBrokersOpen}
        onClose={onBrokersClose}
        nomeContaInicial={nomeContaARegistrar}
      />
      <ModalConversaoCSV isOpen={isCSVOpen} onClose={onCSVClose} />
    </VStack>
  );
}
