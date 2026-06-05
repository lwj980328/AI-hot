from pydantic import BaseModel


class ReportState(BaseModel):
    """报告状态"""
    title: str = ""
    summary: str = ""
    markdown_content: str = ""
