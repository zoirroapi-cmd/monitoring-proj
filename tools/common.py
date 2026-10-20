def human_size(num_bytes):
    for unit in ["Б", "КБ", "МБ", "ГБ"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} ТБ"
