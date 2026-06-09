# 项目开发日志 (Dev Log)
> 核心原则：此日志用于记录阶段性产出、架构妥协记录以及避坑指南。每次开启新 Milestone 前，AI 助手必须优先读取此文件。

## Milestone 1: MVP 骨架与单 Agent 闭环
**状态:** 🟢 已完成
**完成日期:** 2026-06-05

### 1. 核心产出 (What was done)
* **API 路由层**: 实现 `/api/v1/tasks` (POST/GET)、`/api/v1/workflows/run` (POST)、`/api/v1/reports` (GET) 等端点
* **AgentState 完整 Pydantic 模型**: 按照 `01_状态模型设计.md` 完整定义了 AgentState、ResearchState、ContextState、AnalysisState、MemoryState、ReportState，包含 models 字段和 ModelRecord
* **单向 LangGraph 工作流**: 实现 `START → Research → Report → END` 线性流程
* **PostgreSQL 数据库持久化**: 创建 tasks、workflow_runs、reports 三张表，使用 SQLAlchemy 2.0 + AsyncSession
* **Service 层**: TaskService、WorkflowService、ReportService，返回 DTO 而非 ORM 对象
* **Repository 层**: BaseRepository 提供通用 CRUD，各实体 Repository 继承实现
* **LLM Service**: 统一封装 LLM 调用，解决 Agent 直接访问外部服务的架构违规
* **统一异常体系**: ServiceError、NotFoundError、WorkflowError 等异常类
* **Docker 环境**: docker-compose.yml 配置 PostgreSQL 15

### 2. 踩坑与返工记录 (Mistakes & Rework - 核心反思)

**踩坑 1: LangGraph 返回值类型误解**
* **问题描述**: `graph.ainvoke()` 返回的是字典而非 AgentState 对象，导致 `final_state.report.title` 报错 `'dict' object has no attribute 'report'`
* **根本原因**: 对 LangGraph API 的返回值类型理解错误。LangGraph 的 `ainvoke` 总是返回字典，即使输入是 Pydantic 对象
* **最终解法**: 在 `base_manager.py` 中显式转换：`result = await graph.ainvoke(initial_state.model_dump())` + `return AgentState.model_validate(result)`

**踩坑 2: LangGraph 节点函数返回类型错误**
* **问题描述**: 节点函数返回 AgentState 对象，但 LangGraph 期望返回字典用于状态合并
* **根本原因**: 没有正确理解 LangGraph 的状态更新机制——节点函数应返回部分状态字典
* **最终解法**: 修改 `graph.py` 中的节点函数，接收 dict、转换为 AgentState 处理后、返回 `result.model_dump()`

**踩坑 3: Agent 直接访问外部服务（架构违规）**
* **问题描述**: 代码审查发现 ResearchAgent 和 ReportAgent 直接实例化 `AsyncOpenAI` 客户端，违反 `02_Agent设计规范.md` 原则四 "Agent不得直接访问 HTTP客户端"
* **根本原因**: 为快速实现功能而忽略了架构约束，将 LLM 调用逻辑直接写在 Agent 内部
* **最终解法**: 抽取 `LLMService` 单例类，Agent 通过构造函数注入 LLMService，符合依赖倒置原则

**踩坑 4: API 路由缺少版本前缀**
* **问题描述**: API 路由使用 `/tasks`、`/workflows/run`，而 `08_API设计.md` 要求使用 `/api/v1` 前缀
* **根本原因**: 实施时未严格对照 API 设计文档
* **最终解法**: 修改 `main.py` 中的路由注册，统一使用 `/api/v1/tasks`、`/api/v1/workflows`、`/api/v1/reports` 前缀

**踩坑 5: Service 层返回 ORM 对象**
* **问题描述**: TaskService.create_task() 直接返回 Task ORM 对象，违反 `09_Service设计.md` 第17节 "Service层禁止返回ORM对象"
* **根本原因**: 为简化实现而跳过 DTO 层
* **最终解法**: 创建 `services/dto/task_dto.py`，Service 方法返回 TaskDTO、WorkflowRunDTO、ReportDTO

**踩坑 6: 依赖遗漏和端口占用**
* **问题描述**: 启动时报错 `ModuleNotFoundError: No module named 'langgraph'`，以及端口 8000 被占用
* **根本原因**: pyproject.toml 遗漏 langgraph 依赖；Windows 下进程未正常退出导致端口占用
* **最终解法**: 添加依赖并 `uv sync`；换端口或 `taskkill` 杀死残留进程

