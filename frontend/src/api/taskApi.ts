import apiClient from "./client";
import type { Task, CreateTaskRequest } from "@/types/task";

/** 任务 API */
export const taskApi = {
  /** 创建研究任务 */
  create: async (request: CreateTaskRequest): Promise<Task> => {
    const { data } = await apiClient.post<Task>("/tasks", request);
    return data;
  },

  /** 获取任务列表 */
  list: async (limit = 20, offset = 0): Promise<Task[]> => {
    const { data } = await apiClient.get<Task[]>("/tasks", {
      params: { limit, offset },
    });
    return data;
  },

  /** 获取任务详情 */
  get: async (taskId: string): Promise<Task> => {
    const { data } = await apiClient.get<Task>(`/tasks/${taskId}`);
    return data;
  },

  /** 删除任务 */
  delete: async (taskId: string): Promise<void> => {
    await apiClient.delete(`/tasks/${taskId}`);
  },
};
