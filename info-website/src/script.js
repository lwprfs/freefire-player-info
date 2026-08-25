/**
 * Free Fire Player Info - Fixed with Pet Images on Main Page
 */

// ================================
// State
// ================================

const STATE = {
    currentUID: null,
    currentData: null,
    currentRegion: 'BD',
    apiKeys: [],
    currentKeyIndex: 0,
    usageCache: {},
    theme: 'dark',
    history: [],
    isDark: true,
    rankData: null,
    itemData: null,
    cdn_img_json: {},
    pngs_json_list: [],
    itemIndex: {},
};

const DOM = {};

// ================================
// DOM Cache
// ================================

function cacheDom() {
    DOM.searchInput = document.getElementById('searchInput');
    DOM.searchBtn = document.getElementById('searchBtn');
    DOM.regionSelect = document.getElementById('regionSelect');
    DOM.historyToggle = document.getElementById('historyToggle');
    DOM.themeToggle = document.getElementById('themeToggle');

    DOM.loading = document.getElementById('loading');
    DOM.error = document.getElementById('error');
    DOM.errorMessage = document.getElementById('errorMessage');
    DOM.playerCard = document.getElementById('playerCard');

    DOM.playerName = document.getElementById('playerName');
    DOM.playerUID = document.getElementById('playerUID');
    DOM.playerLevel = document.getElementById('playerLevel');
    DOM.playerRegion = document.getElementById('playerRegion');
    DOM.playerLikes = document.getElementById('playerLikes');
    DOM.playerAvatar = document.getElementById('playerAvatar');
    DOM.playerCreated = document.getElementById('playerCreated');

    DOM.ovUID = document.getElementById('ovUID');
    DOM.ovName = document.getElementById('ovName');
    DOM.ovLevel = document.getElementById('ovLevel');
    DOM.ovRegion = document.getElementById('ovRegion');
    DOM.ovLikes = document.getElementById('ovLikes');
    DOM.ovSeason = document.getElementById('ovSeason');
    DOM.ovCredit = document.getElementById('ovCredit');
    DOM.ovTitle = document.getElementById('ovTitle');
    DOM.ovBio = document.getElementById('ovBio');
    DOM.ovGender = document.getElementById('ovGender');
    DOM.ovLanguage = document.getElementById('ovLanguage');
    DOM.ovMode = document.getElementById('ovMode');
    DOM.ovRelease = document.getElementById('ovRelease');
    DOM.ovAccountType = document.getElementById('ovAccountType');
    DOM.ovCreated = document.getElementById('ovCreated');
    DOM.ovLastLogin = document.getElementById('ovLastLogin');

    DOM.brRank = document.getElementById('brRank');
    DOM.brPoints = document.getElementById('brPoints');
    DOM.csRank = document.getElementById('csRank');
    DOM.csPoints = document.getElementById('csPoints');
    DOM.brMax = document.getElementById('brMax');
    DOM.csMax = document.getElementById('csMax');
    DOM.showBr = document.getElementById('showBr');
    DOM.showCs = document.getElementById('showCs');

    DOM.equippedItems = document.getElementById('equippedItems');
    DOM.outfitItems = document.getElementById('outfitItems');
    DOM.weaponItems = document.getElementById('weaponItems');
    DOM.skillItems = document.getElementById('skillItems');
    DOM.petInfo = document.getElementById('petInfo');

    DOM.guildContainer = document.getElementById('guildContainer');

    DOM.totalRequests = document.getElementById('totalRequests');
    DOM.apiKeyDisplay = document.getElementById('apiKeyDisplay');
    DOM.apiPlan = document.getElementById('apiPlan');
    DOM.usageBar = document.getElementById('usageBar');
    DOM.usageText = document.getElementById('usageText');

    DOM.historyList = document.getElementById('historyList');
    DOM.refreshBtn = document.getElementById('refreshBtn');
    DOM.exportBtn = document.getElementById('exportBtn');

    DOM.tabs = document.querySelectorAll('.tab');
    DOM.tabPanes = document.querySelectorAll('.tab-pane');

    // Popup elements
    DOM.popup = document.getElementById('itemPopup');
    DOM.popupImage = document.getElementById('popupImage');
    DOM.popupTitle = document.getElementById('popupTitle');
    DOM.popupDesc = document.getElementById('popupDescription');
    DOM.popupId = document.getElementById('popupId');
    DOM.popupRarity = document.getElementById('popupRarity');
    DOM.popupType = document.getElementById('popupType');
    DOM.popupBadge = document.getElementById('popupRarityBadge');
    DOM.popupClose = document.getElementById('popupCloseBtn');
    DOM.popupTelegram = document.getElementById('popupTelegramBtn');
    DOM.popupLens = document.getElementById('popupLensBtn');
}

