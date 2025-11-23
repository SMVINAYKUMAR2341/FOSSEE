import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { datasetAPI } from '../services/api';
import Navbar from '../components/Navbar';
import ChartComponent from '../components/ChartComponent';
import AdvancedCharts from '../components/AdvancedCharts';
import MLComparisonCharts from '../components/MLComparisonCharts';
import './Visualization.css';

const Visualization = () => {
  const [searchParams] = useSearchParams();
  const [dataset, setDataset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [predictions, setPredictions] = useState(null);
  const [predictionsLoading, setPredictionsLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDataset();
    fetchPredictions();
  }, [searchParams]);

  const fetchDataset = async () => {
    try {
      const datasetId = searchParams.get('id');
      
      if (datasetId) {
        // Fetch specific dataset
        const response = await datasetAPI.getDatasetDetail(datasetId);
        setDataset(response.data);
      } else {
        // Fetch latest dataset from history
        const historyResponse = await datasetAPI.getHistory();
        if (historyResponse.data.length > 0) {
          setDataset(historyResponse.data[0]);
        } else {
          setError('No datasets available');
        }
      }
    } catch (err) {
      setError('Failed to fetch dataset');
    } finally {
      setLoading(false);
    }
  };

  const fetchPredictions = async () => {
    setPredictionsLoading(true);
    try {
      const response = await datasetAPI.getAllPredictions();
      console.log('Predictions response:', response.data);
      
      if (response.data) {
        setPredictions(response.data.predictions || []);
      } else {
        setPredictions([]);
      }
    } catch (err) {
      console.error('Error fetching predictions:', err);
      setPredictions([]);
    } finally {
      setPredictionsLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    try {
      const response = await datasetAPI.generateReport(dataset.id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `equipment_report_${dataset.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to generate report');
    }
  };

  if (loading) {
    return (
      <div>
        <Navbar />
        <div className="container">
          <div className="loading">Loading visualization...</div>
        </div>
      </div>
    );
  }

  if (error || !dataset) {
    return (
      <div>
        <Navbar />
        <div className="container">
          <div className="error-message">{error || 'No data available'}</div>
          <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Navbar />
      <div className="container">
        <div className="visualization-header">
          <h1>Data Visualization</h1>
          <p>{dataset.filename} - {new Date(dataset.timestamp).toLocaleString()}</p>
        </div>

        <div className="visualization-actions">
          <button className="btn btn-secondary" onClick={handleDownloadReport}>
            📄 Download PDF Report
          </button>
          <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>
            ← Back to Dashboard
          </button>
        </div>

        {/* Summary Cards */}
        <div className="summary-cards">
          <div className="summary-card-item">
            <div className="card-icon">📊</div>
            <div className="card-content">
              <div className="card-label">Total Equipment</div>
              <div className="card-value">{dataset.count}</div>
            </div>
          </div>
          
          <div className="summary-card-item">
            <div className="card-icon">💧</div>
            <div className="card-content">
              <div className="card-label">Avg Flowrate</div>
              <div className="card-value">{dataset.avg_flowrate.toFixed(2)}</div>
            </div>
          </div>
          
          <div className="summary-card-item">
            <div className="card-icon">⚡</div>
            <div className="card-content">
              <div className="card-label">Avg Pressure</div>
              <div className="card-value">{dataset.avg_pressure.toFixed(2)}</div>
            </div>
          </div>
          
          <div className="summary-card-item">
            <div className="card-icon">🌡️</div>
            <div className="card-content">
              <div className="card-label">Avg Temperature</div>
              <div className="card-value">{dataset.avg_temperature.toFixed(2)}</div>
            </div>
          </div>
        </div>

        {/* Parameter Ranges */}
        {dataset.ranges && (
          <div className="ranges-section">
            <h3>📏 Parameter Ranges</h3>
            <div className="ranges-grid">
              <div className="range-card">
                <h4>💧 Flowrate</h4>
                <p>Min: <strong>{dataset.ranges.flowrate.min.toFixed(2)}</strong></p>
                <p>Max: <strong>{dataset.ranges.flowrate.max.toFixed(2)}</strong></p>
                <p>Std Dev: <strong>{dataset.ranges.flowrate.std_dev.toFixed(2)}</strong></p>
              </div>
              <div className="range-card">
                <h4>⚡ Pressure</h4>
                <p>Min: <strong>{dataset.ranges.pressure.min.toFixed(2)}</strong></p>
                <p>Max: <strong>{dataset.ranges.pressure.max.toFixed(2)}</strong></p>
                <p>Std Dev: <strong>{dataset.ranges.pressure.std_dev.toFixed(2)}</strong></p>
              </div>
              <div className="range-card">
                <h4>🌡️ Temperature</h4>
                <p>Min: <strong>{dataset.ranges.temperature.min.toFixed(2)} °C / {((dataset.ranges.temperature.min * 9/5) + 32).toFixed(2)} °F</strong></p>
                <p>Max: <strong>{dataset.ranges.temperature.max.toFixed(2)} °C / {((dataset.ranges.temperature.max * 9/5) + 32).toFixed(2)} °F</strong></p>
                <p>Std Dev: <strong>{dataset.ranges.temperature.std_dev.toFixed(2)} °C / {((dataset.ranges.temperature.std_dev * 9/5)).toFixed(2)} °F</strong></p>
              </div>
            </div>
          </div>
        )}

        {/* Advanced Charts Section */}
        <AdvancedCharts dataset={dataset} />

        {/* ML Model Comparison Charts */}
        {predictions && predictions.length > 0 && dataset?.ml_metrics && (
          <div className="ml-comparison-section">
            <h2>🤖 ML Model Performance Analysis</h2>
            <MLComparisonCharts dataset={dataset} predictions={predictions} />
          </div>
        )}

        {/* Type-wise Breakdown Table */}
        {dataset.type_wise_breakdown && Object.keys(dataset.type_wise_breakdown).length > 0 && (
          <div className="type-wise-section">
            <h3>📋 Type-wise Analysis</h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Equipment Type</th>
                    <th>Count</th>
                    <th>Avg Flowrate</th>
                    <th>Avg Pressure</th>
                    <th>Avg Temp</th>
                    <th>Temp Range</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(dataset.type_wise_breakdown).map(([type, stats]) => (
                    <tr key={type}>
                      <td><strong>{type}</strong></td>
                      <td>{stats.count}</td>
                      <td>{stats.avg_flowrate}</td>
                      <td>{stats.avg_pressure}</td>
                      <td>{stats.avg_temperature} °C / {((stats.avg_temperature * 9/5) + 32).toFixed(1)} °F</td>
                      <td>{stats.min_temperature?.toFixed(1)} - {stats.max_temperature?.toFixed(1)} °C / {((stats.min_temperature * 9/5) + 32).toFixed(1)} - {((stats.max_temperature * 9/5) + 32).toFixed(1)} °F</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ML Training Results */}
        {dataset.ml_metrics && (
          <div className="ml-metrics-section">
            <h3>🤖 Machine Learning Model Training Results</h3>
            <p className="ml-info">
              ✅ Model trained with {dataset.ml_metrics.total_samples || 'N/A'} total samples
              ({dataset.ml_metrics.training_samples || 'N/A'} training, {dataset.ml_metrics.test_samples || 'N/A'} testing)
            </p>
            
            <div className="ml-metrics-grid">
              {/* Flowrate Model */}
              {dataset.ml_metrics.flowrate && (
                <div className="ml-metric-card">
                  <h4>💧 Flowrate Prediction Model</h4>
                  <div className="metric-details">
                    <p>R² Score: <strong className={(dataset.ml_metrics.flowrate?.r2_score ?? 0) > 0.8 ? 'good-score' : 'avg-score'}>
                      {typeof dataset.ml_metrics.flowrate?.r2_score === 'number' ? (dataset.ml_metrics.flowrate.r2_score * 100).toFixed(1) + '%' : 'N/A'}
                    </strong></p>
                    <p>RMSE: <strong>{typeof dataset.ml_metrics.flowrate?.rmse === 'number' ? dataset.ml_metrics.flowrate.rmse.toFixed(2) : 'N/A'}</strong></p>
                    <p>MAE: <strong>{typeof dataset.ml_metrics.flowrate?.mae === 'number' ? dataset.ml_metrics.flowrate.mae.toFixed(2) : 'N/A'}</strong></p>
                  </div>
                </div>
              )}

              {/* Pressure Model */}
              {dataset.ml_metrics.pressure && (
                <div className="ml-metric-card">
                  <h4>⚡ Pressure Prediction Model</h4>
                  <div className="metric-details">
                    <p>R² Score: <strong className={(dataset.ml_metrics.pressure?.r2_score ?? 0) > 0.8 ? 'good-score' : 'avg-score'}>
                      {typeof dataset.ml_metrics.pressure?.r2_score === 'number' ? (dataset.ml_metrics.pressure.r2_score * 100).toFixed(1) + '%' : 'N/A'}
                    </strong></p>
                    <p>RMSE: <strong>{typeof dataset.ml_metrics.pressure?.rmse === 'number' ? dataset.ml_metrics.pressure.rmse.toFixed(2) : 'N/A'}</strong></p>
                    <p>MAE: <strong>{typeof dataset.ml_metrics.pressure?.mae === 'number' ? dataset.ml_metrics.pressure.mae.toFixed(2) : 'N/A'}</strong></p>
                  </div>
                </div>
              )}

              {/* Temperature Model */}
              {dataset.ml_metrics.temperature && (
                <div className="ml-metric-card">
                  <h4>🌡️ Temperature Prediction Model</h4>
                  <div className="metric-details">
                    <p>R² Score: <strong className={(dataset.ml_metrics.temperature?.r2_score ?? 0) > 0.8 ? 'good-score' : 'avg-score'}>
                      {typeof dataset.ml_metrics.temperature?.r2_score === 'number' ? (dataset.ml_metrics.temperature.r2_score * 100).toFixed(1) + '%' : 'N/A'}
                    </strong></p>
                    <p>RMSE: <strong>{typeof dataset.ml_metrics.temperature?.rmse === 'number' ? dataset.ml_metrics.temperature.rmse.toFixed(2) : 'N/A'}</strong></p>
                    <p>MAE: <strong>{typeof dataset.ml_metrics.temperature?.mae === 'number' ? dataset.ml_metrics.temperature.mae.toFixed(2) : 'N/A'}</strong></p>
                  </div>
                </div>
              )}

              {/* Classification Model */}
              {dataset.ml_metrics.classification && (
                <div className="ml-metric-card">
                  <h4>🔧 Equipment Type Classification</h4>
                  <div className="metric-details">
                    <p>Accuracy: <strong className="good-score">
                      {(dataset.ml_metrics.classification.accuracy * 100).toFixed(1)}%
                    </strong></p>
                    <p>Trained on: <strong>{dataset.ml_metrics.equipment_types?.length || 0} types</strong></p>
                  </div>
                </div>
              )}
            </div>

            <div className="ml-info-box">
              <p>
                <strong>📚 About the Models:</strong>
              </p>
              <ul>
                <li>Data preprocessing includes outlier removal (Z-score &lt; 3) and missing value handling</li>
                <li>Random Forest and Gradient Boosting models used for regression</li>
                <li>Random Forest Classifier for equipment type prediction</li>
                <li>Models automatically retrain when new data is uploaded</li>
                <li>R² Score &gt; 80% indicates excellent model performance</li>
              </ul>
            </div>
          </div>
        )}

        {/* Raw Data Table */}
        {dataset.raw_data && dataset.raw_data.length > 0 && (
          <div className="card">
            <h3>Equipment Data Table</h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>S.No.</th>
                    <th>Equipment Name</th>
                    <th>Type</th>
                    <th>Flowrate</th>
                    <th>Pressure</th>
                    <th>Temperature</th>
                  </tr>
                </thead>
                <tbody>
                  {dataset.raw_data.map((row, index) => (
                    <tr key={index}>
                      <td>{index + 1}</td>
                      <td>{row['Equipment Name']}</td>
                      <td>{row['Type']}</td>
                      <td>{row['Flowrate']}</td>
                      <td>{row['Pressure']}</td>
                      <td>{row['Temperature']}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Visualization;
