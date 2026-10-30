"""user 表。

本文件只描述"表长什么样"：列、类型、约束。
不写接口出入参（在 schemas/），不写查询逻辑（在 api/ 或 services/）。
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, comment="用户id")
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="用户名")
    # 只存哈希，绝不存明文；长度 60 以上，留余量给其他算法
    password: Mapped[str] = mapped_column(String(255), comment="密码哈希")
    nickname: Mapped[str] = mapped_column(String(50), comment="昵称")
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, comment="邮箱")
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否启用")
