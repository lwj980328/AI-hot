from app.schemas.records.source_document import SourceDocument


class ModelRecord(SourceDocument):
    """模型记录"""
    source_type: str = "model"
    downloads: int = 0
    likes: int = 0
