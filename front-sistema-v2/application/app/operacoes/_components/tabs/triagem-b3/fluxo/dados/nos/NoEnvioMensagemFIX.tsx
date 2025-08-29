import { ReactNode } from "react";
import GrafoFluxo from "../GrafoFluxo";
import NoAbstrato from "../NoAbstrato";
import { companies } from "../companies";
import { EnvioAlocacao } from "@/lib/types/api/iv/v1";
import { Button, HStack, Icon, useDisclosure } from "@chakra-ui/react";
import { IoBugOutline } from "react-icons/io5";
import ModalDetalhesErro from "../../../ModalDetalhesErro";

export type BotaoDetalhesErroProps = {
  msg: EnvioAlocacao;
};

export function BotaoDetalhesErro({ msg }: BotaoDetalhesErroProps) {
  const { isOpen, onOpen, onClose } = useDisclosure();

  return (
    <HStack justifyContent="flex-end">
      <Button
        onClick={onOpen}
        colorScheme="rosa"
        leftIcon={<Icon as={IoBugOutline} />}
      >
        Detalhes
      </Button>
      <ModalDetalhesErro erro={msg.erro} isOpen={isOpen} onClose={onClose} />
    </HStack>
  );
}

export default class NoEnvioMensagemFIX extends NoAbstrato {
  public mensagem: EnvioAlocacao | null = null;

  public prefixo() {
    return "envio-mensagem-";
  }
  public label() {
    return "Envio mensagem FIX";
  }

  public detalhes() {
    if (!this.mensagem?.erro) return "";
    return <BotaoDetalhesErro msg={this.mensagem} />;
  }
}
