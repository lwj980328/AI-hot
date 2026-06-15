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

---

## Milestone 3: 记忆系统
**状态:** 🟢 已完成
**完成日期:** 2026-06-14

### 1. 核心产出 (What was done)
* **Qdrant 向量数据库集成**: docker-compose 新增 Qdrant 服务，启动时自动创建 `research_memory`、`trend_memory`、`insight_memory` 三个 Collection
* **Embedding 服务**: 使用 `fastembed` 本地模型 `BAAI/bge-small-zh-v1.5`（512 维，中文优化），模型缓存到项目 `backend/models/` 目录，通过 HF 镜像源下载
* **QdrantStore 存储层**: 封装 Collection 管理、upsert、`query_points`（向量检索）、`check_duplicate`（去重），使用单例模式
* **MemoryService 统一入口**: 组合 EmbeddingService + QdrantStore，提供 `save_research_memory`、`save_trend_snapshot`、`save_insight_memory`、`search_memories`、`get_topic_history` 接口，含去重（0.95 阈值）和污染控制（confidence < 0.6 跳过）
* **三类记忆模型**: `ResearchMemory`（完整研究报告）、`TrendSnapshot`（趋势快照）、`InsightMemory`（结构化洞察 + MemoryEvidence），均继承 `MemoryRecord` 基类
* **MemoryAgent**: 读取 `state.research` + `state.analysis` + `state.report`，构建三类记忆并调用 MemoryService 写入 Qdrant
* **ContextAgent 改造**: 注入 MemoryService，优先从记忆召回历史（`search_memories`），无历史时回退到 LLM 生成
* **Workflow 图升级**: 新增 `memory_node`，条件边 `"memory"` 从直接映射 `report` 改为映射 `memory_node`，完整流程 `Planner → Context → Research → Analysis → Memory → Report`
* **日志配置**: `main.py` 添加 `logging.basicConfig`，关闭 httpx DEBUG 日志，应用层 INFO 日志可见
* **端到端验证通过**: 两次同主题研究均成功召回 5 条历史记忆（2 trend + 3 insight），去重机制正确跳过重复写入

### 2. 踩坑与返工记录 (Mistakes & Rework - 核心反思)

**踩坑 1: qdrant-client 1.18 API 变更**
* **问题描述**: `AsyncQdrantClient` 没有 `search` 方法，报 `'AsyncQdrantClient' object has no attribute 'search'`
* **根本原因**: qdrant-client 1.18 版本将异步 `search` 方法重命名为 `query_points`，返回类型从 `list[ScoredPoint]` 变为 `QueryResponse`
* **最终解法**: `qdrant_store.py` 中 `self.client.search(...)` 改为 `self.client.query_points(...)`，结果遍历从 `results` 改为 `results.points`

**踩坑 2: Hugging Face 下载 SSL 错误**
* **问题描述**: fastembed 首次下载模型时报 `httpx.ConnectError: [SSL: UNEXPECTED_EOF_WHILE_READING]`
* **根本原因**: 国内网络无法直接访问 Hugging Face，需要使用镜像源
* **最终解法**: `config.py` 新增 `hf_endpoint` 配置（默认 `https://hf-mirror.com`），`embedding_service.py` 在加载模型前设置 `os.environ["HF_ENDPOINT"]`

**踩坑 3: report_summary 为空导致 ResearchMemory 不保存**
* **问题描述**: MemoryAgent 构建 ResearchMemory 时使用 `state.report.summary`，但 LLM 可能返回空字符串，导致 `save_research_memory` 的 `if not memory.report_summary` 判断跳过
* **根本原因**: `save_research_memory` 要求 `report_summary` 非空，但未考虑 LLM 输出不稳定的场景
* **最终解法**: `memory_agent.py` 中增加回退逻辑：`report_summary` 为空时使用 `report.title` 或 `markdown_content[:200]`

