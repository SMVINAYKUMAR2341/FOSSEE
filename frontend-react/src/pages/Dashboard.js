import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { datasetAPI } from '../services/api';
import Navbar from '../components/Navbar';
import './Dashboard.css';

const Dashboard = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await datasetAPI.getHistory();
      setHistory(response.data);
    } catch (err) {
      setError('Failed to fetch dataset history');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async (datasetId) => {
    try {
      const response = await datasetAPI.generateReport(datasetId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `equipment_report_${datasetId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to generate report');
    }
  };

  const handleViewVisualization = (datasetId) => {
    navigate(`/visualization?id=${datasetId}`);
  };

  const handleQuickUploadSample = async () => {
    try {
      // Fetch and upload sample data in one click
      const response = await fetch('/sample_equipment_data.csv');
      const blob = await response.blob();
      const file = new File([blob], 'sample_equipment_data.csv', { type: 'text/csv' });
      
      await datasetAPI.uploadCSV(file);
      
      // Refresh history
      fetchHistory();
      
      // Show success message
      alert('✅ Sample data uploaded successfully! View it in the history below.');
    } catch (err) {
      alert('Failed to upload sample data: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleDeleteDataset = async (datasetId) => {
    if (!window.confirm('Are you sure you want to delete this dataset?')) return;
    try {
      await datasetAPI.deleteDataset(datasetId);
      setHistory(history.filter(ds => ds.id !== datasetId));
      alert('Dataset deleted successfully!');
    } catch (err) {
      alert('Failed to delete dataset');
    }
  };

  return (
    <div>
      <Navbar />
      <div className="container">
        <div className="dashboard-header">
          <h1>Welcome, {user?.username}!</h1>
          <p>Manage your chemical equipment datasets</p>
        </div>

        <div className="dashboard-actions">
          <button className="btn btn-primary" onClick={() => navigate('/upload')}>
            📤 Upload New CSV
          </button>
          <button className="btn btn-secondary" onClick={handleQuickUploadSample}>
            ⚡ Quick Upload Sample
          </button>
          {history.length > 0 && (
            <button className="btn btn-secondary" onClick={() => navigate('/visualization')}>
              📊 View Latest Visualization
            </button>
          )}
        </div>

        <div className="card">
          <h2>Dataset History (Last 5 Uploads)</h2>
          <p className="help-text">📊 Each row shows the <strong>Data Summary API</strong> response: count, averages (flowrate, pressure, temperature), and type distribution</p>
          
          {loading && <div className="loading">Loading...</div>}
          {error && <div className="error-message">{error}</div>}
          
          {!loading && history.length === 0 && (
            <p className="no-data">No datasets uploaded yet. Upload a CSV to get started!</p>
          )}
          
          {!loading && history.length > 0 && (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Filename</th>
                    <th>Upload Date</th>
                    <th>Equipment Count</th>
                    <th>Equipment Types</th>
                    <th>Avg Flowrate</th>
                    <th>Avg Pressure</th>
                    <th>Avg Temperature</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((dataset) => (
                    <tr key={dataset.id}>
                      <td>{dataset.filename}</td>
                      <td>{new Date(dataset.timestamp).toLocaleString()}</td>
                      <td>{dataset.count}</td>
                      <td>{dataset.equipment_types_count || Object.keys(dataset.type_distribution || {}).length}</td>
                      <td>{dataset.avg_flowrate.toFixed(2)}</td>
                      <td>{dataset.avg_pressure.toFixed(2)}</td>
                      <td>{dataset.avg_temperature.toFixed(2)} °C / {((dataset.avg_temperature * 9/5) + 32).toFixed(2)} °F</td>
                      <td>
                        <button 
                          className="btn-small btn-primary"
                          onClick={() => handleViewVisualization(dataset.id)}
                        >
                          View
                        </button>
                        <button 
                          className="btn-small btn-secondary"
                          onClick={() => handleDownloadReport(dataset.id)}
                        >
                          PDF
                        </button>
                        <button 
                          className="btn-small btn-danger"
                          onClick={() => handleDeleteDataset(dataset.id)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
