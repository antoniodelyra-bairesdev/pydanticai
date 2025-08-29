"use client";

import ConteinerComRotulo from "@/app/_components/layout/ConteinerComRotulo";
import {
  Fundo,
  FundoCaracteristicaExtra,
  FundoClassificacaoDocumento,
  GestorFundo,
  InstituicaoFinanceira,
  Mesa,
} from "@/lib/types/api/iv/v1";
import { CloseIcon, EditIcon } from "@chakra-ui/icons";
import { Button, HStack, Heading, Icon, Text, VStack } from "@chakra-ui/react";
import {
  IoBusinessOutline,
  IoCheckmarkCircleOutline,
  IoDocumentsOutline,
  IoIdCardOutline,
  IoPeopleOutline,
  IoSaveOutline,
  IoSwapVerticalOutline,
} from "react-icons/io5";

import { useFundoDetalhes } from "../_providers/FundoDetalhesProvider";
import InformacoesGeraisConteudo from "./InformacoesGeraisConteudo";
import AdministracaoConteudo from "./AdministracaoConteudo";
import CadastrosEContasConteudo from "./CadastrosEContasConteudo";
import DatasELimitesConteudo from "./DatasELimitesConteudo";
import BenchmarkETaxasConteudo from "./BenchmarkETaxasConteudo";
import GestaoConteudo from "./GestaoConteudo";
import DocumentosConteudo, { DocumentoComEstado } from "./DocumentosConteudo";
import { useAsync, useHTTP } from "@/lib/hooks";
import serializacao from "./serializacao";
import { useState } from "react";
import { EstadoArquivoEnum } from "./WrapperArquivo";

export type DetalhesFundoProps = {
  fundo: Fundo;
  lista_gestores: GestorFundo[];
  lista_administradores: InstituicaoFinanceira[];
  lista_controladores: InstituicaoFinanceira[];
  lista_custodiantes: InstituicaoFinanceira[];
  lista_mesas: Mesa[];
  caracteristicas_extras: FundoCaracteristicaExtra[];
  categorias_documentos: FundoClassificacaoDocumento[];
};

export default function DetalhesFundo({
  fundo,
  lista_gestores,
  lista_administradores,
  lista_controladores,
  lista_custodiantes,
  lista_mesas,
  caracteristicas_extras,
  categorias_documentos,
}: DetalhesFundoProps) {
  const estado = useFundoDetalhes();

  const { reset, editando, setEditando } = estado;

  const httpClient = useHTTP({ withCredentials: true });
  const [enviando, iniciarEnvio] = useAsync();

  const [documentos, setDocumentos] = useState<DocumentoComEstado[]>([]);

  const enviar = () => {
    if (enviando) return;
    iniciarEnvio(async () => {
      const body = new FormData();
      documentos
        .filter((d) => d.arquivoLocal && d.estado === EstadoArquivoEnum.inserir)
        .map((d) => d.arquivoLocal!)
        .forEach((a) => body.append("novos_arquivos", a));
      const dados = serializacao(estado, documentos);
      body.append("dados_serializados", JSON.stringify(dados));
      const response = await httpClient.fetch(`v1/fundos/` + fundo.id, {
        method: "PUT",
        multipart: true,
        body,
      });
      if (!response.ok) return;

      console.log(await response.json());
      setEditando(false);
    });
  };

  return (
    <VStack alignItems="stretch" gap={0} minH="100%">
      <HStack
        bgColor="white"
        borderBottom="1px solid"
        borderColor="cinza.main"
        justifyContent="space-between"
        p="12px 24px"
        position="sticky"
        top={0}
        left={0}
        zIndex={10}
      >
        <Heading size="lg" fontWeight={500}>
          {fundo.nome}
        </Heading>
        <HStack>
          <Button
            size="sm"
            colorScheme={editando ? "verde" : "azul_3"}
            leftIcon={<Icon as={editando ? IoSaveOutline : EditIcon} />}
            onClick={() => {
              if (editando) {
                enviar();
              } else {
                setEditando(true);
              }
            }}
          >
            {editando ? "Salvar" : "Editar"}
          </Button>
          {editando && (
            <Button
              size="sm"
              colorScheme="rosa"
              leftIcon={<Icon as={CloseIcon} />}
              onClick={() => {
                setEditando(false);
                reset();
              }}
            >
              Cancelar
            </Button>
          )}
        </HStack>
      </HStack>
      <VStack
        flex={1}
        alignItems="stretch"
        p="24px"
        bgColor="cinza.50"
        gap="18px"
      >
        <HStack alignItems="stretch" gap="36px">
          <ConteinerComRotulo
            flex={2}
            fontWeight={600}
            rotulo="Informações gerais"
            icone={<Icon as={IoIdCardOutline} color="verde.main" />}
          >
            <InformacoesGeraisConteudo lista_gestores={lista_gestores} />
          </ConteinerComRotulo>
          <ConteinerComRotulo
            flex={2}
            fontWeight={600}
            rotulo="Administração"
            icone={<Icon as={IoBusinessOutline} color="verde.main" />}
          >
            <AdministracaoConteudo
              lista_administradores={lista_administradores}
              lista_controladores={lista_controladores}
              lista_custodiantes={lista_custodiantes}
            />
          </ConteinerComRotulo>
        </HStack>
        <HStack alignItems="stretch">
          <ConteinerComRotulo
            flex={1}
            fontWeight={600}
            rotulo="Cadastros e contas"
            icone={<Icon as={IoCheckmarkCircleOutline} color="verde.main" />}
          >
            <CadastrosEContasConteudo />
          </ConteinerComRotulo>
        </HStack>
        <HStack alignItems="stretch" gap="36px">
          <ConteinerComRotulo
            flex={3}
            fontWeight={600}
            rotulo="Datas e limites"
            icone={<Icon as={IoSwapVerticalOutline} color="verde.main" />}
          >
            <DatasELimitesConteudo />
          </ConteinerComRotulo>
          <ConteinerComRotulo
            flex={1}
            fontWeight={600}
            rotulo="Benchmark e taxas"
            icone={
              <Text as="span" color="verde.main">
                $
              </Text>
            }
          >
            <BenchmarkETaxasConteudo />
          </ConteinerComRotulo>
        </HStack>
        <ConteinerComRotulo
          flex={1}
          fontWeight={600}
          rotulo="Gestão"
          icone={<Icon as={IoPeopleOutline} color="verde.main" />}
        >
          <GestaoConteudo
            lista_mesas={lista_mesas}
            caracteristicas_extras={caracteristicas_extras}
          />
        </ConteinerComRotulo>
        <ConteinerComRotulo
          flex={1}
          fontWeight={600}
          rotulo="Documentos"
          icone={<Icon as={IoDocumentsOutline} color="verde.main" />}
        >
          <DocumentosConteudo
            onDocumentosChange={setDocumentos}
            categorias_documentos={categorias_documentos}
          />
        </ConteinerComRotulo>
      </VStack>
    </VStack>
  );
}
