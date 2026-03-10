import os, yaml
from flask import session
import conlang.paths as paths

def load_yaml(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def save_yaml(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

def get_current_project_file(filename):
    """獲取當前選定專案路徑下的檔案，並確保目錄存在"""
    p_name = session.get('current_project', '_default_')
    project_dir = paths.get_project_dir(p_name)
    return os.path.join(project_dir, filename)

def get_config():
    """標準化獲取 config.yaml 資料與檔案路徑"""
    path = get_current_project_file('config.yaml')
    return load_yaml(path), path

def save_config(data):
    """直接儲存目前的 config 資料"""
    path = get_current_project_file('config.yaml')
    save_yaml(path, data)

def get_lexicon():
    """標準化獲取 dict.yaml 資料與檔案路徑"""
    path = get_current_project_file('dict.yaml')
    return load_yaml(path), path