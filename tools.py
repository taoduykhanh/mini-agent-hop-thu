# -*- coding: utf-8 -*-
"""Bo tool cua mini-agent v4: cac ham Python thuan de nhiem vu goi truc tiep.

Khong con LLM cuc bo, khong can API key. Muse viet nhiem vu (file .py),
runner tai ve va chay, nhiem vu import cac ham o day de dung.
"""
import os
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_LDCONSOLE = None


def _ldconsole():
    global _LDCONSOLE
    if _LDCONSOLE:
        return _LDCONSOLE
    import json
    p = os.path.join(BASE_DIR, "config.json")
    cfg = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    c = cfg.get("ldconsole", r"C:\LDPlayer\LDPlayer9\ldconsole.exe")
    if not os.path.exists(c):
        raise RuntimeError("Khong tim thay ldconsole.exe: " + c)
    _LDCONSOLE = c
    return c


def _run(args, timeout=30):
    p = subprocess.run(args, capture_output=True, timeout=timeout, shell=False)
    out = (p.stdout or b"").decode("utf-8", "replace")
    err = (p.stderr or b"").decode("utf-8", "replace")
    txt = ("STDOUT:\n" + out + ("\nSTDERR:\n" + err if err else "")).strip()
    return txt[:4000] if txt else "(khong co output)"


def chay_lenh(lenh):
    """Chay 1 lenh shell Windows. Tra ve output (toi da 4000 ky tu)."""
    return _run(["cmd", "/c", lenh], timeout=60)


def doc_file(duong_dan):
    """Doc noi dung file text."""
    with open(duong_dan, encoding="utf-8", errors="replace") as f:
        return f.read()[:8000]


def ghi_file(duong_dan, noi_dung):
    """Ghi (hoac ghi de) file text."""
    with open(duong_dan, "w", encoding="utf-8") as f:
        f.write(noi_dung)
    return "Da ghi %d ky tu vao %s" % (len(noi_dung), duong_dan)


def liet_ke(duong_dan="."):
    """Liet ke file/thu muc trong 1 thu muc."""
    return "\n".join(sorted(os.listdir(duong_dan)))


def bam_ld(index, x, y):
    """Bam (tap) vao cua so LDPlayer so `index` tai toa do x, y."""
    lc = _ldconsole()
    _run([lc, "adb", "--index", str(index),
          "--command", "shell input tap %d %d" % (int(x), int(y))])
    return "Da bam (%d, %d) tren LDPlayer %s" % (int(x), int(y), index)


def chup_ld(index):
    """Chup man hinh cua so LDPlayer so `index`, luu file anh. Tra ve duong dan."""
    lc = _ldconsole()
    remote = "/sdcard/miniagent_shot.png"
    local = os.path.join(BASE_DIR, "shot_%s.png" % index)
    _run([lc, "adb", "--index", str(index),
          "--command", "shell screencap -p " + remote])
    time.sleep(0.5)
    _run([lc, "pull", "--index", str(index),
          "--remote", remote, "--local", local])
    if os.path.exists(local):
        return "Da luu anh: " + local
    return "Chup that bai (kiem tra LDPlayer co mo cua so %s khong)" % index


def _adb_path():
    return os.path.join(os.path.dirname(_ldconsole()), "adb.exe")


def tap_adb(serial, x, y, timeout=25):
    """Tap truc tiep qua adb (khong qua ldconsole)."""
    _run([_adb_path(), "-s", serial, "shell", "input", "tap",
          str(int(x)), str(int(y))], timeout=timeout)
    return "Da tap (%d, %d)" % (int(x), int(y))


def doc_vi_tri():
    """Doc vi tri cac nut da hieu chuan bang calib_nut.py."""
    import json
    p = os.path.join(BASE_DIR, "vi_tri_nut.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


def bam_nut(ten_nut, serial="emulator-5554"):
    """Bam nut da hieu chuan theo ten. Chay 'python calib_nut.py' truoc."""
    ds = doc_vi_tri()
    if ten_nut not in ds:
        raise RuntimeError("Chua hieu chuan nut '%s'. Chay: python calib_nut.py" % ten_nut)
    x, y = ds[ten_nut]
    return tap_adb(serial, x, y) + " [nut: %s]" % ten_nut
