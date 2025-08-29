import { ModificationMap } from "@/app/_components/grid/ValidationGrid";
import { Ativo, Evento } from "../types/api/iv/v1";

export const wait = (ms: number) => new Promise((ok) => setTimeout(ok, ms));

export const runningEnv = () =>
  typeof window === "undefined" ? "server" : "client";

export const deeplyModifiedAssetCodes = (
  addedAssets: Ativo[],
  modifiedAssets: ModificationMap<Ativo>,
  deletedAssets: Ativo[],
  addedEvents: Evento[],
  modifiedEvents: ModificationMap<Evento>,
  deletedEvents: Evento[],
) => {
  const codigosAtivosModificados = Object.keys(modifiedAssets);

  const codigosAtivosComEventosAdicionados = addedEvents
    .map((e) => e.ativo_codigo)
    .filter((codigo) => codigo);
  const codigosAtivosComEventosModificados = Object.entries(modifiedEvents)
    .map((entry) => {
      const evento = entry[1];
      const valorOriginalEvento = evento.data.original;
      return valorOriginalEvento?.ativo_codigo;
    })
    .filter((codigo) => codigo) as string[];
  const codigosAtivosComEventosDeletados = deletedEvents.map(
    (e) => e.ativo_codigo,
  );

  const codigosAtivosProfundamenteModificados = [
    ...codigosAtivosModificados,
    ...codigosAtivosComEventosAdicionados,
    ...codigosAtivosComEventosModificados,
    ...codigosAtivosComEventosDeletados,
  ];

  const codigosUnicosAtivosProfundamenteModificados = [
    ...new Set(codigosAtivosProfundamenteModificados),
  ];

  return codigosUnicosAtivosProfundamenteModificados.filter(
    (codigo) =>
      !addedAssets.find((a) => a.codigo === codigo) &&
      !deletedAssets.find((a) => a.codigo === codigo),
  );
};

export const deeplyModifiedAssets = (
  allAssets: Record<string, Ativo>,
  allEvents: Record<string, Evento>,
  addedAssets: Ativo[],
  modifiedAssets: ModificationMap<Ativo>,
  deletedAssets: Ativo[],
  addedEvents: Evento[],
  modifiedEvents: ModificationMap<Evento>,
  deletedEvents: Evento[],
): ModificationMap<Ativo> => {
  const deeplyModified: ModificationMap<Ativo> = { ...modifiedAssets };

  const applyDeepChanges = (
    ativo?: Ativo,
    evento?: Evento,
    remove: boolean = false,
  ) => {
    if (!ativo || !evento) return;
    if (!(ativo.codigo in deeplyModified)) {
      deeplyModified[ativo.codigo] = {
        data: {
          original: structuredClone(ativo),
          new: ativo,
        },
        fields: {},
      };
    }
    const eventIndex = ativo.fluxos.findIndex((e) => e.id === evento.id);
    if (!eventIndex) {
      ativo.fluxos.push(evento);
      return;
    }

    ativo.fluxos.splice(eventIndex, 1, ...(remove ? [] : [evento]));
  };

  addedEvents.forEach((evento) =>
    applyDeepChanges(allAssets[evento.ativo_codigo], evento),
  );
  Object.entries(modifiedEvents).forEach(([_, diff]) =>
    applyDeepChanges(
      allAssets[diff.data.new?.ativo_codigo ?? ""],
      diff.data.new ?? undefined,
    ),
  );
  deletedEvents.forEach((evento) =>
    applyDeepChanges(allAssets[evento.ativo_codigo], evento, true),
  );

  Object.keys(deeplyModified).forEach((codigo) => {
    if (
      addedAssets.find((a) => a.codigo === codigo) ||
      deletedAssets.find((a) => a.codigo === codigo)
    ) {
      delete deeplyModified[codigo];
    }
  });

  return deeplyModified;
};

