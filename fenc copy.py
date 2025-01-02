from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
                             QLabel, QCheckBox, QGroupBox, QFileDialog, QRadioButton, QButtonGroup, QMessageBox)
from PyQt5.QtCore import Qt
import os
import subprocess
import win32com.shell.shell as shell
from cryptography.fernet import Fernet

class FolCryptorApp(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.init_ui()

        # Initialize encryption key
        self.key = b'xr4IxVuQUPqDJW5A36J5exq8W7ie3t4j9t3asHyD_bI='
        self.fernet = Fernet(self.key)

    def init_ui(self):
        self.setWindowTitle("FolCryptor")
        self.setGeometry(100, 100, 800, 600)
        self.apply_theme()

        main_layout = QVBoxLayout()

        # Menu Section
        menu_group = QGroupBox("Select Type")
        menu_layout = QHBoxLayout()

        self.folder_radio = QRadioButton("Folder")
        self.file_radio = QRadioButton("File")
        self.folder_radio.setChecked(True)

        menu_layout.addWidget(self.folder_radio)
        menu_layout.addWidget(self.file_radio)
        menu_group.setLayout(menu_layout)
        main_layout.addWidget(menu_group)

        # Path Selection Section
        path_group = QGroupBox("Select Target")
        path_layout = QHBoxLayout()

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select a folder or file")

        self.browse_button = QPushButton("Choose")
        self.browse_button.clicked.connect(self.browse_target)

        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)
        path_group.setLayout(path_layout)
        main_layout.addWidget(path_group)

        # Action Selection Section
        actions_group = QGroupBox("Select Actions")
        actions_layout = QHBoxLayout()

        self.encrypt_checkbox = QCheckBox("Encrypt/Decrypt")
        self.lock_checkbox = QCheckBox("Lock/Unlock")
        self.hidden_checkbox = QCheckBox("Hidden/Unhidden")
        self.backup_checkbox = QCheckBox("Backup")

        actions_layout.addWidget(self.encrypt_checkbox)
        actions_layout.addWidget(self.lock_checkbox)
        actions_layout.addWidget(self.hidden_checkbox)
        actions_layout.addWidget(self.backup_checkbox)
        actions_group.setLayout(actions_layout)
        main_layout.addWidget(actions_group)

        # Spacer
        teksaja = QLabel(" ")
        teksaja.setStyleSheet("margin-bottom: 100px; background-color: none;")
        main_layout.addWidget(teksaja)

        # Action Buttons Section
        buttons_layout = QHBoxLayout()

        self.gas_button = QPushButton("GAS")
        self.gas_button.clicked.connect(self.execute_gas)

        self.restore_button = QPushButton("MENGEMBALIKAN")
        self.restore_button.clicked.connect(self.execute_restore)

        buttons_layout.addWidget(self.gas_button)
        buttons_layout.addWidget(self.restore_button)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def apply_theme(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme['background']};
                color: {self.theme['text']};
            }}
            QGroupBox {{
                border: 1px solid {self.theme['border']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                margin-bottom: 20px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }}
            QLineEdit {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 4px;
                padding: 5px;
                color: {self.theme['text']};
            }}
            QPushButton {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 4px;
                padding: 8px;
                color: {self.theme['text']};
            }}
            QPushButton:hover {{
                background-color: {self.theme['button_hover']};
            }}
            QCheckBox {{
                color: {self.theme['text']};
            }}
        """)

    def browse_target(self):
        if self.folder_radio.isChecked():
            target = QFileDialog.getExistingDirectory(self, "Select Folder")
        else:
            target, _ = QFileDialog.getOpenFileName(self, "Select File")

        if target:
            self.path_input.setText(target)
            print(f"Selected target: {target}")

    def execute_gas(self):
        target = self.path_input.text()
        if not target or not os.path.exists(target):
            self.show_message("Error", "File or Directory not found.")
            return

        try:
            if self.encrypt_checkbox.isChecked():
                if self.folder_radio.isChecked():
                    self.encrypt_folder(target)
                else:
                    self.encrypt_file(target)
        except Exception as e:
            self.show_message("Error", str(e))

    def execute_restore(self):
        target = self.path_input.text()
        if not target:
            self.show_message("Error", "Please select a valid target.")
            return

        try:
            if self.encrypt_checkbox.isChecked():
                if self.folder_radio.isChecked():
                    self.decrypt_folder(target)
                else:
                    self.decrypt_file(target)
        except Exception as e:
            self.show_message("Error", str(e))

    def encrypt_folder(self, folder_path):
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower() == "desktop.ini":
                    continue
                file_path = os.path.join(root, file)
                self.encrypt_file(file_path)

    def decrypt_folder(self, folder_path):
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.enc'):
                    self.decrypt_file(os.path.join(root, file))

    def encrypt_file(self, file_path):
        with open(file_path, 'rb') as f:
            data = f.read()
        encrypted_data = self.fernet.encrypt(data)
        with open(file_path + '.enc', 'wb') as f:
            f.write(encrypted_data)
        os.remove(file_path)

        # Set encrypted file icon
        self.set_file_icon(file_path + '.enc', "imej/iconenkrip.ico")

    def decrypt_file(self, file_path):
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = self.fernet.decrypt(encrypted_data)
        original_path = file_path[:-4]
        with open(original_path, 'wb') as f:
            f.write(decrypted_data)
        os.remove(file_path)

        # Refresh file icon to default
        self.refresh_file_icon(original_path)

    def set_file_icon(self, file_path, icon_path):
        desktop_ini_path = os.path.join(os.path.dirname(file_path), "desktop.ini")
        with open(desktop_ini_path, 'w') as f:
            f.write(f"[.ShellClassInfo]\nIconResource={icon_path},0\n")
        os.system(f'attrib +s +h "{desktop_ini_path}"')
        shell.SHChangeNotify(0x00002000, 0x0003, file_path, None)

    def refresh_file_icon(self, file_path):
        shell.SHChangeNotify(0x00002000, 0x0003, file_path, None)

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    theme = {
        "background": "#333333",
        "text": "#FFFFFF",
        "border": "#555555",
        "content_background": "#444444",
        "button_hover": "#555555",
        "accent": "#00AAFF"
    }

    window = FolCryptorApp(theme)
    window.show()
    sys.exit(app.exec_())
