# 项目：   库函数
# 模块：   实物工具-照片备份
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2018-11-17 17:59

from orange import HOME, Path, R, sh

dest = HOME / "OneDrive - business/图片/本机照片"
Pattern = R / r".*?(?P<year>20\d{2})\-?(?P<month>\d{2})\-?(?P<day>\d{2}).*?"


# @arg('path', nargs='?', default='noset', help='从指定的目录备份照片')
def main(path="."):
    if path != "noset":
        path = Path(path or ".")
        for filename in path:
            if filename.lsuffix in (".jpg", ".mp4"):
                m = Pattern == str(filename)
                if m:
                    m = m.groupdict()
                    d = dest / m["year"]
                    d.ensure()
                    d = d / m["month"]
                    d.ensure()
                    dest_ = d / str(filename.name)
                    if dest_:
                        print(f"{dest_} exists, skipped!", flush=True)
                    elif filename.drive == dest_.drive:
                        filename.rename(dest_)
                        print(f"{filename} -> {dest_}", flush=True)
                    else:
                        print(f"{filename} -> {d}", flush=True)
                        sh > f'copy "{filename}" "{d}"'
