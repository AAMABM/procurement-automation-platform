import api from './client';
import type { Invoice } from '../types/invoice';

export const invoicesApi = {
  async list(): Promise<Invoice[]> {
    const { data } = await api.get<Invoice[]>('/invoices');
    return data;
  },
  async createGR(po_id: string, received_by: string) {
    const { data } = await api.post('/goods-receipts', { po_id, received_by });
    return data;
  },
  async createInvoice(po_id: string, invoice_number: string, total_amount: number) {
    const { data } = await api.post('/invoices', { po_id, invoice_number, total_amount });
    return data;
  },
};