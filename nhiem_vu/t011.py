# -*- coding: utf-8 -*-
"""Nhiem vu t011: chup man hinh bang adb truc tiep (bo qua ldconsole)."""
import os, sys, subprocess, time
if os.name == "nt":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools import _ldconsole

lc = _ldconsole()
adb = os.path.join(os.path.dirname(lc), "adb.exe")
BASE = os.path.dirname(os.path.abspath(__file__))

def adb_run(args, timeout=25):
    try:
        p = subprocess.run([adb] + args, capture_output=True, timeout=timeout)
        return p.returncode, p.stdout.decode("utf-8", "replace")[:500].strip(), p.stderr.decode("utf-8", "replace")[:300].strip()
    except Exception as e:
        return -1, "", "LOI: %s %s" % (type(e).__name__, e)

print("B1: adb devices", flush=True)
rc, out, err = adb_run(["devices"])
print(out, flush=True)

print("B2: ldconsole echo index 0/1", flush=True)
for idx in ["0", "1"]:
    try:
        p = subprocess.run([lc, "adb", "--index", idx, "--command", "shell echo ok"],
                           capture_output=True, timeout=15)
        print("index %s: rc=%d out=[%s]" % (idx, p.returncode, p.stdout.decode("utf-8", "replace")[:200].strip()), flush=True)
    except Exception as e:
        print("index %s LOI: %s" % (idx, e), flush=True)

print("B3: chup truc tiep qua adb -s emulator-5554", flush=True)
remote = "/sdcard/mu_t011.png"
local = os.path.join(BASE, "shot_t011.png")
adb_run(["-s", "emulator-5554", "shell", "screencap", "-p", remote])
time.sleep(1)
rc, out, err = adb_run(["-s", "emulator-5554", "pull", remote, local])
print("pull rc=%d %s %s" % (rc, out, err), flush=True)
print("file ton tai: %s" % os.path.exists(local), flush=True)
if os.path.exists(local):
    print("OK: Da luu anh: " + local, flush=True)
print("XONG: t011 hoan tat", flush=True)
