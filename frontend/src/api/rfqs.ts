import api from './client';
import type { RFQ, Quotation } from '../types/rfq';

export const rfqsApi = {
  async list(): Promise<RFQ[]> {
    const { data } = await api.get<RFQ[]>('/rfqs');
    return data;
  },
  async create(title: string, deadline: string, vendor_ids: string[]): Promise<RFQ> {
    const { data } = await api.post<RFQ>('/rfqs', { title, deadline, vendor_ids });
    return data;
  },
  async submitQuotation(rfq_id: string, vendor_id: string, lead_time_days: number, line_items: any[]): Promise<Quotation> {
    const { data } = await api.post<Quotation>(`/rfqs/${rfq_id}/quotations`, { vendor_id, lead_time_days, line_items });
    return data;
  },
  async award(rfq_id: string, quotation_id: string): Promise<any> {
    const { data } = await api.post(`/rfqs/${rfq_id}/award`, { quotation_id });
    return data;
  }
};