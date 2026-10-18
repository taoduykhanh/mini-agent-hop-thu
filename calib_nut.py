# -*- coding: utf-8 -*-
"""Tool hieu chuan vi tri nut bam. CHAY TRUC TIEP TREN PC (khong qua mailbox).

Cach dung:
  pip install opencv-python   (chi can 1 lan)
  python calib_nut.py

Quy trinh moi nut:
  1. Nhap ten nut (khong dau, vd: nut_tui)
  2. Chon so giay dem nguoc (mac dinh 5)
  3. Nhan Enter -> dem nguoc -> BAN CHUYEN SANG LDPLAYER, mo dung man hinh
  4. Tool tu chup man hinh, hien cua so anh -> click chuot trai vao nut
Ket qua luu vao vi_tri_nut.json. Cac task sau goi bam_nut("ten_nut").
"""
import os
import sys
import subprocess
import time
import json
import re

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from tools import _ldconsole

try:
    import cv2
except ImportError:
    print("Chua co opencv. Chay lenh: pip install opencv-python")
    sys.exit(1)

adb = os.path.join(os.path.dirname(_ldconsole()), "adb.exe")


def adb_run(args, timeout=25):
    p = subprocess.run([adb] + args, capture_output=True, timeout=timeout)
    return p.stdout.decode("utf-8", "replace").strip()


m = re.search(r"(emulator-\d+)\s+device", adb_run(["devices"]))
serial = m.group(1) if m else "emulator-5554"
print("Dang dung may: " + serial, flush=True)


def chup():
    remote = "/sdcard/calib_tmp.png"
    local = os.path.join(BASE, "calib_tmp.png")
    adb_run(["-s", serial, "shell", "screencap", "-p", remote])
    time.sleep(1)
    adb_run(["-s", serial, "pull", remote, local])
    return local


fp = os.path.join(BASE, "vi_tri_nut.json")
ds = {}
if os.path.exists(fp):
    ds = json.load(open(fp, encoding="utf-8"))

print("=== HIEU CHUAN NUT BAM ===", flush=True)
print("Go 'xong' de ket thuc.", flush=True)
while True:
    ten = input("\nTen nut (vd: nut_tui) [xong = ket thuc]: ").strip()
    if ten.lower() == "xong":
        break
    if not ten:
        continue
    s_giay = input("So giay dem nguoc de mo man hinh game [Enter = 5]: ").strip()
    try:
        giay = int(s_giay) if s_giay else 5
    except ValueError:
        giay = 5
    input("Nhan Enter de bat dau dem nguoc %d giay, ROI CHUYEN NGAY SANG LDPLAYER... " % giay)
    for i in range(giay, 0, -1):
        print("  %d..." % i, flush=True)
        time.sleep(1)
    print("Chup!", flush=True)
    img = cv2.imread(chup())
    if img is None:
        print("Chup that bai, thu lai nut nay.", flush=True)
        continue
    h, w = img.shape[:2]
    scale = min(1.0, 1100.0 / w)
    small = cv2.resize(img, (int(w * scale), int(h * scale))) if scale < 1 else img
    win = "Click vao nut: %s" % ten
    diem = []

    def on_click(ev, x, y, flags, param):
        if ev == cv2.EVENT_LBUTTONDOWN:
            diem.append((int(x / scale), int(y / scale)))
            cv2.destroyAllWindows()

    cv2.imshow(win, small)
    cv2.setMouseCallback(win, on_click)
    cv2.waitKey(0)
    if diem:
        ds[ten] = [diem[0][0], diem[0][1]]
        print("Da luu %s = %s" % (ten, diem[0]), flush=True)
    else:
        print("Chua click -> bo qua nut nay.", flush=True)

json.dump(ds, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nXong! Da luu %d nut vao vi_tri_nut.json" % len(ds), flush=True)
