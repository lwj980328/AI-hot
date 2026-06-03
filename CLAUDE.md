# AI前沿热点研究智能体（AI Frontier Research Agent）

---

# 1. 项目定位

本项目旨在构建一个面向 AI 前沿技术追踪与深度研究的 Agent 平台。

系统基于：

- LangGraph
- PydanticAI
- FastAPI
- PostgreSQL
- Qdrant

构建。

项目目标不是聊天机器人，而是：

```text
AI Research Operating System
```

用于：

- AI热点发现
- 趋势跟踪
- 深度研究
- 长期知识积累
- 自动化报告生成

---

# 2. 核心能力

系统支持两类研究模式：

## 模式一：日报模式（Daily Research）

自动追踪：

- Arxiv
- GitHub
- HuggingFace
- 技术博客
- MCP生态

生成：

- 每日热点摘要
- 趋势快报

---

## 模式二：深度研究模式（Deep Research）

用户输入研究主题：

```text
MCP生态发展趋势

OpenAI Agent SDK分析

AI Coding Agent竞争格局
```

系统自动完成：

```text
研究规划
↓

资料检索
↓

多轮分析
↓

知识整合
↓

研究报告生成
```

---

# 3. MVP目标

第一阶段（MVP）必须实现：

## Agent能力

- Research Workflow
- 多Agent协作
- 工具调用
- 报告生成

---

## 数据能力

支持：

- Arxiv
- GitHub

---

## 记忆能力

支持：

- 长期记忆存储
- 历史研究召回

---

## 输出能力

支持：

- Markdown报告
- Web Dashboard

---

# 4. 技术栈

## 后端

- Python 3.12+
- uv
- FastAPI
- LangGraph
- PydanticAI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL
- Qdrant

---

## 前端

- React
- Vite
- TypeScript
- TailwindCSS
- ReactFlow
- Zustand
- TanStack Query
- Shadcn/UI

---

# 5. 核心架构原则

## 原则一：状态驱动

LangGraph State 是系统唯一事实来源（SSOT）。

所有节点只能通过 State 通信。

禁止：

- 全局变量
- 隐式共享状态
- Agent之间直接传递对象

---

## 原则二：强类型

所有核心对象必须使用 Pydantic 定义。

包括：

- AgentState
- Agent输入输出
- Tool输入输出
- API模型
- 数据模型

禁止裸 dict 作为核心业务对象。

---

## 原则三：Agent只负责推理

Agent负责：

- 规划
- 决策
- 分析
- 总结

Agent不得直接访问：

- PostgreSQL
- Qdrant
- HTTP接口
- MCP Server

Agent不得直接实例化工具。

---

## 原则四：工具统一管理

所有工具必须通过：

```text
ToolRegistry
```

注册。

Agent只能声明工具需求。

工具执行统一由：

```text
ToolRegistry
↓
ToolService
↓
Tool
```

完成。

禁止：

```python
agent.run():
    arxiv_tool.search(...)
```

---

## 原则五：分层架构

统一调用链：

```text
API
↓
Service
↓
Repository
↓
Database
```

---

Workflow调用链：

```text
WorkflowManager
↓
Service
↓
Repository
```

---

禁止跳层访问。

---

## 原则六：可扩展

系统必须支持：

- 本地工具
- MCP工具
- 新Workflow
- 新Agent

扩展时不得修改现有核心架构。

---

# 6. Workflow架构

系统采用：

```text
WorkflowManager
↓
LangGraph
↓
Agent
↓
Tool
↓
Memory
```

架构。

---

支持：

## Daily Workflow

日报模式

---

## Research Workflow

深度研究模式

---

## Trend Workflow

趋势分析模式（后续实现）

---

## Adhoc Workflow

即时研究模式

---

# 7. Agent体系

当前Agent：

```text
PlannerAgent

ContextAgent

ResearchAgent

AnalysisAgent

ReportAgent
```

---

Agent职责：

## PlannerAgent

研究规划

---

## ContextAgent

上下文构建

---

## ResearchAgent

研究策略制定

工具需求生成

资料整理

---

## AnalysisAgent

分析推理

洞察提取

---

## ReportAgent

报告生成

---

Memory不是Agent。

Memory体系通过：

```text
RecallNode

UpdateNode

MemoryService
```

实现。

---

# 8. 工具体系

统一抽象：

```text
BaseTool
```

---

统一注册：

```text
ToolRegistry
```

---

统一执行：

