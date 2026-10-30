"""用户相关的业务编排。

注册和登录都是"多步操作"：查重 / 校验密码 / 写库 / 提交。
放在这里，路由函数就只剩一行调用，改业务流程时不用动路由。
"""

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


async def register_user(db: AsyncSession, data: UserCreate) -> User:
    """注册：用户名/邮箱查重 -> 密码哈希 -> 落库 -> 提交。

    并发下同时注册同一个用户名，这里查重会漏（两个请求都查不到），
    最终靠表上的 unique 约束兜底，捕获 IntegrityError 转 400。
    """
    exists = await db.scalar(
        select(User).where(or_(User.username == data.username, User.email == data.email))
    )
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或邮箱已存在")

    user = User(
        username=data.username,
        password=hash_password(data.password),   # 只存哈希
        nickname=data.nickname,
        email=data.email,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User:
    """登录校验。

    用户不存在与密码错误返回同一句提示，避免攻击者通过响应差异枚举用户名。
    """
    user = await db.scalar(select(User).where(User.username == username))
    if user is None or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已禁用")
    return user
