# -*- coding: utf-8 -*-
"""Nhiem vu t014: trich APK SmartPK de phan tich."""
import os, sys, subprocess, re
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

def adb_run(args, timeout=30):
    try:
        p = subprocess.run([adb] + args, capture_output=True, timeout=timeout)
        return p.stdout.decode("utf-8", "replace").strip()
    except Exception as e:
        return "LOI: %s" % e

print("B1: liet ke app ben thu 3", flush=True)
pkgs = adb_run(["shell", "pm", "list", "packages", "-3"])
print(pkgs, flush=True)

cands = [l.replace("package:", "").strip() for l in pkgs.splitlines()
         if "smart" in l.lower()]
print("nghi van SmartPK: %s" % cands, flush=True)
if not cands:
    print("KHONG tim thay -> dung, cho Muse xem danh sach tren", flush=True)
    raise SystemExit(0)

pkg = cands[0]
print("B2: pull APK cua " + pkg, flush=True)
paths = [l.replace("package:", "").strip()
         for l in adb_run(["shell", "pm", "path", pkg]).splitlines() if l.strip()]
print(paths, flush=True)
saved = []
for i, rp in enumerate(paths):
    local = os.path.join(BASE, "smartpk_%d.apk" % i)
    adb_run(["pull", rp, local], timeout=60)
    if os.path.exists(local):
        saved.append("%s (%d bytes)" % (local, os.path.getsize(local)))
print("da pull: %s" % saved, flush=True)

print("B3: thong tin package", flush=True)
dumpsys = adb_run(["shell", "dumpsys", "package", pkg])
m = re.search(r"versionName=(\S+)", dumpsys)
print("versionName: %s" % (m.group(1) if m else "?"), flush=True)
perms = sorted(set(re.findall(r"android\.permission\.([A-Z_]+)", dumpsys)))
print("permissions (%d): %s" % (len(perms), ", ".join(perms[:40])), flush=True)
print("XONG: t014 hoan tat", flush=True)
