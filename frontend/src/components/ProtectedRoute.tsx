import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const ctx = useContext(AuthContext);
  const location = useLocation();

  if (!ctx) throw new Error('ProtectedRoute must be inside AuthProvider');
  if (ctx.loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }
  if (!ctx.user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return <>{children}</>;
}