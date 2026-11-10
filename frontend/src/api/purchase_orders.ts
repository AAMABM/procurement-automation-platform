import api from './client';
import type { PurchaseOrder } from '../types/purchase_order';

export const purchaseOrdersApi = {
  async list(): Promise<PurchaseOrder[]> {
    const { data } = await api.get<PurchaseOrder[]>('/purchase-orders');
    return data;
  },
  async create(requisition_id: string, vendor_id: string): Promise<PurchaseOrder> {
    const { data } = await api.post<PurchaseOrder>('/purchase-orders', { requisition_id, vendor_id });
    return data;
  },
};