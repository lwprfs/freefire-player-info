/**
 * Configuration for Free Fire Player Info
 */

const CONFIG = {
    API: {
        BASE_URL: 'https://api.gameskinbo.com',
        ENDPOINTS: {
            GET_PLAYER: '/ff-info/get',
            USAGE: '/api/usage',
        },
    },

    DEFAULTS: {
        REGION: 'BD',
        HISTORY_LIMIT: 20,
    },

    REGIONS: {
        BD: 'Bangladesh',
        IND: 'India',
        BR: 'Brazil',
        US: 'USA',
        ID: 'Indonesia',
        SG: 'Singapore',
        PK: 'Pakistan',
        MY: 'Malaysia',
        TH: 'Thailand',
        VN: 'Vietnam',
        PH: 'Philippines',
    },

    STORAGE_KEYS: {
        API_KEYS: 'ff_api_keys',
        CURRENT_KEY_INDEX: 'ff_current_key_index',
        HISTORY: 'ff_player_history',
        THEME: 'ff_theme',
        REGION: 'ff_region',
        USAGE_CACHE: 'ff_usage_cache',
    },

    RARITY_COLORS: {
        WHITE: '#ffffff',
        GREEN: '#4caf50',
        BLUE: '#2196f3',
        PURPLE: '#9c27b0',
        GOLD: '#ffd700',
        RED: '#f44336',
        ORANGE: '#ff9800',
    },
};

window.CONFIG = CONFIG;