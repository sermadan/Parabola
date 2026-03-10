import os, json
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import conlang.paths as paths
from conlang.lexicon import generator
from conlang.utils import utils

app = Flask(__name__)
app.secret_key = "conlanger_secret_key"

# 確保專案根目錄存在 (C:\dev\lang\projects)
os.makedirs(paths.PROJECTS_ROOT, exist_ok=True)

@app.context_processor
def inject_globals():
    return {
        'app_name': 'Gugugaga',
        'current_project': session.get('current_project', 'None')
    }

# ==========================================
# 1. 專案管理
# ==========================================

@app.route('/', methods=['GET', 'POST'])
def portal():
    if request.method == 'POST':
        project_name = request.form.get('project_name', '').strip()
        if project_name:
            # 透過 paths 確保目錄建立
            paths.get_project_dir(project_name)
            session['current_project'] = project_name
            return redirect(url_for('portal'))

    all_projects = [d for d in os.listdir(paths.PROJECTS_ROOT) 
                    if os.path.isdir(os.path.join(paths.PROJECTS_ROOT, d))] if os.path.exists(paths.PROJECTS_ROOT) else []
    return render_template('portal.html', projects=all_projects, current=session.get('current_project'))

@app.route('/select_project/<name>')
def select_project(name):
    session['current_project'] = name
    return redirect(url_for('portal'))

# ==========================================
# 2. 核心編輯器 (IPA, Syntax, Morphology)
# ==========================================

@app.route('/ipa', methods=['GET', 'POST'])
def ipa_tool():
    config, config_file = utils.get_config()
    ipa_data = utils.load_yaml(paths.IPA_FILE) # 來自 C:\dev\lang\src\ipa.yaml

    if request.method == 'POST':
        if request.form.get('action_type') == 'reset_ipa':
            config.pop('phonology', None)
        else:
            phon = config.setdefault('phonology', {})
            phon['inventory_consonants'] = sorted(list(set(request.form.getlist('ipa_consonant'))))
            phon['inventory_vowels'] = sorted(list(set(request.form.getlist('ipa_vowel'))))
            phon['inventory'] = phon['inventory_consonants'] + phon['inventory_vowels']
        
        utils.save_yaml(config_file, config)
        return redirect(url_for('ipa_tool')) 

    return render_template('ipa.html', ipa=ipa_data, config=config)

@app.route('/api/save_phonology', methods=['POST'])
def save_phonology():
    data = request.get_json()
    config, path = utils.get_config()
    
    # 更新 Inventory
    config['phonology']['inventory_consonants'] = data.get('inventory_consonants', [])
    config['phonology']['inventory_vowels'] = data.get('inventory_vowels', [])
    
    # 重點：更新自定義分類，這樣 Generator 讀取時就是最新的
    config['phonology']['categories'] = data.get('categories', {})
    
    utils.save_config(config) # 寫回 yaml
    return jsonify({"success": True})

@app.route('/ipa_management', methods=['GET', 'POST'])
def ipa_management():
    config, config_file = utils.get_config()
    if request.method == 'POST':
        phon = config.setdefault('phonology', {})
        weights = {'consonants': {}, 'vowels': {}}
        c_list = phon.get('inventory_consonants', [])
        v_list = phon.get('inventory_vowels', [])

        for key, value in request.form.items():
            if key.startswith('weight_'):
                p = key.replace('weight_', '')
                val = int(value or 10)
                if p in c_list: weights['consonants'][p] = val
                elif p in v_list: weights['vowels'][p] = val

        phon.update({
            'weights': weights,
            'custom_order': request.form.get('custom_order_data', ""),
            'categories': json.loads(request.form.get('custom_categories_json', '{}'))
        })
        
        utils.save_yaml(config_file, config)
        return redirect(url_for('ipa_management'))
    
    return render_template('ipa_management.html', config=config, ipa=utils.load_yaml(paths.IPA_FILE))

