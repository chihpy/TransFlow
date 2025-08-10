"""
"""
import os
import re
import fitz

from utils import mkdir, txt_dump

SOURCE_DIR = os.path.join('data', 'source')
DEST_DIR = os.path.join('data', 'parsed_txt')
mkdir(DEST_DIR)

page_begin = -1
page_end = -1
import re
from typing import List

# === 規則定義 ===
SENTENCE_END = re.compile(r'[。．…\.!?！？](?:["”’)\]」】》]+)?$')  # 句末 + 可選結尾引號/括號
BULLET_LIKE  = re.compile(r'^(\- |\* |• |\d+[\.\)] |[A-Za-z][\.\)] )')  # 常見清單開頭
PAGE_LIKE    = re.compile(
    r'^\s*\d+\s*\|\s*P\s+a\s+g\s+e\s*$'                                   # 2 | P a g e
    r'|^(?:Page|PAGE|p\.|P\.)\s*\d+(?:\s*/\s*\d+|\s+of\s+\d+)?$'          # Page 2, p. 3 of 10
    r'|^第?\s*\d+\s*頁$'                                                  # 第 3 頁 / 3 頁
    r'|^-\s*\d+\s*-$'                                                     # - 3 -
)
CODE_OR_TABLEY = re.compile(r'[`|]{2,}|^-{3,}$|^\+{2,}$')  # 表格/程式碼痕跡（粗略）
SECTION_HEAD   = re.compile(r'^(Section\s+\d+\s*:\s*[^\n]+)', re.IGNORECASE)
INTRO_HEAD     = re.compile(r'^(Introduction)\b', re.IGNORECASE)

def looks_like_heading(line: str) -> bool:
    """短、無句末標點，或冒號結尾、或像標題格式（全大寫/Title Case）"""
    s = line.strip()
    if len(s) <= 40 and not SENTENCE_END.search(s):
        if s.endswith((':', '：')):
            return True
        letters = re.sub(r'[^A-Za-z]', '', s)
        if letters and (letters.isupper() or s.istitle()):
            return True
    return False

def looks_structural(line: str) -> bool:
    s = line.strip()
    return (
        bool(BULLET_LIKE.match(s)) or
        bool(PAGE_LIKE.match(s)) or
        bool(CODE_OR_TABLEY.search(s)) or
        looks_like_heading(s)
    )

def split_heading_inline(line: str) -> List[str]:
    """把『標題+正文黏在同一行』拆開成兩行（若有）"""
    s = line.strip()

    m = SECTION_HEAD.match(s)
    if m:
        head = m.group(1).strip()
        rest = s[len(head):].strip()
        return [head] + ([rest] if rest else [])

    m = INTRO_HEAD.match(s)
    if m:
        head = m.group(1).strip()
        rest = s[len(head):].strip()
        if rest:
            return [head, rest]

    # 泛用啟發式：短前導詞 + 大寫開頭正文
    m = re.match(r'^([A-Z][A-Za-z ]{0,30})(?=\s+[A-Z])\s+(.+)$', s)
    if m:
        head, body = m.groups()
        if len(head) <= 30 and not SENTENCE_END.search(head):
            return [head.strip(), body.strip()]

    return [s]

def soft_join(a: str, b: str) -> str:
    """中英混排時，只在兩側都是 ASCII 字母/數字時補空格"""
    if a and b and a[-1].isascii() and b[0].isascii():
        return (a + ' ' + b).strip()
    return (a + b).strip()

def clean_layout(text: str, merge_broken_lines: bool = False) -> str:
    """
    PDF→文字常見清理：
      1) 換行正規化、刪空行
      2) 剔除頁碼/頁眉
      3) 把『標題+正文』拆成兩行
      4) （可選）保守合併被硬切的句子

    :param text: 原始文字
    :param merge_broken_lines: 是否合併被硬切的行（預設 False）
    """
    # 1) 換行正規化
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2) 初步切行＋過濾空行與頁碼
    prelim = []
    for raw in text.split("\n"):
        s = raw.strip()
        if not s:
            continue
        if PAGE_LIKE.match(s):
            continue
        # 3) 拆『標題+正文』
        pieces = split_heading_inline(s)
        prelim.extend(pieces)

    if not prelim:
        return ""

    if not merge_broken_lines:
        # 只做結構清理，不合併句子
        return "\n".join(prelim)

    # 4) 保守合併：前一行不是句末且下一行不像結構行才合併
    merged = []
    buf = ""
    for ln in prelim:
        if not buf:
            buf = ln
            continue

        prev_is_end = bool(SENTENCE_END.search(buf))
        next_is_struct = looks_structural(ln)

        if (not prev_is_end) and (not next_is_struct):
            buf = soft_join(buf, ln)
        else:
            merged.append(buf)
            buf = ln

    if buf:
        merged.append(buf)

    # 收尾：保守去除空白行（理應不會有）
    merged = [m for m in merged if m.strip()]
    return "\n".join(merged)



if __name__ == "__main__":
    pncb_file_path = os.path.join(SOURCE_DIR, 'PNCB_Item_Writing_Manual.pdf')
    dest_dir = os.path.join(DEST_DIR, 'pncb_all')
    mkdir(dest_dir)
    
    doc = fitz.open(pncb_file_path)
    for page in doc:
        page_number = page.number + 1

        text = page.get_text()
        text = clean_layout(text, merge_broken_lines=True)
        save_file_path = os.path.join(dest_dir, f"{page_number}.txt")
        txt_dump(save_file_path, text)

