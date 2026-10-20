import time
from pathlib import Path

from send2trash import send2trash

from tools.common import human_size

FOLDERS = ["~/Downloads", "~/Documents", "~/Desktop"]
TOP_N = 5
OLD_DAYS = 90


def list_files(folder):
    folder = Path(folder).expanduser()
    files = []
    for path in folder.rglob("*"):
        try:
            if path.is_file() and not path.is_symlink():
                info = path.stat()
                files.append((path, info.st_size, info.st_mtime))
        except OSError:
            continue
    return files


def top_heaviest(files, n=TOP_N):
    return sorted(files, key=lambda f: f[1], reverse=True)[:n]


def old_files(files, days=OLD_DAYS):
    limit = time.time() - days * 24 * 60 * 60
    return [f for f in files if f[2] < limit]


def format_date(timestamp):
    return time.strftime("%Y-%m-%d", time.localtime(timestamp))


def ask_and_trash(candidates):
    freed = 0
    for path, size, mtime in candidates:
        if not path.exists():
            continue
        print(f"\n{human_size(size)}, изменён {format_date(mtime)}")
        print(path)
        answer = input("Отправить в Корзину? [да/нет, Enter = нет, q = выход]: ")
        answer = answer.strip().lower()
        if answer == "q":
            break
        if answer in ("y", "yes", "д", "да"):
            send2trash(str(path))
            freed += size
            print("  -> в Корзине")
    print(f"\nОтправлено в Корзину: {human_size(freed)}")


if __name__ == "__main__":
    all_files = []
    for folder in FOLDERS:
        all_files += list_files(folder)

    print(f"Всего файлов: {len(all_files)}\n")

    print(f"Топ-{TOP_N} самых тяжёлых:")
    for path, size, mtime in top_heaviest(all_files):
        print(f"  {human_size(size):>10}  {format_date(mtime)}  {path}")

    old = old_files(all_files)
    total_old = sum(f[1] for f in old)
    print(
        f"\nНе менялись больше {OLD_DAYS} дней: {len(old)} шт., {human_size(total_old)}"
    )
    print("Самые крупные из них:")
    for path, size, mtime in top_heaviest(old, 10):
        print(f"  {human_size(size):>10}  {format_date(mtime)}  {path}")

    candidates = {}
    for item in top_heaviest(all_files) + top_heaviest(old, 10):
        candidates[item[0]] = item

    print("\n--- Очистка ---")
    ask_and_trash(list(candidates.values()))
