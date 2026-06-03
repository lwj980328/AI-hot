# Workflow设计规范

---

# 1. 文档目标

本文档定义系统工作流（Workflow）设计规范。

本项目采用：

- LangGraph 作为唯一工作流编排框架
- AgentState 作为唯一状态载体
- Agent 作为节点执行单元

Workflow负责：

- 节点调度
- 状态流转
- 条件判断
- 错误恢复
- 研究回环控制

---

# 2. 核心设计原则

## 原则一：State是唯一事实来源

所有节点：

输入：

```python
AgentState
```

输出：

```python
AgentState
```

禁止节点间直接传递对象。

禁止全局共享变量。

---

## 原则二：节点只负责调度Agent

Workflow节点不实现业务逻辑。

业务逻辑全部位于：

```text
PlannerAgent
ContextAgent
ResearchAgent
AnalysisAgent
MemoryAgent
ReportAgent
```

---

## 原则三：显式状态流转

所有流程跳转必须通过：

```python
Conditional Edge
```

实现。

禁止在节点内部控制工作流。

---

## 原则四：支持Deep Research循环

系统允许：

```text
研究
↓
分析
↓
发现证据不足
↓
再次研究
↓
再次分析
```

直到满足终止条件。

---

# 3. 工作流总览

```text
START
  │
  ▼
Planner
  │
  ▼
Context
  │
  ▼
Research
  │
  ▼
Analysis
  │
  ├─────────────┐
  │             │
  │ need_more_data=True
  │             │
  ▼             │
Memory          │
  │             │
  ▼             │
Report          │
  │             │
  ▼             │
 END            │
                │
                ▼
            Research
```

---

# 4. 节点定义

## PlannerNode

对应：

```text
PlannerAgent
```

职责：

将用户问题转化为研究计划。

输入：

```python
state.user_query
```

输出：

```python
state.research.topic

state.research.keywords

state.research.data_sources
```

状态：

```python
TaskStatus.PLANNING
```

---

## ContextNode

对应：

```text
ContextAgent
```

职责：

获取研究所需上下文信息。

当前实现：

```text
Memory Recall
```

未来扩展：

```text
Knowledge Base Recall

Graph Memory Recall

User Preference Recall
```

输入：

```python
state.research.topic
```

输出：

```python
state.context.context_items
```

状态：

```python
TaskStatus.CONTEXT_LOADING
```

---

## ResearchNode

对应：

```text
ResearchAgent
```

职责：

执行数据采集。

调用：

```text
GithubTool

ArxivTool

HuggingFaceTool
```

输入：

```python
state.research
```

输出：

```python
state.research.papers

state.research.repositories

state.research.models
```

状态：

```python
TaskStatus.RESEARCHING
```

---

## AnalysisNode

对应：

```text
AnalysisAgent
```

职责：

生成结构化知识。

输入：

```python
state.research

state.context
```

输出：

```python
state.analysis
```

状态：

```python
TaskStatus.ANALYZING
```

同时负责：

```python
state.research.need_more_data
```

判断。

---

## MemoryNode

对应：

```text
MemoryAgent
```

职责：

更新长期记忆。

输入：

```python
state.research

state.analysis
```

输出：

```python
state.memory
```

状态：

```python
TaskStatus.MEMORY_UPDATING
```

---

## ReportNode

对应：

```text
ReportAgent
```

职责：

生成最终研究报告。

输入：

```python
state.research

state.analysis

state.context
```

输出：

```python
state.report
```

状态：

```python
TaskStatus.REPORTING
```

---

# 5. 条件边设计

## ContinueResearchEdge

负责：

决定是否继续研究。

定义：

```python
def continue_research(
    state: AgentState
) -> str:
```

逻辑：

```python
if state.research.need_more_data:
    return "research"

return "memory"
```

---

# 6. Deep Research回环机制

## 第一轮研究

```text
Research
↓
Analysis
```

Analysis发现：

```text
缺少GitHub生态数据
```

写入：

```python
state.research.need_more_data=True

state.research.information_gaps=[
    "缺少GitHub生态数据"
]
```

---

Workflow自动跳转：

```text
Research
```

---

ResearchAgent读取：

```python
information_gaps
```

继续补充数据。

---

再次进入：

```text
Analysis
```

---

# 7. 最大研究轮次

配置：

```python
MAX_RESEARCH_ROUNDS = 3
```

---

ResearchNode执行时检查：

```python
state.research.search_round
```

---

达到上限：

```python
search_round >= 3
```

强制：

```python
state.research.need_more_data=False
```

进入：

```text
Memory
```

---

# 8. 错误处理机制

所有节点统一接入：

```text
ErrorHandlerNode
```

---

节点异常：

```text
Planner

Context

Research

Analysis

Memory

Report
```

---

统一更新：

```python
state.status=FAILED
```

记录：

```python
state.error_info
```

---

# 9. Workflow实现规范

目录：

```text
backend/app/graph/

├── workflow.py

├── nodes/
│
├── edges/
│
├── handlers/
│
└── error_handler.py
```

---

# 10. LangGraph实现规范

注册节点：

```python
planner

context

research

analysis

memory

report
```

---

注册边：

```python
START
→ planner

planner
→ context

context
→ research

research
→ analysis
```

---

条件边：

```python
analysis
→ research

analysis
→ memory
```

---

普通边：

```python
memory
→ report

report
→ END
```

---

# 11. Workflow触发模式

## 用户研究模式

输入：

```text
最近MCP的发展趋势是什么？
```

执行：

```python
run_workflow(
    task_type="user_research"
)
```

生成：

单份研究报告。

---

## 定时研究模式

调度器获取：

```python
[
    "MCP",
    "Agent",
    "Reasoning Model"
]
```

执行：

```python
for topic in topics:
    run_workflow(topic)
```

最终汇总：

```text
AI热点日报
```

---

# 12. 后续扩展原则

新增能力时：

禁止修改：

```text
ResearchAgent

AnalysisAgent

Workflow结构
```

允许：

```text
扩展ContextNode

新增Tool

新增Memory能力
```

实现能力增强。

---

# 13. 文档依赖

依赖：

- 01\_状态模型设计.md
- 02_Agent设计规范.md
- 03\_工具设计规范.md

后续：

- 05\_记忆系统设计.md
- 06_MCP设计规范.md

必须遵循本文件定义的Workflow结构。
