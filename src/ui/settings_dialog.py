"""
Settings Dialog Module
Handles application settings
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QCheckBox, QSpinBox,
                               QComboBox, QTabWidget, QWidget, QGroupBox,
                               QMessageBox)
from PySide6.QtCore import Qt


class SettingsDialog(QDialog):
    """Settings dialog for application configuration"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Settings")
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings dialog UI"""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # General tab
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "General")
        
        # Browser tab
        browser_tab = self.create_browser_tab()
        tab_widget.addTab(browser_tab, "Browser")
        
        # Data tab
        data_tab = self.create_data_tab()
        tab_widget.addTab(data_tab, "Data")
        
        # Appearance tab
        appearance_tab = self.create_appearance_tab()
        tab_widget.addTab(appearance_tab, "Appearance")
        
        main_layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """Create general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Moodle URL
        url_group = QGroupBox("Moodle Configuration")
        url_layout = QVBoxLayout()
        
        url_label = QLabel("Moodle URL:")
        self.url_input = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)
        
        # Login options
        login_group = QGroupBox("Login Options")
        login_layout = QVBoxLayout()
        
        self.auto_login = QCheckBox("Auto-login on startup")
        login_layout.addWidget(self.auto_login)
        
        self.save_credentials = QCheckBox("Save credentials (encrypted)")
        login_layout.addWidget(self.save_credentials)
        
        login_group.setLayout(login_layout)
        layout.addWidget(login_group)
        
        # Notifications
        notif_group = QGroupBox("Notifications")
        notif_layout = QVBoxLayout()
        
        self.notifications_enabled = QCheckBox("Enable desktop notifications")
        notif_layout.addWidget(self.notifications_enabled)
        
        notif_group.setLayout(notif_layout)
        layout.addWidget(notif_group)
        
        layout.addStretch()
        return tab
    
    def create_browser_tab(self):
        """Create browser settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Browser options
        browser_group = QGroupBox("Browser Options")
        browser_layout = QVBoxLayout()
        
        self.headless = QCheckBox("Run in headless mode (no visible browser)")
        browser_layout.addWidget(self.headless)
        
        # Slow motion
        slow_mo_layout = QHBoxLayout()
        slow_mo_label = QLabel("Slow motion (ms):")
        self.slow_mo = QSpinBox()
        self.slow_mo.setRange(0, 1000)
        self.slow_mo.setSingleStep(50)
        self.slow_mo.setSuffix(" ms")
        slow_mo_layout.addWidget(slow_mo_label)
        slow_mo_layout.addWidget(self.slow_mo)
        slow_mo_layout.addStretch()
        browser_layout.addLayout(slow_mo_layout)
        
        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)
        
        # Timeout settings
        timeout_group = QGroupBox("Timeouts")
        timeout_layout = QVBoxLayout()
        
        timeout_input_layout = QHBoxLayout()
        timeout_label = QLabel("Page load timeout (seconds):")
        self.timeout = QSpinBox()
        self.timeout.setRange(10, 120)
        self.timeout.setSuffix(" s")
        timeout_input_layout.addWidget(timeout_label)
        timeout_input_layout.addWidget(self.timeout)
        timeout_input_layout.addStretch()
        timeout_layout.addLayout(timeout_input_layout)
        
        timeout_group.setLayout(timeout_layout)
        layout.addWidget(timeout_group)
        
        layout.addStretch()
        return tab
    
    def create_data_tab(self):
        """Create data settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Data refresh
        refresh_group = QGroupBox("Data Refresh")
        refresh_layout = QVBoxLayout()
        
        refresh_input_layout = QHBoxLayout()
        refresh_label = QLabel("Auto-refresh interval (seconds):")
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(0, 3600)
        self.refresh_interval.setSpecialValueText("Disabled")
        self.refresh_interval.setSuffix(" s")
        refresh_input_layout.addWidget(refresh_label)
        refresh_input_layout.addWidget(self.refresh_interval)
        refresh_input_layout.addStretch()
        refresh_layout.addLayout(refresh_input_layout)
        
        refresh_group.setLayout(refresh_layout)
        layout.addWidget(refresh_group)
        
        # Export settings
        export_group = QGroupBox("Export Settings")
        export_layout = QVBoxLayout()
        
        self.default_export_format = QComboBox()
        self.default_export_format.addItems(["JSON", "CSV", "Excel"])
        export_layout.addWidget(QLabel("Default export format:"))
        export_layout.addWidget(self.default_export_format)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        layout.addStretch()
        return tab
    
    def create_appearance_tab(self):
        """Create appearance settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Theme
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        
        self.theme = QComboBox()
        self.theme.addItems(["Dark", "Light", "System"])
        theme_layout.addWidget(QLabel("Application theme:"))
        theme_layout.addWidget(self.theme)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        layout.addStretch()
        return tab
    
    def load_settings(self):
        """Load settings from config manager"""
        self.url_input.setText(self.config_manager.get("moodle_url", ""))
        self.auto_login.setChecked(self.config_manager.get("auto_login", False))
        self.save_credentials.setChecked(self.config_manager.get("save_credentials", False))
        self.notifications_enabled.setChecked(self.config_manager.get("notifications_enabled", True))
        self.headless.setChecked(self.config_manager.get("headless", True))
        self.slow_mo.setValue(self.config_manager.get("slow_mo", 100))
        self.timeout.setValue(self.config_manager.get("timeout", 30))
        self.refresh_interval.setValue(self.config_manager.get("data_refresh_interval", 300))
        
        theme = self.config_manager.get("theme", "dark")
        theme_index = 0 if theme == "dark" else 1 if theme == "light" else 2
        self.theme.setCurrentIndex(theme_index)
        
        export_format = self.config_manager.get("default_export_format", "JSON")
        self.default_export_format.setCurrentText(export_format)
    
    def save_settings(self):
        """Save settings to config manager"""
        self.config_manager.set("moodle_url", self.url_input.text())
        self.config_manager.set("auto_login", self.auto_login.isChecked())
        self.config_manager.set("save_credentials", self.save_credentials.isChecked())
        self.config_manager.set("notifications_enabled", self.notifications_enabled.isChecked())
        self.config_manager.set("headless", self.headless.isChecked())
        self.config_manager.set("slow_mo", self.slow_mo.value())
        self.config_manager.set("timeout", self.timeout.value())
        self.config_manager.set("data_refresh_interval", self.refresh_interval.value())
        
        themes = ["dark", "light", "system"]
        self.config_manager.set("theme", themes[self.theme.currentIndex()])
        
        self.config_manager.set("default_export_format", self.default_export_format.currentText())
        
        if self.config_manager.save_config():
            QMessageBox.information(self, "Success", "Settings saved successfully")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save settings")