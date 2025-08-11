"""
"""
import os
import json

def json_load(file_path):
    with open(file_path, 'r') as f:
        data_dict = json.load(f)
    return data_dict

def json_dump(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    print(f"Data successfully written to {file_path}")
    
class FileManager:
    def __init__(self,
                 data_name,
                 task_name,
                 cache_base_dir: str = "data/cache",
                 output_base_dir: str = 'data/outputs'
                 ):
        self.data_name = os.path.splitext(data_name)[0]
        self.cache_dir = os.path.join(cache_base_dir, task_name, self.data_name)
        os.makedirs(self.cache_dir, exist_ok=True)
        self.output_dir = os.path.join(output_base_dir, task_name)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def cache_hit(self, _id):
        id_names = os.listdir(self.cache_dir)
        ids = [name.split('.')[0] for name in id_names]
        if _id in ids:
            return True
        else:
            return False
    
    def get_cache(self, _id):
        cache_file_path = os.path.join(self.cache_dir, f"{_id}.json")
        data = json_load(cache_file_path)
        return data
    
    def save_cache(self, _id, rv):
        cache_file_path = os.path.join(self.cache_dir, f"{_id}.json")
        json_dump(cache_file_path, rv)
    
    def save_output(self, rvs):
        save_file_path = os.path.join(self.output_dir, self.data_name + '.json')
        json_dump(save_file_path, rvs)