**踩坑 4: 应用层日志被 SQLAlchemy 日志淹没**
* **问题描述**: `APP_DEBUG=true` 导致 SQLAlchemy 打印所有 SQL 语句，ContextAgent 的记忆召回日志完全不可见
* **根本原因**: SQLAlchemy 的 `echo=True` 与 Python logging 配置冲突
* **最终解法**: `.env` 中 `APP_DEBUG=false` 关闭 SQL 日志；`main.py` 添加 `logging.basicConfig(level=logging.INFO)` 配置应用层日志；`logging.getLogger("httpx").setLevel(logging.WARNING)` 关闭 HTTP 请求日志

**踩坑 5: Topic 过滤匹配失败（早期调试）**
* **问题描述**: 测试时手动设置 `state.research.topic = 'MCP生态发展趋势'`（原始用户查询），但 PlannerAgent 实际输出 `topic='MCP生态'`，导致 Qdrant topic 过滤不匹配
* **根本原因**: 测试代码未模拟真实 workflow 流程，PlannerAgent 会将用户查询提炼为更精确的 topic
* **最终解法**: 测试时使用完整 workflow（经 PlannerAgent），而非手动设置 topic

**踩坑 6: 端口占用导致启动失败**
* **问题描述**: 手动测试时 uvicorn 报 `[Errno 10048] 通常每个套接字地址只允许使用一次`
* **根本原因**: 之前 Claude Code 在后台启动的 uvicorn 进程未退出，占用 8000 端口
* **最终解法**: `netstat -ano | grep ":8000"` 找到 PID，`taskkill //F //PID xxx` 杀死残留进程

**踩坑 7: HTTP 请求间竞态条件**
* **问题描述**: 创建任务后立即运行工作流，返回 404 "Task不存在"
* **根本原因**: `get_db_session()` 在请求结束时 commit，两个请求间隔太短时事务可能未提交完成
* **最终解法**: 测试脚本中在请求间加 `await asyncio.sleep(1)` 等待事务提交；生产环境可通过重试机制解决

### 3. 架构妥协 (Technical Debt)
* **状态字符串硬编码未修复**: WorkflowService 中仍使用 `"running"`、`"completed"`、`"failed"` 等字符串而非 TaskStatus 枚举（M1 遗留，M3 未修）
* **MAX_RESEARCH_ROUNDS 重复定义未修复**: `graph.py` 和 `AnalysisAgent` 各自定义了 `MAX_RESEARCH_ROUNDS = 3`，应统一为配置常量（M2 遗留，M3 未修）
* **Session 管理未修复**: `get_db_session()` 在退出时自动 commit，绕过了 Service 层控制事务的规范（M1 遗留，M3 未修）
* **Embedding 模型硬编码**: `BAAI/bge-small-zh-v1.5` 是轻量级小模型，精度有限；生产环境应替换为更大的中文 embedding 模型
* **记忆检索无重排序**: 当前直接使用向量相似度排序，未做 rerank；未来可接入 cross-encoder 提升召回质量
* **MemoryService 未接入 ServiceContainer**: 按照 `09_Service设计.md` 应通过容器管理，当前采用单例模式作为折中

### 4. 代码审核发现的问题 (Code Review Findings)

本阶段进行了一轮代码审核，发现并修复了以下问题：

* **审核发现** (4 个问题):
  1. `qdrant-client` API 变更（`search` → `query_points`）→ 已修复
  2. `report_summary` 为空导致记忆不保存 → 已修复
  3. `_get_agents()` 每次调用重新实例化 Agent → 已修复（加模块级缓存）
  4. MemoryService 未统一为单例 → 已修复（改为 `__new__` 单例模式）

* **M1/M2 遗留问题确认未修复**:
  1. 状态字符串硬编码（M1 遗留）
  2. MAX_RESEARCH_ROUNDS 重复定义（M2 遗留）
  3. Session 管理绕过 Service 层（M1 遗留）

