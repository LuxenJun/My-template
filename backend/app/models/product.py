"""product 表（示例表）。

新项目里这张表通常会被删掉换成自己的业务表，
删的时候连带删 schemas/product.py、api/products.py、models/__init__.py 里的那一行。
"""

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True, comment="商品id")
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="商品名")
    # 金额必须用 Numeric，Float 会有 0.1+0.2 != 0.3 的误差
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), comment="价格")
    stock: Mapped[int] = mapped_column(Integer, default=0, comment="库存")
    category: Mapped[str] = mapped_column(String(50), index=True, comment="分类")
    on_sale: Mapped[bool] = mapped_column(default=True, comment="是否上架")
    description: Mapped[str | None] = mapped_column(String(255), comment="描述")
