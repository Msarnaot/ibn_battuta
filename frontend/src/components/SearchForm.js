import React, { useState } from 'react';
import {
  Paper,
  Grid,
  TextField,
  Button,
  Typography,
  Box,
  Switch,
  FormControlLabel,
  Slider,
  CircularProgress
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { format, addDays } from 'date-fns';

function SearchForm({ onSearch, loading }) {
  const today = format(new Date(), 'yyyy-MM-dd');
  const weekFromNow = format(addDays(new Date(), 7), 'yyyy-MM-dd');
  const tenDaysFromNow = format(addDays(new Date(), 10), 'yyyy-MM-dd');

  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    customer_location: '',
    departure_date: weekFromNow,
    return_date: tenDaysFromNow,
    budget_per_night: 300,
    is_round_trip: true,
  });

  const handleChange = (field) => (event) => {
    const value = event.target.type === 'checkbox'
      ? event.target.checked
      : event.target.value;

    setFormData({
      ...formData,
      [field]: value,
    });
  };

  const handleBudgetChange = (event, newValue) => {
    setFormData({
      ...formData,
      budget_per_night: newValue,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const searchParams = {
      origin: formData.origin,
      destination: formData.destination,
      customer_location: formData.customer_location || formData.destination,
      departure_date: formData.departure_date,
      return_date: formData.is_round_trip ? formData.return_date : null,
      budget_per_night: formData.budget_per_night,
    };

    onSearch(searchParams);
  };

  return (
    <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        Plan Your Business Trip
      </Typography>

      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          {/* Origin and Destination */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Departure City/Airport"
              variant="outlined"
              value={formData.origin}
              onChange={handleChange('origin')}
              required
              placeholder="e.g., Toronto or YYZ"
              helperText="City name or airport code"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Destination City/Airport"
              variant="outlined"
              value={formData.destination}
              onChange={handleChange('destination')}
              required
              placeholder="e.g., London or LHR"
              helperText="City name or airport code"
            />
          </Grid>

          {/* Customer Location */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Customer Location"
              variant="outlined"
              value={formData.customer_location}
              onChange={handleChange('customer_location')}
              placeholder="e.g., Canary Wharf, London"
              helperText="Where will you be visiting your customer? (Leave empty if same as destination)"
            />
          </Grid>

          {/* Dates */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Departure Date"
              type="date"
              variant="outlined"
              value={formData.departure_date}
              onChange={handleChange('departure_date')}
              required
              InputLabelProps={{ shrink: true }}
              inputProps={{ min: today }}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Return Date"
              type="date"
              variant="outlined"
              value={formData.return_date}
              onChange={handleChange('return_date')}
              disabled={!formData.is_round_trip}
              InputLabelProps={{ shrink: true }}
              inputProps={{ min: formData.departure_date }}
            />
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_round_trip}
                  onChange={handleChange('is_round_trip')}
                  color="primary"
                />
              }
              label="Round trip"
            />
          </Grid>

          {/* Budget Slider */}
          <Grid item xs={12}>
            <Typography gutterBottom sx={{ fontWeight: 500 }}>
              Hotel Budget per Night: ${formData.budget_per_night}
            </Typography>
            <Slider
              value={formData.budget_per_night}
              onChange={handleBudgetChange}
              min={100}
              max={1000}
              step={50}
              marks={[
                { value: 100, label: '$100' },
                { value: 300, label: '$300' },
                { value: 500, label: '$500' },
                { value: 1000, label: '$1000' },
              ]}
              valueLabelDisplay="auto"
              color="primary"
            />
          </Grid>

          {/* Submit Button */}
          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              size="large"
              fullWidth
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
              sx={{
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #5568d3 0%, #6a4192 100%)',
                }
              }}
            >
              {loading ? 'Searching...' : 'Search Travel Options'}
            </Button>
          </Grid>
        </Grid>
      </form>

      <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
        <Typography variant="body2" color="text.secondary">
          💡 <strong>Pro tips:</strong>
          <ul style={{ marginTop: '8px', marginLeft: '20px' }}>
            <li>Use airport codes (e.g., YYZ, LHR) for faster results</li>
            <li>We prioritize Aeroplan airlines for your points</li>
            <li>Hotels are selected based on coffee shops, historical areas, and trendy neighborhoods</li>
            <li>Budget includes all your hotel preferences</li>
          </ul>
        </Typography>
      </Box>
    </Paper>
  );
}

export default SearchForm;
