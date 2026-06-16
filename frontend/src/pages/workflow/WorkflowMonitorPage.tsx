import { useSearchParams } from "react-router-dom";
import { useTasks, useTask } from "@/hooks/useTasks";
import { useWorkflowStatus } from "@/hooks/useWorkflowStatus";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { EmptyState } from "@/components/shared/EmptyState";
import { WorkflowCanvas } from "@/features/workflow/WorkflowCanvas";
import { formatDateTime } from "@/utils/format";
import { TaskList } from "@/features/research/TaskList";
import {
  GitBranch,
  ArrowLeft,
} from "lucide-react";
import { Button } from "@/components/ui/button";

/** Workflow Monitor 页面 */
export function WorkflowMonitorPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTaskId = searchParams.get("task");

  const { data: tasks, isLoading: tasksLoading } = useTasks(50);
  const { data: activeTask } = useTask(activeTaskId || "");
  const { data: workflowStatus, isLoading: statusLoading } =
    useWorkflowStatus(activeTaskId || "");

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

        {/* Workflow 可视化 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GitBranch className="h-5 w-5" />
              工作流执行状态
            </CardTitle>
          </CardHeader>
          <CardContent>
            {statusLoading ? (
              <div className="flex justify-center py-12">
                <LoadingSpinner />
              </div>
            ) : workflowStatus ? (
              <WorkflowCanvas
                nodeStates={workflowStatus.node_states}
                toolCalls={workflowStatus.tool_calls || []}
              />
            ) : (
              <EmptyState
                title="无法获取工作流状态"
                description="请稍后重试"
                icon={<GitBranch size={48} />}
              />
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  // 任务列表视图
  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">
          Workflow Monitor
        </h2>
        <p className="text-muted-foreground">
          选择一个任务查看工作流执行状态
        </p>
      </div>

      {/* 任务列表 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GitBranch className="h-5 w-5" />
            任务列表
          </CardTitle>
        </CardHeader>
        <CardContent>
          <TaskList tasks={tasks || []} isLoading={tasksLoading} />
        </CardContent>
      </Card>
    </div>
  );
}
