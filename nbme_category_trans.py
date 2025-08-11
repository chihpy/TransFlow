"""
"""
import os
from tqdm import tqdm
from utils import json_load, json_dump
from langchain_core.prompts import ChatPromptTemplate
from src.file_manager import FileManager
from src.llm_handler import LLMHandler
from src.prompt import system_prompt

source_file_path = os.path.join('data', 'nbme.json')
save_file_path = os.path.join('data', 'nbme_zh.json')

def get_message():
    prompt = ChatPromptTemplate.from_messages([
        'system', system_prompt,
        'human', 'input: {query}'
    ])
    return prompt

import hashlib

def string_to_id(s: str) -> str:
    """把字串穩定地轉成ID（SHA-256 十六進位）。"""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

if __name__ == "__main__":
    fm = FileManager(data_name='nbme', task_name='nbme_trans')
    model_provider = 'ollama'
    model_name = "gpt-oss:20b"
    json_mode = False
    llm = LLMHandler(model_provider=model_provider,
                     model_name=model_name,
                     json_mode=json_mode)
    # input prepare
    data = json_load(source_file_path)
    l2_dict = {}
    l3_dict = {}
    l4_dict = {}
    rvs = []
    prompt_template = get_message()

    for instance in tqdm(data):
        l2 = instance['l2']
        l3 = instance['l3']
        l4 = instance['l4']
        querys = [l2, l3, l4]
        l234 = []
        for query in querys:
            _id = string_to_id(query)[:8]
            if fm.cache_hit(_id):
                rv = fm.get_cache(_id)
            else:
                prompt = prompt_template.invoke({'query': query})
                response = llm.invoke(prompt)
                rv = {
                    'id': _id,
                    'zh': response,
                    'en': query
                }
                fm.save_cache(_id, rv)
            l234.append(rv)
        l2_dict[f"{l234[0]['en']}"] = l234[0]['zh']
        l3_dict[f"{l234[1]['en']}"] = l234[1]['zh']
        l4_dict[f"{l234[2]['en']}"] = l234[2]['zh']
        rvs.append({
            'l2': l234[0]['zh'],
            'l3': l234[1]['zh'],
            'l4': l234[2]['zh']
        })
    json_dump(save_file_path, rvs)
    json_dump('data/l2map.json', l2_dict)
    json_dump('data/l3map.json', l3_dict)
    json_dump('data/l4map.json', l4_dict)

        




