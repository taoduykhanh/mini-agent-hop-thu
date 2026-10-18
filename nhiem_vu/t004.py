# -*- coding: utf-8 -*-
"""Nhiem vu t004 (Muse giao): quet adb xem thay duoc may ao nao."""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools import _ldconsole

lc = _ldconsole()
adb = os.path.join(os.path.dirname(lc), "adb.exe")
print("adb.exe: " + adb + " ton tai=" + str(os.path.exists(adb)), flush=True)

def chay(cmd, timeout=20):
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return "rc=%d out=[%s] err=[%s]" % (
            p.returncode,
            p.stdout.decode("utf-8", "replace")[:500].strip(),
            p.stderr.decode("utf-8", "replace")[:300].strip())
    except Exception as e:
        return "LOI: %s %s" % (type(e).__name__, e)

print("B1: adb devices", flush=True)
print(chay([adb, "devices"]), flush=True)
print("B2: kill-server + start-server", flush=True)
print(chay([adb, "kill-server"], timeout=10), flush=True)
print(chay([adb, "start-server"]), flush=True)
print("B3: adb devices sau restart", flush=True)
print(chay([adb, "devices"]), flush=True)
print("B4: thu connect thu cong cong 5555/5557", flush=True)
for port in [5555, 5557]:
    print("connect 127.0.0.1:%d -> %s" % (port, chay([adb, "connect", "127.0.0.1:%d" % port], timeout=15)), flush=True)
print("B5: adb devices cuoi", flush=True)
print(chay([adb, "devices"]), flush=True)
print("XONG: t004 hoan tat", flush=True)
