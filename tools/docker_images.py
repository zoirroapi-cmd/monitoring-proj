import subprocess


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "команда завершилась с ошибкой")
    return result.stdout


def list_images():
    fmt = "{{.ID}}|{{.Repository}}|{{.Tag}}|{{.Size}}|{{.CreatedSince}}"
    out = run(["docker", "image", "ls", "--no-trunc", "--format", fmt])
    images = {}
    for line in out.splitlines():
        image_id, repo, tag, size, created = line.split("|")
        item = images.setdefault(
            image_id, {"tags": [], "size": size, "created": created}
        )
        if repo != "<none>" and tag != "<none>":
            item["tags"].append(f"{repo}:{tag}")
    return images


def used_image_ids():
    container_ids = run(["docker", "ps", "-a", "-q"]).split()
    if not container_ids:
        return set()
    out = run(["docker", "inspect", "--format", "{{.Image}}"] + container_ids)
    return set(out.split())


def ask_and_remove(candidates):
    removed = 0
    for image_id, item in candidates:
        tags = item["tags"]
        name = ", ".join(tags) if tags else "<без имени>"
        print(f"\n{name}")
        print(f"  {item['size']}, создан {item['created']}, id {image_id[7:19]}")
        answer = input("Удалить образ? [да/нет, Enter = нет, q = выход]: ")
        answer = answer.strip().lower()
        if answer == "q":
            break
        if answer in ("y", "yes", "д", "да"):
            for target in (tags if tags else [image_id]):
                try:
                    run(["docker", "rmi", target])
                    print(f"  -> удалён {target}")
                except RuntimeError as e:
                    print(f"  не вышло: {e}")
                    break
            else:
                removed += 1
    print(f"\nУдалено образов: {removed}. Сравни `docker system df` до и после.")


def build_cache_info():
    fmt = "{{.Type}}|{{.Size}}|{{.Reclaimable}}"
    out = run(["docker", "system", "df", "--format", fmt])
    for line in out.splitlines():
        kind, size, reclaimable = line.split("|")
        if kind == "Build Cache":
            return size, reclaimable
    return None


def ask_and_prune_cache():
    info = build_cache_info()
    if info is None:
        print("\nНе удалось узнать размер кеша сборки.")
        return
    size, reclaimable = info
    print(f"\nКеш сборки: всего {size}, можно удалить {reclaimable}")
    answer = input("Очистить кеш сборки? [да/нет, Enter = нет]: ")
    if answer.strip().lower() in ("y", "yes", "д", "да"):
        try:
            run(["docker", "builder", "prune", "--all", "--force"])
            print("  -> кеш очищен")
            print(f"  Сейчас: {build_cache_info()}")
        except RuntimeError as e:
            print(f"  не вышло: {e}")


if __name__ == "__main__":
    try:
        images = list_images()
        used = used_image_ids()
    except (RuntimeError, FileNotFoundError) as e:
        print("Docker недоступен:", e)
        raise SystemExit(1)

    candidates = [(i, x) for i, x in images.items() if i not in used]
    candidates.sort(key=lambda c: bool(c[1]["tags"]))

    print(f"Образов: {len(images)}, без контейнеров: {len(candidates)}")
    ask_and_remove(candidates)
    ask_and_prune_cache()