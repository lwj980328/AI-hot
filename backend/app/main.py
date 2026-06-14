import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.api import tasks, workflows, reports
from app.memory.memory_service import MemoryService

# 配置应用日志：显示 INFO 级别，格式简洁
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
# 关闭 httpx 的 DEBUG 日志（Qdrant/LLM 请求）
logging.getLogger("httpx").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: 创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Startup: 初始化 Qdrant Collection
    memory_service = MemoryService()
    await memory_service.init()

    yield

    # Shutdown: 关闭数据库连接
    await engine.dispose()


app = FastAPI(
    title="AI Research OS",
    description="AI前沿热点研究智能体",
    version="0.1.0",
    lifespan=lifespan,
)

# 注册路由 - 使用 /api/v1 前缀
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["Workflows"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
