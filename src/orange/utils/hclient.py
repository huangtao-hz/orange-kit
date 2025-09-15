# 项目：标准库函数
# 模块：网络爬虫
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2016-12-26 17:08
# 修订：2017-01-14
# 修订：2018-11-01 23:13 从 asyncio 引入 wait 和 run
# 修改：2022-11-22 23:11 由  root 调整为 host 参数, 在 _request 函数中增加 ssl=False 参数
# 修改：2023-05-05 20:21 get_soup 新增 features 参数，默认值是 lxml


from asyncio import run, wait

from aiohttp import ClientSession
from bs4 import BeautifulSoup as BS4

from orange import Path

__all__ = "Crawler", "wait", "BS4"


class Crawler(ClientSession):
    def _request(self, *args, **kw):
        return super()._request(*args, ssl=False, **kw)

    async def get_text(self, url, *args, method="GET", **kw):
        # 以获取指定网页的文本
        async with self.request(method, url, *args, **kw) as resp:
            return await resp.text()

    async def get_soup(self, url, *args, features="lxml", **kw):
        # 获取指定网页的BeautifulSoup实例
        text = await self.get_text(url, *args, **kw)
        return BS4(text, features=features)

    async def download(self, url, params=None, path=".", *args, **kw):
        # 下载文件，其中path可以是下载文件的文件名，也可以是下载目录
        async with self.get(url, params=params, *args, **kw) as resp:
            path = Path(path)
            if path.is_dir():
                from urllib.parse import unquote

                # 获取文件名字段
                filename = resp.headers["Content-Disposition"]
                filename = filename.split(";")[-1]  # 获取最后一个参数
                tp, filename = filename.split("=")
                if tp.strip() == "filename*":
                    filename = (filename.split("'"))[-1]
                if filename.startswith('"'):
                    filename = filename[1:-1]
                filename = unquote(filename)
                path = path / Path(filename).name
            path.write(data=await resp.read())  # 写入文件

    async def batch(self, *coros):
        "批量执行 coro"
        return wait([self._loop.create_task(coro) for coro in coros])

    async def get_json(self, url, *args, encoding=None, method="GET", **kw):
        # 获取指定网页的JSON数据
        async with self.request(method, url, *args, **kw) as resp:
            return await resp.json(encoding=encoding)

    async def run(self):
        # 爬虫的主运行程序
        raise Exception("This function doesnt exist!")

    @classmethod
    def start(cls, target=None, args=None, kwargs=None, **kw):
        # target：待执行的命令，必须为协程，若无，则调用run
        # target的第一个参数应为 session
        # args：target的位置参数
        # kwargs: target的关键字参数
        # kw: cls的关键字参数
        args = args or []
        kwargs = kwargs or {}
        target = target or cls.run

        async def _main():
            async with cls(**kw) as sess:
                await target(sess, *args, **kwargs)

        run(_main())
