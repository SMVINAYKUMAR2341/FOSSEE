import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const MLComparisonCharts = ({ dataset, predictions }) => {
  if (!dataset || !predictions || predictions.length === 0) {
    return null;
  }

  // Extract ML metrics
  const mlMetrics = dataset.ml_metrics || {};
  const hasMLMetrics = mlMetrics && (mlMetrics.flowrate || mlMetrics.pressure || mlMetrics.temperature);

  if (!hasMLMetrics) {
    return null;
  }

  // 1. Model Accuracy Comparison (R² Scores)
  const accuracyData = {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [
      {
        label: 'R² Score (%)',
        data: [
          (mlMetrics.flowrate?.r2_score || 0) * 100,
          (mlMetrics.pressure?.r2_score || 0) * 100,
          (mlMetrics.temperature?.r2_score || 0) * 100,
        ],
        backgroundColor: [
          'rgba(54, 162, 235, 0.7)',
          'rgba(255, 99, 132, 0.7)',
          'rgba(75, 192, 192, 0.7)',
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(255, 99, 132, 1)',
          'rgba(75, 192, 192, 1)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const accuracyOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: true, text: 'ML Model Accuracy (R² Score)' },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: { display: true, text: 'Accuracy (%)' },
      },
    },
  };

  // 2. Error Metrics Comparison (MSE & MAE)
  const errorMetricsData = {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [
      {
        label: 'MSE',
        data: [
          mlMetrics.flowrate?.mse || 0,
          mlMetrics.pressure?.mse || 0,
          mlMetrics.temperature?.mse || 0,
        ],
        backgroundColor: 'rgba(255, 159, 64, 0.6)',
        borderColor: 'rgba(255, 159, 64, 1)',
        borderWidth: 2,
      },
      {
        label: 'MAE',
        data: [
          mlMetrics.flowrate?.mae || 0,
          mlMetrics.pressure?.mae || 0,
          mlMetrics.temperature?.mae || 0,
        ],
        backgroundColor: 'rgba(153, 102, 255, 0.6)',
        borderColor: 'rgba(153, 102, 255, 1)',
        borderWidth: 2,
      },
    ],
  };

  const errorMetricsOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Model Error Metrics (MSE vs MAE)' },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'Error Value' },
      },
    },
  };

  // 3. Predicted vs Actual Comparison (using type-wise averages)
  const typeWiseBreakdown = dataset.type_wise_breakdown || {};
  
  // Create a map of predictions by equipment type for easy lookup
  const predictionMap = {};
  predictions.forEach(p => {
    predictionMap[p.equipment_type] = p;
  });
  
  // Get equipment types that have both actual data and predictions
  const equipmentTypes = Object.keys(typeWiseBreakdown).filter(type => predictionMap[type]);
  
  // Build aligned arrays
  const actualAvgFlowrate = [];
  const actualAvgPressure = [];
  const actualAvgTemperature = [];
  const predictedFlowrate = [];
  const predictedPressure = [];
  const predictedTemperature = [];
  
  equipmentTypes.forEach(type => {
    actualAvgFlowrate.push(typeWiseBreakdown[type].avg_flowrate);
    actualAvgPressure.push(typeWiseBreakdown[type].avg_pressure);
    actualAvgTemperature.push(typeWiseBreakdown[type].avg_temperature);
    
    const pred = predictionMap[type];
    predictedFlowrate.push(pred.predicted_flowrate);
    predictedPressure.push(pred.predicted_pressure);
    predictedTemperature.push(pred.predicted_temperature);
  });

  const flowrateComparisonData = {
    labels: equipmentTypes,
    datasets: [
      {
        label: 'Actual Avg Flowrate',
        data: actualAvgFlowrate,
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
      },
      {
        label: 'Predicted Flowrate',
        data: predictedFlowrate,
        backgroundColor: 'rgba(255, 206, 86, 0.5)',
        borderColor: 'rgba(255, 206, 86, 1)',
        borderWidth: 2,
      },
    ],
  };

  const flowrateComparisonOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Flowrate: Actual vs Predicted' },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'Flowrate' },
      },
    },
  };

  const pressureComparisonData = {
    labels: equipmentTypes,
    datasets: [
      {
        label: 'Actual Avg Pressure',
        data: actualAvgPressure,
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 2,
      },
      {
        label: 'Predicted Pressure',
        data: predictedPressure,
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 2,
      },
    ],
  };

  const pressureComparisonOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Pressure: Actual vs Predicted' },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'Pressure' },
      },
    },
  };

  const temperatureComparisonData = {
    labels: equipmentTypes,
    datasets: [
      {
        label: 'Actual Avg Temperature',
        data: actualAvgTemperature,
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 2,
      },
      {
        label: 'Predicted Temperature',
        data: predictedTemperature,
        backgroundColor: 'rgba(255, 159, 64, 0.5)',
        borderColor: 'rgba(255, 159, 64, 1)',
        borderWidth: 2,
      },
    ],
  };

  const temperatureComparisonOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Temperature: Actual vs Predicted' },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'Temperature (°C)' },
      },
    },
  };

  // 4. Prediction Accuracy Line Chart
  const predictionAccuracyData = {
    labels: equipmentTypes,
    datasets: [
      {
        label: 'Flowrate Accuracy',
        data: equipmentTypes.map((type, i) => {
          const actual = actualAvgFlowrate[i];
          const predicted = predictedFlowrate[i];
          return actual > 0 ? ((1 - Math.abs(actual - predicted) / actual) * 100).toFixed(2) : 0;
        }),
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        tension: 0.3,
        fill: true,
      },
      {
        label: 'Pressure Accuracy',
        data: equipmentTypes.map((type, i) => {
          const actual = actualAvgPressure[i];
          const predicted = predictedPressure[i];
          return actual > 0 ? ((1 - Math.abs(actual - predicted) / actual) * 100).toFixed(2) : 0;
        }),
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.3,
        fill: true,
      },
      {
        label: 'Temperature Accuracy',
        data: equipmentTypes.map((type, i) => {
          const actual = actualAvgTemperature[i];
          const predicted = predictedTemperature[i];
          return actual > 0 ? ((1 - Math.abs(actual - predicted) / actual) * 100).toFixed(2) : 0;
        }),
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.3,
        fill: true,
      },
    ],
  };

  const predictionAccuracyOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Prediction Accuracy by Equipment Type' },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: { display: true, text: 'Accuracy (%)' },
      },
    },
  };

  try {
    return (
      <div className="ml-comparison-section">
        <h3>🤖 Machine Learning Model Performance Analysis</h3>
        
        <div className="advanced-charts-grid">
          <div className="card chart-card">
            <Bar options={accuracyOptions} data={accuracyData} />
          </div>

          <div className="card chart-card">
            <Bar options={errorMetricsOptions} data={errorMetricsData} />
          </div>

          <div className="card chart-card full-width">
            <Line options={predictionAccuracyOptions} data={predictionAccuracyData} />
          </div>

          <div className="card chart-card">
            <Bar options={flowrateComparisonOptions} data={flowrateComparisonData} />
          </div>

          <div className="card chart-card">
            <Bar options={pressureComparisonOptions} data={pressureComparisonData} />
          </div>

          <div className="card chart-card">
            <Bar options={temperatureComparisonOptions} data={temperatureComparisonData} />
          </div>
        </div>
      </div>
    );
  } catch (error) {
    console.error('Error rendering ML comparison charts:', error);
    return null;
  }
};

export default MLComparisonCharts;
