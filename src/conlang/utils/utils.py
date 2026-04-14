import os
import yaml
from flask import session
import conlang.paths as paths

def load_yaml(path):
    """安全載入 YAML 檔案"""
    if not path or not os.path.exists(path): 
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return yaml.safe_load(f) or {}
        except yaml.YAMLError:
            return {}

def save_yaml(path, data):
    """
    安全儲存 YAML，確保路徑合法且自動建立資料夾。
    防止 Windows Console 寫入錯誤。
    """
    if not path or not isinstance(path, str):
        return

    try:
        abs_path = os.path.abspath(path)
        folder = os.path.dirname(abs_path)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(abs_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    except Exception as e:
        print(f"DEBUG: save_yaml 發生錯誤: {e}")

def get_current_project_file(filename):
    """
    獲取專案檔案路徑。
    如果檔案不存在，則建立一個完全空的 {} YAML 檔案。
    """
    p_name = session.get('current_project')
    if not p_name:
        return ""
        
    project_dir = paths.get_project_dir(p_name)
    target_path = os.path.join(project_dir, filename)
    
    # 如果專案目錄下沒這個檔案，就初始化一個空的 YAML
    if not os.path.exists(target_path):
        save_yaml(target_path, {})
        
    return target_path

def get_config():
    """
    獲取專案 config.yaml。
    回傳 (data, path)
    """
    # 移除原本報錯的 seed_template 參數
    path = get_current_project_file('config.yaml')
    
    if not path:
        return {}, ""
        
    data = load_yaml(path)
    return data, path

def save_config(data):
    """儲存 config.yaml"""
    path = get_current_project_file('config.yaml')
    save_yaml(path, data)

def get_lexicon():
    """獲取詞典資料 dict.yaml"""
    path = get_current_project_file('dict.yaml')
    return load_yaml(path), path

def load_ipa_data():
    """載入系統唯讀的 IPA 資料"""
    # 這裡依然使用 paths.DEFAULT_IPA，它是系統路徑，不是專案路徑
    return load_yaml(paths.DEFAULT_IPA)