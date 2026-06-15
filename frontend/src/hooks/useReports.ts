import { useQuery } from "@tanstack/react-query";
import { reportApi } from "@/api/reportApi";

/** 报告详情 Hook */
export function useReport(reportId: string) {
  return useQuery({
    queryKey: ["report", reportId],
    queryFn: () => reportApi.get(reportId),
    enabled: !!reportId,
  });
}

/** 根据任务获取报告 Hook */
export function useReportByTask(taskId: string) {
  return useQuery({
    queryKey: ["report", "task", taskId],
    queryFn: () => reportApi.getByTask(taskId),
    enabled: !!taskId,
  });
}
