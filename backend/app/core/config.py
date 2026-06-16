from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_hotspot"

    # OpenAI
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Embedding (本地模型，首次运行自动下载约100MB)
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    embedding_dimension: int = 512
    embedding_cache_dir: str = "./models"
    hf_endpoint: str = "https://hf-mirror.com"

    # Tools - 工具层配置
    github_api_token: str = ""  # 可选，提高 GitHub API 限流额度
    tool_timeout_seconds: int = 30  # 工具 HTTP 请求超时时间
    tool_max_retries: int = 3  # 工具调用失败最大重试次数
    arxiv_max_results: int = 10  # Arxiv 单次搜索最大返回条数
    huggingface_max_results: int = 10  # HuggingFace 单次搜索最大返回条数
    tavily_api_key: str = ""  # Tavily 搜索 API Key

    # Workflow - 工作流配置
    max_research_rounds: int = 3  # Deep Research 最大研究轮次

    # App
    app_env: str = "development"
    app_debug: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
