import { useContext } from 'react';
import { Box, Card, CardContent, Grid, Typography, Stack, Chip } from '@mui/material';
import { AuthContext } from '../contexts/AuthContext';

export function DashboardPage() {
  const ctx = useContext(AuthContext);
  const user = ctx?.user;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Dashboard</Typography>
      <Typography variant="body1" color="text.secondary" mb={4}>
        Welcome to the Procurement Automation Platform.
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Your Profile</Typography>
              <Typography variant="body2">Email: {user?.email}</Typography>
              <Typography variant="body2">Last Login: {user?.last_login_at ?? '—'}</Typography>
              <Stack direction="row" spacing={1} mt={2}>
                {user?.roles.map((r) => <Chip key={r.id} label={r.name} size="small" />)}
                {user?.is_superuser && <Chip label="SUPERUSER" color="primary" size="small" />}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}