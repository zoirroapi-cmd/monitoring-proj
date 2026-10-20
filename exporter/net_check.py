import socket
import ssl
import subprocess
import time


def check_tcp(host, port=443):
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=3):
            pass
    except OSError:
        return None
    end = time.perf_counter()
    return round((end - start) * 1000, 1)


def ms_since(start):
    return round((time.perf_counter() - start) * 1000, 1)


def check_https(host, port=443, timeout=5):
    result = {"dns": None, "tcp": None, "tls": None, "http": None, "failed_at": None}
    stage = "dns"
    sock = None
    try:
        t = time.perf_counter()
        ip = socket.gethostbyname(host)
        result["dns"] = ms_since(t)

        stage = "tcp"
        t = time.perf_counter()
        sock = socket.create_connection((ip, port), timeout=timeout)
        result["tcp"] = ms_since(t)

        stage = "tls"
        t = time.perf_counter()
        context = ssl.create_default_context()
        tls = context.wrap_socket(sock, server_hostname=host)
        result["tls"] = ms_since(t)

        stage = "http"
        t = time.perf_counter()
        request = f"HEAD / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        tls.sendall(request.encode())
        if not tls.recv(1):
            raise OSError("соединение закрыто без ответа")
        result["http"] = ms_since(t)
    except OSError:
        result["failed_at"] = stage
    finally:
        if sock:
            sock.close()
    return result


def get_vpn_services():
    out = subprocess.run(
        ["scutil", "--nc", "list"],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    ).stdout
    services = {}
    for line in out.splitlines():
        if '"' not in line:
            continue
        name = line.split('"')[1]
        services[name] = "(Connected)" in line
    return services


def route_interface(ip="8.8.8.8"):
    out = subprocess.run(
        ["route", "-n", "get", ip],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    ).stdout
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("interface:"):
            return line.split(":", 1)[1].strip()
    return None


if __name__ == "__main__":
    print("VPN:", get_vpn_services())
    print("маршрут идёт через:", route_interface())
    for site in ["ya.ru", "youtube.com"]:
        print(site, check_https(site))
