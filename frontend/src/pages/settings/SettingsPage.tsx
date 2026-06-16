import { useHealth } from "@/hooks/useHealth";
import { useTools } from "@/hooks/useTools";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Badge } from "@/components/ui/badge";
import { Activity, Database, Server, Cpu, Brain } from "lucide-react";

/** 系统信息卡片 */
function SystemInfoCard({
  title,
  icon: Icon,
  items,
}: {
  title: string;
  icon: React.ElementType;
  items: { label: string; value: string; status?: "ok" | "error" }[];
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Icon className="h-5 w-5" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.label}
              className="flex items-center justify-between"
            >
              <span className="text-sm text-muted-foreground">
                {item.label}
              </span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{item.value}</span>
                {item.status && (
                  <Badge
                    variant={item.status === "ok" ? "default" : "destructive"}
                    className="text-xs"
                  >
                    {item.status === "ok" ? "正常" : "异常"}
                  </Badge>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

/** 设置页面 */
export function SettingsPage() {
  const { data: health, isLoading: healthLoading } = useHealth();
  const { data: tools, isLoading: toolsLoading } = useTools();

  const isLoading = healthLoading || toolsLoading;

  return (
    <div className="page-enter space-y-6">
      {/* 页面标题 */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">设置</h2>
        <p className="text-muted-foreground">系统配置和状态信息</p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner />
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {/* 系统状态 */}
          <SystemInfoCard
            title="系统状态"
            icon={Activity}
            items={[
              {
                label: "后端服务",
                value: health?.status === "ok" ? "运行中" : "离线",
                status: health?.status === "ok" ? "ok" : "error",
              },
              {
                label: "版本",
                value: health?.version || "未知",
              },
            ]}
          />

          {/* 数据库 */}
          <SystemInfoCard
            title="数据库"
            icon={Database}
            items={[
              {
                label: "PostgreSQL",
                value: health?.status === "ok" ? "已连接" : "未知",
                status: health?.status === "ok" ? "ok" : "error",
              },
              {
                label: "Qdrant",
                value: health?.status === "ok" ? "已连接" : "未知",
                status: health?.status === "ok" ? "ok" : "error",
              },
            ]}
          />

          {/* 工具系统 */}
          <SystemInfoCard
            title="工具系统"
            icon={Server}
            items={[
              {
                label: "本地工具",
                value: tools ? `${tools.local_count} 个` : "加载中...",
              },
              {
                label: "MCP 工具",
                value: tools ? `${tools.mcp_count} 个` : "加载中...",
              },
              {
                label: "工具总数",
                value: tools ? `${tools.total} 个` : "加载中...",
              },
            ]}
          />

          {/* 模型配置 */}
          <SystemInfoCard
            title="模型配置"
            icon={Cpu}
            items={[
              { label: "LLM", value: "GPT-4" },
              { label: "Embedding", value: "BAAI/bge-small-zh-v1.5" },
            ]}
          />
        </div>
      )}

      {/* 技术栈 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            技术栈
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <div className="space-y-1">
              <h4 className="text-sm font-medium">后端</h4>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline">FastAPI</Badge>
                <Badge variant="outline">LangGraph</Badge>
                <Badge variant="outline">PydanticAI</Badge>
              </div>
            </div>
            <div className="space-y-1">
              <h4 className="text-sm font-medium">前端</h4>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline">React</Badge>
                <Badge variant="outline">TypeScript</Badge>
                <Badge variant="outline">TailwindCSS</Badge>
              </div>
            </div>
            <div className="space-y-1">
              <h4 className="text-sm font-medium">数据库</h4>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline">PostgreSQL</Badge>
                <Badge variant="outline">Qdrant</Badge>
              </div>
            </div>
            <div className="space-y-1">
              <h4 className="text-sm font-medium">可视化</h4>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline">ReactFlow</Badge>
                <Badge variant="outline">Zustand</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 关于 */}
      <Card>
        <CardHeader>
          <CardTitle>关于</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground space-y-2">
            <p>
              <strong>AI Research OS</strong> - AI 前沿热点研究智能体
            </p>
            <p>
              基于 LangGraph + PydanticAI + FastAPI 构建的 AI Research
              Operating System。
            </p>
            <p>
              支持多 Agent 协作、工具调用、记忆系统、MCP 集成等能力。
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
