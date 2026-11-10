import { useEffect, useState } from 'react';
import {
  Box, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Chip, CircularProgress, Alert, Button, Stack,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField
} from '@mui/material';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import ReceiptIcon from '@mui/icons-material/Receipt';
import { purchaseOrdersApi } from '../api/purchase_orders';
import { invoicesApi } from '../api/invoices';
import type { PurchaseOrder } from '../types/purchase_order';

export function PurchaseOrdersPage() {
  const [pos, setPos] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal states
  const [grOpen, setGrOpen] = useState(false);
  const [invOpen, setInvOpen] = useState(false);
  const [selectedPo, setSelectedPo] = useState<PurchaseOrder | null>(null);
  const [invNumber, setInvNumber] = useState('');
  const [invAmount, setInvAmount] = useState(0);

  const loadPOs = async () => {
    try {
      setLoading(true);
      const data = await purchaseOrdersApi.list();
      setPos(data);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load POs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadPOs(); }, []);

  const handleReceiveGoods = async () => {
    if (!selectedPo) return;
    try {
      await invoicesApi.createGR(selectedPo.id, 'Admin Receiver');
      setGrOpen(false);
      alert('Goods received successfully. PO status is now FULFILLED.');
      loadPOs();
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to receive goods.');
    }
  };

  const handleCreateInvoice = async () => {
    if (!selectedPo) return;
    try {
      await invoicesApi.createInvoice(selectedPo.id, invNumber, invAmount);
      setInvOpen(false);
      alert('Invoice created! Check the Invoices page for the 3-Way Match result.');
      loadPOs();
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to create invoice.');
    }
  };

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
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {pos.map((po) => (
              <TableRow key={po.id}>
                <TableCell>{po.po_number}</TableCell>
                <TableCell>{po.vendor?.name}</TableCell>
                <TableCell>${Number(po.total_amount).toFixed(2)} {po.currency}</TableCell>
                <TableCell><strong>SAP Status</strong></TableCell>
                <TableCell>
  <Chip label="SYNCED" color="success" size="small" variant="outlined" />
</TableCell>
                <TableCell>
                  <Chip label={po.status} color={po.status === 'CLOSED' ? 'success' : 'primary'} size="small" />
                </TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1}>
                    {po.status === 'ISSUED' && (
                      <Button size="small" variant="contained" color="info" startIcon={<LocalShippingIcon />} onClick={() => { setSelectedPo(po); setGrOpen(true); }}>
                        Receive Goods
                      </Button>
                    )}
                    {po.status === 'FULFILLED' && (
                      <Button size="small" variant="contained" color="warning" startIcon={<ReceiptIcon />} onClick={() => { setSelectedPo(po); setInvAmount(Number(po.total_amount)); setInvOpen(true); }}>
                        Create Invoice
                      </Button>
                    )}
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Receive Goods Modal */}
      <Dialog open={grOpen} onClose={() => setGrOpen(false)}>
        <DialogTitle>Receive Goods (GR)</DialogTitle>
        <DialogContent>
          <Typography variant="body2" mt={1}>
            Confirm that all items for {selectedPo?.po_number} have been physically delivered and verified.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGrOpen(false)}>Cancel</Button>
          <Button onClick={handleReceiveGoods} variant="contained" color="info">Confirm Receipt</Button>
        </DialogActions>
      </Dialog>

      {/* Create Invoice Modal */}
      <Dialog open={invOpen} onClose={() => setInvOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Enter Vendor Invoice</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense" label="Vendor Invoice Number" fullWidth
            value={invNumber} onChange={(e) => setInvNumber(e.target.value)}
          />
          <TextField
            margin="dense" label="Invoice Amount" type="number" fullWidth
            value={invAmount} onChange={(e) => setInvAmount(Number(e.target.value))}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInvOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateInvoice} variant="contained" color="warning" disabled={!invNumber || !invAmount}>
            Submit Invoice
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}