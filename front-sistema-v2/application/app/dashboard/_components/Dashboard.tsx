"use client";

import { useAsync } from "@/lib/hooks";
import { wait } from "@/lib/util/misc";
import { RepeatIcon } from "@chakra-ui/icons";
import {
  Box,
  Button,
  Progress,
  Skeleton,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  VStack,
  keyframes,
} from "@chakra-ui/react";
import { MutableRefObject, useRef, useState } from "react";

const reports: { title: string; link: string }[] = [
  {
    title: "Relatório de Alocação",
    link: "b259f358-e082-4f61-b71e-cacd84e41e3a",
  },
  {
    title: "Relatório de bancos",
    link: "178f06e1-fd0a-4e97-8e5c-090f847c0650",
  },
  {
    title: "Relatório de Compras e Vendas",
    link: "0e0c77e9-d016-4ec6-8491-3832ceecc0fd",
  },
  {
    title: "Comparação de Portfólios dos Fundos",
    link: "b0559159-ce16-45ab-9f28-395c5f2d8f96",
  },
  {
    title: "Relatório de FIDCs",
    link: "21202f06-be37-4d93-aca3-4012ecf1e136",
  },
  {
    title: "Relatório de ratings",
    link: "b06e174f-80c7-48f8-980c-20d225b919db",
  },
  {
    title: "Distribuição de Empresas por Analistas",
    link: "07d999ad-4877-4c70-bf20-d62925dac6ef",
  },
  {
    title: "Mercado Secundário de Crédito",
    link: "aea731ec-338c-4d0f-88ea-be9a054f60b8",
  },
  {
    title: "Acompanhamento da indústria",
    link: "24998cb7-4c37-491d-bb9d-ff2dd9efebc9",
  },
  {
    title: "Comparativo ISPs",
    link: "f86cd26b-bf33-414b-94f3-f158f389c7f7",
  },
  {
    title: "PnL",
    link: "28159305-f496-4c18-a89e-d854e05234dd",
  },
].map(({ title, link }) => ({
  title,
  link: `https://app.powerbi.com/reportEmbed?reportId=${link}&autoAuth=true&ctid=828d299c-d85c-4fc7-abf2-9c0724378d20&navContentPaneEnabled=false`,
}));

const frames = () => keyframes`
    0% { transform: rotate(0turn); }
    100% { transform: rotate(1turn); }
`;

const animation = () => `${frames()} 1s linear infinite`;

export default function Dashboard() {
  const iframes = useRef<
    Record<string, MutableRefObject<HTMLIFrameElement | null>>
  >({});

  const [loading, setLoading] = useState(
    reports
      .map(({ title }) => title)
      .reduce(
        (obj, title) => ({ ...obj, [title]: false }),
        {} as Record<string, boolean>,
      ),
  );

  return (
    <Tabs h="100%" display="flex" flexDirection="column">
      <TabList>
        {reports.map((r) => (
          <Tab fontSize="sm">{r.title}</Tab>
        ))}
      </TabList>
      <TabPanels flex={1}>
        {reports.map(({ link, title }) => (
          <TabPanel h="100%" p={0}>
            <VStack
              w="100%"
              h="100%"
              alignItems="flex-start"
              position="relative"
            >
              <VStack
                cursor={loading[title] ? "auto" : "pointer"}
                animation={loading[title] ? animation() : "none"}
                zIndex={20}
                position="absolute"
                bottom="32px"
                right="32px"
                bgColor={loading[title] ? "cinza.600" : "verde.main"}
                color={loading[title] ? "cinza.400" : "white"}
                borderRadius="50%"
                w="48px"
                h="48px"
                justifyContent="center"
                onClick={async () => {
                  if (loading[title]) return;
                  setLoading({ ...loading, [title]: true });
                  await wait(1000);
                  setLoading({ ...loading, [title]: false });
                }}
              >
                <RepeatIcon width="60%" height="60%" />
              </VStack>
              {loading[title] ? (
                <Skeleton h="100%" w="100%" />
              ) : (
                <iframe
                  ref={iframes.current[title]}
                  style={{ width: "100%", height: "100%" }}
                  src={link}
                />
              )}
            </VStack>
          </TabPanel>
        ))}
      </TabPanels>
    </Tabs>
  );
}
