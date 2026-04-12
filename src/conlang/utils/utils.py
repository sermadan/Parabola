import os
import yaml
import shutil
from flask import session
import conlang.paths as paths

def load_yaml(path):
    if not os.path.exists(path): 
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return yaml.safe_load(f) or {}
        except yaml.YAMLError:
            return {}

def save_yaml(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

def get_current_project_file(filename, seed_template=None, auto_copy=True):
    """
    獲取檔案路徑。
    auto_copy: 如果為 False，則不執行 shutil.copy
    """
    p_name = session.get('current_project')
    if not p_name:
        return seed_template if seed_template else ""
        
    project_dir = paths.get_project_dir(p_name)
    target_path = os.path.join(project_dir, filename)
    
    # 只有當檔案不存在、有提供範本、且 auto_copy 為 True 時才拷貝
    if not os.path.exists(target_path) and seed_template and os.path.exists(seed_template):
        if auto_copy:
            shutil.copy(seed_template, target_path)
        else:
            # 不拷貝，直接返回路徑，讓外層知道檔案目前還不存在
            return target_path
            
    return target_path

def get_config():
    # 這裡加入 auto_copy=False
    config_path = get_current_project_file('config.yaml', seed_template=paths.DEFAULT_MASTER, auto_copy=False)
    
    # 真正檢查硬碟檔案是否存在
    if not os.path.exists(config_path):
        # 檔案不存在，回傳空字典（或只含基本結構），並標記為 False
        return {}, False
        
    # 檔案存在，正常載入
    data = load_yaml(config_path)
    return data, True

def save_config(data):
    path = get_current_project_file('config.yaml', seed_template=paths.DEFAULT_MASTER)
    save_yaml(path, data)

def get_lexicon():
    """獲取詞典資料"""
    path = get_current_project_file('dict.yaml')
    return load_yaml(path), path

def load_ipa_data():
    """IPA 資料通常是唯讀的系統資料"""
    return load_yaml(paths.DEFAULT_IPA)