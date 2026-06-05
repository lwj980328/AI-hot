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
