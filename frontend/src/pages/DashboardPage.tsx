import { useEffect, useState } from 'react';
import {
  Box, Grid, Card, CardContent, Typography, CircularProgress, Alert, Chip
} from '@mui/material';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import AssignmentIcon from '@mui/icons-material/Assignment';
import WarningIcon from '@mui/icons-material/Warning';
import ReplyIcon from '@mui/icons-material/Reply';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { analyticsApi, DashboardStats } from '../api/analytics';

export function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    analyticsApi.getDashboard()
      .then(setStats)
      .catch((err: any) => setError(err.response?.data?.error?.message || 'Failed to load analytics.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!stats) return null;

  const formatCurrency = (val: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Procurement Overview</Typography>
      <Typography variant="body1" color="text.secondary" mb={4}>
        Real-time KPIs and insights across the Procure-to-Pay lifecycle.
      </Typography>

      {/* KPI CARDS */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1} color="primary.main">
                <AttachMoneyIcon sx={{ mr: 1 }} /> <Typography variant="subtitle2">Total Spend</Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">{formatCurrency(Number(stats.total_spend))}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1} color="info.main">
                <LocalShippingIcon sx={{ mr: 1 }} /> <Typography variant="subtitle2">Active POs</Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">{stats.active_pos}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1} color="warning.main">
                <AssignmentIcon sx={{ mr: 1 }} /> <Typography variant="subtitle2">Pending PRs</Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">{stats.pending_requisitions}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1} color="error.main">
                <WarningIcon sx={{ mr: 1 }} /> <Typography variant="subtitle2">Exception Rate</Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">{stats.exception_rate}%</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1} color="success.main">
                <ReplyIcon sx={{ mr: 1 }} /> <Typography variant="subtitle2">RFQ Response</Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">{stats.rfq_response_rate}%</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* CHARTS */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card elevation={2} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>Spend by Vendor (Top 5)</Typography>
            <Box height={300} mt={2}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.spend_by_vendor} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="vendor_name" tick={{ fontSize: 12 }} />
                  <YAxis tickFormatter={(val) => `$${val}`} tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(val: number) => formatCurrency(val)} />
                  <Bar dataKey="total_spend" fill="#0a6ed1" radius={[4, 4, 0, 0]} barSize={50} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card elevation={2} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>System Health</Typography>
            <Box display="flex" flexDirection="column" gap={2} mt={2}>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography variant="body2">Database Connection</Typography>
                <Chip label="HEALTHY" color="success" size="small" />
              </Box>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography variant="body2">SAP Integration</Typography>
                <Chip label="CONNECTED" color="success" size="small" />
              </Box>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography variant="body2">API Status</Typography>
                <Chip label="ONLINE" color="success" size="small" />
              </Box>
            </Box>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}