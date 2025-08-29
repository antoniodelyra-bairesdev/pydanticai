import {
  ModificationMap,
  ValidationGridColDef,
} from "@/app/_components/grid/ValidationGrid";
import { getColorHex } from "@/app/theme";
import { SingularPluralMapping, pluralOrSingular } from "@/lib/util/string";
import { AddIcon, DeleteIcon, EditIcon } from "@chakra-ui/icons";
import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Button,
  Card,
  CardBody,
  Divider,
  HStack,
  Heading,
  StackDivider,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  VStack,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import DiffRow from "./DiffRow";

export type NestedDiffArrayProperties<T> = {
  [K in keyof T as T[K] extends any[] ? K : never]: DiffSummaryProps<
    T[K] extends any[] ? T[K][number] : never
  > & {
    label?: string;
    relationship: (
      owner: T,
      nested: T[K] extends any[] ? T[K][number] : never,
    ) => boolean;
  };
};

export type DiffSummaryProps<T> = {
  identifier: keyof T;
  colDefs: ValidationGridColDef[];
  added: T[];
  modified: ModificationMap<T>;
  deleted: T[];
  nested?: Partial<NestedDiffArrayProperties<T>>;
  showAdded?: boolean;
  showDeleted?: boolean;
  showModified?: boolean;
  idFormatter?: (identifier: string, data: T) => string;
};

