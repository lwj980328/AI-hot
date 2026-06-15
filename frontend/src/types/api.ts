/** 统一 API 响应结构 - 与后端一致 */
export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T | null;
}

/** 健康检查响应 */
export interface HealthResponse {
  status: string;
  version: string;
}

/** 分页数据 */
export interface PaginatedData<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}
