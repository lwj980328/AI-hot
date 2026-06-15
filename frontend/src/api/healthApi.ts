import axios from "axios";
import type { HealthResponse } from "@/types/api";

/** 健康检查 API - 不走 /api/v1 前缀 */
export const healthApi = {
  /** 检查后端健康状态 */
  check: async (): Promise<HealthResponse> => {
    const { data } = await axios.get<HealthResponse>("/health");
    return data;
  },
};
