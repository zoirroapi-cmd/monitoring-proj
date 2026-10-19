import subprocess

from tools.common import human_size


def find_qemu():
    out = subprocess.run(
        ["ps", "-axo", "pid=,rss=,etime=,comm="],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    ).stdout
    found = []
    for line in out.splitlines():
        parts = line.split(None, 3)
        if len(parts) < 4:
            continue
        pid, rss_kb, etime, command = parts
        if "qemu" in command.lower():
            found.append((int(pid), int(rss_kb) * 1024, etime, command.split("/")[-1]))
    return found


if __name__ == "__main__":
    vms = find_qemu()
    if not vms:
        print("Запущенных qemu-виртуалок нет")
    else:
        total = sum(vm[1] for vm in vms)
        print(f"qemu-процессов: {len(vms)}, занимают {human_size(total)}")
        for pid, rss, etime, name in vms:
            print(f"  PID {pid:>6}  {human_size(rss):>10}  работает {etime}  {name}")