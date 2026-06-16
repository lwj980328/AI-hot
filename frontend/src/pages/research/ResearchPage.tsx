import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useTasks, useTask, useCreateTask, useDeleteTask } from "@/hooks/useTasks";
import { useRunWorkflow } from "@/hooks/useWorkflows";
import { useWorkflowStatus } from "@/hooks/useWorkflowStatus";
import { useReportByTask } from "@/hooks/useReports";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { TaskForm } from "@/features/research/TaskForm";
import { TaskList } from "@/features/research/TaskList";
import { WorkflowCanvas } from "@/features/workflow/WorkflowCanvas";
import { formatDateTime } from "@/utils/format";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  FileText,
  ArrowLeft,
  FlaskConical,
  GitBranch,
  Play,
  RefreshCw,
} from "lucide-react";

/** Research 页面 */
export function ResearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const activeTaskId = searchParams.get("task");
  const [deletingTaskId, setDeletingTaskId] = useState<string | null>(null);

  const { data: tasks, isLoading: tasksLoading } = useTasks(50);
  const { data: activeTask } = useTask(activeTaskId || "");
  const { data: workflowStatus } = useWorkflowStatus(activeTaskId || "");
  // 只在任务完成后才请求报告
  const { data: report, isLoading: reportLoading } = useReportByTask(
    activeTask?.status === "completed" ? activeTaskId || "" : ""
  );
  const runWorkflow = useRunWorkflow();
  const createTask = useCreateTask();
  const deleteTask = useDeleteTask();

  const handleBack = () => {
    setSearchParams({});
  };

  // 删除任务
  const handleDeleteTask = async (taskId: string) => {
    if (!confirm("确定要删除这个任务吗？")) return;
    setDeletingTaskId(taskId);
    try {
      await deleteTask.mutateAsync(taskId);
      // 如果删除的是当前选中的任务，清除选中
      if (activeTaskId === taskId) {
        handleBack();
      }
    } catch (error) {
      console.error("删除任务失败:", error);
    } finally {
      setDeletingTaskId(null);
    }
  };

  // 重新研究
  const handleRerun = async () => {
    if (!activeTask) return;
    try {
      const newTask = await createTask.mutateAsync({
        user_query: activeTask.user_query,
        task_name: activeTask.task_name,
      });
      navigate(`/research?task=${newTask.id}`, { replace: true });
    } catch (error) {
      console.error("创建任务失败:", error);
    }
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

        {/* 操作按钮区域 */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              {/* 未完成的任务：继续完成按钮 */}
              {activeTask.status === "created" && (
                <Button
                  onClick={() => runWorkflow.mutate({ task_id: activeTaskId! })}
                  disabled={runWorkflow.isPending}
                >
                  {runWorkflow.isPending ? (
                    <>
                      <LoadingSpinner className="mr-2 h-4 w-4" />
                      启动中...
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-4 w-4" />
                      开始研究
                    </>
                  )}
                </Button>
              )}

              {/* 运行中的任务：显示状态 */}
              {["planning", "context_loading", "researching", "analyzing", "memory_updating", "reporting"].includes(activeTask.status) && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <LoadingSpinner className="h-4 w-4" />
                  <span>工作流执行中...</span>
                </div>
              )}

              {/* 已完成或失败的任务：重新研究按钮 */}
              {["completed", "failed"].includes(activeTask.status) && (
                <Button onClick={handleRerun} disabled={createTask.isPending}>
                  {createTask.isPending ? (
                    <>
                      <LoadingSpinner className="mr-2 h-4 w-4" />
                      创建中...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      重新研究
                    </>
                  )}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* 工作流可视化 */}
        {workflowStatus && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="h-5 w-5" />
                工作流执行状态
              </CardTitle>
            </CardHeader>
            <CardContent>
              <WorkflowCanvas
                nodeStates={workflowStatus.node_states}
                toolCalls={workflowStatus.tool_calls || []}
                nodeLogs={workflowStatus.node_logs || []}
              />
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
          <TaskList
            tasks={tasks || []}
            isLoading={tasksLoading}
            onDelete={handleDeleteTask}
            deletingId={deletingTaskId}
          />
        </CardContent>
      </Card>
    </div>
  );
}
