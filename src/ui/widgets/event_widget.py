"""
Event Widget Module
Displays event information in a card format
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont


class EventWidget(QWidget):
    """Widget to display event information"""
    
    def __init__(self, event_data):
        super().__init__()
        self.event_data = event_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the widget UI"""
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Event icon (based on type)
        icon = "📅"
        if 'is_past' in self.event_data and self.event_data['is_past']:
            icon = "✅"
        elif 'priority' in self.event_data and self.event_data['priority'] == 'high':
            icon = "⚠️"
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px; padding: 10px;")
        layout.addWidget(icon_label)
        
        # Event info
        info_layout = QVBoxLayout()
        
        # Event name
        name = self.event_data.get('name', 'Unknown Event')
        name_label = QLabel(name)
        name_label.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #ecf0f1;
        """)
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)
        
        # Event details
        details_layout = QHBoxLayout()
        
        # Event time
        if 'timestart' in self.event_data:
            timestamp = self.event_data['timestart']
            if isinstance(timestamp, (int, float)):
                datetime = QDateTime.fromSecsSinceEpoch(timestamp)
                time_str = datetime.toString("MMM d, yyyy h:mm AP")
                time_label = QLabel(f"🕐 {time_str}")
                time_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
                details_layout.addWidget(time_label)
        
        # Event course
        if 'course' in self.event_data:
            course_name = self.event_data['course'].get('fullname', 'Unknown Course')
            course_label = QLabel(f"📚 {course_name}")
            course_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
            details_layout.addWidget(course_label)
        
        details_layout.addStretch()
        info_layout.addLayout(details_layout)
        
        layout.addLayout(info_layout)
        
        # Status indicator
        if 'is_past' in self.event_data and self.event_data['is_past']:
            status_label = QLabel("Past")
            status_label.setStyleSheet("""
                color: #7f8c8d;
                font-size: 12px;
                padding: 5px 10px;
                background-color: #34495e;
                border-radius: 10px;
            """)
        else:
            status_label = QLabel("Upcoming")
            status_label.setStyleSheet("""
                color: #27ae60;
                font-size: 12px;
                padding: 5px 10px;
                background-color: #1e4a2e;
                border-radius: 10px;
            """)
        
        layout.addWidget(status_label)
        
        # Set widget style
        self.setStyleSheet("""
            EventWidget {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 8px;
                margin: 5px;
                padding: 10px;
            }
            EventWidget:hover {
                background-color: #34495e;
                border-color: #3498db;
            }
        """)
        
        # Set fixed height
        self.setFixedHeight(90)