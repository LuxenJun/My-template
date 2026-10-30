"""模型集中导出。

main.py 只要 `import app.models`，所有表类就完成注册，
建表时不会漏表。新增模型后记得在这里加一行。
"""

from app.models.product import Product
from app.models.user import User

__all__ = ["Product", "User"]
