# AI Frontier Research Agent

> 基于 LangGraph 多智能体协作的自动化 AI 研究操作系统

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue?logo=python" />
  <img src="https://img.shields.io/badge/LangGraph-0.2+-green?logo=langchain" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-teal?logo=fastapi" />
  <img src="https://img.shields.io/badge/React-19-61dafb?logo=react" />
  <img src="https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql" />
  <img src="https://img.shields.io/badge/Qdrant-Vector_DB-red" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

---

## 项目简介

AI Frontier Research Agent 是一个面向 AI 前沿技术追踪与深度研究的 Agent 平台。系统通过 6 个专用 Agent 协作，模拟人类研究团队的工作流，实现从热点发现、深度调研到报告生成的全自动闭环。

**核心能力：**

- **自动研究**：输入研究主题，系统自动完成规划 → 采集 → 分析 → 报告的全流程
- **深度回环**：AnalysisAgent 动态判断信息缺口，驱动多轮数据补充（Deep Research）
- **长期记忆**：研究成果向量化存储，支持跨会话的知识召回与复用
- **实时可视化**：前端工作流画布实时展示 Agent 执行状态、工具调用与输出

---

## 系统架构

```
用户请求
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI (API Layer)                       │
│          /api/v1/tasks · /workflows · /reports              │
└──────────────────────────┬──────────────────────────────────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    ▼                      ▼                      ▼
┌─────────┐       ┌──────────────┐       ┌──────────────┐
│ Service │       │   Workflow   │       │    Memory    │
│  Layer  │       │    Layer     │       │    Layer     │
│         │       │  LangGraph   │       │ PostgreSQL + │
│         │       │  Agent 编排  │       │   Qdrant     │
└────┬────┘       └──────┬───────┘       └──────────────┘
     │                   │
     ▼                   ▼
┌─────────┐       ┌──────────────┐
│  Repo   │       │  Agent ×6    │
│  Layer  │       │  只负责推理   │
└────┬────┘       └──────┬───────┘
     │                   │
     ▼                   ▼
┌─────────┐       ┌──────────────┐
│   DB    │       │  Tool ×4     │
│PostgreSQL│      │  Arxiv/GitHub │
└─────────┘       │  HF/Web      │
                  └──────────────┘
```

---

## 多智能体工作流

基于 LangGraph 状态图编排，6 个 Agent 流水线协作：

```
START → Planner → Context → Research → Analysis ──┐
                                       │           │
                                  need_more?       │
                                   /      \        │
                              Research    Memory ──┤
                              (回环)        │       │
                                       Report ─────┘
                                           │
                                          END
```

| Agent | 职责 | 说明 |
|-------|------|------|
| **Planner** | 研究规划 | 将用户查询拆解为 topic、keywords、data_sources |
| **Context** | 上下文构建 | 优先从记忆召回历史，无历史时 LLM 生成背景 |
| **Researcher** | 数据采集 | 调用真实工具获取论文/仓库/模型，失败降级为 LLM 模拟 |
| **Analyst** | 分析推理 | 提取热点、趋势、洞察，判断是否需要补充数据 |
| **Memory** | 记忆沉淀 | 三类记忆向量化写入 Qdrant，含去重与置信度过滤 |
| **Report** | 报告生成 | 生成结构化 Markdown 报告，标注数据来源 |

---

## 技术栈

### 后端

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.12+ |
| Web 框架 | FastAPI (全异步) |
| Agent 编排 | LangGraph |
| LLM | OpenAI API (gpt-4o-mini) |
| ORM | SQLAlchemy 2.0 + asyncpg |
| 数据库迁移 | Alembic |
| 向量数据库 | Qdrant |
| Embedding | FastEmbed (bge-small-zh-v1.5) |
| MCP 集成 | mcp SDK |

### 前端

| 类别 | 技术 |
|------|------|
| 框架 | React 19 + TypeScript 6 |
| 构建 | Vite 8 |
| 样式 | TailwindCSS 4 |
| 工作流可视化 | @xyflow/react |
| 状态管理 | Zustand + TanStack Query |
| 路由 | React Router 7 |
| Markdown 渲染 | react-markdown |

### 基础设施

| 服务 | 用途 |
|------|------|
| PostgreSQL 15 | 结构化数据存储 |
| Qdrant | 向量检索 |
| Docker | 基础设施容器化 |

