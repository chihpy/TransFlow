"""
"""
import os
from tqdm import tqdm
from langchain_core.prompts import ChatPromptTemplate

from src.llm_handler import LLMHandler
from src.file_manager import FileManager
from utils import mkdir, json_dump

SYS_PROMPT = (
    "你是一個專業的醫療內容翻譯者，負責將英文的 USMLE Content Outline 翻譯為 台灣用語下的繁體中文\n"
    "根據輸入的 Content，直接輸出翻譯過後的結果，不要輸出多餘文字與符號"
)

HUMAN_PROMPT = (
    "Content: {content}\n"
)

def get_message():
    prompt = ChatPromptTemplate.from_messages([
        'system', SYS_PROMPT,
        'human', HUMAN_PROMPT
    ])
    return prompt

if __name__ == "__main__":
    model_provider = 'ollama'
#    model_name = "gpt-oss:20b"
    model_name = 'gemma3:12b'
    json_mode = False
    llm = LLMHandler(model_provider=model_provider,
                     model_name=model_name,
                     json_mode=json_mode)
    prompt_template = get_message()
    source_file_path = os.path.join('data', 'Content_Outline', 'content_temp.txt')
    fm = FileManager(data_name=os.path.basename(source_file_path), task_name='usmle_content_outline_trans')
    with open(source_file_path, 'r') as f:
        lines = f.readlines()
    line_map = []
    rvs = []
    ig_cnt = 0
    for line in tqdm(lines):
        line_lst = line.split(';')
        collect = []
        for idx, txt in enumerate(line_lst):
            query = txt.strip()

            _id = fm.query2id(query)
            if fm.cache_hit(_id):
                rv = fm.get_cache(_id)
                rv['zh'] = rv['zh'].strip()
                collect.append(rv['zh'])
            else:
                prompt = prompt_template.invoke({'content': query})
                response = llm.invoke(prompt)
                rv = {
                    'en': query,
                    'zh': response,
                }
                fm.save_cache(_id, rv)
                collect.append(response)
        newline = '; '.join(collect)

        line_map.append((newline, line.strip()))
        rvs.append(newline)
    txt = '\n'.join(rvs)
    with open('content_zh.txt', 'w') as f:
        f.write(txt)
    json_dump('content_map.json', line_map)