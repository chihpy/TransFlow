"""
"""
import os
import re
import fitz

from utils import mkdir, txt_dump

SOURCE_DIR = os.path.join('data', 'source')
DEST_DIR = os.path.join('data', 'parsed_txt')
mkdir(DEST_DIR)

page_begin = 70
page_end = 84

#def pdf_cleaner(text):
#    # split to lines
#    lines = text.split("\n")
#    # filter empty lines
#    non_empty_lines = [line.strip() for line in lines if line.strip() != ""]
#    # join to text
#    text = "\n".join(non_empty_lines)
#    return text

#def pdf_cleaner(text):
#    lines = text.split("\n")
#    cleaned_lines = []
#
#    # 先過濾頁碼行（只包含數字，且在 70~84 之間）
#    for line in lines:
#        stripped = line.strip()
#        if stripped.isdigit():
#            num = int(stripped)
#            if 70 <= num <= 84:
#                continue  # 跳過頁碼
#        cleaned_lines.append(stripped)
#
#    # 合併被斷掉的句子
#    merged_lines = []
#    buffer = ""
#    sentence_end = re.compile(r'[。．.!?！？]$')  # 中文+英文句號符號
#
#    for line in cleaned_lines:
#        if not buffer:
#            buffer = line
#            continue
#
#        # 如果前一行不是句尾，代表要跟這一行合併
#        if not sentence_end.search(buffer):
#            buffer += " " + line
#        else:
#            merged_lines.append(buffer)
#            buffer = line
#
#    if buffer:
#        merged_lines.append(buffer)
#
#    # 去掉空行
#    merged_lines = [l for l in merged_lines if l.strip() != ""]
#
#    return "\n".join(merged_lines)

def pdf_cleaner(text: str) -> str:
    # 正規化換行
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 分行 + 前處理
    lines = []
    for raw in text.split("\n"):
        s = raw.strip()
        if not s:
            continue
        # 1) 去掉只含數字且為 70~84 的頁碼行
        if s.isdigit():
            n = int(s)
            if 70 <= n <= 84:
                continue
        # 2) 把行首的 "f" + 空白/Tab 改成 "- "
        s = re.sub(r'^f[\t ]+', '- ', s)
        lines.append(s)

    if not lines:
        return ""

    # 3) 合併被硬切的行：只有遇到句尾標點才換行
    sentence_end = re.compile(r'[。．.!?！？](?:["”’)\]]+)?$')  # 句點/驚嘆/問號，允許結尾引號/括號
    is_bullet = lambda ln: ln.startswith("- ")

    merged = []
    buf = ""

    for ln in lines:
        if not buf:
            buf = ln
            continue

        # 若上一行不是句尾，且目前行不是項目符號，就併到同一句
        if (not sentence_end.search(buf)) and (not is_bullet(ln)):
            buf = f"{buf} {ln}".strip()
        else:
            merged.append(buf)
            buf = ln

    if buf:
        merged.append(buf)

    # 移除可能殘留的空行（保守）
    merged = [m for m in merged if m.strip()]

    return "\n".join(merged)


if __name__ == "__main__":
    nbme_file_path = os.path.join(SOURCE_DIR, 'NBME_Item Writing Guide.pdf')
    dest_dir = os.path.join(DEST_DIR, 'nbme')
    mkdir(dest_dir)
    
    doc = fitz.open(nbme_file_path)
    for page in doc:
        page_number = page.number + 1
        if page_number < page_begin:
            continue
        elif page_number > page_end:
            break

        text = page.get_text()
        text = pdf_cleaner(text)
        save_file_path = os.path.join(dest_dir, f"{page_number}.txt")
        txt_dump(save_file_path, text)

