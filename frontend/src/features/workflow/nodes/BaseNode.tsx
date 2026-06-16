import { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import { cn } from "@/utils/cn";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import {
  CheckCircle,
  XCircle,
  Clock,
  Wrench,
} from "lucide-react";
import type { NodeStatus } from "@/types/workflow";

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

/** 节点状态样式 */
const statusStyles: Record<NodeStatus, string> = {
  pending: "border-gray-300 bg-gray-50",
  running: "border-blue-500 bg-blue-50 shadow-blue-200 shadow-lg animate-pulse",
  completed: "border-green-500 bg-green-50",
  failed: "border-red-500 bg-red-50",
};

/** 基础节点组件 */
function BaseNodeComponent({
  data,
  sourcePosition = Position.Bottom,
  targetPosition = Position.Top,
}: {
  data: {
    label: string;
    description: string;
    status: NodeStatus;
    toolCount: number;
  };
  sourcePosition?: Position;
  targetPosition?: Position;
}) {
  const { label, description, status, toolCount } = data;

  return (
    <div
      className={cn(
        "rounded-lg border-2 px-4 py-3 min-w-[160px] transition-all duration-300",
        statusStyles[status]
      )}
    >
      {/* 目标连接点 */}
      <Handle
        type="target"
        position={targetPosition}
        className="w-3 h-3 !bg-gray-400"
      />

      {/* 节点内容 */}
      <div className="flex items-center gap-2 mb-1">
        <StatusIcon status={status} />
        <span className="font-semibold text-sm">{label}</span>
      </div>

      <p className="text-xs text-muted-foreground mb-2">{description}</p>

      {/* 工具调用计数 */}
      {toolCount > 0 && (
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <Wrench size={12} />
          <span>{toolCount} 个工具</span>
        </div>
      )}

      {/* 源连接点 */}
      <Handle
        type="source"
        position={sourcePosition}
        className="w-3 h-3 !bg-gray-400"
      />
    </div>
  );
}

export const BaseNode = memo(BaseNodeComponent);