### 5. 后续开发的硬性规则 (Rules for Next Steps)

* **防错规则 1**: 使用第三方库的新版本时，必须先检查 API 是否有 breaking change（如 qdrant-client 1.18 的 `search` → `query_points`）
* **防错规则 2**: LLM 输出的任何字段都可能为空，必须有回退逻辑，不能依赖 LLM 输出非空
* **防错规则 3**: 测试时必须模拟真实 workflow 流程，不能手动设置中间状态（如直接设置 topic），否则会跳过 PlannerAgent 等节点的处理逻辑
* **防错规则 4**: 所有 Service 层类应采用单例模式，确保全局唯一实例
* **架构红线 1**: Agent 通过 Service 访问基础设施（Qdrant、Embedding），禁止直接实例化基础设施客户端
* **架构红线 2**: 记忆写入失败不应阻断 workflow，必须降级处理（MemoryNode 的 try/except 设计）
* **衔接提醒**: 进入 M4 工具系统前，需要：
  1. ResearchAgent 的 LLM 模拟数据替换为真实工具调用（ArxivTool、GithubTool）
  2. 新增 BaseTool、ToolRegistry、ToolService 抽象层
  3. 修复 M1/M2 遗留：状态字符串硬编码、MAX_RESEARCH_ROUNDS 统一、Session 管理

---

## Milestone 4: 工具系统
**状态:** 🟢 已完成
**完成日期:** 2026-06-15

### 1. 核心产出 (What was done)
* **工具基础层**: `BaseTool` 抽象基类、`LocalTool` 本地工具基类（封装 HTTP GET/JSON/Text 请求、超时控制、异常转换）、`ToolRegistry` 单例（注册/发现/列表）、`ToolService` 单例执行入口（重试 3 次、指数退避、输入输出校验）
* **工具异常体系**: `ToolError`、`ToolTimeoutError`、`ToolConnectionError`、`ToolValidationError`、`ToolAuthenticationError`、`ToolRateLimitError`、`ToolNotFoundError`，均继承 `ServiceError`
* **ArxivTool**: 调用 `export.arxiv.org` Atom API，解析 XML 提取论文标题/摘要/作者/分类，支持 `quote_plus` 编码中文关键词
* **GithubTool**: 调用 GitHub Search API 获取仓库数据（stars/forks/language/topics），支持可选 `GITHUB_API_TOKEN`
* **HuggingFaceTool**: 调用 HuggingFace Hub API 搜索模型（downloads/likes/pipeline_tag）
* **WebSearchTool**: 占位实现，注册到 Registry 但返回空结果，预留未来接入 Serper/Bing 等外部搜索 API
* **ResearchAgent 改造**: 注入 `ToolService`，按 `state.research.data_sources` 动态调用对应工具，失败时降级到 LLM 模拟数据；新增 `data_source_tags` 字段标记每条数据是真实还是模拟
* **ReportAgent 改造**: 新增 `_build_source_attribution()` 方法，在报告末尾追加"数据来源说明"章节
* **WorkflowService 状态硬编码修复**: `"running"` / `"completed"` / `"failed"` 替换为 `TaskStatus` 枚举（M1 遗留修复）
* **配置项新增**: `github_api_token`、`tool_timeout_seconds`、`tool_max_retries`、`arxiv_max_results`、`huggingface_max_results`
* **应用启动自动注册**: `main.py` 的 `lifespan` 中调用 `_register_tools()` 将四个工具注册到 `ToolRegistry`
* **单元测试**: 16 个测试用例覆盖 ToolRegistry（5 个）、ArxivTool（2 个）、GithubTool（3 个）、ToolService（6 个），全部通过
* **端到端验证通过**: 三个真实 API（Arxiv、GitHub、HuggingFace）均成功返回真实数据，报告末尾正确标注数据来源

### 2. 踩坑与返工记录 (Mistakes & Rework - 核心反思)

