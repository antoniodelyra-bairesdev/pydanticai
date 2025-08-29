"use client";

import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box,
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Divider,
  Heading,
  HStack,
  Icon,
  Input,
  Link,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Progress,
  Stack,
  Step,
  StepDescription,
  StepIcon,
  StepIndicator,
  StepNumber,
  Stepper,
  StepSeparator,
  StepStatus,
  StepTitle,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  useDisclosure,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import VisualizacaoPastas from "./VisualizacaoPastas";
import {
  ArquivoCarteira,
  PastaCarteiras,
  ResultadoExportacao,
} from "@/lib/types/api/iv/carteiras";
import Hint from "@/app/_components/texto/Hint";
import { useAsync, useHTTP } from "@/lib/hooks";
import {
  IoArrowForwardOutline,
  IoCheckmarkOutline,
  IoCloseOutline,
  IoCloudDownloadOutline,
  IoCloudUploadOutline,
  IoDocumentOutline,
  IoHelpOutline,
  IoInformationCircleOutline,
  IoOpenOutline,
} from "react-icons/io5";
import ContagemBolinhas from "@/app/carteira-diaria/_components/ContagemBolinhas";
import Seta from "@/app/carteira-diaria/_components/Seta";
import { downloadBlob } from "@/lib/util/http";
import { pathMetadata } from "@/app/path.metadata";
import MiniTela from "./Minitela";
import { getColorHex } from "@/app/theme";

const converterResultado = (resultado: Record<string, string>) => {
  const dados: PastaCarteiras = {
    nome: "Raiz",
    detalhes: null,
    status: "OK",
    subpastas: [],
    carteiras: [],
  };
  Object.entries(resultado).forEach(([key, value]) => {
    const pastas = key.split("/").filter((_) => _);
    const arquivo = pastas.pop();
    let pastaMae = dados;
    for (const nomePasta of pastas) {
      let pastaExistente = pastaMae.subpastas.find((p) => p.nome === nomePasta);
      if (!pastaExistente) {
        pastaExistente = {
          nome: nomePasta,
          status: "OK",
          detalhes: null,
          carteiras: [],
          subpastas: [],
        };
        pastaMae.subpastas.push(pastaExistente);
      }
      pastaMae = pastaExistente;
    }
    pastaMae.carteiras.push({
      nome: arquivo ?? "---",
      status: value !== "DESCONHECIDO" ? "OK" : "ERRO",
      detalhes: value !== "DESCONHECIDO" ? null : "Carteira não reconhecida",
      tipo:
        value !== "DESCONHECIDO"
          ? (value as "XML_ANBIMA_4.01" | "XML_ANBIMA_5.0")
          : null,
    });
  });
  return dados.subpastas;
};

