"""商品接口测试。

这些用例不需要数据库：401 在验签依赖里就返回了，不会走到查库。
需要真库的用例（注册、登录、增删改查）后续按同样方式补。
"""

from httpx import AsyncClient


async def test_health(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


async def test_products_requires_login(client: AsyncClient):
    """不带令牌访问商品列表，应该是 401，不是 500 也不是 200。"""
    r = await client.get("/products")
    assert r.status_code == 401
    assert r.json()["detail"] == "缺少令牌"


async def test_products_rejects_bad_token(client: AsyncClient):
    """乱填的令牌必须被验签拦下。"""
    r = await client.get("/products", headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401
    assert r.json()["detail"] == "令牌无效"
