# -*- coding: utf-8 -*-
"""Nhiem vu t009: kiem tra adb sau khi user bat Debug ADB + restart VM."""
import os, sys, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools import _ldconsole, _run, chup_ld

lc = _ldconsole()
adb = os.path.join(os.path.dirname(lc), "adb.exe")

def adb_run(args, timeout=20):
    try:
        p = subprocess.run([adb] + args, capture_output=True, timeout=timeout)
        return p.stdout.decode("utf-8", "replace")[:800].strip() or "(rong)"
    except Exception as e:
        return "LOI: %s %s" % (type(e).__name__, e)

print("B1: don dep offline entries", flush=True)
print(adb_run(["disconnect"]), flush=True)

print("B2: adb devices (thử 3 lần, cách 20s)", flush=True)
devs = ""
for i in range(3):
    devs = adb_run(["devices"])
    print("lan %d: %s" % (i + 1, devs), flush=True)
    if "emulator" in devs or "\tdevice" in devs:
        break
    time.sleep(20)

if "emulator" in devs or "\tdevice" in devs:
    print("B3: THAY THIET BI! chup man hinh index 0", flush=True)
    try:
        print(chup_ld(0), flush=True)
    except Exception as e:
        print("chup_ld LOI: %s" % e, flush=True)
else:
    print("B3: van chua thay device, thu echo qua ldconsole", flush=True)
    for idx in ["0", "1"]:
        print("index %s -> %s" % (idx, _run([lc, "adb", "--index", idx, "--command", "shell echo ok"], timeout=15)[:300]), flush=True)
print("XONG: t009 hoan tat", flush=True)
