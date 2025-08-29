import TagInput from "@/app/_components/forms/TagInput";
import { Ativo, Evento } from "@/lib/types/api/iv/v1";
import { strCSSColor } from "@/lib/util/string";
import {
  AlertDialog,
  AlertDialogBody,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogOverlay,
  Button,
  Text,
} from "@chakra-ui/react";
import { useRef, useState } from "react";

export type DuplicarAtivoModalProps = {
  isOpen: boolean;
  ativosExistentes: string[];
  onClose(inserted: (Partial<Ativo> & { fluxos: Evento[] })[]): void;

  ativo?: Ativo;
};

export default function InserirAtivoModal({
  ativo,
  isOpen,
  ativosExistentes,
  onClose,
}: DuplicarAtivoModalProps) {
  const [codigos, setCodigos] = useState<string[]>([]);
  const [value, setValue] = useState("");

  const dupCancelRef = useRef<HTMLButtonElement>(null);

  const cancel = () => onClose([]);

  const insertAtivos = () => {
    const novosAtivos: (Partial<Ativo> & { fluxos: Evento[] })[] = [];
    for (const codigo of codigos) {
      const novoAtivo = {
        ...(ativo ? structuredClone(ativo) : { fluxos: [] }),
        codigo,
      };
      novoAtivo.fluxos.forEach((f) => {
        f.id = Math.random();
        f.ativo_codigo = codigo;
        (f as any).tipo_evento = f.tipo.nome;
      });
      novosAtivos.push(novoAtivo);
    }
    onClose(novosAtivos);
  };

  return (
    <AlertDialog
      isOpen={isOpen}
      onClose={cancel}
      leastDestructiveRef={dupCancelRef}
    >
      <AlertDialogOverlay>
        <AlertDialogContent overflow="hidden" minW="512px">
          <AlertDialogHeader bgColor="azul_1.600" color="white">
            {ativo ? (
              <Text>
                Duplicar ativo{" "}
                <Text
                  p="2px 4px"
                  borderRadius="4px"
                  as="span"
                  color={strCSSColor(ativo.codigo)}
                >
                  {ativo.codigo}
                </Text>
              </Text>
            ) : (
              <Text>Inserir ativos</Text>
            )}
          </AlertDialogHeader>
          <form onSubmit={(ev) => ev.preventDefault()}>
            <AlertDialogBody>
              <Text mb="16px">Quais os códigos dos ativos?</Text>
              <TagInput
                onTagsChanged={setCodigos}
                onValueChanged={setValue}
                forbidden={
                  ativo ? [...ativosExistentes, ativo.codigo] : ativosExistentes
                }
                forbiddenMsg="Os ativos abaixo já existem e serão desconsiderados:"
              />
            </AlertDialogBody>
            <AlertDialogFooter gap={2}>
              <Button size="sm" ref={dupCancelRef} onClick={cancel}>
                Cancelar
              </Button>
              <Button
                size="sm"
                type="submit"
                isDisabled={codigos.length === 0 || !!value}
                colorScheme="azul_1"
                onClick={insertAtivos}
              >
                Salvar
              </Button>
            </AlertDialogFooter>
          </form>
        </AlertDialogContent>
      </AlertDialogOverlay>
    </AlertDialog>
  );
}
