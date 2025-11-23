# Chemical Equipment Parameter Visualizer
### Hybrid Web + Desktop Application

> **FOSSEE Intern Screening Task** - A hybrid application demonstrating data visualization and analytics for chemical equipment, running on both Web and Desktop platforms with a unified Django backend.

---

## 📋 Project Overview

This project implements a **Hybrid Web + Desktop Application** that allows users to upload CSV files containing chemical equipment data (Equipment Name, Type, Flowrate, Pressure, Temperature). The Django backend parses the data, performs comprehensive analysis, and provides summary statistics via REST API. Both **React (Web)** and **PyQt5 (Desktop)** frontends consume this unified API to display data tables, interactive charts, and analytical summaries.

---

## 🎯 Key Features

### Core Requirements ✅
- ✅ **CSV Upload** - Both Web and Desktop interfaces support CSV file uploads to the backend
- ✅ **Data Summary API** - Django REST API returns total count, averages, and equipment type distribution
- ✅ **Dual Visualization** - Chart.js (Web) and Matplotlib (Desktop) for consistent data presentation
- ✅ **History Management** - SQLite database stores last 5 uploaded datasets with summaries
- ✅ **PDF Report Generation** - Comprehensive reports with all charts and statistics
- ✅ **User Authentication** - Secure JWT-based login/register system
- ✅ **Sample CSV Provided** - `sample_equipment_data.csv` included for testing

### Enhanced Features 🚀
- 📊 **15+ Interactive Charts** - Advanced visualizations including scatter, radar, trends, and ML comparisons
- 🤖 **Machine Learning Integration** - Random Forest & Gradient Boosting models for parameter prediction
- 📈 **Real-time Analytics** - Equipment performance metrics and type-wise breakdowns
- 🎨 **Modern UI Design** - Dark gradient theme with glassmorphism effects and animations
- 📱 **Responsive Design** - Optimized for all screen sizes and devices

---

## 🛠️ Tech Stack (As Per Requirements)

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend (Web)** | React.js + Chart.js | Interactive web UI with data tables and charts |
| **Frontend (Desktop)** | PyQt5 + Matplotlib | Desktop application with same visualization capabilities |
| **Backend** | Django + Django REST Framework | Unified REST API backend for both frontends |
| **Data Handling** | Pandas | CSV parsing, data processing, and analytics |
| **Database** | SQLite | Store last 5 uploaded datasets with metadata |
| **Version Control** | Git & GitHub | Source code management and collaboration |
| **Sample Data** | sample_equipment_data.csv | Provided sample CSV for testing and demo |

### Additional Technologies Used
- **Backend**: scikit-learn (ML models), matplotlib & ReportLab (PDF generation), scipy (statistical analysis)
- **Frontend (Web)**: Material-UI (MUI), Axios (API calls), React Router (navigation)
- **Authentication**: JWT tokens for secure user sessions

---

## 📁 Project Structure

```
FOSSEE/
├── backend/                          # Django Backend (Common API)
│   ├── api/                         # Django REST Framework app
│   │   ├── models.py               # Database models (DatasetHistory)
│   │   ├── views.py                # API endpoints
│   │   ├── serializers.py          # DRF serializers
│   │   ├── ml_models.py            # ML training & prediction
│   │   ├── utils.py                # PDF generation & data processing
│   │   └── migrations/             # Database migrations
│   ├── core/                       # Django project settings
│   │   ├── settings.py
│   │   └── urls.py
│   ├── media/                      # Uploaded files & ML models
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example               # Environment variables template
│
├── frontend-react/                 # Web Frontend (React.js + Chart.js)
│   ├── src/
│   │   ├── components/            # Reusable components
│   │   │   ├── AdvancedCharts.js  # Chart.js visualizations
│   │   │   ├── MLComparisonCharts.js
│   │   │   └── Navbar.js
│   │   ├── pages/                 # Page components
│   │   │   ├── Login.js           # Dark theme login
│   │   │   ├── Register.js        # Dark theme register
│   │   │   ├── Dashboard.js       # Upload history
│   │   │   ├── Upload.js          # CSV upload
│   │   │   └── Visualization.js   # Charts display
│   │   ├── services/              # API service layer
│   │   └── context/               # Auth context (JWT)
│   ├── public/
│   │   └── sample_equipment_data.csv
│   ├── package.json
│   └── .env.example
│
├── desktop-pyqt5/                 # Desktop Frontend (PyQt5 + Matplotlib)
│   ├── ui/                        # PyQt5 UI windows
│   │   ├── login_window.py
│   │   ├── dashboard_window.py
│   │   ├── upload_window.py
│   │   └── charts_window.py
│   ├── services/                  # API client
│   │   └── api_client.py
│   ├── charts/                    # Matplotlib charts
│   ├── main.py                    # Desktop app entry point
│   └── requirements.txt
│
├── sample_equipment_data.csv      # Sample CSV for testing
├── .gitignore
└── README.md                      # This file
```

