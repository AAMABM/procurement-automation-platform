import { useEffect, useState } from 'react';
import {
  Box, Button, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Chip, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, CircularProgress, Alert, IconButton, Stack, Grid,
  MenuItem
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import SendIcon from '@mui/icons-material/Send';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import { requisitionsApi, PRCreatePayload } from '../api/requisitions';
import { purchaseOrdersApi } from '../api/purchase_orders';
import { vendorsApi } from '../api/vendors';
import type { PurchaseRequisition } from '../types/requisition';
import type { Vendor } from '../types/vendor';

const getStatusColor = (status: string) => {
  switch (status) {
    case 'DRAFT': return 'default';
    case 'SUBMITTED': return 'warning';
    case 'APPROVED': return 'success';
    case 'REJECTED': return 'error';
    default: return 'default';
  }
};

export function RequisitionsPage() {
  const [prs, setPrs] = useState<PurchaseRequisition[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create PR Modal state
  const [open, setOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [title, setTitle] = useState('');
  const [justification, setJustification] = useState('');
  const [lineItems, setLineItems] = useState([
    { description: '', quantity: 1, unit_price: 0, gl_account: '', cost_center: '' }
  ]);

  // Create PO Modal state
  const [poOpen, setPoOpen] = useState(false);
  const [selectedPrId, setSelectedPrId] = useState<string | null>(null);
  const [selectedVendorId, setSelectedVendorId] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const [prData, vendorData] = await Promise.all([
        requisitionsApi.list(),
        vendorsApi.list()
      ]);
      setPrs(prData);
      setVendors(vendorData);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleAddLineItem = () => {
    setLineItems([...lineItems, { description: '', quantity: 1, unit_price: 0, gl_account: '', cost_center: '' }]);
  };

  const handleRemoveLineItem = (index: number) => {
    if (lineItems.length === 1) return;
    setLineItems(lineItems.filter((_, i) => i !== index));
  };

  const handleLineItemChange = (index: number, field: string, value: any) => {
    const updated = [...lineItems];
    (updated[index] as any)[field] = value;
    setLineItems(updated);
  };

  const calculateTotal = () => lineItems.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);

  const handleCreatePR = async () => {
    try {
      setSubmitting(true);
      const payload: PRCreatePayload = { title, currency: 'USD', justification, line_items: lineItems };
      await requisitionsApi.create(payload);
      setOpen(false);
      setTitle(''); setJustification(''); 
      setLineItems([{ description: '', quantity: 1, unit_price: 0, gl_account: '', cost_center: '' }]);
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to create PR.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAction = async (action: 'submit' | 'approve' | 'reject', id: string) => {
    try {
      if (action === 'submit') await requisitionsApi.submit(id);
      if (action === 'approve') await requisitionsApi.approve(id);
      if (action === 'reject') await requisitionsApi.reject(id);
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.error?.message || `Failed to ${action} PR.`);
    }
  };

  const handleCreatePO = async () => {
    if (!selectedPrId || !selectedVendorId) return;
    try {
      setSubmitting(true);
      await purchaseOrdersApi.create(selectedPrId, selectedVendorId);
      setPoOpen(false);
      setSelectedPrId(null);
      setSelectedVendorId('');
      alert('Purchase Order created successfully!');
      loadData(); // Refresh PRs (so the button disappears if we add logic for that later)
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to create PO.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Purchase Requisitions</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpen(true)}>
          Create Requisition
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>PR Number</strong></TableCell>
              <TableCell><strong>Title</strong></TableCell>
              <TableCell><strong>Total Amount</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {prs.map((pr) => (
              <TableRow key={pr.id}>
                <TableCell>{pr.pr_number}</TableCell>
                <TableCell>{pr.title}</TableCell>
                <TableCell>${Number(pr.total_amount).toFixed(2)} {pr.currency}</TableCell>
                <TableCell>
                  <Chip label={pr.status} color={getStatusColor(pr.status) as any} size="small" />
                </TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1}>
                    {pr.status === 'DRAFT' && (
                      <Button size="small" variant="outlined" color="primary" startIcon={<SendIcon />} onClick={() => handleAction('submit', pr.id)}>
                        Submit
                      </Button>
                    )}
                    {pr.status === 'SUBMITTED' && (
                      <>
                        <Button size="small" variant="contained" color="success" startIcon={<CheckCircleIcon />} onClick={() => handleAction('approve', pr.id)}>
                          Approve
                        </Button>
                        <Button size="small" variant="outlined" color="error" startIcon={<CancelIcon />} onClick={() => handleAction('reject', pr.id)}>
                          Reject
                        </Button>
                      </>
                    )}
                    {pr.status === 'APPROVED' && (
                      <Button size="small" variant="contained" color="secondary" startIcon={<ShoppingCartIcon />} onClick={() => { setSelectedPrId(pr.id); setPoOpen(true); }}>
                        Create PO
                      </Button>
                    )}
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* CREATE PR MODAL (unchanged) */}
      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>Create Purchase Requisition</DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2} mb={3}>
            <Grid item xs={12} sm={8}>
              <TextField label="Title" fullWidth value={title} onChange={(e) => setTitle(e.target.value)} />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField label="Currency" fullWidth disabled value="USD" />
            </Grid>
            <Grid item xs={12}>
              <TextField label="Justification" fullWidth multiline rows={2} value={justification} onChange={(e) => setJustification(e.target.value)} />
            </Grid>
          </Grid>

          <Typography variant="h6" mt={2} mb={1}>Line Items</Typography>
          {lineItems.map((item, index) => (
            <Grid container spacing={1} key={index} mb={1} alignItems="center">
              <Grid item xs={12} sm={3}>
                <TextField label="Description" size="small" fullWidth value={item.description} onChange={(e) => handleLineItemChange(index, 'description', e.target.value)} />
              </Grid>
              <Grid item xs={4} sm={2}>
                <TextField label="Qty" type="number" size="small" fullWidth value={item.quantity} onChange={(e) => handleLineItemChange(index, 'quantity', Number(e.target.value))} />
              </Grid>
              <Grid item xs={4} sm={2}>
                <TextField label="Unit Price" type="number" size="small" fullWidth value={item.unit_price} onChange={(e) => handleLineItemChange(index, 'unit_price', Number(e.target.value))} />
              </Grid>
              <Grid item xs={4} sm={2}>
                <TextField label="GL Account" size="small" fullWidth value={item.gl_account} onChange={(e) => handleLineItemChange(index, 'gl_account', e.target.value)} />
              </Grid>
              <Grid item xs={6} sm={2}>
                <TextField label="Cost Center" size="small" fullWidth value={item.cost_center} onChange={(e) => handleLineItemChange(index, 'cost_center', e.target.value)} />
              </Grid>
              <Grid item xs={6} sm={1}>
                <IconButton color="error" onClick={() => handleRemoveLineItem(index)} disabled={lineItems.length === 1}>
                  <DeleteIcon />
                </IconButton>
              </Grid>
            </Grid>
          ))}
          <Button startIcon={<AddIcon />} onClick={handleAddLineItem} sx={{ mt: 1 }}>Add Line Item</Button>
          
          <Box mt={3} p={2} bgcolor="grey.100" borderRadius={1} display="flex" justifyContent="space-between">
            <Typography variant="subtitle1" fontWeight="bold">Total Estimated Amount:</Typography>
            <Typography variant="subtitle1" fontWeight="bold">${Number(calculateTotal()).toFixed(2)} USD</Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreatePR} variant="contained" disabled={submitting || !title || lineItems.some(i => !i.description || !i.gl_account || !i.cost_center)}>
            {submitting ? 'Saving...' : 'Save Draft'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* CREATE PO MODAL */}
      <Dialog open={poOpen} onClose={() => setPoOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Convert to Purchase Order</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Select a Vendor to issue the Purchase Order.
          </Typography>
          <TextField
            select
            fullWidth
            label="Select Vendor"
            value={selectedVendorId}
            onChange={(e) => setSelectedVendorId(e.target.value)}
          >
            {vendors.map((vendor) => (
              <MenuItem key={vendor.id} value={vendor.id}>
                {vendor.name} ({vendor.tax_id})
              </MenuItem>
            ))}
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPoOpen(false)}>Cancel</Button>
          <Button onClick={handleCreatePO} variant="contained" color="secondary" disabled={submitting || !selectedVendorId}>
            {submitting ? 'Creating...' : 'Create PO'}
          </Button>
        </DialogActions>
      </Dialog>

    </Box>
  );
}