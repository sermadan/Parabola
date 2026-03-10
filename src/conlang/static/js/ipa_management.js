// ==========================================
// 全域變數
// ==========================================
let weights = { consonant: {}, vowel: {} };
let inventory = { consonant: [], vowel: [] };
let customCategories = {};
let currentEditingCat = null; 

const SORT_ORDER = ['base', 'aspiration', 'length', 'nasalized', 'palatalization', 'labialization', 'creaky'];

// ==========================================
// 核心數據初始化
// ==========================================
function initData(ipa, config) {
    inventory = {
        consonant: config.phonology?.inventory_consonants || [],
        vowel: config.phonology?.inventory_vowels || []
    };
    const sourceWeights = config.phonology?.weights || {};
    weights = { consonant: {}, vowel: {} };
    
    ['consonant', 'vowel'].forEach(type => {
        const pluralType = type + 's'; 
        const dataSection = sourceWeights[pluralType] || sourceWeights[type] || {};
        inventory[type].forEach(char => {
            const val = dataSection[char] !== undefined ? dataSection[char] : 10;
            weights[type][char] = parseInt(val);
        });
    });
}

// ==========================================
// 權重管理邏輯
// ==========================================
function updateWeight(type, char, val) {
    const numericVal = parseInt(val);
    if (weights[type]) weights[type][char] = numericVal;
    const safeClass = btoa(encodeURIComponent(char)).replace(/=/g, '');
    
    // 更新數值標籤 (numeric-label)
    document.querySelectorAll(`.val-label-${safeClass}`).forEach(el => el.innerText = numericVal);
    document.querySelectorAll(`input[data-char="${char}"]`).forEach(el => el.value = numericVal);
    
    // 更新卡片外觀 (interactive-pill)
    document.querySelectorAll(`.interactive-pill[data-ipa="${char}"]`).forEach(card => {
        const input = card.querySelector('input[type="range"]');
        if (input) input.setAttribute('value', numericVal);
        card.style.opacity = (numericVal === 0) ? "0.5" : "1";
    });
}

// ==========================================
// 類別管理 (Category)
// ==========================================
function initCategories() {
    const raw = document.getElementById('hiddenCategoriesJson')?.value || '{}';
    try { customCategories = JSON.parse(raw); } catch(e) { customCategories = {}; }
    renderCategoryList();
    renderCategoryPicker();
}

function renderCategoryList() {
    const container = document.getElementById('category-list');
    if (!container) return;
    container.innerHTML = '';
    
    Object.keys(customCategories).forEach(code => {
        const symbols = customCategories[code];
        const isEditing = (currentEditingCat === code);
        const div = document.createElement('div');
        
        // 使用 list-item-edit 結構與 editing 狀態
        div.className = `list-item-edit ${isEditing ? 'editing' : ''}`;
        div.onclick = () => selectCategoryForEdit(code);

        div.innerHTML = `
            <div class="item-main" onclick="event.stopPropagation()">
                <div class="input-group-inline">
                    <span class="label-caps" data-i18n="label_cat_code">CODE</span>
                    <input type="text" class="cat-code-input" value="${code}" 
                           onchange="updateCategoryCode('${code}', this.value)">
                </div>
                
                <div class="symbol-display-area">
                    <div style="margin-bottom: 8px;">
                        <span class="label-caps" data-i18n="${isEditing ? 'status_editing' : 'status_click_edit'}">

</span>
                    </div>
                    <div class="cat-symbols-box" id="box-${code}">
                        ${symbols.length > 0 ? symbols.map(s => `
                            <span class="tag-chip">
                                ${s}
                                <span class="remove" onclick="event.stopPropagation(); removeSymbolFromCat('${code}', '${s}')">×</span>
                            </span>
                        `).join('') : '<span style="color:var(--text-sub); font-size:0.8rem; padding:8px;">(Empty)</span>'}
                    </div>
                </div>
            </div>
            <div class="item-actions">
                <button type="button" class="btn-icon delete" title="Delete" 
                        onclick="event.stopPropagation(); deleteCategory('${code}')">
                    🗑️
                </button>
            </div>
        `;
        container.appendChild(div);
    });
    syncCategoriesToHidden();
}

function selectCategoryForEdit(code) {
    currentEditingCat = (currentEditingCat === code) ? null : code;
    renderCategoryList();
}

function addNewCategory() {
    const newCode = "NEW_" + Math.floor(Math.random()*100);
    customCategories[newCode] = [];
    currentEditingCat = newCode;
    renderCategoryList();
}

function deleteCategory(code) {
    if (currentEditingCat === code) currentEditingCat = null;
    delete customCategories[code];
    renderCategoryList();
}

