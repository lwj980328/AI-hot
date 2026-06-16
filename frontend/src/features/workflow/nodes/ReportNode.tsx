import { memo } from "react";
import { Position } from "@xyflow/react";
import { BaseNode } from "./BaseNode";

/** Report 节点 - 最终节点，只有目标连接点 */
function ReportNodeComponent({ data }: { data: Record<string, unknown> }) {
  return (
    <BaseNode
      data={data as { label: string; description: string; status: "pending" | "running" | "completed" | "failed"; toolCount: number }}
      targetPosition={Position.Top}
    />
  );
}

export const ReportNode = memo(ReportNodeComponent);
