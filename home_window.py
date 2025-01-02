from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QFrame, QScrollArea, QStackedWidget, QGraphicsBlurEffect, QGraphicsOpacityEffect)
from PyQt5.QtCore import QTimer, Qt, QSize  # Tambahkan QSize di sini
from PyQt5.QtGui import QIcon
import subprocess
import platform
from seblak.content_widget import ContentWidget
from seblak.theme_manager import ThemeManager

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = ThemeManager.LIGHT_THEME
        self.active_menu = None
        self.sidebar_expanded = True
        self.menu_buttons = {}
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        self.setWindowTitle("ZeroDefender App")
        self.setMinimumSize(1200, 800)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(10, 10, 10, 10)

        # Toggle sidebar button
        toggle_btn = QPushButton()
        toggle_btn.setIcon(QIcon("imej/sidebar.png"))
        toggle_btn.setObjectName("toggleSidebar")
        toggle_btn.clicked.connect(self.toggle_sidebar)
        toggle_btn.setCursor(Qt.PointingHandCursor)
        top_bar_layout.addWidget(toggle_btn, alignment=Qt.AlignLeft)
        toggle_btn.setIconSize(QSize(50, 50))

        # App title
        self.app_title = QLabel("ZERO-DEFENDER APP")
        self.app_title.setObjectName("appTitle")
        top_bar_layout.addWidget(self.app_title, alignment=Qt.AlignLeft)

        # Ping label
        self.ping_label = QLabel("Ping: --")
        self.ping_label.setStyleSheet(f"margin-left: 300px; color: {self.current_theme['accent']}; font-size: 14px; ")
        top_bar_layout.addWidget(self.ping_label, alignment=Qt.AlignRight)

        # Theme toggle button
        self.theme_toggle = QPushButton()
        self.theme_toggle.setIcon(QIcon("imej/theme.png"))
        self.theme_toggle.clicked.connect(self.toggle_theme)
        self.theme_toggle.setCursor(Qt.PointingHandCursor)
        self.theme_toggle.setObjectName("themeToggle")
        top_bar_layout.addWidget(self.theme_toggle, alignment=Qt.AlignRight)

        main_layout.addWidget(top_bar)

        # Content area
        self.content_widget = QWidget()  # Main content widget
        self.content_widget.setObjectName("contentWidget")
        content_layout = QHBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar with scroll area
        self.sidebar_container = QFrame()
        self.sidebar_container.setObjectName("sidebar")
        self.sidebar_container.setFixedWidth(250)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(156, 163, 175, 0.5);
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        sidebar_widget = QWidget()
        sidebar_widget.setStyleSheet("background-color: transparent;")  # Make entire sidebar content transparent
        self.sidebar_layout = QVBoxLayout(sidebar_widget)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(5)

        # Menu items with icons
        self.menu_items = [
            "HOME", "REVSHELL GENERATOR", "HASH GENERATOR",
            "REVIP DOMAIN CHECK", "SUBDO FINDER", "DOMAIN INFO",
            "PORT SCANNER", "DB VULNERABILITY", "SHODAN DORKING",
            "FOLDER ENCRYPTOR", "ENCODING KODE", "WEB SEO ANALYSIS",
            "SQLI SCANNER", "GABUT TOOLS", "CHECK UPDATE", "ABOUT"
        ]

        menu_icons = {
            "HOME": "home.png",
            "REVSHELL GENERATOR": "revshell.png",
            "HASH GENERATOR": "hash.png",
            "REVIP DOMAIN CHECK": "revip.png",
            "SUBDO FINDER": "subdofind.png",
            "DOMAIN INFO": "domaininfo.png",
            "PORT SCANNER": "nmap.png",
            "DB VULNERABILITY": "vulndb.png",
            "SHODAN DORKING": "shodan.png",
            "FOLDER ENCRYPTOR": "encrypt.png",
            "ENCODING KODE": "obfuscator.png",
            "WEB SEO ANALYSIS": "alexa.png",
            "SQLI SCANNER": "sqlinjection.png",
            "GABUT TOOLS": "gab ut.png",
            "CHECK UPDATE": "update.png",
            "ABOUT": "about.png"
        }

        for item in self.menu_items:
            btn = QPushButton(item)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, x=item: self.switch_content(x))
            btn.setObjectName(f"menu_{item}")
            if item in menu_icons:
                btn.setIcon(QIcon(f"imej/{menu_icons[item]}"))
                btn.setIconSize(QSize(40, 40))  # Retain icon size
            btn.setProperty("active", False)
            btn.setProperty("class", "menu-button")
            self.menu_buttons[item] = btn
            self.sidebar_layout.addWidget(btn)

        scroll_area.setWidget(sidebar_widget)
        self.sidebar_container.setLayout(QVBoxLayout())
        self.sidebar_container.layout().addWidget(scroll_area)
        content_layout.addWidget(self.sidebar_container)

        # Stack widget for content
        self.stack = QStackedWidget()
        self.stack.addWidget(ContentWidget("HOME", self.current_theme))
        content_layout.addWidget(self.stack)

        main_layout.addWidget(self.content_widget)

        # Timer for ping updates
        self.ping_timer = QTimer(self)
        self.ping_timer.timeout.connect(self.update_ping)
        self.ping_timer.start(2000)  # Update every 2 seconds

    def apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.current_theme['background']};
            }}
            #topBar {{
                background-color: {self.current_theme['sidebar_background']};
                border-bottom: 1px solid {self.current_theme['border']};
                padding: 10px;
            }}
            #sidebar {{
                background-color: {self.current_theme['sidebar_background']};
            }}
            #contentWidget {{
                background-color: {self.current_theme['background']};
                
            }}
            QPushButton[class="menu-button"] {{
                background-color: {self.current_theme['background']};
                color: {self.current_theme['text']};
                border-radius: 8px;
                text-align: left;
                border: none;
                font-size: 14px;
                width: 90px;
            }}
            QPushButton[class="menu-button"]:hover {{
                background-color: {self.current_theme['button_hover']};
            }}
            QPushButton[active="true"] {{
                background-color: {self.current_theme['menu_active']};
                color: {self.current_theme['accent']};
                font-weight: bold;
            }}
            #appTitle {{
                color: {self.current_theme['text']};
                font-size: 25px;
                font-weight: bold;
                margin-left: -10px;
            }}
            #toggleSidebar, #themeToggle {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
                min-width: 50px;
                max-width: 50px;
                height: 50px
            }}
            #toggleSidebar:hover, #themeToggle:hover {{
                background-color: {self.current_theme['button_hover']};
            }}
        """)

    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.sidebar_container.setFixedWidth(60)
            for btn in self.menu_buttons.values():
                btn.setText("")
                btn.setStyleSheet(f"""
                    padding-bottom: 20px;
                    background-color: transparent;
                    color: {self.current_theme['text']};
                    border-radius: 8px;
                    margin-left: -6px;
                """)
        else:
            self.sidebar_container.setFixedWidth(250)
            for item, btn in self.menu_buttons.items():
                btn.setText(item)
                btn.setStyleSheet("")
        
        self.sidebar_expanded = not self.sidebar_expanded

    def update_ping(self):
        if self.ping_label:
            self.ping_label.setText(self.check_ping())

    def check_ping(self):
        try:
            ping_command = (
                ["ping", "-n", "1", "8.8.8.8"] if platform.system() == "Windows"
                else ["ping", "-c", "1", "8.8.8.8"]
            )
            ping_result = subprocess.run(
                ping_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if ping_result.returncode == 0:
                output = ping_result.stdout.lower()
                if "time=" in output:
                    latency = float(
                        output.split("time=")[-1].split(" ")[0].replace("ms", "")
                    )
                    return f"Ping: <font color='{self.current_theme['accent']}'>{latency} ms</font>"
            return f"Ping: <font color='red'>Failed</font>"
        except Exception as e:
            return f"Ping: <font color='red'>{str(e)}</font>"

    def toggle_theme(self):
        self.current_theme = ThemeManager.LIGHT_THEME if self.current_theme == ThemeManager.DARK_THEME else ThemeManager.DARK_THEME
        self.apply_theme()
        self.switch_content(self.active_menu or "HOME")

    def switch_content(self, title):
        self.active_menu = title
        
        # Update active menu button
        for item, btn in self.menu_buttons.items():
            btn.setProperty("active", item == title)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        # Clear and add new content
        widget = ContentWidget(title, self.current_theme)
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)
