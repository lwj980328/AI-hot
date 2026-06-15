import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCreateTask } from "@/hooks/useTasks";
import { useRunWorkflow } from "@/hooks/useWorkflows";
import { Loader2, Search } from "lucide-react";

/** 任务创建表单 */
export function TaskForm() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const createTask = useCreateTask();
  const runWorkflow = useRunWorkflow();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      // 创建任务
      const task = await createTask.mutateAsync({
        user_query: query,
        task_name: query,
      });

      // 异步触发工作流（不等待结果）
      runWorkflow.mutate({ task_id: task.id });

      // 立即跳转到研究页面（不等待工作流完成）
      // 使用 replace 防止用户返回到表单页面
      navigate(`/research?task=${task.id}`, { replace: true });
    } catch (error) {
      console.error("创建任务失败:", error);
    }
  };

  const isLoading = createTask.isPending || runWorkflow.isPending;

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="输入研究主题，例如：MCP 生态发展趋势"
          className="pl-9"
          disabled={isLoading}
        />
      </div>
      <Button type="submit" disabled={isLoading || !query.trim()}>
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            创建中...
          </>
        ) : (
          "开始研究"
        )}
      </Button>
    </form>
  );
}
