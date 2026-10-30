"""所有 ORM 模型的公共父类。

这里只做一件事：定义 Base，并把 create_time / update_time 提成公共列，
新表继承 Base 就自动带这两个字段，不必每张表抄一遍。
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), comment="修改时间"
    )
