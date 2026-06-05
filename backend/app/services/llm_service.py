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
        """调用LLM获取JSON响应"""
        content = await self.chat(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            json_mode=True,
        )
        return json.loads(content)
