import React, { useEffect, useState } from 'react';
import { Button, TextField, Card, Typography } from '@mui/material';
import api from '../services/api';

const UserProfile = () => {
  const [user, setUser] = useState(null);
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    api.get('/user/')
      .then(res => setUser(res.data))
      .catch(() => setMessage('Failed to load user info'));
  }, []);

  const handleChangePassword = () => {
    if (newPassword !== confirmPassword) {
      setMessage('New passwords do not match');
      return;
    }
    api.post('/change-password/', {
      old_password: oldPassword,
      new_password: newPassword
    })
      .then(() => {
        setMessage('Password changed successfully');
        setShowChangePassword(false);
        setOldPassword('');
        setNewPassword('');
        setConfirmPassword('');
      })
      .catch(() => setMessage('Failed to change password'));
  };

  return (
    <Card style={{ maxWidth: 400, margin: '2rem auto', padding: '2rem' }}>
      <Typography variant="h5" gutterBottom>User Profile</Typography>
      {user ? (
        <>
          <Typography variant="body1"><b>Username:</b> {user.username}</Typography>
          <Typography variant="body1"><b>Email:</b> {user.email}</Typography>
          <Button variant="contained" color="primary" style={{ marginTop: 16 }} onClick={() => setShowChangePassword(!showChangePassword)}>
            Change Password
          </Button>
          {showChangePassword && (
            <div style={{ marginTop: 16 }}>
              <TextField label="Old Password" type="password" fullWidth margin="normal" value={oldPassword} onChange={e => setOldPassword(e.target.value)} />
              <TextField label="New Password" type="password" fullWidth margin="normal" value={newPassword} onChange={e => setNewPassword(e.target.value)} />
              <TextField label="Confirm New Password" type="password" fullWidth margin="normal" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} />
              <Button variant="contained" color="secondary" onClick={handleChangePassword} style={{ marginTop: 8 }}>Submit</Button>
            </div>
          )}
        </>
      ) : (
        <Typography>Loading...</Typography>
      )}
      {message && <Typography color="error" style={{ marginTop: 16 }}>{message}</Typography>}
    </Card>
  );
};

export default UserProfile;
