import type { Vendor } from './vendor';

export interface POLineItem {
  id: string;
  description: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  gl_account: string;
  cost_center: string;
}

export interface PurchaseOrder {
  id: string;
  po_number: string;
  requisition_id: string;
  vendor_id: string;
  status: string;
  total_amount: number;
  currency: string;
  created_at: string;
  vendor: Vendor;
  line_items: POLineItem[];
}