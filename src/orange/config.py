# 项目：   数智综合运营系统项目管理软件
# 模块：   参数配置模块
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2025-09-05 15:48
# 修订：2025-09-06 采用 class 来实现

import os
import sys
from typing import Any

from toml import dump, load

from .shell import Path


class Config(object):
    "一个简单的程序配置库，采用 toml 格式"

    def __init__(self, prog: str = ""):
        if not prog:
            prog = Path(sys.argv[0]).pname or "test"

        if os.name == "nt":
            self.path = Path(f"$localappdata/{prog}/{prog}.toml")
        else:
            self.path = Path(f"~/.config/{prog}/{prog}.toml")
        try:
            self.path.parent.ensure(True)
        except Exception:
            ...
        self.config = load(self.path) if self.path else {}

    def get(self, key: str, default: Any = None) -> Any:
        "获取参数配置，如系统未配置，这返回并保存默认值"
        d = self.config.copy()
        for k in key.split("."):
            d = d.get(k, None)
            if not d:
                if default:
                    self.set(key, default)
                return default
        return d

    def set(self, key: str, value: Any):
        "保存参数配置，一般由 get 自动使用"
        d = self.config
        keys = list(key.split("."))
        for k in keys[:-1]:
            d2 = d.get(k, {})
            if not d2:
                d[k] = d2
            d = d2
        d[keys[-1]] = value
        self.save()

    def save(self):
        "保存参数配置到配置文件，一般由系统自动调用"
        with self.path.open("w", encoding="utf8") as f:
            dump(self.config, f)
