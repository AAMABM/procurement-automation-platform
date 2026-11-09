import api from './client';
import type { PurchaseRequisition } from '../types/requisition';

export interface PRCreatePayload {
  title: string;
  currency: string;
  justification?: string;
  line_items: {
    description: string;
    quantity: number;
    unit_price: number;
    gl_account: string;
    cost_center: string;
  }[];
}

export const requisitionsApi = {
  async list(): Promise<PurchaseRequisition[]> {
    const { data } = await api.get<PurchaseRequisition[]>('/requisitions');
    return data;
  },
  async create(payload: PRCreatePayload): Promise<PurchaseRequisition> {
    const { data } = await api.post<PurchaseRequisition>('/requisitions', payload);
    return data;
  },
  async submit(id: string): Promise<PurchaseRequisition> {
    const { data } = await api.post<PurchaseRequisition>(`/requisitions/${id}/submit`);
    return data;
  },
  async approve(id: string): Promise<PurchaseRequisition> {
    const { data } = await api.post<PurchaseRequisition>(`/requisitions/${id}/approve`);
    return data;
  },
  async reject(id: string): Promise<PurchaseRequisition> {
    const { data } = await api.post<PurchaseRequisition>(`/requisitions/${id}/reject`);
    return data;
  },
};