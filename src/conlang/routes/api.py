import json
from flask import Blueprint, request, jsonify
from conlang.lexicon import generator
from conlang.utils import utils

api_bp = Blueprint('api', __name__, url_prefix='/api')

def _update_lexicon(callback):
    try:
        lex_data, lex_file = utils.get_lexicon()
        if 'words' not in lex_data: lex_data['words'] = []
        callback(lex_data['words'], request.json)
        utils.save_yaml(lex_file, lex_data)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

# --- 音系 (Phonology) API ---
@api_bp.route('/save_phonology', methods=['POST'])
def save_phonology():
    data = request.get_json()
    config, path = utils.get_config()
    phon = config.setdefault('phonology', {})
    phon['inventory_consonants'] = data.get('inventory_consonants', [])
    phon['inventory_vowels'] = data.get('inventory_vowels', [])
    phon['inventory'] = phon['inventory_consonants'] + phon['inventory_vowels']
    phon['categories'] = data.get('categories', {})
    utils.save_yaml(path, config) 
    return jsonify({"success": True})

# --- 單字生成 API ---
@api_bp.route('/generate_words', methods=['POST'])
def api_generate_words():
    try:
        data = request.get_json()
        if not data: return jsonify({"status": "error", "message": "No data"}), 400
        swadesh = data.get('swadesh_list', [])
        config, _ = utils.get_config()
        try:
            target_count = int(data.get('count', 20))
            min_syl = int(data.get('min_syl', 1))
            max_syl = int(data.get('max_syl', 3))
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid number format"}), 400

        generated = generator.func(
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

# --- 字典 CRUD API ---
@api_bp.route('/dictionary/add', methods=['POST'])
def api_add_entry():
    return _update_lexicon(lambda words, data: words.insert(0, {
        'word': data['word'], 
        'pos': data['pos'], 
        'translation': data['translation'],
        'ipa': data['ipa'], 
        'syllables': data['ipa'].split('.') if data.get('ipa') else [],
        'notes': data.get('notes', '')
    }))

@api_bp.route('/dictionary/update', methods=['POST'])
def api_update_entry():
    def update_logic(words, data):
        index = data.get('index')
        if index is not None and 0 <= index < len(words):
            words[index] = {
                'word': data['word'], 
                'pos': data['pos'], 
                'translation': data['translation'],
                'ipa': data['ipa'], 
                'syllables': data['ipa'].split('.') if data.get('ipa') else [],
                'notes': data.get('notes', '')
            }
        else: raise ValueError("Invalid index")
    return _update_lexicon(update_logic)

@api_bp.route('/dictionary/delete', methods=['POST'])
def api_delete_entry():
    return _update_lexicon(lambda words, data: words.pop(data.get('index')) if 0 <= data.get('index') < len(words) else None)