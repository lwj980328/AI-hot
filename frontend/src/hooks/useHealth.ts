import { useQuery } from "@tanstack/react-query";
import { healthApi } from "@/api/healthApi";

/** 健康检查 Hook */
export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: healthApi.check,
    // 每 30 秒检查一次
    refetchInterval: 30000,
    // 失败时不重试
    retry: false,
  });
}
