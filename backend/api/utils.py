"""
Utility functions for data processing and PDF generation
"""
import pandas as pd
import numpy as np
from scipy import stats
import json
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt


def process_csv_file(csv_file):
    """
    Process uploaded CSV file and compute comprehensive statistics.
    
    Args:
        csv_file: Django UploadedFile object
        
    Returns:
        dict: Dictionary containing computed statistics and raw data
    """
    try:
        # Read CSV file using pandas
        df = pd.read_csv(csv_file)
        
        # Validate required columns
        required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # --- Preprocessing & Cleaning ---
        # 1. Handle missing values
        numeric_cols = ['Flowrate', 'Pressure', 'Temperature']
        for col in numeric_cols:
            # Ensure numeric
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Fill missing values with median
            if df[col].isnull().any():
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
        
        # 2. Remove outliers using Z-score (if enough data)
        if len(df) > 5:
            try:
                z_scores = np.abs(stats.zscore(df[numeric_cols]))
                # Keep rows where all z-scores are < 3
                df = df[(z_scores < 3).all(axis=1)]
            except Exception as e:
                print(f"Outlier removal skipped: {e}")

        # Basic statistics
        total_count = len(df)
        avg_flowrate = df['Flowrate'].mean()
        avg_pressure = df['Pressure'].mean()
        avg_temperature = df['Temperature'].mean()
        
        # Equipment type distribution
        type_distribution = df['Type'].value_counts().to_dict()
        equipment_types_count = len(type_distribution)
        
        # Parameter ranges (min, max, std_dev)
        ranges = {
            'flowrate': {
                'min': float(df['Flowrate'].min()),
                'max': float(df['Flowrate'].max()),
                'std_dev': float(df['Flowrate'].std())
            },
            'pressure': {
                'min': float(df['Pressure'].min()),
                'max': float(df['Pressure'].max()),
                'std_dev': float(df['Pressure'].std())
            },
            'temperature': {
                'min': float(df['Temperature'].min()),
                'max': float(df['Temperature'].max()),
                'std_dev': float(df['Temperature'].std())
            }
        }
        
        # Type-wise breakdown
        type_wise_breakdown = {}
        for equipment_type in type_distribution.keys():
            type_df = df[df['Type'] == equipment_type]
            type_wise_breakdown[equipment_type] = {
                'count': int(type_df.shape[0]),
                'avg_flowrate': round(float(type_df['Flowrate'].mean()), 2),
                'avg_pressure': round(float(type_df['Pressure'].mean()), 2),
                'avg_temperature': round(float(type_df['Temperature'].mean()), 2),
                'min_flowrate': float(type_df['Flowrate'].min()),
                'max_flowrate': float(type_df['Flowrate'].max()),
                'min_pressure': float(type_df['Pressure'].min()),
                'max_pressure': float(type_df['Pressure'].max()),
                'min_temperature': float(type_df['Temperature'].min()),
                'max_temperature': float(type_df['Temperature'].max())
            }
        
        # Convert dataframe to JSON for storage
        raw_data = df.to_dict('records')
        
        return {
            'count': total_count,
            'equipment_types_count': equipment_types_count,
            'avg_flowrate': round(avg_flowrate, 2),
            'avg_pressure': round(avg_pressure, 2),
            'avg_temperature': round(avg_temperature, 2),
            'type_distribution': type_distribution,
            'ranges': ranges,
            'type_wise_breakdown': type_wise_breakdown,
            'raw_data': raw_data
        }
    
    except Exception as e:
        raise ValueError(f"Error processing CSV file: {str(e)}")


