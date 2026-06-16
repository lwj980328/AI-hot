import { useQuery } from "@tanstack/react-query";
import { toolApi } from "@/api/toolApi";

/** 工具列表 Hook */
export function useTools() {
  return useQuery({
    queryKey: ["tools"],
    queryFn: () => toolApi.list(),
    // 每 60 秒刷新一次
    refetchInterval: 60000,
  });
}
