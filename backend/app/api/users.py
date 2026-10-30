"""用户路由。

本模块不整体要求登录（注册、登录本身不能要求），
只有 /me 在参数里单独加 Depends(get_current_user)。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import LoginIn, TokenOut, UserCreate, UserOut, UserUpdate
from app.services.user import authenticate_user, register_user

router = APIRouter(prefix="/users", tags=["用户"])


@router.post("/register", response_model=UserOut, status_code=201, summary="注册")
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    # 业务编排在 services/user.py，这里只调一次
    return await register_user(db, data)


@router.post("/login", response_model=TokenOut, summary="登录，拿令牌")
async def login(data: LoginIn, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.username, data.password)
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "expires_in": settings.jwt_expire_minutes * 60,
    }


@router.get("/me", response_model=UserOut, summary="当前登录用户")
async def read_me(current_user: User = Depends(get_current_user)):
    # 验签、查人都在依赖里做完了，函数体一行
    return current_user


@router.patch("/me", response_model=UserOut, summary="修改自己的资料")
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    changes = data.model_dump(exclude_unset=True)   # 只取真正传了的字段
    if "email" in changes and changes["email"] != current_user.email:
        exists = await db.scalar(select(User.id).where(User.email == changes["email"]))
        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被占用")
    if "password" in changes:
        changes["password"] = hash_password(changes["password"])

    for field, value in changes.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)
    return current_user
