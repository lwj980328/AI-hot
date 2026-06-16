import json
import logging
from openai import AsyncOpenAI
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    """LLM服务 - 统一管理LLM调用

    解决Agent直接访问外部HTTP服务的架构违规问题
    Agent应通过此Service调用LLM，而非直接实例化OpenAI客户端
    """

    _instance: "LLMService | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            settings = get_settings()
            cls._instance.client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )
            cls._instance.model = settings.openai_model
        return cls._instance

    async def chat(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> str:
        """调用LLM获取文本响应"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    async def chat_json(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
    ) -> dict:
        """调用LLM获取JSON响应

        支持容错解析：如果 LLM 返回的内容包含 markdown 代码块包裹的 JSON，
        会自动提取代码块内的内容后再解析。
        """
        content = await self.chat(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            json_mode=True,
        )

        # 容错解析：提取 ```json ... ``` 代码块内的内容
        return self._parse_json_content(content)

    @staticmethod
    def _parse_json_content(content: str) -> dict:
        """解析 JSON 内容，支持 markdown 代码块包裹

        Args:
            content: LLM 返回的内容，可能是纯 JSON 或 markdown 代码块包裹的 JSON

        Returns:
            解析后的字典

        Raises:
            json.JSONDecodeError: 无法解析为 JSON
        """
        # 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 尝试提取 ```json ... ``` 代码块
        import re

        json_block_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
        match = re.search(json_block_pattern, content, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
            return json.loads(json_str)

        # 尝试提取 { ... } 块
        brace_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
        match = re.search(brace_pattern, content, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)

        # 所有尝试都失败，抛出原始错误
        raise json.JSONDecodeError(f"无法从内容中提取 JSON: {content[:200]}...", content, 0)
