"""纯接口层。

只做三件事：校验入参（Pydantic 已做）、调 services 或直接查库、返回结果。
不允许出现密码哈希、令牌解析（在 core/security.py）和连接创建（在 db/session.py）。
"""
