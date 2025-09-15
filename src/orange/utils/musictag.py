# 项目：标准库函数
# 模块：音乐标签
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2019-02-23 14:03

import shutil

import mutagen

from orange import Path, R, sh

FixPatterns = ((R / r"\[.*?\]", ""),)
FixTags = "title", "album", "artist"


def fixtag(val):
    for p, v in FixPatterns:
        val = p / val % v
    return val


class MusicTag(dict):
    __slots__ = ("file", "tags")

    def __init__(self, filename, easy=True):
        _file = mutagen.File(filename, easy=easy)
        self.file = _file
        self.tags = _file.tags
        for k, v in _file.tags.items():
            if isinstance(v, list):
                v = v[0]
            self[k.lower()] = str(v)

    @property
    def track(self):
        track = self.get("track") or self.get("tracknumber")
        if track:
            tracks = track.split("/")
            return "%02d" % (int(tracks[0]))

    def libpath(self, suffix=".m4a", path=None):
        path = Path(path or "~/Music")
        track = self.track
        track = f"{track} " if track else ""
        title = self.get("title")
        if title:
            name = "".join([track, title, suffix])
            artist = self.get("artist", "Unknow Artist")
            album = self.get("album", title)
            return path / artist / album / name

    def save(self):
        self.file.save()

    def fixtags(self):
        modified = False
        tags = self.tags
        for tag in tags.keys():
            _tag = tag.lower()
            if _tag in FixTags:
                val = self[_tag]
                v = fixtag(val)
                if v != val:
                    self[_tag], tags[tag] = v, v
                    modified = True
        if modified:
            self.file.save()


def main():
    for src in Path("~/Downloads"):
        from urllib.parse import unquote

        from orange import decode

        name = src.name
        name = decode(name.encode("latin1"))
        if "%" in name:
            name = unquote(name)
        print(name)
        continue
        suffix = src.lsuffix
        if suffix in (".ape", ".flac", ".m4a", "mp3"):
            s = MusicTag(src)
            s.fixtags()
            d = s.libpath(
                suffix=".m4a" if suffix in (".ape", ".flac") else suffix
            )
            if not d:
                d.parent.ensure()
                if suffix in (".ape", ".flac"):
                    cmd = f'ffmpeg -i "{src}" -acodec alac "{d}"'
                    sh > cmd
                elif suffix in (".m4a", ".mp3"):
                    shutil.copyfile(src, d)
                print(f"create: {d.name}")