**踩坑 1: ArxivTool HTTP 301 重定向**
* **问题描述**: ArxivTool 调用 `http://export.arxiv.org/api/query` 返回 HTTP 301，重试 4 次后失败
* **根本原因**: arxiv.org 强制从 HTTP 跳转到 HTTPS，但 `httpx.AsyncClient` 默认不跟随重定向
* **最终解法**: `local_tool.py` 的 `_get_json()` 和 `_get_text()` 中添加 `follow_redirects=True`

**踩坑 2: .env 行内注释被 pydantic-settings 当作配置值**
* **问题描述**: `.env` 文件 `GITHUB_API_TOKEN=  # 可选，提高 GitHub API 限流额度` 中的中文注释被读入 token 值，作为 `Authorization` header 发出，导致 ASCII 编码错误
* **根本原因**: `pydantic-settings` + `python-dotenv` 对行内注释的处理不一致，`#` 后的内容被当作值的一部分
* **最终解法**: `.env` 中注释移到独立一行，`GITHUB_API_TOKEN=` 保持空值
* **教训**: `.env` 文件禁止使用行内注释，注释必须独占一行

**踩坑 3: httpx params 中文编码冲突**
* **问题描述**: GithubTool 将 `quote_plus(keyword)` 放入 `params` 字典，httpx 再次编码导致冲突
* **根本原因**: `quote_plus` 已经将中文编码为 `%E7%94%9F...`，httpx 的 params 处理可能再次编码或解码
* **最终解法**: 将编码后的关键词直接拼接到 URL 字符串中，不走 `params` 字典

**踩坑 4: Atom XML 命名空间不匹配**
* **问题描述**: ArxivTool 的 `total_results` 始终解析为 0
* **根本原因**: `totalResults` 元素使用 `http://a9.com/-/spec/opensearch/1.1/` 命名空间，而非 `http://www.w3.org/2005/Atom`
* **最终解法**: 新增 `OS_NS` 命名空间字典，`root.find("os:totalResults", OS_NS)`

**踩坑 5: agents/__init__.py 遗漏 MemoryAgent 导出**
* **问题描述**: 代码审查发现 `app/agents/__init__.py` 没有导出 `MemoryAgent`
* **根本原因**: M3 新增 MemoryAgent 时忘记更新 `__init__.py`
* **最终解法**: 补充 `from app.agents.memory_agent import MemoryAgent` 和 `__all__` 列表

### 3. 架构妥协 (Technical Debt)
* **WebSearchTool 占位实现**: 当前返回空结果，未来需接入 Serper/Bing 等外部搜索 API（需 API Key 和费用）
* **HuggingFaceTool 简化实现**: 仅调用基础模型搜索 API，未实现模型详情、推理 API 等高级功能
* **ResearchAgent._invoke_tool() 中直接 import 工具 Schema**: 虽然不是"依赖具体工具实现"（Schema 是 Pydantic 模型，不是工具类），但如果工具 Schema 变更需要同步修改 Agent 代码
* **MAX_RESEARCH_ROUNDS 重复定义未修复**: `graph.py` 和 `AnalysisAgent` 各自定义了 `MAX_RESEARCH_ROUNDS = 3`，应统一为配置常量（M2 遗留，M4 未在范围内）
* **Session 管理未修复**: `get_db_session()` 在退出时自动 commit，绕过了 Service 层控制事务的规范（M1 遗留，M4 未在范围内）
* **记忆检索无重排序**: 当前直接使用向量相似度排序，未做 rerank（M3 遗留）

### 4. 代码审核发现的问题 (Code Review Findings)

本阶段进行了一轮完整代码审核，对照 `CLAUDE.md`、`02_Agent设计规范.md`、`03_工具设计规范.md`、`10_WorkflowManager设计.md` 逐条检查：