@app.route('/syntax', methods=['GET', 'POST'])
def syntax():
    config, config_file = utils.get_config()
    master = utils.load_yaml(paths.MASTER_FILE)
    
    if request.method == 'POST':
        if request.form.get('action_type') == 'reset':
            utils.save_yaml(config_file, {'phonology': config.get('phonology', {})})
            return redirect(url_for('syntax'))

        new_config = config.copy()
        for key in list(new_config.keys()):
            if key.startswith('sec_'): del new_config[key]

        for raw_key, values in request.form.lists():
            if '|' not in raw_key or raw_key.startswith('order|') or raw_key == 'action_type': continue
            parts = raw_key.split('|')
            vals = [v.strip() for v in values if v.strip()]
            if not vals: continue
            if parts[0] == 'bools':
                new_config.setdefault(parts[1], {}).setdefault('bools', {})[parts[2]] = True
            elif parts[0] == 'settings':
                new_config.setdefault(parts[1], {}).setdefault('settings', {})[parts[2]] = vals
            elif len(parts) == 2:
                new_config.setdefault(parts[0], {})[parts[1]] = vals

        for raw_key in request.form.keys():
            if not raw_key.startswith('order|'): continue
            sorted_list = request.form.get(raw_key).split()
            p = raw_key.replace('order|', '').split('|')
            if p[0] == 'settings' and len(p) == 3:
                sec, feat = p[1], p[2]
                if sec in new_config and 'settings' in new_config[sec] and feat in new_config[sec]['settings']:
                    curr = new_config[sec]['settings'][feat]
                    new_config[sec]['settings'][feat] = [x for x in sorted_list if x in curr]
            elif len(p) == 2:
                sec, cat = p[0], p[1]
                if sec in new_config and cat in new_config[sec]:
                    curr = new_config[sec][cat]
                    if isinstance(curr, list):
                        new_config[sec][cat] = [x for x in sorted_list if x in curr]

        utils.save_yaml(config_file, new_config)
        return redirect(url_for('syntax'))
    
    return render_template('syntax.html', master=master, config=config)

@app.route('/morphology', methods=['GET', 'POST'])
def morphology_mgr():
    config, config_file = utils.get_config()
    if request.method == 'POST':
        new_morphology = {}
        for key, values in request.form.lists():
            if key.startswith('dims|'):
                section = key.split('|')[1].replace('[]', '')
                dims = [v.strip() for v in values if v.strip()]
                if dims: new_morphology.setdefault(section, {})['selected_matrix_dims'] = dims
        for key in request.form:
            if key.startswith('matrix|') and '|content[]' in key:
                parts = key.split('|')
                if len(parts) < 4: continue
                section, combo_key = parts[1], parts[2]
                contents = request.form.getlist(key)
                pairs = [{'marker': c.strip()} for c in contents if c.strip()]
                if pairs: new_morphology.setdefault(section, {}).setdefault('markers', {})[combo_key] = pairs
        config['morphology'] = new_morphology
        utils.save_yaml(config_file, config)
        return redirect(url_for('morphology_mgr'))
    return render_template('morphology.html', config=config)

# ==========================================
# 3. 字典與詞庫 (Lexicon & Dictionary)
# ==========================================

@app.route('/lexicon')
def lexicon():
    config, _ = utils.get_config()
    return render_template('lexicon.html', config=config)

@app.route('/dictionary')
def view_dictionary():
    lex_data, _ = utils.get_lexicon()
    return render_template('dictionary.html', dictionary=lex_data.get('words', []))

def _update_lexicon(callback):
    try:
        lex_data, lex_file = utils.get_lexicon()
        if 'words' not in lex_data: lex_data['words'] = []
        callback(lex_data['words'], request.json)
        utils.save_yaml(lex_file, lex_data)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route('/dictionary/api/add', methods=['POST'])
def api_add_entry():
    return _update_lexicon(lambda words, data: words.insert(0, {
        'word': data['word'], 'pos': data['pos'], 'translation': data['translation'],
        'ipa': data['ipa'], 'syllables': data['ipa'].split('.') if data.get('ipa') else []
    }))

@app.route('/dictionary/api/update', methods=['POST'])
def api_update_entry():
    def update_logic(words, data):
        index = data.get('index')
        if index is not None and 0 <= index < len(words):
            words[index] = {
                'word': data['word'], 'pos': data['pos'], 'translation': data['translation'],
                'ipa': data['ipa'], 'syllables': data['ipa'].split('.') if data.get('ipa') else []
            }
        else: raise ValueError("Invalid index")
    return _update_lexicon(update_logic)

@app.route('/dictionary/api/delete', methods=['POST'])
def api_delete_entry():
    return _update_lexicon(lambda words, data: words.pop(data.get('index')) if 0 <= data.get('index') < len(words) else None)

# ==========================================
# 4. 生成器 API
# ==========================================

@app.route('/api/generate_words', methods=['POST'])
def api_generate_words():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        swadesh = data.get('swadesh_list', [])
        config, _ = utils.get_config()
        
        # 確保從前端拿到的數字都是 int，避免傳入 generator 時出錯
        try:
            target_count = int(data.get('count', 20))
            min_syl = int(data.get('min_syl', 1))
            max_syl = int(data.get('max_syl', 3))
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid number format"}), 400

        generated = generator.func(
            # 如果有提供清單，則生成清單長度的單字；否則依照 count 數量
            count=len(swadesh) if swadesh else target_count,
            config=config.get('phonology', {}),
            pattern=data.get('pattern', 'CV'),
            min_syl=min_syl,
            max_syl=max_syl,
            translations=swadesh
        )
        
        return jsonify({"status": "success", "words": generated})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)