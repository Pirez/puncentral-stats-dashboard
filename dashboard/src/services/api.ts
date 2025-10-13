import axios from 'axios';
import * as ApiTypes from '../types/api';
import { rateLimiter } from '../utils/rateLimiter';

// API configuration from environment variables
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_TOKEN = import.meta.env.VITE_API_TOKEN;

// Debug: Log token status (only shows if token exists, not the token itself)
console.log('API Configuration:');
console.log('- Base URL:', API_BASE_URL);
console.log('- Token configured:', API_TOKEN ? 'YES' : 'NO');
if (API_TOKEN) {
  console.log('- Token length:', API_TOKEN.length);
  console.log('- Token preview:', API_TOKEN.substring(0, 10) + '...');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: API_TOKEN ? {
    'Authorization': `Bearer ${API_TOKEN}`
  } : {}
});

// Debug: Log request details
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', {
      url: config.url,
      method: config.method,
      baseURL: config.baseURL,
      hasAuthHeader: !!config.headers.Authorization,
    });
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Debug: Log response details
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      url: response.config.url,
      status: response.status,
      dataType: Array.isArray(response.data) ? `Array[${response.data.length}]` : typeof response.data,
    });
    return response;
  },
  (error) => {
    console.error('API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
    });
    return Promise.reject(error);
  }
);

// Helper function to wrap API calls with rate limiting
async function withRateLimit<T>(
  key: string,
  requestFn: () => Promise<T>
): Promise<T> {
  return rateLimiter.execute(key, requestFn);
}

export const apiService = {
  getPlayerStats: async (): Promise<ApiTypes.PlayerStats[]> => {
    return withRateLimit('player-stats', async () => {
      const response = await api.get<ApiTypes.PlayerStats[]>('/api/player-stats');
      return response.data;
    });
  },

  getMapStats: async (): Promise<ApiTypes.MapStats[]> => {
    return withRateLimit('map-stats', async () => {
      const response = await api.get<ApiTypes.MapStats[]>('/api/map-stats');
      return response.data;
    });
  },

  getChickenKills: async (): Promise<ApiTypes.ChickenKills[]> => {
    return withRateLimit('chicken-kills', async () => {
      const response = await api.get<ApiTypes.ChickenKills[]>('/api/chicken-kills');
      return response.data;
    });
  },

  getMapWinRates: async (): Promise<ApiTypes.MapWinRate[]> => {
    return withRateLimit('map-win-rates', async () => {
      const response = await api.get<ApiTypes.MapWinRate[]>('/api/map-win-rates');
      return response.data;
    });
  },

  getRankInfo: async (): Promise<ApiTypes.RankInfo[]> => {
    return withRateLimit('rank-info', async () => {
      const response = await api.get<ApiTypes.RankInfo[]>('/api/rank-info');
      return response.data;
    });
  },

  getKDRatios: async (): Promise<ApiTypes.KDRatio[]> => {
    return withRateLimit('kd-ratios', async () => {
      const response = await api.get<ApiTypes.KDRatio[]>('/api/kd-ratios');
      return response.data;
    });
  },

  getKDOverTime: async (): Promise<ApiTypes.KDOverTime[]> => {
    return withRateLimit('kd-over-time', async () => {
      const response = await api.get<ApiTypes.KDOverTime[]>('/api/kd-over-time');
      return response.data;
    });
  },

  getLastMatch: async (): Promise<ApiTypes.LastMatch> => {
    return withRateLimit('last-match', async () => {
      const response = await api.get<ApiTypes.LastMatch>('/api/last-match');
      return response.data;
    });
  },

  getMultiKills: async (): Promise<ApiTypes.MultiKillStats[]> => {
    return withRateLimit('multi-kills', async () => {
      const response = await api.get<ApiTypes.MultiKillStats[]>('/api/multi-kills');
      return response.data;
    });
  },

  getUtilityDamage: async (): Promise<ApiTypes.UtilityDamageStats[]> => {
    return withRateLimit('utility-damage', async () => {
      const response = await api.get<ApiTypes.UtilityDamageStats[]>('/api/utility-damage');
      return response.data;
    });
  },
};
