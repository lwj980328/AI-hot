"""向量化服务 - 将文本转换为向量

使用 fastembed 本地模型（BAAI/bge-small-zh-v1.5）。
- 不需要 GPU，CPU 即可运行
- 首次运行自动下载模型到本地缓存（约100MB）
- 模型缓存位置：项目根目录 ./models/（可通过 embedding_cache_dir 配置）
- 支持中文
"""

import os
import logging
from pathlib import Path
from fastembed import TextEmbedding
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding 服务（本地模型）"""

    _instance: "EmbeddingService | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            settings = get_settings()

            # 设置 HF 镜像源（必须在模型加载前设置）
            if settings.hf_endpoint:
                os.environ["HF_ENDPOINT"] = settings.hf_endpoint
                logger.info(f"HF 镜像源: {settings.hf_endpoint}")

            cache_dir = Path(settings.embedding_cache_dir).resolve()
            cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(
                f"加载 Embedding 模型: {settings.embedding_model}, "
                f"缓存目录: {cache_dir}"
            )
            cls._instance.model = TextEmbedding(
                model_name=settings.embedding_model,
                cache_dir=str(cache_dir),
            )
        return cls._instance

    async def embed(self, text: str) -> list[float]:
        """将单条文本转换为向量

        Args:
            text: 待向量化的文本

        Returns:
            向量列表
        """
        # fastembed 的 embed 方法返回一个生成器
        embeddings = list(self.model.embed([text]))
        return embeddings[0].tolist()

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量向量化

        Args:
            texts: 待向量化的文本列表

        Returns:
            向量列表
        """
        if not texts:
            return []

        embeddings = list(self.model.embed(texts))
        return [e.tolist() for e in embeddings]