function updateCategoryCode(oldCode, newCode) {
    newCode = newCode.toUpperCase().trim().replace(/\s+/g, '_');
    if (!newCode || newCode === oldCode) return renderCategoryList();
    
    // 如果新代碼已存在，提示或放棄
    if (customCategories[newCode]) {
        alert("Category code already exists!");
        return renderCategoryList();
    }

    customCategories[newCode] = customCategories[oldCode];
    delete customCategories[oldCode];
    
    if (currentEditingCat === oldCode) currentEditingCat = newCode;
    
    syncCategoriesToHidden();
    renderCategoryList();
}

function removeSymbolFromCat(code, symbol) {
    customCategories[code] = customCategories[code].filter(s => s !== symbol);
    syncCategoriesToHidden();
    renderCategoryList();
}

function toggleSymbolInCurrentCat(char) {
    if (!currentEditingCat) return;
    const symbols = customCategories[currentEditingCat];
    if (symbols.includes(char)) {
        customCategories[currentEditingCat] = symbols.filter(s => s !== char);
    } else {
        customCategories[currentEditingCat].push(char);
    }
    renderCategoryList();
}

function syncCategoriesToHidden() {
    const el = document.getElementById('hiddenCategoriesJson');
    if (el) el.value = JSON.stringify(customCategories);
}

// ==========================================
// 介面渲染生成器
// ==========================================
function createCardHTML(char, type, isPicker = false) {
    const val = weights[type][char] || 10;
    const safeClass = btoa(encodeURIComponent(char)).replace(/=/g, '');
    const clickAction = isPicker ? `onclick="toggleSymbolInCurrentCat('${char}')"` : '';
    const style = (val === 0 && !isPicker) ? 'style="opacity:0.5"' : '';

    return `
        <div class="interactive-pill ${isPicker ? 'pill-compact' : ''}" data-ipa="${char}" data-type="${type}" ${style} ${clickAction}>
            <div class="ipa-symbol-text">${char}</div>
            ${!isPicker ? `
            <div class="slider-box">
                <div class="label-caps">
                    <span data-i18n="label_frequency"></span> 
                    <span class="numeric-label val-label-${safeClass}">${val}</span>
                </div>
                <input type="range" name="weight_${char}" data-char="${char}" data-type="${type}"
                       min="0" max="100" value="${val}" 
                       oninput="updateWeight('${type}', '${char}', this.value)">
            </div>` : ``}
        </div>`;
}

function renderCategoryPicker() {
    const area = document.getElementById('category-picker-area');
    if (!area) return;
    let html = '<div class="grid-auto-layout">';
    ['consonant', 'vowel'].forEach(type => {
        inventory[type].forEach(char => {
            html += createCardHTML(char, type, true);
        });
    });
    html += '</div>';
    area.innerHTML = html;
}

// ==========================================
// 排序與頁籤邏輯
// ==========================================
function applyGlobalSort() {
    const orderStr = document.getElementById('hiddenCustomOrder').value;
    const alphabetArray = orderStr.split(/\s+/).filter(s => s !== "");
    const orderMap = {};
    alphabetArray.forEach((char, index) => { orderMap[char] = index; });

    document.querySelectorAll('.weight-zone .grid-auto-layout, #overall-display-area .grid-auto-layout').forEach(grid => {
        const cards = Array.from(grid.querySelectorAll('.interactive-pill'));
        cards.sort((a, b) => {
            const posA = orderMap[a.dataset.ipa] ?? 999;
            const posB = orderMap[b.dataset.ipa] ?? 999;
            return posA - posB || a.dataset.ipa.localeCompare(b.dataset.ipa);
        });
        cards.forEach(card => grid.appendChild(card));
    });
}

function initSortablePool() {
    const pool = document.getElementById('sort-pool');
    const hiddenInput = document.getElementById('hiddenCustomOrder');
    if (!pool || !hiddenInput) return;
    const allChars = [...inventory.consonant, ...inventory.vowel];
    let currentOrder = hiddenInput.value.split(/\s+/).filter(s => allChars.includes(s));
    allChars.forEach(c => { if(!currentOrder.includes(c)) currentOrder.push(c); });
    pool.innerHTML = '';
    currentOrder.forEach(char => {
        const chip = document.createElement('div');
        chip.className = 'tag-chip';
        chip.draggable = true;
        chip.innerText = char;
        chip.addEventListener('dragstart', () => chip.classList.add('dragging'));
        chip.addEventListener('dragend', () => {
            chip.classList.remove('dragging');
            hiddenInput.value = Array.from(pool.querySelectorAll('.tag-chip')).map(c => c.innerText).join(' ');
            applyGlobalSort();
        });
        pool.appendChild(chip);
    });
    pool.addEventListener('dragover', e => {
        e.preventDefault();
        const dragging = document.querySelector('.dragging');
        const afterElement = Array.from(pool.querySelectorAll('.tag-chip:not(.dragging)')).find(el => {
            const box = el.getBoundingClientRect();
            return e.clientX < box.left + box.width / 2;
        });
        if (!afterElement) pool.appendChild(dragging);
        else pool.insertBefore(dragging, afterElement);
    });
}

