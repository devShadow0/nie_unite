"""
Course Widget Module
Displays course information in a card format
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class CourseWidget(QWidget):
    """Widget to display course information"""
    
    def __init__(self, course_data):
        super().__init__()
        self.course_data = course_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the widget UI"""
        # Main layout
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Course icon
        icon_label = QLabel("📘")
        icon_label.setStyleSheet("font-size: 32px; padding: 10px;")
        layout.addWidget(icon_label)
        
        # Course info
        info_layout = QVBoxLayout()
        
        # Course name
        name = self.course_data.get('fullname', self.course_data.get('name', 'Unknown Course'))
        name_label = QLabel(name)
        name_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #ecf0f1;
        """)
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)
        
        # Course details
        details_layout = QHBoxLayout()
        
        # Course ID or code
        if 'id' in self.course_data:
            id_label = QLabel(f"ID: {self.course_data['id']}")
            id_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
            details_layout.addWidget(id_label)
        
        # Progress if available
        if 'progress' in self.course_data:
            progress = self.course_data['progress']
            progress_label = QLabel(f"Progress: {progress}%")
            progress_label.setStyleSheet("color: #3498db; font-size: 12px;")
            details_layout.addWidget(progress_label)
        
        details_layout.addStretch()
        info_layout.addLayout(details_layout)
        
        # Progress bar if available
        if 'progress' in self.course_data and self.course_data['progress'] is not None:
            progress_bar = QProgressBar()
            progress_bar.setValue(self.course_data['progress'])
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    background-color: #34495e;
                    border-radius: 3px;
                    height: 8px;
                    max-width: 200px;
                }
                QProgressBar::chunk {
                    background-color: #3498db;
                    border-radius: 3px;
                }
            """)
            info_layout.addWidget(progress_bar)
        
        layout.addLayout(info_layout)
        
        # Set widget style
        self.setStyleSheet("""
            CourseWidget {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 8px;
                margin: 5px;
                padding: 10px;
            }
            CourseWidget:hover {
                background-color: #34495e;
                border-color: #3498db;
            }
        """)
        
        # Set fixed height
        self.setFixedHeight(100)