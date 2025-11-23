"""
Login Window for Desktop Application
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from services.api_client import APIClient
from ui.dashboard_window import DashboardWindow


class LoginWindow(QWidget):
    """Login window with username and password fields"""
    
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.dashboard_window = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Chemical Equipment Visualizer - Login')
        self.setGeometry(100, 100, 450, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel#title {
                color: #667eea;
                font-size: 24px;
                font-weight: bold;
            }
            QLabel#subtitle {
                color: #4a5568;
                font-size: 14px;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #e2e8f0;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
            }
            QPushButton#login {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#login:hover {
                background-color: #5568d3;
            }
            QPushButton#register {
                background-color: #48bb78;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#register:hover {
                background-color: #38a169;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 30, 50, 30)
        
        # Title
        title = QLabel('Chemical Equipment Visualizer')
        title.setObjectName('title')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel('Desktop Application')
        subtitle.setObjectName('subtitle')
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Username field
        username_label = QLabel('Username:')
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter your username')
        layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel('Password:')
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Enter your password')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(10)
        
        # Login button
        self.login_btn = QPushButton('Login')
        self.login_btn.setObjectName('login')
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)
        
        # Register button
        self.register_btn = QPushButton('Register New Account')
        self.register_btn.setObjectName('register')
        self.register_btn.clicked.connect(self.handle_register)
        layout.addWidget(self.register_btn)
        
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Enable Enter key to login
        self.password_input.returnPressed.connect(self.handle_login)
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter both username and password')
            return
        
        try:
            self.login_btn.setEnabled(False)
            self.login_btn.setText('Logging in...')
            
            # Attempt login
            result = self.api_client.login(username, password)
            
            # Show dashboard
            self.dashboard_window = DashboardWindow(self.api_client, result['user'])
            self.dashboard_window.show()
            self.close()
            
        except Exception as e:
            error_msg = str(e)
            if 'Invalid credentials' in error_msg or '401' in error_msg:
                QMessageBox.critical(self, 'Login Failed', 'Invalid username or password')
            else:
                QMessageBox.critical(self, 'Error', f'Login failed: {error_msg}')
        finally:
            self.login_btn.setEnabled(True)
            self.login_btn.setText('Login')
    
    def handle_register(self):
        """Handle register button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter both username and password')
            return
        
        try:
            self.register_btn.setEnabled(False)
            self.register_btn.setText('Registering...')
            
            # Attempt registration
            result = self.api_client.register(username, password)
            
            # Show dashboard
            self.dashboard_window = DashboardWindow(self.api_client, result['user'])
            self.dashboard_window.show()
            self.close()
            
        except Exception as e:
            error_msg = str(e)
            if 'already exists' in error_msg:
                QMessageBox.critical(self, 'Registration Failed', 'Username already exists')
            else:
                QMessageBox.critical(self, 'Error', f'Registration failed: {error_msg}')
        finally:
            self.register_btn.setEnabled(True)
            self.register_btn.setText('Register New Account')
