import os

# 這是 C:\dev\lang\src\conlang
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

# 這是 C:\dev\lang\src
SRC_ROOT = os.path.abspath(os.path.join(PACKAGE_DIR, ".."))

# 這是 C:\dev\lang
LANG_ROOT = os.path.abspath(os.path.join(SRC_ROOT, ".."))

# 專案目錄 C:\dev\lang\projects
PROJECTS_ROOT = os.path.join(LANG_ROOT, 'projects')

# 系統檔案 - 強制指向 src 目錄
IPA_FILE = os.path.join(PACKAGE_DIR, 'ipa.yaml')
MASTER_FILE = os.path.join(PACKAGE_DIR, 'master.yaml')

def get_project_dir(project_name):
    path = os.path.join(PROJECTS_ROOT, project_name or '_default_')
    os.makedirs(path, exist_ok=True)
    return path

def get_project_file(project_name, filename):
    return os.path.join(get_project_dir(project_name), filename)