"use client";

import { Tab, TabList, TabPanel, TabPanels, Tabs } from "@chakra-ui/react";
import tabsComponents from "./tabs";

export default function LiberacaoCotas() {
  const tabs = [
    {
      title: "Batimentos Iniciais",
      component: <tabsComponents.BatimentosIniciais />,
    },
    { title: "Aluguel de Ações", component: <tabsComponents.AluguelAcoes /> },
    {
      title: "Movimentações PGBL",
      component: <tabsComponents.MovimentacoesPGBL />,
    },
    { title: "Preços de Ativos", component: <tabsComponents.PrecosAtivos /> },
    {
      title: "Taxa de Performance",
      component: <tabsComponents.TaxaPerformance />,
    },
    {
      title: "Operações Compromissadas",
      component: <tabsComponents.OperacoesCompromissadas />,
    },
    {
      title: "Batimento Estoque",
      component: <tabsComponents.BatimentoEstoque />,
    },
    {
      title: "Relatórios D-2",
      component: <tabsComponents.RelatoriosD2 />,
    },
  ];

  return (
    <Tabs h="100%" display="flex" flexDirection="column">
      <TabList overflowX="auto" overflowY="hidden">
        {tabs.map(({ title }) => (
          <Tab key={title}>{title}</Tab>
        ))}
      </TabList>
      <TabPanels flex={1} overflow="auto">
        {tabs.map(({ title, component }) => (
          <TabPanel key={title} h="100%">
            {component}
          </TabPanel>
        ))}
      </TabPanels>
    </Tabs>
  );
}