```text
ToolService
```

---

支持：

## 本地工具

- WebSearchTool
- ArxivTool
- GithubTool

---

## MCP工具

通过：

```text
MCPToolAdapter
```

接入。

---

# 9. 记忆体系

采用：

```text
PostgreSQL
+
Qdrant
```

双存储架构。

---

PostgreSQL：

完整数据存储。

---

Qdrant：

向量检索。

---

Memory Collection：

```text
research_memory

trend_memory

insight_memory

report_memory

source_memory
```

---

# 10. 数据架构

数据库：

```text
PostgreSQL
```

---

ORM：

```text
SQLAlchemy 2.0
```

---

迁移：

```text
Alembic
```

---

Repository Pattern：

```text
Repository
↓
Service
↓
Workflow/API
```

---

禁止直接访问数据库。

---

# 11. 项目目录规范

```text
project/

├── backend/
│
│ ├── app/
│ │
│ │ ├── agents/
│ │
│ │ ├── workflows/
│ │ │
│ │ │ WorkflowManager
│ │ │ LangGraph定义
│ │ │ Graph节点
│ │
│ │ ├── tools/
│ │ │
│ │ │ BaseTool
│ │ │ ToolRegistry
│ │ │ MCPAdapter
│ │
│ │ ├── memory/
│ │ │
│ │ │ Recall
│ │ │ Update
│ │ │ MemoryService
│ │
│ │ ├── services/
│ │ │
│ │ │ 业务服务层
│ │
│ │ ├── repositories/
│ │ │
│ │ │ Repository实现
│ │
│ │ ├── models/
│ │ │
│ │ │ SQLAlchemy模型
│ │
│ │ ├── schemas/
│ │ │
│ │ │ Pydantic模型
│ │
│ │ ├── api/
│ │ │
│ │ │ FastAPI接口
│ │
│ │ ├── db/
│ │ │
│ │ │ 数据库配置
│ │
│ │ └── core/
│
│ └── tests/
│
├── frontend/
│
│ ├── src/
│ │
│ │ ├── pages/
│ │ ├── features/
│ │ ├── api/
│ │ ├── stores/
│ │ ├── components/
│ │ ├── layouts/
│ │ └── types/
│
├── docs/
│
└── CLAUDE.md
```

---

# 12. 文档体系

```text
01_状态模型设计.md

02_Agent设计规范.md

03_工具设计规范.md

04_Workflow设计规范.md

05_记忆系统设计.md

06_MCP设计规范.md

07_数据库设计.md

08_API设计.md

09_Service设计.md

10_WorkflowManager设计.md

11_前端设计.md

12_开发实施计划.md

13_ClaudeCode开发指南.md
```

---

# 13. 文档优先级

```text
CLAUDE.md

↓

01_状态模型设计.md

↓

02_Agent设计规范.md

↓

03_工具设计规范.md

↓

04_Workflow设计规范.md

↓

其它文档
```

低优先级文档不得推翻高优先级文档。

---

# 14. 开发模式

采用：

```text
Milestone驱动开发
```

禁止：

```text
技术层驱动开发
```

---

每个Milestone必须：

```text
可运行

可验收

可演示
```

---

开发顺序：

```text
Milestone 1
最小可运行系统

↓

Milestone 2
多Agent工作流

↓

Milestone 3
记忆系统

↓

Milestone 4
工具系统

↓

Milestone 5
MCP集成

↓

Milestone 6
前端MVP

↓

Milestone 7
Workflow可视化

↓

Milestone 8
最终展示版
```

---

# 15. Claude Code工作规则

Claude Code必须：

- 遵循所有设计文档
- 严格按照Milestone开发
- 不得跨Milestone实现功能
- 不得修改架构设计

---

每次开发必须输出：

```text
当前Milestone

目标

新增文件

修改文件

验收步骤
```

---

# 16. 项目完成标准

系统最终形成：

```text
用户问题
↓
WorkflowManager
↓
Agent协作
↓
Tool调用
↓
Memory召回
↓
分析推理
↓
研究报告生成
↓
知识沉淀
```

完整闭环。

---

# 17. 非目标（Out of Scope）

当前项目不追求：

- 通用聊天机器人
- 多用户权限系统
- 企业级SaaS能力
- 分布式微服务架构

优先保证：

```text
Agent能力展示

工程架构能力展示

Research Workflow展示
```

用于：

```text
大模型应用开发岗位

Agent开发岗位

AI工程化岗位
```
