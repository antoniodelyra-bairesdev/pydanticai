"use client";

import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import {
  HStack,
  Step,
  StepIcon,
  StepIndicator,
  StepNumber,
  Stepper,
  StepSeparator,
  StepStatus,
  StepTitle,
  TabPanel,
  TabPanels,
  Tabs,
  Text,
  useDisclosure,
  useSteps,
  VStack,
} from "@chakra-ui/react";
import React, { useState } from "react";
import PassoProcessamento from "./passos/PassoProcessamento";
import PassoSeparacao from "./passos/PassoSeparacao";
import {
  MercadoEnum,
  SugestaoAlocacao,
} from "@/lib/types/api/iv/operacoes/processamento";
import { BoletaClient } from "@/lib/providers/AlocacoesProvider";

export type ModalNovaBoletaProps = {
  isOpen: boolean;
  onClose: () => void;
  onBoletasChange: (boletas: BoletaClient[]) => void;
};

export default function ModalNovaBoleta({
  isOpen,
  onClose,
  onBoletasChange,
}: ModalNovaBoletaProps) {
  const steps = ["Processamento", "Separação" /*"Revisão"*/];
  const { activeStep, setActiveStep } = useSteps({
    index: 0,
    count: steps.length,
  });

  const stepper = (
    <HStack w="100%" justifyContent="center">
      <Stepper flex={1} maxW="320px" colorScheme="verde" index={activeStep}>
        {steps.map((s) => (
          <Step key={s}>
            <VStack>
              <StepIndicator>
                <StepStatus
                  complete={<StepIcon />}
                  incomplete={<StepNumber />}
                  active={<StepNumber />}
                />
              </StepIndicator>
              <StepTitle>{s}</StepTitle>
            </VStack>
            <StepSeparator />
          </Step>
        ))}
      </Stepper>
    </HStack>
  );

  const prev = () => {
    if (activeStep === 0) {
      return onClose();
    }
    setActiveStep(Math.max(activeStep - 1, 0));
  };

  const {
    isOpen: isOpenConfirm,
    onOpen: onOpenConfirm,
    onClose: onCloseConfirm,
  } = useDisclosure();

  const next = () => {
    if (activeStep === 0) {
      return onOpenConfirm();
    }
    if (activeStep === steps.length - 1) {
      onBoletasChange(boletas);
      setActiveStep(0);
      setAlocacoes([]);
      setBoletas([]);
      return onClose();
    }
    setActiveStep((activeStep + 1) % steps.length);
  };

  const [alocacoes, setAlocacoes] = useState<SugestaoAlocacao[]>([]);
  const [boletas, setBoletas] = useState<BoletaClient[]>([]);

  return (
    <ConfirmModal
      isOpen={isOpen}
      onClose={() => {}}
      title={stepper}
      size="6xl"
      cancelContent={activeStep === 0 ? "Cancelar" : "Anterior"}
      confirmContent={
        activeStep === 1 ? "Adicionar alocações ao rascunho" : "Próximo"
      }
      confirmEnabled={
        (activeStep === 0 && alocacoes.length > 0) ||
        (activeStep === 1 &&
          boletas.length > 0 &&
          boletas.every(
            (b) =>
              ((b.boleta.id < 0 &&
                b.boleta.mercado_negociado_id !== MercadoEnum.INDEFINIDO) ||
                b.boleta.id > 0) &&
              b.boleta.data_liquidacao,
          ))
      }
      onCancelAction={prev}
      onConfirmAction={next}
    >
      <Tabs index={activeStep}>
        <TabPanels>
          <TabPanel p={0}>
            <PassoProcessamento onAlocacoesChange={setAlocacoes} />
          </TabPanel>
          <TabPanel p={0}>
            <PassoSeparacao
              alocacoes={alocacoes}
              onBoletasChange={setBoletas}
            />
          </TabPanel>
          {/* <TabPanel p={0}>
            <PassoRevisao boletas={boletas} />
          </TabPanel> */}
        </TabPanels>
      </Tabs>
      <ConfirmModal
        isOpen={isOpenConfirm}
        onClose={onCloseConfirm}
        onConfirmAction={() => {
          setActiveStep(1);
        }}
        title="Aviso"
        cancelContent="Voltar e alterar arquivo"
        confirmContent="Prosseguir com alocações"
        size="xl"
      >
        <Text fontSize="sm">
          Linhas de operação com erro serão{" "}
          <Text as="strong" color="rosa.main">
            desconsideradas
          </Text>
          .
        </Text>
        <Text fontSize="sm">
          Linhas de operação que possuem aviso serão{" "}
          <Text as="strong" color="amarelo.main">
            mantidas
          </Text>
          .
        </Text>
        <Text m="12px 0" fontSize="sm" fontWeight="bold">
          Deseja continuar?
        </Text>
      </ConfirmModal>
    </ConfirmModal>
  );
}
