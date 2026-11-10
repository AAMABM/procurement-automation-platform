import { useEffect, useState } from 'react';
import {
  Box, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Chip, CircularProgress, Alert
} from '@mui/material';
import { invoicesApi } from '../api/invoices';
import type { Invoice } from '../types/invoice';

const getStatusColor = (status: string) => {
  if (status === 'MATCHED') return 'success';
  if (status === 'EXCEPTION') return 'error';
  return 'warning';
};

export function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    invoicesApi.list()
      .then(setInvoices)
      .catch((err) => setError(err.response?.data?.error?.message || 'Failed to load invoices.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box>
      <Typography variant="h4" mb={3}>Invoices (3-Way Match)</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Invoice #</strong></TableCell>
              <TableCell><strong>PO ID</strong></TableCell>
              <TableCell><strong>Total Amount</strong></TableCell>
              <TableCell><strong>Match Status</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {invoices.map((inv) => (
              <TableRow key={inv.id}>
                <TableCell>{inv.invoice_number}</TableCell>
                <TableCell>{inv.po_id.substring(0, 8)}...</TableCell>
                <TableCell>${Number(inv.total_amount).toFixed(2)} {inv.currency}</TableCell>
                <TableCell>
                  <Chip label={inv.status} color={getStatusColor(inv.status) as any} size="small" />
                </TableCell>
              </TableRow>
            ))}
            {invoices.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} align="center">No invoices processed yet.</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}