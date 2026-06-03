# ClaudeCode开发指南

# 1. 文档目标

本文档用于指导 Claude Code 按照项目规范逐阶段开发系统。

Claude Code 必须：

```text
遵循架构

遵循开发计划

遵循目录结构

遵循模块边界
```

---

禁止：

```text
自由发挥

重构架构

修改设计规范
```

---

# 2. Claude Code 工作原则

---

## 原则一

设计文档优先。

---

必须遵循：

```text
CLAUDE.md

01~12全部规范文档
```

---

如果发现：

```text
设计与实现冲突
```

必须：

```text
提出问题
```

而不是：

```text
自行修改架构
```

---

## 原则二

严格按照 Milestone 开发。

---

禁止：

```text
开发 Milestone 1 时实现 Milestone 4 功能
```

---

禁止：

```text
提前实现 MCP
```

---

禁止：

```text
提前实现 ReactFlow
```

---

## 原则三

一次只完成一个功能闭环。

---

例如：

```text
Task
↓
Workflow
↓
Report
```

完成后再进入下一功能。

---

# 3. Claude Code 输出要求

每次执行任务时：

必须输出：

```text
当前Milestone

目标

修改文件

新增文件

验收方式
```

---

示例：

```text
当前Milestone：
Milestone 2

目标：
实现AnalysisAgent

新增文件：
analysis_agent.py

修改文件：
research_graph.py

验收：
能够产生结构化分析结果
```

---

# 4. 文件创建原则

---

允许：

```text
按文档目录创建文件
```

---

禁止：

```text
随意新增目录
```

---

禁止：

```text
创建未定义模块
```

---

例如：

允许：

```text
backend/app/services/
```

---

禁止：

```text
backend/core_v2/
```

---

# 5. Milestone 开发流程

统一采用：

```text
阅读规范
↓

创建目录

↓

创建接口

↓

实现逻辑

↓

运行验证

↓

输出结果
```

---

# 6. Milestone 1 Prompt 模板

目标：

```text
最小可运行系统
```

---

Prompt：

```text
当前进入 Milestone 1。

请严格遵循：

CLAUDE.md
07_数据库设计.md
08_API设计.md
09_Service设计.md
10_WorkflowManager设计.md

开发目标：

实现最小可运行系统。

实现范围：

- PostgreSQL连接
- Alembic初始化
- Task模型
- WorkflowRun模型
- Report模型
- TaskRepository
- WorkflowRepository
- ReportRepository
- TaskService
- WorkflowService
- ReportService
- ResearchWorkflowManager
- FastAPI基础API

不要实现：

- Qdrant
- Memory
- ToolRegistry
- MCP
- ReactFlow

开发完成后：

输出新增文件列表、修改文件列表、运行方式、验收步骤。
```

---

# 7. Milestone 1 预期产出

目录：

```text
backend/app/

api/
db/
services/
workflows/
```

---

文件：

```text
database.py

task.py

workflow_run.py

report.py

task_service.py

workflow_service.py

report_service.py

research_manager.py
```

---

验收：

```text
创建任务

触发Workflow

生成报告
```

---

# 8. Milestone 2 Prompt 模板

目标：

```text
多Agent工作流
```

---

Prompt：

```text
当前进入 Milestone 2。

请基于已完成的 Milestone 1 开发。

实现：

- PlannerAgent
- ContextAgent
- AnalysisAgent
- ReportAgent

实现：

Research Loop

更新：

ResearchWorkflowManager

不要实现：

- Qdrant
- Memory
- MCP

输出：

新增Agent
修改Graph
验收步骤
```

---

# 9. Milestone 2 预期产出

新增：

```text
planner_agent.py

context_agent.py

analysis_agent.py

report_agent.py
```

---

修改：

```text
research_graph.py
```

---

验收：

```text
能够执行多Agent流程
```

---

# 10. Milestone 3 Prompt 模板

目标：

```text
记忆系统
```

---

Prompt：

```text
当前进入 Milestone 3。

请严格遵循：

05_记忆系统设计.md

07_数据库设计.md

09_Service设计.md

实现：

- Qdrant接入
- MemoryService
- RecallNode
- UpdateNode
- report_memory
- source_memory

不要实现：

MCP

前端

输出：

新增文件
修改文件
验收步骤
```

---

# 11. Milestone 3 预期产出

新增：

```text
memory_service.py

qdrant_store.py

recall_node.py

update_node.py
```

