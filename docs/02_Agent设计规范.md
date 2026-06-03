# Agent设计规范

---

# 1. 文档目标

本文档定义系统中所有 Agent 的职责边界、输入输出规范以及与 Workflow、Tool、State 的协作方式。

本项目采用：

- LangGraph 负责工作流编排
- PydanticAI 负责 Agent 实现
- Pydantic 负责结构化数据定义

Agent 是系统唯一业务执行单元。

---

# 2. Agent设计原则

## 原则一：单一职责

一个 Agent 只负责一个领域。

禁止：

```text
ResearchAgent
同时负责
分析
报告生成
记忆管理
```

---

## 原则二：状态驱动

Agent只能：

```text
读取AgentState

更新AgentState
```

禁止：

```text
Agent之间直接通信
```

---

## 原则三：结构化输出

所有Agent输出必须使用：

```python
Pydantic Model
```

禁止返回自由文本。

---

## 原则四：Agent不直接访问基础设施

Agent不得直接访问：

```text
数据库

Qdrant

Redis

HTTP客户端

MCP客户端
```

必须通过：

```text
Tool

Service
```

访问。

---

## 原则五：Agent不直接依赖具体工具实现

Agent不得直接实例化或调用具体工具。

Agent只能通过 ToolRegistry 声明工具需求。

工具执行由 ToolService 统一完成。

---

## 原则六：Agent可独立测试

每个Agent必须支持：

```text
Mock Tool

Mock Memory

Mock Service
```

测试。

---

# 3. Agent体系结构

系统包含六个核心Agent：

```text
PlannerAgent

ContextAgent

ResearchAgent

AnalysisAgent

MemoryAgent

ReportAgent
```

---

# 4. Agent职责总览

| Agent         | 主要职责       |
| ------------- | -------------- |
| PlannerAgent  | 制定研究计划   |
| ContextAgent  | 构建研究上下文 |
| ResearchAgent | 收集研究资料   |
| AnalysisAgent | 生成结构化洞察 |
| MemoryAgent   | 更新长期记忆   |
| ReportAgent   | 输出研究报告   |

---

# 5. PlannerAgent

---

## 职责

将用户需求转换为研究计划。

---

## 输入

读取：

```python
state.user_query
```

---

## 输出

更新：

```python
state.research.topic

state.research.keywords

state.research.data_sources
```

---

## 示例

输入：

```text
最近MCP的发展趋势
```

输出：

```python
topic="MCP"

keywords=[
    "MCP",
    "Model Context Protocol"
]

data_sources=[
    "github",
    "arxiv",
    "huggingface"
]
```

---

## 不允许修改

```python
state.context

state.analysis

state.memory

state.report
```

---

## Tool权限

无。

PlannerAgent禁止调用任何Tool。

---

# 6. ContextAgent

---

## 职责

构建研究上下文。

---

## 设计目标

ResearchAgent不直接访问历史记忆。

所有历史信息统一由：

```text
ContextAgent
```

提供。

---

## 当前能力

支持：

```text
Research Memory Recall

Trend Recall

Insight Recall
```

---

## 未来能力

支持：

```text
Knowledge Base Recall

Graph Memory Recall

User Preference Recall
```

---

## 输入

读取：

```python
state.research.topic
```

---

## 输出

写入：

```python
state.context.context_items
```

---

## ContextItem来源

当前：

```text
ResearchMemory

TrendSnapshot

InsightMemory
```

---

## Tool权限

允许：

```text
MemoryService
```

---

禁止：

```text
QdrantClient
```

直接访问。

---

# 7. ResearchAgent

---

## 职责

负责资料采集。

---

## 输入

读取：

```python
state.research

state.context
```

---

## 输出

更新：

```python
state.research.papers

state.research.repositories

state.research.models
```

---

## Tool权限

允许：

```text
GithubTool

ArxivTool

HuggingFaceTool
```

---

未来允许：

```text
Github MCP Tool

Search MCP Tool

Browser MCP Tool
```

---

## Deep Research职责

支持：

```text
多轮研究
```

模式。

---

读取：

```python
state.research.information_gaps
```

执行补充研究。

---

## 不负责

禁止：

```text
趋势分析

洞察生成

报告生成
```

---

# 8. AnalysisAgent

---

## 职责

从原始资料中提取知识。

---

## 输入

读取：

```python
state.research

state.context
```

---

## 输出

写入：

```python
state.analysis
```

---

## 核心任务

---

### 热点识别

生成：

```python
state.analysis.hot_topics
```

---

### 趋势分析

生成：

```python
state.analysis.trend_summary
```

---

### 洞察生成

生成：

```python
AnalysisInsight
```

---

### 证据绑定

每个洞察必须关联：

```python
Evidence
```

---

禁止：

```text
无来源结论
```

---

### 信息缺口检测

发现：

```text
证据不足

研究不充分
```

时：

写入：

```python
state.research.need_more_data=True
```

以及：

```python
state.research.information_gaps
```

---

## 历史对比能力

读取：

```python
state.context.context_items
```

实现：

```text
趋势增长分析

趋势下降分析

演化分析
```

---

# 9. MemoryAgent

---

## 职责

更新长期记忆。

---

## 注意

MemoryAgent：

```text
只负责写入

不负责召回
```

---

召回职责属于：

```text
ContextAgent
```

---

## 输入

读取：

```python
state.research

state.analysis
```

---

## 输出

写入：

```python
state.memory.memory_ids

state.memory.memory_updated
```

---

## 写入内容

---

### ResearchMemory

研究结果。

---

### TrendSnapshot

趋势快照。

---

### InsightMemory

洞察。

---

## Tool权限

允许：

```text
MemoryService
```

---

禁止：

```text
QdrantClient
```

直接访问。

---

# 10. ReportAgent

---

## 职责

生成最终研究报告。

---

## 输入

读取：

```python
state.research

state.context

state.analysis
```

---

## 输出

写入：

```python
state.report
```

---

## 生成内容

---

### 报告标题

```python
report.title
```

---

### 执行摘要

```python
report.summary
```

---

### Markdown正文

```python
report.markdown_content
```

---

## 报告要求

必须包含：

```text
研究主题

数据来源

趋势分析

核心洞察

证据引用

未来观察方向
```

---

# 11. Agent与State映射

| Agent    | 读取                        | 写入     |
| -------- | --------------------------- | -------- |
| Planner  | user_query                  | research |
| Context  | research                    | context  |
| Research | research、context           | research |
| Analysis | research、context           | analysis |
| Memory   | research、analysis          | memory   |
| Report   | research、context、analysis | report   |

---

# 12. Agent与Tool映射

| Agent    | Tool                                   |
| -------- | -------------------------------------- |
| Planner  | 无                                     |
| Context  | MemoryService                          |
| Research | GithubTool、ArxivTool、HuggingFaceTool |
| Analysis | 无                                     |
| Memory   | MemoryService                          |
| Report   | 无                                     |

---

# 13. Agent目录规范

```text
backend/app/agents/

├── planner_agent.py

├── context_agent.py

├── research_agent.py

├── analysis_agent.py

├── memory_agent.py

└── report_agent.py
```

---

# 14. Agent测试规范

```text
backend/tests/agents/
```

每个Agent至少包含：

```text
正常流程测试

边界测试

异常测试

输出结构测试
```

---

# 15. 文档依赖

依赖：

```text
01_状态模型设计.md
```

后续文档：

```text
03_工具设计规范.md

04_Workflow设计规范.md

05_记忆系统设计.md
```

不得违反本文件定义的职责边界。