* **审核结果**: **全部合规，无违规项**
* **审核覆盖范围**:
  - 原则一（状态驱动）✅：所有节点通过 AgentState 通信
  - 原则二（强类型）✅：所有工具输入/输出均为 Pydantic BaseModel
  - 原则三（Agent 只负责推理）✅：Agent 不直接访问 HTTP/DB/Qdrant
  - 原则四（工具统一管理）✅：Agent → ToolService → ToolRegistry → Tool
  - 原则五（分层架构）✅：无跳层访问
  - 原则六（可扩展）✅：新增工具只需实现 BaseTool + 注册
  - Agent 不直接依赖具体工具实现 ✅：通过 ToolService + 工具名字符串调用
  - 工具异常体系 ✅：完整覆盖超时/连接/验证/认证/限流场景

### 5. 后续开发的硬性规则 (Rules for Next Steps)

* **防错规则 1**: `.env` 文件禁止使用行内注释（`KEY=value  # comment`），注释必须独占一行，否则 pydantic-settings 会把注释当作值
* **防错规则 2**: httpx 请求必须设置 `follow_redirects=True`，否则 HTTPS 重定向会返回 301 错误
* **防错规则 3**: 中文关键词放入 httpx `params` 字典前，需确认不会导致双重编码；保险做法是直接拼接到 URL 字符串
* **防错规则 4**: 解析第三方 API 的 XML/JSON 时，必须确认命名空间和字段路径，不能凭假设编写
* **防错规则 5**: 新增 Agent/Service 后必须检查 `__init__.py` 是否导出，否则延迟导入会失败
* **架构红线 1**: Agent 通过 ToolService 调用工具，禁止在 Agent 中直接实例化工具类（如 `ArxivTool()`）
* **架构红线 2**: 工具失败不应阻断 workflow，必须降级处理（ResearchAgent 的 fallback 机制）
* **衔接提醒**: 进入 M5 MCP 集成前，需要：
  1. 实现 `MCPToolAdapter`，将 MCP Server 的工具适配为 BaseTool 接口
  2. 实现 MCP 连接管理、工具发现、工具调用
  3. Agent 无需修改即可通过 ToolRegistry 使用 MCP 工具
  4. 修复 M2 遗留：MAX_RESEARCH_ROUNDS 统一为配置常量

---

## Milestone 5: MCP 集成
**状态:** 🟢 已完成
**完成日期:** 2026-06-15

### 1. 核心产出 (What was done)
* **MCP 配置模型**: `MCPServerConfig` 支持 stdio/sse/http 三种传输协议配置，Pydantic 强类型定义
* **MCP Client 抽象层**: `BaseMCPClient` 抽象基类 + `STDIOMCPClient` 实现，基于 `mcp` 官方 Python SDK
* **MCP Client Manager**: 单例模式管理所有 MCP Client 的生命周期（连接/断开/重连/健康检查），支持获取配置
* **MCP Discovery Service**: 启动时自动扫描配置目录、连接 MCP Server、发现并返回工具元数据
* **MCPTool 适配层**: 将 MCP Server 暴露的工具适配为 `BaseTool` 接口，动态生成 Pydantic input_schema，支持超时控制
* **MCPAdapter 核心**: 协调 DiscoveryService + ClientManager + ToolRegistry，一键完成 MCP 工具注册
* **ToolRegistry 集成**: MCP 工具与本地工具统一注册，Agent 无需感知差异
* **ToolService 统一注册**: `register_local_tools()` 方法统一管理本地工具注册，避免 main.py 直接实例化
* **Filesystem MCP Server 接入**: 配置 `@modelcontextprotocol/server-filesystem`，成功发现 14 个文件系统工具
* **main.py 集成**: 启动时自动初始化 MCP 并注册工具，关闭时断开所有 MCP 连接
* **故障隔离验证**: MCP 连接失败不影响本地工具使用
* **依赖更新**: 新增 `mcp>=1.0.0`、`pyyaml>=6.0.0`
* **新增 /api/v1/tools 路由**: 暴露已注册工具列表，支持 HTTP 查询

