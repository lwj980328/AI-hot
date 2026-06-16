import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface NodeOutputCardProps {
  nodeId: string;
  outputSummary: string;
}

/** 解析 JSON 字符串，失败返回 null */
function tryParseJson(str: string): unknown {
  try {
    return JSON.parse(str);
  } catch {
    return null;
  }
}

/** Planner 节点输出 */
function PlannerOutput({ data }: { data: Record<string, unknown> }) {
  return (
    <div className="space-y-2 text-sm">
      <div>
        <span className="text-muted-foreground">研究主题：</span>
        <span className="font-medium">{data.topic as string}</span>
      </div>
      {Array.isArray(data.keywords) && (
        <div>
          <span className="text-muted-foreground">关键词：</span>
          <div className="flex flex-wrap gap-1 mt-1">
            {(data.keywords as string[]).map((kw, i) => (
              <Badge key={i} variant="secondary" className="text-xs">
                {kw}
              </Badge>
            ))}
          </div>
        </div>
      )}
      {Array.isArray(data.data_sources) && (
        <div>
          <span className="text-muted-foreground">数据源：</span>
          <div className="flex flex-wrap gap-1 mt-1">
            {(data.data_sources as string[]).map((ds, i) => (
              <Badge key={i} variant="outline" className="text-xs">
                {ds}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/** Context 节点输出 */
function ContextOutput({ data }: { data: Array<Record<string, unknown>> }) {
  return (
    <div className="space-y-2 text-sm">
      {data.map((item, i) => (
        <Card key={i} className="p-2">
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="secondary" className="text-xs">
              {String(item.type || '')}
            </Badge>
            <span className="font-medium text-xs">{String(item.title || '')}</span>
          </div>
          <p className="text-xs text-muted-foreground line-clamp-2">
            {String(item.content || '')}
          </p>
        </Card>
      ))}
    </div>
  );
}

/** Research 节点输出 */
function ResearchOutput({ data }: { data: Record<string, unknown> }) {
  return (
    <div className="space-y-2 text-sm">
      <div className="flex gap-4">
        <div>
          <span className="text-muted-foreground">论文：</span>
          <span className="font-medium">{Array.isArray(data.papers) ? data.papers.length : 0} 篇</span>
        </div>
        <div>
          <span className="text-muted-foreground">项目：</span>
          <span className="font-medium">{Array.isArray(data.repositories) ? data.repositories.length : 0} 个</span>
        </div>
        <div>
          <span className="text-muted-foreground">模型：</span>
          <span className="font-medium">{Array.isArray(data.models) ? data.models.length : 0} 个</span>
        </div>
      </div>
      {data.search_round !== undefined && (
        <div>
          <span className="text-muted-foreground">搜索轮次：</span>
          <span className="font-medium">{data.search_round as number}</span>
        </div>
      )}
    </div>
  );
}

/** Analysis 节点输出 */
function AnalysisOutput({ data }: { data: Record<string, unknown> }) {
  const hotTopics = Array.isArray(data.hot_topics) ? data.hot_topics as string[] : [];
  const trendSummary = typeof data.trend_summary === 'string' ? data.trend_summary : '';
  const insights = Array.isArray(data.insights) ? data.insights as Array<Record<string, unknown>> : [];

  return (
    <div className="space-y-2 text-sm">
      {hotTopics.length > 0 && (
        <div>
          <span className="text-muted-foreground">热点话题：</span>
          <div className="flex flex-wrap gap-1 mt-1">
            {hotTopics.map((topic, i) => (
              <Badge key={i} variant="secondary" className="text-xs">
                {topic}
              </Badge>
            ))}
          </div>
        </div>
      )}
      {trendSummary && (
        <div>
          <span className="text-muted-foreground">趋势摘要：</span>
          <p className="text-xs text-muted-foreground mt-1">
            {trendSummary}
          </p>
        </div>
      )}
      {insights.length > 0 && (
        <div>
          <span className="text-muted-foreground">洞察：</span>
          <div className="space-y-1 mt-1">
            {insights.map((insight, i) => (
              <div key={i} className="text-xs">
                <span className="font-medium">• {String(insight.title || '')}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/** Memory 节点输出 */
function MemoryOutput({ data }: { data: Record<string, unknown> }) {
  return (
    <div className="space-y-2 text-sm">
      <div>
        <span className="text-muted-foreground">记忆更新：</span>
        <Badge variant={data.memory_updated ? "default" : "secondary"}>
          {data.memory_updated ? "已更新" : "未更新"}
        </Badge>
      </div>
      {Array.isArray(data.memory_ids) && data.memory_ids.length > 0 && (
        <div>
          <span className="text-muted-foreground">写入记忆数：</span>
          <span className="font-medium">{data.memory_ids.length} 条</span>
        </div>
      )}
    </div>
  );
}

/** Report 节点输出 */
function ReportOutput({ data }: { data: Record<string, unknown> }) {
  const title = typeof data.title === 'string' ? data.title : '';
  const summary = typeof data.summary === 'string' ? data.summary : '';
  const contentLength = typeof data.content_length === 'number' ? data.content_length : 0;
  const isFallback = typeof data.is_fallback === 'boolean' ? data.is_fallback : false;

  return (
    <div className="space-y-2 text-sm">
      {title && (
        <div>
          <span className="text-muted-foreground">报告标题：</span>
          <span className="font-medium">{title}</span>
        </div>
      )}
      {summary && (
        <div>
          <span className="text-muted-foreground">执行摘要：</span>
          <p className="text-xs text-muted-foreground mt-1">
            {summary}
          </p>
        </div>
      )}
      <div className="flex gap-4">
        {contentLength > 0 && (
          <div>
            <span className="text-muted-foreground">内容长度：</span>
            <span className="font-medium">{contentLength} 字符</span>
          </div>
        )}
        <div>
          <span className="text-muted-foreground">报告类型：</span>
          <Badge variant={isFallback ? "destructive" : "default"}>
            {isFallback ? "降级报告" : "LLM 生成"}
          </Badge>
        </div>
      </div>
    </div>
  );
}

/** 默认输出（无法解析时显示） */
function DefaultOutput({ raw }: { raw: string }) {
  return (
    <pre className="text-xs text-muted-foreground whitespace-pre-wrap break-all">
      {raw}
    </pre>
  );
}

/** 节点输出卡片组件 */
export function NodeOutputCard({ nodeId, outputSummary }: NodeOutputCardProps) {
  const data = tryParseJson(outputSummary);

  if (!data) {
    return <DefaultOutput raw={outputSummary} />;
  }

  // 根据节点类型渲染不同的输出内容
  switch (nodeId) {
    case "planner":
      return <PlannerOutput data={data as Record<string, unknown>} />;
    case "context":
      return <ContextOutput data={data as Array<Record<string, unknown>>} />;
    case "research":
      return <ResearchOutput data={data as Record<string, unknown>} />;
    case "analysis":
      return <AnalysisOutput data={data as Record<string, unknown>} />;
    case "memory":
      return <MemoryOutput data={data as Record<string, unknown>} />;
    case "report":
      return <ReportOutput data={data as Record<string, unknown>} />;
    default:
      return <DefaultOutput raw={outputSummary} />;
  }
}