export default function ConversorComponent() {
  const [preprocessamento, setPreprocessamento] = useState<PastaCarteiras[]>(
    [],
  );
  const [exportacao, setExportacao] = useState<PastaCarteiras[]>([]);
  const [download, setDownload] = useState<Blob | null>(null);

  const [carregandoPreprocessamento, iniciarCarregamentoPreprocessamento] =
    useAsync();
  const [carregandoExportacao, iniciarCarregamentoExportacao] = useAsync();

  const httpClient = useHTTP({ withCredentials: true });

  const [arquivos, setArquivos] = useState<FileList | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const preprocessar = useCallback(
    () =>
      iniciarCarregamentoPreprocessamento(async () => {
        setPreprocessamento([]);
        setExportacao([]);
        setProgressoConversao(0);
        setTamanhoConversao(0);
        setDownload(null);
        if (!arquivos) return;
        const body = new FormData();
        for (const arquivo of arquivos) {
          body.append("arquivos", arquivo);
        }
        const response = await httpClient.fetch(
          "v1/fundos/carteiras/conversor/processar?pre=true",
          {
            hideToast: { success: true },
            method: "POST",
            multipart: true,
            body,
          },
        );
        if (!response.ok) return;

        setPreprocessamento(converterResultado(await response.json()));
      }),
    [arquivos],
  );

  const converter = useCallback(
    () =>
      iniciarCarregamentoExportacao(async () => {
        setExportacao([]);
        setProgressoConversao(0);
        setTamanhoConversao(0);
        setDownload(null);
        if (!arquivos) return;
        const body = new FormData();
        for (const arquivo of arquivos) {
          body.append("arquivos", arquivo);
        }
        const response = await httpClient.fetch(
          "v1/fundos/carteiras/conversor/processar?pre=false",
          {
            hideToast: { success: true },
            method: "POST",
            multipart: true,
            body,
          },
        );
        if (!response.ok) return;
        const resultado = await response.formData();
        const dados = resultado.get("dados") as string;
        setExportacao(converterResultado(JSON.parse(dados)));
        const blob = resultado.get("arquivo") as Blob;
        setDownload(blob);
      }),
    [arquivos],
  );

  const [progressoConversao, setProgressoConversao] = useState(0);
  const [tamanhoConversao, setTamanhoConversao] = useState(0);

  const limpar = useCallback(() => {
    if (inputRef.current) {
      (inputRef.current as any).value = null;
    }
    setArquivos(null);
    setPreprocessamento([]);
    setExportacao([]);
    setProgressoConversao(0);
    setTamanhoConversao(0);
    setDownload(null);
  }, []);

  const {
    isOpen: isHelpOpen,
    onClose: onHelpClose,
    onOpen: onHelpOpen,
  } = useDisclosure();

  useEffect(() => {
    console.log({ arquivos });
  }, [arquivos]);

  const [paginaHelp, setPaginaHelp] = useState(0);
  const paginasHelp = useMemo(
    () => [
      <VStack alignItems="stretch" w="100%" p="12px 24px" gap="24px">
        <VStack alignItems="stretch" fontSize="sm" lineHeight={1.2}>
          <Heading size="sm">Painel</Heading>
          <Text textAlign="justify">
            A barra superior é o painel de controle da ferramenta. Nela você
            fará a limpeza, importação, pré-processamento, processamento e
            exportação das carteiras
          </Text>
        </VStack>
      </VStack>,
      <VStack alignItems="stretch" w="100%" p="12px 24px" gap="24px">
        <VStack alignItems="stretch" fontSize="sm" lineHeight={1.2}>
          <Heading size="sm">Visualização</Heading>
          <Text textAlign="justify">
            Os painéis da esquerda e da direita na parte de baixo mostram,
            respectivamente, um resumo dos dados importados e um resumo dos
            dados processados pela ferramenta.
          </Text>
        </VStack>
      </VStack>,
      <VStack alignItems="stretch" w="100%" p="12px 24px" gap="24px">
        <VStack alignItems="stretch" fontSize="sm" lineHeight={1.2}>
          <Heading size="sm">Importação de arquivos (1/2)</Heading>
          <Text textAlign="justify">
            Somente arquivos no formato <kbd>.xml</kbd> e <kbd>.zip</kbd> serão
            aceitos pela ferramenta. Múltiplos arquivos podem ser processados de
            uma vez. Caso tenha uma carteira XML nomeada com uma extensão
            diferente - <kbd>.txt</kbd>, por exemplo - a ferramenta se recusará
            a ler o arquivo. Você precisará renomeá-lo para a extensão correta:{" "}
            <kbd>.xml</kbd>.
          </Text>
        </VStack>
      </VStack>,
      <VStack alignItems="stretch" w="100%" p="12px 24px" gap="24px">
        <VStack alignItems="stretch" fontSize="sm" lineHeight={1.2}>
          <Heading size="sm">Importação de arquivos (2/2)</Heading>
          <Text textAlign="justify">
            Selecione os arquivos desejados e clique em "pré-processar". O botão
            só ficará disponível para clique após selecionar os arquivos.
          </Text>
        </VStack>
      </VStack>,
      <VStack alignItems="stretch" w="100%" p="12px 24px" gap="24px">
        <VStack alignItems="stretch" fontSize="sm" lineHeight={1.2}>
          <Heading size="sm">Resultado do pré-processamento (1/4)</Heading>
          <Text textAlign="justify">
            O painel mostrará quais arquivos foram lidos, qual a hierarquia de
            pastas e qual o tipo de carteira detectada.
          </Text>
        </VStack>
      </VStack>,
      <VStack alignItems="stretch" w="100%" p="12px 24px" gap="24px">
        <VStack alignItems="stretch" fontSize="sm" lineHeight={1.2}>
          <Heading size="sm">Resultado do pré-processamento (2/4)</Heading>
          <Text textAlign="justify">
            Arquivos XML 4.01 serão mostrados com ícone verde. Estas carteiras
            não serão mexidas e a ferramenta irá ignorá-las no processo de
            conversão.
          </Text>
        </VStack>
      </VStack>,
      <VStack alignItems="stretch" w="100%" p="12px 24px" gap="24px">
        <VStack alignItems="stretch" fontSize="sm" lineHeight={1.2}>
          <Heading size="sm">Resultado do pré-processamento (3/4)</Heading>
          <Text textAlign="justify">
            Arquivos XML 5.0 serão mostrados com ícone roxo, junto com um
            informativo de que os arquivos serão convertidos para um ou mais
            XMLs 4.01, dependendo de quantos produtos de investimento são
            informados dentro do XML.
          </Text>
        </VStack>
      </VStack>,
      <VStack alignItems="stretch" w="100%" p="12px 24px" gap="24px">
        <VStack alignItems="stretch" fontSize="sm" lineHeight={1.2}>
          <Heading size="sm">Resultado do pré-processamento (4/4)</Heading>
          <Text textAlign="justify">
            Arquivos que não são XMLs 4.01 ou XMLs 5.0 (ou são, mas não
            conseguiram ser processados), serão mostrados com ícone vermelho.
            Estes arquivos também não serão mexidos e a ferramenta irá
            ignorá-los no processo de conversão.
          </Text>
        </VStack>
      </VStack>,
      <VStack alignItems="stretch" w="100%" p="12px 24px" gap="24px">
        <VStack alignItems="stretch" fontSize="sm" lineHeight={1.2}>
          <Heading size="sm">Exportação (1/5)</Heading>
          <Text textAlign="justify">
            Caso algum arquivo desejado não esteja presente ou possua algum
            problema, recomendamos verificar o arquivo e a carteira para
            verificar se ela não está mal-formada.
          </Text>
          <Text textAlign="justify">
            Caso contrário, clique em "converter" para iniciar o processo de
            conversão das carteiras.
          </Text>
        </VStack>
      </VStack>,
      <VStack alignItems="stretch" w="100%" p="12px 24px" gap="24px">
        <VStack alignItems="stretch" fontSize="sm" lineHeight={1.2}>
          <Heading size="sm">Exportação (2/5)</Heading>
          <Text textAlign="justify">
            Uma barra de carregamento mostrará que a conversão está sendo feita.
            A conversão pode demorar caso várias carteiras tenham sido
            informadas. Atualmente não mostramos o progresso individual de cada
            conversão.
          </Text>
        </VStack>
      </VStack>,
      <VStack alignItems="stretch" w="100%" p="12px 24px" gap="24px">
        <VStack alignItems="stretch" fontSize="sm" lineHeight={1.2}>
          <Heading size="sm">Exportação (3/5)</Heading>
          <Text textAlign="justify">
            O resultado da conversão ficará disponível no painel direito,
            mostrando quais os arquivos resultantes (incluindo os arquivos que
            não foram modificados).
          </Text>
        </VStack>
      </VStack>,
      <VStack alignItems="stretch" w="100%" p="12px 24px" gap="24px">
        <VStack alignItems="stretch" fontSize="sm" lineHeight={1.2}>
          <Heading size="sm">Exportação (4/5)</Heading>
          <Text textAlign="justify">
            Alguns XMLs 5.0 podem gerar mais de um XML 4.01 como resultado, pois
            possuem mais de um produto dentro da carteira como, por exemplo,
            classes com subclasses.
          </Text>
          <Table size="sm">
            <Thead>
              <Tr>
                <Th>Original</Th>
                <Th>Exportado</Th>
              </Tr>
            </Thead>
            <Tbody>
              <Tr>
                <Td p={0}>
                  <HStack
                    p="2px 16px"
                    bgColor="roxo.50"
                    color="roxo.main"
                    fontSize="xs"
                    position="relative"
                  >
                    <Text flex={1}>SubClasse_0</Text>
                    <Text fontWeight={600}>XML 5.0</Text>
                    <Icon
                      as={IoArrowForwardOutline}
                      position="absolute"
                      right="-6px"
                    />
                  </HStack>
                </Td>
                <Td p={0}>
                  <HStack
                    p="2px 16px"
                    bgColor="verde.50"
                    color="verde.main"
                    fontSize="xs"
                  >
                    <Text fontWeight={600}>XML 4.01</Text>
                    <Text flex={1}>SubClasse_0</Text>
                  </HStack>
                </Td>
              </Tr>
              <Tr>
                <Td p={0}>
                  <HStack
                    p="2px 16px"
                    bgColor="roxo.50"
                    color="roxo.main"
                    fontSize="xs"
                    position="relative"
                  >
                    <Text flex={1}>Cart_Adm_1</Text>
                    <Text fontWeight={600}>XML 5.0</Text>
                    <Icon
                      as={IoArrowForwardOutline}
                      position="absolute"
                      right="-6px"
                    />
                  </HStack>
                </Td>
                <Td p={0}>
                  <HStack
                    p="2px 16px"
                    bgColor="verde.50"
                    color="verde.main"
                    fontSize="xs"
                  >
                    <Text fontWeight={600}>XML 4.01</Text>
                    <Text flex={1}>Cart_Adm_1</Text>
                  </HStack>
                </Td>
              </Tr>
              <Tr>
                <Td p={0}>
                  <HStack
                    p="2px 16px"
                    bgColor="roxo.50"
                    color="roxo.main"
                    fontSize="xs"
                    position="relative"
                  >
                    <Text flex={1}>Classe_Sem_SubCl_2</Text>
                    <Text fontWeight={600}>XML 5.0</Text>
                    <Icon
                      as={IoArrowForwardOutline}
                      position="absolute"
                      right="-6px"
                    />
                  </HStack>
                </Td>
                <Td p={0}>
                  <HStack
                    p="2px 16px"
                    bgColor="verde.50"
                    color="verde.main"
                    fontSize="xs"
                  >
                    <Text fontWeight={600}>XML 4.01</Text>
                    <Text flex={1}>Classe_Sem_SubCl_2</Text>
                  </HStack>
                </Td>
              </Tr>
              <Tr>
                <Td p={0}>
                  <HStack
                    p="2px 16px"
                    bgColor="roxo.50"
                    color="roxo.main"
                    fontSize="xs"
                    position="relative"
                  >
                    <Text flex={1}>Fundo_Nao_Adaptado_3</Text>
                    <Text fontWeight={600}>XML 5.0</Text>
                    <Icon
                      as={IoArrowForwardOutline}
                      position="absolute"
                      right="-6px"
                    />
                  </HStack>
                </Td>
                <Td p={0}>
                  <HStack
                    p="2px 16px"
                    bgColor="verde.50"
                    color="verde.main"
                    fontSize="xs"
                  >
                    <Text fontWeight={600}>XML 4.01</Text>
                    <Text flex={1}>Fundo_Nao_Adaptado_3</Text>
                  </HStack>
                </Td>
              </Tr>
              <Tr>
                <Td p={0} rowSpan={4}>
                  <HStack
                    p="2px 16px"
                    bgColor="roxo.50"
                    color="roxo.main"
                    fontSize="xs"
                    position="relative"
                  >
                    <Text flex={1}>Classe_4 + SubCl_5 + SubCl_6</Text>
                    <Text fontWeight={600}>XML 5.0</Text>
                    <Icon
                      as={IoArrowForwardOutline}
                      position="absolute"
                      top="-6px"
                      right="-6px"
                      transform="rotate(-45deg)"
                    />
                    <Icon
                      as={IoArrowForwardOutline}
                      position="absolute"
                      right="-6px"
                    />
                    <Icon
                      as={IoArrowForwardOutline}
                      position="absolute"
                      bottom="-6px"
                      right="-6px"
                      transform="rotate(45deg)"
                    />
                  </HStack>
                </Td>
              </Tr>
              <Tr>
                <Td p={0}>
                  <HStack
                    p="2px 16px"
                    bgColor="verde.50"
                    color="verde.main"
                    fontSize="xs"
                  >
                    <Text fontWeight={600}>XML 4.01</Text>
                    <Text flex={1}>Classe_4</Text>
                  </HStack>
                </Td>
              </Tr>
              <Tr>
                <Td p={0}>
                  <HStack
                    p="2px 16px"
                    bgColor="verde.50"
                    color="verde.main"
                    fontSize="xs"
                  >
                    <Text fontWeight={600}>XML 4.01</Text>
                    <Text flex={1}>SubCl_5</Text>
                  </HStack>
                </Td>
              </Tr>
              <Tr>
                <Td p={0}>
                  <HStack
                    p="2px 16px"
                    bgColor="verde.50"
                    color="verde.main"
                    fontSize="xs"
                  >
                    <Text fontWeight={600}>XML 4.01</Text>
                    <Text flex={1}>SubCl_6</Text>
                  </HStack>
                </Td>
              </Tr>
            </Tbody>
          </Table>
        </VStack>
      </VStack>,
      <VStack alignItems="stretch" w="100%" p="12px 24px" gap="24px">
        <VStack alignItems="stretch" fontSize="sm" lineHeight={1.2}>
          <Heading size="sm">Exportação (5/5)</Heading>
          <Text textAlign="justify">
            O arquivo final estará disponível em formato de pasta compactada no
            formato <kbd>.zip</kbd>. Clique em "Baixar" para salvar o arquivo.
          </Text>
        </VStack>
      </VStack>,
    ],
    [],
  );

  return (
    <VStack
      alignItems="stretch"
      w="100%"
      h="100%"
      overflow="hidden"
      p="8px"
      bgColor="cinza.main"
    >
      <Stack direction={{ base: "column", lg: "row" }} alignItems="stretch">
        <Card position="relative" role="group" overflow="hidden">
          <Box
            position="absolute"
            left={0}
            top={0}
            bottom={0}
            w="4px"
            bgColor="azul_1.main"
            _groupHover={{ bgColor: "azul_2.main" }}
            transition="0.125s background-color"
          />
          <CardHeader>
            <HStack>
              <HStack
                color="verde.main"
                justifyContent="center"
                mt="4px"
                position="relative"
              >
                <Icon w="24px" h="24px" as={IoDocumentOutline} />
                <Text
                  fontWeight={700}
                  mt="3px"
                  textAlign="center"
                  fontSize="6px"
                  position="absolute"
                >
                  XML
                </Text>
              </HStack>
              <Heading size="md" fontWeight={600}>
                Conversor de carteiras
              </Heading>
            </HStack>
          </CardHeader>
          <CardFooter p="0 20px">
            <HStack flexWrap="wrap" w="100%">
              <Button
                flex={1}
                size="xs"
                leftIcon={<Icon as={IoHelpOutline} />}
                onClick={onHelpOpen}
              >
                Manual de uso
              </Button>
              <Link
                fontSize="xs"
                fontWeight={600}
                textDecoration="underline"
                textDecorationColor="azul_2.main"
                color="azul_2.main"
                href="https://www.anbima.com.br/pt_br/representar/foruns-de-representacao/servicos-fiduciarios/servicos-fiduciarios.htm"
                rel="noopener noreferrer"
                target="_blank"
              >
                Mais informações
              </Link>
            </HStack>
          </CardFooter>
          <Modal isOpen={isHelpOpen} onClose={onHelpClose} size="2xl">
            <ModalOverlay />
            <ModalContent>
              <ModalHeader>
                <Heading size="md">Manual de uso</Heading>
              </ModalHeader>
              <Divider />
              <ModalCloseButton />
              <ModalBody>
                <HStack w="100%" position="relative">
                  <VStack
                    flex={1}
                    alignItems="stretch"
                    justifyContent="space-between"
                    minH="60vh"
                  >
                    {paginasHelp[paginaHelp]}
                    <VStack alignItems="stretch" p="24px">
                      <MiniTela passo={paginaHelp} />
                    </VStack>
                  </VStack>
                  <Seta
                    left="-9px"
                    position="absolute"
                    orientacao="ESQUERDA"
                    posicao={paginaHelp}
                    setPosicao={setPaginaHelp}
                    tamanho={paginasHelp.length}
                  />
                  <Seta
                    right="-9px"
                    position="absolute"
                    orientacao="DIREITA"
                    posicao={paginaHelp}
                    setPosicao={setPaginaHelp}
                    tamanho={paginasHelp.length}
                  />
                </HStack>
              </ModalBody>
              <ModalFooter>
                <HStack w="100%" justifyContent="center">
                  <ContagemBolinhas
                    posicao={paginaHelp}
                    tamanho={paginasHelp.length}
                  />
                </HStack>
              </ModalFooter>
            </ModalContent>
          </Modal>
        </Card>
        <Card flex={1}>
          <CardBody>
            <Stepper
              colorScheme="verde"
              size="sm"
              flexWrap="wrap"
              index={
                exportacao.length
                  ? 3
                  : preprocessamento.length
                    ? 2
                    : arquivos
                      ? 1
                      : 0
              }
              gap={0}
            >
              <Step key={0} style={{ gap: 0, flex: 1 }}>
                <HStack
                  border="1px solid"
                  borderColor="cinza.main"
                  borderRadius="4px"
                  padding="4px 8px"
                  flex={1}
                >
                  <StepIndicator>
                    <StepStatus
                      complete={<StepIcon />}
                      incomplete={<StepNumber />}
                      active={<StepNumber />}
                    />
                  </StepIndicator>
                  <Box overflow="hidden">
                    <StepTitle>Escolher arquivos</StepTitle>
                    <StepDescription>
                      <VStack alignItems="stretch" gap="4px">
                        <Input
                          p={0}
                          size="xs"
                          type="file"
                          accept=".zip,.xml"
                          multiple
                          onChange={(ev) => setArquivos(ev.target.files)}
                          ref={inputRef}
                        />
                        <HStack gap="4px">
                          <Button
                            flex={1}
                            size="xs"
                            leftIcon={
                              <Icon as={IoCloseOutline} color="rosa.main" />
                            }
                            onClick={limpar}
                            isDisabled={
                              !arquivos?.length ||
                              carregandoExportacao ||
                              carregandoPreprocessamento
                            }
                          >
                            Limpar
                          </Button>
                          <Button
                            flex={2}
                            size="xs"
                            leftIcon={
                              <Icon
                                as={IoCheckmarkOutline}
                                color="azul_2.main"
                              />
                            }
                            onClick={preprocessar}
                            isDisabled={
                              !arquivos?.length ||
                              carregandoExportacao ||
                              carregandoPreprocessamento
                            }
                          >
                            Pré-processar
                          </Button>
                        </HStack>
                      </VStack>
                    </StepDescription>
                  </Box>
                </HStack>
                <StepSeparator />
              </Step>
              <Step key={1} style={{ gap: 0, flex: 1 }}>
                <HStack
                  border="1px solid"
                  borderColor="cinza.main"
                  borderRadius="4px"
                  padding="4px 8px"
                  flex={1}
                >
                  <StepIndicator>
                    <StepStatus
                      complete={<StepIcon />}
                      incomplete={<StepNumber />}
                      active={<StepNumber />}
                    />
                  </StepIndicator>
                  <Box>
                    <StepTitle>Pré-processamento</StepTitle>
                    <StepDescription>
                      <VStack gap="4px" alignItems="stretch">
                        <HStack h="24px">
                          <Text>Conferir detalhes</Text>
                        </HStack>
                        <HStack
                          maxW="90vw"
                          w="200px"
                          h="24px"
                          justifyContent="center"
                        >
                          {carregandoPreprocessamento ? (
                            <>
                              <Progress
                                flex={1}
                                colorScheme="verde"
                                isIndeterminate
                                borderRadius="4px"
                                h="12px"
                                value={24}
                              />
                              <Text
                                fontSize="10px"
                                fontWeight={600}
                                position="absolute"
                              >
                                Carregando...
                              </Text>
                            </>
                          ) : (
                            <Button
                              isDisabled={
                                !preprocessamento.length ||
                                carregandoExportacao ||
                                carregandoPreprocessamento
                              }
                              flex={1}
                              leftIcon={
                                <Icon
                                  as={IoCloudUploadOutline}
                                  color="roxo.main"
                                />
                              }
                              size="xs"
                              onClick={converter}
                            >
                              Converter
                            </Button>
                          )}
                        </HStack>
                      </VStack>
                    </StepDescription>
                  </Box>
                </HStack>
                <StepSeparator />
              </Step>
              <Step key={2} style={{ gap: 0, flex: 1 }}>
                <HStack
                  border="1px solid"
                  borderColor="cinza.main"
                  borderRadius="4px"
                  padding="4px 8px"
                  flex={1}
                >
                  <StepIndicator>
                    <StepStatus
                      complete={<StepIcon />}
                      incomplete={<StepNumber />}
                      active={<StepNumber />}
                    />
                  </StepIndicator>
                  <Box>
                    <StepTitle>Conversão das carteiras</StepTitle>
                    <StepDescription>
                      <VStack gap="4px" alignItems="stretch">
                        <HStack h="24px">
                          <Text>Progresso da conversão</Text>
                        </HStack>
                        <HStack
                          maxW="90vw"
                          w="200px"
                          h="24px"
                          justifyContent="center"
                        >
                          <Progress
                            flex={1}
                            isIndeterminate={carregandoExportacao}
                            colorScheme="verde"
                            borderRadius="4px"
                            h="12px"
                            value={
                              (tamanhoConversao === 0
                                ? 0
                                : progressoConversao / tamanhoConversao) * 100
                            }
                          />
                          <Text
                            fontSize="10px"
                            fontWeight={600}
                            position="absolute"
                            color={
                              progressoConversao === tamanhoConversao
                                ? "white"
                                : "black"
                            }
                          >
                            {tamanhoConversao
                              ? `${progressoConversao}/${tamanhoConversao}`
                              : "---"}
                          </Text>
                        </HStack>
                      </VStack>
                    </StepDescription>
                  </Box>
                </HStack>
                <StepSeparator />
              </Step>
              <Step key={3} style={{ gap: 0, flex: 1 }}>
                <HStack
                  border="1px solid"
                  borderColor="cinza.main"
                  borderRadius="4px"
                  padding="4px 8px"
                  flex={1}
                >
                  <StepIndicator>
                    <StepStatus
                      complete={<StepIcon />}
                      incomplete={<StepNumber />}
                      active={<StepNumber />}
                    />
                  </StepIndicator>
                  <Box>
                    <StepTitle>Exportação</StepTitle>
                    <StepDescription>
                      <VStack gap="4px" alignItems="stretch">
                        <HStack h="24px">
                          <Text>Arquivo disponível para download</Text>
                        </HStack>
                        <Button
                          isDisabled={!download}
                          colorScheme="azul_1"
                          size="xs"
                          leftIcon={
                            <Icon
                              as={IoCloudDownloadOutline}
                              color="verde.main"
                            />
                          }
                          onClick={() =>
                            download && downloadBlob(download, download?.name)
                          }
                        >
                          Baixar
                        </Button>
                      </VStack>
                    </StepDescription>
                  </Box>
                </HStack>
                <StepSeparator />
              </Step>
            </Stepper>
          </CardBody>
        </Card>
      </Stack>
      <HStack flex={1} alignItems="stretch" overflow="hidden">
        <VStack flex={1} alignItems="stretch" overflow="hidden">
          <Card bgColor="azul_1.main" color="white">
            <CardBody>
              <Heading size="sm">Pré-processamento</Heading>
            </CardBody>
          </Card>
          <Card flex={1} overflow="auto">
            <VisualizacaoPastas pastas={preprocessamento} />
          </Card>
        </VStack>
        <VStack flex={1} alignItems="stretch" overflow="hidden">
          <Card bgColor="azul_1.main" color="white">
            <CardBody>
              <Heading size="sm">Exportação</Heading>
            </CardBody>
          </Card>
          <Card flex={1} overflow="auto">
            <VisualizacaoPastas pastas={exportacao} />
          </Card>
        </VStack>
      </HStack>
    </VStack>
  );
}