### 3. 架构妥协 (Technical Debt)
* **Mock 数据设定**: 本阶段未引入 ToolRegistry，ResearchAgent 的输出由 LLM 直接生成假数据。此逻辑必须在 M4 阶段被真实 API 替换
* **简化工作流结构**: M1 仅实现 `Research → Report`，跳过了 PlannerAgent、ContextAgent、AnalysisAgent。这些将在 M2 阶段补充
* **缺少 sources 表和 tool_execution_logs 表**: 按照 `07_数据库设计.md` MVP 阶段应实现，但 M1 为简化而跳过，将在 M4 阶段补充
* **缺少 UnitOfWork 和 ServiceContainer**: `09_Service设计.md` 要求的事务边界控制和服务容器未实现，将在后续阶段补充
* **状态字符串硬编码**: WorkflowService 中使用 `"running"`、`"completed"` 等字符串而非 TaskStatus 枚举，需统一
* **Session 管理**: `get_db_session()` 在退出时自动 commit，绕过了 Service 层控制事务的规范

### 4. 后续开发的硬性规则 (Rules for Next Steps)

* **防错规则 1**: LangGraph 节点函数必须返回字典（或与状态结构兼容的 dict），不能返回 Pydantic 对象；`ainvoke` 返回值总是字典，需要显式转换
* **防错规则 2**: Agent 绝对不能直接实例化 HTTP 客户端或外部服务，必须通过 Service 层注入依赖
* **防错规则 3**: 每次实现新功能前，必须先查阅对应的设计文档（如 API 设计、Service 设计），确保路由前缀、返回类型、异常处理符合规范
* **架构红线 1**: LangGraph 中的 Agent 节点绝对不能直接互相调用方法，必须统一通过更新 `AgentState` 传递数据
* **架构红线 2**: Service 层禁止返回 ORM 对象，必须转换为 DTO；禁止直接接收 AsyncSession
* **衔接提醒**: 进入 M2 多 Agent 协作前，需要：
  1. 将 `graph.py` 中的模块级 Agent 实例化改为延迟初始化
  2. 考虑 PlannerAgent 的输入输出接口设计
  3. 为 ContextAgent 预留 MemoryService 接口（M3 才实现）

---

## Milestone 2: 多Agent工作流
**状态:** 🟢 已完成
**完成日期:** 2026-06-09

### 1. 核心产出 (What was done)
* **PlannerAgent**: 读取 `user_query`，输出 `research.topic`、`research.keywords`、`research.data_sources`
* **ContextAgent**: 读取 `research.topic`，输出 `context.context_items`（M2 阶段通过 LLM 生成领域背景，M3 接入 MemoryService）
* **AnalysisAgent**: 读取 `research` + `context`，输出 `analysis.hot_topics`、`analysis.trend_summary`、`analysis.insights`，同时判断 `need_more_data` 和 `information_gaps`
* **五节点 LangGraph 工作流**: 实现 `START → Planner → Context → Research → Analysis → Report → END`
* **Deep Research 回环**: 条件边 `continue_research` 根据 `need_more_data` 决定回到 Research 或继续到 Report，最多 `MAX_RESEARCH_ROUNDS = 3` 轮
* **延迟导入机制**: `_get_agents()` 函数解决 `app.agents ↔ app.workflows` 循环依赖
* **端到端验证通过**: 输入"MCP生态发展趋势"，完整执行五个节点，输出 2225 字符研究报告

### 2. 踩坑与返工记录 (Mistakes & Rework - 核心反思)

**踩坑 1: 循环导入 (app.agents ↔ app.workflows)**
* **问题描述**: `app.agents.__init__` → `planner_agent` → `app.services` → `workflow_service` → `graph.py` → `app.agents.planner_agent` 形成环路，启动报 `ImportError: cannot import name 'PlannerAgent' from partially initialized module`
* **根本原因**: `graph.py` 在模块顶层 `from app.agents.planner_agent import PlannerAgent`，而 `app.agents.__init__` 尚未初始化完成
* **最终解法**: `graph.py` 中使用 `_get_agents()` 延迟导入，不在模块顶层 import Agent

**踩坑 2: search_round 递增位置错误**
* **问题描述**: 代码审查发现 `search_round += 1` 写在 `graph.py` 的 `research_node` 中，而非 `ResearchAgent.run()` 内部
* **根本原因**: 混淆了"工作流控制逻辑"和"研究状态管理"的边界。`search_round` 属于 `ResearchState`，其递增是研究状态管理的一部分
* **最终解法**: 将 `search_round += 1` 移到 `ResearchAgent.run()` 内部，`graph.py` 只保留轮次上限检查

**踩坑 3: API 请求模型 task_name 必填**
* **问题描述**: 用户在 PowerShell 测试时只传 `{"user_query": "MCP生态发展趋势"}`，返回 422 错误 `"Field required: task_name"`
* **根本原因**: `CreateTaskRequest` 中 `task_name: str` 定义为必填字段，但对用户来说这是冗余信息
* **最终解法**: 改为 `task_name: str | None = None`，`TaskService.create_task()` 中 `task_name = task_name or user_query`

