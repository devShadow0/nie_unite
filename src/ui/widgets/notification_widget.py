"""
Notification Widget Module
Displays notification information in a card format
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class NotificationWidget(QWidget):
    """Widget to display notification information"""
    
    def __init__(self, notification_data):
        super().__init__()
        self.notification_data = notification_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the widget UI"""
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Notification icon
        icon = "🔔"
        if 'is_read' in self.notification_data and not self.notification_data['is_read']:
            icon = "🔴"
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px; padding: 10px;")
        layout.addWidget(icon_label)
        
        # Notification info
        info_layout = QVBoxLayout()
        
        # Notification subject
        subject = self.notification_data.get('subject', 'Notification')
        subject_label = QLabel(subject)
        
        # Bold if unread
        if 'is_read' in self.notification_data and not self.notification_data['is_read']:
            subject_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #ecf0f1;
            """)
        else:
            subject_label.setStyleSheet("""
                font-size: 14px;
                color: #bdc3c7;
            """)
        
        subject_label.setWordWrap(True)
        info_layout.addWidget(subject_label)
        
        # Notification details
        details_layout = QHBoxLayout()
        
        # Time
        if 'timecreated' in self.notification_data:
            from datetime import datetime
            timestamp = self.notification_data['timecreated']
            if isinstance(timestamp, (int, float)):
                time_str = datetime.fromtimestamp(timestamp).strftime("%b %d, %Y")
                time_label = QLabel(f"🕐 {time_str}")
                time_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
                details_layout.addWidget(time_label)
        
        # From
        if 'userfrom' in self.notification_data:
            user = self.notification_data['userfrom']
            if isinstance(user, dict):
                from_name = user.get('fullname', 'Unknown')
            else:
                from_name = str(user)
            from_label = QLabel(f"👤 {from_name}")
            from_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
            details_layout.addWidget(from_label)
        
        details_layout.addStretch()
        info_layout.addLayout(details_layout)
        
        layout.addLayout(info_layout)
        
        # Read/Unread indicator
        if 'is_read' in self.notification_data:
            if self.notification_data['is_read']:
                status_label = QLabel("Read")
                status_label.setStyleSheet("""
                    color: #7f8c8d;
                    font-size: 11px;
                    padding: 3px 8px;
                    background-color: #34495e;
                    border-radius: 10px;
                """)
            else:
                status_label = QLabel("New")
                status_label.setStyleSheet("""
                    color: #e74c3c;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 3px 8px;
                    background-color: #4a2a2a;
                    border-radius: 10px;
                """)
            
            layout.addWidget(status_label)
        
        # Set widget style
        self.setStyleSheet("""
            NotificationWidget {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 8px;
                margin: 5px;
                padding: 10px;
            }
            NotificationWidget:hover {
                background-color: #34495e;
                border-color: #3498db;
            }
        """)
        
        # Set fixed height
        self.setFixedHeight(80)