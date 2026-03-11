import random

class WordGenerator:
    def __init__(self, phonology_config):
        self.config = phonology_config
        self.consonants = phonology_config.get('inventory_consonants', [])
        self.vowels = phonology_config.get('inventory_vowels', [])
        self.categories = phonology_config.get('categories', {})
        self.weights = phonology_config.get('weights', {})
        
        # 取得權重字典，若無則給空字典
        c_weight_map = self.weights.get('consonants', {}) or self.weights.get('consonant', {}) or {}
        v_weight_map = self.weights.get('vowels', {}) or self.weights.get('vowel', {}) or {}

        # 預先準備權重列表
        self.c_weights = [int(c_weight_map.get(c, 10)) for c in self.consonants]
        self.v_weights = [int(v_weight_map.get(v, 10)) for v in self.vowels]
        
        # 針對自定義分類處理新結構 {"symbols": [...], "comment": "..."}
        self.cat_members = {}
        self.cat_weights = {}

        for cat_name, data in self.categories.items():
            # 支援新結構 (dict) 或 舊結構 (list)
            if isinstance(data, dict):
                members = data.get('symbols', [])
            else:
                members = data # 相容舊格式
            
            self.cat_members[cat_name] = members
            
            # 抓取該分類成員對應的權重
            ws = []
            for m in members:
                # 依序找 Consonant, Vowel 權重，都沒找到給 10
                w = c_weight_map.get(m) or v_weight_map.get(m) or 10
                ws.append(int(w))
            self.cat_weights[cat_name] = ws

    def _generate_syllable(self, pattern):
        syllable = ""
        # 這裡 pattern 是單個音節模式，如 "CVC"
        for char in pattern:
            if char == 'C' and self.consonants:
                syllable += random.choices(self.consonants, weights=self.c_weights, k=1)[0]
            elif char == 'V' and self.vowels:
                syllable += random.choices(self.vowels, weights=self.v_weights, k=1)[0]
            elif char in self.cat_members:
                members = self.cat_members[char]
                ws = self.cat_weights.get(char)
                if members and ws and sum(ws) > 0:
                    syllable += random.choices(members, weights=ws, k=1)[0]
                elif members:
                    syllable += random.choice(members)
            else:
                syllable += char
        return syllable

    def generate(self, count=10, pattern="CV", min_syl=1, max_syl=3, translations=None):
        results = []
        pattern_list = pattern.split() if pattern else ["CV"]
        
        for i in range(count):
            num_syl = random.randint(min_syl, max_syl)

            word_ipa = "".join([self._generate_syllable(random.choice(pattern_list)) for _ in range(num_syl)])
            
            current_trans = ""
            if translations and i < len(translations):
                item = translations[i]
                current_trans = item.get('meaning', '') if isinstance(item, dict) else item
            
            results.append({
                "word": word_ipa,
                "translation": current_trans,
                "pos": "noun"
            })
        return results


def func(count, config, pattern, min_syl, max_syl, translations=None):
    gen = WordGenerator(config)
    return gen.generate(count, pattern, min_syl, max_syl, translations)