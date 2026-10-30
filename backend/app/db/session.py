"""数据库连接相关的一切。

引擎、连接池、会话工厂、get_db 依赖都在这里。业务代码不自己建连接，
一律通过 Depends(get_db) 拿会话。换数据库只改 .env 里的 DB_URL。
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

async_engine = create_async_engine(
    settings.db_url,
    echo=settings.debug,     # 开发时打印 SQL，上线把 debug 关掉即自动关闭
    pool_recycle=3600,       # 防 MySQL 8 小时空闲断连
    pool_pre_ping=True,      # 取连接前先 ping，坏连接自动换新
)

# expire_on_commit=False：commit 后对象属性仍可读，
# 接口返回刚写入的对象时不会因此多查一次库
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """请求进来开一个会话，请求结束自动关闭。"""
    async with async_session_factory() as session:
        yield session
