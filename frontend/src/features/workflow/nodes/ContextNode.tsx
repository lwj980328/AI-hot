import { memo } from "react";
import { BaseNode } from "./BaseNode";

/** Context 节点 */
function ContextNodeComponent({ data }: { data: Record<string, unknown> }) {
  return (
    <BaseNode
      data={data as { label: string; description: string; status: "pending" | "running" | "completed" | "failed"; toolCount: number }}
    />
  );
}

export const ContextNode = memo(ContextNodeComponent);
