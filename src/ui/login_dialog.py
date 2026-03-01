"""
Login Dialog Module
Handles user login input
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QCheckBox, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from pathlib import Path


class LoginDialog(QDialog):
    """Login dialog for Moodle credentials"""
    
    login_attempt = Signal(str, str, str)  # username, password, url
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Moodle Login")
        self.setFixedSize(450, 350)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        # Set window flags for frameless dialog
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setup_ui()
        self.load_saved_credentials()
    
    def setup_ui(self):
        """Setup the login dialog UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # Title
        title_label = QLabel("🔐 Moodle Login")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #ecf0f1;
            padding: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Subtitle
        subtitle = QLabel("Enter your Moodle credentials")
        subtitle.setStyleSheet("color: #bdc3c7; font-size: 12px;")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Username field
        username_label = QLabel("Username / Email")
        username_label.setStyleSheet("color: #ecf0f1; font-weight: bold;")
        main_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username or email")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
                color: #ecf0f1;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        main_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setStyleSheet("color: #ecf0f1; font-weight: bold;")
        main_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
                color: #ecf0f1;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        main_layout.addWidget(self.password_input)
        
        # Moodle URL field
        url_label = QLabel("Moodle URL")
        url_label.setStyleSheet("color: #ecf0f1; font-weight: bold;")
        main_layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://moodlegurukul.nie.ac.in")
        self.url_input.setText("https://moodlegurukul.nie.ac.in")
        self.url_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
                color: #ecf0f1;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        main_layout.addWidget(self.url_input)
        
        # Options
        options_layout = QHBoxLayout()
        
        self.save_credentials = QCheckBox("Save credentials")
        self.save_credentials.setStyleSheet("color: #ecf0f1;")
        options_layout.addWidget(self.save_credentials)
        
        self.auto_login = QCheckBox("Auto-login")
        self.auto_login.setStyleSheet("color: #ecf0f1;")
        options_layout.addWidget(self.auto_login)
        
        options_layout.addStretch()
        main_layout.addLayout(options_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("🚀 Login")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.login_button.clicked.connect(self.attempt_login)
        button_layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton("✖ Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Made with love text
        love_label = QLabel("Made with ❤️ by devShadow")
        love_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        love_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(love_label)
    
    def load_saved_credentials(self):
        """Load saved credentials from config"""
        username, password = self.config_manager.get_credentials()
        if username:
            self.username_input.setText(username)
            self.password_input.setText(password)
            self.save_credentials.setChecked(True)
        
        moodle_url = self.config_manager.get("moodle_url")
        if moodle_url:
            self.url_input.setText(moodle_url)
        
        self.auto_login.setChecked(self.config_manager.get("auto_login", False))
    
    def attempt_login(self):
        """Attempt login with entered credentials"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        url = self.url_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Missing Information", 
                               "Please enter both username and password")
            return
        
        if not url:
            QMessageBox.warning(self, "Missing Information", 
                               "Please enter the Moodle URL")
            return
        
        # Save settings if requested
        if self.save_credentials.isChecked():
            self.config_manager.set("username", username)
            self.config_manager.set("password", password)
        else:
            self.config_manager.set("username", "")
            self.config_manager.set("password", "")
        
        self.config_manager.set("moodle_url", url)
        self.config_manager.set("auto_login", self.auto_login.isChecked())
        self.config_manager.set("save_credentials", self.save_credentials.isChecked())
        self.config_manager.save_config()
        
        # Emit login signal
        self.login_attempt.emit(username, password, url)
        
        # Close dialog
        self.accept()