from tools.vm_check import parse_ps

SAMPLE = """\
  101  2048 05:12 /usr/sbin/cfprefsd
  412 5767168 03-04:12:55 /Users/x/My VMs/qemu-system-aarch64
  500  1024 00:10 /Applications/Safari
"""


def test_parse_ps_finds_only_qemu():
    result = parse_ps(SAMPLE)
    assert len(result) == 1


def test_parse_ps_extracts_fields():
    pid, size_bytes, etime, name = parse_ps(SAMPLE)[0]
    assert pid == 412
    assert size_bytes == 5767168 * 1024
    assert etime == "03-04:12:55"
    assert name == "qemu-system-aarch64"


def test_parse_ps_empty_text():
    assert parse_ps("") == []


def test_parse_ps_skips_garbage_lines():
    assert parse_ps("мусор без колонок\nещё один") == []