"""
Main Window Module
Main application window with tabs for different data views
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QTabWidget, QPushButton, QLabel, QStatusBar,
                               QProgressBar, QMessageBox, QFileDialog, QMenuBar,
                               QMenu, QToolBar)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize
from PySide6.QtGui import QIcon, QAction, QFont, QPixmap
import qdarkstyle
from pathlib import Path

from ..core.moodle_fetcher import MoodleFetcher
from ..core.data_manager import DataManager
from .login_dialog import LoginDialog
from .settings_dialog import SettingsDialog
from .widgets.course_widget import CourseWidget
from .widgets.event_widget import EventWidget
from .widgets.notification_widget import NotificationWidget


class FetchWorker(QThread):
    """Worker thread for fetching Moodle data"""
    
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(int)
    
    def __init__(self, username, password, url, headless=True, slow_mo=100):
        super().__init__()
        self.username = username
        self.password = password
        self.url = url
        self.headless = headless
        self.slow_mo = slow_mo
    
    def run(self):
        """Run the fetch operation"""
        fetcher = MoodleFetcher(headless=self.headless, slow_mo=self.slow_mo)
        
        try:
            self.progress.emit(20)
            result = fetcher.login(self.username, self.password, self.url)
            
            self.progress.emit(80)
            
            if result['success']:
                self.finished.emit(result)
            else:
                self.error.emit(result['message'])
            
            self.progress.emit(100)
            
        except Exception as e:
            self.error.emit(str(e))
        finally:
            fetcher.close()


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.data_manager = DataManager()
        self.current_data = None
        
        self.setWindowTitle("Moodle Data Fetcher")
        self.setMinimumSize(1200, 800)
        
        self.setup_ui()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()
        
        # Auto-login if enabled
        if self.config_manager.get("auto_login"):
            QTimer.singleShot(500, self.auto_login)
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📊 Moodle Data Dashboard")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #ecf0f1;
            padding: 10px;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.refresh_button = QPushButton("🔄 Refresh Data")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """)
        self.refresh_button.clicked.connect(self.show_login_dialog)
        header_layout.addWidget(self.refresh_button)
        
        self.export_button = QPushButton("📥 Export Data")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """)
        self.export_button.clicked.connect(self.export_data)
        self.export_button.setEnabled(False)
        header_layout.addWidget(self.export_button)
        
        main_layout.addLayout(header_layout)
        
        # Stats bar
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.courses_stats = QLabel("📚 Courses: 0")
        self.courses_stats.setStyleSheet("""
            background-color: #34495e;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
            color: #ecf0f1;
        """)
        stats_layout.addWidget(self.courses_stats)
        
        self.events_stats = QLabel("📅 Events: 0")
        self.events_stats.setStyleSheet("""
            background-color: #34495e;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
            color: #ecf0f1;
        """)
        stats_layout.addWidget(self.events_stats)
        
        self.notifications_stats = QLabel("🔔 Notifications: 0")
        self.notifications_stats.setStyleSheet("""
            background-color: #34495e;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
            color: #ecf0f1;
        """)
        stats_layout.addWidget(self.notifications_stats)
        
        stats_layout.addStretch()
        main_layout.addLayout(stats_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #34495e;
                border-radius: 5px;
                background-color: #2c3e50;
            }
            QTabBar::tab {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
            }
            QTabBar::tab:hover {
                background-color: #2980b9;
            }
        """)
        
        # Create tabs
        self.courses_tab = QWidget()
        self.events_tab = QWidget()
        self.notifications_tab = QWidget()
        self.calendar_tab = QWidget()
        self.recent_tab = QWidget()
        
        # Setup tab layouts
        self.setup_courses_tab()
        self.setup_events_tab()
        self.setup_notifications_tab()
        self.setup_calendar_tab()
        self.setup_recent_tab()
        
        # Add tabs
        self.tab_widget.addTab(self.courses_tab, "📚 Courses")
        self.tab_widget.addTab(self.events_tab, "📅 Events")
        self.tab_widget.addTab(self.notifications_tab, "🔔 Notifications")
        self.tab_widget.addTab(self.calendar_tab, "🗓 Calendar")
        self.tab_widget.addTab(self.recent_tab, "⏱ Recent Courses")
        
        main_layout.addWidget(self.tab_widget)
    
    def setup_courses_tab(self):
        """Setup courses tab"""
        layout = QVBoxLayout()
        self.courses_tab.setLayout(layout)
        
        # Course list will be populated dynamically
        self.courses_container = QWidget()
        self.courses_layout = QVBoxLayout()
        self.courses_container.setLayout(self.courses_layout)
        
        # Add scroll area
        from PySide6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidget(self.courses_container)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        layout.addWidget(scroll)
    
    def setup_events_tab(self):
        """Setup events tab"""
        layout = QVBoxLayout()
        self.events_tab.setLayout(layout)
        
        self.events_container = QWidget()
        self.events_layout = QVBoxLayout()
        self.events_container.setLayout(self.events_layout)
        
        scroll = QScrollArea()
        scroll.setWidget(self.events_container)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
    
    def setup_notifications_tab(self):
        """Setup notifications tab"""
        layout = QVBoxLayout()
        self.notifications_tab.setLayout(layout)
        
        self.notifications_container = QWidget()
        self.notifications_layout = QVBoxLayout()
        self.notifications_container.setLayout(self.notifications_layout)
        
        scroll = QScrollArea()
        scroll.setWidget(self.notifications_container)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
    
    def setup_calendar_tab(self):
        """Setup calendar tab"""
        layout = QVBoxLayout()
        self.calendar_tab.setLayout(layout)
        
        calendar_label = QLabel("Calendar View (Coming Soon)")
        calendar_label.setAlignment(Qt.AlignCenter)
        calendar_label.setStyleSheet("font-size: 18px; color: #7f8c8d; padding: 50px;")
        layout.addWidget(calendar_label)
    
    def setup_recent_tab(self):
        """Setup recent courses tab"""
        layout = QVBoxLayout()
        self.recent_tab.setLayout(layout)
        
        self.recent_container = QWidget()
        self.recent_layout = QVBoxLayout()
        self.recent_container.setLayout(self.recent_layout)
        
        scroll = QScrollArea()
        scroll.setWidget(self.recent_container)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("📁 File")
        
        login_action = QAction("🔐 Login", self)
        login_action.triggered.connect(self.show_login_dialog)
        file_menu.addAction(login_action)
        
        export_menu = file_menu.addMenu("📤 Export")
        
        export_json_action = QAction("Export as JSON", self)
        export_json_action.triggered.connect(lambda: self.export_data('json'))
        export_menu.addAction(export_json_action)
        
        export_csv_action = QAction("Export as CSV", self)
        export_csv_action.triggered.connect(lambda: self.export_data('csv'))
        export_menu.addAction(export_csv_action)
        
        export_excel_action = QAction("Export as Excel", self)
        export_excel_action.triggered.connect(lambda: self.export_data('excel'))
        export_menu.addAction(export_excel_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("❌ Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("⚙ Settings")
        
        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self.show_settings_dialog)
        settings_menu.addAction(preferences_action)
        
        # Help menu
        help_menu = menubar.addMenu("❓ Help")
        
        about_action = QAction("ℹ About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Add actions to toolbar
        toolbar.addAction("🔐 Login", self.show_login_dialog)
        toolbar.addSeparator()
        toolbar.addAction("📥 Export", self.export_data)
        toolbar.addAction("⚙ Settings", self.show_settings_dialog)
        toolbar.addSeparator()
        toolbar.addAction("❓ Help", self.show_about_dialog)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Add status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
    
    def show_login_dialog(self):
        """Show login dialog"""
        dialog = LoginDialog(self.config_manager, self)
        dialog.login_attempt.connect(self.start_fetch)
        dialog.exec()
    
    def show_settings_dialog(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.config_manager, self)
        dialog.exec()
    
    def show_about_dialog(self):
        """Show about dialog"""
        about_text = """
        <h2>🎓 Moodle Data Fetcher</h2>
        <p>Version 2.0.0</p>
        <p>An enterprise-grade application to fetch and visualize Moodle data.</p>
        <p><b>Features:</b><br>
        • Automated Moodle login<br>
        • Fetch courses, events, notifications<br>
        • Export data to JSON, CSV, Excel<br>
        • Modern UI with dark theme<br>
        • Secure credential storage</p>
        <p><b>Made with ❤️ by devShadow</b></p>
        <p>© 2024 All rights reserved</p>
        """
        
        QMessageBox.about(self, "About Moodle Fetcher", about_text)
    
    def auto_login(self):
        """Perform auto-login"""
        username, password = self.config_manager.get_credentials()
        url = self.config_manager.get("moodle_url")
        
        if username and password and url:
            self.start_fetch(username, password, url)
    
    def start_fetch(self, username, password, url):
        """Start fetching data in background thread"""
        # Disable UI elements
        self.refresh_button.setEnabled(False)
        self.export_button.setEnabled(False)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Fetching data...")
        
        # Create and start worker thread
        self.worker = FetchWorker(
            username, password, url,
            headless=self.config_manager.get("headless", True),
            slow_mo=self.config_manager.get("slow_mo", 100)
        )
        self.worker.finished.connect(self.on_fetch_finished)
        self.worker.error.connect(self.on_fetch_error)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.start()
    
    def on_fetch_finished(self, result):
        """Handle fetch completion"""
        self.current_data = result['data']
        
        # Save data to files
        saved_files = self.data_manager.save_data(self.current_data)
        
        # Update UI
        self.update_display()
        self.update_stats()
        
        # Update status
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Data fetched successfully - {result['title']}")
        
        # Enable UI
        self.refresh_button.setEnabled(True)
        self.export_button.setEnabled(True)
        
        # Show success message
        QMessageBox.information(self, "Success", 
                               f"Data fetched successfully!\nSaved to: {saved_files['combined']}")
    
    def on_fetch_error(self, error_message):
        """Handle fetch error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Fetch failed")
        
        # Enable UI
        self.refresh_button.setEnabled(True)
        
        # Show error message
        QMessageBox.critical(self, "Error", f"Failed to fetch data: {error_message}")
    
    def update_display(self):
        """Update the display with current data"""
        if not self.current_data:
            return
        
        # Clear existing widgets
        self.clear_layout(self.courses_layout)
        self.clear_layout(self.events_layout)
        self.clear_layout(self.notifications_layout)
        self.clear_layout(self.recent_layout)
        
        # Add course widgets
        if self.current_data.get('courses'):
            for course in self.current_data['courses']:
                widget = CourseWidget(course)
                self.courses_layout.addWidget(widget)
        else:
            label = QLabel("No courses found")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #7f8c8d; padding: 50px;")
            self.courses_layout.addWidget(label)
        
        # Add event widgets
        if self.current_data.get('events'):
            for event in self.current_data['events']:
                widget = EventWidget(event)
                self.events_layout.addWidget(widget)
        else:
            label = QLabel("No events found")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #7f8c8d; padding: 50px;")
            self.events_layout.addWidget(label)
        
        # Add notification widgets
        if self.current_data.get('notifications'):
            for notification in self.current_data['notifications']:
                widget = NotificationWidget(notification)
                self.notifications_layout.addWidget(widget)
        else:
            label = QLabel("No notifications found")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #7f8c8d; padding: 50px;")
            self.notifications_layout.addWidget(label)
        
        # Add recent course widgets
        if self.current_data.get('recent_courses'):
            for course in self.current_data['recent_courses']:
                widget = CourseWidget(course)
                self.recent_layout.addWidget(widget)
        else:
            label = QLabel("No recent courses found")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #7f8c8d; padding: 50px;")
            self.recent_layout.addWidget(label)
    
    def update_stats(self):
        """Update statistics display"""
        if not self.current_data:
            return
        
        stats = self.data_manager.get_statistics(self.current_data)
        
        if 'courses' in stats:
            courses = stats['courses']
            self.courses_stats.setText(
                f"📚 Courses: {courses['total']} "
                f"({courses['in_progress']} in progress, {courses['completed']} completed)"
            )
        
        if 'events' in stats:
            events = stats['events']
            self.events_stats.setText(
                f"📅 Events: {events['total']} "
                f"({events['upcoming']} upcoming, {events['past']} past)"
            )
        
        if 'notifications' in stats:
            notifications = stats['notifications']
            self.notifications_stats.setText(
                f"🔔 Notifications: {notifications['total']} "
                f"({notifications['unread']} unread)"
            )
    
    def export_data(self, format_type='json'):
        """Export data in specified format"""
        if not self.current_data:
            QMessageBox.warning(self, "No Data", "No data to export. Please fetch data first.")
            return
        
        file_dialog = QFileDialog()
        
        if format_type == 'json':
            file_path, _ = file_dialog.getSaveFileName(
                self, "Save JSON", str(Path.home()), "JSON Files (*.json)")
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_data, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "Success", f"Data exported to {file_path}")
        
        elif format_type == 'csv':
            # Ask which data type to export
            items = ["courses", "events", "notifications", "recent_courses"]
            from PySide6.QtWidgets import QInputDialog
            data_type, ok = QInputDialog.getItem(
                self, "Export CSV", "Select data type to export:", items, 0, False)
            
            if ok and data_type:
                file_path = self.data_manager.export_to_csv(self.current_data, data_type)
                if file_path:
                    QMessageBox.information(self, "Success", f"Data exported to {file_path}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to export data")
        
        elif format_type == 'excel':
            file_path = self.data_manager.export_to_excel(self.current_data)
            if file_path:
                QMessageBox.information(self, "Success", f"Data exported to {file_path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to export data")
    
    def clear_layout(self, layout):
        """Clear all widgets from a layout"""
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()