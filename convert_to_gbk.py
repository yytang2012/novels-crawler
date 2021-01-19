import os
from pathlib import Path

from novelsCrawler.settings import DOWNLOADS


def main(novel_dir=DOWNLOADS, gbk_dir=None):
    if gbk_dir is None or os.path.isdir(gbk_dir) is False:
        gbk_dir = os.path.join(novel_dir, "gbk_novel")
        if os.path.isdir(gbk_dir) is False:
            os.mkdir(gbk_dir)

    novel_dir = Path(novel_dir)
    novel_list = novel_dir.glob("*.txt")
    # novel_list = [str(novel) for novel in novel_list]
    for novel in list(novel_list)[:1]:
        new_novel_path = os.path.join(gbk_dir, novel.name)
        with open(str(novel), 'r', encoding="utf-8") as fs, \
                open(new_novel_path, 'w', encoding="gbk") as fd:
            s = fs.read()
            fd.write(s)

if __name__ == '__main__':
    main()