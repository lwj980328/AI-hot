import { useState } from "react";
import { useTasks, useDeleteTask } from "@/hooks/useTasks";
import { useHealth } from "@/hooks/useHealth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { TaskForm } from "@/features/research/TaskForm";
import { formatRelativeTime } from "@/utils/format";
import { useNavigate } from "react-router-dom";
import {
  ClipboardList,
  CheckCircle,
  Activity,
  Trash2,
} from "lucide-react";

/** 统计卡片组件 */
function StatCard({
  title,
  value,
  icon: Icon,
  loading,
}: {
  title: string;
  value: string | number;
  icon: React.ElementType;
  loading?: boolean;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        {loading ? (
          <LoadingSpinner size={20} />
        ) : (
          <div className="text-2xl font-bold">{value}</div>
        )}
      </CardContent>
    </Card>
  );
}

/** Dashboard 页面 */
export function DashboardPage() {
  // 获取最近 100 条任务用于统计
  const { data: tasks, isLoading: tasksLoading } = useTasks(100);
  const { data: health, isLoading: healthLoading } = useHealth();
  const navigate = useNavigate();
  const deleteTask = useDeleteTask();
  const [deletingTaskId, setDeletingTaskId] = useState<string | null>(null);

  // 删除任务
  const handleDeleteTask = async (taskId: string, e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止冒泡，避免触发卡片点击
    if (!confirm("确定要删除这个任务吗？")) return;
    setDeletingTaskId(taskId);
    try {
      await deleteTask.mutateAsync(taskId);
    } catch (error) {
      console.error("删除任务失败:", error);
    } finally {
      setDeletingTaskId(null);
    }
  };

  // 统计数据
  const totalTasks = tasks?.length ?? 0;
  const completedTasks = tasks?.filter((t) => t.status === "completed").length ?? 0;
  const isHealthy = health?.status === "ok";

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">
          AI 前沿热点研究智能体 - 系统概览
        </p>
      </div>

      {/* 快速创建 */}
      <Card>
        <CardHeader>
          <CardTitle>快速研究</CardTitle>
        </CardHeader>
        <CardContent>
          <TaskForm />
        </CardContent>
      </Card>

      {/* 统计卡片 */}
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          title="总任务数"
          value={totalTasks}
          icon={ClipboardList}
          loading={tasksLoading}
        />
        <StatCard
          title="已完成"
          value={completedTasks}
          icon={CheckCircle}
          loading={tasksLoading}
        />
        <StatCard
          title="系统状态"
          value={isHealthy ? "正常" : "离线"}
          icon={Activity}
          loading={healthLoading}
        />
      </div>

      {/* 最近任务 */}
      <Card>
        <CardHeader>
          <CardTitle>最近任务</CardTitle>
        </CardHeader>
        <CardContent>
          {tasksLoading ? (
            <div className="flex justify-center py-8">
              <LoadingSpinner />
            </div>
          ) : tasks && tasks.length > 0 ? (
            <div className="space-y-3">
              {tasks.slice(0, 5).map((task) => (
                <div
                  key={task.id}
                  className="flex items-center justify-between rounded-lg border p-3 cursor-pointer hover:bg-accent"
                  onClick={() => navigate(`/research?task=${task.id}`)}
                >
                  <div className="flex-1">
                    <p className="font-medium">{task.task_name}</p>
                    <p className="text-sm text-muted-foreground">
                      {formatRelativeTime(task.created_at)}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={task.status} />
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-muted-foreground hover:text-destructive"
                      onClick={(e) => handleDeleteTask(task.id, e)}
                      disabled={deletingTaskId === task.id}
                    >
                      {deletingTaskId === task.id ? (
                        <LoadingSpinner className="h-4 w-4" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">
              暂无任务，创建你的第一个研究任务
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
