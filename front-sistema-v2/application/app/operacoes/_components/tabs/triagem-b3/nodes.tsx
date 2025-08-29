import { Box, HStack, Icon, Text, VStack, keyframes } from "@chakra-ui/react";
import Image, { StaticImageData } from "next/image";
import { Handle, NodeProps, Position } from "reactflow";

import React from "react";
import { IconType } from "react-icons";
import { getColorHex } from "@/app/theme";
import {
  IoCheckmarkOutline,
  IoShuffleOutline,
  IoTimeOutline,
} from "react-icons/io5";

export const realocacao = () => ({
  color: getColorHex("amarelo.main"),
  text: "Solicita Realocação",
  icon: IoShuffleOutline,
});

export const aguardando = (text: string = "Aguardando") => ({
  color: getColorHex("cinza.400"),
  icon: IoTimeOutline,
  text,
});

export const ok = (text: string = "Concluído") => ({
  color: getColorHex("verde.main"),
  icon: IoCheckmarkOutline,
  text,
});

export const recusado = (text: string = "Recusado") => ({
  color: getColorHex("rosa.main"),
  icon: IoTimeOutline,
  text,
});

export type Company = {
  name: string;
  icon?: StaticImageData | IconType;
  detail?: React.ReactNode;
};

export type OperacaoNodeData = {
  label: string;
  details?: React.ReactNode;
  status: {
    pending?: boolean;
    bgColor?: string;
    icon: any;
    color: string;
    text: string;
  };
  company: Company;
};

export function IVNode({
  ...props
}: NodeProps<OperacaoNodeData> & { hasSource?: boolean; hasTarget?: boolean }) {
  return (
    <OperacaoNode
      {...props}
      borderColor={props.data.status.color}
      detail={
        typeof props.data.company.detail === "string" ? (
          <Box flex={1} bgColor={props.data.company.detail} />
        ) : (
          (props.data.company.detail ?? <Box flex={1} bgColor="cinza.500" />)
        )
      }
      pending={props.data.status.pending}
    >
      <VStack
        bgColor={props.data.status.bgColor}
        borderLeft="1px solid"
        borderLeftColor="cinza.main"
        fontSize="xs"
        flex={1}
        h="100%"
        p="8px"
        alignItems="stretch"
        gap={0}
        justifyContent="center"
      >
        <HStack justifyContent="space-between">
          {props.data.company.icon ? (
            "src" in props.data.company.icon ? (
              <Image
                alt="simbolo"
                src={props.data.company.icon}
                width={18}
                height={18}
              />
            ) : (
              <Icon
                boxSize="18px"
                as={props.data.company.icon}
                color="cinza.500"
              />
            )
          ) : (
            <></>
          )}
          <Text color={props.data.status.color}>
            <Icon as={props.data.status.icon} />
            <strong>{" " + props.data.status.text}</strong>
          </Text>
        </HStack>
        <Text>
          <strong>{props.data.company?.name}</strong> - {props.data.label}
        </Text>
        {typeof props.data.details === "string" ? (
          <Text>{props.data.details}</Text>
        ) : (
          props.data.details
        )}
      </VStack>
    </OperacaoNode>
  );
}

export function BasicNode({
  ...props
}: NodeProps<OperacaoNodeData> & { hasSource?: boolean; hasTarget?: boolean }) {
  return (
    <OperacaoNode
      {...props}
      borderColor={props.data.status.color}
      bgColor={props.data.status?.bgColor}
      pending={props.data.status.pending}
    >
      <VStack gap={0} w="100%" pr="4px" color={props.data.status.color}>
        <Icon fontSize="24px" as={props.data.status.icon} />
        <Text textAlign="center" fontWeight="bold">
          {props.data.status.text}
        </Text>
      </VStack>
    </OperacaoNode>
  );
}

const frames = () => keyframes`
    0% { outline-width: 0px; }
    50% { outline-width: 8px; }
    100% { outline-width: 0px; }
`;

const animation = () => `${frames()} 1s ease-in-out infinite`;

export function OperacaoNode({
  detail,
  children,
  hasSource,
  hasTarget,
  borderColor,
  bgColor,
  pending,
}: NodeProps & {
  detail?: React.ReactNode;
  children?: React.ReactNode;
  hasSource?: boolean;
  hasTarget?: boolean;
  borderColor?: string;
  bgColor?: string;
  pending?: boolean;
}) {
  return (
    <>
      {hasSource && (
        <Handle
          type="source"
          isConnectableStart={true}
          position={Position.Right}
        />
      )}
      <HStack
        outline="0px solid"
        outlineColor="azul_4.main"
        animation={pending ? animation() : undefined}
        p={0}
        overflow="hidden"
        w="300px"
        h="100px"
        alignItems="stretch"
        bgColor={bgColor ?? "white"}
        gap={0}
        borderRadius="4px"
        border="2px solid"
        borderColor={borderColor}
      >
        <VStack w="5px" alignItems="stretch" gap={0}>
          {detail}
        </VStack>
        <HStack flex={1}>{children}</HStack>
      </HStack>
      {hasTarget && (
        <Handle
          type="target"
          isConnectableEnd={true}
          position={Position.Left}
        />
      )}
    </>
  );
}
