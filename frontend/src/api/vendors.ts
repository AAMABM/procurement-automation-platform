import api from './client';
import type { Vendor, VendorCreate } from '../types/vendor';

export const vendorsApi = {
  async list(): Promise<Vendor[]> {
    const { data } = await api.get<Vendor[]>('/vendors');
    return data;
  },
  async create(payload: VendorCreate): Promise<Vendor> {
    const { data } = await api.post<Vendor>('/vendors', payload);
    return data;
  },
};