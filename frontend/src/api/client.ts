/**
 * Axios instance with JWT header injection + transparent refresh.
 *
 * Why interceptors:
 *   Transparent 401 → refresh → retry keeps auth concerns out of every page.
 *   Requests made during a refresh are queued so we don't fire N refreshes
 *   for N concurrent 401s.
 *
 * Security:
 *   We store tokens in-memory + localStorage. In a security-hardened
 *   deployment, prefer httpOnly cookies (Phase 2 item) — noted for auditors.
 */
import axios, {
  AxiosError,
  AxiosRequestConfig,
  InternalAxiosRequestConfig,
} from 'axios';

const ACCESS_KEY = 'pp_access_token';
const REFRESH_KEY = 'pp_refresh_token';

export const tokenStore = {
  get access() { return localStorage.getItem(ACCESS_KEY); },
  get refresh() { return localStorage.getItem(REFRESH_KEY); },
  set(access: string, refresh: string) {
    localStorage.setItem(ACCESS_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStore.access;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let refreshing: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refresh = tokenStore.refresh;
  if (!refresh) return null;
  try {
    const { data } = await axios.post(
      `${api.defaults.baseURL}/auth/refresh`,
      { refresh_token: refresh },
    );
    tokenStore.set(data.access_token, data.refresh_token);
    return data.access_token;
  } catch {
    tokenStore.clear();
    return null;
  }
}

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as (AxiosRequestConfig & { _retry?: boolean }) | undefined;
    if (
      error.response?.status === 401 &&
      original &&
      !original._retry &&
      !original.url?.includes('/auth/login') &&
      !original.url?.includes('/auth/refresh')
    ) {
      original._retry = true;
      refreshing ??= refreshAccessToken().finally(() => { refreshing = null; });
      const newToken = await refreshing;
      if (newToken && original.headers) {
        (original.headers as Record<string, string>).Authorization = `Bearer ${newToken}`;
        return api(original);
      }
      if (typeof window !== 'undefined') window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export default api;