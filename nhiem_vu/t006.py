# -*- coding: utf-8 -*-
"""Nhiem vu t006 (Muse giao): tim may ao dang chay thuoc ban LDPlayer nao."""
import subprocess

def chay(cmd, timeout=30):
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout, shell=True)
        return p.stdout.decode("utf-8", "replace")[:2000].strip() or "(rong)"
    except Exception as e:
        return "LOI: %s %s" % (type(e).__name__, e)

print("B1: duong dan process gia lap dang chay", flush=True)
print(chay('wmic process get Name,ExecutablePath | findstr /i "dnplayer VBoxHeadless ldplayer"'), flush=True)
print("B2: thu muc LDPlayer o E", flush=True)
print(chay('dir "E:\\LDPlayer" /b'), flush=True)
print("B3: port LISTEN lien quan adb", flush=True)
print(chay('netstat -ano | findstr "LISTENING" | findstr ":5555 :5557 :5037"'), flush=True)
print("XONG: t006 hoan tat", flush=True)
