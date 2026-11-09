import { createTheme } from '@mui/material/styles';

/**
 * Enterprise theme — restrained colors, high contrast, accessible.
 * Blue primary aligns with SAP Fiori Horizon palette for familiarity.
 */
export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#0a6ed1' },
    secondary: { main: '#354a5f' },
    background: { default: '#f5f6f7', paper: '#ffffff' },
  },
  typography: {
    fontFamily: [
      '72',
      'Arial',
      'Helvetica',
      'sans-serif',
    ].join(','),
    h4: { fontWeight: 600 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
  },
  shape: { borderRadius: 8 },
});