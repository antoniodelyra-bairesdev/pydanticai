"use client";

import { getColorHex } from "@/app/theme";
import { useColors } from "@/lib/hooks";
import { AssetPageContext } from "@/lib/providers/AssetPageProvider";
import {
  SingularPluralMapping,
  pluralOrSingular,
  strCSSColor,
} from "@/lib/util/string";
import { CalendarIcon, WarningIcon } from "@chakra-ui/icons";
import { HStack, StackDivider, Text, VStack } from "@chakra-ui/react";
import { useContext } from "react";
import TopBarItem from "./TopBarItem";
import TopBarSection from "./TopBarSection";

const s: SingularPluralMapping = {
  "&": { singular: "i", plural: "em" },
  "#": { singular: "", plural: "m" },
  $: { singular: "", plural: "s" },
};

export default function ErrorSection() {
  const { bgText, hover } = useColors();
  const {
    clientSideAssetsCellErrors: aCells,
    clientSideEventsCellErrors: eCells,
    clientSideNoDueDateErrors: ddErrors,
    clientSideDueDateIsNotLastDateErrors: ddnldErrors,
  } = useContext(AssetPageContext);
  const noErrors = (
    <Text w="100%" textAlign="center" fontSize="xs" color={bgText}>
      Não há erros
    </Text>
  );

  const getColoredRecords = (data: Record<string, number>) =>
    Object.entries(data)
      .sort()
      .map(([code, count]) => (
        <HStack
          gap={0}
          p={0}
          mb="4px"
          border={`1px solid ${getColorHex(hover)}`}
          alignItems="stretch"
        >
          <Text
            bgColor={hover}
            pl="4px"
            pr="4px"
            fontSize="xs"
            color={strCSSColor(code)}
          >
            {code}
          </Text>
          <Text pl="4px" pr="4px" fontSize="xs">
            <Text as="span" fontWeight="600">
              {count}{" "}
            </Text>
            {pluralOrSingular(`vencimento$`, s, count)}
          </Text>
        </HStack>
      ));

  const getColoredItems = (data: string[]) =>
    data.sort().map((code) => (
      <Text
        as="span"
        m="4px"
        p="4px"
        borderRadius="4px"
        fontSize="xs"
        bgColor={hover}
        color={strCSSColor(code ?? "")}
      >
        {code}{" "}
      </Text>
    ));

  return (
    <TopBarSection title="Erros" flexGrow={3} minW="360px">
      <HStack alignItems="flex-start" divider={<StackDivider />}>
        <VStack alignItems="flex-start" w="50%">
          <Text fontSize="xs">Ativos:</Text>
          {aCells ? (
            <TopBarItem
              color="rosa.main"
              icon={<WarningIcon color="rosa.main" />}
              txt={pluralOrSingular(
                `${aCells} célula$ com erro$ de validação`,
                s,
                aCells,
              )}
            />
          ) : (
            noErrors
          )}
        </VStack>
        <VStack alignItems="flex-start" w="50%">
          <Text fontSize="xs">Eventos:</Text>
          {Boolean(
            eCells + Object.keys(ddErrors).length + ddnldErrors.length,
          ) ? (
            <>
              {!!eCells && (
                <TopBarItem
                  color="rosa.main"
                  icon={<WarningIcon color="rosa.main" />}
                  txt={pluralOrSingular(
                    `${eCells} célula$ com erro$ de validação`,
                    s,
                    eCells,
                  )}
                />
              )}
              {!!Object.keys(ddErrors).length && (
                <TopBarItem
                  color="rosa.main"
                  icon={<CalendarIcon color="rosa.main" />}
                  txt={pluralOrSingular(
                    `${Object.keys(ddErrors).length} ativo$ não possu& exatamente um evento de vencimento`,
                    s,
                    Object.keys(ddErrors).length,
                  )}
                  menu={getColoredRecords(ddErrors)}
                />
              )}
              {!!ddnldErrors.length && (
                <TopBarItem
                  color="rosa.main"
                  icon={<CalendarIcon color="rosa.main" />}
                  txt={pluralOrSingular(
                    `O último evento de ${ddnldErrors.length} ativo$ não é um vencimento`,
                    s,
                    ddnldErrors.length,
                  )}
                  menu={getColoredItems(ddnldErrors)}
                />
              )}
            </>
          ) : (
            noErrors
          )}
        </VStack>
      </HStack>
    </TopBarSection>
  );
}
