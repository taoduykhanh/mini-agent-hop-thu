# -*- coding: utf-8 -*-
"""Nhiem vu t001 (Muse giao): kiem tra runner song + chup man hinh LDPlayer 0."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools import chay_lenh, chup_ld

print("Runner dang chay tot!")
print(chay_lenh("echo hello tu may cua ban"))
print(chup_ld(0))
print("XONG: t001 hoan tat")
