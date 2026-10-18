# -*- coding: utf-8 -*-
"""Nhiem vu t007 (Muse giao): tim adb cua ban LDPlayer dang chay game."""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

base = r"C:\Program Files\ldplayer9box"
print("dir goc:", flush=True)
try:
    print(os.listdir(base), flush=True)
except Exception as e:
    print("LOI dir:", e, flush=True)

cands = []
for root, dirs, files in os.walk(base):
    for f in files:
        if f.lower() in ("adb.exe", "ldconsole.exe"):
            cands.append(os.path.join(root, f))
    if root.count(os.sep) - base.count(os.sep) >= 2:
        dirs[:] = []
print("tim thay:", flush=True)
for c in cands:
    print("  " + c, flush=True)

adb = next((c for c in cands if c.lower().endswith("adb.exe")), None)
if adb:
    print("thu adb devices cua ban nay:", flush=True)
    try:
        p = subprocess.run([adb, "devices"], capture_output=True, timeout=20)
        print(p.stdout.decode("utf-8", "replace")[:800], flush=True)
    except Exception as e:
        print("LOI:", type(e).__name__, e, flush=True)
else:
    print("KHONG thay adb.exe trong ban nay", flush=True)
print("XONG: t007 hoan tat", flush=True)
