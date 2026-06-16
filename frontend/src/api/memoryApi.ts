import apiClient from "./client";
import type { MemorySearchResponse, MemoryStats } from "@/types/memory";

/** 记忆 API */
export const memoryApi = {
  /** 语义搜索记忆 */
  search: async (
    query: string,
    options?: { topic?: string; limit?: number }
  ): Promise<MemorySearchResponse> => {
    const { data } = await apiClient.get<MemorySearchResponse>("/memories/search", {
      params: {
        q: query,
        topic: options?.topic,
        limit: options?.limit || 5,
      },
    });
    return data;
  },

  /** 获取记忆列表 */
  list: async (options?: {
    memoryType?: string;
    topic?: string;
    limit?: number;
  }): Promise<MemorySearchResponse> => {
    const { data } = await apiClient.get<MemorySearchResponse>("/memories", {
      params: {
        memory_type: options?.memoryType,
        topic: options?.topic,
        limit: options?.limit || 20,
      },
    });
    return data;
  },

  /** 获取记忆统计 */
  getStats: async (): Promise<MemoryStats> => {
    const { data } = await apiClient.get<MemoryStats>("/memories/stats");
    return data;
  },
};
