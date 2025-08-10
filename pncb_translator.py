"""
"""
import os
import time
import json
from tqdm import tqdm

from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from utils import mkdir, json_dump

MODEL_NAME = "llama3.1:8b"
#MODEL_NAME = "gemma3:12b"
#MODEL_NAME = "gpt-oss:20b"
MODEL_DISP_NAME = MODEL_NAME.split(':')[0]
SOURCE_DIR = os.path.join('data', 'parsed_txt', 'pncb_all')
DEST_DIR = os.path.join('data', 'outputs', 'trans', f'pncb_{MODEL_DISP_NAME}')
mkdir(DEST_DIR)
STAT_DIR = os.path.join('data', 'stat')
mkdir(STAT_DIR)

TEMPERATURE = 0.0

system_prompt_template = PromptTemplate(
    input_variables=[],
    template=(
        "You are a professional bilingual translator. "
        "Translate user-provided English sentences into **Traditional Chinese**. "
        "Keep the meaning accurate, natural, and concise. "
        "Do not add commentary, notes, explanations, or quotes; output only the translation. "
        "Preserve numerals and named entities. If the input line is blank, output a blank line."
    ),
)

# 使用者輸入提示（需要填變數的部分）
user_prompt_template = PromptTemplate(
    input_variables=["line"],
    template="Translate the following English sentence into Traditional Chinese (output only the translation):\n{line}"
)

def build_chat(model_name: str, temperature: float) -> ChatOllama:
    return ChatOllama(model=model_name, temperature=temperature)

def get_messages(var):
    messages = [
        SystemMessage(content=system_prompt_template.format()),
        HumanMessage(content=user_prompt_template.format(**var))
    ]
    return messages

if __name__ == "__main__":
    # Initialize model
    chat = build_chat(model_name=MODEL_NAME, temperature=TEMPERATURE)
    file_names = os.listdir(SOURCE_DIR)
    file_names = ['21.txt', '22.txt']
    stat_file_path = os.path.join(STAT_DIR, f'pncb_question_stat_{MODEL_DISP_NAME}.jsonl')
    for idx, file_name in enumerate(file_names):
#        if idx == 5:
#            break
        print("---" * 3 + f"{idx}" + "---"*3)
        file_path = os.path.join(SOURCE_DIR, file_name)
        with open(file_path, 'r') as f:
            lines = f.readlines()
        num_lines = len(lines)
        rv = []
        line_index = 0
        for line in tqdm(lines):
            messages = get_messages({
                'line': line
            })
            ###
            t0 = time.perf_counter()
            response = chat.invoke(messages)
            t1 = time.perf_counter()
            rv.append((response.content, line))

            md = getattr(response, "response_metadata", {}) or {}
            in_tok   = int(md.get("prompt_eval_count") or md.get("input_tokens") or 0)
            out_tok  = int(md.get("eval_count") or md.get("output_tokens") or 0)
            dur_ns   = int(md.get("total_duration") or (md.get("prompt_eval_duration", 0) + md.get("eval_duration", 0)) or 0)
            model_time_s = dur_ns / 1e9 if dur_ns else 0.0
            wall_time_s  = t1 - t0
            out_per_s_model = (out_tok / model_time_s) if model_time_s > 0 and out_tok > 0 else 0.0
            out_per_s_wall  = (out_tok / wall_time_s) if wall_time_s > 0 and out_tok > 0 else 0.0

            stat = {
                "page": idx,
                'line_idx': line_index,
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "model_time_s": round(model_time_s, 6),
                "wall_time_s": round(wall_time_s, 6),
                "out_tokens_per_s_model": round(out_per_s_model, 3),
                "out_tokens_per_s_wall": round(out_per_s_wall, 3),
            }
            with open(stat_file_path, 'a', encoding='utf-8') as fw:
                fw.write(json.dumps(stat, ensure_ascii=False) + "\n")

            line_index += 1

        base_name, _ = os.path.splitext(file_name)
        save_file_path = os.path.join(DEST_DIR, base_name + '.json')
        json_dump(save_file_path, rv)

    
