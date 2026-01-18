import React, { useState } from 'react';
import {
  Container,
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Typography
} from '@mui/material';
import FlightIcon from '@mui/icons-material/Flight';
import SearchForm from './components/SearchForm';
import SearchResults from './components/SearchResults';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#667eea',
    },
    secondary: {
      main: '#764ba2',
    },
    background: {
      default: '#1a1a2e',
      paper: '#16213e',
    },
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
});

function App() {
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (searchParams) => {
    setLoading(true);
    setError(null);
    setSearchResults(null);

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchParams),
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setSearchResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1, minHeight: '100vh', pb: 4 }}>
        <AppBar position="static" elevation={0} sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
          <Toolbar>
            <FlightIcon sx={{ mr: 2, fontSize: 32 }} />
            <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
              Ibn Battuta
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Automated Travel Booking
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 4 }}>
          <SearchForm onSearch={handleSearch} loading={loading} />

          {error && (
            <Box sx={{ mt: 3, p: 3, bgcolor: 'error.dark', borderRadius: 2 }}>
              <Typography color="error.light">
                Error: {error}
              </Typography>
            </Box>
          )}

          {searchResults && (
            <SearchResults results={searchResults} />
          )}
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
