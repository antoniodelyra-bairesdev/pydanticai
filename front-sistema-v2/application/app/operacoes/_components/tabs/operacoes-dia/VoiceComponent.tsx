import { Voice } from "@/lib/types/api/iv/v1";
import { Box, Button, HStack, Icon, Text, VStack } from "@chakra-ui/react";
import { companies } from "../triagem-b3/fluxo/dados/companies";
import Image, { StaticImageData } from "next/image";
import { IoCubeOutline, IoServerOutline, IoTimeOutline } from "react-icons/io5";
import { fmtDatetime, fmtNumber } from "@/lib/util/string";

export type VoiceComponentProps = {
  voice: Voice;
  onRegistrarCorretoraClick?: (contaB3Corretora: string) => void;
};

export default function VoiceComponent({
  voice,
  onRegistrarCorretoraClick,
}: VoiceComponentProps) {
  const bg = voice.registro_contraparte ? "cinza.50" : "rosa.50";
  const bgAccent = voice.registro_contraparte ? "cinza.100" : "rosa.100";
  const lines = voice.registro_contraparte ? "cinza.main" : "rosa.200";
  return (
    <HStack
      gap={0}
      w="100%"
      alignItems="stretch"
      overflow="hidden"
      border="1px solid"
      borderColor="cinza.100"
      borderRadius="4px"
    >
      <VStack w="6px" gap={0} bgColor="red" alignItems="stretch">
        {companies.b3.detail}
      </VStack>
      <VStack bgColor={bgAccent} w="100%" alignItems="stretch" gap={0}>
        <HStack
          bgColor={bg}
          key={voice.id_trader + voice.criado_em}
          alignItems="stretch"
          wrap="wrap"
          pl="8px"
        >
          <HStack gap={0} alignItems="stretch" wrap="wrap">
            <HStack
              pr="8px"
              borderRight="1px solid"
              borderColor={lines}
              fontSize="sm"
            >
              <Image
                width={24}
                height={24}
                alt="icone b3"
                src={companies.b3.icon as StaticImageData}
              />
              <Text fontWeight="bold">{voice.id_trader}</Text>
            </HStack>
            <HStack
              w="64px"
              fontSize="14px"
              p="4px 8px 4px 8px"
              borderRight="1px solid"
              borderColor={lines}
              justifyContent="center"
            >
              <Text
                fontWeight={900}
                color={voice.vanguarda_compra ? "azul_3.main" : "rosa.main"}
                fontSize="10px"
                border="2px solid"
                borderRadius="4px"
                borderColor={
                  voice.vanguarda_compra ? "azul_3.main" : "rosa.main"
                }
                p="2px"
                lineHeight={1}
              >
                {voice.vanguarda_compra ? "COMPRA" : "VENDE"}
              </Text>
            </HStack>
            <HStack
              p="4px 8px 4px 8px"
              borderRight="1px solid"
              borderColor={lines}
            >
              <Text fontWeight={900}>{voice.codigo_ativo}</Text>
              <Text>{voice.taxa}%</Text>
            </HStack>
            <VStack
              fontSize="xs"
              p="4px 8px 4px 8px"
              gap={0}
              alignItems="flex-start"
              borderRight="1px solid"
              borderColor={lines}
            >
              <Text>
                <Icon as={IoCubeOutline} mr="4px" color="cinza.500" />
                {fmtNumber(voice.quantidade, 0)}
              </Text>
              <Text color="verde.main" fontWeight="bold">
                R$ {fmtNumber(voice.preco_unitario, 6)}
              </Text>
            </VStack>
            <VStack
              fontSize="xs"
              p="4px 8px 4px 8px"
              gap={0}
              alignItems="flex-start"
              borderRight="1px solid"
              borderColor={lines}
            >
              <Text color="cinza.500" fontWeight="bold">
                Total negociado:
              </Text>
              <Text color="verde.main" fontWeight="bold">
                R$ {fmtNumber(voice.preco_unitario * voice.quantidade, 2)}
              </Text>
            </VStack>
            <VStack
              gap={0}
              alignItems="flex-start"
              justifyContent="center"
              fontSize="xs"
              p="4px 8px 4px 8px"
            >
              <HStack>
                <Icon
                  color={
                    voice.registro_contraparte ? "verde.main" : "rosa.main"
                  }
                  as={IoServerOutline}
                  mr="4px"
                />
                <Text fontWeight="bold">
                  {voice.registro_contraparte?.nome ?? "---"}
                </Text>
              </HStack>
              <HStack>
                <Image
                  width={16}
                  height={16}
                  alt="icone b3"
                  src={companies.b3.icon as StaticImageData}
                />
                <Text color="cinza.700">{voice.nome_contraparte}</Text>
              </HStack>
            </VStack>
          </HStack>
          <HStack flex={1} justifyContent="flex-end" pb="4px" pt="4px">
            {!voice.registro_contraparte && (
              <Button
                key="btn"
                ml="4px"
                size="xs"
                colorScheme="rosa"
                onClick={() =>
                  onRegistrarCorretoraClick?.(voice.nome_contraparte)
                }
              >
                Registrar corretora
              </Button>
            )}
            <HStack key="hora" pr="8px" fontSize="xs">
              <Icon color="cinza.500" fontSize="16px" as={IoTimeOutline} />
              <Text>{fmtDatetime(voice.criado_em).split(" ").at(-1)}</Text>
            </HStack>
          </HStack>
        </HStack>
        <Box
          w="100%"
          h="4px"
          bgColor="cinza.main"
          visibility={voice.registro_contraparte ? undefined : "hidden"}
        />
      </VStack>
    </HStack>
  );
}
