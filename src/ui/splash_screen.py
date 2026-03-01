"""
Splash Screen Module
Shows loading animation while app initializes
"""

from PySide6.QtWidgets import QSplashScreen, QProgressBar, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer, Property, QEasingCurve, QPropertyAnimation
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient, QBrush
from pathlib import Path


class AnimatedSplashScreen(QSplashScreen):
    """Custom animated splash screen"""
    
    def __init__(self):
        # Create a pixmap for the splash
        pixmap = QPixmap(600, 400)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        super().__init__(pixmap)
        
        self._opacity = 1.0
        self.progress = 0
        
        # Setup animation
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(2000)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Create progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(150, 300, 300, 10)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #2d2d2d;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #9b59b6);
                border-radius: 5px;
            }
        """)
        
        # Start animation
        self.animation.start()
    
    def get_opacity(self):
        return self._opacity
    
    def set_opacity(self, value):
        self._opacity = value
        self.update()
    
    opacity = Property(float, get_opacity, set_opacity)
    
    def drawContents(self, painter):
        """Custom paint event"""
        painter.setOpacity(self._opacity)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(44, 62, 80))
        gradient.setColorAt(1, QColor(52, 73, 94))
        painter.fillRect(self.rect(), QBrush(gradient))
        
        # Draw logo/text
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 36, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "🎓 Moodle\nFetcher")
        
        # Draw "Made with love by devShadow"
        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(self.rect().adjusted(0, 100, 0, 0), 
                        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom, 
                        "Made with ❤️ by devShadow")
        
        # Update progress bar
        self.progress_bar.setValue(self.progress)
        self.progress_bar.repaint()


class SplashScreen(QWidget):
    """Main splash screen widget"""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set fixed size
        self.setFixedSize(600, 400)
        
        # Center on screen
        self.center_on_screen()
        
        # Setup UI
        self.setup_ui()
        
        # Animation timer
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)
    
    def center_on_screen(self):
        """Center window on screen"""
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def setup_ui(self):
        """Setup splash screen UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Create animated splash
        self.splash = AnimatedSplashScreen()
        layout.addWidget(self.splash)
    
    def update_progress(self):
        """Update progress bar"""
        self.progress += 2
        self.splash.progress = self.progress
        
        if self.progress >= 100:
            self.timer.stop()
        
        self.splash.update()
    
    def finish(self, widget):
        """Finish splash and show main window"""
        self.close()
        widget.show()
    
    def paintEvent(self, event):
        """Paint the splash screen"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw shadow
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 50))
        painter.drawRoundedRect(self.rect().adjusted(5, 5, -5, -5), 20, 20)
        
        # Draw main background
        painter.setBrush(QColor(44, 62, 80))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -10, -10), 20, 20)