---

## 🚀 Setup Instructions

### Prerequisites
- **Python 3.13+** - Backend runtime
- **Node.js 16+** and npm - Frontend (Web) dependencies
- **Git** - Version control
- **PyQt5** - Desktop application framework (installed via requirements.txt)

### 1. Backend Setup (Django)

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Run migrations
python manage.py migrate

# (Optional) Create superuser
python manage.py createsuperuser

# Start Django backend
python manage.py runserver
```

Backend will run at **http://localhost:8000**

### 2. Frontend Setup (React Web App)

```bash
# Navigate to frontend folder
cd frontend-react

# Install dependencies
npm install

# Create .env file from example
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Start React development server
npm start
```

Frontend will run at **http://localhost:3000**

### 3. Desktop Application Setup (PyQt5)

```bash
# Navigate to desktop folder
cd desktop-pyqt5

# Ensure backend virtual environment is active or install PyQt5
pip install -r requirements.txt

# Start desktop application
python main.py
```

<<<<<<< HEAD
The desktop application will connect to the Django backend at **http://localhost:8000**

---

## 📖 Usage Guide

### Web Application (React)

1. **Register/Login** - Navigate to `http://localhost:3000` and create an account or login
2. **Upload CSV** - Click "Upload Data" and select a CSV file with the required format
3. **View Dashboard** - See your upload history (last 5 datasets)
4. **Explore Visualizations** - Navigate to "Visualization" page to see 15+ interactive charts
5. **Download PDF Report** - Click "Download PDF Report" button for comprehensive analysis
6. **Check ML Performance** - View machine learning model metrics and predictions

### Desktop Application (PyQt5)

1. **Launch** - Run `python main.py` from the `desktop-pyqt5` folder
2. **Login/Register** - Use the same credentials as the web application
3. **Upload CSV** - Use the upload window to select and upload CSV files
4. **View Dashboard** - See your upload history synchronized with web app
5. **Explore Charts** - Open charts window to view Matplotlib-based visualizations
6. **Seamless Sync** - All data syncs with web app through the unified backend API

---

## 📊 Sample CSV Format

A sample CSV file (`sample_equipment_data.csv`) is provided in the repository for testing and demo purposes.

### Required Columns:
```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120,5.2,110
Compressor-1,Compressor,95,8.4,95
Valve-1,Valve,60,4.1,105
HeatExchanger-1,HeatExchanger,150,6.8,120
Reactor-1,Reactor,200,9.2,150
Condenser-1,Condenser,80,4.5,85
```

### Column Descriptions:
- `Equipment Name` - Unique identifier for equipment
- `Type` - Equipment category (Pump, Compressor, Valve, HeatExchanger, Reactor, Condenser)
- `Flowrate` - Flow rate value (numeric)
- `Pressure` - Pressure value (numeric)
- `Temperature` - Temperature value in Celsius (numeric)

---

## 📡 API Endpoints

### Authentication
- `POST /api/register/` - User registration
- `POST /api/login/` - User login
- `GET /api/user/` - Get current user info

### Data Management
- `POST /api/upload-csv/` - Upload CSV and train ML model
- `GET /api/history/` - Get upload history (last 5 datasets)
- `GET /api/dataset/<id>/` - Get dataset details

### ML & Analytics
- `GET /api/predictions/` - Get all predictions
- `POST /api/predict/` - Predict parameters for equipment type
- `GET /api/generate-report/?dataset_id=<id>` - Download PDF report

---

## 📈 Features Breakdown

### Data Summary & Analytics
- **Total Equipment Count** - Count of all equipment in dataset
- **Average Values** - Mean flowrate, pressure, and temperature
- **Type Distribution** - Equipment categorization and counts
- **Parameter Ranges** - Min, max, and standard deviation for each parameter
- **Type-wise Breakdown** - Detailed statistics per equipment type

