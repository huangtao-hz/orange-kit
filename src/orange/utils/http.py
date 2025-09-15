# 项目：   我的工具箱
# 模块：   互联网模块
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2021-03-11 21:57
# 修改：2022-11-21 21:06 引入 Session 类


from bs4 import BeautifulSoup as Soup
from requests import get
from requests.sessions import Session as _Session

default_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.52",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "*/*",
    "Connection": "keep-alive",
}


class Session(_Session):
    host = None

    def __init__(self, host: str = None, cookies=None, headers=None) -> None:
        super().__init__()
        self.host = host
        self.cookies = cookies
        self.headers = headers or default_headers

    def get(self, url: str, method="GET", **kwargs):
        return self.request(
            method=method,
            url=url,
        )


def get_json(url, params=None, **kwargs):
    resp = get(url, params, **kwargs)
    if resp.status_code == 200:
        return resp.json()


def get_text(url, params=None, encoding=None, **kwargs):
    resp = get(url, params, **kwargs)
    if resp.status_code == 200:
        if encoding:
            return resp.content.decode(encoding)
        else:
            return resp.text


def get_soup(url, params=None, **kwargs):
    text = get_text(url, params, **kwargs)
    if text:
        return Soup(text, "lxml")
