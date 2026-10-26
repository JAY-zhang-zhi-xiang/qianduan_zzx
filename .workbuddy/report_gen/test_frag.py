# -*- coding: utf-8 -*-
import json, os, subprocess
SKILL = r"D:/workbuddy/resources/app.asar.unpacked/resources/plugins/workbuddy-builtin/skills/workbuddy-local-office-edit"
PY = r"C:/Users/Lenovo/.workbuddy/binaries/python/envs/default/Scripts/python.exe"

def call(tool, args):
    ap = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_t.json")
    json.dump(args, open(ap, "w", encoding="utf-8"), ensure_ascii=False)
    r = subprocess.run([PY, "edsdk.py", "call", tool, "--json-file", ap], cwd=SKILL,
                       capture_output=True, text=True, encoding="utf-8")
    out = (r.stdout or "") + (r.stderr or "")
    for line in reversed(out.strip().split("\n")):
        line = line.strip()
        if line.startswith("{"):
            try: return json.loads(line)
            except Exception: pass
    raise RuntimeError(out[:800])


fid = "new_doc_978605793600_5813"
print("fid", fid)

line1 = "  &lt;a class=&quot;zzx-tabbar__item&quot; href=&quot;zone.html&quot;&gt;"
line2 = "    &lt;i class=&quot;iconfont icon-xiaoxi&quot;&gt;&lt;/i&gt;"
line3 = "  &lt;/a&gt;"

# A: 普通段落，无背景
A = '<p style="font-family:Consolas;font-size:9pt;text-indent:0;margin:0;line-height:1.2">A 方案：普通段落</p>'
for t in [line1, line2, line3]:
    A += '<p style="font-family:Consolas;font-size:9pt;text-indent:0;margin:0;line-height:1.2">%s</p>' % t

# B: 单格表格 + <br>
B = ('<table style="border-collapse:collapse;width:100%"><tr>'
     '<td style="border:1px solid #aaaaaa">'
     '<p style="font-family:Consolas;font-size:9pt;text-indent:0;margin:0;line-height:1.2">B 方案：单格表格+换行<br>'
     + line1 + '<br>' + line2 + '<br>' + line3 +
     '</p></td></tr></table>')

# C: 带边框的表格（给表1用）
C = ('<table style="border-collapse:collapse;width:100%"><tr>'
     '<td style="border:1px solid #888888;width:30%"><p style="font-size:10.5pt;text-indent:0;margin:0">导航位置</p></td>'
     '<td style="border:1px solid #888888;width:70%"><p style="font-size:10.5pt;text-indent:0;margin:0">iconfont 图标名</p></td>'
     '</tr><tr>'
     '<td style="border:1px solid #888888"><p style="font-size:10.5pt;text-indent:0;margin:0">首页</p></td>'
     '<td style="border:1px solid #888888"><p style="font-size:10.5pt;text-indent:0;margin:0">首页-选中</p></td>'
     '</tr></table>')

html = A + '<p style="text-indent:0;margin:10pt 0">&#160;</p>' + B + '<p style="text-indent:0;margin:10pt 0">&#160;</p>' + C
r = call("doc_insert_html_content", {"file_id": fid, "idx": 0, "html_text": html})
print("insert", r.get("message"), r.get("position"))
r = call("save_file", {"file_id": fid, "file_path": "C:/Users/Lenovo/Desktop/高级网页设计/.workbuddy/report_gen/test.docx"})
print(r.get("message") or r)