function switchMainTab(type) {
    document.querySelectorAll(".tab-content, .tab-btn").forEach(el => el.classList.remove("active"));
    const targetTab = document.getElementById(`${type}-tab`);
    const targetBtn = document.querySelector(`.tab-btn[data-type="${type}"]`);
    if (targetTab) targetTab.classList.add("active");
    if (targetBtn) targetBtn.classList.add("active");
    localStorage.setItem('ipa_mgr_last_main', type);
}

function renderSubTabs(type, subKeys) {
    const bar = document.getElementById(`${type}-sub-bar`);
    if (!bar) return;
    bar.innerHTML = ''; 
    subKeys.sort((a, b) => (SORT_ORDER.indexOf(a) === -1 ? 999 : SORT_ORDER.indexOf(a)) - (SORT_ORDER.indexOf(b) === -1 ? 999 : SORT_ORDER.indexOf(b)));
    subKeys.forEach(key => {
        const btn = document.createElement('button');
        btn.className = 'tab-btn';
        btn.type = 'button';
        const i18nKey = (key === 'base') ? 'ipa_plain' : `ipa_${key}`;
        btn.innerHTML = `<span data-i18n="${i18nKey}"></span>`;
        btn.onclick = () => {
            bar.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.querySelectorAll(`#${type}-display-area .weight-zone`).forEach(z => z.classList.remove('active'));
            document.getElementById(`zone-${type}-${key}`).classList.add('active');
        };
        bar.appendChild(btn);
    });
    if (bar.firstChild) bar.firstChild.click();
}

// ==========================================
// 初始化主邏輯 (修正區塊標題)
// ==========================================
function initAll(ipaData, configData) {
    initData(ipaData, configData);
    
    ['consonant', 'vowel'].forEach(type => {
        const area = document.getElementById(`${type}-display-area`);
        if (!area) return;
        const diacritics = ipaData.diacritics || {};
        const subKeys = ['base', ...Object.keys(diacritics).filter(k => 
            diacritics[k].applies_to === type + 's' && inventory[type].some(v => v.includes(diacritics[k].symbol))
        )];

        subKeys.forEach(key => {
            const items = inventory[type].filter(char => {
                if (key === 'base') return !Object.values(diacritics).some(d => d.symbol && char.includes(d.symbol) && char !== d.symbol);
                return diacritics[key].symbol && char.includes(diacritics[key].symbol);
            });

            if (items.length > 0) {
                const zone = document.createElement('div');
                zone.id = `zone-${type}-${key}`;
                zone.className = 'weight-zone';

                // --- 標題格式化 ---
                const header = document.createElement('div');
                header.className = 'section-header';
                const i18nKey = (key === 'base') ? 'ipa_plain' : `ipa_${key}`;
                header.innerHTML = `<h2 data-i18n="${i18nKey}">${key}</h2>`;
                zone.appendChild(header);

                const grid = document.createElement('div');
                grid.className = 'grid-auto-layout';
                items.forEach(c => grid.innerHTML += createCardHTML(c, type));
                zone.appendChild(grid);

                area.appendChild(zone);
            }
        });
        renderSubTabs(type, subKeys);
    });

    // Overall 區域 (修正樣式結構與標籤生成)
    const overallArea = document.getElementById('overall-display-area');
    if (overallArea) {
        overallArea.innerHTML = ''; 
        const overallSubKeys = [];

        ['consonant', 'vowel'].forEach(type => {
            if (inventory[type].length > 0) {
                overallSubKeys.push(type + 's'); // 用於 renderSubTabs

                const zone = document.createElement('div');
                zone.id = `zone-overall-${type}s`; // 與 renderSubTabs ID 對應
                zone.className = 'weight-zone'; // 確保 Percentile Bar 樣式正確

                const header = document.createElement('div');
                header.className = 'section-header';
                header.innerHTML = `<h2 data-i18n="ipa_${type}s">${type}s</h2>`;
                zone.appendChild(header);

                const grid = document.createElement('div');
                grid.className = 'grid-auto-layout';
                inventory[type].forEach(c => grid.innerHTML += createCardHTML(c, type));
                zone.appendChild(grid);

                overallArea.appendChild(zone);
            }
        });
        
        // 生成 Overall 的子標籤 Bar (Consonants / Vowels)
        renderSubTabs('overall', overallSubKeys);
    }

    initCategories();
    initSortablePool();
    applyGlobalSort();
    if (window.applyTranslations) window.applyTranslations();
}