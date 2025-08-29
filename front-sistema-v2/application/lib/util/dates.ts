export function isSixMonthOrMoreApart(date1: Date, date2: Date): boolean {
  const NUMERO_DIAS_MES: number = 30;
  const NUMERO_HORAS_DIA: number = 24;
  const NUMERO_MINUTOS_HORA: number = 60;
  const NUMERO_SEGUNDOS_MINUTO: number = 60;
  const NUMERO_MILISEGUNDOS_SEGUNDO: number = 1000;
  const SEIS_MESES_EM_MILISEGUNDOS: number =
    6 *
    NUMERO_DIAS_MES *
    NUMERO_HORAS_DIA *
    NUMERO_MINUTOS_HORA *
    NUMERO_SEGUNDOS_MINUTO *
    NUMERO_MILISEGUNDOS_SEGUNDO;

  const diferencaEmMilisegundos: number = date1.getTime() - date2.getTime();

  return Math.abs(diferencaEmMilisegundos) >= SEIS_MESES_EM_MILISEGUNDOS;
}

export function getDataFormatadaFromDate(date: Date): string {
  const dia = String(date.getDate()).padStart(2, "0");
  const mes = String(date.getMonth() + 1).padStart(2, "0");
  const ano = date.getFullYear();

  return `${ano}-${mes}-${dia}`;
}

export const mes = (numero: number) =>
  ({
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
  })[numero];
