"use client";

import { Tab, TabList, TabPanel, TabPanels, Tabs } from "@chakra-ui/react";

import ResetPasswordTab from "./abas/ResetPasswordTab";
import SettingsTab from "./abas/configuracoes/SettingsTab";
import AccountTab from "./abas/conta/AccountTab";

export default function Settings() {
  const tabs = [
    ["Aparência", <SettingsTab />],
    ["Dados Pessoais", <AccountTab />],
    ["Alterar Senha", <ResetPasswordTab />],
  ] as const;

  return (
    <Tabs variant="enclosed-colored">
      <TabList>
        {tabs.map(([name]) => (
          <Tab key={name}>{name}</Tab>
        ))}
      </TabList>
      <TabPanels>
        {tabs.map(([name, tab]) => (
          <TabPanel key={name}>{tab}</TabPanel>
        ))}
      </TabPanels>
    </Tabs>
  );
}