---

## 项目结构

```
AI热点/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI 路由层
│   │   ├── services/         # 业务服务层
│   │   ├── repositories/     # 数据访问层
│   │   ├── agents/           # 6 个专用 Agent
│   │   ├── workflows/        # LangGraph 工作流定义
│   │   ├── tools/            # 工具体系 (Arxiv/GitHub/HF/Web)
│   │   ├── memory/           # 记忆系统 (Qdrant + Embedding)
│   │   ├── mcp/              # MCP 协议集成
│   │   ├── schemas/          # Pydantic 数据模型
│   │   ├── db/               # SQLAlchemy ORM 模型
│   │   ├── core/             # 配置管理
│   │   └── main.py           # 应用入口
│   ├── tests/                # 单元测试
│   └── pyproject.toml        # Python 项目配置
│
├── frontend/
│   ├── src/
│   │   ├── pages/            # 页面组件
│   │   ├── features/         # 功能模块 (研究/工作流/报告/记忆)
│   │   ├── components/       # 通用组件
│   │   ├── api/              # API 客户端
│   │   ├── hooks/            # React Query Hooks
│   │   ├── stores/           # Zustand 状态
│   │   ├── types/            # TypeScript 类型
│   │   └── utils/            # 工具函数
│   └── package.json          # 前端依赖
│
├── docs/                     # 设计文档 (13 篇)
├── docker-compose.yml        # PostgreSQL + Qdrant 编排
└── CLAUDE.md                 # 项目架构规范
```

---

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose

### 1. 启动基础设施

```bash
docker compose up -d
```

启动 PostgreSQL (端口 5432) 和 Qdrant (端口 6333)。

### 2. 启动后端

```bash
cd backend

# 安装依赖 (使用 uv)
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY

# 运行数据库迁移
uv run alembic upgrade head

# 启动服务
uv run uvicorn app.main:app --reload --port 8000
```

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000 即可使用。

---

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/tasks` | 创建研究任务 |
| `GET` | `/api/v1/tasks` | 获取任务列表 |
| `POST` | `/api/v1/workflows/run` | 运行工作流 |
| `GET` | `/api/v1/workflows/{id}/status` | 查询工作流状态 |
| `GET` | `/api/v1/reports` | 获取报告列表 |
| `GET` | `/api/v1/tools` | 获取可用工具列表 |
| `GET` | `/api/v1/memories` | 搜索记忆 |
| `GET` | `/health` | 健康检查 |

---

## 示例用法

### 创建研究任务

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"user_query": "MCP生态发展趋势"}'
```

### 运行工作流

```bash
curl -X POST http://localhost:8000/api/v1/workflows/run \
  -H "Content-Type: application/json" \
  -d '{"task_id": "<task-id>"}'
```

---

## 设计原则

1. **状态驱动**：AgentState 是唯一事实来源，Agent 间通过 State 通信
2. **强类型**：全链路 Pydantic 模型，禁止裸 dict 作为核心业务对象
3. **Agent 只推理**：Agent 只负责 LLM 调用，不直接访问数据库/网络/MCP
4. **工具统一管理**：BaseTool → ToolRegistry → ToolService 三层抽象
5. **分层架构**：API → Service → Repository → Database，禁止跳层
6. **容错降级**：节点级 try-except + Agent 级降级 + 工具级重试

---

## 文档

详细设计文档位于 `docs/` 目录：

| 文档 | 内容 |
|------|------|
| 01_状态模型设计 | AgentState 及子状态定义 |
| 02_Agent设计规范 | Agent 职责、输入输出、约束 |
| 03_工具设计规范 | BaseTool、ToolRegistry、ToolService |
| 04_Workflow设计规范 | LangGraph 图定义、节点函数、条件边 |
| 05_记忆系统设计 | PostgreSQL + Qdrant 双存储架构 |
| 06_MCP设计规范 | MCP 协议集成方案 |
| 07_数据库设计 | ORM 模型、表结构 |
| 08_API设计 | RESTful 端点规范 |
| 09_Service设计 | 业务服务层规范 |
| 10_WorkflowManager设计 | 工作流管理器规范 |
| 11_前端设计 | React 组件架构 |
| 12_开发实施计划 | 8 个 Milestone 规划 |
| 13_ClaudeCode开发指南 | AI 辅助开发规范 |

---

## License

MIT
