export interface Invoice {
  id: string;
  invoice_number: string;
  po_id: string;
  vendor_id: string;
  total_amount: number;
  currency: string;
  status: string;
  created_at: string;
}