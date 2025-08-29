"use client";

import {
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Text,
} from "@chakra-ui/react";
import CurvaDITab from "./CurvaDITab";
import CurvaNTNBTab from "./CurvaNTNBTab";
import InflacaoTab from "./InflacaoTab";

import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
} from "chart.js";
import ZoomPlugin from "chartjs-plugin-zoom";

Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
  ZoomPlugin,
);

export default function Indicadores() {
  const tabs = [
    { title: "Curva DI", component: <CurvaDITab /> },
    { title: "Curva NTN-B", component: <CurvaNTNBTab /> },
    { title: "Inflação", component: <InflacaoTab /> },
  ];

  return (
    <Tabs h="100%" display="flex" flexDirection="column" isLazy>
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
