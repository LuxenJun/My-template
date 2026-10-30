"""pytest 公共夹具。

client 用 httpx 的 ASGITransport 直接调 app，不需要真的启动 uvicorn，
也不触发 lifespan（所以测试不会去连数据库建表）。
需要真库的测试单独建 fixture 覆盖 get_db 依赖。
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
