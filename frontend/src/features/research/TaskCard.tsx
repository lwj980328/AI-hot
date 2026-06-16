import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { formatRelativeTime } from "@/utils/format";
import { Trash2 } from "lucide-react";
import type { Task } from "@/types/task";

interface TaskCardProps {
  task: Task;
  onDelete?: (taskId: string) => void;
  isDeleting?: boolean;
}

/** 任务卡片组件 */
export function TaskCard({ task, onDelete, isDeleting }: TaskCardProps) {
  const navigate = useNavigate();

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止冒泡，避免触发卡片点击
    onDelete?.(task.id);
  };

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
          <div className="flex items-center gap-2">
            <StatusBadge status={task.status} />
            {onDelete && (
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-muted-foreground hover:text-destructive"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                {isDeleting ? (
                  <LoadingSpinner className="h-4 w-4" />
                ) : (
                  <Trash2 className="h-4 w-4" />
                )}
              </Button>
            )}
          </div>
        </div>
        <div className="mt-3 text-xs text-muted-foreground">
          {formatRelativeTime(task.created_at)}
        </div>
      </CardContent>
    </Card>
  );
}
