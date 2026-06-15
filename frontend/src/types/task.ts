/** 任务状态 - 与后端 TaskStatus 枚举一致 */
export type TaskStatus =
  | "created"
  | "planning"
  | "context_loading"
  | "researching"
  | "analyzing"
  | "memory_updating"
  | "reporting"
  | "completed"
  | "failed";

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
