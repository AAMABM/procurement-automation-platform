import api from './client';

export interface DashboardStats {
  total_spend: number;
  active_pos: number;
  pending_requisitions: number;
  exception_rate: number;
  rfq_response_rate: number;
  spend_by_vendor: { vendor_name: string; total_spend: number }[];
}

export const analyticsApi = {
  async getDashboard(): Promise<DashboardStats> {
    const { data } = await api.get<DashboardStats>('/analytics/dashboard');
    return data;
  },
};