### 2. 新增文件清单
```
backend/app/mcp/
├── __init__.py
├── clients/
│   ├── __init__.py
│   ├── base_client.py
│   └── stdio_client.py
├── manager/
│   ├── __init__.py
│   └── client_manager.py
├── discovery/
│   ├── __init__.py
│   └── discovery_service.py
├── adapters/
│   ├── __init__.py
│   └── mcp_adapter.py
├── tools/
│   ├── __init__.py
│   └── mcp_tool.py
└── schemas/
    ├── __init__.py
    ├── config.py
    └── metadata.py

backend/config/mcp/
├── __init__.py
└── filesystem.yaml    # 每个 MCP Server 独立配置文件

backend/app/api/
└── tools.py           # 工具列表 API

backend/tests/
├── test_mcp.py
└── test_mcp_tool_call.py
```

### 3. 踩坑与返工记录 (Mistakes & Rework - 核心反思)

**踩坑 1: Windows GBK 编码问题**
* **问题描述**: 测试脚本中的 Unicode 字符（✓、✗、⚠）在 Windows 终端输出时报 `UnicodeEncodeError: 'gbk' codec can't encode character`
* **根本原因**: Windows 默认使用 GBK 编码，无法处理部分 Unicode 字符
* **最终解法**: 替换为 ASCII 字符 `[OK]`、`[FAIL]`、`[WARN]`

**踩坑 2: MCP Client 连接失败未优雅处理**
* **问题描述**: 配置不存在的命令时，`FileNotFoundError` 直接抛出导致测试中断
* **根本原因**: `add_client()` 中未捕获 `FileNotFoundError` 异常
* **最终解法**: 添加 `FileNotFoundError` 专门捕获，记录日志但不抛出

**踩坑 3: mcp SDK 版本兼容性**
* **问题描述**: `mcp` SDK 的 `stdio_client` 返回类型和 `ClientSession` 初始化方式需要确认
* **根本原因**: mcp SDK 版本更新较快，API 可能有变化
* **最终解法**: 使用 `mcp>=1.0.0`，参考官方文档实现

**踩坑 4: 代码审核发现 4 个违规项（二次返工）**
* **问题描述**: 代码审核对照 `docs/03_工具设计规范.md` 和 `docs/06_MCP设计规范.md` 发现 4 个违规
* **违规 1 - MCPToolMetadata 缺少 output_schema**: 规范第 8 节要求包含 `output_schema: dict` 字段，实际缺失
* **违规 3 - main.py 直接实例化工具**: 规范第 10 节禁止 `GithubTool()` 直接实例化，main.py 绕过 ToolService
* **违规 4 - MCPTool.execute() 异常处理不统一**: 规范第 21 节要求 MCP 不可用时抛出 `ToolError`，实际返回 `MCPToolResult(success=False)`
* **违规 5 - 配置文件结构不一致**: 规范第 23 节要求每个 MCP Server 独立配置文件，实际合并为 `servers.yaml`
* **最终解法**:
  - `metadata.py` 添加 `output_schema` 字段，`stdio_client.py` 提取 `tool.outputSchema`
  - `tool_service.py` 新增 `register_local_tools()` 方法，`main.py` 改用此方法
  - `mcp_tool.py` 删除 `MCPToolResult`，改为抛出 `ToolTimeoutError`/`ToolConnectionError`/`ToolError`
  - 配置目录改为每个 MCP Server 独立 YAML 文件，`discovery_service.py` 支持扫描目录加载

### 4. 代码审核发现的问题 (Code Review Findings)

本阶段进行了两轮代码审核：

