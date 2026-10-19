import time
from pathlib import Path

from tools.common import human_size
from tools.heavy_files import old_files, top_heaviest


def test_human_size_bytes():
    assert human_size(500) == "500.0 Б"


def test_human_size_megabytes():
    assert human_size(5 * 1024 * 1024) == "5.0 МБ"


def test_top_heaviest_sorts_by_size():
    files = [
        (Path("a"), 10, 0),
        (Path("b"), 300, 0),
        (Path("c"), 20, 0),
    ]
    result = top_heaviest(files, 2)
    assert [f[0].name for f in result] == ["b", "c"]


def test_old_files_keeps_only_old():
    now = time.time()
    day = 24 * 60 * 60
    files = [
        (Path("old"), 1, now - 100 * day),
        (Path("new"), 1, now - 1 * day),
    ]
    result = old_files(files, days=90)
    assert [f[0].name for f in result] == ["old"]