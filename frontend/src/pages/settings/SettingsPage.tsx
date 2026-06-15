import { useHealth } from "@/hooks/useHealth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Badge } from "@/components/ui/badge";
import { Activity, Database, Server, Cpu } from "lucide-react";

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
  const { data: health, isLoading } = useHealth();

  return (
    <div className="space-y-6">
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
              { label: "PostgreSQL", value: "已连接" },
              { label: "Qdrant", value: "已连接" },
            ]}
          />

          {/* 工具系统 */}
          <SystemInfoCard
            title="工具系统"
            icon={Server}
            items={[
              { label: "本地工具", value: "4 个" },
              { label: "MCP 工具", value: "14 个" },
            ]}
          />

          {/* 模型配置 */}
          <SystemInfoCard
            title="模型配置"
            icon={Cpu}
            items={[
              { label: "LLM", value: "GPT-4" },
              { label: "Embedding", value: "text-embedding-3-small" },
            ]}
          />
        </div>
      )}

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
