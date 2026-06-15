from typing import TypeVar, Generic, Type, Sequence
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Repository基类，提供通用CRUD操作"""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> ModelType:
        """创建记录"""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get_by_id(self, id: str) -> ModelType | None:
        """根据ID查询"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 100, offset: int = 0) -> Sequence[ModelType]:
        """查询列表，按创建时间倒序排列"""
        result = await self.session.execute(
            select(self.model)
            .order_by(desc(self.model.created_at))
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
