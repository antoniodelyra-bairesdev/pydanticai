import { Fundo } from "@/lib/types/api/iv/v1";
import { Checkbox, HStack, Text } from "@chakra-ui/react";

export type ItemFundoSiteInstitucionalProps = {
  marcado: boolean;
  fundo: Fundo;
  onFundoMarcado: (fundo: Fundo) => void;
  onFundoDesmarcado: (fundo: Fundo) => void;
};

export default function ItemFundoLista({
  marcado,
  fundo,
  onFundoMarcado,
  onFundoDesmarcado,
}: ItemFundoSiteInstitucionalProps) {
  return (
    <HStack>
      <Checkbox
        colorScheme="verde"
        size="sm"
        onChange={(ev) =>
          (ev.target.checked ? onFundoMarcado : onFundoDesmarcado)(fundo)
        }
        isChecked={marcado}
      />
      <Text flex={1} fontSize="sm">
        {fundo.nome}
      </Text>
    </HStack>
  );
}
