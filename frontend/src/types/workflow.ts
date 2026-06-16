/** 工作流运行状态 */
export type WorkflowRunStatus = "pending" | "running" | "completed" | "failed";

/** 节点状态 */
export type NodeStatus = "pending" | "running" | "completed" | "failed";

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

/** 工具调用记录 - 与后端 ToolCallRecord 一致 */
export interface ToolCallRecord {
  node_name: string;
  tool_name: string;
  input_params: Record<string, unknown>;
  output_summary: string;
  success: boolean;
  duration_ms: number;
  called_at: string;
}

/** 工作流状态响应 - 与后端 get_workflow_status 返回一致 */
export interface WorkflowStatusResponse {
  task_id: string;
  task_status: string;
  current_node: string;
  node_states: Record<string, NodeStatus>;
  tool_calls?: ToolCallRecord[];
}

/** 节点元数据 */
export interface NodeMeta {
  id: string;
  label: string;
  description: string;
  status: NodeStatus;
  toolCount: number;
}

/** 工作流图节点 */
export interface WorkflowGraphNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: NodeMeta;
}

/** 工作流图边 */
export interface WorkflowGraphEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
  animated?: boolean;
  label?: string;
}
