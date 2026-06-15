import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.base import Base
from app.api import tasks, workflows, reports, tools
from app.memory.memory_service import MemoryService
from app.tools.base.tool_service import get_tool_service
from app.mcp import get_mcp_adapter

# 配置应用日志：显示 INFO 级别，格式简洁
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
# 关闭 httpx 的 DEBUG 日志（Qdrant/LLM 请求）
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def _register_tools():
    """注册所有工具到 ToolRegistry

    在应用启动时调用，确保 ToolService 可以找到所有工具。
    包括本地工具和 MCP 工具。

    遵循 docs/03_工具设计规范.md，通过 ToolService 统一管理工具注册，
    避免直接实例化具体工具类。
    """
    tool_service = get_tool_service()

    # 注册本地工具（通过 ToolService 统一管理）
    tool_service.register_local_tools()

    # 注册 MCP 工具
    mcp_adapter = get_mcp_adapter()
    try:
        mcp_count = await mcp_adapter.init_and_register()
        logger.info(f"MCP 工具注册完成，共 {mcp_count} 个")
    except Exception as e:
        logger.error(f"MCP 工具注册失败: {e}")
        # MCP 失败不影响本地工具使用

    logger.info("工具注册流程完成")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: 创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Startup: 初始化 Qdrant Collection
    memory_service = MemoryService()
    await memory_service.init()

    # Startup: 注册所有工具到 ToolRegistry (包括 MCP 工具)
    await _register_tools()

    yield

    # Shutdown: 断开所有 MCP 连接
    from app.mcp import get_mcp_client_manager
    client_manager = get_mcp_client_manager()
    await client_manager.disconnect_all()
    logger.info("MCP 连接已断开")

    # Shutdown: 关闭数据库连接
    await engine.dispose()


app = FastAPI(
    title="AI Research OS",
    description="AI前沿热点研究智能体",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 配置 - 允许前端开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由 - 使用 /api/v1 前缀
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["Workflows"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(tools.router, prefix="/api/v1/tools", tags=["Tools"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
