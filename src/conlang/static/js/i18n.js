// ===============================
// i18n.js  (Flask + CSV version)
// ===============================

let i18nData = {};     // 原始分類結構
let i18nFlat = {};     // 扁平快取 (key -> {zh, en, uk, ...})
let currentLang = 'zh';
let isTranslating = false;


// ===============================
// 1️⃣  載入 CSV
// ===============================
async function loadTranslations() {
    try {
        const response = await fetch(
            window.TRANSLATION_URL + "?t=" + new Date().getTime()
        );
        if (!response.ok) throw new Error("Fetch failed");

        const text = await response.text();
        parseCSV(text);

        applyTranslations();
        observeDOM();

        console.log("✅ i18n loaded");

    } catch (err) {
        console.error("❌ i18n load error:", err);
    }
}


// ===============================
// 2️⃣  解析 CSV (自動解析 Header 與多語系欄位)
// ===============================
function parseCSV(data) {
    const cleanData = data.replace(/^\uFEFF/, '');
    const rows = parseCSVRows(cleanData);

    if (rows.length < 2) return;

    // 自動抓取第一列 Header: ["category", "key", "en", "zh", "uk", ...]
    const headers = rows[0].map(h => h.trim().toLowerCase().replace(/^"|"$/g, ''));
    
    // 相容 "category" 與 "cat"
    const catIdx = headers.findIndex(h => h === 'category' || h === 'cat');
    const keyIdx = headers.indexOf('key');

    if (catIdx === -1 || keyIdx === -1) {
        console.error("❌ CSV 格式錯誤：必須包含 'category' (或 'cat') 與 'key' 欄位");
        return;
    }

    i18nData = {};
    i18nFlat = {};

    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        
        // 過濾全空行
        if (!row || row.length === 0 || row.every(cell => !cell.trim())) continue;

        const category = row[catIdx] ? row[catIdx].trim() : '';
        const key = row[keyIdx] ? row[keyIdx].trim() : '';

        if (!key) continue;

        const langMap = {};
        headers.forEach((header, idx) => {
            if (idx !== catIdx && idx !== keyIdx && row[idx] !== undefined) {
                langMap[header] = row[idx];
            }
        });

        // 建立分類結構與扁平快取
        if (!i18nData[category]) i18nData[category] = {};
        i18nData[category][key] = langMap;
        i18nFlat[key] = langMap;
    }
}

// 標準 CSV 解析器（支援逗號、引號、空行與換行）
function parseCSVRows(text) {
    const result = [];
    let row = [];
    let field = '';
    let inQuotes = false;

    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        const nextChar = text[i + 1];

        if (char === '"') {
            if (inQuotes && nextChar === '"') {
                field += '"';
                i++;
            } else {
                inQuotes = !inQuotes;
            }
        } else if (char === ',' && !inQuotes) {
            row.push(field);
            field = '';
        } else if ((char === '\r' || char === '\n') && !inQuotes) {
            if (char === '\r' && nextChar === '\n') i++;
            row.push(field);
            result.push(row);
            row = [];
            field = '';
        } else {
            field += char;
        }
    }
    if (field || row.length > 0) {
        row.push(field);
        result.push(row);
    }
    return result;
}


// ===============================
// 3️⃣  核心翻譯函式 (JS 用)
// ===============================
function t(key, params = {}) {
    const entry = i18nFlat[key];
    if (!entry) return key;

    // 找不到該語系時，降級順序：指定語言 -> zh -> en -> key 本身
    let text = entry[currentLang] || entry['zh'] || entry['en'] || key;

    // 參數替換 {name}
    Object.keys(params).forEach(p => {
        text = text.replace(new RegExp(`{${p}}`, 'g'), params[p]);
    });

    return text;
}


// ===============================
// 4️⃣  套用到 HTML
// ===============================
function applyTranslations() {
    if (!Object.keys(i18nFlat).length) return;
    if (isTranslating) return;

    isTranslating = true;

    // 1. 文字內容套用 [data-i18n="key"]
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.dataset.i18n;
        if (!key) return;

        const translated = t(key);
        const displayText = translated !== key
            ? translated
            : generateDebugText(key);

        if (el.textContent !== displayText) {
            el.textContent = displayText;
        }

        const parentOption = el.closest('option');
        if (parentOption) {
            parentOption.text = displayText;
            parentOption.label = displayText;
        }
    });

    // 2. Placeholder 獨立套用 [data-i18n-placeholder="key"]
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (!key) return;

        const translated = t(key);
        const displayText = translated !== key ? translated : generateDebugText(key);

        if (el.placeholder !== displayText) {
            el.placeholder = displayText;
        }
    });

    setTimeout(() => {
        isTranslating = false;
    }, 50);
}


// ===============================
// 5️⃣  DOM 監聽（動態元素）
// ===============================
function observeDOM() {
    const observer = new MutationObserver((mutations) => {
        if (isTranslating) return;

        const hasNewNodes = mutations.some(m => m.addedNodes.length > 0);
        if (hasNewNodes) {
            applyTranslations();
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}


// ===============================
// 6️⃣  語言切換
// ===============================
function updateLangMode(mode) {
    currentLang = mode;
    localStorage.setItem('conlang-pref-lang', mode);

    // 更新頁面上所有引導頁（/guide）連結的 query 參數
    updateGuideLinks(mode);

    // 若當前位於 /guide 頁面，且 URL 上的 lang 參數不同，則直接刷新頁面載入對應 Markdown
    if (window.location.pathname === '/guide') {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('lang') !== mode) {
            window.location.href = `/guide?lang=${mode}`;
            return;
        }
    }

    applyTranslations();
    updateLangButtonUI(mode);
}


function updateLangButtonUI(mode) {
    document.querySelectorAll('.btn-lang').forEach(btn => {
        btn.style.background = 'transparent';
        btn.style.color = 'var(--text-sub)';
        btn.style.boxShadow = 'none';
    });

    const activeBtn = document.getElementById('btn-' + mode);
    if (activeBtn) {
        activeBtn.style.background = 'white';
        activeBtn.style.color = 'var(--primary)';
        activeBtn.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
    }
}

// 自動將所有的 /guide 連結補上語系參數
function updateGuideLinks(mode) {
    document.querySelectorAll('a[href^="/guide"]').forEach(link => {
        link.href = `/guide?lang=${mode}`;
    });
}


// ===============================
// 7️⃣  Debug 文字產生（找不到翻譯時）
// ===============================
function generateDebugText(key) {
    const cleaned = key
        .replace(/_/g, ' ')
        .replace(/-/g, ' ');
    return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
}


// ===============================
// 8️⃣  初始化
// ===============================
document.addEventListener('DOMContentLoaded', () => {
    // 優先看網址有無 ?lang= 參數，沒有才拿 localStorage，最後預設 'zh'
    const urlParams = new URLSearchParams(window.location.search);
    const langFromUrl = urlParams.get('lang');

    currentLang = langFromUrl || localStorage.getItem('conlang-pref-lang') || 'zh';
    localStorage.setItem('conlang-pref-lang', currentLang);

    updateGuideLinks(currentLang);
    updateLangButtonUI(currentLang);
    loadTranslations();
});


// ===============================
// 9️⃣  對外開放
// ===============================
window.t = t;
window.updateLangMode = updateLangMode;