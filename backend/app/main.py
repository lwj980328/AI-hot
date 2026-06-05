from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.api import tasks, workflows, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: 创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
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
