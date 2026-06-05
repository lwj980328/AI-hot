from app.schemas.records.source_document import SourceDocument


class RepositoryRecord(SourceDocument):
    """代码仓库记录"""
    source_type: str = "repository"
    stars: int = 0
    language: str = ""
