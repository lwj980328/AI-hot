/** 记忆类型枚举 */
export type MemoryType = "research" | "trend" | "insight";

/** 记忆证据 */
export interface MemoryEvidence {
  statement: string;
  source_ids: string[];
  confidence: number;
}

/** 记忆项 */
export interface MemoryItem {
  memory_id: string;
  memory_type: MemoryType;
  topic: string;
  summary: string;
  created_at?: string;
  source_ids: string[];
  score: number;

  // Research Memory 特有字段
  report_title?: string;
  report_summary?: string;

  // Trend Snapshot 特有字段
  hot_topics?: string[];
  project_count?: number;
  paper_count?: number;
  model_count?: number;
  confidence_score?: number;

  // Insight Memory 特有字段
  insight_title?: string;
  insight_description?: string;
  evidences?: MemoryEvidence[];
}

/** 记忆搜索响应 */
export interface MemorySearchResponse {
  research: MemoryItem[];
  trend: MemoryItem[];
  insight: MemoryItem[];
  total: number;
}

/** 记忆统计 */
export interface MemoryStats {
  research_count: number;
  trend_count: number;
  insight_count: number;
  total: number;
}
