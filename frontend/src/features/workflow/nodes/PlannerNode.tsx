import { memo } from "react";
import { Position } from "@xyflow/react";
import { BaseNode } from "./BaseNode";

/** Planner 节点 */
function PlannerNodeComponent({ data }: { data: Record<string, unknown> }) {
  return (
    <BaseNode
      data={data as { label: string; description: string; status: "pending" | "running" | "completed" | "failed"; toolCount: number }}
      sourcePosition={Position.Bottom}
    />
  );
}

export const PlannerNode = memo(PlannerNodeComponent);
