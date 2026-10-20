import time

import psutil
from net_metrics import start_network_thread
from prometheus_client import Gauge, start_http_server

cpu_gauge = Gauge("mac_cpu_percent", "Загрузка CPU в процентах")
mac_ram_percent = Gauge("mac_ram_percent", "Загрузка RAM")
mac_swap_percent = Gauge("mac_swap_percent", "Загрузка SWAP")


def collect_metrics():

    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    data = {
        "cpu_percent": cpu,
        "ram_percent": mem.percent,
        "swap_percent": swap.percent,
    }
    return data


start_http_server(9101)

while True:
    start_network_thread()
    result = collect_metrics()
    cpu_gauge.set(result["cpu_percent"])
    mac_ram_percent.set(result["ram_percent"])
    mac_swap_percent.set(result["swap_percent"])
    print(result)
    time.sleep(5)
