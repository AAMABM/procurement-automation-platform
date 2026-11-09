import { useContext } from 'react';
import {
  AppBar,
  Box,
  Button,
  Container,
  Toolbar,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Stack,
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import { AuthContext } from '../contexts/AuthContext';

export function DashboardPage() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('DashboardPage must be inside AuthProvider');
  const { user, logout } = ctx;

  return (
    <Box minHeight="100vh" bgcolor="grey.50">
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Procurement Platform
          </Typography>
          <Stack direction="row" spacing={2} alignItems="center">
            <Typography variant="body2">{user?.full_name}</Typography>
            <Button onClick={logout} startIcon={<LogoutIcon />} size="small">
              Sign out
            </Button>
          </Stack>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" mb={3}>
          Welcome back, {user?.full_name}. This is Phase 1 — Identity &amp; Foundation.
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Your Account
                </Typography>
                <Typography variant="body2">Email: {user?.email}</Typography>
                <Typography variant="body2">
                  Last login: {user?.last_login_at ?? '—'}
                </Typography>
                <Stack direction="row" spacing={1} mt={2}>
                  {user?.roles.map((r) => (
                    <Chip key={r.id} label={r.name} size="small" />
                  ))}
                  {user?.is_superuser && <Chip label="SUPERUSER" color="primary" size="small" />}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Coming soon
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Purchase Requisitions, RFQs, Purchase Orders, Approvals,
                  Vendors, Invoices, Contracts, and Reporting will be added in
                  subsequent phases.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}