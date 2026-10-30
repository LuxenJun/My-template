"""通用分页。

任何一个"列表 + 总数"的接口都可以用：
    items, total = await paginate(db, select(Product).order_by(Product.id), page, page_size)

第一次写列表接口就要用，第二个列表接口复用它——这就是 utils 该出现的位置。
"""

from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def paginate(
    db: AsyncSession,
    stmt: Select,
    page: int,
    page_size: int,
) -> tuple[list[Any], int]:
    """返回 (当前页数据, 总条数)。

    共两条 SQL：一条 count，一条带 offset/limit 的查询。
    count 用 stmt.subquery() 包一层，所以原 stmt 里的 where / join 都会生效。
    """
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0

    rows = await db.execute(stmt.offset((page - 1) * page_size).limit(page_size))
    return list(rows.scalars().all()), total
