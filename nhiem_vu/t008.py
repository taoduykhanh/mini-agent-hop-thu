# -*- coding: utf-8 -*-
"""Nhiem vu t008: tim port VM dang nghe roi adb connect thu."""
import subprocess

def chay(cmd, timeout=30):
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout,
                           shell=isinstance(cmd, str))
        return p.stdout.decode("utf-8", "replace")[:2500].strip() or "(rong)"
    except Exception as e:
        return "LOI: %s %s" % (type(e).__name__, e)

print("B1: PID cua Ld9BoxHeadless", flush=True)
out1 = chay('tasklist /FI "IMAGENAME eq Ld9BoxHeadless.exe" /FO TABLE')
print(out1, flush=True)
pids = [t for t in out1.split() if t.isdigit()]
print("PIDs:", pids, flush=True)

print("B2: port LISTEN cua PID VM", flush=True)
ports = []
for pid in pids:
    ns = chay('netstat -ano | findstr "LISTENING" | findstr " %s"' % pid)
    print(ns, flush=True)
    for line in ns.splitlines():
        parts = line.split()
        if len(parts) >= 2 and ":" in parts[1]:
            port = parts[1].rsplit(":", 1)[-1]
            if port.isdigit() and port != "5037":
                ports.append(port)
ports = sorted(set(ports))
print("port ung vien:", ports, flush=True)

print("B3: adb connect tung port", flush=True)
adb = r"E:\LDPlayer\LDPlayer9\adb.exe"
for port in ports[:10]:
    print("connect 127.0.0.1:%s -> %s" % (port, chay([adb, "connect", "127.0.0.1:" + port], timeout=15)), flush=True)
print("B4: adb devices", flush=True)
print(chay([adb, "devices"], timeout=15), flush=True)
print("XONG: t008 hoan tat", flush=True)
