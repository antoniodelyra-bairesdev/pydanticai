import { fmtCETIP } from "@/lib/util/string";
import { AddIcon } from "@chakra-ui/icons";
import { HStack, Button, Box, Text } from "@chakra-ui/react";
import CardRegistro from "./CardRegistro";
import { useFundoDetalhes } from "../_providers/FundoDetalhesProvider";

import IconeB3 from "@/public/b3.png";
import IconeBCB from "@/public/bcb.png";
import IconeVanguarda from "@/public/SimboloIcatuVanguarda_Azul.png";
import IconeBritech from "@/public/brit_services_logo.jpg";

export default function CadastrosEContasConteudo() {
  const {
    editando,
    fundoAtualizado,
    contaBritech,
    setContaBritech,
    contaCetip,
    setContaCetip,
    contaSelic,
    setContaSelic,
  } = useFundoDetalhes();

  return (
    <HStack fontSize="xs" p="8px" flexWrap="wrap" alignItems="stretch">
      <CardRegistro
        tipoRegistro="ID"
        imagem={IconeVanguarda}
        nome="Sistema Vanguarda"
        valor={String(fundoAtualizado.id)}
        cor="verde.main"
      />
      {fundoAtualizado.codigo_brit && (
        <CardRegistro
          editando={editando}
          valor={contaBritech}
          onValorChange={setContaBritech}
          tipoRegistro="Lastro"
          imagem={IconeBritech}
          nome="BRITech"
          cor="#833397"
        />
      )}
      {fundoAtualizado.conta_cetip && (
        <CardRegistro
          editando={editando}
          valor={contaCetip}
          onValorChange={setContaCetip}
          imagem={IconeB3}
          nome="CETIP"
        />
      )}
      <CardRegistro
        editando={editando}
        imagem={IconeBCB}
        nome="SELIC"
        valor={contaSelic}
        onValorChange={setContaSelic}
      />
      <Box>
        {editando && (
          <Button
            bgColor="cinza.200"
            h="100%"
            size="xs"
            key={-1}
            leftIcon={<AddIcon />}
          >
            <Text as="span">Adicionar</Text>
          </Button>
        )}
      </Box>
    </HStack>
  );
}
