import { memo } from "react";
import { BaseNode } from "./BaseNode";

/** Analysis 节点 */
function AnalysisNodeComponent({ data }: { data: Record<string, unknown> }) {
  return (
    <BaseNode
      data={data as { label: string; description: string; status: "pending" | "running" | "completed" | "failed"; toolCount: number }}
    />
  );
}

export const AnalysisNode = memo(AnalysisNodeComponent);
