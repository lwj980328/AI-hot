import type { TaskStatus } from "@/types/task";
import type { WorkflowRunStatus } from "@/types/workflow";

/** 状态显示配置 */
export const statusConfig: Record<string, { label: string; color: string }> = {
  pending: { label: "等待中", color: "bg-gray-100 text-gray-700" },
  running: { label: "运行中", color: "bg-blue-100 text-blue-700" },
  completed: { label: "已完成", color: "bg-green-100 text-green-700" },
  failed: { label: "失败", color: "bg-red-100 text-red-700" },
};

/** 获取状态配置 */
export function getStatusConfig(status: TaskStatus | WorkflowRunStatus) {
  return statusConfig[status] || statusConfig.pending;
}
