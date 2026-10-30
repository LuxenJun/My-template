"""安全算法集中处。

密码哈希、令牌签发、令牌解析都在这里。路由文件不直接 import bcrypt / jwt，
只调本文件的函数——以后换算法（bcrypt -> argon2，HS256 -> RS256）只改这一个文件。
"""

import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


# ---------------- 密码 ----------------

def hash_password(raw: str) -> str:
    """明文 -> 60 字符 bcrypt 哈希串（含随机盐）。"""
    return bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()


def verify_password(raw: str, stored: str) -> bool:
    """用输入密码重算哈希，与库里的串比对。

    stored 以 $2 开头视为 bcrypt；否则按历史明文数据比对，
    这样老库里已有的明文账号也能登录，登录后可逐步升级为哈希。
    """
    if stored.startswith("$2"):
        return bcrypt.checkpw(raw.encode(), stored.encode())
    return secrets.compare_digest(raw.encode(), stored.encode())


# ---------------- 令牌 ----------------

def create_access_token(user_id: int) -> str:
    """签发令牌：sub=用户 id，iat=签发时间，exp=过期时间，全部 UTC。"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """验签并解出 payload；失败时抛 jwt 异常，由调用方决定转成什么响应。"""
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],   # 必须限定算法，防 alg=none 伪造
    )
