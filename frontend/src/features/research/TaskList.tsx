import { TaskCard } from "./TaskCard";
import { EmptyState } from "@/components/shared/EmptyState";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { ClipboardList } from "lucide-react";
import type { Task } from "@/types/task";

interface TaskListProps {
  tasks: Task[];
  isLoading: boolean;
}

/** 任务列表组件 */
export function TaskList({ tasks, isLoading }: TaskListProps) {
  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <LoadingSpinner />
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <EmptyState
        title="暂无任务"
        description="创建你的第一个研究任务"
        icon={<ClipboardList size={48} />}
      />
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  );
}
