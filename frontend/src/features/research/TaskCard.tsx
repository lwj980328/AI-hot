import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { formatRelativeTime } from "@/utils/format";
import type { Task } from "@/types/task";

interface TaskCardProps {
  task: Task;
}

/** 任务卡片组件 */
export function TaskCard({ task }: TaskCardProps) {
  const navigate = useNavigate();

  return (
    <Card
      className="cursor-pointer transition-colors hover:bg-accent"
      onClick={() => navigate(`/research?task=${task.id}`)}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-medium">{task.task_name}</h3>
            <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
              {task.user_query}
            </p>
          </div>
          <StatusBadge status={task.status} />
        </div>
        <div className="mt-3 text-xs text-muted-foreground">
          {formatRelativeTime(task.created_at)}
        </div>
      </CardContent>
    </Card>
  );
}
