import { useEffect, useState } from 'react';
import {
  Box, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Chip, CircularProgress, Alert
} from '@mui/material';
import { purchaseOrdersApi } from '../api/purchase_orders';
import type { PurchaseOrder } from '../types/purchase_order';

export function PurchaseOrdersPage() {
  const [pos, setPos] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    purchaseOrdersApi.list()
      .then(setPos)
      .catch((err) => setError(err.response?.data?.error?.message || 'Failed to load POs.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box>
      <Typography variant="h4" mb={3}>Purchase Orders</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>PO Number</strong></TableCell>
              <TableCell><strong>Vendor</strong></TableCell>
              <TableCell><strong>Total Amount</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {pos.map((po) => (
              <TableRow key={po.id}>
                <TableCell>{po.po_number}</TableCell>
                <TableCell>{po.vendor?.name}</TableCell>
                <TableCell>${Number(po.total_amount).toFixed(2)} {po.currency}</TableCell>
                <TableCell>
                  <Chip label={po.status} color="primary" size="small" />
                </TableCell>
              </TableRow>
            ))}
            {pos.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} align="center">No Purchase Orders found.</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}