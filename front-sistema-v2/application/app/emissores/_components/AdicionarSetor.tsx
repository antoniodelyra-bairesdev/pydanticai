import ConfirmModal from "@/app/_components/modal/ConfirmModal";
import { getColorHex } from "@/app/theme";
import { EmissorSetor } from "@/lib/types/api/iv/v1";
import {
  Box,
  Input,
  Card,
  CardBody,
  HStack,
  VStack,
  Icon,
  Text,
  Divider,
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
} from "@chakra-ui/react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { IconType } from "react-icons";
import * as _AllIcons from "react-icons/io5";
import { getIcon } from "./SetoresGrid";

const AllIcons = Object.entries(_AllIcons)
  .filter(([nome]) => nome.endsWith("Outline"))
  .sort(([nomeA], [nomeB]) => nomeA.localeCompare(nomeB))
  .map(
    ([nome, icon]) =>
      [nome.replace("Io", "").replace("Outline", ""), icon] as const,
  );

export type AdicionarSetorProps = {
  setor?: EmissorSetor;

  isOpen: boolean;
  onClose: () => void;
  onConfirm: (setor: EmissorSetor, action: "edit" | "add") => void;
};

export default function ModalSetor({
  setor,
  isOpen,
  onClose,
  onConfirm: onSetorAdded,
}: AdicionarSetorProps) {
  const [setorData, setSetorData] = useState<Partial<EmissorSetor>>(
    setor ?? {},
  );
  const [nome, setNome] = useState(setor?.nome ?? "");

  useEffect(() => {
    if (isOpen === true) {
      setSetorData(setor ?? {});
      setNome(setor?.nome ?? "");
    }
  }, [isOpen]);

  const selecionado = useCallback(
    (nome: string) => nome === setorData?.sistema_icone,
    [setorData],
  );

  const icons = useMemo(
    () => (
      <HStack maxH="50vh" overflowY="auto" p="8px" wrap="wrap">
        {AllIcons.map(([label, icone]) => (
          <Box
            cursor="pointer"
            flex={1}
            bgColor={
              getColorHex(selecionado(label) ? "verde.main" : "cinza.main") +
              "7F"
            }
            _hover={{
              bgColor: selecionado(label) ? "verde.main" : "cinza.main",
            }}
            color={selecionado(label) ? "white" : "black"}
            borderRadius="8px"
            onClick={() => {
              if (selecionado(label))
                return setSetorData({ ...setorData, sistema_icone: undefined });
              setSetorData({ ...setorData, sistema_icone: label });
            }}
          >
            <VStack minW="64px" h="48px" gap={0} justifyContent="center">
              <Icon as={icone} fontSize="20px" />
              <Text fontSize="11px">{label}</Text>
            </VStack>
          </Box>
        ))}
      </HStack>
    ),
    [setorData],
  );

  return (
    <ConfirmModal
      isOpen={isOpen}
      onClose={onClose}
      title={setor ? `Editar ${setor.nome}` : "Adicionar setor"}
      confirmEnabled={nome.trim().length > 0}
      size="2xl"
      onConfirmAction={() => {
        const { id = Math.random(), sistema_icone } = setorData;
        if (!nome) return;
        onSetorAdded(
          { id, nome: nome.trim(), sistema_icone },
          setor ? "edit" : "add",
        );
      }}
    >
      <Text fontSize="xs" mt="12px">
        Nome do setor
      </Text>
      <Input
        size="sm"
        placeholder="Digite o nome do setor..."
        value={nome}
        onChange={(ev) => setNome(ev.target.value)}
      />
      <Text fontSize="xs" mt="24px">
        Utilizar ícone do sistema?
      </Text>
      <Card variant="outline">
        <CardBody p={0}>
          <Accordion allowMultiple={true} defaultIndex={[]}>
            <AccordionItem p={0} border="none">
              <AccordionButton>
                <HStack w="100%" justifyContent="space-between">
                  <Text fontSize="xs">
                    Selecionado:
                    {setorData?.sistema_icone ? (
                      <Text ml="4px" as="span" fontStyle="italic">
                        <Icon
                          verticalAlign="center"
                          mr="4px"
                          as={
                            getIcon(setorData.sistema_icone) ??
                            _AllIcons.IoAlertCircle
                          }
                          color="verde.main"
                        />
                        {setorData?.sistema_icone}
                      </Text>
                    ) : (
                      <Text as="span" color="cinza.500">
                        {" "}
                        Nenhum
                      </Text>
                    )}
                  </Text>
                  <AccordionIcon color="cinza.500" />
                </HStack>
              </AccordionButton>
              <AccordionPanel p={0}>{icons}</AccordionPanel>
            </AccordionItem>
          </Accordion>
        </CardBody>
      </Card>
    </ConfirmModal>
  );
}
