# -*- coding: utf-8 -*-
"""逐段把 HTML 片段写入 .doc（经由 editor_sdk 的 doc_insert_html_content）。"""
import os, json, subprocess, sys

SKILL = r"D:\workbuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\workbuddy-local-office-edit"
PY = r"C:/Users/Lenovo/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
FILE_ID = "new_doc_840328248100_5cd3"


def call(tool, args):
    ap = os.path.join(HERE, "_args.json")
    with open(ap, "w", encoding="utf-8") as f:
        json.dump(args, f, ensure_ascii=False)
    r = subprocess.run([PY, "edsdk.py", "call", tool, "--json-file", ap],
                       cwd=SKILL, capture_output=True, text=True, encoding="utf-8")
    out = (r.stdout or "") + (r.stderr or "")
    for line in reversed(out.strip().split("\n")):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except Exception:
                continue
    raise RuntimeError("无法解析返回：\n" + out[:1500])


def pos(res, prev):
    p = res.get("position")
    if p is None:
        p = res.get("last_edit_index")
    return prev if p is None else p


steps = ["1_cover", "2_purpose", "3_process", "4_code", "5_test", "6_summary"]
idx = 0

for i, name in enumerate(steps):
    html = open(os.path.join(HERE, name + ".html"), encoding="utf-8").read()
    res = call("doc_insert_html_content", {"file_id": FILE_ID, "idx": idx, "html_text": html})
    idx = pos(res, idx)
    print("[%s] -> position=%s" % (name, idx))

    if name == "1_cover":
        res = call("doc_insert_page_break", {"file_id": FILE_ID, "idx": idx})
        idx = pos(res, idx)
        print("[page break] -> position=%s" % idx)

print("done, final idx =", idx)
