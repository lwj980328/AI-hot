from pydantic import BaseModel, Field


class ReportState(BaseModel):
    """报告状态"""

    title: str = ""
    summary: str = ""
    markdown_content: str = ""
    is_fallback: bool = Field(
        default=False, description="是否为降级报告（LLM 调用失败时使用模板生成）"
    )
