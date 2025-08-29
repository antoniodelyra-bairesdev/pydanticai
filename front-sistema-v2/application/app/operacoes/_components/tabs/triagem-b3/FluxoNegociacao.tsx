import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  Background,
  ControlButton,
  Controls,
  Edge,
  Handle,
  Node,
  NodeProps,
  NodeTypes,
  Position,
  ReactFlow,
  useEdgesState,
  useNodesState,
  getNodesBounds,
  getViewportForBounds,
} from "reactflow";

import Dagre from "@dagrejs/dagre";

import "reactflow/dist/style.css";
import { Box, HStack, Icon, Text, VStack, keyframes } from "@chakra-ui/react";
import Image, { StaticImageData } from "next/image";

import { IconType } from "react-icons";
import { OperacaoType } from "@/lib/types/api/iv/v1";
import { No } from "./fluxo/dados/tipos";
import GrafoFluxo from "./fluxo/dados/GrafoFluxo";
import {
  IoCameraOutline,
  IoContractOutline,
  IoExpandOutline,
} from "react-icons/io5";
import { toPng } from "html-to-image";
import { useAsync } from "@/lib/hooks";
import { getColorHex } from "@/app/theme";
import { wait } from "@/lib/util/misc";

const nodeTypes: NodeTypes = {
  "company-in": (props) => <IVNode {...props} hasTarget={true} />,
  "company-out": (props) => <IVNode {...props} hasSource={true} />,
  "company-in-out": (props) => (
    <IVNode {...props} hasTarget={true} hasSource={true} />
  ),
  in: (props) => <BasicNode {...props} hasTarget={true} />,
  out: (props) => <BasicNode {...props} hasSource={true} />,
  "in-out": (props) => (
    <BasicNode {...props} hasTarget={true} hasSource={true} />
  ),
};

export type FluxoNegociacaoMethods = {
  setNodes: (nodes: No[]) => void;
  setEdges: (edges: Edge[]) => void;
  foco: (...nos: No[]) => void;
};

export type FluxoNegociacaoProps = {
  // methods?: MutableRefObject<FluxoNegociacaoMethods | undefined>
  operacao: OperacaoType;
  eventoSelecionado: number;
};

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

export default function FluxoNegociacao({
  operacao,
  eventoSelecionado,
}: FluxoNegociacaoProps) {
  const { eventos } = operacao;

  const [nodes, _setNodes, onNodesChange] = useNodesState([]);
  const [edges, _setEdges, onEdgesChange] = useEdgesState([]);

  const onLayout = useCallback(
    (nos: No[], arestas: Edge[]) => {
      const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));
      const getLayoutedElements = (
        nodes: Node[],
        edges: Edge[],
        direction: "TB" | "LR",
      ) => {
        g.setGraph({ rankdir: direction });
        edges.forEach((edge) => g.setEdge(edge.source, edge.target));
        nodes.forEach((node) =>
          g.setNode(node.id, {
            ...node,
            width: node.width ?? 300,
            height: node.height ?? 100,
          }),
        );
        Dagre.layout(g);
        return {
          nodes: nodes.map((node) => {
            const { x, y } = g.node(node.id);
            return { ...node, position: { x, y } };
          }),
          edges,
        };
      };
      const layouted = getLayoutedElements(nos, arestas, "LR");
      _setNodes([...layouted.nodes]);
      _setEdges([...layouted.edges]);
    },
    [nodes, edges],
  );

  const methods = useRef({ foco: (nos: No[]) => {}, download: async () => {} });

  useEffect(() => {
    const grafo = GrafoFluxo.makefluxoOperacoes(operacao);
    const evts = eventos.slice(0, eventoSelecionado + 1);
    if (eventos.length !== evts.length) {
      grafo.passado = true;
    }
    if (eventoSelecionado >= 0) evts.forEach((ev) => grafo.adicionarEvento(ev));
    onLayout(grafo.nos, grafo.arestas);
    methods.current.foco(grafo.foco);
  }, [eventoSelecionado, eventos.length]);

  const [fullScreen, setFullScreen] = useState(false);

  const toggleFullScreen = useCallback(() => {
    setFullScreen(!fullScreen);
  }, [fullScreen]);

  const elementRef = useRef<HTMLDivElement | null>(null);

  const [baixando, iniciarDownload] = useAsync();

  return (
    <Box
      w={fullScreen ? "100vw" : "100%"}
      h={fullScreen ? "100vh" : "100%"}
      position={fullScreen ? "absolute" : "static"}
      top={fullScreen ? 0 : undefined}
      left={fullScreen ? 0 : undefined}
      zIndex={fullScreen ? 99999 : 0}
      bgColor="white"
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        ref={elementRef}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        edgesUpdatable={false}
        edgesFocusable={false}
        nodesDraggable={false}
        nodesConnectable={false}
        nodesFocusable={true}
        elementsSelectable={true}
        fitView={true}
        style={{ width: "100%", height: "100%", cursor: "default" }}
        onInit={(instance) => {
          methods.current.foco = (nos: No[]) =>
            setTimeout(
              () =>
                instance.fitView({ nodes: nos, maxZoom: 0.75, duration: 200 }),
              5,
            );
          methods.current.download = () =>
            iniciarDownload(async () => {
              const nb = getNodesBounds(instance.getNodes());
              const tr = getViewportForBounds(nb, nb.width, nb.height, 1, 1);

              instance.setViewport(tr);

              await wait(500);

              await new Promise<void>((resolve) =>
                setTimeout(() => {
                  const options = {
                    width: nb.width,
                    height: nb.height,
                  };
                  if (!elementRef.current) return;
                  toPng(elementRef.current, options).then((b64) => {
                    const a = document.createElement("a");
                    a.href = b64;
                    a.target = "_blank";
                    a.click();
                    resolve();
                  });
                }, 0),
              );

              await wait(500);
            });

          setTimeout(() => {
            [
              ...document.getElementsByClassName("react-flow__attribution"),
            ].forEach((e) => e.remove());
          }, 5);
        }}
        minZoom={0.25}
      >
        <Background />
        <Controls showInteractive={false} position="bottom-right">
          <ControlButton
            disabled={baixando}
            style={{
              backgroundColor: baixando ? getColorHex("cinza.400") : undefined,
            }}
            onClick={() => methods.current?.download()}
          >
            <Icon as={IoCameraOutline} />
          </ControlButton>
          <ControlButton onClick={toggleFullScreen}>
            <Icon as={fullScreen ? IoContractOutline : IoExpandOutline} />
          </ControlButton>
        </Controls>
      </ReactFlow>
    </Box>
  );
}
