from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy声明式基类，所有ORM模型必须继承此类"""
    pass
