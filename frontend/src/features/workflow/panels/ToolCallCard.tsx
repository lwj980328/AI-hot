import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, XCircle, Clock } from "lucide-react";
import type { ToolCallRecord } from "@/types/workflow";

interface ToolCallCardProps {
  toolCall: ToolCallRecord;
}

/** 工具调用卡片组件 */
export function ToolCallCard({ toolCall }: ToolCallCardProps) {
  const { tool_name, input_params, output_summary, success, duration_ms } =
    toolCall;

  return (
    <Card className={success ? "" : "border-red-200"}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            {success ? (
              <CheckCircle size={14} className="text-green-500" />
            ) : (
              <XCircle size={14} className="text-red-500" />
            )}
            <span>{tool_name}</span>
          </div>
          <Badge variant="outline" className="text-xs">
            <Clock size={10} className="mr-1" />
            {duration_ms}ms
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="text-xs space-y-2">
        {/* 输入参数 */}
        <div>
          <p className="text-muted-foreground mb-1">输入参数：</p>
          <pre className="bg-muted p-2 rounded text-xs overflow-x-auto">
            {JSON.stringify(input_params, null, 2)}
          </pre>
        </div>

        {/* 输出摘要 */}
        <div>
          <p className="text-muted-foreground mb-1">输出：</p>
          <p className={success ? "" : "text-red-500"}>{output_summary}</p>
        </div>
      </CardContent>
    </Card>
  );
}
