# 后端模板

FastAPI + SQLAlchemy 2.0（异步）+ Pydantic v2 + JWT，配套 `../frontend`（Vue 3 + Element Plus）。

已内置：注册 / 登录 / 令牌验签 / 用户资料 / 商品增删改查（分页、模糊搜索、分类过滤）/ CORS / 测试骨架。

## 一、跑起来

```powershell
cd "D:\study\My template\backend"

# 1. 装依赖（会建 .venv）
uv sync

# 2. 配好 .env（已经有一份，确认 DB_URL 指向的库存在）
#    库不存在就先建：CREATE DATABASE your_db DEFAULT CHARSET utf8mb4;

# 3. 启动
uv run uvicorn app.main:app --reload
```

打开 <http://127.0.0.1:8000/docs>。

启动时 `lifespan` 会自动建表（`create_all`）。**注意：create_all 只建新表，不改已有表**，
后期改字段要上 alembic 迁移，或手动 ALTER。

## 二、三分钟验证全链路

```powershell
# 注册
$body = '{"username":"admin","password":"123456","nickname":"管理员","email":"a@b.com"}'
Invoke-RestMethod -Uri http://127.0.0.1:8000/users/register -Method Post -ContentType "application/json" -Body $body

# 登录拿令牌
$r = Invoke-RestMethod -Uri http://127.0.0.1:8000/users/login -Method Post -ContentType "application/json" -Body '{"username":"admin","password":"123456"}'
$t = $r.access_token

# 带令牌访问受保护接口
Invoke-RestMethod -Uri http://127.0.0.1:8000/products -Headers @{Authorization="Bearer $t"}
```

不带令牌访问 `/products` 返回 401；令牌改一个字符也返回 401。

## 三、目录职责

```
app/
├── main.py            装配：建 app、CORS、建表、挂路由（不写业务）
├── core/config.py     所有配置的唯一出口，值来自 .env
├── core/security.py   密码哈希 + 令牌签发/验签（换算法只改这里）
├── db/base.py         Base + create_time/update_time 公共列
├── db/session.py      engine、连接池、get_db（换数据库只改这里）
├── models/            每张表的列与约束（不认识 HTTP）
├── schemas/           收什么、吐什么、什么算合法
├── api/               路由（不含哈希、不含建连接）
├── services/          多步业务编排（可选层）
└── utils/             与业务无关的纯函数（可选层）
```

三条不能破：

1. 依赖单向：`api -> services -> models/db`，反向 import 会循环导入
2. `models/` 里不许出现 `HTTPException`、`status_code`、`Request`
3. `schemas/` 的响应模型不继承 `models/` 的表类——密码字段从源头就不存在

## 四、新增一个业务模块（照着做）

以"订单 order"为例：

1. `models/order.py` 写 `Order(Base)`，列、类型、约束
2. `models/__init__.py` 加一行 `from app.models.order import Order` 并补进 `__all__`
3. `schemas/order.py` 写 `OrderCreate` / `OrderUpdate` / `OrderOut`（Out 不含敏感字段）
4. `api/orders.py` 写 `router = APIRouter(prefix="/orders", tags=["订单"], dependencies=[Depends(get_current_user)])`，再写接口
5. `main.py` 加 `from app.api import orders` 和 `app.include_router(orders.router)`
6. 启动，看 `/docs` 出现"订单"分组

多步操作（扣库存 + 写订单）出现第二次时，抽到 `services/order.py`。

## 五、删掉示例表，换成自己的

模板自带 `user` + `product` 两张示例表。换项目时：

- 删 `models/product.py`、`schemas/product.py`、`api/products.py`
- 删 `models/__init__.py` 里 product 那两行
- 删 `main.py` 里 products 的 import 和 include_router
- `user` 建议留着，登录逻辑直接复用

## 六、和前端对接

| 项 | 值 |
|---|---|
| 后端端口 | 8000（uvicorn 默认） |
| 前端端口 | 5173（vite 默认），已在 `CORS_ORIGINS` 放行 |
| 鉴权 | 请求头 `Authorization: Bearer <access_token>` |
| 令牌有效期 | 30 分钟，`JWT_EXPIRE_MINUTES` 可改 |
| 接口契约 | `http://127.0.0.1:8000/openapi.json`，前端可据此生成 TS 类型 |

前端 pinia 已装 `pinia-plugin-persistedstate`，令牌放 store 里持久化即可。

## 七、测试

```powershell
uv run pytest -v
```

现有 3 个用例不需要数据库。要测注册/增删改查，在 `conftest.py` 里覆盖 `get_db`
指向测试库（或 sqlite 内存库）。
