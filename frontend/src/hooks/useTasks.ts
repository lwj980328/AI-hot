import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { taskApi } from "@/api/taskApi";
import type { CreateTaskRequest } from "@/types/task";

/** 任务列表 Hook */
export function useTasks(limit = 50, offset = 0) {
  return useQuery({
    queryKey: ["tasks", limit, offset],
    queryFn: () => taskApi.list(limit, offset),
    // 每 10 秒刷新一次任务列表
    refetchInterval: 10000,
    // 窗口获得焦点时刷新
    refetchOnWindowFocus: true,
  });
}

/** 任务详情 Hook */
export function useTask(taskId: string) {
  return useQuery({
    queryKey: ["task", taskId],
    queryFn: () => taskApi.get(taskId),
    enabled: !!taskId,
    // 每 5 秒刷新一次，用于跟踪任务状态
    refetchInterval: (query) => {
      const data = query.state.data;
      // 如果任务已完成或失败，停止轮询
      if (data?.status === "completed" || data?.status === "failed") {
        return false;
      }
      // 否则每 5 秒刷新
      return 5000;
    },
  });
}

/** 创建任务 Hook */
export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateTaskRequest) => taskApi.create(request),
    onSuccess: () => {
      // 创建成功后刷新任务列表
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}
