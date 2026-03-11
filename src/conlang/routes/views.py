import os, json
from flask import Blueprint, render_template, request, redirect, url_for, session
import conlang.paths as paths
from conlang.utils import utils

views_bp = Blueprint('views', __name__)

# --- 1. 專案管理 ---
@views_bp.route('/', methods=['GET', 'POST'])
def portal():
    if request.method == 'POST':
        project_name = request.form.get('project_name', '').strip()
        if project_name:
            paths.get_project_dir(project_name)
            session['current_project'] = project_name
            return redirect(url_for('views.portal'))
    all_projects = [d for d in os.listdir(paths.PROJECTS_ROOT) 
                    if os.path.isdir(os.path.join(paths.PROJECTS_ROOT, d))] if os.path.exists(paths.PROJECTS_ROOT) else []
    return render_template('portal.html', projects=all_projects, current=session.get('current_project'))

@views_bp.route('/select_project/<name>')
def select_project(name):
    session['current_project'] = name
    return redirect(url_for('views.portal'))

# --- 2. 核心編輯器 (IPA, Syntax, Morphology) ---
@views_bp.route('/ipa', methods=['GET', 'POST'])
def ipa_tool():
    config, config_file = utils.get_config()
    ipa_data = utils.load_yaml(paths.IPA_FILE)
    if request.method == 'POST':
        if request.form.get('action_type') == 'reset_ipa':
            config.pop('phonology', None)
        else:
            phon = config.setdefault('phonology', {})
            phon['inventory_consonants'] = sorted(list(set(request.form.getlist('ipa_consonant'))))
            phon['inventory_vowels'] = sorted(list(set(request.form.getlist('ipa_vowel'))))
            phon['inventory'] = phon['inventory_consonants'] + phon['inventory_vowels']
        utils.save_yaml(config_file, config)
        return redirect(url_for('views.ipa_tool')) 
    return render_template('ipa.html', ipa=ipa_data, config=config)

@views_bp.route('/ipa_management', methods=['GET', 'POST'])
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
        return redirect(url_for('views.ipa_management'))
    return render_template('ipa_management.html', config=config, ipa=utils.load_yaml(paths.IPA_FILE))

@views_bp.route('/syntax', methods=['GET', 'POST'])
def syntax():
    config, config_file = utils.get_config()
    master = utils.load_yaml(paths.MASTER_FILE)
    if request.method == 'POST':
        if request.form.get('action_type') == 'reset':
            utils.save_yaml(config_file, {'phonology': config.get('phonology', {})})
            return redirect(url_for('views.syntax'))
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
        return redirect(url_for('views.syntax'))
    return render_template('syntax.html', master=master, config=config)

@views_bp.route('/morphology', methods=['GET', 'POST'])
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
        return redirect(url_for('views.morphology_mgr'))
    return render_template('morphology.html', config=config)

# --- 3. 字典與詞庫 ---
@views_bp.route('/lexicon')
def lexicon():
    config, _ = utils.get_config()
    return render_template('lexicon.html', config=config)

@views_bp.route('/dictionary')
def view_dictionary():
    lex_data, _ = utils.get_lexicon()
    return render_template('dictionary.html', dictionary=lex_data.get('words', []))