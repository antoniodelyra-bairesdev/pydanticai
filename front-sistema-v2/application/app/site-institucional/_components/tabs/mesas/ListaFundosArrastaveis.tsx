import { Fundo } from "@/lib/types/api/iv/v1";
import {
  Card,
  CardBody,
  CardHeader,
  HStack,
  Icon,
  StackProps,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useState } from "react";
import {
  IoEyeOffOutline,
  IoGlobeOutline,
  IoReorderFourOutline,
} from "react-icons/io5";

export type ControleArrasto = {
  fundo: { id: number; nome: string };
  remover: () => void;
};

export type ListaFundosArrastaveisProps = {
  fundos: { id: number; nome: string }[];
  setFundos: (fundos: { id: number; nome: string }[]) => void;
  controleArrasto: ControleArrasto | undefined;
  setControleArrasto: (controle: ControleArrasto | undefined) => void;
} & StackProps;

export default function ListaFundosArrastaveis({
  fundos,
  setFundos,
  controleArrasto,
  setControleArrasto,
  ...props
}: ListaFundosArrastaveisProps) {
  const [cursorOnTop, setCursorOnTop] = useState(false);

  return (
    <VStack
      alignItems="stretch"
      borderRadius="8px"
      onDrop={(ev) => {
        ev.preventDefault();
        console.log({ controleArrasto });
        if (!controleArrasto) return;
        const existe = fundos.find((f) => controleArrasto.fundo.id === f.id);
        if (existe) return;
        fundos.unshift(controleArrasto.fundo);
        controleArrasto.remover();
        setFundos(fundos);
      }}
      onMouseOver={() => setCursorOnTop(true)}
      onDragOver={(ev) => {
        ev.preventDefault();
        setCursorOnTop(true);
      }}
      onMouseLeave={() => setCursorOnTop(false)}
      onDragLeave={() => setCursorOnTop(false)}
      {...(controleArrasto && cursorOnTop
        ? {
            border: "1px dashed",
            borderColor: "azul_3.main",
            bgColor: "azul_3.100",
          }
        : {})}
      {...props}
    >
      {fundos.map((f) => (
        <Card
          onDragStart={() =>
            setControleArrasto({
              fundo: f,
              remover: () => {
                const index = fundos.findIndex((fp) => fp.id === f.id);
                if (index === -1) return;
                fundos.splice(index, 1);
                setFundos(fundos);
                setControleArrasto(undefined);
              },
            })
          }
          fontSize="xs"
          cursor="grab"
          draggable
          key={f.id}
        >
          <HStack flexDirection="row-reverse">
            <CardHeader userSelect="none" flex={1} p="8px 12px 8px 0px">
              <Text>{f.nome}</Text>
            </CardHeader>
            <CardBody flex={0} p="8px 12px">
              <Icon as={IoReorderFourOutline} />
            </CardBody>
          </HStack>
        </Card>
      ))}
    </VStack>
  );
}
