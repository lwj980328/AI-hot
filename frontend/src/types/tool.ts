/** 工具类型 */
export type ToolType = "local" | "mcp";

/** 工具元数据 */
export interface ToolMetadata {
  name: string;
  description: string;
  type: ToolType;
  input_schema: Record<string, unknown>;
}

/** 工具列表响应 */
export interface ToolListResponse {
  total: number;
  local_count: number;
  mcp_count: number;
  tools: ToolMetadata[];
}
