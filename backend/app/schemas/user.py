"""用户接口的输入输出契约。

关键：UserOut 里没有 password 字段——字段根本不存在，就不可能泄露。
UserOut 继承 BaseModel，不继承 models.User。
"""

from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field


def check_password_bytes(v: str) -> str:
    """bcrypt 5.0 对超 72 字节的密码直接抛异常，必须在进函数前用 422 挡住。

    max_length 限的是字符数，中文一个字占 3 字节，所以这里按字节再查一遍。
    """
    if len(v.encode("utf-8")) > 72:
        raise ValueError("密码最长 72 字节（1 个中文占 3 字节）")
    return v


# 注册/改密码用：长度 + 字节数都卡
PasswordIn = Annotated[str, Field(min_length=6, max_length=72), AfterValidator(check_password_bytes)]
# 登录用：只卡字节数，避免历史账号因旧规则登不进
PasswordLogin = Annotated[str, AfterValidator(check_password_bytes)]


class UserCreate(BaseModel):
    """注册入参。约束由 Pydantic 校验，不合法直接 422，不进函数体。"""

    username: str = Field(min_length=3, max_length=50)
    password: PasswordIn
    nickname: str = Field(min_length=1, max_length=50)
    email: EmailStr


class UserUpdate(BaseModel):
    """修改入参，全部可选。配合 model_dump(exclude_unset=True) 实现局部更新。"""

    password: PasswordIn | None = None
    nickname: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = None


class UserOut(BaseModel):
    """响应模型，不含任何敏感字段。"""

    id: int
    username: str
    nickname: str
    email: str
    is_active: bool
    create_time: datetime
    update_time: datetime

    # 允许直接读 ORM 对象属性，不用手动转 dict
    model_config = ConfigDict(from_attributes=True)


class LoginIn(BaseModel):
    username: str
    password: PasswordLogin


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
