import type { Vendor } from './vendor';

export interface RFQInvitation {
  id: string;
  vendor_id: string;
  status: string;
  vendor: Vendor;
}

export interface QuotationLineItem {
  id: string;
  description: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Quotation {
  id: string;
  vendor_id: string;
  total_amount: number;
  lead_time_days: number;
  status: string;
  vendor: Vendor;
  line_items: QuotationLineItem[];
}

export interface RFQ {
  id: string;
  rfq_number: string;
  title: string;
  status: string;
  deadline: string;
  invitations: RFQInvitation[];
  quotations: Quotation[];
}