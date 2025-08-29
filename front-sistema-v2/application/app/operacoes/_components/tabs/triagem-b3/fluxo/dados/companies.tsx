import B3Icon from "@/public/b3.png";
import BradescoIcon from "@/public/bradesco.png";
import ItauIcon from "@/public/itau.png";
import IVIcon from "@/public/SimboloIcatuVanguarda_Azul.png";
import MellonIcon from "@/public/mellon.png";
import SantanderIcon from "@/public/santander.png";
import DaycovalIcon from "@/public/daycoval.png";
import IcatuSegurosIcon from "@/public/icatu_seguros.png";
import RioGrandeSegurosIcon from "@/public/rio_grande.png";
import IntragIcon from "@/public/intrag.webp";
import BTGIcon from "@/public/btg.png";
import { Company } from "./tipos";
import {
  Box,
  HStack,
  Icon,
  StackProps,
  Text,
  TextProps,
} from "@chakra-ui/react";
import {
  IoBusinessOutline,
  IoHelpOutline,
  IoPeopleOutline,
} from "react-icons/io5";
import Image from "next/image";

export const companies: Record<string, Company> = {
  b3: {
    name: "B3",
    icon: B3Icon,
    detail: (
      <>
        <Box flex={1} bgColor="#001b74" />
        <Box flex={1} bgColor="white" />
        <Box flex={1} bgColor="#001b74" />
      </>
    ),
  },
  bradesco: {
    name: "Bradesco",
    icon: BradescoIcon,
    detail: (
      <>
        <Box bgColor="white" flex={2} />
        <Box bgColor="red" flex={1} />
        <Box bgColor="white" flex={1} />
        <Box bgColor="red" flex={1} />
        <Box bgColor="white" flex={5} />
      </>
    ),
  },
  contraparte: {
    name: "Contraparte",
    icon: IoPeopleOutline,
  },
  custodiante_contraparte: {
    name: "Custodiante Contraparte",
    icon: IoBusinessOutline,
  },
  itau: {
    name: "Itaú",
    icon: ItauIcon,
    detail: "laranja.main",
  },
  mellon: {
    name: "Mellon",
    icon: MellonIcon,
    detail: (
      <>
        <Box bgColor="#a5a5a5" flex={1} />
        <Box bgColor="#b48735" flex={3} />
        <Box bgColor="#a39772" flex={1} />
      </>
    ),
  },
  santander: {
    name: "Santander",
    icon: SantanderIcon,
    detail: (
      <>
        <Box bgColor="red" flex={5} />
        <Box bgColor="white" flex={2} />
        <Box bgColor="red" flex={1} />
        <Box bgColor="white" flex={2} />
        <Box bgColor="red" flex={1} />
        <Box bgColor="white" flex={2} />
        <Box bgColor="red" flex={5} />
      </>
    ),
  },
  daycoval: {
    name: "Daycoval",
    icon: DaycovalIcon,
    detail: (
      <>
        <Box bgColor="blue" flex={5} />
      </>
    ),
  },
  intrag: {
    name: "Intrag DTVM",
    icon: IntragIcon,
    detail: "laranja.main",
  },
  btg: {
    name: "BTG Pactual",
    icon: BTGIcon,
    detail: "blue",
  },
  icatu_seguros: {
    name: "Icatu Seguros",
    icon: IcatuSegurosIcon,
    detail: "blue",
  },
  rio_grande: {
    name: "Rio Grande Seguros",
    icon: RioGrandeSegurosIcon,
    detail: (
      <>
        <Box bgColor="blue" flex={5} />
      </>
    ),
  },
  vanguarda: {
    name: "Vanguarda",
    icon: IVIcon,
    detail: (
      <>
        <Box flex={3} bgColor="azul_1.main" />
        <Box flex={1} bgColor="azul_2.main" />
        <Box flex={1} bgColor="azul_3.main" />
        <Box flex={1} bgColor="azul_4.main" />
      </>
    ),
  },
  nao_registrado: {
    name: "Não registrado",
    icon: IoHelpOutline,
  },
};
companies["itaú"] = companies["itau"];

export const buscar = (nomeEmpresa: string) => {
  const [primeiroNome, segundoNome] = nomeEmpresa
    .toLocaleLowerCase()
    .split(" ");
  return (
    companies[primeiroNome] ??
    companies[segundoNome] ??
    companies[primeiroNome + "_" + segundoNome] ??
    companies["nao_registrado"]
  );
};

export const banner = (
  nomeEmpresa: string,
  w = 16,
  h = 16,
  {
    hstackProps,
    textProps,
  }: {
    hstackProps?: StackProps;
    textProps?: TextProps;
  },
) => {
  const empresa = buscar(nomeEmpresa);
  const icone = empresa.icon ? (
    "src" in empresa.icon ? (
      <Image width={w} height={h} src={empresa.icon} alt="Ícone" />
    ) : (
      <Icon w={w + "px"} h={h + "px"} as={empresa.icon} />
    )
  ) : (
    <Icon w={w + "px"} h={h + "px"} as={IoHelpOutline} />
  );
  return (
    <HStack {...hstackProps}>
      {icone}
      <Text {...textProps}>{empresa.name}</Text>
    </HStack>
  );
};
