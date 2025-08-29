"use client";

import VResize from "@/app/_components/misc/VResize";
import EmissoresGrid from "./EmissoresGrid";
import SetoresGrid from "./SetoresGrid";
import GruposGrid from "./GruposGrid";
import {
  AnalistaCredito,
  EmissorGrupo,
  EmissorSetor,
} from "@/lib/types/api/iv/v1";
import { useEmissoresPageData } from "../provider";
import { useEffect } from "react";
import { Box, HStack } from "@chakra-ui/react";

export type EmissoresProps = {
  analistas: Record<string, AnalistaCredito>;
  grupos: Record<string, EmissorGrupo>;
  setores: Record<string, EmissorSetor>;
};

export default function Emissores({
  analistas,
  grupos,
  setores,
}: EmissoresProps) {
  const { setAnalistas, setGrupos, setSetores } = useEmissoresPageData();

  useEffect(() => {
    setAnalistas(analistas);
    setGrupos(grupos);
    setSetores(setores);
  }, []);

  return (
    <HStack w="100%" h="100%" p="12px">
      <Box minW="420px" flex={1} h="100%">
        <EmissoresGrid />
      </Box>
      <VResize
        topElement={<SetoresGrid />}
        bottomElement={<GruposGrid />}
        minW="420px"
        w="25%"
        h="100%"
        startingProportion={0.45}
      />
    </HStack>
  );
}
