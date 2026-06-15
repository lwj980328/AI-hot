import type { TaskStatus } from "@/types/task";
import type { WorkflowRunStatus } from "@/types/workflow";

/** 状态显示配置 - 与后端 TaskStatus 枚举一致 */
export const statusConfig: Record<string, { label: string; color: string }> = {
  created: { label: "已创建", color: "bg-gray-100 text-gray-700" },
  planning: { label: "规划中", color: "bg-blue-100 text-blue-700" },
  context_loading: { label: "加载上下文", color: "bg-blue-100 text-blue-700" },
  researching: { label: "研究中", color: "bg-blue-100 text-blue-700" },
  analyzing: { label: "分析中", color: "bg-blue-100 text-blue-700" },
  memory_updating: { label: "更新记忆", color: "bg-blue-100 text-blue-700" },
  reporting: { label: "生成报告", color: "bg-blue-100 text-blue-700" },
  pending: { label: "等待中", color: "bg-gray-100 text-gray-700" },
  running: { label: "运行中", color: "bg-blue-100 text-blue-700" },
  completed: { label: "已完成", color: "bg-green-100 text-green-700" },
  failed: { label: "失败", color: "bg-red-100 text-red-700" },
};

/** 获取状态配置 */
export function getStatusConfig(status: TaskStatus | WorkflowRunStatus) {
  return statusConfig[status] || statusConfig.created;
}
