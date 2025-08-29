"use client";

import { useColors } from "@/lib/hooks";
import { AssetPageContext } from "@/lib/providers/AssetPageProvider";
import { deeplyModifiedAssetCodes } from "@/lib/util/misc";
import {
  SingularPluralMapping,
  pluralOrSingular,
  strCSSColor,
} from "@/lib/util/string";
import { AddIcon, DeleteIcon, EditIcon } from "@chakra-ui/icons";
import { Text } from "@chakra-ui/react";
import { useContext, useMemo } from "react";
import TopBarItem from "./TopBarItem";
import TopBarSection from "./TopBarSection";

export type SummarySectionProps = {
  deleted: string[];
  modified: string[];
  added: string[];
};

const s: SingularPluralMapping = {
  $: { singular: "", plural: "s" },
};

export default function SummarySection() {
  const { bgText, hover } = useColors();

  const {
    addedAssets,
    modifiedAssets,
    deletedAssets,
    addedEvents,
    modifiedEvents,
    deletedEvents,

    clientSideEvents,
  } = useContext(AssetPageContext);

  const deeplyModified = useMemo(
    () =>
      deeplyModifiedAssetCodes(
        addedAssets,
        modifiedAssets,
        deletedAssets,
        addedEvents,
        modifiedEvents,
        deletedEvents,
      ),
    [
      addedAssets,
      modifiedAssets,
      deletedAssets,
      addedEvents,
      modifiedEvents,
      deletedEvents,
    ],
  );

  const getColoredItems = (data: string[]) =>
    data.sort().map((code) => (
      <Text
        as="span"
        m="4px"
        p="4px"
        borderRadius="4px"
        fontSize="xs"
        bgColor={hover}
        color={strCSSColor(code)}
      >
        {code}{" "}
      </Text>
    ));

  return (
    <TopBarSection title="Alterações" flexGrow={1.5} minW="200px">
      {[...deletedAssets, ...deeplyModified, ...addedAssets].length ? (
        <>
          {!deletedAssets.length || (
            <TopBarItem
              menu={getColoredItems(deletedAssets.map((a) => a.codigo))}
              icon={<DeleteIcon color="rosa.main" />}
              txt={`${deletedAssets.length} ${pluralOrSingular("ativo$ removido$", s, deletedAssets.length)}`}
              alignSelf="stretch"
            />
          )}
          {!deeplyModified.length || (
            <TopBarItem
              menu={getColoredItems(deeplyModified)}
              icon={<EditIcon color="amarelo.main" />}
              txt={`${deeplyModified.length} ${pluralOrSingular("ativo$ modificado$", s, deeplyModified.length)}`}
              alignSelf="stretch"
            />
          )}
          {!addedAssets.length || (
            <TopBarItem
              menu={getColoredItems(addedAssets.map((a) => a.codigo))}
              icon={<AddIcon color="verde.main" />}
              txt={`${addedAssets.length} ${pluralOrSingular("ativo$ adicionado$", s, addedAssets.length)}`}
              alignSelf="stretch"
            />
          )}
        </>
      ) : (
        <Text w="100%" textAlign="center" fontSize="xs" color={bgText}>
          Não há alterações
        </Text>
      )}
    </TopBarSection>
  );
}
