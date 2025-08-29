import { extendTheme, ThemeConfig } from "@chakra-ui/react";

export const colorsVanguarda = {
  azul_1: {
    main: "#1b3157",
    50: "#e7ebf1",
    100: "#c2cddd",
    200: "#9cadc6",
    300: "#768daf",
    400: "#58749f",
    500: "#385d91",
    600: "#315588",
    700: "#284b7c",
    800: "#224270",
    900: "#1b3157",
  },
  azul_2: {
    main: "#0d6696",
    50: "#e3f7fc",
    100: "#b8eaf7",
    200: "#8bddf2",
    300: "#62cfee",
    400: "#46c4ed",
    500: "#2fb9ec",
    600: "#27abdd",
    700: "#1c98cb",
    800: "#1a86b7",
    900: "#0d6696",
  },
  azul_3: {
    main: "#2e96bf",
    50: "#e1f4f8",
    100: "#b5e3ed",
    200: "#87d0e2",
    300: "#61bed7",
    400: "#48b0d2",
    500: "#36a3cc",
    600: "#2e96bf",
    700: "#2484ad",
    800: "#227399",
    900: "#185478",
  },
  azul_4: {
    main: "#00badb",
    50: "#e0f7fc",
    100: "#b2eaf6",
    200: "#80ddf0",
    300: "#4ccee8",
    400: "#24c4e1",
    500: "#00badb",
    600: "#00aac8",
    700: "#0096ad",
    800: "#008294",
    900: "#005f68",
  },
  cinza: {
    main: "#e6e7e8",
    50: "#fafbfc",
    100: "#f5f6f7",
    200: "#f1f2f3",
    300: "#e6e7e8",
    400: "#c4c5c6",
    500: "#a6a7a8",
    600: "#7c7d7e",
    700: "#686969",
    800: "#48494a",
    900: "#272728",
  },
  verde: {
    main: "#5ebb47",
    50: "#eaf7e9",
    100: "#ceeac8",
    200: "#aedda5",
    300: "#8ed080",
    400: "#75c664",
    500: "#5ebb47",
    600: "#54ac3e",
    700: "#479933",
    800: "#3c8829",
    900: "#256915",
  },
  amarelo: {
    main: "#ffc14f",
    50: "#fffde9",
    100: "#fff8c9",
    200: "#fff4a6",
    300: "#ffee84",
    400: "#ffe96b",
    500: "#ffe454",
    600: "#ffd956",
    700: "#ffc14f",
    800: "#faab48",
    900: "#f1853d",
  },
  laranja: {
    main: "#f58b2e",
    50: "#fffee9",
    100: "#fefac8",
    200: "#fdf6a4",
    300: "#fcf27f",
    400: "#f9ed63",
    500: "#f7e849",
    600: "#fedf4c",
    700: "#fdc945",
    800: "#fbb23d",
    900: "#f58b2e",
  },
  rosa: {
    main: "#f04f6f",
    50: "#fde5ea",
    100: "#fcbecb",
    200: "#f994aa",
    300: "#f56b88",
    400: "#f04f6f",
    500: "#ec3b58",
    600: "#db3556",
    700: "#c63052",
    800: "#b12a4f",
    900: "#8d2049",
  },
  roxo: {
    main: "#963b82",
    50: "#f2e6ef",
    100: "#e0bfd8",
    200: "#cc96bf",
    300: "#b76ea5",
    400: "#a65293",
    500: "#963b82",
    600: "#8b367c",
    700: "#7b2f74",
    800: "#6c2a6b",
    900: "#522259",
  },
} as const;

const theme = extendTheme({
  config: {
    initialColorMode: "light",
    useSystemColorMode: false,
  } as ThemeConfig,
  colors: colorsVanguarda,
});

export default theme;

export const getColorHex = (color: string): string => {
  const accesses = color.split(".");
  if (accesses.length === 2) {
    const [col, variant] = accesses;
    return theme.colors[col][variant];
  } else if (accesses.length === 1) {
    const [col] = accesses;
    return theme.colors[col].main;
  }
  return "#FF0000";
};
