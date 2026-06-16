import { Brain, TrendingUp, Lightbulb, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/utils/cn";
import type { MemoryItem, MemoryType } from "@/types/memory";

interface MemoryCardProps {
  memory: MemoryItem;
  isSelected?: boolean;
  onClick?: () => void;
}

/** 记忆类型配置 */
const memoryTypeConfig: Record<
  MemoryType,
  { label: string; icon: typeof Brain; color: string }
> = {
  research: {
    label: "研究记忆",
    icon: Brain,
    color: "bg-blue-100 text-blue-700",
  },
  trend: {
    label: "趋势快照",
    icon: TrendingUp,
    color: "bg-green-100 text-green-700",
  },
  insight: {
    label: "洞察记忆",
    icon: Lightbulb,
    color: "bg-yellow-100 text-yellow-700",
  },
};

/** 记忆卡片组件 */
export function MemoryCard({ memory, isSelected, onClick }: MemoryCardProps) {
  const config = memoryTypeConfig[memory.memory_type] || memoryTypeConfig.research;
  const Icon = config.icon;

  // 获取显示标题
  const title =
    memory.report_title || memory.insight_title || memory.topic || "未知主题";

  // 获取显示摘要
  const summary =
    memory.report_summary || memory.insight_description || memory.summary || "";

  // 格式化时间
  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString("zh-CN", {
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div
      className={cn(
        "cursor-pointer rounded-lg border p-4 transition-all hover:shadow-md",
        isSelected
          ? "border-primary bg-primary/5 shadow-sm"
          : "border-border bg-card hover:border-primary/50"
      )}
      onClick={onClick}
    >
      {/* 头部：类型标签 + 相似度 */}
      <div className="mb-2 flex items-center justify-between">
        <Badge variant="secondary" className={cn("text-xs", config.color)}>
          <Icon className="mr-1 h-3 w-3" />
          {config.label}
        </Badge>
        {memory.score > 0 && (
          <span className="text-xs text-muted-foreground">
            {(memory.score * 100).toFixed(0)}% 匹配
          </span>
        )}
      </div>

      {/* 标题 */}
      <h3 className="mb-1 line-clamp-1 text-sm font-medium">{title}</h3>

      {/* 摘要 */}
      <p className="mb-2 line-clamp-2 text-xs text-muted-foreground">
        {summary}
      </p>

      {/* 底部：主题 + 时间 */}
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span className="line-clamp-1 max-w-[60%]">
          主题: {memory.topic}
        </span>
        {memory.created_at && (
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {formatDate(memory.created_at)}
          </span>
        )}
      </div>

      {/* 趋势快照特有：统计数据 */}
      {memory.memory_type === "trend" && memory.hot_topics && (
        <div className="mt-2 flex flex-wrap gap-1">
          {memory.hot_topics.slice(0, 3).map((topic, i) => (
            <Badge key={i} variant="outline" className="text-xs">
              {topic}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}
