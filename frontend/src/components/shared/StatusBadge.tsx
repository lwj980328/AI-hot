import { Badge } from "@/components/ui/badge";
import { getStatusConfig } from "@/utils/status";
import type { TaskStatus } from "@/types/task";
import type { WorkflowRunStatus } from "@/types/workflow";

interface StatusBadgeProps {
  status: TaskStatus | WorkflowRunStatus;
}

/** 状态徽章组件 */
export function StatusBadge({ status }: StatusBadgeProps) {
  const config = getStatusConfig(status);
  return <Badge className={config.color}>{config.label}</Badge>;
}
