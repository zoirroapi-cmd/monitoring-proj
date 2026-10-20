import subprocess

from tools.common import human_size


def run_ps():
    result = subprocess.run(
        ["ps", "-axo", "pid=,rss=,etime=,comm="],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ps завершился с ошибкой")
    return result.stdout


def parse_ps(text):
    found = []
    for line in text.splitlines():
        parts = line.split(None, 3)
        if len(parts) < 4:
            continue
        pid, rss_kb, etime, command = parts
        if "qemu" in command.lower():
            found.append((int(pid), int(rss_kb) * 1024, etime, command.split("/")[-1]))
    return found


def find_qemu():
    return parse_ps(run_ps())


if __name__ == "__main__":
    try:
        vms = find_qemu()
    except RuntimeError as e:
        print("Не удалось получить список процессов:", e)
        raise SystemExit(1)
    if not vms:
        print("Запущенных qemu-виртуалок нет")
    else:
        total = sum(vm[1] for vm in vms)
        print(f"qemu-процессов: {len(vms)}, занимают {human_size(total)}")
        for pid, rss, etime, name in vms:
            print(f"  PID {pid:>6}  {human_size(rss):>10}  работает {etime}  {name}")
