/** 工作流运行状态 */
export type WorkflowRunStatus = "pending" | "running" | "completed" | "failed";

/** 触发类型 */
export type TriggerType = "manual" | "scheduled" | "auto";

/** 工作流运行记录 */
export interface WorkflowRun {
  id: string;
  task_id: string;
  run_number: number;
  trigger_type: TriggerType;
  status: WorkflowRunStatus;
  started_at: string;
  finished_at: string | null;
  error_message: string | null;
}

/** 运行工作流请求 */
export interface RunWorkflowRequest {
  task_id: string;
}
