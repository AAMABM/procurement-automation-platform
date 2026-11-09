export interface PRLineItem {
  id: string;
  description: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  gl_account: string;
  cost_center: string;
}

export interface PurchaseRequisition {
  id: string;
  pr_number: string;
  title: string;
  status: 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'REJECTED' | 'CANCELLED';
  total_amount: number;
  currency: string;
  justification: string | null;
  required_by: string | null;
  requester_id: string;
  created_at: string;
  line_items: PRLineItem[];
}