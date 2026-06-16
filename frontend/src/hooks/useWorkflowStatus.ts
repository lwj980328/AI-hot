import { useQuery } from "@tanstack/react-query";
import { workflowApi } from "@/api/workflowApi";

/** 工作流状态 Hook - 用于 Workflow 可视化（M7 新增） */
export function useWorkflowStatus(taskId: string) {
  return useQuery({
    queryKey: ["workflowStatus", taskId],
    queryFn: () => workflowApi.getStatus(taskId),
    enabled: !!taskId,
    // 每 3 秒刷新一次，用于跟踪工作流执行状态
    refetchInterval: (query) => {
      const data = query.state.data;
      // 如果任务已完成或失败，停止轮询
      if (data?.task_status === "completed" || data?.task_status === "failed") {
        return false;
      }
      // 否则每 3 秒刷新（任务执行过程中实时获取工具调用记录）
      return 3000;
    },
  });
}
