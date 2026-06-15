import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { taskApi } from "@/api/taskApi";
import type { CreateTaskRequest } from "@/types/task";

/** 任务列表 Hook */
export function useTasks(limit = 20, offset = 0) {
  return useQuery({
    queryKey: ["tasks", limit, offset],
    queryFn: () => taskApi.list(limit, offset),
  });
}

/** 任务详情 Hook */
export function useTask(taskId: string) {
  return useQuery({
    queryKey: ["task", taskId],
    queryFn: () => taskApi.get(taskId),
    enabled: !!taskId,
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
