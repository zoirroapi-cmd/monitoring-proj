import math
import threading
import time

from prometheus_client import Gauge

from net_check import check_https, get_vpn_services, route_interface

TARGETS = ["ya.ru", "youtube.com"]
STAGES = ["dns", "tcp", "tls", "http"]
INTERVAL = 15

vpn_connected = Gauge(
    "mac_vpn_connected", "VPN service connected (1/0)", ["service"]
)
via_tunnel = Gauge(
    "mac_route_via_tunnel", "Internet traffic goes through a tunnel interface (1/0)"
)
check_ok = Gauge(
    "mac_net_check_ok", "HTTPS check passed all stages (1/0)", ["target"]
)
check_ms = Gauge(
    "mac_net_check_ms", "Time of each check stage in ms", ["target", "stage"]
)
check_failed = Gauge(
    "mac_net_check_failed_stage", "1 if the check broke at this stage", ["target", "stage"]
)


def collect_once():
    for name, connected in get_vpn_services().items():
        vpn_connected.labels(service=name).set(1 if connected else 0)

    iface = route_interface()
    via_tunnel.set(1 if iface and iface.startswith("utun") else 0)

    for target in TARGETS:
        result = check_https(target)
        check_ok.labels(target=target).set(1 if result["failed_at"] is None else 0)
        for stage in STAGES:
            value = result[stage]
            check_ms.labels(target=target, stage=stage).set(
                math.nan if value is None else value
            )
            check_failed.labels(target=target, stage=stage).set(
                1 if result["failed_at"] == stage else 0
            )


def loop():
    while True:
        try:
            collect_once()
        except Exception as e:
            print("net check error:", e)
        time.sleep(INTERVAL)


def start_network_thread():
    threading.Thread(target=loop, daemon=True).start()