---

验收：

```text
第二次研究可召回历史内容
```

---

# 12. Milestone 4 Prompt 模板

目标：

```text
工具系统
```

---

Prompt：

```text
当前进入 Milestone 4。

请遵循：

03_工具设计规范.md

实现：

BaseTool

ToolRegistry

ToolService

WebSearchTool

GithubTool

ArxivTool

Agent通过ToolRegistry调用工具

禁止Agent直接依赖工具实现。

输出：

工具目录结构
新增文件
验收步骤
```

---

# 13. Milestone 4 预期产出

新增：

```text
base_tool.py

tool_registry.py

tool_service.py

web_search_tool.py

github_tool.py

arxiv_tool.py
```

---

验收：

```text
ResearchAgent能够自主调用工具
```

---

# 14. Milestone 5 Prompt 模板

目标：

```text
MCP集成
```

---

Prompt：

```text
当前进入 Milestone 5。

请遵循：

06_MCP设计规范.md

实现：

MCPClient

MCPToolAdapter

MCPToolProvider

接入ToolRegistry

不要修改已有本地工具架构。

输出：

新增文件
调用流程
验收步骤
```

---

# 15. Milestone 5 预期产出

新增：

```text
mcp_client.py

mcp_adapter.py

mcp_provider.py
```

---

验收：

```text
至少成功调用一个MCP工具
```

---

# 16. Milestone 6 Prompt 模板

目标：

```text
前端MVP
```

---

Prompt：

```text
当前进入 Milestone 6。

请遵循：

11_前端设计.md

实现：

Dashboard

Research Workspace

Reports

接入：

Task API

Workflow API

Report API

不要实现：

ReactFlow

Memory Center

输出：

页面结构
新增组件
运行方式
```

---

# 17. Milestone 6 预期产出

页面：

```text
Dashboard

Research Workspace

Reports
```

---

验收：

```text
能够创建任务并查看报告
```

---

# 18. Milestone 7 Prompt 模板

目标：

```text
Workflow可视化
```

---

Prompt：

```text
当前进入 Milestone 7。

请遵循：

11_前端设计.md

实现：

ReactFlow

Workflow Monitor

Condition Edge

Node Status

展示：

Planner

Context

Research

Analysis

Memory

Report

输出：

新增组件
交互说明
验收步骤
```

---

# 19. Milestone 7 预期产出

新增：

```text
WorkflowCanvas.tsx

PlannerNode.tsx

ResearchNode.tsx

ConditionEdge.tsx
```

---

验收：

```text
可视化展示Agent执行路径
```

---

# 20. Milestone 8 Prompt 模板

目标：

```text
最终展示版
```

---

Prompt：

```text
当前进入 Milestone 8。

实现：

Memory Center

语义搜索

界面优化

错误处理优化

性能优化

不要修改核心架构。

输出：

优化项列表
验收步骤
```

---

# 21. Claude Code 自检清单

每次开发完成后：

必须检查：

```text
是否符合目录结构

是否符合接口规范

是否符合Service边界

是否符合Workflow规范

是否符合Tool规范
```

---

# 22. 禁止事项

禁止：

```text
Agent直接访问数据库

Agent直接访问Qdrant

Workflow直接访问Repository

API直接访问Repository
```

---

禁止：

```text
绕过ToolRegistry调用工具
```

---

禁止：

```text
修改AgentState核心结构
```

---

# 23. 提交前检查

必须通过：

```text
项目启动

接口调用

核心流程运行
```

---

之后才允许进入：

```text
下一个Milestone
```

---

# 24. Claude Code 开发节奏

推荐：

```text
Milestone 1
完成并验收

↓

Milestone 2
完成并验收

↓

Milestone 3
完成并验收

...
```

---

不要：

```text
连续开发1~8
```

---

# 25. 最终开发顺序

```text
CLAUDE.md

↓

01~11 规范文档

↓

12_开发实施计划.md

↓

13_ClaudeCode开发指南.md

↓

Milestone 1

↓

Milestone 2

↓

Milestone 3

↓

Milestone 4

↓

Milestone 5

↓

Milestone 6

↓

Milestone 7

↓

Milestone 8
```

---

# 26. 文档定位

本文档不是架构文档。

而是：

```text
Claude Code执行手册
```

用于保证：

```text
开发顺序正确

实现范围正确

代码结构正确

最终系统符合设计规范
```
