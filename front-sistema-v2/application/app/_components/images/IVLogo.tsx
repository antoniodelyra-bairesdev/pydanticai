import { Image, useColorMode } from "@chakra-ui/react";

import IVPrincipalAzul from "@/public/IcatuVanguarda_Principal_Azul.png";
import IVPrincipalBranco from "@/public/IcatuVanguarda_Principal_Branco.png";
import IVPrincipalAzulMonocromatico from "@/public/IcatuVanguarda_Principal_Monocromatico_Azul.png";
import IVPrincipalBrancoMonocromatico from "@/public/IcatuVanguarda_Principal_Monocromatico_Branco.png";

import IVSecundariaAzul from "@/public/IcatuVanguarda_Secundaria_Azul.png";
import IVSecundariaBranco from "@/public/IcatuVanguarda_Secundaria_Branco.png";
import IVSecundariaAzulMonocromatico from "@/public/IcatuVanguarda_Secundaria_Monocromatico_Azul.png";
import IVSecundariaBrancoMonocromatico from "@/public/IcatuVanguarda_Secundaria_Monocromatico_Branco.png";

import IVSimboloAzul from "@/public/SimboloIcatuVanguarda_Azul.png";

export type IVLogoProps = {
  variant?: "icon" | "vertical" | "horizontal";
  monochrome?: boolean;
  forceColorMode?: "light" | "dark";
};

export default function IVLogo({
  variant = "horizontal",
  monochrome = false,
  forceColorMode,
}: IVLogoProps) {
  const { colorMode } = useColorMode();

  const choices = {
    light: {
      icon: IVSimboloAzul,
      vertical: monochrome ? IVSecundariaAzulMonocromatico : IVSecundariaAzul,
      horizontal: monochrome ? IVPrincipalAzulMonocromatico : IVPrincipalAzul,
    },
    dark: {
      icon: IVSimboloAzul,
      vertical: monochrome
        ? IVSecundariaBrancoMonocromatico
        : IVSecundariaBranco,
      horizontal: monochrome
        ? IVPrincipalBrancoMonocromatico
        : IVPrincipalBranco,
    },
  };

  return (
    <Image
      objectFit="contain"
      src={choices[forceColorMode ?? colorMode][variant].src}
    />
  );
}
