import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { datasetAPI } from '../services/api';
import Navbar from '../components/Navbar';
import './Upload.css';
import { 
  CloudUpload, 
  CheckCircle, 
  TrendingUp, 
  Database, 
  Cpu, 
  Activity,
  BarChart3,
  Zap,
  Droplets,
  Thermometer
} from 'lucide-react';

const Upload = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [summary, setSummary] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.csv')) {
        setError('Please select a CSV file');
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError('');
      setSuccess('');
      setSummary(null);
    }
  };

  const handleLoadSample = async () => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      // Fetch the sample CSV from public folder
      const response = await fetch('/sample_equipment_data.csv');
      const blob = await response.blob();
      const file = new File([blob], 'sample_equipment_data.csv', { type: 'text/csv' });
      
      setFile(file);
      setSuccess('✅ Sample data loaded! Click "Upload and Process" to continue.');
    } catch (err) {
      setError('Failed to load sample data. Make sure sample_equipment_data.csv is in the public folder.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await datasetAPI.uploadCSV(file);
      setSummary(response.data);
      setSuccess('CSV uploaded and processed successfully!');
      setFile(null);
      // Reset file input
      document.getElementById('csvFile').value = '';
    } catch (err) {
      console.error('Upload error:', err);
      let errorMessage = 'Failed to upload CSV file';
      
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        errorMessage = 'Upload timed out. The file might be too large or the ML training is taking too long. Please try again.';
      } else if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-page">
      <Navbar />
      <div className="upload-container">
        <div className="upload-hero">
          <div className="hero-icon-wrapper">
            <CloudUpload className="hero-icon" size={64} />
            <div className="icon-glow"></div>
          </div>
          <h1 className="hero-title">Upload Chemical Equipment Dataset</h1>
          <p className="hero-subtitle">Upload your CSV data and watch AI-powered analysis happen in real-time</p>
        </div>

        <div className="upload-card glass-effect">
          <div className="card-header">
            <Database size={28} />
            <h2>CSV File Upload</h2>
          </div>
          
          {error && (
            <div className="alert alert-error">
              <div className="alert-icon">⚠️</div>
              <div className="alert-content">{error}</div>
            </div>
          )}
          
          {success && (
            <div className="alert alert-success">
              <div className="alert-icon">✓</div>
              <div className="alert-content">{success}</div>
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="file-upload-area">
              <input
                type="file"
                id="csvFile"
                accept=".csv"
                onChange={handleFileChange}
                disabled={loading}
                className="file-input-hidden"
              />
              <label htmlFor="csvFile" className={`file-upload-label ${file ? 'has-file' : ''}`}>
                <div className="upload-icon-wrapper">
                  <CloudUpload size={48} className="upload-icon" />
                </div>
                <div className="upload-text">
                  <p className="upload-main-text">
                    {file ? file.name : 'Click to browse or drag and drop'}
                  </p>
                  <p className="upload-sub-text">
                    CSV files only • Max 10MB
                  </p>
                </div>
                {file && <CheckCircle className="check-icon" size={32} />}
              </label>
              
              <div className="file-requirements">
                <p className="requirements-title">📋 Required Columns:</p>
                <div className="requirements-tags">
                  <span className="tag">Equipment Name</span>
                  <span className="tag">Type</span>
                  <span className="tag">Flowrate</span>
                  <span className="tag">Pressure</span>
                  <span className="tag">Temperature</span>
                </div>
              </div>
            </div>
            
            <div className="action-buttons">
              <button type="submit" className="btn btn-primary btn-large" disabled={!file || loading}>
                {loading ? (
                  <>
                    <Activity className="btn-icon spin" size={20} />
                    Processing...
                  </>
                ) : (
                  <>
                    <TrendingUp className="btn-icon" size={20} />
                    Upload & Analyze
                  </>
                )}
              </button>
              <button 
                type="button" 
                className="btn btn-secondary btn-large" 
                onClick={handleLoadSample}
                disabled={loading}
              >
                <BarChart3 className="btn-icon" size={20} />
                Load Sample Data
              </button>
            </div>
          </form>
        </div>

        {summary && (
          <div className="results-section">
            <div className="section-header">
              <h2 className="section-title">
                <Activity size={32} className="title-icon" />
                Analysis Results
              </h2>
              <div className="success-badge">
                <CheckCircle size={20} />
                <span>Successfully Processed</span>
              </div>
            </div>

            {/* Key Metrics Cards */}
            <div className="metrics-showcase">
              <div className="metric-card metric-primary">
                <div className="metric-icon-wrapper">
                  <Database size={32} />
                </div>
                <div className="metric-content">
                  <p className="metric-label">Total Equipment</p>
                  <p className="metric-value">{summary.count}</p>
                </div>
                <div className="metric-trend">
                  <TrendingUp size={20} />
                </div>
              </div>

              <div className="metric-card metric-success">
                <div className="metric-icon-wrapper">
                  <Cpu size={32} />
                </div>
                <div className="metric-content">
                  <p className="metric-label">Equipment Types</p>
                  <p className="metric-value">{summary.equipment_types_count || Object.keys(summary.type_distribution).length}</p>
                </div>
                <div className="metric-trend">
                  <CheckCircle size={20} />
                </div>
              </div>

              <div className="metric-card metric-info">
                <div className="metric-icon-wrapper">
                  <Droplets size={32} />
                </div>
                <div className="metric-content">
                  <p className="metric-label">Avg Flowrate</p>
                  <p className="metric-value">{summary.avg_flowrate.toFixed(1)}</p>
                  <p className="metric-unit">L/min</p>
                </div>
              </div>

              <div className="metric-card metric-warning">
                <div className="metric-icon-wrapper">
                  <Zap size={32} />
                </div>
                <div className="metric-content">
                  <p className="metric-label">Avg Pressure</p>
                  <p className="metric-value">{summary.avg_pressure.toFixed(1)}</p>
                  <p className="metric-unit">PSI</p>
                </div>
              </div>

              <div className="metric-card metric-danger">
                <div className="metric-icon-wrapper">
                  <Thermometer size={32} />
                </div>
                <div className="metric-content">
                  <p className="metric-label">Avg Temperature</p>
                  <p className="metric-value">
                    {summary.avg_temperature.toFixed(1)}
                    <span className="metric-unit">°C</span>
                    {' / '}
                    {((summary.avg_temperature * 9/5) + 32).toFixed(1)}
                    <span className="metric-unit">°F</span>
                  </p>
                </div>
              </div>
            </div>

            {summary.ml_trained && (
              <div className="ml-success-message">
                <p className="ml-info">
                  ✅ Machine Learning model trained successfully with {summary.ml_metrics?.total_samples || 0} samples.
                  View detailed analysis and metrics in the Visualization tab.
                </p>
              </div>
            )}

            <div className="summary-actions">
              <button 
                className="btn btn-primary" 
                onClick={() => navigate(`/visualization?id=${summary.id}`)}
              >
                📊 View Detailed Visualization
              </button>
              <button 
                className="btn btn-secondary" 
                onClick={() => navigate('/dashboard')}
              >
                ← Back to Dashboard
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Upload;
