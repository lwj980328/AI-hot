import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { workflowApi } from "@/api/workflowApi";
import type { RunWorkflowRequest } from "@/types/workflow";

/** 运行工作流 Hook */
export function useRunWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: RunWorkflowRequest) => workflowApi.run(request),
    onSuccess: () => {
      // 运行成功后刷新任务列表
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}

/** 任务运行记录 Hook */
export function useWorkflowRuns(taskId: string) {
  return useQuery({
    queryKey: ["workflowRuns", taskId],
    queryFn: () => workflowApi.getRuns(taskId),
    enabled: !!taskId,
  });
}
