/** 统一 API 响应结构 */
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
