"""商品路由（示例模块）。

和 users.py 的差别只有一处：整个模块要求登录，
所以 dependencies 写在 APIRouter 上，模块内每个接口都自动验签，
不用在每个函数参数里各写一遍 Depends(get_current_user)。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut, ProductPage, ProductUpdate
from app.utils.pagination import paginate

router = APIRouter(
    prefix="/products",
    tags=["商品"],
    dependencies=[Depends(get_current_user)],   # 整个模块需要登录
)


@router.get("", response_model=ProductPage, summary="分页列表")
async def list_products(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(None, description="按商品名模糊搜索"),
    category: str | None = Query(None, description="按分类精确过滤"),
    db: AsyncSession = Depends(get_db),
):
    # 路径写 "" 而不是 "/"：prefix 是 /products，写 "/" 会变成 /products/ 触发 307 重定向
    stmt = select(Product)
    if keyword:
        stmt = stmt.where(Product.name.like(f"%{keyword}%"))
    if category:
        stmt = stmt.where(Product.category == category)

    items, total = await paginate(db, stmt.order_by(Product.id.desc()), page, page_size)
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.post("", response_model=ProductOut, status_code=201, summary="新增")
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    product = Product(**data.model_dump())
    db.add(product)          # add 是同步方法，不要写 await
    await db.commit()
    await db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductOut, summary="详情")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    return product


@router.put("/{product_id}", response_model=ProductOut, summary="修改")
async def update_product(
    product_id: int, data: ProductUpdate, db: AsyncSession = Depends(get_db)
):
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204, summary="删除")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")

    await db.delete(product)
    await db.commit()
