import {
  Brain,
  TrendingUp,
  Lightbulb,
  Clock,
  FileText,
  Database,
  BarChart3,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { MemoryItem } from "@/types/memory";

interface MemoryDetailProps {
  memory: MemoryItem;
}

/** 记忆详情组件 */
export function MemoryDetail({ memory }: MemoryDetailProps) {
  // 格式化时间
  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString("zh-CN", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  // 获取类型图标
  const getTypeIcon = () => {
    switch (memory.memory_type) {
      case "research":
        return <Brain className="h-5 w-5 text-blue-500" />;
      case "trend":
        return <TrendingUp className="h-5 w-5 text-green-500" />;
      case "insight":
        return <Lightbulb className="h-5 w-5 text-yellow-500" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  // 获取类型标签
  const getTypeLabel = () => {
    switch (memory.memory_type) {
      case "research":
        return "研究记忆";
      case "trend":
        return "趋势快照";
      case "insight":
        return "洞察记忆";
      default:
        return "未知类型";
    }
  };

  return (
    <div className="space-y-4">
      {/* 头部信息 */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          {getTypeIcon()}
          <Badge variant="secondary">{getTypeLabel()}</Badge>
        </div>
        {memory.created_at && (
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            {formatDate(memory.created_at)}
          </div>
        )}
      </div>

      {/* 主题 */}
      <div>
        <h2 className="text-lg font-semibold">
          {memory.report_title || memory.insight_title || memory.topic}
        </h2>
        <p className="text-sm text-muted-foreground">主题: {memory.topic}</p>
      </div>

      {/* 摘要 */}
      <Card className="p-4">
        <h3 className="mb-2 flex items-center gap-2 text-sm font-medium">
          <FileText className="h-4 w-4" />
          摘要
        </h3>
        <p className="text-sm text-muted-foreground">
          {memory.report_summary || memory.insight_description || memory.summary}
        </p>
      </Card>

      {/* Research Memory 特有：报告内容 */}
      {memory.memory_type === "research" && memory.report_summary && (
        <Card className="p-4">
          <h3 className="mb-2 flex items-center gap-2 text-sm font-medium">
            <FileText className="h-4 w-4" />
            研究报告摘要
          </h3>
          <p className="text-sm text-muted-foreground">{memory.report_summary}</p>
        </Card>
      )}

      {/* Trend Snapshot 特有：统计数据 */}
      {memory.memory_type === "trend" && (
        <Card className="p-4">
          <h3 className="mb-3 flex items-center gap-2 text-sm font-medium">
            <BarChart3 className="h-4 w-4" />
            趋势数据
          </h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {memory.project_count !== undefined && (
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {memory.project_count}
                </div>
                <div className="text-xs text-muted-foreground">项目数</div>
              </div>
            )}
            {memory.paper_count !== undefined && (
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {memory.paper_count}
                </div>
                <div className="text-xs text-muted-foreground">论文数</div>
              </div>
            )}
            {memory.model_count !== undefined && (
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {memory.model_count}
                </div>
                <div className="text-xs text-muted-foreground">模型数</div>
              </div>
            )}
            {memory.confidence_score !== undefined && (
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {(memory.confidence_score * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-muted-foreground">置信度</div>
              </div>
            )}
          </div>

          {/* 热门话题 */}
          {memory.hot_topics && memory.hot_topics.length > 0 && (
            <div className="mt-4">
              <h4 className="mb-2 text-xs font-medium text-muted-foreground">
                热门话题
              </h4>
              <div className="flex flex-wrap gap-2">
                {memory.hot_topics.map((topic, i) => (
                  <Badge key={i} variant="outline">
                    {topic}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Insight Memory 特有：证据 */}
      {memory.memory_type === "insight" && memory.evidences && memory.evidences.length > 0 && (
        <Card className="p-4">
          <h3 className="mb-3 flex items-center gap-2 text-sm font-medium">
            <Database className="h-4 w-4" />
            证据链
          </h3>
          <div className="space-y-3">
            {memory.evidences.map((evidence, i) => (
              <div key={i} className="rounded-md border p-3">
                <p className="text-sm">{evidence.statement}</p>
                <div className="mt-2 flex items-center gap-2">
                  <Badge variant="secondary" className="text-xs">
                    置信度: {(evidence.confidence * 100).toFixed(0)}%
                  </Badge>
                  {evidence.source_ids.length > 0 && (
                    <span className="text-xs text-muted-foreground">
                      来源: {evidence.source_ids.length} 个
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* 来源信息 */}
      {memory.source_ids && memory.source_ids.length > 0 && (
        <Card className="p-4">
          <h3 className="mb-2 flex items-center gap-2 text-sm font-medium">
            <Database className="h-4 w-4" />
            数据来源
          </h3>
          <div className="flex flex-wrap gap-2">
            {memory.source_ids.map((sourceId, i) => (
              <Badge key={i} variant="outline" className="text-xs">
                {sourceId}
              </Badge>
            ))}
          </div>
        </Card>
      )}

      {/* 相似度分数 */}
      {memory.score > 0 && (
        <div className="text-center text-sm text-muted-foreground">
          相似度: {(memory.score * 100).toFixed(1)}%
        </div>
      )}
    </div>
  );
}
