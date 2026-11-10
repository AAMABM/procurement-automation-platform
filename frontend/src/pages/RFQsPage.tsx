import { useEffect, useState } from 'react';
import {
  Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Chip, CircularProgress, Alert, Button, Stack, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, MenuItem, Grid, IconButton
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import GavelIcon from '@mui/icons-material/Gavel';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import DeleteIcon from '@mui/icons-material/Delete';
import { rfqsApi } from '../api/rfqs';
import { vendorsApi } from '../api/vendors';
import type { RFQ, Quotation } from '../types/rfq';
import type { Vendor } from '../types/vendor';

const getStatusColor = (status: string) => {
  switch (status) {
    case 'PUBLISHED': return 'warning';
    case 'EVALUATION': return 'info';
    case 'AWARDED': return 'success';
    default: return 'default';
  }
};

export function RFQsPage() {
  const [rfqs, setRfqs] = useState<RFQ[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modals
  const [createOpen, setCreateOpen] = useState(false);
  const [quoteOpen, setQuoteOpen] = useState(false);
  const [compareOpen, setCompareOpen] = useState(false);
  const [selectedRfq, setSelectedRfq] = useState<RFQ | null>(null);

  // Create Form State
  const [title, setTitle] = useState('');
  const [deadline, setDeadline] = useState('');
  const [selectedVendors, setSelectedVendors] = useState<string[]>([]);

  // Quote Form State
  const [quoteVendorId, setQuoteVendorId] = useState('');
  const [leadTime, setLeadTime] = useState(7);
  const [quoteItems, setQuoteItems] = useState([{ description: '', quantity: 1, unit_price: 0 }]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [rfqData, vendorData] = await Promise.all([rfqsApi.list(), vendorsApi.list()]);
      setRfqs(rfqData);
      setVendors(vendorData);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleCreate = async () => {
    try {
      await rfqsApi.create(title, new Date(deadline).toISOString(), selectedVendors);
      setCreateOpen(false);
      setTitle(''); setDeadline(''); setSelectedVendors([]);
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to create RFQ.');
    }
  };

  const handleQuoteSubmit = async () => {
    if (!selectedRfq) return;
    try {
      await rfqsApi.submitQuotation(selectedRfq.id, quoteVendorId, leadTime, quoteItems);
      setQuoteOpen(false);
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to submit quote.');
    }
  };

  const handleAward = async (quotationId: string) => {
    if (!selectedRfq) return;
    if (!window.confirm("Are you sure? This will generate a Purchase Order and reject all other quotes.")) return;
    try {
      await rfqsApi.award(selectedRfq.id, quotationId);
      setCompareOpen(false);
      alert("Awarded successfully! PO Generated.");
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to award quote.');
    }
  };

  const calculateQuoteTotal = () => quoteItems.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Sourcing (RFQs)</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateOpen(true)}>
          Create RFQ
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>RFQ Number</strong></TableCell>
              <TableCell><strong>Title</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell><strong>Invited</strong></TableCell>
              <TableCell><strong>Quotes Received</strong></TableCell>
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rfqs.map((rfq) => (
              <TableRow key={rfq.id}>
                <TableCell>{rfq.rfq_number}</TableCell>
                <TableCell>{rfq.title}</TableCell>
                <TableCell>
                  <Chip label={rfq.status} color={getStatusColor(rfq.status) as any} size="small" />
                </TableCell>
                <TableCell>{rfq.invitations.length}</TableCell>
                <TableCell>{rfq.quotations.length}</TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1}>
                    {(rfq.status === 'PUBLISHED' || rfq.status === 'EVALUATION') && (
                      <Button size="small" variant="outlined" color="info" startIcon={<AssignmentTurnedInIcon />} onClick={() => { setSelectedRfq(rfq); setQuoteOpen(true); }}>
                        Enter Quote
                      </Button>
                    )}
                    {rfq.status === 'EVALUATION' && (
                      <Button size="small" variant="contained" color="secondary" startIcon={<GavelIcon />} onClick={() => { setSelectedRfq(rfq); setCompareOpen(true); }}>
                        Compare & Award
                      </Button>
                    )}
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* CREATE RFQ MODAL */}
      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Create Request for Quotation</DialogTitle>
        <DialogContent dividers>
          <TextField label="RFQ Title" fullWidth margin="dense" value={title} onChange={(e) => setTitle(e.target.value)} />
          <TextField label="Deadline" type="datetime-local" fullWidth margin="dense" InputLabelProps={{ shrink: true }} value={deadline} onChange={(e) => setDeadline(e.target.value)} />
          <TextField
            select fullWidth margin="dense" label="Invite Vendors" SelectProps={{ multiple: true }}
            value={selectedVendors} onChange={(e) => setSelectedVendors(typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value)}
          >
            {vendors.filter(v => v.status === 'ACTIVE').map((v) => (
              <MenuItem key={v.id} value={v.id}>{v.name}</MenuItem>
            ))}
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained" disabled={!title || !deadline || selectedVendors.length === 0}>Publish RFQ</Button>
        </DialogActions>
      </Dialog>

      {/* ENTER QUOTE MODAL */}
      <Dialog open={quoteOpen} onClose={() => setQuoteOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>Simulate Vendor Quotation</DialogTitle>
        <DialogContent dividers>
          <TextField select fullWidth margin="dense" label="Select Vendor" value={quoteVendorId} onChange={(e) => setQuoteVendorId(e.target.value)}>
            {selectedRfq?.invitations.map((inv) => (
              <MenuItem key={inv.vendor_id} value={inv.vendor_id}>{inv.vendor.name}</MenuItem>
            ))}
          </TextField>
          <TextField label="Lead Time (Days)" type="number" fullWidth margin="dense" value={leadTime} onChange={(e) => setLeadTime(Number(e.target.value))} />
          
          <Typography variant="h6" mt={2} mb={1}>Quote Line Items</Typography>
          {quoteItems.map((item, index) => (
            <Grid container spacing={1} key={index} mb={1}>
              <Grid item xs={5}><TextField label="Description" size="small" fullWidth value={item.description} onChange={(e) => { const newItems = [...quoteItems]; newItems[index].description = e.target.value; setQuoteItems(newItems); }} /></Grid>
              <Grid item xs={2}><TextField label="Qty" type="number" size="small" fullWidth value={item.quantity} onChange={(e) => { const newItems = [...quoteItems]; newItems[index].quantity = Number(e.target.value); setQuoteItems(newItems); }} /></Grid>
              <Grid item xs={3}><TextField label="Unit Price" type="number" size="small" fullWidth value={item.unit_price} onChange={(e) => { const newItems = [...quoteItems]; newItems[index].unit_price = Number(e.target.value); setQuoteItems(newItems); }} /></Grid>
              <Grid item xs={2}>
                <IconButton color="error" onClick={() => setQuoteItems(quoteItems.filter((_, i) => i !== index))} disabled={quoteItems.length === 1}><DeleteIcon /></IconButton>
              </Grid>
            </Grid>
          ))}
          <Button startIcon={<AddIcon />} onClick={() => setQuoteItems([...quoteItems, { description: '', quantity: 1, unit_price: 0 }])}>Add Item</Button>
          <Box mt={2} p={2} bgcolor="grey.100" display="flex" justifyContent="space-between">
            <Typography fontWeight="bold">Total Quote Amount:</Typography>
            <Typography fontWeight="bold">${calculateQuoteTotal().toFixed(2)} USD</Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setQuoteOpen(false)}>Cancel</Button>
          <Button onClick={handleQuoteSubmit} variant="contained" disabled={!quoteVendorId}>Submit Quote</Button>
        </DialogActions>
      </Dialog>

      {/* COMPARE & AWARD MODAL */}
      <Dialog open={compareOpen} onClose={() => setCompareOpen(false)} fullWidth maxWidth="lg">
        <DialogTitle>Quote Comparison: {selectedRfq?.rfq_number}</DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={3}>
            {selectedRfq?.quotations.map((quote: Quotation) => (
              <Grid item xs={12} sm={6} md={4} key={quote.id}>
                <Paper elevation={3} sx={{ p: 2, border: quote.status === 'AWARDED' ? '2px solid green' : 'none' }}>
                  <Typography variant="h6">{quote.vendor.name}</Typography>
                  <Typography color="text.secondary" variant="body2">Lead Time: {quote.lead_time_days} days</Typography>
                  <Typography variant="h5" mt={2} mb={2} color={quote.total_amount === Math.min(...selectedRfq.quotations.map(q => Number(q.total_amount))) ? 'success.main' : 'text.primary'}>
                    ${Number(quote.total_amount).toFixed(2)}
                  </Typography>
                  <Chip label={quote.status} color={quote.status === 'AWARDED' ? 'success' : 'default'} size="small" />
                  <Button 
                    fullWidth variant="contained" color="secondary" sx={{ mt: 2 }}
                    disabled={quote.status === 'AWARDED'}
                    onClick={() => handleAward(quote.id)}
                  >
                    Award Contract
                  </Button>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCompareOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}