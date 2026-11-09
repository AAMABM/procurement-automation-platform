import api from './client';
import type { LoginRequest, TokenResponse, UserResponse } from '../types/auth';

export const authApi = {
  async login(payload: LoginRequest): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>('/auth/login', payload);
    return data;
  },
  async me(): Promise<UserResponse> {
    const { data } = await api.get<UserResponse>('/auth/me');
    return data;
  },
};