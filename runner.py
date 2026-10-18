# -*- coding: utf-8 -*-
"""Runner thuong truc cua mini-agent v4.

Kien truc: Muse la NAO (giao nhiem vu, viet code, day len GitHub),
runner la TAY (chay tren may ban, thuc thi). Khong can API key nao ca.

Vong lap (moi 30 giay):
 1. Tu cap nhat: doc manifest.json, file code nao co phien ban moi thi tai ve.
    Neu chinh runner.py moi -> tu khoi dong lai.
 2. Nhan nhiem vu: doc nhiem_vu.json; co task_id moi thi tai nhiem_vu/<id>.py
    ve, chay (gioi han timeout), ghi ket qua len ket_qua/<id>.json,
    dong thoi bao ve hop thu de Muse biet.
"""
import base64
import json
import os
import re
import subprocess
import sys
import time

RUNNER_VERSION = "4.4"

if os.name == "nt":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import requests
except ImportError:
    requests = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRANG_THAI = os.path.join(BASE_DIR, "trang_thai.json")
LOG = os.path.join(BASE_DIR, "runner_log.txt")

REPO = "taoduykhanh/mini-agent-hop-thu"
BRANCH = "main"
RAW = "https://raw.githubusercontent.com/%s/%s" % (REPO, BRANCH)
API_CONTENTS = "https://api.github.com/repos/%s/contents" % REPO
POLL = 30


def load_cfg():
    p = os.path.join(BASE_DIR, "config.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


def log(msg):
    line = "[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def doc_trang_thai():
    if os.path.exists(TRANG_THAI):
        try:
            with open(TRANG_THAI, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"phien_ban": {}, "nhiem_vu_da_lam": []}


def luu_trang_thai(tt):
    with open(TRANG_THAI, "w", encoding="utf-8") as f:
        json.dump(tt, f, ensure_ascii=False, indent=1)


def tai_raw(path):
    r = requests.get(RAW + "/" + path, timeout=20)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.text


def github_token():
    t = os.environ.get("GITHUB_TOKEN", load_cfg().get("github_token", ""))
    if not t or t.startswith("DÁN"):
        raise RuntimeError("Chua co github_token trong config.json (xem README).")
    return t


def ghi_file_repo(path_repo, noi_dung_text, message):
    """Tao moi / ghi de 1 file text len repo (can token)."""
    token = github_token()
    h = {"Authorization": "Bearer " + token,
         "Accept": "application/vnd.github+json"}
    url = API_CONTENTS + "/" + path_repo
    r = requests.get(url + "?ref=" + BRANCH, headers=h, timeout=20)
    sha = r.json()["sha"] if r.status_code == 200 else None
    payload = {"message": message,
               "content": base64.b64encode(noi_dung_text.encode("utf-8")).decode(),
               "branch": BRANCH}
    if sha:
        payload["sha"] = sha
    r2 = requests.put(url, headers=h, json=payload, timeout=20)
    if r2.status_code not in (200, 201):
        raise RuntimeError("Ghi repo that bai: %s %s" % (r2.status_code, r2.text[:200]))


def tu_cap_nhat(tt):
    """Tai code moi theo manifest.json. Tra ve True neu runner.py doi -> can restart."""
    try:
        txt = tai_raw("manifest.json")
        if not txt:
            return False
        vers = json.loads(txt).get("phien_ban", {})
        restart = False
        for fname, v in vers.items():
            if not re.fullmatch(r"[a-z_]+\.py", fname):
                continue
            cur = tt.get("phien_ban", {}).get(fname, 0)
            if int(v) > int(cur):
                nd = tai_raw(fname)
                if nd is None:
                    continue
                with open(os.path.join(BASE_DIR, fname), "w", encoding="utf-8") as f:
                    f.write(nd)
                tt.setdefault("phien_ban", {})[fname] = int(v)
                log("Da cap nhat %s -> v%s" % (fname, v))
                if fname == "runner.py":
                    restart = True
        luu_trang_thai(tt)
        return restart
    except Exception as e:
        log("Loi tu cap nhat: %s" % e)
        return False


def lay_nhiem_vu():
    try:
        txt = tai_raw("nhiem_vu.json")
        return json.loads(txt) if txt else None
    except Exception as e:
        log("Loi doc nhiem vu: %s" % e)
        return None


def _kill_cay(pid):
    """Giet ca cay tien trinh cua nhiem vu (ke ca tien trinh con/chau
    nhu ldconsole.exe, adb.exe). subprocess.run mac dinh chi giet
    tien trinh truc tiep, de sot chau treo se giu ket noi adb bi ket."""
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                           capture_output=True, timeout=10)
        else:
            import signal
            os.killpg(os.getpgid(pid), signal.SIGKILL)
    except Exception as e:
        log("Khong giet duoc cay tien trinh %s: %s" % (pid, e))


