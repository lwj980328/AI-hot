import { useState } from "react";
import { useTasks } from "@/hooks/useTasks";
import { useReportByTask } from "@/hooks/useReports";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { EmptyState } from "@/components/shared/EmptyState";
import { ReportViewer } from "@/features/reports/ReportViewer";
import { formatRelativeTime } from "@/utils/format";
import { FileText } from "lucide-react";
import type { Task } from "@/types/task";

/** 报告列表页面 */
export function ReportListPage() {
  const { data: tasks, isLoading: tasksLoading } = useTasks(50);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  // 只显示已完成的任务（有报告）
  const completedTasks = tasks?.filter((t) => t.status === "completed") || [];

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">研究报告</h2>
        <p className="text-muted-foreground">浏览历史研究报告</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[300px_1fr]">
        {/* 左侧：报告列表 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">报告列表</CardTitle>
          </CardHeader>
          <CardContent>
            {tasksLoading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner />
              </div>
            ) : completedTasks.length === 0 ? (
              <EmptyState
                title="暂无报告"
                description="完成研究任务后将生成报告"
                icon={<FileText size={32} />}
              />
            ) : (
              <div className="space-y-2">
                {completedTasks.map((task) => (
                  <div
                    key={task.id}
                    className={`flex items-center justify-between rounded-lg border p-3 cursor-pointer transition-colors ${
                      selectedTask?.id === task.id
                        ? "bg-accent border-primary"
                        : "hover:bg-accent"
                    }`}
                    onClick={() => setSelectedTask(task)}
                  >
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{task.task_name}</p>
                      <p className="text-xs text-muted-foreground">
                        {formatRelativeTime(task.updated_at)}
                      </p>
                    </div>
                    <StatusBadge status={task.status} />
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* 右侧：报告内容 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              {selectedTask ? selectedTask.task_name : "报告预览"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedTask ? (
              <ReportContent taskId={selectedTask.id} />
            ) : (
              <EmptyState
                title="选择报告"
                description="从左侧列表中选择一份报告查看"
                icon={<FileText size={48} />}
              />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

/** 报告内容组件 */
function ReportContent({ taskId }: { taskId: string }) {
  const { data: report, isLoading } = useReportByTask(taskId);

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner />
      </div>
    );
  }

  if (!report) {
    return (
      <EmptyState
        title="报告未找到"
        description="该任务的报告可能尚未生成"
      />
    );
  }

  return <ReportViewer report={report} isLoading={false} />;
}
