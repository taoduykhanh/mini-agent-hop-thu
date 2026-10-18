# -*- coding: utf-8 -*-
"""Nhiem vu t002 (Muse giao): chan doan xem lenh ldconsole ket o buoc nao."""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools import _ldconsole

print("B1: tim ldconsole...", flush=True)
try:
    lc = _ldconsole()
    print("B1 OK: " + lc, flush=True)
except Exception as e:
    print("B1 LOI: " + str(e), flush=True)
    raise SystemExit(1)

print("B2: thu lenh list (10s)...", flush=True)
try:
    p = subprocess.run([lc, "list"], capture_output=True, timeout=10)
    print("B2 OK rc=%d: %s" % (p.returncode, p.stdout.decode("utf-8", "replace")[:400]), flush=True)
except Exception as e:
    print("B2 LOI: %s %s" % (type(e).__name__, e), flush=True)

print("B3: thu adb echo (15s)...", flush=True)
try:
    p = subprocess.run([lc, "adb", "--index", "0", "--command", "shell echo ok"],
                       capture_output=True, timeout=15)
    print("B3 OK rc=%d: %s" % (p.returncode, p.stdout.decode("utf-8", "replace")[:400]), flush=True)
except Exception as e:
    print("B3 LOI: %s %s" % (type(e).__name__, e), flush=True)

print("XONG: t002 hoan tat", flush=True)