def chay_nhiem_vu(nv):
    task_id = str(nv.get("task_id", ""))
    if not re.fullmatch(r"[A-Za-z0-9_-]+", task_id):
        log("task_id khong hop le: %s" % task_id)
        return
    log("Nhan nhiem vu %s: %s" % (task_id, nv.get("mo_ta", "")))
    code = tai_raw("nhiem_vu/%s.py" % task_id)
    if code is None:
        log("Khong tai duoc file nhiem vu %s" % task_id)
        return
    fpath = os.path.join(BASE_DIR, "_task_%s.py" % task_id)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(code)
    timeout = int(nv.get("timeout_giay", 300))
    # Chay nhiem vu trong nhom tien trinh rieng de khi timeout giet duoc ca cay.
    popen_kw = {}
    if os.name == "nt":
        popen_kw["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        popen_kw["start_new_session"] = True
    try:
        env = dict(os.environ)
        env["PYTHONUTF8"] = "1"  # task duoc phep in tieng Viet co dau
        p = subprocess.Popen([sys.executable, "-u", fpath],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=BASE_DIR, env=env, **popen_kw)
        try:
            so, se = p.communicate(timeout=timeout)
            trang_thai = "xong" if p.returncode == 0 else "loi"
        except subprocess.TimeoutExpired:
            log("Nhiem vu %s qua %d giay -> giet ca cay tien trinh" % (task_id, timeout))
            _kill_cay(p.pid)
            try:
                so, se = p.communicate(timeout=10)
            except Exception:
                so, se = b"", b""
            trang_thai = "timeout"
        out = (so or b"").decode("utf-8", "replace")[-6000:]
        err = (se or b"").decode("utf-8", "replace")[-2000:]
        dong = [d for d in out.strip().splitlines() if d.strip()]
        tom_tat = (dong[-1] if dong else "(khong co output)")[:300]
        if err and trang_thai == "loi":
            tom_tat = (tom_tat + " | STDERR: " + err.strip().splitlines()[-1])[:300]
        if trang_thai == "timeout":
            tom_tat = "Qua %d giay chua xong" % timeout
    except Exception as e:
        trang_thai = "loi"
        out, err = "", "Loi chay nhiem vu: %s" % e
        tom_tat = ("Loi chay nhiem vu: %s" % e)[:300]
    kq = {"task_id": task_id, "trang_thai": trang_thai, "tom_tat": tom_tat,
          "output": out, "stderr": err, "runner": RUNNER_VERSION,
          "luc": time.strftime("%Y-%m-%dT%H:%M:%S")}
    try:
        ghi_file_repo("ket_qua/%s.json" % task_id,
                      json.dumps(kq, ensure_ascii=False, indent=1),
                      "ket qua nhiem vu " + task_id)
        from hop_thu import bao_ket_qua
        bao_ket_qua(task_id, "%s: %s" % (trang_thai, tom_tat))
        log("Da bao cao ket qua %s" % task_id)
    except Exception as e:
        log("Loi ghi ket qua: %s" % e)


def main():
    if requests is None:
        print("Chua cai requests. Chay: pip install -r requirements.txt")
        return
    log("Runner v%s bat dau. Nhan Ctrl+C de dung." % RUNNER_VERSION)
    tt = doc_trang_thai()
    while True:
        try:
            if tu_cap_nhat(tt):
                log("Runner co ban moi -> tu khoi dong lai")
                os.execv(sys.executable, [sys.executable, os.path.join(BASE_DIR, "runner.py")])
            nv = lay_nhiem_vu()
            if nv and nv.get("task_id") and nv["task_id"] not in tt.get("nhiem_vu_da_lam", []):
                chay_nhiem_vu(nv)
                tt.setdefault("nhiem_vu_da_lam", []).append(nv["task_id"])
                luu_trang_thai(tt)
        except Exception as e:
            log("Loi vong lap: %s" % e)
        time.sleep(POLL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nRunner dung.")
