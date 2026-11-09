import { useEffect, useState } from 'react';
import {
  Box, Button, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Chip, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, CircularProgress, Alert
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { vendorsApi } from '../api/vendors';
import type { Vendor } from '../types/vendor';

export function VendorsPage() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal state
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', tax_id: '', contact_email: '' });
  const [submitting, setSubmitting] = useState(false);

  const loadVendors = async () => {
    try {
      setLoading(true);
      const data = await vendorsApi.list();
      setVendors(data);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load vendors.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVendors();
  }, []);

  const handleCreate = async () => {
    try {
      setSubmitting(true);
      await vendorsApi.create(formData);
      setOpen(false);
      setFormData({ name: '', tax_id: '', contact_email: '' });
      loadVendors(); // refresh list
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to create vendor.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Vendors</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpen(true)}>
          Add Vendor
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Name</strong></TableCell>
              <TableCell><strong>Tax ID</strong></TableCell>
              <TableCell><strong>Contact Email</strong></TableCell>
              <TableCell><strong>SAP Number</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {vendors.map((vendor) => (
              <TableRow key={vendor.id}>
                <TableCell>{vendor.name}</TableCell>
                <TableCell>{vendor.tax_id}</TableCell>
                <TableCell>{vendor.contact_email}</TableCell>
                <TableCell>{vendor.sap_vendor_number || '—'}</TableCell>
                <TableCell>
                  <Chip 
                    label={vendor.status} 
                    color={vendor.status === 'ACTIVE' ? 'success' : 'default'} 
                    size="small" 
                  />
                </TableCell>
              </TableRow>
            ))}
            {vendors.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} align="center">No vendors found. Click "Add Vendor" to create one.</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add Vendor Modal */}
      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Add New Vendor</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus margin="dense" label="Vendor Name" fullWidth
            value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})}
          />
          <TextField
            margin="dense" label="Tax ID" fullWidth
            value={formData.tax_id} onChange={(e) => setFormData({...formData, tax_id: e.target.value})}
          />
          <TextField
            margin="dense" label="Contact Email" type="email" fullWidth
            value={formData.contact_email} onChange={(e) => setFormData({...formData, contact_email: e.target.value})}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained" disabled={submitting || !formData.name || !formData.tax_id || !formData.contact_email}>
            {submitting ? 'Saving...' : 'Save Vendor'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}