**踩坑 4: 条件边返回值与设计规范不一致**
* **问题描述**: 代码审查发现条件边返回 `"report"`，而 `04_Workflow设计规范.md` 第 5 节定义应返回 `"memory"`
* **根本原因**: M2 跳过 Memory 节点，直接返回了最终目标节点名称
* **最终解法**: 条件边返回 `"memory"`，图中 `"memory"` 映射到 `"report"`，M3 插入 MemoryNode 后映射自然生效

**踩坑 5: Agent 未读取完整状态域**
* **问题描述**: 代码审查发现 ResearchAgent 未读取 `state.context` 和 `information_gaps`，ReportAgent 未读取 `state.context` 和 `state.analysis`
* **根本原因**: 实现时只关注了核心功能，忽略了设计规范中定义的完整输入
* **最终解法**: 修改 prompt 构建逻辑，加入上下文摘要、信息缺口、分析结果

**踩坑 6: WorkflowManager.run() 接口签名不符**
* **问题描述**: 代码审查发现 `run(initial_state: AgentState)` 与 `10_WorkflowManager设计.md` 定义的 `run(task_id: str)` 不一致
* **根本原因**: M1 实现时由 WorkflowService 构建 AgentState 后传入，跳过了 Manager 内部构建
* **最终解法**: 改为 `run(task_id: str, user_query: str)`，Manager 内部构建 AgentState

### 3. 架构妥协 (Technical Debt)
* **ContextAgent 未接入 Memory**: M2 阶段通过 LLM 生成领域背景上下文，M3 必须替换为 `MemoryService.recall()`
* **ResearchAgent 仍使用 LLM 模拟数据**: 未接入真实工具（ArxivTool、GithubTool），M4 阶段必须替换
* **error_handler.py 冗余**: 按设计规范创建了统一错误处理节点，但 LangGraph 节点异常会直接中断图执行，无法自动路由到错误处理节点。实际采用每个节点内部 try/except 的方式，error_handler.py 已删除
* **状态字符串硬编码未修复**: WorkflowService 中仍使用 `"running"`、`"completed"` 等字符串而非 TaskStatus 枚举（M1 遗留）
* **Session 管理未修复**: `get_db_session()` 在退出时自动 commit，绕过了 Service 层控制事务的规范（M1 遗留）
* **MAX_RESEARCH_ROUNDS 重复定义**: `graph.py` 和 `AnalysisAgent` 各自定义了 `MAX_RESEARCH_ROUNDS = 3`，应统一为配置常量

### 4. 代码审核发现的问题 (Code Review Findings)

本阶段进行了两轮代码审核，发现并修复了以下问题：

* **第一轮审核** (3 个问题):
  1. `search_round` 递增在 graph.py 而非 ResearchAgent → 已修复
  2. 计划文档 ASCII 图包含 Memory 节点但实际未实现 → 文档错误，代码正确
  3. 对照 M1 教训检查 → 未犯同样错误

* **第二轮审核** (4 个违规):
  1. ResearchAgent 未读取 `state.context` 和 `information_gaps` → 已修复
  2. ReportAgent 未读取 `state.context` 和 `state.analysis` → 已修复
  3. 条件边返回 `"report"` 而非 `"memory"` → 已修复
  4. `WorkflowManager.run()` 参数类型不符 → 已修复

* **第三轮审核** (完整调用链):
  - 覆盖 API → Service → Manager → Graph → Agent → 状态模型 → 数据库
  - 未发现新违规项

* **教训**: 审核范围应覆盖完整调用链（包括 API 层），不能只审核 M2 新增/修改的文件

### 5. 后续开发的硬性规则 (Rules for Next Steps)

* **防错规则 1**: 代码审核必须覆盖完整调用链（API → Service → Manager → Graph → Agent），不能只审核当前 Milestone 新增的文件
* **防错规则 2**: Agent 的 `run()` 方法必须按照 `02_Agent设计规范.md` 中的"Agent与State映射表"读取所有规定的状态域，不能遗漏
* **防错规则 3**: 条件边返回值必须与 `04_Workflow设计规范.md` 一致（返回 `"memory"` 而非最终目标节点名称），通过图映射控制实际流转
* **防错规则 4**: API 请求模型中的可选字段应有合理默认值，不能依赖用户必填
* **架构红线 1**: `graph.py` 中禁止模块级 import Agent，必须使用延迟导入避免循环依赖
* **架构红线 2**: `search_round` 等研究状态管理逻辑必须在 Agent 内部，graph.py 节点函数只做工作流控制（轮次上限检查）
* **衔接提醒**: 进入 M3 记忆系统前，需要：
  1. ContextAgent 的 LLM 生成上下文替换为 `MemoryService.recall()`
  2. 新增 MemoryAgent 写入研究记忆、趋势快照、洞察
  3. 条件边映射从 `{"memory": "report"}` 改为 `{"memory": "memory"}`
  4. 统一 `MAX_RESEARCH_ROUNDS` 为配置常量
  5. 修复 M1 遗留：状态字符串硬编码、Session 管理
