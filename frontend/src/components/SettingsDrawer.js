import React, { useState, useEffect } from 'react';
import {
  Drawer,
  Box,
  Typography,
  IconButton,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Alert,
  Snackbar,
  Divider,
  Paper,
  Grid
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import FavoriteIcon from '@mui/icons-material/Favorite';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import AddIcon from '@mui/icons-material/Add';
import PlaceIcon from '@mui/icons-material/Place';

function TabPanel({ children, value, index }) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function SettingsDrawer({ open, onClose }) {
  const [tabValue, setTabValue] = useState(0);
  const [favorites, setFavorites] = useState([]);
  const [savedPlaces, setSavedPlaces] = useState([]);
  const [editDialog, setEditDialog] = useState({ open: false, hotel: null });
  const [addPlaceDialog, setAddPlaceDialog] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Load favorites
  const loadFavorites = async () => {
    try {
      const response = await fetch('/api/favorites');
      const data = await response.json();
      if (data.success) {
        setFavorites(data.favorites);
      }
    } catch (error) {
      console.error('Error loading favorites:', error);
    }
  };

  // Load saved places
  const loadSavedPlaces = async () => {
    try {
      const response = await fetch('/api/saved-places');
      const data = await response.json();
      if (data.success) {
        setSavedPlaces(data.saved_places);
      }
    } catch (error) {
      console.error('Error loading saved places:', error);
    }
  };

  useEffect(() => {
    if (open) {
      loadFavorites();
      loadSavedPlaces();
    }
  }, [open]);

  // Delete favorite
  const handleDeleteFavorite = async (placeId, name) => {
    try {
      const response = await fetch(`/api/favorites/${placeId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setFavorites(favorites.filter(f => f.place_id !== placeId));
        setSnackbar({
          open: true,
          message: `Removed ${name} from favorites`,
          severity: 'success'
        });
      }
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Error removing favorite',
        severity: 'error'
      });
    }
  };

  // Update notes
  const handleSaveNotes = async () => {
    try {
      const response = await fetch(`/api/favorites/${editDialog.hotel.place_id}/notes`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes: editDialog.notes })
      });

      if (response.ok) {
        // Update local state
        setFavorites(favorites.map(f =>
          f.place_id === editDialog.hotel.place_id
            ? { ...f, notes: editDialog.notes }
            : f
        ));
        setEditDialog({ open: false, hotel: null });
        setSnackbar({
          open: true,
          message: 'Notes updated',
          severity: 'success'
        });
      }
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Error updating notes',
        severity: 'error'
      });
    }
  };

  // Upload saved places file
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      const text = await file.text();
      const places = JSON.parse(text);

      // Validate format
      if (!Array.isArray(places)) {
        throw new Error('File must contain an array of places');
      }

      const response = await fetch('/api/saved-places', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ places })
      });

      const data = await response.json();

      if (data.success) {
        loadSavedPlaces();
        setSnackbar({
          open: true,
          message: `Added ${data.total} saved places!`,
          severity: 'success'
        });
      }
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Error uploading file. Make sure it\'s valid JSON.',
        severity: 'error'
      });
    }
  };

  // Add place manually
  const handleAddPlace = async (placeData) => {
    try {
      const response = await fetch('/api/saved-places', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ places: [placeData] })
      });

      const data = await response.json();

      if (data.success) {
        loadSavedPlaces();
        setAddPlaceDialog(false);
        setSnackbar({
          open: true,
          message: 'Saved place added!',
          severity: 'success'
        });
      }
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Error adding place',
        severity: 'error'
      });
    }
  };

  return (
    <>
      <Drawer
        anchor="right"
        open={open}
        onClose={onClose}
        sx={{ '& .MuiDrawer-paper': { width: { xs: '100%', sm: 500 } } }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Settings & Favorites
          </Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>

        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} variant="fullWidth">
          <Tab icon={<FavoriteIcon />} label="Favorites" />
          <Tab icon={<PlaceIcon />} label="Saved Places" />
        </Tabs>

        {/* Favorites Tab */}
        <TabPanel value={tabValue} index={0}>
          {favorites.length === 0 ? (
            <Alert severity="info">
              No favorite hotels yet. Click the ❤️ icon on any hotel to save it!
            </Alert>
          ) : (
            <>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {favorites.length} favorite hotel{favorites.length !== 1 ? 's' : ''}
              </Typography>

              <List>
                {favorites.map((hotel) => (
                  <Paper key={hotel.place_id} sx={{ mb: 2, p: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          {hotel.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {hotel.city}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {hotel.address}
                        </Typography>

                        {hotel.notes && (
                          <Box sx={{ mt: 1, p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                            <Typography variant="caption">
                              📝 {hotel.notes}
                            </Typography>
                          </Box>
                        )}

                        <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                          <IconButton
                            size="small"
                            onClick={() => setEditDialog({ open: true, hotel, notes: hotel.notes || '' })}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeleteFavorite(hotel.place_id, hotel.name)}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      </Box>
                    </Box>
                  </Paper>
                ))}
              </List>
            </>
          )}
        </TabPanel>

        {/* Saved Places Tab */}
        <TabPanel value={tabValue} index={1}>
          <Alert severity="info" sx={{ mb: 2 }}>
            Import your favorite coffee shops and restaurants. Hotels near them will rank higher!
          </Alert>

          {/* Upload Section */}
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Upload from Google Maps
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
              Export from <a href="https://takeout.google.com/" target="_blank" rel="noopener noreferrer">Google Takeout</a> → Select "Maps (your places)" → Upload the JSON file
            </Typography>

            <Button
              variant="outlined"
              component="label"
              startIcon={<CloudUploadIcon />}
              fullWidth
            >
              Upload JSON File
              <input
                type="file"
                hidden
                accept=".json"
                onChange={handleFileUpload}
              />
            </Button>
          </Paper>

          <Divider sx={{ my: 2 }}>OR</Divider>

          {/* Manual Add Section */}
          <Paper sx={{ p: 2, mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              fullWidth
              onClick={() => setAddPlaceDialog(true)}
            >
              Add Place Manually
            </Button>
          </Paper>

          {/* List of saved places */}
          {savedPlaces.length > 0 && (
            <>
              <Typography variant="subtitle2" sx={{ mt: 3, mb: 1 }}>
                Your Saved Places ({savedPlaces.length})
              </Typography>

              <List sx={{ maxHeight: 300, overflow: 'auto' }}>
                {savedPlaces.slice(0, 50).map((place, index) => (
                  <ListItem key={index} dense>
                    <ListItemText
                      primary={place.name}
                      secondary={`${place.city || place.address} • ${place.category || place.type}`}
                    />
                  </ListItem>
                ))}
                {savedPlaces.length > 50 && (
                  <Typography variant="caption" color="text.secondary" sx={{ p: 2 }}>
                    ... and {savedPlaces.length - 50} more
                  </Typography>
                )}
              </List>
            </>
          )}
        </TabPanel>
      </Drawer>

      {/* Edit Notes Dialog */}
      <Dialog open={editDialog.open} onClose={() => setEditDialog({ open: false, hotel: null })} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Notes</DialogTitle>
        <DialogContent>
          <Typography variant="subtitle2" gutterBottom>
            {editDialog.hotel?.name}
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Notes"
            value={editDialog.notes || ''}
            onChange={(e) => setEditDialog({ ...editDialog, notes: e.target.value })}
            placeholder="e.g., Room 302 has best view, ask for late checkout"
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog({ open: false, hotel: null })}>Cancel</Button>
          <Button onClick={handleSaveNotes} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>

      {/* Add Place Dialog */}
      <AddPlaceDialog
        open={addPlaceDialog}
        onClose={() => setAddPlaceDialog(false)}
        onAdd={handleAddPlace}
      />

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
}

function AddPlaceDialog({ open, onClose, onAdd }) {
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    type: 'cafe',
    lat: '',
    lng: ''
  });

  const handleSubmit = () => {
    if (!formData.name || !formData.address || !formData.lat || !formData.lng) {
      return;
    }

    onAdd({
      name: formData.name,
      address: formData.address,
      type: formData.type,
      coordinates: {
        lat: parseFloat(formData.lat),
        lng: parseFloat(formData.lng)
      }
    });

    // Reset form
    setFormData({
      name: '',
      address: '',
      type: 'cafe',
      lat: '',
      lng: ''
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Add Saved Place</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Blue Bottle Coffee"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Address"
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              placeholder="e.g., 66 Mint St, San Francisco, CA"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              select
              label="Type"
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              SelectProps={{ native: true }}
            >
              <option value="cafe">Cafe / Coffee Shop</option>
              <option value="restaurant">Restaurant</option>
              <option value="bar">Bar / Nightlife</option>
              <option value="museum">Museum</option>
              <option value="culture">Cultural Attraction</option>
              <option value="other">Other</option>
            </TextField>
          </Grid>

          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Latitude"
              type="number"
              value={formData.lat}
              onChange={(e) => setFormData({ ...formData, lat: e.target.value })}
              placeholder="37.7749"
              inputProps={{ step: 'any' }}
            />
          </Grid>

          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Longitude"
              type="number"
              value={formData.lng}
              onChange={(e) => setFormData({ ...formData, lng: e.target.value })}
              placeholder="-122.4194"
              inputProps={{ step: 'any' }}
            />
          </Grid>

          <Grid item xs={12}>
            <Alert severity="info" sx={{ fontSize: '0.75rem' }}>
              💡 Tip: Find coordinates on Google Maps → Right-click location → Click the coordinates
            </Alert>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained">Add Place</Button>
      </DialogActions>
    </Dialog>
  );
}

export default SettingsDrawer;
