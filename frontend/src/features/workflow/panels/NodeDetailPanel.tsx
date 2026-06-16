import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ToolCallCard } from "./ToolCallCard";
import { NodeOutputCard } from "./NodeOutputCard";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { EmptyState } from "@/components/shared/EmptyState";
import {
  X,
  CheckCircle,
  XCircle,
  Clock,
  Wrench,
  FileOutput,
} from "lucide-react";
import type { NodeStatus, ToolCallRecord, NodeExecutionLog } from "@/types/workflow";

interface NodeDetailPanelProps {
  nodeLabel: string;
  nodeDescription: string;
  nodeId: string;
  status: NodeStatus;
  toolCalls: ToolCallRecord[];
  nodeLog?: NodeExecutionLog;
  onClose: () => void;
}

/** 节点状态图标 */
function StatusIcon({ status }: { status: NodeStatus }) {
  switch (status) {
    case "running":
      return <LoadingSpinner size={16} className="text-blue-500" />;
    case "completed":
      return <CheckCircle size={16} className="text-green-500" />;
    case "failed":
      return <XCircle size={16} className="text-red-500" />;
    case "pending":
    default:
      return <Clock size={16} className="text-gray-400" />;
  }
}

/** 节点状态文本 */
const statusText: Record<NodeStatus, string> = {
  pending: "等待中",
  running: "运行中",
  completed: "已完成",
  failed: "失败",
};

/** 节点详情面板 */
export function NodeDetailPanel({
  nodeLabel,
  nodeDescription,
  nodeId,
  status,
  toolCalls,
  nodeLog,
  onClose,
}: NodeDetailPanelProps) {
  // 判断是否为 Research 节点（有工具调用）
  const isResearchNode = nodeId === "research";

  return (
    <Card className="w-full max-w-md max-h-[80vh] overflow-hidden flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <StatusIcon status={status} />
            {nodeLabel}
          </CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X size={16} />
          </Button>
        </div>
        <p className="text-sm text-muted-foreground">{nodeDescription}</p>
        <div className="flex items-center gap-2">
          <Badge
            variant="outline"
            className={
              status === "completed"
                ? "bg-green-50 text-green-700"
                : status === "running"
                ? "bg-blue-50 text-blue-700"
                : status === "failed"
                ? "bg-red-50 text-red-700"
                : ""
            }
          >
            {statusText[status]}
          </Badge>
          {nodeLog && nodeLog.duration_ms > 0 && (
            <Badge variant="secondary">
              {(nodeLog.duration_ms / 1000).toFixed(1)}s
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="overflow-y-auto flex-1">
        {/* 节点输出摘要 */}
        {nodeLog && (
          <div className="space-y-3 mb-4">
            <div className="flex items-center gap-2 text-sm font-medium">
              <FileOutput size={14} />
              <span>节点输出</span>
            </div>
            <NodeOutputCard nodeId={nodeId} outputSummary={nodeLog.output_summary} />
          </div>
        )}

        {/* 工具调用列表（仅 Research 节点显示） */}
        {isResearchNode && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium">
              <Wrench size={14} />
              <span>工具调用 ({toolCalls.length})</span>
            </div>

            {toolCalls.length === 0 ? (
              <EmptyState
                title="暂无工具调用"
                description="该节点未调用任何工具"
                icon={<Wrench size={24} />}
              />
            ) : (
              <div className="space-y-2">
                {toolCalls.map((call, index) => (
                  <ToolCallCard key={index} toolCall={call} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* 无节点日志且非 Research 节点时显示空状态 */}
        {!nodeLog && !isResearchNode && (
          <EmptyState
            title="暂无执行信息"
            description="该节点尚未执行或无输出信息"
            icon={<FileOutput size={24} />}
          />
        )}
      </CardContent>
    </Card>
  );
}
