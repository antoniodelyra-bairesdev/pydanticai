import { ModificationMap } from "@/app/_components/grid/ValidationGrid";
import {
  ArrowBackIcon,
  ArrowUpIcon,
  CalendarIcon,
  CheckIcon,
  SmallCloseIcon,
} from "@chakra-ui/icons";
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
  CardHeader,
  Divider,
  HStack,
  Heading,
  Icon,
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Progress,
  TabPanel,
  TabPanels,
  Tabs,
  Text,
  VStack,
  keyframes,
  useDisclosure,
  useSteps,
} from "@chakra-ui/react";
import { useMemo, useState } from "react";
import {
  IoBug,
  IoCheckmarkCircle,
  IoChevronForwardCircleOutline,
  IoCloseCircle,
  IoEllipseOutline,
  IoSyncCircleOutline,
  IoWarning,
} from "react-icons/io5";
import JSONText from "../misc/JSONText";
import ConfirmModal from "./ConfirmModal";
import DiffSummary, {
  DiffSummaryProps,
  NestedDiffArrayProperties,
} from "./DiffSummary";

import { motion } from "framer-motion";
import Comment from "../misc/Comment";

export type DiffModalProps<T> = DiffSummaryProps<T> & {
  isOpen: boolean;
  onClose: () => void;
  onCloseAfterSuccess: () => void;
  submitAction: (diff: {
    added: T[];
    modified: ModificationMap<T>;
    deleted: T[];
    nested?: Partial<NestedDiffArrayProperties<T>>;
  }) => (undefined | null | object) | Promise<undefined | null | object>;
};

export enum Status {
  ERROR,
  STOPPED,
  RUNNING,
  OK,
}

const animationKeyframes = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const animation = `${animationKeyframes} 1s linear infinite`;

