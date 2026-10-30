"""配置出口。

全项目所有"会随环境变化"的值都从这里取，业务代码里不许出现硬编码。
值优先从 backend/.env 读取，读不到就用下面 class 里的默认值。
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ 目录：本文件在 backend/app/core/config.py，往上三层
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",          # .env 里有多余的键也不报错
    )

    # ---------- 应用 ----------
    app_name: str = "backend-template"
    debug: bool = True

    # ---------- 数据库 ----------
    # 密码里的 @ 等特殊字符要做 URL 编码，例如 @ -> %40
    db_url: str = "mysql+aiomysql://root:root@localhost:3306/test?charset=utf8"

    # ---------- JWT ----------
    jwt_secret: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    # ---------- CORS ----------
    # 逗号分隔，前端 dev server 默认 5173
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        """把逗号分隔的字符串拆成列表，去掉空项和空格。"""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
