"use client";

import { AddIcon, CalendarIcon, CopyIcon } from "@chakra-ui/icons";
import { Button, LightMode } from "@chakra-ui/react";
import TopBarSection from "./TopBarSection";

export type InsertSectionProps = {
  onAddAtivosClicked: () => void;
  onAddFluxosClicked: () => void;
};

export default function InsertSection({
  onAddAtivosClicked,
  onAddFluxosClicked,
}: InsertSectionProps) {
  return (
    <TopBarSection title="Inserir" minW="180px">
      <LightMode>
        <Button
          onClick={onAddAtivosClicked}
          size="xs"
          leftIcon={
            <>
              <AddIcon mr="4px" /> <CopyIcon />
            </>
          }
          key="addAtivos"
          colorScheme="verde"
        >
          {" "}
          Inserir ativos{" "}
        </Button>
        <Button
          onClick={onAddFluxosClicked}
          size="xs"
          leftIcon={
            <>
              <AddIcon mr="4px" /> <CalendarIcon />
            </>
          }
          key="addFluxos"
          colorScheme="verde"
        >
          {" "}
          Inserir fluxos{" "}
        </Button>
      </LightMode>
    </TopBarSection>
  );
}
