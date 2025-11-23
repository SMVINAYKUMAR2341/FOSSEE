import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Bar, Scatter, Line, Radar, Doughnut, Pie } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const AdvancedCharts = ({ dataset }) => {
  if (!dataset || !dataset.raw_data || !dataset.type_wise_breakdown) {
    return null;
  }

  // 1. Parameter Comparison Data (Bar Chart)
  const types = Object.keys(dataset.type_wise_breakdown);
  const avgFlowrates = types.map(t => dataset.type_wise_breakdown[t].avg_flowrate);
  const avgPressures = types.map(t => dataset.type_wise_breakdown[t].avg_pressure);
  const avgTemperatures = types.map(t => dataset.type_wise_breakdown[t].avg_temperature);

  const comparisonData = {
    labels: types,
    datasets: [
      {
        label: 'Avg Flowrate',
        data: avgFlowrates,
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
      },
      {
        label: 'Avg Pressure',
        data: avgPressures,
        backgroundColor: 'rgba(255, 99, 132, 0.6)',
      },
      {
        label: 'Avg Temperature',
        data: avgTemperatures,
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      },
    ],
  };

  const comparisonOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Average Parameters by Equipment Type' },
    },
  };

  // 2. Flowrate vs Pressure (Scatter Plot)
  // We'll create a dataset for each equipment type to color them differently
  const scatterDatasets = types.map((type, index) => {
    const typeData = dataset.raw_data
      .filter(d => d.Type === type)
      .map(d => ({ x: d.Flowrate, y: d.Pressure }));
    
    const colors = [
      'rgba(255, 99, 132, 1)',
      'rgba(54, 162, 235, 1)',
      'rgba(255, 206, 86, 1)',
      'rgba(75, 192, 192, 1)',
      'rgba(153, 102, 255, 1)',
      'rgba(255, 159, 64, 1)'
    ];

    return {
      label: type,
      data: typeData,
      backgroundColor: colors[index % colors.length],
    };
  });

  const scatterData = { datasets: scatterDatasets };
  const scatterOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Flowrate vs Pressure Correlation' },
    },
    scales: {
      x: { title: { display: true, text: 'Flowrate' } },
      y: { title: { display: true, text: 'Pressure' } },
    },
  };

  // 3. Temperature Trend (Line Chart)
  const lineData = {
    labels: dataset.raw_data.map((_, i) => i + 1),
    datasets: [
      {
        label: 'Temperature',
        data: dataset.raw_data.map(d => d.Temperature),
        borderColor: 'rgba(255, 159, 64, 1)',
        backgroundColor: 'rgba(255, 159, 64, 0.5)',
        tension: 0.3,
      },
    ],
  };

  const lineOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Temperature Variation Across Samples' },
    },
    scales: {
      x: { title: { display: true, text: 'Sample Index' } },
      y: { title: { display: true, text: 'Temperature (°C)' } },
    },
  };

  // 4. Multi-Parameter Line Chart (All parameters over samples)
  const multiLineData = {
    labels: dataset.raw_data.map((_, i) => i + 1),
    datasets: [
      {
        label: 'Flowrate',
        data: dataset.raw_data.map(d => d.Flowrate),
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        tension: 0.3,
        fill: true,
      },
      {
        label: 'Pressure',
        data: dataset.raw_data.map(d => d.Pressure),
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.3,
        fill: true,
      },
      {
        label: 'Temperature',
        data: dataset.raw_data.map(d => d.Temperature),
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.3,
        fill: true,
      },
    ],
  };

  const multiLineOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'All Parameters Trend Analysis' },
    },
    scales: {
      x: { title: { display: true, text: 'Sample Index' } },
      y: { title: { display: true, text: 'Parameter Values' } },
    },
  };

  // 5. Equipment Type Distribution (Pie Chart)
  const typeColors = [
    'rgba(255, 99, 132, 0.8)',
    'rgba(54, 162, 235, 0.8)',
    'rgba(255, 206, 86, 0.8)',
    'rgba(75, 192, 192, 0.8)',
    'rgba(153, 102, 255, 0.8)',
    'rgba(255, 159, 64, 0.8)',
  ];

  const pieData = {
    labels: types,
    datasets: [
      {
        label: 'Equipment Count',
        data: types.map(t => dataset.type_wise_breakdown[t].count),
        backgroundColor: typeColors,
        borderColor: typeColors.map(c => c.replace('0.8', '1')),
        borderWidth: 2,
      },
    ],
  };

  const pieOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'right' },
      title: { display: true, text: 'Equipment Type Distribution' },
    },
  };

  // 6. Radar Chart (Multi-dimensional comparison)
  const radarData = {
    labels: types,
    datasets: [
      {
        label: 'Flowrate',
        data: avgFlowrates,
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
      },
      {
        label: 'Pressure',
        data: avgPressures,
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 2,
      },
      {
        label: 'Temperature',
        data: avgTemperatures,
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 2,
      },
    ],
  };

  const radarOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Parameter Performance Radar' },
    },
    scales: {
      r: {
        beginAtZero: true,
      },
    },
  };

  // 7. Stacked Bar Chart (Parameter ranges by type)
  const stackedBarData = {
    labels: types,
    datasets: [
      {
        label: 'Min Flowrate',
        data: types.map(t => dataset.type_wise_breakdown[t].min_flowrate),
        backgroundColor: 'rgba(54, 162, 235, 0.7)',
        stack: 'Stack 0',
      },
      {
        label: 'Max Flowrate',
        data: types.map(t => dataset.type_wise_breakdown[t].max_flowrate),
        backgroundColor: 'rgba(54, 162, 235, 0.4)',
        stack: 'Stack 0',
      },
    ],
  };

  const stackedBarOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Flowrate Range by Equipment Type' },
    },
    scales: {
      x: { stacked: true },
      y: { stacked: true, title: { display: true, text: 'Flowrate' } },
    },
  };

  // 8. Horizontal Bar Chart (Equipment counts)
  const horizontalBarData = {
    labels: types,
    datasets: [
      {
        label: 'Equipment Count',
        data: types.map(t => dataset.type_wise_breakdown[t].count),
        backgroundColor: types.map((_, i) => typeColors[i % typeColors.length]),
        borderColor: types.map((_, i) => typeColors[i % typeColors.length].replace('0.8', '1')),
        borderWidth: 1,
      },
    ],
  };

  const horizontalBarOptions = {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: true, text: 'Equipment Type Count Comparison' },
    },
    scales: {
      x: { title: { display: true, text: 'Number of Equipment' } },
    },
  };

  // 9. Pressure vs Temperature Scatter
  const pressureTempScatter = types.map((type, index) => {
    const typeData = dataset.raw_data
      .filter(d => d.Type === type)
      .map(d => ({ x: d.Pressure, y: d.Temperature }));

    return {
      label: type,
      data: typeData,
      backgroundColor: typeColors[index % typeColors.length],
    };
  });

  const pressureTempData = { datasets: pressureTempScatter };
  const pressureTempOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Pressure vs Temperature Correlation' },
    },
    scales: {
      x: { title: { display: true, text: 'Pressure' } },
      y: { title: { display: true, text: 'Temperature (°C)' } },
    },
  };

  return (
    <div className="advanced-charts-grid">
      <div className="card chart-card full-width">
        <Bar options={comparisonOptions} data={comparisonData} />
      </div>
      
      <div className="card chart-card full-width">
        <Line options={multiLineOptions} data={multiLineData} />
      </div>

      <div className="card chart-card">
        <Scatter options={scatterOptions} data={scatterData} />
      </div>
      
      <div className="card chart-card">
        <Line options={lineOptions} data={lineData} />
      </div>

      <div className="card chart-card">
        <Scatter options={pressureTempOptions} data={pressureTempData} />
      </div>

      <div className="card chart-card">
        <Radar options={radarOptions} data={radarData} />
      </div>

      <div className="card chart-card">
        <Pie options={pieOptions} data={pieData} />
      </div>

      <div className="card chart-card">
        <Bar options={horizontalBarOptions} data={horizontalBarData} />
      </div>

      <div className="card chart-card">
        <Bar options={stackedBarOptions} data={stackedBarData} />
      </div>
    </div>
  );
};

export default AdvancedCharts;
