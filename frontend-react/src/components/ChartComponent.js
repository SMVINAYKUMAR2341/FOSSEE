import React from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

const ChartComponent = ({ type, data, title }) => {
  // Prepare data for charts
  const labels = Object.keys(data);
  const values = Object.values(data);

  // Color palette
  const backgroundColors = [
    'rgba(102, 126, 234, 0.8)',
    'rgba(118, 75, 162, 0.8)',
    'rgba(72, 187, 120, 0.8)',
    'rgba(245, 101, 101, 0.8)',
    'rgba(237, 137, 54, 0.8)',
    'rgba(66, 153, 225, 0.8)',
  ];

  const borderColors = [
    'rgba(102, 126, 234, 1)',
    'rgba(118, 75, 162, 1)',
    'rgba(72, 187, 120, 1)',
    'rgba(245, 101, 101, 1)',
    'rgba(237, 137, 54, 1)',
    'rgba(66, 153, 225, 1)',
  ];

  const chartData = {
    labels: labels,
    datasets: [
      {
        label: title || 'Data',
        data: values,
        backgroundColor: backgroundColors.slice(0, labels.length),
        borderColor: borderColors.slice(0, labels.length),
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            size: 14,
          },
        },
      },
      title: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleFont: {
          size: 14,
        },
        bodyFont: {
          size: 13,
        },
        padding: 12,
        borderColor: 'rgba(255, 255, 255, 0.3)',
        borderWidth: 1,
      },
    },
  };

  const barOptions = {
    ...options,
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0,
        },
      },
    },
  };

  // Render chart based on type
  switch (type) {
    case 'pie':
      return (
        <div style={{ maxWidth: '400px', margin: '0 auto' }}>
          <Pie data={chartData} options={options} />
        </div>
      );
    case 'bar':
      return <Bar data={chartData} options={barOptions} />;
    case 'line':
      return <Line data={chartData} options={barOptions} />;
    default:
      return <Bar data={chartData} options={barOptions} />;
  }
};

export default ChartComponent;
