import { memo } from "react";
import { BaseNode } from "./BaseNode";

/** Research 节点 - 通常有工具调用 */
function ResearchNodeComponent({ data }: { data: Record<string, unknown> }) {
  return (
    <BaseNode
      data={data as { label: string; description: string; status: "pending" | "running" | "completed" | "failed"; toolCount: number }}
    />
  );
}

export const ResearchNode = memo(ResearchNodeComponent);
