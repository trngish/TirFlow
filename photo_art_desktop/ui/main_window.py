"""
Main Window with Fluent Design navigation
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

from qfluentwidgets import NavigationWidget, NavigationItemPosition, FluentWindow
from qfluentwidgets import SubtitleLabel, setFont


class MainWindow(FluentWindow):
    """Main application window with navigation"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PhotoArt Desktop")
        self.setMinimumSize(1200, 800)

        # Create navigation items
        self.setup_navigation()

        # Import pages
        from ui.pages.preprocess_page import PreprocessPage
        from ui.pages.train_page import TrainPage
        from ui.pages.generate_page import GeneratePage
        from ui.pages.system_page import SystemPage

        self.preprocess_page = PreprocessPage()
        self.train_page = TrainPage()
        self.generate_page = GeneratePage()
        self.system_page = SystemPage()

        # Add pages to navigation
        self.addSubInterface(self.preprocess_page, textual="Preprocess")
        self.addSubInterface(self.train_page, textual="Training")
        self.addSubInterface(self.generate_page, textual="Generate")
        self.addSubInterface(self.system_page, textual="About")

        # Set default page
        self.navigationInterface.setCurrentItem("Preprocess")

    def setup_navigation(self):
        """Setup navigation interface"""
        self.navigationInterface.setExpandWidth(180)
