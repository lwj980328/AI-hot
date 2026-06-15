import apiClient from "./client";
import type { ToolListResponse } from "@/types/tool";

/** 工具 API */
export const toolApi = {
  /** 获取工具列表 */
  list: async (): Promise<ToolListResponse> => {
    const { data } = await apiClient.get<ToolListResponse>("/tools");
    return data;
  },
};
