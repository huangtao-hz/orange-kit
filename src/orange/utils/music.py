# 项目：标准函数库
# 模块：音乐文件转换
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2019-03-07 10:45

from orange import Path, R, sh
from orange.utils.musictag import fixtag

Pattern = R / r'".*?"|\S+'


class CueTime(object):
    __slots__ = "value"

    def __init__(self, value: str):
        if isinstance(value, str):
            m, s, f = map(int, value.split(":"))
            self.value = m * 60 * 75 + s * 75 + f
        else:
            self.value = value

    def __sub__(self, other):
        return CueTime(self.value - other.value)

    def __str__(self):
        s, f = divmod(self.value, 75)
        m, s = divmod(s, 60)
        return "%02d:%02d:%02d" % (m, s, f)

    @property
    def time(self):
        m, s = divmod(self.value, 75 * 60)
        return "%d:%05.2f" % (m, s / 75)

    def __repr__(self):
        return f'CueTime("{self}")'


class CueSheet(object):
    def __init__(self, filename):
        self.album = {}
        self.tracks = {}
        self.trackno = 0
        self.cur_track = {}
        for cmd, *args in filter(
            None, map(Pattern.findall, Path(filename).lines)
        ):
            cmd = cmd.lower()
            args = tuple(
                map(lambda x: x[1:-1] if x.startswith('"') else x, args)
            )
            if hasattr(self, cmd):
                getattr(self, cmd)(*args)
            else:
                self.default(cmd, *args)

    def track(self, no, type_):
        self.trackno = no
        self.cur_track = {}
        self.tracks[self.trackno] = self.cur_track

    def title(self, name):
        name = fixtag(name)
        if self.trackno:
            self.cur_track["title"] = name
        else:
            self.album["album"] = name

    def index(self, flag, time):
        self.cur_track[flag] = CueTime(time)

    def default(self, cmd, *args):
        print(cmd, *args)

    def performer(self, artist):
        obj = self.cur_track if self.trackno else self.album
        obj["artist"] = fixtag(artist)

    def file(self, filename, type_):
        self.filename = filename
        self.type_ = type_

    def __iter__(self):
        end = None  # 上一首歌的结束时间
        count_ = len(self.tracks)
        for no, tags in reversed(tuple(self.tracks.items())):
            begin = tags.pop("01")  # 取本首歌的开始时间
            if end:  # 如果有本首歌的结束时间，则定义曲长
                cmd = f"-ss {begin.time} -t {(end - begin).time}"
            else:
                cmd = f"-ss {begin.time}"  # 无本首歌的结束时间，则忽略
            end = tags.pop("00", begin)  # 取本首歌的空白开始时间，
            tags = tags.copy()  # 取本首歌的信息
            tags.update(tracknumber=f"{no}/{count_}", **self.album)
            yield cmd, tags


if __name__ == "__main__":
    a = CueSheet("~/a.cue")
    music_file = Path("~") / a.filename
    dest = Path("~") / a.album["album"]
    dest.ensure()
    if music_file:
        for cmd, tags in a:
            print(cmd)
            destfile = dest / f"{tags['title']}.m4a"
            sh > f'ffmpeg -i "{music_file}" {cmd} -acodec alac "{destfile}"'
            tag = destfile.music_tag
            tag.tags.update(tags)
            tag.save()
