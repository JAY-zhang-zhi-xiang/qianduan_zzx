# -*- coding: utf-8 -*-
"""重建整份报告：新建 docx → A4 → 逐段写入 → 页码 → 保存。"""
import os, re, json, subprocess

SKILL = r"D:\workbuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\workbuddy-local-office-edit"
PY = r"C:/Users/Lenovo/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = "C:/Users/Lenovo/Desktop/高级网页设计/24002060419-张志翔-图像解决方案项目报告.docx"


def raw(tool, args=None):
    ap = os.path.join(HERE, "_args.json")
    if args is None:
        cmd = [PY, "edsdk.py", "call", tool]
    else:
        with open(ap, "w", encoding="utf-8") as f:
            json.dump(args, f, ensure_ascii=False)
        cmd = [PY, "edsdk.py", "call", tool, "--json-file", ap]
    r = subprocess.run(cmd, cwd=SKILL, capture_output=True, text=True, encoding="utf-8")
    return (r.stdout or "") + (r.stderr or "")


def call(tool, args):
    out = raw(tool, args)
    for line in reversed(out.strip().split("\n")):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except Exception:
                continue
    return {"_raw": out}


# 1. 新建
out = raw("create_doc")
m = re.search(r"file_id=([A-Za-z0-9_\-]+)", out)
fid = m.group(1)
print("new doc:", fid)

# 2. 页面
call("doc_modify_section", {"file_id": fid, "section_index": 0,
                            "page_width": 595.3, "page_height": 841.9,
                            "top_margin": 72, "bottom_margin": 72,
                            "left_margin": 79, "right_margin": 79})

# 3. 逐段写入
steps = ["1_cover", "2_purpose", "3a_process", "3b_icons", "3c_icons", "4_code", "5_test", "6_summary"]
idx = 0
for name in steps:
    html = open(os.path.join(HERE, name + ".html"), encoding="utf-8").read()
    res = call("doc_insert_html_content", {"file_id": fid, "idx": idx, "html_text": html})
    p = res.get("position")
    if p is None:
        p = res.get("last_edit_index")
    if p is not None:
        idx = p
    print("[%s] -> %s" % (name, idx))
    if name in ("1_cover", "3b_icons"):
        res = call("doc_insert_page_break", {"file_id": fid, "idx": idx})
        p = res.get("position") or res.get("last_edit_index")
        if p is not None:
            idx = p
        print("[page break] -> %s" % idx)

# 4. 页码
call("doc_set_page_number", {"file_id": fid, "section_index": 0,
                             "position": "center", "skip_first_page": True})

# 5. 保存
out = raw("save_file", {"file_id": fid, "file_path": TARGET})
print(out.strip().split("\n")[-1][:200])
print("FILE_ID_FOR_REUSE=", fid)
