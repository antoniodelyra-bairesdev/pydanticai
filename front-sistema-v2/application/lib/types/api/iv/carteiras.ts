export type ArquivoCarteira = {
  nome: string;
  status: "OK" | "ERRO";
  tipo: "XML_ANBIMA_4.01" | "XML_ANBIMA_5.0" | null;
  detalhes: string | null;
};

export type PastaCarteiras = {
  nome: string;
  status: "OK" | "ERRO";
  detalhes: string | null;
  carteiras: ArquivoCarteira[];
  subpastas: PastaCarteiras[];
};

export type ResultadoExportacao = {
  caminho: string;
  status: "MANTIDO" | "CONVERTIDO" | "ERRO";
  resultado: string[];
};
