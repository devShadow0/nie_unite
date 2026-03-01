import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
import qdarkstyle

from src.ui.splash_screen import SplashScreen
from src.ui.main_window import MainWindow
from src.core.config_manager import ConfigManager


def main():
    """Main application entry point"""
    
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Moodle Fetcher")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("devShadow")
    
    # Set application icon
    icon_path = Path(__file__).parent / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Apply dark theme
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    
    # Create and show splash screen
    splash = SplashScreen()
    splash.show()
    
    # Process events to show splash immediately
    app.processEvents()
    
    # Initialize config manager
    config_manager = ConfigManager()
    
    # Create main window (but don't show yet)
    main_window = MainWindow(config_manager)
    
    # Timer to simulate loading and transition to main window
    def finish_loading():
        splash.finish(main_window)
        main_window.show()
    
    # Simulate loading time and show main window
    QTimer.singleShot(3000, finish_loading)
    
    # Execute application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()