import { getColorHex } from "@/app/theme";
import { EventoOperacao } from "@/lib/types/api/iv/v1";
import {
  Box,
  HStack,
  Icon,
  StackDivider,
  Text,
  VStack,
} from "@chakra-ui/react";
import { MouseEvent, RefCallback } from "react";
import { Company } from "./nodes";
import Image from "next/image";
import { IoHelpCircleOutline } from "react-icons/io5";
import { fmtDatetime } from "@/lib/util/string";
import { companies } from "./fluxo/dados/companies";

export enum EstadoSelecao {
  PASSADO,
  PRESENTE,
  FUTURO,
}

export type EventoOperacaoItemClickEventParams = {
  operacao: EventoOperacao;
  eventoClique: MouseEvent<HTMLDivElement>;
};

export type EventoOperacaoItemProps = {
  evento: EventoOperacao;
  visual: EstadoSelecao;

  elementRef?: RefCallback<HTMLDivElement | null>;

  onClick: (info: EventoOperacaoItemClickEventParams) => void;
};

const bgColor = (visual: EstadoSelecao) =>
  ({
    [EstadoSelecao.PASSADO]: "white",
    [EstadoSelecao.PRESENTE]: "azul_3.50",
    [EstadoSelecao.FUTURO]: "cinza.main",
  })[visual];

const makeTitle = (icon: Company["icon"], title: string) => (
  <HStack>
    {icon ? (
      "src" in icon ? (
        <Image alt="simbolo" src={icon} width={18} height={18} />
      ) : (
        <Icon boxSize="18px" as={icon} color="cinza.500" />
      )
    ) : (
      <></>
    )}
    <Text>{title}</Text>
  </HStack>
);

const atMap = (n: number) =>
  ({
    1: "Pendente Confirmação Custodiante",
    2: "Pendente Confirmação Contraparte Custodiante",
    3: "Rejeitado pelo Custodiante",
    4: "Rejeitado pela Contraparte Custodiante",
    5: "Confirmado pelo Custodiante",
    6: "Disponível para Registro",
    7: "Pendente de Realocação da Contraparte",
    8: "Realocado",
    9: "Pendente de Realocação",
  })[n] ?? "---";

const getTitle = (evento: EventoOperacao) => {
  switch (evento.informacoes.tipo) {
    case "acato-voice":
      return makeTitle(companies["vanguarda"].icon, "Acato Voice");
    case "alocacao-contraparte":
      return makeTitle(companies["contraparte"].icon, "Alocação contraparte");
    case "alocacao-operador":
      return makeTitle(companies["vanguarda"].icon, "Alocação interna");
    case "aprovacao-backoffice":
      return makeTitle(companies["vanguarda"].icon, "Aprovação Backoffice");
    case "envio-alocacao":
      return makeTitle(companies["vanguarda"].icon, "Sistema envia alocação");
    case "emissao-numeros-controle":
      return makeTitle(
        companies["b3"].icon,
        "Emissão números de controle NoMe",
      );
    case "erro-mensagem":
      return makeTitle(companies["b3"].icon, "Erro de processamento");
    case "atualizacao-custodiante": {
      const cust =
        evento.informacoes.registro_nome.fundo.nome_custodiante.toLowerCase();
      const comp =
        companies[cust.split(" ")[0]] ?? companies[cust.split(" ")[1]];
      return makeTitle(
        comp?.icon ?? IoHelpCircleOutline,
        `Atualização ${evento.informacoes.registro_nome.numero_controle_nome}`,
      );
    }
  }
};

const getBody = (evento: EventoOperacao) => {
  switch (evento.informacoes.tipo) {
    case "atualizacao-custodiante":
      return (
        <Text fontSize="10px" color="cinza.500">
          {evento.informacoes.registro_nome.fundo.nome}
        </Text>
      );
  }
};

export default function EventoOperacaoItem({
  elementRef,
  evento,
  visual,
  onClick,
}: EventoOperacaoItemProps) {
  const selecionado = visual === EstadoSelecao.PRESENTE;
  const hora = fmtDatetime(evento.criado_em).split(" ").at(-1);
  return (
    <HStack
      ref={elementRef}
      p="0px 4px 0px 8px"
      fontSize="xs"
      onClick={(ev) => onClick({ operacao: evento, eventoClique: ev })}
      position="relative"
      bgColor={bgColor(visual)}
      _hover={{
        bgColor: selecionado ? "azul_3.100" : "cinza.100",
      }}
      transition="0.25s all"
      role="group"
      cursor="pointer"
      borderBottom="1px solid"
      borderColor="cinza.200"
      gap={0}
    >
      <Box
        position="absolute"
        width={selecionado ? "4px" : "0px"}
        _groupHover={{
          width: "4px",
        }}
        height="100%"
        top={0}
        left={0}
        bgColor="verde.main"
        transition="0.25s all"
      />
      <HStack
        divider={
          <StackDivider
            borderColor={
              selecionado ? getColorHex("cinza.200") + "3F" : "cinza.200"
            }
          />
        }
      >
        <Text> {hora} </Text>
        <VStack
          h="48px"
          justifyContent="center"
          alignItems="flex-start"
          gap="4px"
        >
          {getTitle(evento)}
          {getBody(evento)}
        </VStack>
      </HStack>
    </HStack>
  );
}
