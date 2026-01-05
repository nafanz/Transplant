import re
import traceback
from pathlib import Path
from typing import Iterator


class Flag310Mixin:
    def member_gen(self):
        for m in self._member_map_.values():
            if m in self:
                yield m

    def __len__(self):
        return len(tuple(self.member_gen()))

    def __iter__(self):
        yield from self.member_gen()


def scantree(path: Path) -> Iterator[Path]:
    for p in path.iterdir():
        if p.is_dir() and not p.name.startswith('.'):
            yield from scantree(p)
        else:
            yield p


def multi_replace(src_txt, replace_map, *extra_maps):
    txt = src_txt
    if extra_maps:
        replace_map = replace_map.copy()
        for x in extra_maps:
            replace_map.update(x)

    for k, v in replace_map.items():
        txt = txt.replace(k, v)
    return txt


STUPID_3_11_TB = re.compile(r'[\s^~]+')


def tb_line_gen(tb):
    for line in traceback.format_tb(tb):
        for sub_line in line.splitlines():
            if STUPID_3_11_TB.fullmatch(sub_line):
                continue
            yield sub_line


unicode_directional_markers = ('\u202a', '\u202b', '\u202c', '\u202d', '\u202e', '\u200e', '\u200f')
uni_t_table = str.maketrans(dict.fromkeys(unicode_directional_markers))
