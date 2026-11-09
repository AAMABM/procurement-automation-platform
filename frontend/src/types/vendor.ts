export interface Vendor {
  id: string;
  name: string;
  tax_id: string;
  contact_email: string;
  sap_vendor_number: string | null;
  status: string;
  created_at: string;
}

export interface VendorCreate {
  name: string;
  tax_id: string;
  contact_email: string;
  sap_vendor_number?: string;
}