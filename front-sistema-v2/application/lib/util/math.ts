export const distribuir = (
  valor: number,
  partes: number,
  casasDecimais: number,
): number[] => {
  const expoente = 10 ** casasDecimais;
  const ajustado = valor * expoente;
  const quociente = Math.floor(ajustado / partes);
  const resto = Math.floor(ajustado % partes);
  return [
    ...Array(resto).fill((quociente + 1) / expoente),
    ...Array(partes - resto).fill(quociente / expoente),
  ];
};
