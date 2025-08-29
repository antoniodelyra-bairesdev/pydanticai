"use client";

import Hint from "@/app/_components/texto/Hint";
import { useSettings, useUser } from "@/lib/hooks";
import { Settings } from "@/lib/providers/SettingsProvider";
import { Card, CardBody, HStack, Stack, Switch, Text } from "@chakra-ui/react";
import { ChangeEvent } from "react";

export type BooleanSettingProps = {
  setting: keyof Settings;
  children: string | string[];
};

export const BooleanSetting = ({ setting, children }: BooleanSettingProps) => {
  const { settings, setSettings } = useSettings();
  const { user } = useUser();
  const changeSetting = ({
    target: { checked },
  }: ChangeEvent<HTMLInputElement>) =>
    setSettings(user, {
      ...settings,
      [setting]: checked,
    });

  return (
    <HStack>
      <Switch
        colorScheme="verde"
        isChecked={settings[setting]}
        onChange={changeSetting}
      />
      <Text fontSize="sm">{children}</Text>
    </HStack>
  );
};

export default function SettingsTab() {
  // const { colorMode, toggleColorMode } = useColorMode()

  return (
    <>
      <Hint>Menu lateral</Hint>
      <Card variant="outline">
        <CardBody>
          <Stack>
            <BooleanSetting setting="openDrawerOnHover">
              Abrir ao aproximar cursor do canto da tela
            </BooleanSetting>
            <BooleanSetting setting="closeDrawerOnLeave">
              Fechar menu ao afastar cursor
            </BooleanSetting>
            <BooleanSetting setting="closeDrawerOnLinkClick">
              Fechar ao selecionar aba
            </BooleanSetting>
            {/* <Button
                        leftIcon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
                        colorScheme={colorMode === 'light' ? 'azul_1' : 'verde'}
                        size='sm'
                        onClick={toggleColorMode}
                        mt='16px'
                    >
                        Usar tema {colorMode === 'light' ? 'escuro' : 'claro'}
                    </Button> */}
          </Stack>
        </CardBody>
      </Card>
    </>
  );
}
