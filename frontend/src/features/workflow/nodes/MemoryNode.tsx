import { memo } from "react";
import { BaseNode } from "./BaseNode";

/** Memory 节点 */
function MemoryNodeComponent({ data }: { data: Record<string, unknown> }) {
  return (
    <BaseNode
      data={data as { label: string; description: string; status: "pending" | "running" | "completed" | "failed"; toolCount: number }}
    />
  );
}

export const MemoryNode = memo(MemoryNodeComponent);
