import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useTasks, useTask } from "@/hooks/useTasks";
import { useRunWorkflow, useWorkflowRuns } from "@/hooks/useWorkflows";
import { useReportByTask } from "@/hooks/useReports";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { TaskForm } from "@/features/research/TaskForm";
import { TaskList } from "@/features/research/TaskList";
import { formatDateTime } from "@/utils/format";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  FileText,
  ArrowLeft,
  FlaskConical,
} from "lucide-react";

/** Research 页面 */
export function ResearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTaskId = searchParams.get("task");

  const { data: tasks, isLoading: tasksLoading } = useTasks(50);
  const { data: activeTask } = useTask(activeTaskId || "");
  const { data: workflowRuns } = useWorkflowRuns(activeTaskId || "");
  // 只在任务完成后才请求报告
  const { data: report, isLoading: reportLoading } = useReportByTask(
    activeTask?.status === "completed" ? activeTaskId || "" : ""
  );
  const runWorkflow = useRunWorkflow();

  // 如果任务状态是 created 且没有运行记录，自动触发工作流
  useEffect(() => {
    if (activeTask?.status === "created" && workflowRuns && workflowRuns.length === 0 && !runWorkflow.isPending) {
      runWorkflow.mutate({ task_id: activeTaskId! });
    }
  }, [activeTask?.status, workflowRuns, activeTaskId]);

  const handleBack = () => {
    setSearchParams({});
  };

  // 任务详情视图
  if (activeTaskId && activeTask) {
    return (
      <div className="space-y-6">
        {/* 返回按钮和标题 */}
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={handleBack}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div className="flex-1">
            <h2 className="text-2xl font-bold tracking-tight">
              {activeTask.task_name}
            </h2>
            <p className="text-muted-foreground">
              创建于 {formatDateTime(activeTask.created_at)}
            </p>
          </div>
          <StatusBadge status={activeTask.status} />
        </div>

        {/* 查询内容 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">研究主题</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{activeTask.user_query}</p>
          </CardContent>
        </Card>

        {/* 运行中状态 - 包括所有中间状态 */}
        {["created", "planning", "context_loading", "researching", "analyzing", "memory_updating", "reporting"].includes(activeTask.status) && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <LoadingSpinner />
                <div>
                  <p className="font-medium">工作流运行中...</p>
                  <p className="text-sm text-muted-foreground">
                    当前阶段：<StatusBadge status={activeTask.status} />
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 报告展示 - 任务完成后显示 */}
        {activeTask.status === "completed" && report && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                {report.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {report.markdown_content}
                </ReactMarkdown>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 加载报告中 */}
        {activeTask.status === "completed" && !report && reportLoading && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <LoadingSpinner />
                <p>加载报告中...</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    );
  }

  // 任务列表视图
  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">研究工作台</h2>
        <p className="text-muted-foreground">
          创建研究任务，执行深度分析
        </p>
      </div>

      {/* 创建任务表单 */}
      <Card>
        <CardHeader>
          <CardTitle>新建研究</CardTitle>
        </CardHeader>
        <CardContent>
          <TaskForm />
        </CardContent>
      </Card>

      {/* 任务历史 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FlaskConical className="h-5 w-5" />
            任务历史
          </CardTitle>
        </CardHeader>
        <CardContent>
          <TaskList tasks={tasks || []} isLoading={tasksLoading} />
        </CardContent>
      </Card>
    </div>
  );
}
