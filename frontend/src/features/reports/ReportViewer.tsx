import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { EmptyState } from "@/components/shared/EmptyState";
import { FileText } from "lucide-react";
import type { Report } from "@/types/report";

interface ReportViewerProps {
  report: Report | null | undefined;
  isLoading: boolean;
}

/** 报告查看器组件 */
export function ReportViewer({ report, isLoading }: ReportViewerProps) {
  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner />
      </div>
    );
  }

  if (!report) {
    return (
      <EmptyState
        title="选择报告"
        description="从左侧列表中选择一份报告查看"
        icon={<FileText size={48} />}
      />
    );
  }

  return (
    <div className="prose prose-sm max-w-none">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {report.markdown_content}
      </ReactMarkdown>
    </div>
  );
}
