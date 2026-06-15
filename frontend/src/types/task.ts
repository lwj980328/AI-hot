/** 任务状态 */
export type TaskStatus = "pending" | "running" | "completed" | "failed";

/** 任务类型 */
export type TaskType = "research" | "daily" | "trend" | "adhoc";

/** 任务响应 */
export interface Task {
  id: string;
  task_name: string;
  user_query: string;
  task_type: TaskType;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
}

/** 创建任务请求 */
export interface CreateTaskRequest {
  task_name?: string;
  user_query: string;
}
