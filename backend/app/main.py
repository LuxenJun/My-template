"""应用装配点。

本文件不写业务，只做三件事：
  1. 建 app（标题、生命周期、CORS）
  2. 启动时建表
  3. 把各模块 router 挂上来

想知道项目有哪些接口，看 include_router 那几行就够了。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401  关键：让所有表类在建表前完成注册，删了会漏表
from app.api import products, users
from app.core.config import settings
from app.db.base import Base
from app.db.session import async_engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    # 开发期用它建表足够；正式项目改表结构要换成 alembic 迁移
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# 前端 Vue dev server 在 5173，跨域必须放行，否则浏览器直接拦请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(products.router)


@app.get("/health", tags=["其他"], summary="健康检查")
async def health():
    return {"status": "ok"}
