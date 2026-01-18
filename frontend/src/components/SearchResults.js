import React, { useState } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Paper,
  Chip,
  Grid,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import FlightIcon from '@mui/icons-material/Flight';
import HotelIcon from '@mui/icons-material/Hotel';
import RestaurantIcon from '@mui/icons-material/Restaurant';
import AttractionsIcon from '@mui/icons-material/Attractions';
import StarIcon from '@mui/icons-material/Star';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';

function TabPanel({ children, value, index }) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

function SearchResults({ results }) {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const formatDuration = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Box sx={{ mt: 4 }}>
      {/* Summary */}
      <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
          Search Summary
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={6} sm={3}>
            <Typography variant="body2" color="rgba(255,255,255,0.8)">Flights Found</Typography>
            <Typography variant="h4" sx={{ fontWeight: 600 }}>{results.summary.total_flights}</Typography>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Typography variant="body2" color="rgba(255,255,255,0.8)">Hotels Found</Typography>
            <Typography variant="h4" sx={{ fontWeight: 600 }}>{results.summary.total_hotels}</Typography>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Typography variant="body2" color="rgba(255,255,255,0.8)">Restaurants</Typography>
            <Typography variant="h4" sx={{ fontWeight: 600 }}>{results.summary.total_restaurants}</Typography>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Typography variant="body2" color="rgba(255,255,255,0.8)">Activities</Typography>
            <Typography variant="h4" sx={{ fontWeight: 600 }}>{results.summary.total_activities}</Typography>
          </Grid>
        </Grid>

        {/* Car Rental */}
        {results.car_rental && results.car_rental.recommended && (
          <Box sx={{ mt: 3, p: 2, bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 2 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
              <DirectionsCarIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Car Rental Recommended
            </Typography>
            <Typography variant="body2">
              {results.car_rental.reason}
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Tabs */}
      <Paper sx={{ borderRadius: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} variant="fullWidth">
          <Tab icon={<FlightIcon />} label="Flights" />
          <Tab icon={<HotelIcon />} label="Hotels" />
          <Tab icon={<RestaurantIcon />} label="Restaurants" />
          <Tab icon={<AttractionsIcon />} label="Activities" />
        </Tabs>

        {/* Flights Tab */}
        <TabPanel value={tabValue} index={0}>
          {results.flights && results.flights.length > 0 ? (
            <Grid container spacing={2}>
              {results.flights.map((flight, index) => (
                <Grid item xs={12} key={index}>
                  <Card variant="outlined" sx={{ '&:hover': { boxShadow: 3 } }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Box>
                          <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            {flight.flight_numbers.join(', ')}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {flight.carriers.join(', ')}
                          </Typography>
                        </Box>
                        <Box sx={{ textAlign: 'right' }}>
                          <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
                            ${flight.price.toFixed(2)}
                          </Typography>
                          <Chip
                            label={`Score: ${Math.round(flight.score)}/100`}
                            size="small"
                            color="primary"
                            sx={{ mt: 0.5 }}
                          />
                        </Box>
                      </Box>

                      <Grid container spacing={2} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="text.secondary">Departure</Typography>
                          <Typography variant="body1">{formatDateTime(flight.departure_time)}</Typography>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="text.secondary">Arrival</Typography>
                          <Typography variant="body1">{formatDateTime(flight.arrival_time)}</Typography>
                        </Grid>
                      </Grid>

                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                        <Chip
                          icon={<AccessTimeIcon />}
                          label={formatDuration(flight.duration_minutes)}
                          size="small"
                          variant="outlined"
                        />
                        <Chip
                          label={flight.cabin_class}
                          size="small"
                          variant="outlined"
                          color={flight.cabin_class === 'BUSINESS' ? 'primary' : 'default'}
                        />
                        {flight.is_nonstop && (
                          <Chip label="Non-stop" size="small" color="success" />
                        )}
                        {flight.is_aeroplan_friendly && (
                          <Chip label="✈️ Aeroplan Points" size="small" color="secondary" />
                        )}
                      </Box>

                      <Typography variant="body2" color="primary.main" sx={{ fontWeight: 500 }}>
                        💡 {flight.recommendation}
                      </Typography>

                      {flight.upgrade_recommendation && (
                        <Box sx={{ mt: 2, p: 2, bgcolor: 'secondary.dark', borderRadius: 1 }}>
                          <Typography variant="body2">
                            {flight.upgrade_recommendation}
                          </Typography>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Typography variant="body1" color="text.secondary" align="center" sx={{ py: 4 }}>
              No flights found matching your criteria.
            </Typography>
          )}
        </TabPanel>

        {/* Hotels Tab */}
        <TabPanel value={tabValue} index={1}>
          {results.hotels && results.hotels.length > 0 ? (
            <Grid container spacing={2}>
              {results.hotels.map((hotel, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card variant="outlined" sx={{ height: '100%', '&:hover': { boxShadow: 3 } }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Typography variant="h6" sx={{ fontWeight: 600, flex: 1 }}>
                          {hotel.name}
                        </Typography>
                        <Chip
                          label={`${Math.round(hotel.score)}/100`}
                          size="small"
                          color="primary"
                        />
                      </Box>

                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <StarIcon sx={{ color: '#FFD700', fontSize: 18 }} />
                        <Typography variant="body1" sx={{ ml: 0.5, fontWeight: 500 }}>
                          {hotel.rating.toFixed(1)}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                          ({hotel.num_reviews} reviews)
                        </Typography>
                      </Box>

                      {hotel.price_level > 0 && (
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          {'$'.repeat(hotel.price_level)}
                        </Typography>
                      )}

                      {hotel.customer_distance_km !== undefined && (
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          📍 {hotel.customer_distance_km.toFixed(1)} km from customer
                        </Typography>
                      )}

                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {hotel.address}
                      </Typography>

                      <Divider sx={{ my: 2 }} />

                      <Typography variant="body2" color="primary.main" sx={{ fontWeight: 500 }}>
                        {hotel.recommendation}
                      </Typography>

                      {hotel.website && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="caption" color="text.secondary">
                            <a
                              href={hotel.website}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{ color: 'inherit' }}
                            >
                              View website →
                            </a>
                          </Typography>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Typography variant="body1" color="text.secondary" align="center" sx={{ py: 4 }}>
              No hotels found matching your criteria.
            </Typography>
          )}
        </TabPanel>

        {/* Restaurants Tab */}
        <TabPanel value={tabValue} index={2}>
          {results.restaurants && results.restaurants.length > 0 ? (
            <Grid container spacing={2}>
              {results.restaurants.map((restaurant, index) => (
                <Grid item xs={12} sm={6} key={index}>
                  <Card variant="outlined" sx={{ height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                        {restaurant.name}
                      </Typography>

                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <StarIcon sx={{ color: '#FFD700', fontSize: 16 }} />
                        <Typography variant="body2" sx={{ ml: 0.5 }}>
                          {restaurant.rating.toFixed(1)} ({restaurant.num_reviews} reviews)
                        </Typography>
                      </Box>

                      {restaurant.price_level > 0 && (
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          {'$'.repeat(restaurant.price_level)}
                        </Typography>
                      )}

                      {restaurant.distance_km < 900 && (
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          📍 {restaurant.distance_km.toFixed(1)} km from hotel
                        </Typography>
                      )}

                      {restaurant.summary && (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                          {restaurant.summary}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Typography variant="body1" color="text.secondary" align="center" sx={{ py: 4 }}>
              No restaurants found.
            </Typography>
          )}
        </TabPanel>

        {/* Activities Tab */}
        <TabPanel value={tabValue} index={3}>
          {results.activities && results.activities.length > 0 ? (
            <Grid container spacing={2}>
              {results.activities.map((activity, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Card variant="outlined" sx={{ height: '100%' }}>
                    <CardContent>
                      <Chip
                        label={activity.category}
                        size="small"
                        sx={{ mb: 1 }}
                      />

                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                        {activity.name}
                      </Typography>

                      {activity.rating > 0 && (
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <StarIcon sx={{ color: '#FFD700', fontSize: 16 }} />
                          <Typography variant="body2" sx={{ ml: 0.5 }}>
                            {activity.rating.toFixed(1)}
                          </Typography>
                        </Box>
                      )}

                      {activity.distance_km < 900 && (
                        <Typography variant="body2" color="text.secondary">
                          📍 {activity.distance_km.toFixed(1)} km from hotel
                        </Typography>
                      )}

                      {activity.summary && (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                          {activity.summary}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Typography variant="body1" color="text.secondary" align="center" sx={{ py: 4 }}>
              No activities found.
            </Typography>
          )}
        </TabPanel>
      </Paper>
    </Box>
  );
}

export default SearchResults;
