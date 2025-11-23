"""
Charts Window with Matplotlib visualizations
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class ChartsWindow(QWidget):
    """Window displaying data visualizations using Matplotlib"""
    
    def __init__(self, api_client, dataset):
        super().__init__()
        self.api_client = api_client
        self.dataset = dataset
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(f'Data Visualization - {self.dataset["filename"]}')
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QWidget {
                background-color: #f7fafc;
            }
            QLabel#title {
                color: #2d3748;
                font-size: 24px;
                font-weight: bold;
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
            QFrame#summary-card {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                margin: 5px;
            }
            QLabel#card-label {
                color: #718096;
                font-size: 12px;
            }
            QLabel#card-value {
                color: #2d3748;
                font-size: 28px;
                font-weight: bold;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel(f'Data Visualization')
        title.setObjectName('title')
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        main_layout.addLayout(header_layout)
        
        # Dataset info
        info_label = QLabel(f"Dataset: {self.dataset['filename']}")
        info_label.setStyleSheet('color: #718096; font-size: 14px;')
        main_layout.addWidget(info_label)
        
        # Summary cards
        cards_layout = QHBoxLayout()
        
        self.create_summary_card(cards_layout, '📊', 'Total Equipment', str(self.dataset['count']))
        self.create_summary_card(cards_layout, '💧', 'Avg Flowrate', f"{self.dataset['avg_flowrate']:.2f}")
        self.create_summary_card(cards_layout, '⚡', 'Avg Pressure', f"{self.dataset['avg_pressure']:.2f}")
        self.create_summary_card(cards_layout, '🌡️', 'Avg Temperature', f"{self.dataset['avg_temperature']:.2f}")
        
        main_layout.addLayout(cards_layout)
        
        # Scroll area for charts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('border: none;')
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(20)
        
        # Create charts
        self.create_pie_chart(scroll_layout)
        self.create_bar_chart(scroll_layout)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def create_summary_card(self, layout, icon, label, value):
        """Create a summary card widget"""
        card = QFrame()
        card.setObjectName('summary-card')
        card.setMinimumWidth(200)
        
        card_layout = QVBoxLayout()
        
        # Icon and label row
        top_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet('font-size: 32px;')
        top_layout.addWidget(icon_label)
        
        label_widget = QLabel(label)
        label_widget.setObjectName('card-label')
        top_layout.addWidget(label_widget)
        top_layout.addStretch()
        
        card_layout.addLayout(top_layout)
        
        # Value
        value_widget = QLabel(value)
        value_widget.setObjectName('card-value')
        card_layout.addWidget(value_widget)
        
        card.setLayout(card_layout)
        layout.addWidget(card)
    
    def create_pie_chart(self, layout):
        """Create pie chart for equipment type distribution"""
        # Create figure
        fig = Figure(figsize=(10, 6))
        canvas = FigureCanvas(fig)
        
        ax = fig.add_subplot(111)
        
        # Prepare data
        types = list(self.dataset['type_distribution'].keys())
        counts = list(self.dataset['type_distribution'].values())
        
        # Create pie chart
        colors = ['#667eea', '#764ba2', '#48bb78', '#f56565', '#ed8936', '#4299e1']
        wedges, texts, autotexts = ax.pie(
            counts, 
            labels=types, 
            autopct='%1.1f%%',
            colors=colors[:len(types)],
            startangle=90,
            textprops={'fontsize': 12, 'weight': 'bold'}
        )
        
        # Make percentage text white
        for autotext in autotexts:
            autotext.set_color('white')
        
        ax.set_title('Equipment Type Distribution (Pie Chart)', 
                    fontsize=16, fontweight='bold', pad=20)
        
        fig.tight_layout()
        
        # Add to layout
        chart_frame = QFrame()
        chart_frame.setStyleSheet('background-color: white; border-radius: 10px; padding: 20px;')
        chart_layout = QVBoxLayout()
        chart_layout.addWidget(canvas)
        chart_frame.setLayout(chart_layout)
        
        layout.addWidget(chart_frame)
    
    def create_bar_chart(self, layout):
        """Create bar chart for equipment type distribution"""
        # Create figure
        fig = Figure(figsize=(10, 6))
        canvas = FigureCanvas(fig)
        
        ax = fig.add_subplot(111)
        
        # Prepare data
        types = list(self.dataset['type_distribution'].keys())
        counts = list(self.dataset['type_distribution'].values())
        
        # Create bar chart
        bars = ax.bar(types, counts, color='#667eea', alpha=0.8, edgecolor='#5568d3', linewidth=2)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        ax.set_xlabel('Equipment Type', fontsize=14, fontweight='bold')
        ax.set_ylabel('Count', fontsize=14, fontweight='bold')
        ax.set_title('Equipment Type Distribution (Bar Chart)', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Rotate x-axis labels if needed
        if len(types) > 5:
            ax.tick_params(axis='x', rotation=45)
        
        fig.tight_layout()
        
        # Add to layout
        chart_frame = QFrame()
        chart_frame.setStyleSheet('background-color: white; border-radius: 10px; padding: 20px;')
        chart_layout = QVBoxLayout()
        chart_layout.addWidget(canvas)
        chart_frame.setLayout(chart_layout)
        
        layout.addWidget(chart_frame)
