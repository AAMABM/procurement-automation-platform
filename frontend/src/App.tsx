import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { theme } from './theme';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { Layout } from './components/Layout';
import { VendorsPage } from './pages/VendorsPage';
import { RequisitionsPage } from './pages/RequisitionsPage'; // <--- Make sure this is here
import { PurchaseOrdersPage } from './pages/PurchaseOrdersPage';

export function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }>
              <Route index element={<DashboardPage />} />
              <Route path="vendors" element={<VendorsPage />} />
              <Route path="requisitions" element={<RequisitionsPage />} /> {/* <--- Make sure this is here */}
              <Route path="purchase-orders" element={<PurchaseOrdersPage />} />
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
}