### Visualizations (Web - Chart.js)
1. Average Parameters Bar Chart - Compare parameters by equipment type
2. All Parameters Trend - Multi-line chart showing parameter trends
3. Flowrate vs Pressure Scatter - Correlation analysis
4. Temperature Trend Line - Temperature variation over data points
5. Pressure vs Temperature Scatter - Cross-parameter analysis
6. Equipment Performance Radar - Multi-dimensional comparison
7. Equipment Distribution Pie - Type distribution visualization
8. Equipment Counts Horizontal Bar - Count comparison
9. Parameter Ranges Stacked Bar - Range visualization

### Visualizations (Desktop - Matplotlib)
- Equipment type distribution charts
- Parameter comparison plots
- Statistical summaries and tables
- Consistent visualization with web interface

### ML Model Performance Charts (6 Charts)
1. R² Score Comparison - Model accuracy metrics
2. Error Metrics (MSE & MAE) - Model error analysis
3. Prediction Accuracy - Time-series accuracy plot
4. Flowrate: Actual vs Predicted
5. Pressure: Actual vs Predicted
6. Temperature: Actual vs Predicted

---

## ✅ Task Completion Checklist

- [x] **CSV Upload** - Implemented in both Web and Desktop
- [x] **Data Summary API** - Django REST API with complete statistics
- [x] **Visualization** - Chart.js (Web) and Matplotlib (Desktop)
- [x] **History Management** - Last 5 datasets stored in SQLite
- [x] **PDF Report Generation** - Comprehensive reports with all charts
- [x] **User Authentication** - JWT-based secure authentication
- [x] **Sample CSV** - Provided and tested with sample_equipment_data.csv
- [x] **Dual Frontend** - Both React and PyQt5 consuming same backend
- [x] **GitHub Repository** - Complete source code with documentation

---

## 📦 Submission Details

**Repository:** https://github.com/SMVINAYKUMAR2341/FOSSEE

**Submitted By:** SMVINAYKUMAR2341

**Project:** FOSSEE Intern Screening Task - Hybrid Web + Desktop Application

**Contents:**
- ✅ Complete source code (backend + both frontends)
- ✅ Setup instructions in README
- ✅ Environment configuration files (.env.example)
- ✅ Sample CSV data for testing
- ✅ Requirements files for all components

---

## 💻 Technologies Demonstrated

- **Backend Development** - Django, DRF, SQLite, Pandas
- **Web Development** - React.js, Chart.js, Material-UI, JWT Authentication
- **Desktop Development** - PyQt5, Matplotlib
- **Machine Learning** - scikit-learn (Random Forest, Gradient Boosting)
- **Data Processing** - Pandas, NumPy, SciPy
- **API Design** - RESTful API architecture
- **Version Control** - Git & GitHub
- **Report Generation** - ReportLab PDF generation

---

## 📝 License

This project is developed as part of FOSSEE Intern Screening Task for educational purposes.

---

## 📧 Contact

