import apiClient from "./client";
import type { WorkflowRun, RunWorkflowRequest } from "@/types/workflow";

/** 工作流 API */
export const workflowApi = {
  /** 运行工作流 */
  run: async (request: RunWorkflowRequest): Promise<WorkflowRun> => {
    const { data } = await apiClient.post<WorkflowRun>("/workflows/run", request);
    return data;
  },

  /** 获取任务的运行记录 */
  getRuns: async (taskId: string): Promise<WorkflowRun[]> => {
    const { data } = await apiClient.get<WorkflowRun[]>(`/tasks/${taskId}/runs`);
    return data;
  },
};