export default function DiffSummary<T>({
  added,
  colDefs,
  deleted,
  identifier,
  modified,
  nested,
  idFormatter = (id) => String(id),
  showAdded = true,
  showDeleted = true,
  showModified = true,
}: DiffSummaryProps<T>) {
  const [selected, setSelected] = useState<{
    id: string;
    diff: ModificationMap<T>[string];
  } | null>(null);

  useEffect(() => {
    setSelected(null);
  }, [added, deleted, modified]);

  const originalData = selected?.diff.data.original;
  const newData = selected?.diff.data.new;

  const btn = (
    { id, diff }: { id: string; diff: ModificationMap<T>[string] },
    icon: React.ReactElement,
  ) => {
    const selectedId = selected?.id;
    const { original, new: novo } = diff.data;
    const fonte = original ?? novo;
    return (
      <Button
        onClick={() => setSelected(selectedId === id ? null : { id, diff })}
        colorScheme={selectedId === id ? "verde" : "gray"}
        justifyContent="flex-start"
        w="100%"
        size="xs"
        key={String(id)}
        leftIcon={icon}
      >
        <Text
          as="span"
          w="100%"
          overflow="hidden"
          whiteSpace="nowrap"
          textOverflow="ellipsis"
        >
          {fonte ? idFormatter(id, fonte) : id}
        </Text>
      </Button>
    );
  };

  const nestedEntries: {
    field: string;
    diff: NestedDiffArrayProperties<T>[keyof NestedDiffArrayProperties<T>];
  }[] = [];

  if (nested) {
    for (const field in nested) {
      const diff = nested[field];
      if (diff) {
        nestedEntries.push({
          field: field as string,
          diff,
        });
      }
    }
  }

  const s: SingularPluralMapping = {
    $: { plural: "s", singular: "" },
  };

  return (
    <HStack gap={0} h="100%" align="stretch" minW="240px">
      <Accordion
        p="8px"
        alignItems="center"
        overflowY="auto"
        borderColor="transparent"
        maxW="240px"
        defaultIndex={[0, 1, 2]}
        allowMultiple={true}
      >
        {[
          ...(showDeleted
            ? [
                [
                  Object.entries(
                    deleted.reduce(
                      (acc, data) => ({
                        ...acc,
                        [String(data[identifier])]: {
                          data: {
                            original: data,
                            new: null,
                          },
                          fields: {},
                        },
                      }),
                      {} as ModificationMap<T>,
                    ),
                  ),
                  "Removido",
                  <DeleteIcon mr="4px" />,
                ] as const,
              ]
            : []),
          ...(showModified
            ? [
                [
                  Object.entries(modified),
                  "Editado",
                  <EditIcon mr="4px" />,
                ] as const,
              ]
            : []),
          ...(showAdded
            ? [
                [
                  Object.entries(
                    added.reduce(
                      (acc, data) => ({
                        ...acc,
                        [String(data[identifier])]: {
                          data: {
                            original: null,
                            new: data,
                          },
                          fields: {},
                        },
                      }),
                      {} as ModificationMap<T>,
                    ),
                  ),
                  "Adicionado",
                  <AddIcon mr="4px" />,
                ] as const,
              ]
            : []),
        ].map(([entries, title, icon], i) => (
          <AccordionItem isDisabled={entries.length === 0} key={i}>
            {({ isExpanded }) => (
              <>
                <AccordionButton p={0}>
                  <Button
                    as="div"
                    colorScheme="azul_1"
                    borderBottomLeftRadius={isExpanded ? 0 : "0.375rem"}
                    borderBottomRightRadius={isExpanded ? 0 : "0.375rem"}
                    w="100%"
                    p="8px"
                  >
                    <Text fontSize="xs" flex="1" textAlign="left">
                      ({entries.length}) {title}
                    </Text>
                    <AccordionIcon />
                  </Button>
                </AccordionButton>
                <AccordionPanel p={0}>
                  <Card
                    borderTopLeftRadius={0}
                    borderTopRightRadius={0}
                    variant="outline"
                  >
                    <CardBody
                      p="4px"
                      display="flex"
                      flexDirection="column"
                      gap="4px"
                    >
                      {entries.map(([id, diff]) => btn({ id, diff }, icon))}
                    </CardBody>
                  </Card>
                </AccordionPanel>
              </>
            )}
          </AccordionItem>
        ))}
      </Accordion>
      <StackDivider borderLeft={`1px solid ${getColorHex("cinza.main")}`} />
      <VStack
        overflowX="auto"
        gap={0}
        p={0}
        flex={4}
        justify={selected ? "stretch" : "center"}
        align={selected ? "stretch" : "center"}
      >
        {selected ? (
          <>
            <Heading size="sm" pt="8px" pb="8px" pl="16px">
              {selected.diff.data.original
                ? idFormatter(selected.id, selected.diff.data.original)
                : selected.diff.data.new
                  ? idFormatter(selected.id, selected.diff.data.new)
                  : selected.id}
            </Heading>
            <Divider />
            <TableContainer w="100%" overflowY="auto">
              <Table w="100%" display="block" style={{ tableLayout: "fixed" }}>
                <Thead>
                  <Tr w="100%">
                    <Th></Th>
                    <Th width="50%" textAlign="center">
                      Anterior
                    </Th>
                    <Th width="50%" textAlign="center">
                      Atual
                    </Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {colDefs.map((colDef, index) => (
                    <DiffRow
                      key={index}
                      index={index}
                      colDef={colDef}
                      originalData={originalData}
                      newData={newData}
                      colRowsCount={colDefs.filter((cd) => !cd.colDefs).length}
                    />
                  ))}
                  {nestedEntries.map(({ field, diff }) => {
                    const nestedAdded = diff.added.filter((nestedData) => {
                      const data = originalData ?? newData;
                      if (!data) return false;
                      return diff.relationship(data, nestedData);
                    });
                    const nestedModified = Object.entries(diff.modified)
                      .filter(([_, modMap]) => {
                        const nestedData =
                          modMap.data.original ?? modMap.data.new;
                        const data = originalData ?? newData;
                        if (!nestedData || !data) return false;
                        return diff.relationship(data, nestedData);
                      })
                      .reduce(
                        (acc, [entry, diff]) => ({ ...acc, [entry]: diff }),
                        {},
                      );
                    const nestedDeleted = diff.deleted.filter((nestedData) => {
                      const data = originalData ?? newData;
                      if (!data) return false;
                      return diff.relationship(data, nestedData);
                    });
                    return (
                      <Tr fontSize="xs">
                        <Td
                          p="8px"
                          textAlign="right"
                          fontWeight="bold"
                          borderRight={`1px solid ${getColorHex("cinza.main")}`}
                        >
                          {diff.label ?? field}
                        </Td>
                        <Td colSpan={2} p={0}>
                          <Accordion allowMultiple={true}>
                            <AccordionItem>
                              {({ isExpanded }) => (
                                <>
                                  <AccordionButton color="white" p={0}>
                                    <Button
                                      colorScheme="azul_1"
                                      as="div"
                                      w="100%"
                                    >
                                      <Text
                                        fontSize="xs"
                                        textAlign="left"
                                        flex={1}
                                      >
                                        {nestedDeleted.length > 0 && (
                                          <Text
                                            m="4px"
                                            p="4px"
                                            borderRadius="4px"
                                            bgColor="whiteAlpha.100"
                                            color="laranja.main"
                                            as="span"
                                          >
                                            {pluralOrSingular(
                                              `${nestedDeleted.length} removido$`,
                                              s,
                                              nestedAdded.length,
                                            )}
                                          </Text>
                                        )}
                                        {Object.keys(nestedModified).length >
                                          0 && (
                                          <Text
                                            m="4px"
                                            p="4px"
                                            borderRadius="4px"
                                            bgColor="whiteAlpha.100"
                                            color="amarelo.main"
                                            as="span"
                                          >
                                            {pluralOrSingular(
                                              `${Object.keys(nestedModified).length} modificado$`,
                                              s,
                                              Object.keys(nestedModified)
                                                .length,
                                            )}
                                          </Text>
                                        )}
                                        {nestedAdded.length > 0 && (
                                          <Text
                                            m="4px"
                                            p="4px"
                                            borderRadius="4px"
                                            bgColor="whiteAlpha.100"
                                            color="verde.main"
                                            as="span"
                                          >
                                            {pluralOrSingular(
                                              `${nestedAdded.length} adicionado$`,
                                              s,
                                              nestedDeleted.length,
                                            )}
                                          </Text>
                                        )}
                                      </Text>
                                      <AccordionIcon />
                                    </Button>
                                  </AccordionButton>
                                  <AccordionPanel
                                    maxH="640px"
                                    overflow="auto"
                                    p="4px"
                                    display="flex"
                                    flexDirection="column"
                                    gap="4px"
                                  >
                                    <DiffSummary
                                      identifier={diff.identifier}
                                      colDefs={diff.colDefs}
                                      added={nestedAdded}
                                      modified={nestedModified}
                                      deleted={nestedDeleted}
                                      nested={diff.nested}
                                    />
                                  </AccordionPanel>
                                </>
                              )}
                            </AccordionItem>
                          </Accordion>
                        </Td>
                      </Tr>
                    );
                  })}
                </Tbody>
              </Table>
            </TableContainer>
          </>
        ) : (
          <Text fontSize="sm" fontWeight="normal" color="cinza.400">
            Selecione algum item para visualizá-lo
          </Text>
        )}
      </VStack>
    </HStack>
  );
}
