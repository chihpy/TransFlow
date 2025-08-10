"""
"""
import os
import json

def mkdir(dir):
    if os.path.isdir(dir):
        print(f"Directory '{dir}' already exists.")
    else:
        os.makedirs(dir)
        print(f"Directory '{dir}' created successfully.")

def txt_dump(file_path, data):
    print("write result to: " + file_path)
    with open(file_path, 'w') as f:
        f.write(data)

def txt_read(file_path):
    print("read file: " + file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        txt = f.read()
    return txt

def json_load(file_path):
    print("load data from: " + file_path)
    with open(file_path, 'r') as f:
        data_dict = json.load(f)
    return data_dict

def json_dump(file_path, data):
    """
    Dumps a dictionary to a JSON file.
    
    Parameters:
    - data (dict): The dictionary to be dumped.
    - filename (str): The path to the file where the JSON will be saved.
    """
    try:
        with open(file_path, 'w') as f:
            print("write result to: " + file_path)
            json.dump(data, f, indent=1, ensure_ascii=False)

    except Exception as e:
        print(f"Error occurred: {e}")

