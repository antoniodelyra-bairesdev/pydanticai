import stringHash from "string-hash";

export const fmtCNPJ = (cnpj: string) => {
  const stripped = cnpj.match(/[0-9]/g) ?? [];
  return (
    stripped.splice(0, 2).join("") +
    "." +
    stripped.splice(0, 3).join("") +
    "." +
    stripped.splice(0, 3).join("") +
    "/" +
    stripped.splice(0, 4).join("") +
    "-" +
    stripped.splice(0, 2).join("")
  );
};

export const fmtCETIP = (cetip: string) => {
  const stripped = cetip.match(/[0-9]/g) ?? [];
  return (
    stripped.splice(0, 5).join("") +
    "." +
    stripped.splice(0, 2).join("") +
    "-" +
    stripped.splice(0, 1).join("")
  );
};

export const onlyNumbers = (txt: string) => txt.replace(/\D/g, "");

const pd = (value: number | string) => {
  return (value + "").padStart(2, "0");
};

export const ptDateToYYYYMMDD = (dateStr: string) =>
  dateStr.split("/").reverse().join("-");

export const dateToStr = (date: Date) =>
  `${date.getFullYear()}-${pd(date.getMonth() + 1)}-${pd(date.getDate())}`;

export const fmtDate = (str: string) => {
  const date = new Date(str + "T00:00:00");
  return date.toLocaleDateString("pt-BR");
};

export const fmtDatetime = (str: string) => {
  const date = new Date(str);
  return `${pd(date.getDate())}/${pd(date.getMonth() + 1)}/${date.getFullYear()} ${pd(date.getHours())}:${pd(date.getMinutes())}:${pd(date.getSeconds())}`;
};

export const ymdToDate = (timestamp: string) => {
  return new Date(timestamp + "T00:00:00");
};

export const strHSL = (str: string): [number, number, number] => {
  const hash = stringHash(str);
  const h = hash % 360;
  const s = ((hash >>> 4) % 25) + 75;

  // Se considerarmos a escala de matiz com luminosidade igual, percebemos que
  // enxergamos os tons de azul/roxo com uma aparente luminosidade menor. Para
  // tentar mitigar esse efeito uso uma correção entre a matiz 180 e 300 e adi-
  // ciono uma luminosidade extra nesses valores, sendo a maior delas em 240,
  // onde temos a matiz de azul que enxergamos com menos intensidade luminosa.

  // Escala de matiz (0 a 360):
  // https://web.archive.org/web/20231027120423/https://www.digimizer.com/manual/help/png/HueScale.png
  // Plot da curva:
  // https://www.geogebra.org/graphing/apvcrahw
  const l =
    ((hash >>> 8) % 10) +
    40 +
    (h > 180 && h < 300
      ? 15 * (Math.sin(((h - 180) / 60) * Math.PI - Math.PI / 2) + 1)
      : 0);

  return [h, s, l];
};

export const strCSSColor = (str: string) => {
  const [h, s, l] = strHSL(str);
  return `hsl(${h},${s}%,${l}%)`;
};

export type SingularPluralMapping = Record<
  string,
  { singular: string; plural: string }
>;

export const pluralOrSingular = (
  text: string,
  suffixMappings: SingularPluralMapping,
  quantity: number,
) => {
  let replaced = text;
  for (const [search, { singular, plural }] of Object.entries(suffixMappings)) {
    replaced = replaced.replaceAll(
      search,
      Math.abs(quantity) <= 1 ? singular : plural,
    );
  }
  return replaced;
};

export const fmtNumber = (quantity: number, fracDigits: number = 2) => {
  return quantity.toLocaleString("pt-BR", {
    minimumFractionDigits: fracDigits,
    maximumFractionDigits: fracDigits,
  });
};

export const numberParser = (
  input: string,
  thousandSeparator: string,
  fractionalSeparator: string,
): number => {
  // Garante que não irá receber um valor em branco
  if (!input.trim()) return NaN;

  input = input.replaceAll(" ", "");

  const data = input.split(fractionalSeparator);
  const fracSepCount = data.length - 1;

  // Garante que só existe no máximo uma vírgula
  if (fracSepCount > 1) return NaN;

  const [intWithSign = "0", frac = "0"] = data;
  const sign = intWithSign.startsWith("-") ? -1 : 1;
  const int = sign === -1 ? intWithSign.substring(1) : intWithSign;

  // Garante que só existem números depois da vírgula
  if (frac.match(/[0-9]/g)?.length !== frac.length) return NaN;

  const thousandSeparations = int.split(thousandSeparator);
  const thousandSepCount = thousandSeparations.length - 1;

  // Não há separação entre os milhares
  if (thousandSepCount === 0) return sign * Number(int + "." + frac);

  // Garante que o número não comece com separação de milhares
  if (int.startsWith(thousandSeparator)) return NaN;

  // Garante que a separação entre os milhares está correta
  for (let i = 4; i <= int.length; i++) {
    const pos = int.length - i;
    if (i % 4 === 0) {
      if (int[pos] !== thousandSeparator) {
        return NaN;
      }
    } else {
      if (![..."1234567890"].includes(int[pos])) {
        return NaN;
      }
    }
  }

  return sign * Number(int.replaceAll(thousandSeparator, "") + "." + frac);
};

export const fmtStrToNumber = (input: string): number => {
  const pt = numberParser(input, ".", ",");
  return !isNaN(pt) ? pt : numberParser(input, ",", ".");
};

export const getNumericDataFromValue = (value: any): number | string => {
  const num =
    typeof value === "string"
      ? fmtStrToNumber(value) // Input normal
      : null; // Célula deletada
  return num !== null && !isNaN(num)
    ? num // Número válido
    : typeof value === "string"
      ? value.trim()
      : ""; // Dado inválido: null ou outra string
};

export const ptNumStrToNumber = (numStr: string) =>
  Number(numStr.replaceAll(".", "").replaceAll(",", "."));
export const fmtNumberComparator = (n1: string, n2: string) =>
  ptNumStrToNumber(n1) - ptNumStrToNumber(n2);
