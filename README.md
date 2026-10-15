# monitoring-proj

Кастомный Prometheus-экспортер для macOS (Apple Silicon) + полный стек мониторинга.

Пет-проект, в котором реализован путь мониторинга от сбора метрик на хосте до визуализации в Grafana.

## Что уже работает

| Компонент | Статус | Описание |
|-----------|--------|---------|
| **Экспортер** | ✅ Готово | Python-экспортер (CPU, RAM, Swap + сетевые проверки) |
| **Prometheus** | ✅ Готово | Docker Compose, скрейпинг экспортера |
| **Grafana + дашборды** | ✅ Готово | Дашборд Mac overview (CPU, SWAP, сайты, VPN) |
| **Сетевые проверки** | ✅ Готово | Статус VPN и доступность сайтов |
| **Cleanup-утилиты** | ✅ Готово | Скрипты очистки неиспользуемых Docker-образов (с dry-run) |
| **CI (GitHub Actions)** | ✅ Готово | Lint + Tests |
| **Alertmanager + Telegram** | ⬜ В планах | |
| **Автозапуск (launchd)** | ⬜ В планах | |
| **Метрики батареи / температуры / диска** | ⬜ В планах | |

## Архитектура
[macOS Host]                              [Docker]
Python Exporter :9101  ←── scrape ──    Prometheus :9090
(psutil + prometheus-client)                   │
├── Grafana :3000
└── Alertmanager → Telegram (план)
text**Почему экспортер работает на хосте, а не в контейнере**

Docker Desktop на macOS запускает контейнеры внутри Linux-виртуальной машины. Процесс внутри контейнера видит ресурсы этой VM, а не реальное железо Mac (CPU, батарею, датчики и т.д.). Поэтому экспортер запускается напрямую на macOS, а Prometheus обращается к нему по адресу `host.docker.internal:9101`.

## Структура проекта
monitoring-proj/
├── exporter/               # Python-экспортер метрик
├── deploy/                 # Docker Compose + конфиги Prometheus/Grafana
├── tools/                  # Утилиты очистки Docker
├── bot/                    # Telegram-бот (в планах)
├── launchd/                # Автозапуск через launchd (в планах)
├── tests/                  # Тесты
├── .github/workflows/      # CI (GitHub Actions)
├── setup.sh
└── requirements.txt

## Быстрый старт

### Требования
- macOS
- Python 3.10+
- Docker Desktop

### 1. Установка зависимостей

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Запуск экспортера
```Bash
python3 exporter/playground.py
Проверка метрик: http://localhost:9101/metrics
Если порт 9101 занят:
Bashkill -9 $(lsof -t -i :9101)
```

### 3. Запуск стека мониторинга
```Bash
cd deploy
docker compose up -d
```

Prometheus: http://localhost:9090
Grafana: http://localhost:3000

## Текущие метрики

| Метрика              | Тип   | Описание                              |
|----------------------|-------|---------------------------------------|
| `mac_cpu_percent`    | Gauge | Загрузка CPU (%)                      |
| `mac_ram_percent`    | Gauge | Использование оперативной памяти (%)  |
| `mac_swap_percent`   | Gauge | Использование swap (%)                |
| Сетевые проверки     | —     | Статус VPN и доступность сайтов       |