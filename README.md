# Chemical Equipment Parameter Visualizer

A comprehensive hybrid application for uploading, processing, and visualizing chemical equipment data with both web and desktop interfaces.

## 🎯 Features

- **CSV Upload & Processing**: Upload equipment data and automatically compute statistics
- **Data Visualization**: Interactive charts using Chart.js (web) and Matplotlib (desktop)
- **PDF Report Generation**: Automatic PDF report creation with charts and summaries
- **History Management**: Automatic storage of last 5 uploads
- **Dual Interface**: Both web (React) and desktop (PyQt5) applications
- **Token Authentication**: Secure API access with Django REST Framework

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: SQLite
- **Data Processing**: Pandas
- **PDF Generation**: ReportLab
- **Visualization**: Matplotlib

### Frontend (Web)
- **Framework**: React.js 18
- **Routing**: React Router v6
- **Charts**: Chart.js + react-chartjs-2
- **HTTP Client**: Axios

### Frontend (Desktop)
- **Framework**: PyQt5
- **Charts**: Matplotlib
- **HTTP Client**: Requests

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "iit bombay internship"
```

### 2. Backend Setup (Django)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

The backend will be available at: `http://localhost:8000`

### 3. Frontend Setup (React Web App)

```bash
# Navigate to frontend directory (from project root)
cd frontend-react

# Install dependencies
npm install

# Start development server
npm start
```

The React app will be available at: `http://localhost:3000`

### 4. Desktop App Setup (PyQt5)

```bash
# Navigate to desktop app directory (from project root)
cd desktop-pyqt5

# Create virtual environment (if not using backend's venv)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

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

## 🚀 Production Deployment

### Backend
```bash
# Collect static files
python manage.py collectstatic

# Use production server (gunicorn)
pip install gunicorn
gunicorn core.wsgi:application
```

### Frontend
```bash
# Build for production
npm run build

# Serve with nginx or any static file server
```

## 📜 License

This project is created for IIT Bombay Internship purposes.

## 👥 Support

For issues or questions, please contact the development team.

## 🎯 Future Enhancements

- [ ] Advanced filtering and search
- [ ] Export to Excel
- [ ] Real-time data updates
- [ ] Multiple chart types
- [ ] Data validation rules
- [ ] Batch upload support
- [ ] Email notifications

---

**Built with ❤️ for Chemical Equipment Analysis**