**GitHub:** [@SMVINAYKUMAR2341](https://github.com/SMVINAYKUMAR2341)

**Repository:** [FOSSEE](https://github.com/SMVINAYKUMAR2341/FOSSEE)

---

## 🙏 Acknowledgments

- **FOSSEE** for the internship opportunity and comprehensive task specifications
- **Django** and **React** communities for excellent documentation
- **Chart.js** and **Matplotlib** for powerful visualization libraries
- **PyQt5** for robust desktop application framework
- **scikit-learn** for machine learning capabilities

=======
## 📁 Project Structure

```
iit bombay internship/
├── backend/                      # Django Backend
│   ├── core/                    # Django project settings
│   │   ├── settings.py         # Main settings
│   │   ├── urls.py             # URL routing
│   │   └── wsgi.py
│   ├── api/                    # REST API app
│   │   ├── models.py          # Database models
│   │   ├── serializers.py     # DRF serializers
│   │   ├── views.py           # API views
│   │   ├── urls.py            # API routing
│   │   ├── utils.py           # Utility functions (CSV, PDF)
│   │   └── admin.py           # Admin interface
│   ├── manage.py              # Django management
│   └── requirements.txt       # Python dependencies
│
├── frontend-react/              # React Web Application
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   │   ├── Navbar.js
│   │   │   └── ChartComponent.js
│   │   ├── pages/            # Page components
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   │   ├── Dashboard.js
│   │   │   ├── Upload.js
│   │   │   └── Visualization.js
│   │   ├── services/         # API services
│   │   │   └── api.js
│   │   ├── context/          # React context
│   │   │   └── AuthContext.js
│   │   ├── App.js           # Main app component
│   │   └── index.js         # Entry point
│   └── package.json         # Node dependencies
│
├── desktop-pyqt5/             # PyQt5 Desktop Application
│   ├── ui/                  # UI components
│   │   ├── login_window.py
│   │   ├── dashboard_window.py
│   │   ├── upload_window.py
│   │   └── charts_window.py
│   ├── services/            # API client
│   │   └── api_client.py
│   ├── charts/              # Chart utilities
│   ├── main.py             # Application entry point
│   └── requirements.txt    # Python dependencies
│
├── sample_equipment_data.csv  # Sample dataset
└── README.md                 # This file
```

## 🔌 API Endpoints

### Authentication
- `POST /api/login/` - User login
- `POST /api/register/` - User registration
- `POST /api/logout/` - User logout
- `GET /api/user/` - Get current user info

### Dataset Management
- `POST /api/upload-csv/` - Upload and process CSV file
- `GET /api/history/` - Get last 5 upload history
- `GET /api/dataset/<id>/` - Get specific dataset details
- `GET /api/generate-report/` - Generate PDF report

## 📊 CSV Format

The CSV file must include the following columns:

| Column Name      | Type    | Description                    |
|-----------------|---------|--------------------------------|
| Equipment Name  | String  | Name of the equipment          |
| Type           | String  | Type/category of equipment     |
| Flowrate       | Float   | Flowrate measurement           |
| Pressure       | Float   | Pressure measurement           |
| Temperature    | Float   | Temperature measurement        |

### Example CSV:

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-001,Pump,150.5,45.2,85.3
Valve-001,Valve,120.0,50.1,78.5
Tank-001,Tank,200.3,30.5,92.1
```

## 🧪 Testing

### Backend Testing

```bash
cd backend
python manage.py test
```

### Frontend Testing

```bash
cd frontend-react
npm test
```

## 🔐 Authentication

The application uses token-based authentication:

1. **Register** a new account or **Login** with existing credentials
2. Receive an authentication token
3. Token is automatically included in all subsequent requests
4. Tokens are stored in:
   - Web: localStorage
   - Desktop: Session (memory)

## 📈 Usage Guide

### Web Application

1. **Login/Register**: Navigate to `http://localhost:3000` and create an account
2. **Upload CSV**: Click "Upload New CSV" and select your data file
3. **View Dashboard**: See summary of your last 5 uploads
4. **Visualize Data**: Click "View" to see interactive charts
5. **Download Report**: Click "PDF" to download a formatted report

### Desktop Application

1. **Launch App**: Run `python main.py`
2. **Login**: Enter your credentials
3. **Upload Dataset**: Click "Upload New CSV" button
4. **View Charts**: Click "View Charts" for any dataset
5. **Download PDF**: Click "Download PDF" to save report

## 🎨 Features Detail

### Computed Statistics
- Total equipment count
- Average flowrate
- Average pressure
- Average temperature
- Equipment type distribution

### Visualizations
- **Pie Chart**: Type distribution percentage
- **Bar Chart**: Type count comparison
- **Data Table**: Raw equipment data preview

### PDF Report Includes
- Summary statistics table
- Equipment type distribution table
- Bar chart visualization
- Timestamp and metadata

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
python manage.py runserver 8001
```

**Database issues:**
```bash
python manage.py flush
python manage.py migrate
```

### Frontend Issues

**Port 3000 in use:**
```bash
PORT=3001 npm start
```

**Node modules issues:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Desktop App Issues

**PyQt5 import errors:**
```bash
pip uninstall PyQt5
pip install PyQt5==5.15.10
```

**Connection refused:**
- Ensure Django backend is running on port 8000
- Check firewall settings

## 🔒 Security Notes

⚠️ **For Production:**
- Change `SECRET_KEY` in `settings.py`
- Set `DEBUG = False`
- Configure `ALLOWED_HOSTS`
- Use HTTPS
- Set up proper CORS origins
- Use environment variables for sensitive data

## 📝 Admin Panel

Access Django admin at: `http://localhost:8000/admin`

Features:
- View all uploaded datasets
- Manage users
- Inspect database records
>>>>>>> cb2ef2331792614d815666ce44f9a67b8a1a5b87
