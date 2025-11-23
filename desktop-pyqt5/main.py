"""
Chemical Equipment Parameter Visualizer - Desktop Application
Main entry point for PyQt5 desktop application
"""
import sys
from PyQt5.QtWidgets import QApplication
from ui.login_window import LoginWindow

def main():
    """Main function to start the desktop application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Chemical Equipment Visualizer")
    app.setOrganizationName("IIT Bombay")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Show login window
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