// ================================
// Load Data
// ================================

async function loadData() {
    try {
        const [cdnData, pngsData, itemDatar] = await Promise.all([
            fetch('assets/cdn.json').then((res) => res.json()),
            fetch('https://raw.githubusercontent.com/0xme/ff-resources/refs/heads/main/pngs/300x300/list.json').then((res) => res.json()),
            fetch('assets/itemData.json').then((res) => res.json()),
        ]);

        STATE.cdn_img_json = cdnData.reduce((map, obj) => Object.assign(map, obj), {});
        STATE.pngs_json_list = pngsData;
        STATE.itemData = itemDatar;

        STATE.itemIndex = {};
        for (const item of itemDatar) {
            STATE.itemIndex[String(item.itemID)] = item;
        }

        console.log('📦 Loaded', Object.keys(STATE.itemIndex).length, 'items');
        console.log('📦 Loaded', Object.keys(STATE.cdn_img_json).length, 'CDN mappings');
        console.log('📦 Loaded', STATE.pngs_json_list.length, 'PNG files');

    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// ================================
// Item Lookup
// ================================

function getItemInfo(itemId) {
    if (!itemId) return null;
    return STATE.itemIndex[String(itemId)] || null;
}

function getItemDisplayName(itemId) {
    const info = getItemInfo(itemId);
    if (!info) return null;
    const name = info.name;
    const desc2 = info.description2;
    const desc = info.description;
    
    if (name && name !== 'NONE' && name !== 'null' && name.trim() !== '') {
        return name;
    }
    if (desc2 && desc2 !== 'NONE' && desc2 !== 'null' && desc2.trim() !== '') {
        return desc2;
    }
    if (desc && desc !== 'NONE' && desc !== 'null' && desc.trim() !== '') {
        return desc;
    }
    return null;
}

function getItemDescription(itemId) {
    const info = getItemInfo(itemId);
    if (!info) return null;
    const desc = info.description;
    const desc2 = info.description2;
    if (desc && desc !== 'NONE' && desc !== 'null' && desc.trim() !== '') {
        return desc;
    }
    if (desc2 && desc2 !== 'NONE' && desc2 !== 'null' && desc2.trim() !== '') {
        return desc2;
    }
    return null;
}

function getItemRarity(itemId) {
    const info = getItemInfo(itemId);
    return info ? info.Rare : null;
}

function getItemIcon(itemId) {
    const info = getItemInfo(itemId);
    return info ? info.icon : null;
}

function getItemType(itemId) {
    const info = getItemInfo(itemId);
    return info ? (info.itemType || info.collectionType) : null;
}

function getItemCollectionType(itemId) {
    const info = getItemInfo(itemId);
    return info ? info.collectionType : null;
}

// ================================
// Get Item Image
// ================================

function getItemImageUrl(itemId) {
    if (!itemId) return null;
    
    const info = getItemInfo(itemId);
    const icon = info ? info.icon : null;
    const idStr = String(itemId);
    
    // 1. Try CDN first
    const cdnUrl = STATE.cdn_img_json[idStr] ?? null;
    if (cdnUrl) {
        return cdnUrl;
    }
    
    // 2. Try ff-resources using icon name
    if (icon && STATE.pngs_json_list?.includes(icon + ".png")) {
        return `https://raw.githubusercontent.com/0xme/ff-resources/refs/heads/main/pngs/300x300/${icon}.png`;
    }
    
    // 3. Try ff-resources with ID
    if (STATE.pngs_json_list?.includes(idStr + ".png")) {
        return `https://raw.githubusercontent.com/0xme/ff-resources/refs/heads/main/pngs/300x300/${idStr}.png`;
    }
    
    // 4. Try pet specific patterns
    if (idStr.startsWith('130') || idStr.startsWith('131')) {
        const petIcon = icon || idStr;
        if (STATE.pngs_json_list?.includes(petIcon + ".png")) {
            return `https://raw.githubusercontent.com/0xme/ff-resources/refs/heads/main/pngs/300x300/${petIcon}.png`;
        }
    }
    
    return null;
}

function getRarityColor(rare) {
    const colors = {
        'WHITE': '#ffffff',
        'GREEN': '#4caf50',
        'BLUE': '#2196f3',
        'PURPLE': '#9c27b0',
        'GOLD': '#ffd700',
        'RED': '#f44336',
        'ORANGE': '#ff9800',
        'CARD': '#ff6b6b',
        'PURPLE_PLUS': '#ab47bc',
        'ORANGE_PLUS': '#ff9100',
        'NONE': '#666666',
    };
    return colors[rare] || '#888888';
}

// ================================
// Theme
// ================================

function initTheme() {
    const saved = localStorage.getItem('ff_theme') || 'dark';
    STATE.theme = saved;
    applyTheme(saved);
}

function applyTheme(theme) {
    STATE.isDark = theme === 'dark';
    document.documentElement.setAttribute('data-theme', theme);
    if (DOM.themeToggle) {
        DOM.themeToggle.textContent = theme === 'dark' ? '🌙' : '☀️';
    }
    localStorage.setItem('ff_theme', theme);
}

function toggleTheme() {
    applyTheme(STATE.isDark ? 'light' : 'dark');
}

// ================================
// API Keys Management
// ================================

function loadApiKeys() {
    try {
        const keys = localStorage.getItem('ff_api_keys');
        if (keys) STATE.apiKeys = JSON.parse(keys);
        const idx = localStorage.getItem('ff_current_key_index');
        if (idx !== null) STATE.currentKeyIndex = parseInt(idx);
    } catch (e) {
        STATE.apiKeys = [];
    }
}

function saveApiKeys() {
    try {
        localStorage.setItem('ff_api_keys', JSON.stringify(STATE.apiKeys));
        localStorage.setItem('ff_current_key_index', String(STATE.currentKeyIndex));
    } catch (e) {}
}

function getActiveApiKey() {
    if (STATE.apiKeys.length === 0) {
        const key = prompt('🔑 Enter your GameSkinBo API key:\n(Get one from https://api.gameskinbo.com)');
        if (key && key.trim()) {
            STATE.apiKeys.push(key.trim());
            STATE.currentKeyIndex = 0;
            saveApiKeys();
            return key.trim();
        }
        return null;
    }
    if (STATE.currentKeyIndex >= STATE.apiKeys.length) {
        STATE.currentKeyIndex = 0;
        saveApiKeys();
    }
    return STATE.apiKeys[STATE.currentKeyIndex];
}

// ================================
// History
// ================================

function loadHistory() {
    try {
        const data = localStorage.getItem('ff_player_history');
        if (data) STATE.history = JSON.parse(data);
    } catch (e) { STATE.history = []; }
}

function saveHistory() {
    try {
        localStorage.setItem('ff_player_history', JSON.stringify(STATE.history));
    } catch (e) {}
}

function addToHistory(uid, name, data) {
    STATE.history = STATE.history.filter(item => item.uid !== uid);
    STATE.history.unshift({ uid, name: name || uid, timestamp: Date.now(), data });
    if (STATE.history.length > 20) STATE.history = STATE.history.slice(0, 20);
    saveHistory();
    renderHistory();
}

function renderHistory() {
    const show = DOM.historyToggle.checked;
    const section = document.getElementById('historySection');
    if (!section) return;
    if (!show) { section.style.display = 'none'; return; }
    section.style.display = 'block';

    if (STATE.history.length === 0) {
        DOM.historyList.innerHTML = '<p class="empty-state">No players in history yet.</p>';
        return;
    }

    DOM.historyList.innerHTML = STATE.history.map(item => `
        <div class="history-item" data-uid="${item.uid}">
            <span class="h-name">${escapeHtml(item.name)}</span>
            <span class="h-uid">(${item.uid})</span>
            <span class="h-time">${formatTimeAgo(item.timestamp)}</span>
        </div>
    `).join('');

    DOM.historyList.querySelectorAll('.history-item').forEach(el => {
        el.addEventListener('click', () => {
            DOM.searchInput.value = el.dataset.uid;
            performSearch();
        });
    });
}

// ================================
// Utility Functions
// ================================

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatTimeAgo(timestamp) {
    const diff = Date.now() - timestamp;
    const mins = Math.floor(diff / 60000);
    const hrs = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    if (mins < 1) return 'just now';
    if (mins < 60) return mins + 'm ago';
    if (hrs < 24) return hrs + 'h ago';
    return days + 'd ago';
}

function formatDate(timestamp) {
    if (!timestamp || timestamp === 'N/A') return 'N/A';
    try {
        const dt = new Date(parseInt(timestamp) * 1000);
        return dt.toLocaleString('en-US', {
            month: 'long', day: 'numeric', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    } catch (e) { return 'N/A'; }
}

function getGenderLabel(gender) {
    if (!gender) return '—';
    return gender.replace('Gender_', '');
}

function getLanguageLabel(lang) {
    if (!lang) return '—';
    return lang.replace('Language_', '');
}

function getModeLabel(mode) {
    if (!mode) return '—';
    return mode.replace('ModePrefer_', '');
}

function getRankDisplay(points, rankData, type) {
    if (!points || points === 'N/A' || points === null || points === '') return 'Unranked';
    try {
        const val = parseInt(points);
        const ranks = rankData?.[type] || {};
        for (const [name, range] of Object.entries(ranks)) {
            const min = range.min_rp !== undefined ? range.min_rp : range.min_stars;
            const max = range.max_rp !== undefined ? range.max_rp : range.max_stars;
            if (val >= min && val <= max) return name;
        }
        return 'Unranked';
    } catch (e) { return 'Unranked'; }
}

// ================================
// API Calls
// ================================

async function fetchPlayerInfo(uid, region) {
    const apiKey = getActiveApiKey();
    if (!apiKey) throw new Error('No API key available.');

    const url = `https://api.gameskinbo.com/ff-info/get?uid=${uid}&region=${region}`;
    const response = await fetch(url, { headers: { 'x-api-key': apiKey } });

    if (!response.ok) {
        let errorMsg = `HTTP ${response.status}`;
        try { const data = await response.json(); if (data.error) errorMsg = data.error; } catch (e) {}
        throw new Error(errorMsg);
    }

    const data = await response.json();
    await updateUsageCache(apiKey);
    return data;
}

async function updateUsageCache(apiKey) {
    try {
        const url = 'https://api.gameskinbo.com/api/usage';
        const response = await fetch(url, { headers: { 'x-api-key': apiKey } });
        if (response.ok) {
            const data = await response.json();
            STATE.usageCache[apiKey] = data;
            localStorage.setItem('ff_usage_cache', JSON.stringify(STATE.usageCache));
        }
    } catch (e) {}
}

// ================================
// Item Popup Functions
// ================================

function openItemPopup(itemId) {
    const info = getItemInfo(itemId);
    const name = getItemDisplayName(itemId) || String(itemId);
    const imageUrl = getItemImageUrl(itemId);
    
    const desc = getItemDescription(itemId) || 'No description available';
    const rare = info?.Rare || 'Unknown';
    const rareColor = getRarityColor(rare);
    const itemType = info?.itemType || 'Unknown';
    const collectionType = info?.collectionType || null;
    const icon = info?.icon || null;
    const isUnique = info?.isUnique || null;

    DOM.popupImage.src = imageUrl || `https://ui-avatars.com/api/?name=${encodeURIComponent(itemId)}&background=FFBA00&color=000&size=200`;
    DOM.popupImage.alt = name;
    DOM.popupImage.onerror = function() {
        this.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(itemId)}&background=FFBA00&color=000&size=200`;
    };
    DOM.popupTitle.textContent = name;
    DOM.popupDesc.textContent = desc;
    DOM.popupId.innerHTML = `<strong>ID:</strong> ${itemId}`;
    DOM.popupRarity.innerHTML = `<strong>Rarity:</strong> <span style="color:${rareColor};">${rare}</span>`;
    
    let typeStr = itemType;
    if (collectionType && collectionType !== 'NONE' && collectionType !== 'null') {
        typeStr += ` (${collectionType})`;
    }
    DOM.popupType.innerHTML = `<strong>Type:</strong> ${typeStr}`;

    if (icon) {
        DOM.popupType.innerHTML += `<br><strong>Icon:</strong> ${icon}`;
    }
    if (isUnique && isUnique !== 'NONE' && isUnique !== 'null') {
        DOM.popupType.innerHTML += `<br><strong>Unique:</strong> ${isUnique}`;
    }

    DOM.popupBadge.textContent = rare;
    DOM.popupBadge.style.color = rareColor;
    DOM.popupBadge.style.borderColor = rareColor;

    DOM.popup.dataset.itemId = itemId;
    DOM.popup.dataset.itemLabel = name;
    DOM.popup.dataset.imageUrl = imageUrl;

    DOM.popup.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeItemPopup() {
    DOM.popup.classList.remove('active');
    document.body.style.overflow = '';
}

function shareItemToTelegram() {
    const itemId = DOM.popup.dataset.itemId;
    const label = DOM.popup.dataset.itemLabel || itemId;
    const imageUrl = DOM.popup.dataset.imageUrl;
    const message = `🎯 *Free Fire Item*\n\n📦 *${label}*\n🆔 ID: \`${itemId}\`\n🖼️ ${imageUrl}`;
    window.open(`https://t.me/share/url?url=${encodeURIComponent(message)}&text=`, '_blank');
}

function openGoogleLens() {
    const imageUrl = DOM.popup.dataset.imageUrl;
    if (imageUrl && !imageUrl.includes('ui-avatars.com')) {
        window.open(`https://lens.google.com/uploadbyurl?url=${encodeURIComponent(imageUrl)}`, '_blank');
    } else {
        alert('No valid image available for Google Lens');
    }
}

// ================================
// Render Functions
// ================================

function renderItemChip(itemId, label) {
    const name = getItemDisplayName(itemId) || String(itemId);
    const rare = getItemRarity(itemId);
    const rareColor = getRarityColor(rare);
    const imageUrl = getItemImageUrl(itemId);
    const hasImage = imageUrl !== null;

    let chipHtml = `
        <div class="item-chip" 
             style="${rare ? `border-color: ${rareColor};` : ''}"
             onclick="openItemPopup('${itemId}')">
    `;

    if (hasImage) {
        chipHtml += `
            <div class="item-chip-image">
                <img src="${imageUrl}" alt="${name}" loading="lazy" 
                     onerror="this.style.display='none'" />
            </div>
        `;
    } else {
        chipHtml += `
            <div class="item-chip-image" style="background: var(--bg-secondary); display:flex; align-items:center; justify-content:center; font-size:32px;">
                🎯
            </div>
        `;
    }

    chipHtml += `
            <div class="item-chip-info">
                ${label ? `<span class="item-chip-label">${label}</span>` : ''}
                <span class="item-chip-name">${name}</span>
                ${rare ? `<span class="item-chip-rarity" style="color:${rareColor};">${rare}</span>` : ''}
            </div>
        </div>
    `;

    return chipHtml;
}

function renderSkillChip(skillId) {
    const name = getItemDisplayName(skillId) || String(skillId);
    return `
        <div class="skill-chip" onclick="openItemPopup('${skillId}')">
            ${name}
        </div>
    `;
}

function renderTitleChip(titleId) {
    const name = getItemDisplayName(titleId) || String(titleId);
    const rare = getItemRarity(titleId);
    const rareColor = getRarityColor(rare);
    const imageUrl = getItemImageUrl(titleId);
    const hasImage = imageUrl !== null;

    let html = `
        <div class="title-chip" 
             style="${rare ? `border-color: ${rareColor};` : ''}"
             onclick="openItemPopup('${titleId}')">
    `;

    if (hasImage) {
        html += `<img src="${imageUrl}" alt="${name}" class="title-chip-image" onerror="this.style.display='none'" />`;
    } else {
        html += `<span class="title-chip-image" style="display:flex; align-items:center; justify-content:center; font-size:16px;">🎯</span>`;
    }

    html += `
            <span class="title-chip-name">${name}</span>
            ${rare ? `<span class="title-chip-rarity" style="color:${rareColor};">${rare}</span>` : ''}
        </div>
    `;

    return html;
}

// ================================
// Display Functions
// ================================

function displayPlayer(data, uid) {
    STATE.currentData = data;
    STATE.currentUID = uid;

    const acc = data.AccountInfo || {};
    const profile = data.AccountProfileInfo || {};
    const social = data.SocialInfo || {};
    const equipped = data.EquippedItemsInfo || {};
    const pet = data.PetInfo || {};
    const guild = data.GuildInfo || {};
    const guildOwner = data.GuildOwnerInfo || {};
    const credit = data.CreditScoreInfo || {};
    const rankData = window.RANK_DATA || null;

    const name = acc.AccountName || 'Unknown';
    const level = acc.AccountLevel || '—';
    const region = acc.AccountRegion || '—';
    const likes = acc.AccountLikes || 0;
    const created = formatDate(acc.AccountCreateTime);

    DOM.playerName.textContent = name;
    DOM.playerUID.textContent = `UID: ${uid}`;
    DOM.playerLevel.textContent = `Level ${level}`;
    DOM.playerRegion.textContent = region || '—';
    DOM.playerLikes.textContent = `❤️ ${likes}`;
    DOM.playerAvatar.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=FFBA00&color=000&size=80`;
    DOM.playerCreated.textContent = created ? `Opened: ${created}` : '';

    // Overview
    DOM.ovUID.textContent = uid;
    DOM.ovName.textContent = name;
    DOM.ovLevel.textContent = level;
    DOM.ovRegion.textContent = region || '—';
    DOM.ovLikes.textContent = likes;
    DOM.ovSeason.textContent = acc.AccountSeasonId || '—';
    DOM.ovCredit.textContent = credit.creditScore || '—';

    const titleId = profile.Title;
    if (titleId) {
        DOM.ovTitle.innerHTML = renderTitleChip(titleId);
    } else {
        DOM.ovTitle.textContent = '—';
    }

    DOM.ovBio.textContent = social.signature || 'No bio';
    DOM.ovGender.textContent = getGenderLabel(social.gender);
    DOM.ovLanguage.textContent = getLanguageLabel(social.language);
    DOM.ovMode.textContent = getModeLabel(social.modePrefer);
    DOM.ovRelease.textContent = data.ReleaseVersion || '—';
    DOM.ovAccountType.textContent = data.AccountType || '—';
    DOM.ovCreated.textContent = created || '—';
    DOM.ovLastLogin.textContent = formatDate(acc.AccountLastLogin);

    // Rank
    const brPoints = profile.BrRankPoint;
    const csPoints = profile.CsRankPoint;

    DOM.brRank.textContent = brPoints ? getRankDisplay(brPoints, rankData, 'br') : 'Unranked';
    DOM.brPoints.textContent = brPoints ? `${brPoints} RP` : '—';
    DOM.csRank.textContent = csPoints ? getRankDisplay(csPoints, rankData, 'cs') : 'Unranked';
    DOM.csPoints.textContent = csPoints ? `${csPoints} ★` : '—';
    DOM.brMax.textContent = profile.BrMaxRank || '—';
    DOM.csMax.textContent = profile.CsMaxRank || '—';
    DOM.showBr.textContent = profile.ShowBrRank ? 'Yes' : 'No';
    DOM.showCs.textContent = profile.ShowCsRank ? 'Yes' : 'No';

    // Equipped Items
    const equippedItems = [];
    if (equipped.EquippedAvatarId) equippedItems.push({ id: equipped.EquippedAvatarId, label: 'Avatar' });
    if (equipped.EquippedBannerId) equippedItems.push({ id: equipped.EquippedBannerId, label: 'Banner' });
    if (equipped.EquippedBPID) equippedItems.push({ id: equipped.EquippedBPID, label: 'BP' });
    if (equipped.EquippedBPBadges) equippedItems.push({ id: equipped.EquippedBPBadges, label: 'BP Badges' });

    DOM.equippedItems.innerHTML = equippedItems.length > 0
        ? equippedItems.map(item => renderItemChip(item.id, item.label)).join('')
        : '<p class="empty-state">No equipped items</p>';

    // Outfit
    const outfit = equipped.EquippedOutfit || [];
    DOM.outfitItems.innerHTML = outfit.length > 0
        ? outfit.map((id) => renderItemChip(id, null)).join('')
        : '<p class="empty-state">No outfit</p>';

    // Weapons
    const weapons = equipped.EquippedWeapon || [];
    DOM.weaponItems.innerHTML = weapons.length > 0
        ? weapons.map((id) => renderItemChip(id, null)).join('')
        : '<p class="empty-state">No weapons</p>';

    // Skills
    const skills = equipped.EquippedSkills || [];
    if (skills.length > 0) {
        const skillGroups = [];
        for (let i = 0; i < skills.length; i += 4) {
            skillGroups.push(skills.slice(i, i + 4));
        }
        DOM.skillItems.innerHTML = skillGroups.map((group, idx) => {
            const skillNames = group.map(id => getItemDisplayName(id) || id).join(', ');
            return `
                <div class="skill-chip" onclick="openItemPopup('${group[0]}')">
                    Slot ${idx + 1}: ${skillNames}
                </div>
            `;
        }).join('');
    } else {
        DOM.skillItems.innerHTML = '<p class="empty-state">No skills</p>';
    }

    // ============================================
    // PET - NOW USES item-chip WITH IMAGES
    // ============================================
    if (pet && pet.id) {
        const petName = getItemDisplayName(pet.id) || pet.id;
        
        // Use item-chip for pet (shows image)
        let petHtml = `
            <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap:10px; width:100%;">
                ${renderItemChip(pet.id, '🐾 Pet')}
        `;
        
        // Pet details as info chips
        petHtml += `
                <div class="pet-detail-chip">Level: ${pet.level || '—'}</div>
                <div class="pet-detail-chip">Exp: ${pet.exp || '—'}</div>
                <div class="pet-detail-chip">Selected: ${pet.isSelected ? '✅ Yes' : '❌ No'}</div>
            </div>
        `;
        
        // Pet Skill (clickable)
        if (pet.selectedSkillId) {
            const skillName = getItemDisplayName(pet.selectedSkillId) || pet.selectedSkillId;
            petHtml += `
                <div style="margin-top:8px; display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                    ${renderItemChip(pet.selectedSkillId, '⚡ Skill')}
            `;
            if (pet.skinId) {
                petHtml += renderItemChip(pet.skinId, '🎨 Skin');
            }
            petHtml += `</div>`;
        } else if (pet.skinId) {
            petHtml += `
                <div style="margin-top:8px; display:grid; grid-template-columns: 1fr; gap:10px;">
                    ${renderItemChip(pet.skinId, '🎨 Skin')}
                </div>
            `;
        }
        
        DOM.petInfo.innerHTML = petHtml;
    } else {
        DOM.petInfo.innerHTML = '<p class="empty-state">No pet</p>';
    }

    // Guild
    if (guild && guild.GuildID && guild.GuildID !== 'None' && guild.GuildID !== 'null') {
        let guildHtml = `
            <div class="guild-info">
                <div class="guild-name">🏰 ${escapeHtml(guild.GuildName || 'Unknown Guild')}</div>
                <div class="guild-detail">
                    <span><strong>ID:</strong> ${guild.GuildID}</span>
                    <span><strong>Level:</strong> ${guild.GuildLevel || '—'}</span>
                    <span><strong>Members:</strong> ${guild.GuildMember || 0}/30</span>
                    <span><strong>Owner:</strong> ${guild.GuildOwner || '—'}</span>
                </div>
        `;
        if (guildOwner && guildOwner.nickname) {
            guildHtml += `
                <div class="guild-leader">
                    <div class="guild-leader-name">👑 ${escapeHtml(guildOwner.nickname)}</div>
                    <div class="guild-detail">
                        <span><strong>UID:</strong> ${guildOwner.accountId || '—'}</span>
                        <span><strong>Level:</strong> ${guildOwner.level || '—'}</span>
                        <span><strong>Likes:</strong> ${guildOwner.liked || 0}</span>
                        <span><strong>BR:</strong> ${guildOwner.rank || '—'} (${guildOwner.rankingPoints || 0} RP)</span>
                        <span><strong>CS:</strong> ${guildOwner.csRank || '—'}</span>
                    </div>
                    <div class="guild-detail">
                        <span><strong>Created:</strong> ${formatDate(guildOwner.createAt)}</span>
                        <span><strong>Last Login:</strong> ${formatDate(guildOwner.lastLoginAt)}</span>
                    </div>
                </div>
            `;
        }
        guildHtml += `</div>`;
        DOM.guildContainer.innerHTML = guildHtml;
    } else {
        DOM.guildContainer.innerHTML = '<p class="empty-state">No guild information</p>';
    }

    // API Usage
    const apiKey = getActiveApiKey();
    const usage = STATE.usageCache[apiKey] || {};
    const limit = usage.limit || 100;
    const used = usage.used || 0;
    const remaining = usage.remaining || (limit - used);
    const pct = Math.min((used / limit) * 100, 100);

    DOM.totalRequests.textContent = used;
    DOM.apiKeyDisplay.textContent = apiKey ? `${apiKey.slice(0, 8)}...${apiKey.slice(-4)}` : '—';
    DOM.apiPlan.textContent = usage.plan || 'free';
    DOM.usageBar.style.width = `${pct}%`;
    DOM.usageBar.style.background = pct > 80 ? 'linear-gradient(135deg, #ff4444, #ff6b00)' : 'var(--accent-gradient)';
    DOM.usageText.textContent = `${used} / ${limit} used (${remaining} remaining)`;

    DOM.playerCard.style.display = 'block';
    DOM.loading.style.display = 'none';
    DOM.error.style.display = 'none';

    addToHistory(uid, name, data);

    const url = new URL(window.location);
    url.searchParams.set('uid', uid);
    url.searchParams.set('region', STATE.currentRegion);
    window.history.pushState({ uid, region: STATE.currentRegion }, '', url);
}

// ================================
// Search
// ================================

async function performSearch() {
    const uid = DOM.searchInput.value.trim();
    if (!uid) { showError('Please enter a UID'); return; }

    const region = DOM.regionSelect.value || 'BD';
    STATE.currentRegion = region;

    DOM.playerCard.style.display = 'none';
    DOM.loading.style.display = 'block';
    DOM.error.style.display = 'none';

    try {
        const data = await fetchPlayerInfo(uid, region);
        displayPlayer(data, uid);
    } catch (err) {
        showError(err.message || 'Failed to fetch player data.');
        DOM.loading.style.display = 'none';
    }
}

function showError(message) {
    DOM.errorMessage.textContent = message;
    DOM.error.style.display = 'flex';
}

function clearError() {
    DOM.error.style.display = 'none';
}

// ================================
// Export
// ================================

function exportPlayerData() {
    if (!STATE.currentData) { alert('No player data to export.'); return; }
    const data = {
        uid: STATE.currentUID,
        fetched: new Date().toISOString(),
        region: STATE.currentRegion,
        data: STATE.currentData,
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `player_${STATE.currentUID}_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ================================
// Tabs
// ================================

function setupTabs() {
    DOM.tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            DOM.tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const target = tab.dataset.tab;
            DOM.tabPanes.forEach(pane => {
                pane.classList.remove('active');
                if (pane.id === `tab-${target}`) pane.classList.add('active');
            });
        });
    });
}

// ================================
// Popup Listeners
// ================================

function setupPopupListeners() {
    DOM.popupClose.addEventListener('click', closeItemPopup);
    DOM.popup.addEventListener('click', function(e) {
        if (e.target === this) closeItemPopup();
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeItemPopup();
    });
    DOM.popupTelegram.addEventListener('click', shareItemToTelegram);
    DOM.popupLens.addEventListener('click', openGoogleLens);
}

// ================================
// Init
// ================================

async function init() {
    cacheDom();
    STATE.rankData = window.RANK_DATA || null;
    await loadData();
    loadApiKeys();
    loadHistory();
    initTheme();

    DOM.searchBtn.addEventListener('click', performSearch);
    DOM.searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') performSearch();
    });
    DOM.themeToggle.addEventListener('click', toggleTheme);
    DOM.historyToggle.addEventListener('change', renderHistory);
    DOM.refreshBtn.addEventListener('click', () => {
        if (STATE.currentUID) performSearch();
    });
    DOM.exportBtn.addEventListener('click', exportPlayerData);

    setupTabs();
    setupPopupListeners();
    renderHistory();

    const urlParams = new URLSearchParams(window.location.search);
    const uid = urlParams.get('uid');
    const region = urlParams.get('region');
    if (uid) {
        DOM.searchInput.value = uid;
        if (region) DOM.regionSelect.value = region;
        setTimeout(performSearch, 300);
    }

    console.log('🎯 Free Fire Player Info initialized with pet images!');
}

document.addEventListener('DOMContentLoaded', init);