export const printLogo = () => {
  console.log(
    "%c▮▮▮%c▮%c▮%c▮%c▮%c▮▮%c▮%c▮%c▮%c▮%c▮▮▮\n▮▮%c▮%c▮%c▮▮▮▮▮▮▮▮%c▮%c▮%c▮▮\n▮%c▮%c▮%c▮▮▮▮▮▮▮▮▮▮▮%c▮%c▮\n%c▮%c▮▮%c▮%c▮%c▮▮%c▮%c▮▮%c▮%c▮%c▮%c▮▮%c▮\n%c▮%c▮▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮▮%c▮\n%c▮%c▮▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮▮▮%c▮\n%c▮%c▮▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮▮▮%c▮\n%c▮%c▮▮%c▮%c▮%c▮%c▮%c▮%c▮▮%c▮%c▮▮▮▮%c▮\n%c▮%c▮%c▮▮%c▮▮%c▮▮▮%c▮%c▮▮▮▮%c▮%c▮\n%c▮%c▮%c▮%c▮▮▮▮▮▮▮▮▮▮%c▮%c▮%c▮\n▮▮%c▮%c▮%c▮%c▮▮▮▮▮▮%c▮%c▮%c▮%c▮▮\n▮▮▮▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮%c▮▮▮▮\n" +
      "%c               \nICAṪU|VANGUARDA",
    ..."000000,151515,5f5f5f,adadad,dcdcdc,f3f3f3,dbdbdb,adadad,656565,131313,000000,5d5d5d,e0e0e0,fefefe,e5e5e5,636363,010101,808080,fafafa,feffff,828282,010101,414141,fcfcfc,e8eaee,acb3c1,c3c9d2,b0b7c3,fafbfb,f1f3f5,a9b1bf,e9ebef,fefefe,4c4c4c,bdbdbd,ffffff,c0c5d0,162a50,53627e,9ca5b5,13274e,b6bcc8,fcfdfd,aab2bf,2d3f61,f6f7f8,fefefe,c7c7c7,eaeaea,ffffff,c0c6d0,172c52,52617e,f0f2f4,2a3c5f,52617e,fdfdfe,475775,9fa8b7,fdfefe,f5f5f5,e3e3e3,ffffff,c0c6d0,172c52,53627e,fdfefe,838ea2,182c52,b1b8c5,2d3e61,f4f5f7,fefefe,ebebeb,9e9e9e,ffffff,c2c7d1,1d3156,576681,fcfcfc,e5e7eb,23365a,9aa3b3,fdfdfe,a3a3a3,1f1f1f,ededed,ffffff,fafafb,ffffff,fafafb,fefefe,eaeaea,282828,000000,393939,e4e4e4,ffffff,eaeaea,3f3f3f,000000,1c1c1c,969696,efefef,ffffff,eeeeee,9c9c9c,222222,000000,252525,848484,cccccc,f5f5f5,f0f0f0,d9d9d9,858585,2f2f2f,000000"
      .split(",")
      .map((_) => "background-color: #" + _ + "; color: #" + _),
    "font-size: 22px; font-weight: bold; background-color: black; color: #5ebb47",
  );
};

export type AtivoIPCAData = {
  mesversario: number;
  ipca_2_meses: boolean;
  ipca_negativo: boolean;
};

export type IndiceData = {
  nome: string;
  ativo_ipca: AtivoIPCAData | null;
};

export const parseIndiceFromCell = (
  input: string | null,
): IndiceData | null => {
  if (!input) {
    return null;
  }
  const [nome, ...detalhes] = input.split("|");
  const data: IndiceData = { nome: nome.trim(), ativo_ipca: null };
  if (nome.trim() !== "IPCA+") {
    return data;
  }
  data.ativo_ipca = {
    mesversario: 15,
    ipca_2_meses: false,
    ipca_negativo: false,
  };
  for (const detalhe of detalhes) {
    const info = detalhe.trim().toLowerCase();
    if (info.startsWith("aniversário")) {
      const numStr = info.split(" ").at(-1);
      const num = parseInt(numStr ?? "");
      if (!isNaN(num) && num >= 1 && num <= 31) {
        data.ativo_ipca.mesversario = num;
      }
    }
    if (info === "segundo mês anterior") {
      data.ativo_ipca.ipca_2_meses = true;
    }
    if (info === "variação positiva") {
      data.ativo_ipca.ipca_negativo = true;
    }
  }
  return data;
};

export const strFromIndice = ({ nome, ativo_ipca }: IndiceData) => {
  const data = [];
  data.push(nome);
  if (ativo_ipca) {
    const { mesversario, ipca_2_meses, ipca_negativo } = ativo_ipca;
    if (mesversario !== 15) {
      data.push(`Aniversário ${mesversario}`);
    }
    if (ipca_2_meses) {
      data.push("Segundo mês anterior");
    }
    if (ipca_negativo) {
      data.push("Variação positiva");
    }
  }
  return data.join(" | ");
};
