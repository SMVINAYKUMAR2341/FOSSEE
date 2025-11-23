"""
Upload Window for CSV file upload
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QMessageBox, QGridLayout,
                             QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class UploadWindow(QWidget):
    """Window for uploading CSV files"""
    
    def __init__(self, api_client, parent=None):
        super().__init__()
        self.api_client = api_client
        self.parent_window = parent
        self.selected_file = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Upload CSV Dataset')
        self.setGeometry(150, 150, 600, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #f7fafc;
            }
            QLabel#title {
                color: #2d3748;
                font-size: 24px;
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
            QFrame#file-frame {
                background-color: white;
                border: 2px dashed #cbd5e0;
                border-radius: 10px;
                padding: 30px;
            }
            QFrame#summary {
                background-color: white;
                border: 2px solid #48bb78;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel#summary-label {
                color: #2d3748;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#summary-value {
                color: #667eea;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel('Upload CSV Dataset')
        title.setObjectName('title')
        layout.addWidget(title)
        
        subtitle = QLabel('Upload chemical equipment data in CSV format')
        subtitle.setObjectName('subtitle')
        layout.addWidget(subtitle)
        
        # File selection frame
        file_frame = QFrame()
        file_frame.setObjectName('file-frame')
        file_layout = QVBoxLayout()
        
        self.file_label = QLabel('No file selected')
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setStyleSheet('font-size: 16px; color: #718096;')
        file_layout.addWidget(self.file_label)
        
        select_btn = QPushButton('📁 Select CSV File')
        select_btn.clicked.connect(self.select_file)
        file_layout.addWidget(select_btn)
        
        # Load sample button
        sample_btn = QPushButton('📋 Load Sample Data')
        sample_btn.setObjectName('secondary')
        sample_btn.clicked.connect(self.load_sample_data)
        file_layout.addWidget(sample_btn)
        
        help_text = QLabel('Required columns: Equipment Name, Type, Flowrate, Pressure, Temperature')
        help_text.setAlignment(Qt.AlignCenter)
        help_text.setStyleSheet('font-size: 12px; color: #a0aec0; margin-top: 10px;')
        file_layout.addWidget(help_text)
        
        file_frame.setLayout(file_layout)
        layout.addWidget(file_frame)
        
        # Summary frame (hidden initially)
        self.summary_frame = QFrame()
        self.summary_frame.setObjectName('summary')
        self.summary_frame.setVisible(False)
        summary_layout = QVBoxLayout()
        
        summary_title = QLabel('Processing Summary')
        summary_title.setStyleSheet('font-size: 18px; font-weight: bold; color: #2d3748;')
        summary_layout.addWidget(summary_title)
        
        # Summary grid
        self.summary_grid = QGridLayout()
        self.summary_grid.setSpacing(15)
        summary_layout.addLayout(self.summary_grid)
        
        self.summary_frame.setLayout(summary_layout)
        layout.addWidget(self.summary_frame)
        
        layout.addStretch()
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.upload_btn = QPushButton('Upload and Process')
        self.upload_btn.setEnabled(False)
        self.upload_btn.clicked.connect(self.upload_file)
        actions_layout.addWidget(self.upload_btn)
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.setObjectName('secondary')
        cancel_btn.clicked.connect(self.close)
        actions_layout.addWidget(cancel_btn)
        
        layout.addLayout(actions_layout)
        
        self.setLayout(layout)
    
    def select_file(self):
        """Open file dialog to select CSV file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv)"
        )
        
        if filename:
            self.selected_file = filename
            self.file_label.setText(f"✓ Selected: {filename.split('/')[-1].split(chr(92))[-1]}")
            self.file_label.setStyleSheet('font-size: 16px; color: #48bb78; font-weight: bold;')
            self.upload_btn.setEnabled(True)
            self.summary_frame.setVisible(False)
    
    def load_sample_data(self):
        """Load the sample equipment data CSV"""
        import os
        
        # Try to find sample_equipment_data.csv in parent directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        parent_dir = os.path.dirname(current_dir)
        sample_file = os.path.join(parent_dir, 'sample_equipment_data.csv')
        
        if os.path.exists(sample_file):
            self.selected_file = sample_file
            self.file_label.setText(f"✓ Loaded: sample_equipment_data.csv (40 equipment entries)")
            self.file_label.setStyleSheet('font-size: 16px; color: #48bb78; font-weight: bold;')
            self.upload_btn.setEnabled(True)
            self.summary_frame.setVisible(False)
            QMessageBox.information(self, 'Sample Data Loaded', 
                                  'Sample equipment data loaded successfully!\nClick "Upload and Process" to continue.')
        else:
            QMessageBox.warning(self, 'Sample Not Found', 
                              f'Sample data file not found at:\n{sample_file}\n\nPlease select a CSV file manually.')
    
    def upload_file(self):
        """Upload the selected file"""
        if not self.selected_file:
            QMessageBox.warning(self, 'Error', 'Please select a file first')
            return
        
        try:
            self.upload_btn.setEnabled(False)
            self.upload_btn.setText('Uploading...')
            
            # Upload file
            result = self.api_client.upload_csv(self.selected_file)
            
            # Show summary
            self.show_summary(result)
            
            QMessageBox.information(self, 'Success', 'CSV uploaded and processed successfully!')
            
            # Refresh parent dashboard
            if self.parent_window:
                self.parent_window.load_history()
        
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Upload failed: {str(e)}')
        finally:
            self.upload_btn.setEnabled(True)
            self.upload_btn.setText('Upload and Process')
    
    def show_summary(self, data):
        """Display processing summary"""
        # Clear existing grid
        for i in reversed(range(self.summary_grid.count())): 
            self.summary_grid.itemAt(i).widget().setParent(None)
        
        # Add summary items
        summaries = [
            ('Total Equipment:', str(data['count'])),
            ('Avg Flowrate:', f"{data['avg_flowrate']:.2f}"),
            ('Avg Pressure:', f"{data['avg_pressure']:.2f}"),
            ('Avg Temperature:', f"{data['avg_temperature']:.2f}")
        ]
        
        for i, (label_text, value_text) in enumerate(summaries):
            label = QLabel(label_text)
            label.setObjectName('summary-label')
            self.summary_grid.addWidget(label, i, 0)
            
            value = QLabel(value_text)
            value.setObjectName('summary-value')
            self.summary_grid.addWidget(value, i, 1)
        
        # Type distribution
        if 'type_distribution' in data:
            dist_label = QLabel('Type Distribution:')
            dist_label.setObjectName('summary-label')
            self.summary_grid.addWidget(dist_label, len(summaries), 0)
            
            dist_text = ', '.join([f"{k}: {v}" for k, v in data['type_distribution'].items()])
            dist_value = QLabel(dist_text)
            dist_value.setObjectName('summary-value')
            dist_value.setWordWrap(True)
            self.summary_grid.addWidget(dist_value, len(summaries), 1)
        
        self.summary_frame.setVisible(True)
