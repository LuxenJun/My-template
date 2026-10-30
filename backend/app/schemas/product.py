"""商品接口的输入输出契约。

注意 price 上的 gt=0：负数价格在进函数前就被 422 挡掉，
路由函数里不用再写 if 判断。
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0, default=0)
    category: str = Field(min_length=1, max_length=50)
    on_sale: bool = True
    description: str | None = Field(default=None, max_length=255)


class ProductUpdate(BaseModel):
    """全部可选，只改前端真正传了的字段。"""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    on_sale: bool | None = None
    description: str | None = Field(default=None, max_length=255)


class ProductOut(BaseModel):
    id: int
    name: str
    price: Decimal
    stock: int
    category: str
    on_sale: bool
    description: str | None
    create_time: datetime
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductPage(BaseModel):
    """分页响应。前端表格组件一般要 total + 当前页数据。"""

    total: int
    page: int
    page_size: int
    items: list[ProductOut]
