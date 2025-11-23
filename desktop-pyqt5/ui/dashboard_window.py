"""
Dashboard Window for Desktop Application
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime
from ui.upload_window import UploadWindow
from ui.charts_window import ChartsWindow


class DashboardWindow(QWidget):
    """Main dashboard showing upload history and actions"""
    
    def __init__(self, api_client, user):
        super().__init__()
        self.api_client = api_client
        self.user = user
        self.upload_window = None
        self.charts_window = None
        self.init_ui()
        self.load_history()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Chemical Equipment Visualizer - Dashboard')
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f7fafc;
            }
            QLabel#welcome {
                color: #2d3748;
                font-size: 28px;
                font-weight: bold;
            }
            QLabel#subtitle {
                color: #718096;
                font-size: 14px;
            }
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5568d3;
            }
            QPushButton#secondary {
                background-color: #48bb78;
            }
            QPushButton#secondary:hover {
                background-color: #38a169;
            }
            QPushButton#danger {
                background-color: #f56565;
            }
            QPushButton#danger:hover {
                background-color: #e53e3e;
            }
            QPushButton#small {
                padding: 5px 10px;
                font-size: 12px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 5px;
                gridline-color: #e2e8f0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #667eea;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QHBoxLayout()
        
        header_left = QVBoxLayout()
        welcome_label = QLabel(f"Welcome, {self.user['username']}!")
        welcome_label.setObjectName('welcome')
        header_left.addWidget(welcome_label)
        
        subtitle = QLabel('Manage your chemical equipment datasets')
        subtitle.setObjectName('subtitle')
        header_left.addWidget(subtitle)
        
        header_layout.addLayout(header_left)
        header_layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton('Logout')
        logout_btn.setObjectName('danger')
        logout_btn.clicked.connect(self.handle_logout)
        logout_btn.setMaximumWidth(100)
        header_layout.addWidget(logout_btn)
        
        layout.addLayout(header_layout)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        upload_btn = QPushButton('📤 Upload New CSV')
        upload_btn.clicked.connect(self.show_upload_window)
        actions_layout.addWidget(upload_btn)
        
        refresh_btn = QPushButton('🔄 Refresh History')
        refresh_btn.setObjectName('secondary')
        refresh_btn.clicked.connect(self.load_history)
        actions_layout.addWidget(refresh_btn)
        
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        # History table
        history_label = QLabel('Dataset History (Last 5 Uploads)')
        history_label.setStyleSheet('font-size: 18px; font-weight: bold; color: #2d3748;')
        layout.addWidget(history_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            'Filename', 'Upload Date', 'Count', 'Avg Flowrate', 
            'Avg Pressure', 'Avg Temp', 'View', 'PDF'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_history(self):
        """Load dataset history from API"""
        try:
            history = self.api_client.get_history()
            self.populate_table(history)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load history: {str(e)}')
    
    def populate_table(self, history):
        """Populate table with history data"""
        self.table.setRowCount(len(history))
        
        for row, dataset in enumerate(history):
            # Filename
            self.table.setItem(row, 0, QTableWidgetItem(dataset['filename']))
            
            # Upload date
            upload_date = datetime.fromisoformat(dataset['timestamp'].replace('Z', '+00:00'))
            self.table.setItem(row, 1, QTableWidgetItem(upload_date.strftime('%Y-%m-%d %H:%M')))
            
            # Count
            self.table.setItem(row, 2, QTableWidgetItem(str(dataset['count'])))
            
            # Avg Flowrate
            self.table.setItem(row, 3, QTableWidgetItem(f"{dataset['avg_flowrate']:.2f}"))
            
            # Avg Pressure
            self.table.setItem(row, 4, QTableWidgetItem(f"{dataset['avg_pressure']:.2f}"))
            
            # Avg Temperature
            self.table.setItem(row, 5, QTableWidgetItem(f"{dataset['avg_temperature']:.2f}"))
            
            # View button
            view_btn = QPushButton('View Charts')
            view_btn.setObjectName('small')
            view_btn.clicked.connect(lambda checked, d=dataset: self.show_charts(d))
            self.table.setCellWidget(row, 6, view_btn)
            
            # PDF button
            pdf_btn = QPushButton('Download PDF')
            pdf_btn.setObjectName('small')
            pdf_btn.clicked.connect(lambda checked, d=dataset: self.download_pdf(d['id']))
            self.table.setCellWidget(row, 7, pdf_btn)
    
    def show_upload_window(self):
        """Show upload window"""
        self.upload_window = UploadWindow(self.api_client, self)
        self.upload_window.show()
    
    def show_charts(self, dataset):
        """Show charts window for a dataset"""
        self.charts_window = ChartsWindow(self.api_client, dataset)
        self.charts_window.show()
    
    def download_pdf(self, dataset_id):
        """Download PDF report for a dataset"""
        try:
            # Get save location
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save PDF Report",
                f"equipment_report_{dataset_id}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if filename:
                # Download report
                pdf_content = self.api_client.generate_report(dataset_id)
                
                # Save to file
                with open(filename, 'wb') as f:
                    f.write(pdf_content)
                
                QMessageBox.information(self, 'Success', f'Report saved to {filename}')
        
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to download report: {str(e)}')
    
    def handle_logout(self):
        """Handle logout"""
        reply = QMessageBox.question(
            self, 'Logout', 
            'Are you sure you want to logout?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.api_client.logout()
            self.close()
            
            # Show login window again
            from ui.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