def generate_type_distribution_chart(type_distribution):
    """
    Generate a bar chart for equipment type distribution.
    
    Args:
        type_distribution: Dictionary with equipment types and counts
        
    Returns:
        BytesIO: Image buffer containing the chart
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    
    types = list(type_distribution.keys())
    counts = list(type_distribution.values())
    
    ax.bar(types, counts, color='steelblue', alpha=0.7)
    ax.set_xlabel('Equipment Type', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Equipment Type Distribution', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    # Save to buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    
    return buffer


def generate_avg_parameters_chart(type_wise):
    """Generate bar chart for average parameters by equipment type."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    types = list(type_wise.keys())
    flowrates = [type_wise[t]['avg_flowrate'] for t in types]
    pressures = [type_wise[t]['avg_pressure'] for t in types]
    temps = [type_wise[t]['avg_temperature'] for t in types]
    
    x = np.arange(len(types))
    width = 0.25
    
    ax.bar(x - width, flowrates, width, label='Avg Flowrate', color='#3498DB')
    ax.bar(x, pressures, width, label='Avg Pressure', color='#E74C3C')
    ax.bar(x + width, temps, width, label='Avg Temperature', color='#F39C12')
    
    ax.set_xlabel('Equipment Type', fontsize=11)
    ax.set_ylabel('Average Value', fontsize=11)
    ax.set_title('Average Parameters by Equipment Type', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(types, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer


def generate_all_parameters_trend(raw_data):
    """Generate multi-line chart for all parameters."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    df = pd.DataFrame(raw_data)
    indices = range(len(df))
    
    ax.plot(indices, df['Flowrate'], marker='o', markersize=3, label='Flowrate', linewidth=2, color='#3498DB')
    ax.plot(indices, df['Pressure'], marker='s', markersize=3, label='Pressure', linewidth=2, color='#E74C3C')
    ax.plot(indices, df['Temperature'], marker='^', markersize=3, label='Temperature', linewidth=2, color='#F39C12')
    
    ax.set_xlabel('Data Point Index', fontsize=11)
    ax.set_ylabel('Parameter Value', fontsize=11)
    ax.set_title('All Parameters Trend', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer


def generate_scatter_chart(raw_data, param1, param2):
    """Generate scatter plot for two parameters."""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    df = pd.DataFrame(raw_data)
    colors_map = {'Reactor': '#E74C3C', 'Pump': '#3498DB', 'Heat Exchanger': '#2ECC71',
                  'Compressor': '#F39C12', 'Valve': '#9B59B6', 'Condenser': '#1ABC9C',
                  'HeatExchanger': '#2ECC71'}
    
    # Use 'Type' column (not 'Equipment_Type')
    type_col = 'Type' if 'Type' in df.columns else 'Equipment_Type'
    
    for eq_type in df[type_col].unique():
        mask = df[type_col] == eq_type
        ax.scatter(df[mask][param1], df[mask][param2], 
                  label=eq_type, alpha=0.6, s=80,
                  color=colors_map.get(eq_type, '#95A5A6'))
    
    ax.set_xlabel(param1, fontsize=11)
    ax.set_ylabel(param2, fontsize=11)
    ax.set_title(f'{param1} vs {param2}', fontsize=13, fontweight='bold')
    ax.legend(fontsize=8, loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer


def generate_radar_chart(type_wise):
    """Generate radar chart for equipment performance."""
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    types = list(type_wise.keys())[:6]  # Limit to 6 types
    if not types:
        return BytesIO()
    
    categories = ['Flowrate', 'Pressure', 'Temperature']
    N = len(categories)
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    colors_list = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C']
    
    for idx, eq_type in enumerate(types):
        values = [
            type_wise[eq_type]['avg_flowrate'],
            type_wise[eq_type]['avg_pressure'],
            type_wise[eq_type]['avg_temperature']
        ]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, label=eq_type, color=colors_list[idx % len(colors_list)])
        ax.fill(angles, values, alpha=0.15, color=colors_list[idx % len(colors_list)])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_title('Equipment Performance Comparison', fontsize=13, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=9)
    ax.grid(True)
    
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer


def generate_pie_chart(type_distribution):
    """Generate pie chart for equipment distribution."""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    types = list(type_distribution.keys())
    counts = list(type_distribution.values())
    colors_list = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C', '#95A5A6']
    
    ax.pie(counts, labels=types, autopct='%1.1f%%', startangle=90, 
           colors=colors_list[:len(types)], textprops={'fontsize': 10})
    ax.set_title('Equipment Type Distribution', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer


def generate_horizontal_bar(type_distribution):
    """Generate horizontal bar chart for equipment counts."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    types = list(type_distribution.keys())
    counts = list(type_distribution.values())
    
    ax.barh(types, counts, color='#3498DB', alpha=0.7)
    ax.set_xlabel('Count', fontsize=11)
    ax.set_ylabel('Equipment Type', fontsize=11)
    ax.set_title('Equipment Type Counts', fontsize=13, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer


def generate_temperature_trend(raw_data):
    """Generate line chart for temperature trend."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    df = pd.DataFrame(raw_data)
    indices = range(len(df))
    
    ax.plot(indices, df['Temperature'], marker='o', markersize=4, 
            linewidth=2, color='#E74C3C', label='Temperature')
    ax.fill_between(indices, df['Temperature'], alpha=0.2, color='#E74C3C')
    
    ax.set_xlabel('Data Point Index', fontsize=11)
    ax.set_ylabel('Temperature', fontsize=11)
    ax.set_title('Temperature Trend Over Data Points', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer


def generate_r2_comparison_chart(ml_metrics):
    """Generate R² score comparison chart."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    params = []
    r2_scores = []
    
    for param in ['flowrate', 'pressure', 'temperature']:
        if param in ml_metrics and ml_metrics[param]:
            params.append(param.capitalize())
            r2_scores.append(ml_metrics[param].get('r2_score', 0) * 100)
    
    colors_list = ['#3498DB', '#E74C3C', '#F39C12']
    ax.bar(params, r2_scores, color=colors_list[:len(params)], alpha=0.7)
    
    ax.set_ylabel('R² Score (%)', fontsize=11)
    ax.set_title('ML Model Accuracy (R² Score)', fontsize=13, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)
    
    for i, v in enumerate(r2_scores):
        ax.text(i, v + 2, f'{v:.2f}%', ha='center', fontweight='bold')
    
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer


def generate_error_metrics_chart(ml_metrics):
    """Generate error metrics (MSE & MAE) comparison chart."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    params = []
    mse_values = []
    mae_values = []
    
    for param in ['flowrate', 'pressure', 'temperature']:
        if param in ml_metrics and ml_metrics[param]:
            params.append(param.capitalize())
            mse_values.append(ml_metrics[param].get('mse', 0))
            mae_values.append(ml_metrics[param].get('mae', 0))
    
    x = np.arange(len(params))
    width = 0.35
    
    ax.bar(x - width/2, mse_values, width, label='MSE', color='#E74C3C', alpha=0.7)
    ax.bar(x + width/2, mae_values, width, label='MAE', color='#3498DB', alpha=0.7)
    
    ax.set_ylabel('Error Value', fontsize=11)
    ax.set_title('Model Error Metrics (MSE & MAE)', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(params)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer


def generate_pdf_report(dataset_history):
    """
    Generate a comprehensive PDF report for a dataset with all charts.
    
    Args:
        dataset_history: DatasetHistory model instance
        
    Returns:
        BytesIO: PDF file buffer
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Title
    title = Paragraph("Chemical Equipment Parameter Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Report metadata
    metadata = [
        ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ['Dataset File:', dataset_history.filename],
        ['Upload Date:', dataset_history.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')],
    ]
    
    metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7F8C8D')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(metadata_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary section
    elements.append(Paragraph("Summary Statistics", heading_style))
    
    summary_data = [
        ['Metric', 'Value'],
        ['Total Equipment Count', str(dataset_history.count)],
        ['Average Flowrate', f"{dataset_history.avg_flowrate:.2f}"],
        ['Average Pressure', f"{dataset_history.avg_pressure:.2f}"],
        ['Average Temperature', f"{dataset_history.avg_temperature:.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Equipment Type Distribution section
    elements.append(Paragraph("Equipment Type Distribution", heading_style))
    
    type_dist_data = [['Equipment Type', 'Count']]
    for eq_type, count in dataset_history.type_distribution.items():
        type_dist_data.append([eq_type, str(count)])
    
    type_table = Table(type_dist_data, colWidths=[3*inch, 3*inch])
    type_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ECC71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(type_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Chart 1: Equipment Type Distribution Bar Chart
    chart_buffer = generate_type_distribution_chart(dataset_history.type_distribution)
    chart_image = Image(chart_buffer, width=6*inch, height=3.5*inch)
    elements.append(chart_image)
    elements.append(PageBreak())
    
    # ===== ADVANCED CHARTS SECTION =====
    elements.append(Paragraph("Advanced Data Analysis Charts", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Get raw data
    raw_data = dataset_history.raw_data
    type_wise = dataset_history.type_wise_breakdown
    
    if raw_data and len(raw_data) > 0:
        # Chart 2: Average Parameters by Equipment Type
        chart = generate_avg_parameters_chart(type_wise)
        elements.append(Image(chart, width=6*inch, height=3.5*inch))
        elements.append(Spacer(1, 0.2*inch))
        
        # Chart 3: All Parameters Trend
        chart = generate_all_parameters_trend(raw_data)
        elements.append(Image(chart, width=6*inch, height=3.5*inch))
        elements.append(PageBreak())
        
        # Chart 4: Flowrate vs Pressure Scatter
        chart = generate_scatter_chart(raw_data, 'Flowrate', 'Pressure')
        elements.append(Image(chart, width=5.5*inch, height=3.5*inch))
        elements.append(Spacer(1, 0.2*inch))
        
        # Chart 5: Pressure vs Temperature Scatter
        chart = generate_scatter_chart(raw_data, 'Pressure', 'Temperature')
        elements.append(Image(chart, width=5.5*inch, height=3.5*inch))
        elements.append(PageBreak())
        
        # Chart 6: Equipment Performance Radar
        chart = generate_radar_chart(type_wise)
        elements.append(Image(chart, width=5.5*inch, height=4*inch))
        elements.append(Spacer(1, 0.2*inch))
        
        # Chart 7: Equipment Type Pie Chart
        chart = generate_pie_chart(dataset_history.type_distribution)
        elements.append(Image(chart, width=5*inch, height=4*inch))
        elements.append(PageBreak())
        
        # Chart 8: Horizontal Bar - Equipment Counts
        chart = generate_horizontal_bar(dataset_history.type_distribution)
        elements.append(Image(chart, width=6*inch, height=3.5*inch))
        elements.append(Spacer(1, 0.2*inch))
        
        # Chart 9: Temperature Trend Line
        chart = generate_temperature_trend(raw_data)
        elements.append(Image(chart, width=6*inch, height=3.5*inch))
        elements.append(PageBreak())
    
    # ===== ML METRICS SECTION =====
    ml_metrics = dataset_history.ml_metrics
    if ml_metrics and (ml_metrics.get('flowrate') or ml_metrics.get('pressure') or ml_metrics.get('temperature')):
        elements.append(Paragraph("Machine Learning Model Performance", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # ML Metrics Summary Table
        ml_summary_data = [['Parameter', 'R² Score', 'MSE', 'MAE', 'RMSE']]
        
        for param in ['flowrate', 'pressure', 'temperature']:
            if param in ml_metrics and ml_metrics[param]:
                metrics = ml_metrics[param]
                ml_summary_data.append([
                    param.capitalize(),
                    f"{metrics.get('r2_score', 0):.4f}",
                    f"{metrics.get('mse', 0):.4f}",
                    f"{metrics.get('mae', 0):.4f}",
                    f"{metrics.get('rmse', 0):.4f}"
                ])
        
        ml_table = Table(ml_summary_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        ml_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9B59B6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(ml_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Chart 10: R² Score Comparison
        chart = generate_r2_comparison_chart(ml_metrics)
        elements.append(Image(chart, width=6*inch, height=3.5*inch))
        elements.append(Spacer(1, 0.2*inch))
        
        # Chart 11: Error Metrics Comparison (MSE & MAE)
        chart = generate_error_metrics_chart(ml_metrics)
        elements.append(Image(chart, width=6*inch, height=3.5*inch))
        elements.append(PageBreak())
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer
