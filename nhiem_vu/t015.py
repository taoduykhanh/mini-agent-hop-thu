# -*- coding: utf-8 -*-
"""Nhiem vu t015: tu tim API HOM DO / KHO trong ma game da dich nguoc tren PC nay,
+ liet ke cac file LOCAL cua project mu-vng-bot ma GitHub khong co (cfg_*, bundle,
src_lua...) de Muse doc hieu ma khong can user gui tay.

Chi DOC va bao cao. Khong sua/xoa bat ky file nao cua game hay cua project.
Bao cao day du ghi vao ket_qua/t015_kho_api.txt tren repo hop thu (qua API GitHub,
token doc tu config.json canh runner). Tom tat ngan in ra dong cuoi.
"""
import base64
import glob
import json
import os
import re
import sys
import time

if os.name == "nt":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE = os.path.dirname(os.path.abspath(__file__))
BAT_DAU = time.time()
NGAN_SACH = 420          # giay: chừa thời gian upload báo cáo
R = []                   # các dòng báo cáo


def p(s=""):
    print(s, flush=True)
    R.append(str(s))


def het_gio():
    return time.time() - BAT_DAU > NGAN_SACH


# ---------- 1. Tìm các gốc chứa mã game / project ----------
p("=== T015: TIM API KHO / HOM DO ===")
p("Thu muc agent: %s" % BASE)
p("Thu muc nha user: %s" % os.path.expanduser("~"))

TEN_THU_MUC_LUA = {"src_lua", "src_luac", "lua_out", "game_pull", "lua_src"}
BO_QUA = {"windows", "program files", "program files (x86)", "programdata",
          "$recycle.bin", "system volume information", "node_modules", ".git"}

goc_lua = []        # thu muc chua nhieu file .lua cua game
clone_bot = []      # thu muc mu-vng-bot tren PC


def dem_lua(path, cap=400):
    n = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d.lower() not in BO_QUA]
        n += sum(1 for f in files if f.endswith(".lua"))
        if n >= cap:
            return n
    return n


def quet_o(dia, do_sau_toi_da=5):
    """Đi bộ 1 ổ đĩa/thư mục lớn ở độ sâu hạn chế, tìm gốc lua + clone bot."""
    if not os.path.isdir(dia):
        return
    for root, dirs, files in os.walk(dia):
        sau = root[len(dia):].count(os.sep)
        if sau >= do_sau_toi_da:
            dirs[:] = []
        dirs[:] = [d for d in dirs if d.lower() not in BO_QUA]
        ten = os.path.basename(root).lower()
        if ten in TEN_THU_MUC_LUA:
            goc_lua.append(root)
            dirs[:] = []
        elif ten == "mu-vng-bot":
            clone_bot.append(root)
            goc_lua.append(root)          # trong clone có lua_inject + cfg local
            dirs[:] = []                  # không chui sâu vào clone ở vòng này
        elif any(f.startswith("cfg_") and f.endswith(".lua") for f in files):
            goc_lua.append(root)          # thư mục chứa thẳng cfg_*.lua = mã config game
        if het_gio():
            return


# đoán nhanh các vị trí đã biết trước
doan = [
    r"E:\GitHub\mu-vng-bot", r"D:\GitHub\mu-vng-bot", r"C:\GitHub\mu-vng-bot",
    os.path.join(os.path.expanduser("~"), "Downloads", "mini-agent-v4"),
    BASE,
]
for d in doan:
    if os.path.isdir(d):
        if os.path.basename(d).lower() == "mu-vng-bot" and d not in clone_bot:
            clone_bot.append(d)
        if d not in goc_lua:
            goc_lua.append(d)

# scratchpad của Claude Code (build_patch.py từng trỏ tới ...\scratchpad\game_pull)
for mau in glob.glob(r"C:\Users\*\AppData\Local\Temp\claude\*\*\scratchpad"):
    goc_lua.append(mau)
    gp = os.path.join(mau, "game_pull")
    if os.path.isdir(gp):
        goc_lua.append(gp)

for dia in (r"E:\ ", r"D:\ ", r"C:\Users"):
    quet_o(dia.strip(), 5)
    if het_gio():
        break

goc_lua = sorted(set(goc_lua))
p("")
p("--- GOC LUA TIM THAY (%d) ---" % len(goc_lua))
for g in goc_lua:
    p("%s  (~%d file .lua)" % (g, dem_lua(g)))

