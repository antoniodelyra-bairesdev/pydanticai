import { PublicoAlvoEnum } from "@/lib/types/api/iv/v1";
import {
  HStack,
  StackDivider,
  VStack,
  Icon,
  RadioGroup,
  Radio,
  Text,
} from "@chakra-ui/react";
import {
  IoCashOutline,
  IoArrowDownOutline,
  IoArrowUpOutline,
  IoPersonCircleOutline,
} from "react-icons/io5";
import CardDias from "./CardDias";
import InputEditavel from "./InputEditavel";
import { useFundoDetalhes } from "../_providers/FundoDetalhesProvider";

const garantirNumero = (setter: (n: number) => void) => (valor: string) => {
  const num = Number(valor);
  setter(isNaN(num) ? 0 : num);
};

export default function DatasELimitesConteudo() {
  const {
    editando,

    publicoAlvo,
    setPublicoAlvo,

    minimoAplicacao,
    setMinimoAplicacao,
    minimoMovimentacao,
    setMinimoMovimentacao,
    minimoSaldo,
    setMinimoSaldo,

    diasAplicacaoCotizacao,
    setDiasAplicacaoCotizacao,
    duAplicacaoCotizacao,
    setDuAplicacaoCotizacao,
    textoLivreAplicacaoCotizacao,
    setTextoLivreAplicacaoCotizacao,

    diasAplicacaoFinanceiro,
    setDiasAplicacaoFinanceiro,
    duAplicacaoFinanceiro,
    setDuAplicacaoFinanceiro,
    textoLivreAplicacaoFinanceiro,
    setTextoLivreAplicacaoFinanceiro,

    diasResgateCotizacao,
    setDiasResgateCotizacao,
    duResgateCotizacao,
    setDuResgateCotizacao,
    textoLivreResgateCotizacao,
    setTextoLivreResgateCotizacao,

    diasResgateFinanceiro,
    setDiasResgateFinanceiro,
    duResgateFinanceiro,
    setDuResgateFinanceiro,
    textoLivreResgateFinanceiro,
    setTextoLivreResgateFinanceiro,
  } = useFundoDetalhes();

  return (
    <HStack p="8px" divider={<StackDivider />}>
      <VStack flex={3} alignItems="stretch" gap="16px">
        <VStack flex={1} alignItems="stretch">
          <HStack gap="12px" mb="8px">
            <HStack fontSize="lg" gap={0} position="relative" w="14px" h="14px">
              <Icon position="absolute" color="cinza.400" as={IoCashOutline} />
              <Icon
                top="4px"
                left="6px"
                position="absolute"
                color="verde.main"
                as={IoArrowDownOutline}
              />
            </HStack>
            <Text fontSize="sm">Aplicação</Text>
          </HStack>
          <HStack>
            <CardDias
              dias={diasAplicacaoCotizacao}
              onDiasChange={setDiasAplicacaoCotizacao}
              duMarcado={duAplicacaoCotizacao}
              onDuMarcadoChange={setDuAplicacaoCotizacao}
              textoLivre={textoLivreAplicacaoCotizacao}
              onTextoLivreChange={setTextoLivreAplicacaoCotizacao}
              titulo="Cotização"
              flex={1}
              editando={editando}
            />
            <CardDias
              dias={diasAplicacaoFinanceiro}
              onDiasChange={setDiasAplicacaoFinanceiro}
              duMarcado={duAplicacaoFinanceiro}
              onDuMarcadoChange={setDuAplicacaoFinanceiro}
              textoLivre={textoLivreAplicacaoFinanceiro}
              onTextoLivreChange={setTextoLivreAplicacaoFinanceiro}
              titulo="Financeiro"
              flex={1}
              editando={editando}
            />
          </HStack>
        </VStack>
        <VStack flex={1} alignItems="stretch">
          <HStack gap="12px" mb="8px">
            <HStack fontSize="lg" gap={0} position="relative" w="14px" h="14px">
              <Icon position="absolute" color="cinza.400" as={IoCashOutline} />
              <Icon
                top="4px"
                left="6px"
                position="absolute"
                color="rosa.main"
                as={IoArrowUpOutline}
              />
            </HStack>
            <Text fontSize="sm">Resgate</Text>
          </HStack>
          <HStack>
            <CardDias
              dias={diasResgateCotizacao}
              onDiasChange={setDiasResgateCotizacao}
              duMarcado={duResgateCotizacao}
              onDuMarcadoChange={setDuResgateCotizacao}
              textoLivre={textoLivreResgateCotizacao}
              onTextoLivreChange={setTextoLivreResgateCotizacao}
              titulo="Cotização"
              flex={1}
              editando={editando}
            />
            <CardDias
              dias={diasResgateFinanceiro}
              onDiasChange={setDiasResgateFinanceiro}
              duMarcado={duResgateFinanceiro}
              onDuMarcadoChange={setDuResgateFinanceiro}
              textoLivre={textoLivreResgateFinanceiro}
              onTextoLivreChange={setTextoLivreResgateFinanceiro}
              titulo="Financeiro"
              flex={1}
              editando={editando}
            />
          </HStack>
        </VStack>
      </VStack>
      <VStack flex={2} fontSize="xs" alignItems="stretch">
        <HStack gap="6px" fontSize="sm">
          <Icon color="verde.main" as={IoPersonCircleOutline} />
          <Text>Público alvo</Text>
        </HStack>
        <RadioGroup
          size="sm"
          isDisabled={!editando}
          colorScheme="verde"
          defaultValue={publicoAlvo as any}
          value={publicoAlvo as any}
          onChange={(v) => setPublicoAlvo(Number(v) as any)}
        >
          <VStack
            alignItems="stretch"
            borderRadius="8px"
            border="1px solid"
            borderColor="cinza.main"
            p="8px"
          >
            <Radio value={PublicoAlvoEnum.Investidor_Geral as any}>
              <Text fontSize="xs">Investidor geral</Text>
            </Radio>
            <Radio value={PublicoAlvoEnum.Investidor_Qualificado as any}>
              <Text fontSize="xs">Investidor qualificado</Text>
            </Radio>
            <Radio value={PublicoAlvoEnum.Investidor_Profissional as any}>
              <Text fontSize="xs">Investidor profissional</Text>
            </Radio>
          </VStack>
        </RadioGroup>
        <HStack>
          <Text w="150px">Aplicação mínima:</Text>
          <HStack flex={1} alignItems="stretch" gap={0}>
            <Text
              {...(editando
                ? {
                    border: "1px solid",
                    borderRight: "none",
                    borderColor: "cinza.main",
                    bgColor: "cinza.100",
                    p: "2px",
                  }
                : { p: "3px 8px 2px 2px" })}
            >
              R$
            </Text>
            <InputEditavel
              valor={String(minimoAplicacao)}
              onValorChange={garantirNumero(setMinimoAplicacao)}
              flex={1}
              w="128px"
              editando={editando}
              placeholder="Não há"
              textoValorVazio="Não há"
            />
          </HStack>
        </HStack>
        <HStack>
          <Text w="150px">Movimentação mínima:</Text>
          <HStack flex={1} alignItems="stretch" gap={0}>
            <Text
              {...(editando
                ? {
                    border: "1px solid",
                    borderRight: "none",
                    borderColor: "cinza.main",
                    bgColor: "cinza.100",
                    p: "2px",
                  }
                : { p: "3px 8px 2px 2px" })}
            >
              R$
            </Text>
            <InputEditavel
              valor={String(minimoMovimentacao)}
              onValorChange={garantirNumero(setMinimoMovimentacao)}
              flex={1}
              w="128px"
              editando={editando}
              placeholder="Não há"
              textoValorVazio="Não há"
            />
          </HStack>
        </HStack>
        <HStack>
          <Text w="150px">Saldo mínimo:</Text>
          <HStack flex={1} alignItems="stretch" gap={0}>
            <Text
              {...(editando
                ? {
                    border: "1px solid",
                    borderRight: "none",
                    borderColor: "cinza.main",
                    bgColor: "cinza.100",
                    p: "2px",
                  }
                : { p: "3px 8px 2px 2px" })}
            >
              R$
            </Text>
            <InputEditavel
              valor={String(minimoSaldo)}
              onValorChange={garantirNumero(setMinimoSaldo)}
              flex={1}
              w="128px"
              editando={editando}
              placeholder="Não há"
              textoValorVazio="Não há"
            />
          </HStack>
        </HStack>
      </VStack>
    </HStack>
  );
}