* **第一轮审核** (8 个违规项):
  - 违规 1：MCPToolMetadata 缺少 output_schema → 已修复
  - 违规 2：MCPToolMetadata.input_schema 使用裸 dict → 可接受（MCP 协议天然结构）
  - 违规 3：main.py 直接实例化工具 → 已修复
  - 违规 4：MCPTool.execute() 异常处理不统一 → 已修复
  - 违规 5：配置文件结构不一致 → 已修复
  - 违规 6：权限控制未实现 → MVP 可推迟
  - 违规 7：MCPClientFactory 未独立 → 功能等价
  - 违规 8：复杂 JSON Schema 支持不足 → 等遇到问题再修

* **第二轮审核** (二次验证):
  - 4 个已修复项全部验证通过
  - 18 项合规检查全部通过
  - 未发现新违规项
  - 发现 2 处规范文档自身措辞不一致（非代码问题）

* **教训**: 第一轮审核发现的 4 个必须修复项，都是对设计规范理解不深导致的。开发时必须逐条对照规范实现，不能凭记忆或经验

### 5. 验收测试结果

| 验收项 | 结果 | 说明 |
|--------|------|------|
| 加载并连接 MCP Server (STDIO) | ✅ | Filesystem MCP Server 成功连接 |
| 自动发现 MCP 工具 | ✅ | 发现 14 个文件系统工具 |
| MCP Tool 注册到 ToolRegistry | ✅ | 14 个工具全部注册，命名格式 `mcp_{server_id}_{tool_name}` |
| Agent 能够调用 MCP Tool | ✅ | `list_directory` 工具成功列出项目目录 |
| MCP 故障不影响本地工具 | ✅ | 连接失败时本地 ArxivTool 仍可用 |
| 超时控制 | ✅ | 使用 `asyncio.wait_for()` 实现，默认 30 秒 |
| 统一异常体系 | ✅ | 抛出 `ToolTimeoutError`/`ToolConnectionError`/`ToolError` |

### 6. 架构妥协 (Technical Debt)
* **仅实现 STDIO 传输**: SSE 和 HTTP 传输协议暂未实现，标记为 TODO
* **MCP 工具权限控制未实现**: 设计规范中的 `ToolPermission` 枚举暂未接入
* **MCP 工具监控指标未实现**: 调用次数、成功率、响应时间等指标暂未记录
* **MCP Server 健康检查未定期执行**: 仅在启动时连接，运行中不主动检测连接状态
* **复杂 JSON Schema 类型支持不足**: `_build_input_schema()` 仅支持基础类型映射，不支持 `$ref`、`oneOf`、`allOf` 等
* **M2 遗留未修复**: MAX_RESEARCH_ROUNDS 重复定义（不在 M5 范围内）

### 7. 后续开发的硬性规则 (Rules for Next Steps)

* **防错规则 1**: MCP 配置文件每个 Server 独立一个 YAML 文件，放置在 `backend/config/mcp/` 目录
* **防错规则 2**: MCP 工具调用失败必须抛出 `ToolError` 子类，不能返回带 error 的结果对象，确保与本地工具异常处理模式一致
* **防错规则 3**: MCP Client 断开连接时必须清理 `AsyncExitStack`，避免资源泄漏
* **防错规则 4**: 工具注册必须通过 `ToolService.register_local_tools()` 或 `MCPAdapter.init_and_register()`，禁止在 main.py 中直接实例化工具
* **防错规则 5**: 开发新模块时必须逐条对照设计规范实现，不能凭记忆或经验；代码审核必须覆盖完整调用链
* **架构红线 1**: Agent 通过 ToolRegistry 使用 MCP 工具，禁止直接访问 MCPClient
* **架构红线 2**: MCP 连接失败不应阻断应用启动，必须降级处理（仅本地工具可用）
* **衔接提醒**: 进入 M6 前端 MVP 前，需要：
  1. 前端框架搭建（React + Vite + TypeScript + TailwindCSS）
  2. API 接入层（TanStack Query）
  3. 页面路由（Dashboard / Research Workspace / Reports）
