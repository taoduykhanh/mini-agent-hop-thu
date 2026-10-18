# -*- coding: utf-8 -*-
"""Nhiem vu t012: auto thu hoi do rac - Mo Tui -> Thu Hoi -> Thu Hoi."""
import os, sys, subprocess, time, re
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

def adb_run(args, timeout=25, serial=None):
    cmd = [adb] + (["-s", serial] if serial else []) + args
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return p.returncode, p.stdout.decode("utf-8", "replace").strip(), p.stderr.decode("utf-8", "replace")[:200].strip()
    except Exception as e:
        return -1, "", "LOI: %s" % e

def tap(s, fx, fy, w, h):
    x, y = int(fx * w), int(fy * h)
    adb_run(["shell", "input", "tap", str(x), str(y)], serial=s)
    return (x, y)

def shot(s, name):
    remote = "/sdcard/%s.png" % name
    local = os.path.join(BASE, name + ".png")
    adb_run(["shell", "screencap", "-p", remote], serial=s)
    time.sleep(1)
    adb_run(["pull", remote, local], serial=s)
    return local if os.path.exists(local) else "THAT BAI"

print("B0: tim device + kich thuoc man hinh", flush=True)
rc, out, err = adb_run(["devices"])
print(out, flush=True)
m = re.search(r"(emulator-\d+)\s+device", out)
s = m.group(1) if m else "emulator-5554"
print("serial: " + s, flush=True)
rc, out, err = adb_run(["shell", "wm", "size"], serial=s)
m2 = re.search(r"(\d+)x(\d+)", out)
w, h = (int(m2.group(1)), int(m2.group(2))) if m2 else (1280, 720)
print("w=%d h=%d" % (w, h), flush=True)

print("B1: bam nut Tui", flush=True)
print("tap " + str(tap(s, 0.935, 0.30, w, h)), flush=True)
time.sleep(2)
print("anh: " + shot(s, "t012_1_mo_tui"), flush=True)

print("B2: bam nut Thu Hoi trong tui", flush=True)
print("tap " + str(tap(s, 0.62, 0.90, w, h)), flush=True)
time.sleep(2)
print("anh: " + shot(s, "t012_2_thu_hoi"), flush=True)

print("B3: bam nut Thu Hoi trong giao dien thu hoi", flush=True)
print("tap " + str(tap(s, 0.85, 0.90, w, h)), flush=True)
time.sleep(2)
print("anh: " + shot(s, "t012_3_xong"), flush=True)
print("XONG: t012 hoan tat", flush=True)
