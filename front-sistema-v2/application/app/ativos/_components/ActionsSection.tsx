"use client";

import { ValidationGridColDef } from "@/app/_components/grid/ValidationGrid";
import DiffModal from "@/app/_components/modal/DiffModal";
import { useHTTP } from "@/lib/hooks";
import { AssetPageContext } from "@/lib/providers/AssetPageProvider";
import {
  Ativo,
  Emissor,
  Evento,
  IndicePapel,
  InsertedAtivoSchema,
  ModifiedAtivoSchema,
  TipoEvento,
  TipoPapel,
} from "@/lib/types/api/iv/v1";
import { deeplyModifiedAssets, parseIndiceFromCell } from "@/lib/util/misc";
import { ArrowRightIcon, EditIcon, SmallCloseIcon } from "@chakra-ui/icons";
import { Button, Tooltip, useDisclosure } from "@chakra-ui/react";
import { useContext, useMemo } from "react";
import TopBarSection from "./TopBarSection";

export type ActionsSectionProps = {
  assetColDefs: ValidationGridColDef[];
  eventColDefs: ValidationGridColDef[];
  editing: boolean;
  tipos_ativos: TipoPapel[];
  tipos_fluxos: TipoEvento[];
  emissores: Emissor[];
  indices: IndicePapel[];
  onEditToggle: (newValue: boolean) => void;
};

export default function ActionsSection({
  tipos_ativos,
  tipos_fluxos,
  emissores,
  indices,
  assetColDefs,
  eventColDefs,
  editing,
  onEditToggle,
}: ActionsSectionProps) {
  const { icon, color, text } = editing
    ? {
        icon: <SmallCloseIcon />,
        color: "rosa",
        text: "Desabilitar modo de edição",
      }
    : { icon: <EditIcon />, color: "azul_1", text: "Habilitar modo de edição" };

  const {
    clientSideAssetsCellErrors: aErrors,
    clientSideEventsCellErrors: eErrors,
    clientSideNoDueDateErrors: ddErrors,
    clientSideDueDateIsNotLastDateErrors: ddnldErrors,

    loadedAssetsRef,
    loadedEventsRef,

    addedAssets,
    modifiedAssets,
    deletedAssets,
    addedEvents,
    modifiedEvents,
    deletedEvents,
  } = useContext(AssetPageContext);
  const hasErrors = Boolean(
    aErrors + eErrors + Object.keys(ddErrors).length + ddnldErrors.length,
  );

  const { isOpen, onOpen, onClose } = useDisclosure();

  const deeplyModified = useMemo(
    () =>
      deeplyModifiedAssets(
        loadedAssetsRef.current,
        loadedEventsRef.current,
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

  const httpClient = useHTTP({ withCredentials: true });

  return (
    <TopBarSection title="Ações" minW="180px">
      <Button
        onClick={() => onEditToggle(!editing)}
        colorScheme={color}
        leftIcon={icon}
        size="xs"
      >
        {text}
      </Button>
      {editing && (
        <Tooltip
          color="white"
          p="8px"
          borderRadius="8px"
          bgColor="azul_1.700"
          fontSize="xs"
          hasArrow
          isDisabled={!hasErrors}
          label="Corrija os erros da tabela antes de revisar as alterações."
        >
          <Button
            isDisabled={hasErrors}
            leftIcon={<ArrowRightIcon />}
            onClick={() => {
              onOpen();
            }}
            colorScheme="azul_1"
            key="salvar"
            size="xs"
          >
            Revisar alterações
          </Button>
        </Tooltip>
      )}
      <DiffModal<Ativo>
        identifier="codigo"
        colDefs={assetColDefs}
        isOpen={isOpen}
        onClose={onClose}
        added={addedAssets}
        modified={deeplyModified}
        deleted={deletedAssets}
        nested={{
          fluxos: {
            label: "Eventos",
            relationship(owner, nested) {
              return owner.codigo === nested.ativo_codigo;
            },
            identifier: "id",
            colDefs: eventColDefs,
            added: addedEvents,
            modified: modifiedEvents,
            deleted: deletedEvents,
          },
        }}
        submitAction={async () => {
          const assetWithIds = (a: Ativo) => ({
            ...a,
            serie: a.serie ? a.serie : null,
            emissao: a.emissao ? a.emissao : null,
            tipo_id: Number(
              tipos_ativos.find((ta) => ta.nome === (a.tipo as any))?.id,
            ),
            indice_id: Number(
              indices.find(
                (i) => i.nome === (a.indice as any).split("|")[0].trim(),
              )?.id,
            ),
            emissor_id: Number(
              emissores.find((e) => e.nome === (a.emissor as any))?.id ?? 0,
            ),
            ativo_ipca:
              parseIndiceFromCell(a.indice as any)?.ativo_ipca ?? undefined,
          });
          const eventsWithIds = (e: Evento) => ({
            ...e,
            percentual: e.percentual ? e.percentual : null,
            pu_evento: e.pu_evento ? e.pu_evento : null,
            pu_calculado: e.pu_calculado ? e.pu_calculado : null,
            tipo_id: Number(
              tipos_fluxos.find((tf) => tf.nome === (e as any).tipo_evento)?.id,
            ),
          });

          const deleted: string[] = deletedAssets.map((a) => a.codigo);
          const modified: ModifiedAtivoSchema[] = Object.entries(
            deeplyModified,
          ).map(([codigo, diff]) => ({
            ...assetWithIds(diff.data.new!),
            fluxos: {
              deleted: deletedEvents
                .filter((e) => e.ativo_codigo === codigo)
                .map((e) => e.id),
              modified: Object.values(modifiedEvents).map((value) =>
                eventsWithIds({ ...value.data.new! }),
              ),
              added: addedEvents
                .filter((e) => e.ativo_codigo === codigo)
                .map((e) => eventsWithIds(e)),
            },
          }));
          const added: InsertedAtivoSchema[] = addedAssets.map((a) => ({
            ...assetWithIds(a),
            fluxos: a.fluxos.map((e) => eventsWithIds(e)),
          }));
          console.debug({ deleted, modified, added });

          const result = await httpClient.fetch("/v1/ativos/transacao", {
            method: "PUT",
            body: JSON.stringify({ deleted, modified, added }),
          });

          if (!result.ok) {
            return {
              error: await result.json(),
            };
          }
        }}
        onCloseAfterSuccess={() => {
          onEditToggle(false);
        }}
      />
    </TopBarSection>
  );
}
