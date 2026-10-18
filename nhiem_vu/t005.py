# -*- coding: utf-8 -*-
"""Nhiem vu t005 (Muse giao): kiem tra process gia lap nao dang chay that."""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def chay(cmd, timeout=20):
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout, shell=True)
        return p.stdout.decode("utf-8", "replace")[:1500].strip() or "(rong)"
    except Exception as e:
        return "LOI: %s %s" % (type(e).__name__, e)

print("B1: process dnplayer (may ao LDPlayer)", flush=True)
print(chay('tasklist /FI "IMAGENAME eq dnplayer.exe" /FO TABLE'), flush=True)
print("B2: cac process gia lap pho bien khac", flush=True)
print(chay('tasklist | findstr /i "HD-Player Nox MuMu MuMuPlayer memu bluestacks"'), flush=True)
print("B3: port adb dang nghe (5555/5557/5037)", flush=True)
print(chay('netstat -ano | findstr "5555 5557 5037"'), flush=True)
print("XONG: t005 hoan tat", flush=True)
