import { useCallback, useEffect, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  type NodeTypes,
  type EdgeTypes,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { PlannerNode } from "./nodes/PlannerNode";
import { ContextNode } from "./nodes/ContextNode";
import { ResearchNode } from "./nodes/ResearchNode";
import { AnalysisNode } from "./nodes/AnalysisNode";
import { MemoryNode } from "./nodes/MemoryNode";
import { ReportNode } from "./nodes/ReportNode";
import { LoopEdge } from "./edges/LoopEdge";
import { NodeDetailPanel } from "./panels/NodeDetailPanel";
import type { NodeStatus, ToolCallRecord } from "@/types/workflow";

/** 自定义节点类型 */
const nodeTypes: NodeTypes = {
  planner: PlannerNode,
  context: ContextNode,
  research: ResearchNode,
  analysis: AnalysisNode,
  memory: MemoryNode,
  report: ReportNode,
};

/** 自定义边类型 */
const edgeTypes: EdgeTypes = {
  loop: LoopEdge,
};

/** 节点描述 */
const nodeDescriptions: Record<string, string> = {
  planner: "将用户查询转化为研究计划",
  context: "构建研究所需上下文，召回历史记忆",
  research: "执行资料采集，调用工具获取数据",
  analysis: "从原始资料中提取结构化知识",
  memory: "将研究结果写入长期记忆",
  report: "生成最终研究报告",
};

/** 节点标签 */
const nodeLabels: Record<string, string> = {
  planner: "Planner",
  context: "Context",
  research: "Research",
  analysis: "Analysis",
  memory: "Memory",
  report: "Report",
};

interface WorkflowCanvasProps {
  nodeStates: Record<string, NodeStatus>;
  toolCalls: ToolCallRecord[];
}

/** 构建初始节点 */
function buildNodes(
  nodeStates: Record<string, NodeStatus>,
  toolCalls: ToolCallRecord[]
): Node[] {
  // 计算每个节点的工具调用数量
  const toolCountByNode: Record<string, number> = {};
  toolCalls.forEach((call) => {
    toolCountByNode[call.node_name] =
      (toolCountByNode[call.node_name] || 0) + 1;
  });

  return [
    {
      id: "planner",
      type: "planner",
      position: { x: 250, y: 0 },
      data: {
        label: nodeLabels.planner,
        description: nodeDescriptions.planner,
        status: nodeStates.planner || "pending",
        toolCount: toolCountByNode.planner || 0,
      },
    },
    {
      id: "context",
      type: "context",
      position: { x: 250, y: 100 },
      data: {
        label: nodeLabels.context,
        description: nodeDescriptions.context,
        status: nodeStates.context || "pending",
        toolCount: toolCountByNode.context || 0,
      },
    },
    {
      id: "research",
      type: "research",
      position: { x: 250, y: 200 },
      data: {
        label: nodeLabels.research,
        description: nodeDescriptions.research,
        status: nodeStates.research || "pending",
        toolCount: toolCountByNode.research || 0,
      },
    },
    {
      id: "analysis",
      type: "analysis",
      position: { x: 250, y: 300 },
      data: {
        label: nodeLabels.analysis,
        description: nodeDescriptions.analysis,
        status: nodeStates.analysis || "pending",
        toolCount: toolCountByNode.analysis || 0,
      },
    },
    {
      id: "memory",
      type: "memory",
      position: { x: 250, y: 400 },
      data: {
        label: nodeLabels.memory,
        description: nodeDescriptions.memory,
        status: nodeStates.memory || "pending",
        toolCount: toolCountByNode.memory || 0,
      },
    },
    {
      id: "report",
      type: "report",
      position: { x: 250, y: 500 },
      data: {
        label: nodeLabels.report,
        description: nodeDescriptions.report,
        status: nodeStates.report || "pending",
        toolCount: toolCountByNode.report || 0,
      },
    },
  ];
}

/** 构建边 */
function buildEdges(nodeStates: Record<string, NodeStatus>): Edge[] {
  const edges: Edge[] = [
    {
      id: "planner-context",
      source: "planner",
      target: "context",
      animated: nodeStates.context === "running",
    },
    {
      id: "context-research",
      source: "context",
      target: "research",
      animated: nodeStates.research === "running",
    },
    {
      id: "research-analysis",
      source: "research",
      target: "analysis",
      animated: nodeStates.analysis === "running",
    },
    {
      id: "analysis-memory",
      source: "analysis",
      target: "memory",
      animated: nodeStates.memory === "running",
    },
    {
      id: "memory-report",
      source: "memory",
      target: "report",
      animated: nodeStates.report === "running",
    },
    // 回环边：analysis → research
    {
      id: "analysis-research-loop",
      source: "analysis",
      target: "research",
      type: "loop",
      label: "Deep Research",
      animated: nodeStates.research === "running" && nodeStates.analysis === "completed",
    },
  ];

  return edges;
}

/** Workflow Canvas 组件 */
export function WorkflowCanvas({
  nodeStates,
  toolCalls,
}: WorkflowCanvasProps) {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  // 当 nodeStates 或 toolCalls 变化时，重新构建节点和边
  useEffect(() => {
    const newNodes = buildNodes(nodeStates, toolCalls);
    const newEdges = buildEdges(nodeStates);
    setNodes(newNodes);
    setEdges(newEdges);
  }, [nodeStates, toolCalls, setNodes, setEdges]);

  // 节点点击事件
  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      setSelectedNodeId(node.id);
    },
    []
  );

  // 选中的节点
  const selectedNode = selectedNodeId
    ? nodes.find((n) => n.id === selectedNodeId)
    : null;

  // 选中节点的工具调用
  const selectedToolCalls = selectedNodeId
    ? toolCalls.filter((call) => call.node_name === selectedNodeId)
    : [];

  return (
    <div className="relative w-full h-[600px] border rounded-lg bg-background">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        attributionPosition="bottom-left"
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>

      {/* 节点详情面板 */}
      {selectedNode && (
        <div className="absolute top-4 right-4 z-10">
          <NodeDetailPanel
            nodeLabel={nodeLabels[selectedNode.id] || selectedNode.id}
            nodeDescription={nodeDescriptions[selectedNode.id] || ""}
            status={
              (selectedNode.data.status as NodeStatus) || "pending"
            }
            toolCalls={selectedToolCalls}
            onClose={() => setSelectedNodeId(null)}
          />
        </div>
      )}
    </div>
  );
}
