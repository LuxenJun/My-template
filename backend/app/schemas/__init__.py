"""schemas 包。

约定：每个业务实体一个文件，文件内固定三类模型
    XxxCreate  收：新增时前端传什么
    XxxUpdate  收：修改时前端传什么（全部可选）
    XxxOut     吐：返回给前端什么（绝不含敏感字段）
需要分页时额外加 XxxPage。
"""
