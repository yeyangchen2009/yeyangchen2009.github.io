# -*- coding: utf-8 -*-
"""门户 hook：发布新文章后自动更新各系门户 issue 的路线表。

每个系列一个模块（如 zhong.py），需定义：

    PORTAL_ISSUE: int                # 门户 issue 编号
    def apply(body, series_index, issue_number) -> str

``apply`` 是纯字符串处理：把门户表里当前「⏳ 下一篇」的行改为
「[✅ #N](/post/N.html)」，并把下一篇转为「⏳ 下一篇」。
取/存 issue body 由 publish-post.py 负责，hook 不直接联网。
"""
