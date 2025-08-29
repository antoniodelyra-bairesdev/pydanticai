"use client";

import { getColorHex } from "@/app/theme";
import { Card, CardBody, Heading, VStack } from "@chakra-ui/react";
import {
  Background,
  Node,
  ReactFlow,
  ReactFlowProvider,
  applyNodeChanges,
  useNodesState,
} from "reactflow";

import "reactflow/dist/style.css";

const nodeSize = {
  width: 100,
  height: 40,
};

const nodeTypes = {};

const initialNodes: Node[] = [
  {
    id: "Start",
    data: {
      label: "Rotina",
    },
    type: "custom",
    ...nodeSize,
    position: { x: 0, y: 0 },
  },
  {
    id: "End",
    data: {
      label: "Final",
    },
    type: "custom",
    ...nodeSize,
    position: { x: 400, y: 0 },
  },
];

export default function FontesDados() {
  const [nodes, setNodes] = useNodesState(initialNodes);

  return (
    <VStack alignItems="stretch">
      <Heading size="md">Ih alá</Heading>
      <Card variant="outline">
        <CardBody p={0}>
          <ReactFlowProvider>
            <ReactFlow
              style={{ minHeight: "256px" }}
              nodes={nodes}
              onNodesChange={(changes) => {
                setNodes((nodes) => applyNodeChanges(changes, nodes));
              }}
              nodeTypes={nodeTypes}
              fitView
            >
              <Background color={getColorHex("azul_4.main")} />
            </ReactFlow>
          </ReactFlowProvider>
        </CardBody>
      </Card>
    </VStack>
  );
}