# ---------- 2. Grep API kho trong các gốc lua ----------
TU_DIEM = [
    (re.compile(r"warehouse", re.I), 4),
    (re.compile(r"storage", re.I), 4),
    (re.compile(r"depot", re.I), 4),
    (re.compile(r"homdo|hom_do", re.I), 3),
    (re.compile(r"UIID\.\w*(?:Ware|Storage|Depot|Kho)\w*"), 4),
    (re.compile(r"\w*(?:Warehouse|Storage|Depot)\w*(?:Message|Data|Controller|Manager)"), 4),
    (re.compile(r"Req\w*(?:Warehouse|Storage|Depot)\w*"), 4),
    (re.compile(r"\bbank\b", re.I), 1),
]
MO_NE0 = re.compile(r"BagSellInfoUI|BagSell")   # mỏ neo: file định nghĩa UIID/Message

khop = []        # (diem, file, dong_so, noi_dung)
neo = []         # dòng chứa mỏ neo
so_file_quet = 0
for g in goc_lua:
    if het_gio():
        break
    for root, dirs, files in os.walk(g):
        dirs[:] = [d for d in dirs if d.lower() not in BO_QUA and d != "__pycache__"]
        for fn in files:
            if not (fn.endswith(".lua") or fn.endswith(".txt")):
                continue
            path = os.path.join(root, fn)
            try:
                if os.path.getsize(path) > 8 * 1024 * 1024:
                    continue
                with open(path, encoding="utf-8", errors="replace") as f:
                    lines = f.read().splitlines()
            except Exception:
                continue
            so_file_quet += 1
            for i, dong in enumerate(lines, 1):
                d = dong.strip()
                if not d:
                    continue
                if MO_NE0.search(d):
                    neo.append((path, i, d[:220]))
                diem = sum(w for rx, w in TU_DIEM if rx.search(d))
                if diem >= 3:
                    khop.append((diem, path, i, d[:220]))
        if het_gio():
            break

khop.sort(key=lambda x: -x[0])
p("")
p("--- KET QUA GREP KHO (quet %d file, %d dong khop) ---" % (so_file_quet, len(khop)))
for diem, path, i, d in khop[:500]:
    p("[%d] %s:%d: %s" % (diem, path, i, d))
p("")
p("--- MO NEO BagSell (file nao dinh nghia UIID/Message thi kho cung o do) ---")
for path, i, d in neo[:80]:
    p("%s:%d: %s" % (path, i, d))

# ---------- 3. Liệt kê file local của clone mu-vng-bot (phần GitHub không có) ----------
p("")
p("--- FILE LOCAL TRONG MU-VNG-BOT (%d clone) ---" % len(clone_bot))
for c in clone_bot:
    p("CLONE: %s" % c)
    for root, dirs, files in os.walk(c):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for fn in sorted(files):
            path = os.path.join(root, fn)
            try:
                kt = os.path.getsize(path)
            except Exception:
                kt = -1
            p("  %s  (%d byte)" % (os.path.relpath(path, c), kt))
        if het_gio():
            break

# ---------- 4. Upload báo cáo lên hộp thư ----------
txt = "\n".join(R)
if len(txt) > 350000:
    txt = txt[:350000] + "\n... (bao cao qua dai, da cat bot)"


def ghi_file_repo(path_repo, noi_dung, message):
    import requests
    cfg = {}
    p_cfg = os.path.join(BASE, "config.json")
    if os.path.exists(p_cfg):
        cfg = json.load(open(p_cfg, encoding="utf-8"))
    token = os.environ.get("GITHUB_TOKEN", cfg.get("github_token", ""))
    if not token or token.startswith("DÁN"):
        raise RuntimeError("khong co github_token trong config.json cua agent")
    h = {"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json"}
    url = "https://api.github.com/repos/taoduykhanh/mini-agent-hop-thu/contents/" + path_repo
    r = requests.get(url + "?ref=main", headers=h, timeout=20)
    payload = {"message": message, "branch": "main",
               "content": base64.b64encode(noi_dung.encode("utf-8")).decode()}
    if r.status_code == 200:
        payload["sha"] = r.json()["sha"]
    r2 = requests.put(url, headers=h, json=payload, timeout=30)
    if r2.status_code not in (200, 201):
        raise RuntimeError("ghi repo loi %s: %s" % (r2.status_code, r2.text[:200]))


da_upload = "khong"
try:
    ghi_file_repo("ket_qua/t015_kho_api.txt", txt, "t015: bao cao tim API kho (agent tu tim tren PC)")
    da_upload = "co"
except Exception as e:
    p("(loi upload bao cao: %s)" % e)

print("XONG t015: %d goc lua, %d dong khop kho, %d dong neo, upload=%s"
      % (len(goc_lua), len(khop), len(neo), da_upload), flush=True)
