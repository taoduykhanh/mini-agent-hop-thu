# -*- coding: utf-8 -*-
"""Nhiem vu t003 (Muse giao): thu adb vao tung index xem may nao phan hoi."""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools import _ldconsole

lc = _ldconsole()
for idx in ["0", "1"]:
    print("Thu adb echo vao index %s (15s)..." % idx, flush=True)
    try:
        p = subprocess.run([lc, "adb", "--index", idx, "--command", "shell echo ok"],
                           capture_output=True, timeout=15)
        print("index %s: rc=%d out=[%s] err=[%s]" % (
            idx, p.returncode,
            p.stdout.decode("utf-8", "replace")[:300].strip(),
            p.stderr.decode("utf-8", "replace")[:300].strip()), flush=True)
    except Exception as e:
        print("index %s LOI: %s %s" % (idx, type(e).__name__, e), flush=True)

print("XONG: t003 hoan tat", flush=True)
