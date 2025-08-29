import {
  MercadoEnum,
  TipoTituloPrivadoEnum,
} from "../types/api/iv/operacoes/processamento";

export const ehFluxoII = (
  tipo_ativo: TipoTituloPrivadoEnum,
  mercado: MercadoEnum,
) =>
  [
    TipoTituloPrivadoEnum.Debênture,
    TipoTituloPrivadoEnum.CRI,
    TipoTituloPrivadoEnum.CRA,
    TipoTituloPrivadoEnum.FIDC,
  ].includes(tipo_ativo) && mercado === MercadoEnum.SECUNDARIO;
