import { HStack, Input, Tag, Text } from "@chakra-ui/react";
import { useState } from "react";

export type InputBenchmarkProps = {
  editando?: boolean;
  size?: "xs" | "sm" | "md" | "lg";
  listaIndices?: string[];
  tokens: string[];
  indices: string[];
  onTokensUpdate: (tokens: string[]) => void;
  onIndicesUpdate: (indices: string[]) => void;
};

const espacos = [" ", "\r", "\t", "\n"];
const naoVazio = (s: string) => Boolean(s);
const sifraoSeguidoDePeloMenosUmNumero = /\$([0-9])+/g;
const ehInterpolacao = (t: string) =>
  (t.match(sifraoSeguidoDePeloMenosUmNumero) ?? [])[0] === t;

export default function InputBenchmark({
  editando,
  size,
  tokens,
  indices,
  listaIndices = [],
  onTokensUpdate,
  onIndicesUpdate,
}: InputBenchmarkProps) {
  const listaIndicesMinuscula = listaIndices.map((i) => i.toLocaleLowerCase());

  const [input, setInput] = useState("");

  const processarTokens = (novaString: string) => {
    novaString = novaString.replaceAll("$", "");

    const temEspaco = espacos.some((espaco) => novaString.includes(espaco));
    if (!temEspaco) return setInput(novaString);

    const fragmentosValidos = novaString.split(/ |\r|\t|\n/g).filter(naoVazio);

    let proximoIndice = indices.length;
    const indicesEncontrados: string[] = [];
    const fragmentosProcessados: string[] = [];

    fragmentosValidos.forEach((fragmento) => {
      const posicaoIndiceEncontrado = listaIndicesMinuscula.findIndex(
        (i) => i === fragmento.toLocaleLowerCase(),
      );

      if (posicaoIndiceEncontrado === -1)
        return fragmentosProcessados.push(fragmento);
      fragmentosProcessados.push("$" + proximoIndice++);

      indicesEncontrados.push(listaIndices[posicaoIndiceEncontrado]);
    });

    setInput("");

    onTokensUpdate([...tokens, ...fragmentosProcessados]);
    onIndicesUpdate([...indices, ...indicesEncontrados]);
  };

  const removerTokens = () => {
    const ultimoToken = tokens.pop();
    if (!ultimoToken) return;

    setInput(ehInterpolacao(ultimoToken) ? (indices.pop() ?? "") : ultimoToken);

    onTokensUpdate?.([...tokens]);
    onIndicesUpdate([...indices]);
  };

  return (
    <HStack flexWrap="wrap" gap={0} alignItems="stretch">
      <HStack
        minH="24px"
        border="1px solid"
        borderColor="cinza.main"
        flex={1}
        bgColor="cinza.100"
        flexWrap="wrap"
        p="0 8px"
        fontSize={size}
        gap="4px"
      >
        {tokens.map((t, i) => {
          if (!ehInterpolacao(t))
            return (
              <Text as="span" wordBreak="break-word" key={i}>
                {t}
              </Text>
            );
          const posicaoIndice = Number(t.slice(1));
          return (
            <Tag key={i} bgColor="verde.100" borderRadius="full">
              <Text fontSize={size}>{indices[posicaoIndice]}</Text>
            </Tag>
          );
        })}
      </HStack>
      <Input
        visibility={editando ? "visible" : "hidden"}
        size={size}
        value={input}
        onKeyDown={(ev) => {
          if (ev.key === "Enter") {
            return processarTokens(ev.currentTarget.value + "\n");
          }
          if (ev.key === "Backspace") {
            if (ev.currentTarget.value !== "") return;
            ev.preventDefault();
            removerTokens();
          }
        }}
        onChange={(ev) => processarTokens(ev.target.value)}
        focusBorderColor="verde.main"
      />
    </HStack>
  );
}
