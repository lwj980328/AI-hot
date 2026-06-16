import { useQuery } from "@tanstack/react-query";
import { memoryApi } from "@/api/memoryApi";

/** 记忆搜索 Hook */
export function useMemorySearch(query: string, options?: { topic?: string; limit?: number }) {
  return useQuery({
    queryKey: ["memories", "search", query, options],
    queryFn: () => memoryApi.search(query, options),
    enabled: !!query,
    // 搜索结果不自动刷新
    refetchInterval: false,
  });
}

/** 记忆列表 Hook */
export function useMemories(options?: {
  memoryType?: string;
  topic?: string;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["memories", "list", options],
    queryFn: () => memoryApi.list(options),
    // 每 30 秒刷新一次
    refetchInterval: 30000,
  });
}

/** 记忆统计 Hook */
export function useMemoryStats() {
  return useQuery({
    queryKey: ["memories", "stats"],
    queryFn: () => memoryApi.getStats(),
    // 每 30 秒刷新一次
    refetchInterval: 30000,
  });
}
