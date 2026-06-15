import apiClient from "./client";
import type { Report } from "@/types/report";

/** 报告 API */
export const reportApi = {
  /** 获取报告详情 */
  get: async (reportId: string): Promise<Report> => {
    const { data } = await apiClient.get<Report>(`/reports/${reportId}`);
    return data;
  },

  /** 根据任务 ID 获取报告 */
  getByTask: async (taskId: string): Promise<Report> => {
    const { data } = await apiClient.get<Report>(`/reports/by-task/${taskId}`);
    return data;
  },
};