export default function DiffModal<T>({
  added,
  modified,
  deleted,
  identifier,
  colDefs,
  nested,
  isOpen,
  onClose,
  onCloseAfterSuccess,
  submitAction,
}: DiffModalProps<T>) {
  const {
    isOpen: isConfirmOpen,
    onOpen: onConfirmOpen,
    onClose: onConfirmClose,
  } = useDisclosure();

  const { activeStep, setActiveStep } = useSteps({ count: 2 });

  const [running, setRunning] = useState(false);

  const [error, setError] = useState<object | null>(null);

  const actions = useMemo(
    () => [
      [
        { leftIcon: <SmallCloseIcon />, title: "Fechar", action: onClose },
        {
          rightIcon: <ArrowUpIcon />,
          title: "Executar",
          colorScheme: "azul_2",
          action: onConfirmOpen,
          isDisabled: false,
        },
      ],
      [
        {
          leftIcon: <ArrowBackIcon />,
          title: "Voltar",
          isDisabled: !error,
          action() {
            setActiveStep(0);
          },
        },
        {
          rightIcon: <CheckIcon />,
          title: "Concluir",
          colorScheme: "verde",
          isDisabled: error,
          action: () => {
            setActiveStep(0);
            setError(null);
            onClose();
            onCloseAfterSuccess();
          },
        },
      ],
    ],
    [error],
  );

  return (
    <>
      <Modal size="6xl" isCentered isOpen={isOpen} onClose={() => {}}>
        <ModalOverlay />
        <ModalContent height="90vh" overflow="hidden">
          <ModalHeader
            bgColor="azul_1.600"
            display="flex"
            flexDirection="row"
            justifyContent="center"
            p="8px"
          >
            <HStack w="20%" minW="180px">
              <VStack gap={0}>
                {activeStep === 0 ? (
                  <Icon
                    fontSize="3xl"
                    as={IoChevronForwardCircleOutline}
                    color="amarelo.main"
                  />
                ) : (
                  <Icon
                    fontSize="3xl"
                    as={IoCheckmarkCircle}
                    color="verde.main"
                  />
                )}
                <Text fontSize="md" color="white">
                  Revisão
                </Text>
              </VStack>
              <Divider
                borderColor={activeStep === 1 ? "verde.main" : "white"}
                borderWidth="1px"
              />
              <VStack gap={0}>
                {activeStep === 1 ? (
                  running ? (
                    <Box
                      as={motion.div}
                      display="flex"
                      flexDirection="column"
                      justifyContent="center"
                      animation={animation}
                    >
                      <Icon
                        fontSize="3xl"
                        as={IoSyncCircleOutline}
                        color="amarelo.main"
                      />
                    </Box>
                  ) : error ? (
                    <Icon fontSize="3xl" as={IoCloseCircle} color="rosa.main" />
                  ) : (
                    <Icon
                      fontSize="3xl"
                      as={IoCheckmarkCircle}
                      color="verde.main"
                    />
                  )
                ) : (
                  <Icon fontSize="3xl" as={IoEllipseOutline} color="white" />
                )}
                <Text fontSize="md" color="white">
                  Resultado
                </Text>
              </VStack>
            </HStack>
          </ModalHeader>
          <Divider />
          <ModalBody p={0} m={0} h="100%" overflowY="auto">
            <Tabs index={activeStep} h="100%">
              <TabPanels p={0} h="100%">
                <TabPanel p={0} h="100%" overflowY="auto">
                  <DiffSummary
                    identifier={identifier}
                    colDefs={colDefs}
                    added={added}
                    deleted={deleted}
                    modified={modified}
                    nested={nested}
                  />
                </TabPanel>
                <TabPanel h="100%" p={0}>
                  <VStack h="100%" alignItems="stretch">
                    <Box flex={1} p="32px">
                      {!running && (
                        <Card overflow="hidden">
                          <CardHeader
                            bgColor={error ? "rosa.main" : "verde.main"}
                          >
                            <Heading size="md" color="white">
                              {error ? (
                                <>
                                  <Icon
                                    verticalAlign="bottom"
                                    as={IoCloseCircle}
                                    mr="8px"
                                  />{" "}
                                  Erro.
                                </>
                              ) : (
                                <>
                                  <Icon
                                    verticalAlign="bottom"
                                    as={IoCheckmarkCircle}
                                    mr="8px"
                                  />{" "}
                                  Sucesso!
                                </>
                              )}
                            </Heading>
                          </CardHeader>
                          <CardBody p={0}>
                            {error ? (
                              <>
                                <Text m="12px" fontSize="sm">
                                  Houve uma falha durante a execução. Entre em
                                  contato com o time de tecnologia.
                                </Text>
                                <Accordion
                                  allowMultiple={true}
                                  defaultIndex={[0]}
                                >
                                  <AccordionItem p={0} border="none">
                                    <AccordionButton>
                                      <HStack
                                        color="cinza.500"
                                        fontSize="xs"
                                        flex={1}
                                      >
                                        <Icon as={IoBug} />
                                        <Text>Detalhes técnicos</Text>
                                      </HStack>
                                      <AccordionIcon color="cinza.500" />
                                    </AccordionButton>
                                    <AccordionPanel p={0}>
                                      <JSONText json={error} />
                                    </AccordionPanel>
                                  </AccordionItem>
                                </Accordion>
                              </>
                            ) : (
                              <Text m="12px" fontSize="sm">
                                A operação foi concluída com êxito. Você já pode
                                fechar a janela.
                              </Text>
                            )}
                          </CardBody>
                        </Card>
                      )}
                    </Box>
                    {running && (
                      <Progress isIndeterminate={true} colorScheme="verde" />
                    )}
                  </VStack>
                </TabPanel>
              </TabPanels>
            </Tabs>
          </ModalBody>
          <Divider />
          <ModalFooter gap="8px">
            {actions[activeStep].map(
              ({
                action,
                title,
                colorScheme,
                leftIcon,
                rightIcon,
                isDisabled,
              }) => (
                <Button
                  leftIcon={leftIcon}
                  rightIcon={rightIcon}
                  colorScheme={colorScheme}
                  onClick={action}
                  isDisabled={running || Boolean(isDisabled)}
                  size="sm"
                >
                  {title}
                </Button>
              ),
            )}
          </ModalFooter>
        </ModalContent>
      </Modal>
      <ConfirmModal
        title={
          <Heading size="md" fontWeight="normal">
            <Icon
              verticalAlign="bottom"
              color="laranja.main"
              fontSize="2xl"
              as={IoWarning}
              mr="8px"
            />
            Aviso: As alterações serão armazenadas no banco de dados
          </Heading>
        }
        isOpen={isConfirmOpen}
        onClose={onConfirmClose}
        onConfirmAction={async () => {
          setActiveStep(1);
          setRunning(true);
          let error: object | null = null;
          try {
            error =
              (await submitAction({ added, modified, deleted, nested })) ??
              null;
          } catch (err) {
            error = JSON.parse(JSON.stringify(err));
          } finally {
            setRunning(false);
            setError(error);
          }
        }}
        size="lg"
      >
        <Text fontSize="sm" mb="12px">
          Após clicar em "Confirmar", suas alterações não poderão ser desfeitas.
          Caso não tenha certeza, clique em "Cancelar" e revise suas alterações
          na tela anterior.
        </Text>
        <Comment fontSize="sm">
          <Icon
            as={CalendarIcon}
            color="amarelo.main"
            m="4px"
            mr="8px"
            verticalAlign="bottom"
          />
          <strong>Atenção!</strong> Todas as datas dos ativos alterados{" "}
          <em>(inclusive as datas que não foram diretamente editadas)</em> serão
          corrigidas para o próximo dia útil.
        </Comment>
      </ConfirmModal>
    </>
  );
}
