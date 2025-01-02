from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from seblak.home_window import HomeWindow
from seblak.theme_manager import ThemeManager

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = ThemeManager.LIGHT_THEME
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        self.setWindowTitle("ZeroDefender - Login")
        self.setFixedSize(400, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(25)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.png").scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Welcome text
        welcome_label = QLabel("Welcome to ZeroDefender")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(welcome_label)

        # Form container
        form_container = QWidget()
        form_container.setObjectName("formContainer")
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)

        # Password
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setMinimumSize(280, 45)
        # Tambahkan event handler untuk tombol Enter
        self.password.returnPressed.connect(self.check_login)
        form_layout.addWidget(self.password)

        # Login button
        self.login_btn = QPushButton("LOGIN")
        self.login_btn.setMinimumSize(280, 45)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.check_login)
        form_layout.addWidget(self.login_btn)

        layout.addWidget(form_container)

        # Theme toggle
        self.theme_toggle = QPushButton()
        self.theme_toggle.setIcon(QIcon("imej/theme.png"))
        self.theme_toggle.setFixedSize(40, 40)
        self.theme_toggle.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_toggle, alignment=Qt.AlignRight)

    def check_login(self):
        if self.password.text() == "qwerty666":
            self.home_window = HomeWindow()
            self.home_window.show()
            self.close()
        else:
            error_messages = [
                "Waduh! Password-nya kayak orang lagi nyari sinyal - nggak nyambung! 😅",
                "Hmm... Password-nya kayak es krim di tengah padang pasir - mencair! 🍦",
                "Ups! Password-nya kayak kopi tanpa gula - kurang pas! ☕",
                "Duh! Password-nya kayak WiFi tetangga - keprotect! 🔐",
                "Wah, password-nya kayak payung di musim kemarau - nggak cocok! ☂️",
                "Password-nya kayak kentang goreng dingin - kurang kriuk! 🍟",
                "Hmm... Password-nya kayak martabak tanpa telur - ada yang kurang! 🥘",
                "Password-nya kayak sepatu kekecilan - nggak pas! 👟",
                "Wah, password-nya kayak nasi tanpa lauk - belum lengkap! 🍚",
                "Password-nya kayak bantal tanpa kasur - kurang nyaman! 🛏️"
            ]
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(random.choice(error_messages))
            msg.setWindowTitle("Yah... Coba Lagi Ya!")
            msg.exec_()

    def apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.current_theme['background']};
            }}
            QLabel {{
                color: {self.current_theme['text']};
            }}
            #formContainer {{
                background-color: {self.current_theme['content_background']};
                border-radius: 15px;
                padding: 20px;
            }}
            QLineEdit {{
                padding: 10px 15px;
                border: 2px solid {self.current_theme['accent']};
                border-radius: 10px;
                background-color: {self.current_theme['background']};
                color: {self.current_theme['text']};
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {self.current_theme['accent']};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.current_theme['button_hover']};
            }}
        """)

    def toggle_theme(self):
        self.current_theme = ThemeManager.DARK_THEME if self.current_theme == ThemeManager.LIGHT_THEME else ThemeManager.LIGHT_THEME
        self.apply_theme()

    def check_login(self):
        if self.password.text() == "qwerty666":
            self.home_window = HomeWindow()
            self.home_window.show()
            self.close()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Invalid password!")