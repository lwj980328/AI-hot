import { Loader2, Database } from "lucide-react";
import { MemoryCard } from "./MemoryCard";
import { EmptyState } from "@/components/shared/EmptyState";
import type { MemoryItem } from "@/types/memory";

interface MemoryListProps {
  memories: MemoryItem[];
  isLoading?: boolean;
  selectedId?: string;
  onSelect: (memory: MemoryItem) => void;
}

/** 记忆列表组件 */
export function MemoryList({
  memories,
  isLoading,
  selectedId,
  onSelect,
}: MemoryListProps) {
  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (memories.length === 0) {
    return (
      <EmptyState
        icon={<Database className="h-12 w-12" />}
        title="暂无记忆数据"
        description="完成研究任务后，系统会自动保存研究记忆、趋势快照和洞察。"
      />
    );
  }

  return (
    <div className="space-y-3">
      {memories.map((memory) => (
        <MemoryCard
          key={memory.memory_id}
          memory={memory}
          isSelected={memory.memory_id === selectedId}
          onClick={() => onSelect(memory)}
        />
      ))}
    </div>
  );
}
