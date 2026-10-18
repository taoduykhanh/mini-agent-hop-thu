# -*- coding: utf-8 -*-
"""Nhiem vu t013: auto thu hoi bang toa do da hieu chuan."""
import os, sys, subprocess, time, re
if os.name == "nt":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools import _ldconsole, bam_nut, doc_vi_tri

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

print("B0: doc vi tri da hieu chuan", flush=True)
ds = doc_vi_tri()
print("nut: %s" % ds, flush=True)
for k in ["nut_tui", "nut_thu_hoi_1", "nut_thu_hoi_2"]:
    if k not in ds:
        print("THIEU nut %s -> dung lai" % k, flush=True)
        raise SystemExit(1)

rc, out, err = adb_run(["devices"])
m = re.search(r"(emulator-\d+)\s+device", out)
s = m.group(1) if m else "emulator-5554"
print("serial: " + s, flush=True)

def shot(name):
    remote = "/sdcard/%s.png" % name
    local = os.path.join(BASE, name + ".png")
    adb_run(["shell", "screencap", "-p", remote], serial=s)
    time.sleep(1)
    adb_run(["pull", remote, local], serial=s)
    return local if os.path.exists(local) else "THAT BAI"

print("B1: bam nut_tui", flush=True)
print(bam_nut("nut_tui", serial=s), flush=True)
time.sleep(2)
print("anh: " + shot("t013_1_mo_tui"), flush=True)

print("B2: bam nut_thu_hoi_1", flush=True)
print(bam_nut("nut_thu_hoi_1", serial=s), flush=True)
time.sleep(2)
print("anh: " + shot("t013_2_thu_hoi"), flush=True)

print("B3: bam nut_thu_hoi_2", flush=True)
print(bam_nut("nut_thu_hoi_2", serial=s), flush=True)
time.sleep(2)
print("anh: " + shot("t013_3_xong"), flush=True)
print("XONG: t013 hoan tat", flush=True)
