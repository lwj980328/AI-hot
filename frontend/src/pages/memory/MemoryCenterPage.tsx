import { useState, useMemo } from "react";
import {
  Brain,
  TrendingUp,
  Lightbulb,
  Database,
  BarChart3,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatCardsSkeleton } from "@/components/ui/skeleton";
import { MemorySearch } from "@/features/memory/MemorySearch";
import { MemoryList } from "@/features/memory/MemoryList";
import { MemoryDetail } from "@/features/memory/MemoryDetail";
import { useMemories, useMemorySearch, useMemoryStats } from "@/hooks/useMemories";
import type { MemoryItem, MemoryType } from "@/types/memory";

/** 记忆类型筛选配置 */
const memoryTypeFilters = [
  { value: "all", label: "全部", icon: Database },
  { value: "research", label: "研究记忆", icon: Brain },
  { value: "trend", label: "趋势快照", icon: TrendingUp },
  { value: "insight", label: "洞察记忆", icon: Lightbulb },
] as const;

/** Memory Center 页面 */
export function MemoryCenterPage() {
  const [selectedMemory, setSelectedMemory] = useState<MemoryItem | null>(null);
  const [activeFilter, setActiveFilter] = useState<MemoryType | "all">("all");
  const [searchQuery, setSearchQuery] = useState("");

  // 获取记忆统计
  const { data: stats, isLoading: statsLoading } = useMemoryStats();

  // 获取记忆列表
  const { data: memoriesData, isLoading: listLoading } = useMemories({
    memoryType: activeFilter === "all" ? undefined : activeFilter,
    limit: 50,
  });

  // 搜索记忆
  const { data: searchData, isLoading: searchLoading } = useMemorySearch(
    searchQuery,
    { limit: 20 }
  );

  // 合并所有记忆
  const allMemories = useMemo(() => {
    if (searchQuery && searchData) {
      // 搜索模式
      return [
        ...searchData.research,
        ...searchData.trend,
        ...searchData.insight,
      ].sort((a, b) => b.score - a.score);
    }

    if (memoriesData) {
      // 列表模式
      return [
        ...memoriesData.research,
        ...memoriesData.trend,
        ...memoriesData.insight,
      ].sort((a, b) => {
        // 处理 created_at 可能为空的情况
        const timeA = a.created_at ? new Date(a.created_at).getTime() : 0;
        const timeB = b.created_at ? new Date(b.created_at).getTime() : 0;
        return timeB - timeA;
      });
    }

    return [];
  }, [searchQuery, searchData, memoriesData]);

  // 按类型筛选
  const filteredMemories = useMemo(() => {
    if (activeFilter === "all") return allMemories;
    return allMemories.filter((m) => m.memory_type === activeFilter);
  }, [allMemories, activeFilter]);

  // 统计数据
  const statsData = stats || {
    research_count: 0,
    trend_count: 0,
    insight_count: 0,
    total: 0,
  };

  // 处理搜索
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setSelectedMemory(null);
  };

  // 处理记忆选择
  const handleSelectMemory = (memory: MemoryItem) => {
    setSelectedMemory(memory);
  };

  return (
    <div className="page-enter space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold">Memory Center</h1>
        <p className="text-muted-foreground">
          展示系统积累的长期记忆，包括研究记忆、趋势快照和洞察。
        </p>
      </div>

      {/* 统计卡片 */}
      {statsLoading ? (
        <StatCardsSkeleton count={4} />
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <Card className="flex items-center gap-3 p-4 card-hover">
            <div className="rounded-full bg-blue-100 p-2">
              <Brain className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">{statsData.research_count}</div>
              <div className="text-xs text-muted-foreground">研究记忆</div>
            </div>
          </Card>
          <Card className="flex items-center gap-3 p-4 card-hover">
            <div className="rounded-full bg-green-100 p-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">{statsData.trend_count}</div>
              <div className="text-xs text-muted-foreground">趋势快照</div>
            </div>
          </Card>
          <Card className="flex items-center gap-3 p-4 card-hover">
            <div className="rounded-full bg-yellow-100 p-2">
              <Lightbulb className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">{statsData.insight_count}</div>
              <div className="text-xs text-muted-foreground">洞察记忆</div>
            </div>
          </Card>
          <Card className="flex items-center gap-3 p-4 card-hover">
            <div className="rounded-full bg-purple-100 p-2">
              <BarChart3 className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <div className="text-2xl font-bold">{statsData.total}</div>
              <div className="text-xs text-muted-foreground">总记忆数</div>
            </div>
          </Card>
        </div>
      )}

      {/* 搜索栏 */}
      <MemorySearch onSearch={handleSearch} />

      {/* 类型筛选 */}
      <div className="flex flex-wrap gap-2">
        {memoryTypeFilters.map((filter) => {
          const Icon = filter.icon;
          const isActive = activeFilter === filter.value;
          return (
            <Badge
              key={filter.value}
              variant={isActive ? "default" : "outline"}
              className="cursor-pointer"
              onClick={() => {
                setActiveFilter(filter.value);
                setSelectedMemory(null);
              }}
            >
              <Icon className="mr-1 h-3 w-3" />
              {filter.label}
            </Badge>
          );
        })}
        {searchQuery && (
          <Badge variant="secondary" className="ml-auto">
            搜索: {searchQuery}
          </Badge>
        )}
      </div>

      {/* 主内容区：列表 + 详情 */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* 左侧：记忆列表 */}
        <div className="h-[600px] overflow-y-auto rounded-lg border p-4">
          <MemoryList
            memories={filteredMemories}
            isLoading={listLoading || searchLoading}
            selectedId={selectedMemory?.memory_id}
            onSelect={handleSelectMemory}
          />
        </div>

        {/* 右侧：记忆详情 */}
        <div className="h-[600px] overflow-y-auto rounded-lg border p-4">
          {selectedMemory ? (
            <MemoryDetail memory={selectedMemory} />
          ) : (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              <div className="text-center">
                <Database className="mx-auto mb-4 h-12 w-12 opacity-50" />
                <p>选择一条记忆查看详情</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
