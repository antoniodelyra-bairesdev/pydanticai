import Hint from "@/app/_components/texto/Hint";
import { useAsync, useHTTP } from "@/lib/hooks";
import {
  ResultadoBuscaBoleta,
  SugestaoAlocacao,
  SugestaoBoleta,
} from "@/lib/types/api/iv/operacoes/processamento";
import {
  Box,
  Button,
  HStack,
  Icon,
  Radio,
  RadioGroup,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useCallback, useEffect, useState } from "react";
import { IoClose, IoCloudUpload } from "react-icons/io5";
import BoletaComponent from "../../../boletas/BoletaComponent";
import { BoletaClient } from "@/lib/providers/AlocacoesProvider";

export type PassoSeparacaoProps = {
  alocacoes: SugestaoAlocacao[];
  onBoletasChange: (boletas: BoletaClient[]) => void;
};
export default function PassoSeparacao({
  alocacoes,
  onBoletasChange,
}: PassoSeparacaoProps) {
  const [estrategia, setEstrategia] = useState("manter-criar");

  const [resultado, setResultado] = useState<BoletaClient[] | null>(null);

  const [processando, processar] = useAsync();
  const httpClient = useHTTP({ withCredentials: true });

  const enviar = () => {
    if (processando) return;
    setResultado(null);
    processar(async () => {
      const body = JSON.stringify(alocacoes);
      const response = await httpClient.fetch(
        `v1/operacoes/alocacoes/separacao?formato=titpriv&estrategia_duplicadas=${estrategia}`,
        {
          method: "POST",
          body,
        },
      );
      if (!response.ok) return;
      const boletas: ResultadoBuscaBoleta[] = await response.json();
      setResultado(
        boletas.map((boleta) => {
          boleta.alocacoes.forEach((a, i) => (a.id = i));
          return {
            boleta,
            client_id: Math.random(),
          };
        }),
      );
    });
  };

  useEffect(() => {
    setResultado(null);
  }, [alocacoes]);

  useEffect(() => {
    onBoletasChange(resultado ?? []);
  }, [resultado]);

  const limpar = useCallback(() => {
    setResultado(null);
  }, []);

  return (
    <VStack alignItems="stretch">
      <HStack alignItems="stretch">
        <VStack flex={1} gap={0} alignItems="stretch">
          <Hint>Estratégia de separação</Hint>
          <VStack alignItems="stretch">
            <RadioGroup
              value={estrategia}
              onChange={setEstrategia}
              size="sm"
              colorScheme="verde"
            >
              <VStack
                alignItems="stretch"
                gap={0}
                borderRadius="8px"
                border="1px solid"
                borderColor="azul_1.100"
                p="8px"
              >
                <Radio isDisabled value="ignorar-alterar">
                  Considerar alocações iguais no sistema como duplicadas e
                  ignorá-las. Sugerir alterar boleta(s) existente(s) com as
                  características das demais alocações.
                </Radio>
                <Radio isDisabled value="ignorar-criar">
                  Considerar alocações iguais no sistema como duplicadas e
                  ignorá-las. Sugerir criar novas boletas para as novas
                  alocações.
                </Radio>
                <Radio isDisabled value="manter-alterar">
                  Considerar todas as alocações, independente se já existem
                  iguais no sistema. Sugerir alterar boleta(s) existente(s) com
                  as características das alocações.
                </Radio>
                <Radio value="manter-criar">
                  Considerar todas as alocações, independente se já existem
                  iguais no sistema. Sugerir criar novas boletas para as
                  alocações.
                </Radio>
              </VStack>
            </RadioGroup>
            <HStack justifyContent="flex-end">
              <HStack>
                <Button
                  colorScheme="rosa"
                  size="xs"
                  leftIcon={<Icon as={IoClose} />}
                  onClick={limpar}
                >
                  Limpar
                </Button>
                <Button
                  colorScheme="verde"
                  size="xs"
                  leftIcon={<Icon as={IoCloudUpload} />}
                  onClick={enviar}
                >
                  Processar
                </Button>
              </HStack>
            </HStack>
          </VStack>
        </VStack>
      </HStack>
      <VStack alignItems="stretch">
        {resultado?.map((b, i) => (
          <BoletaComponent
            key={i}
            passo="IMPORTACAO"
            boleta={b}
            onBoletaChange={(b) => {
              if (!resultado) return;
              resultado[i] = b;
              setResultado([...resultado]);
            }}
          />
        ))}
      </VStack>
    </VStack>
  );
}
