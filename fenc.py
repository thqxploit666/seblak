from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
                             QLabel, QCheckBox, QGroupBox, QFileDialog, QRadioButton, 
                             QButtonGroup, QMessageBox, QProgressBar, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os
import subprocess
import win32com.shell.shell as shell
from cryptography.fernet import Fernet
import sys

class WorkerThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, operation_type, params):
        super().__init__()
        self.operation_type = operation_type
        self.params = params
        self.fernet = Fernet(params.get('key'))
        
    def run(self):
        try:
            if self.operation_type == 'encrypt_folder':
                self.encrypt_folder(self.params['path'])
            elif self.operation_type == 'decrypt_folder':
                self.decrypt_folder(self.params['path'])
            elif self.operation_type == 'encrypt_file':
                self.encrypt_single_file(self.params['path'])
            elif self.operation_type == 'decrypt_file':
                self.decrypt_single_file(self.params['path'])
            
            self.finished.emit(True, "Operation completed successfully")
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def encrypt_folder(self, folder_path):
        total_files = sum([len(files) for _, _, files in os.walk(folder_path)])
        processed_files = 0
        
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower() == "desktop.ini" or file.endswith('.enc'):
                    continue
                    
                file_path = os.path.join(root, file)
                self.encrypt_single_file(file_path)
                
                processed_files += 1
                progress = int((processed_files / total_files) * 100)
                self.progress.emit(progress)
    
    def decrypt_folder(self, folder_path):
        total_files = sum([len(files) for _, _, files in os.walk(folder_path)])
        processed_files = 0
        
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.enc'):
                    file_path = os.path.join(root, file)
                    self.decrypt_single_file(file_path)
                    
                    processed_files += 1
                    progress = int((processed_files / total_files) * 100)
                    self.progress.emit(progress)
    
    def encrypt_single_file(self, file_path):
        with open(file_path, 'rb') as f:
            data = f.read()
        encrypted_data = self.fernet.encrypt(data)
        with open(file_path + '.enc', 'wb') as f:
            f.write(encrypted_data)
        os.remove(file_path)
        
    def decrypt_single_file(self, file_path):
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = self.fernet.decrypt(encrypted_data)
        with open(file_path[:-4], 'wb') as f:
            f.write(decrypted_data)
        os.remove(file_path)

class FolCryptorApp(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.key = b'xr4IxVuQUPqDJW5A36J5exq8W7ie3t4j9t3asHyD_bI='
        self.fernet = Fernet(self.key)
        self.worker = None
        self.init_ui()

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

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Spacer
        spacer = QLabel(" ")
        spacer.setStyleSheet("margin-bottom: 100px; background-color: none;")
        main_layout.addWidget(spacer)

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
        else:
            print("No target selected")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def operation_finished(self, success, message):
        self.progress_bar.setVisible(False)
        self.enable_ui(True)
        
        if success:
            self.show_message("Success", message)
        else:
            self.show_message("Error", message)

    def enable_ui(self, enabled):
        self.gas_button.setEnabled(enabled)
        self.restore_button.setEnabled(enabled)
        self.path_input.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
        self.folder_radio.setEnabled(enabled)
        self.file_radio.setEnabled(enabled)
        self.encrypt_checkbox.setEnabled(enabled)
        self.lock_checkbox.setEnabled(enabled)
        self.hidden_checkbox.setEnabled(enabled)
        self.backup_checkbox.setEnabled(enabled)

    def execute_gas(self):
        target = self.path_input.text()
        if not target or not os.path.exists(target):
            self.show_message("Error", "File or Directory not found.")
            return

        if self.encrypt_checkbox.isChecked():
            self.enable_ui(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            params = {
                'path': target,
                'key': self.key
            }

            self.worker = WorkerThread(
                'encrypt_folder' if self.folder_radio.isChecked() else 'encrypt_file',
                params
            )
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.operation_finished)
            self.worker.start()

        if self.hidden_checkbox.isChecked():
            try:
                self.hide_target(target)
            except Exception as e:
                self.show_message("Error", f"Hide failed: {str(e)}")

        if self.backup_checkbox.isChecked():
            try:
                self.backup_target(target)
            except Exception as e:
                self.show_message("Error", f"Backup failed: {str(e)}")

        if self.lock_checkbox.isChecked():
            try:
                self.lock_target(target)
            except Exception as e:
                self.show_message("Error", f"Lock failed: {str(e)}")

    def execute_restore(self):
        target = self.path_input.text()
        if not target:
            self.show_message("Error", "Please select a valid target.")
            return

        if self.lock_checkbox.isChecked():
            try:
                self.unlock_target(target)
            except Exception as e:
                self.show_message("Error", f"Unlock failed: {str(e)}")
                return  # Stop further actions if unlocking fails

        if self.encrypt_checkbox.isChecked():
            self.enable_ui(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            params = {
                'path': target,
                'key': self.key
            }

            self.worker = WorkerThread(
                'decrypt_folder' if self.folder_radio.isChecked() else 'decrypt_file',
                params
            )
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.operation_finished)
            self.worker.start()

        if self.hidden_checkbox.isChecked():
            try:
                self.unhide_target(target)
            except Exception as e:
                self.show_message("Error", f"Unhide failed: {str(e)}")

    def lock_target(self, target):
        desktop_ini_path = os.path.join(target, "desktop.ini")
        try:
            self.set_folder_icon(target, "imej/betmut.ico")
            subprocess.run(['icacls', desktop_ini_path, '/grant', 'Everyone:(R)', '/C'], check=True, shell=True)
            os.system(f'attrib +s +h "{desktop_ini_path}"')
            subprocess.run(['icacls', target, '/inheritance:r', '/deny', 'Everyone:(F)', '/T', '/C'], check=True, shell=True)
        except Exception as e:
            print(f"Error locking target: {str(e)}")

    def unlock_target(self, target):
        try:
            subprocess.run(['icacls', target, '/reset', '/T', '/C'], check=True, shell=True)
            desktop_ini_path = os.path.join(target, "desktop.ini")
            if os.path.exists(desktop_ini_path):
                os.remove(desktop_ini_path)
            os.system(f'attrib -r -s -h "{target}"')
        except Exception as e:
            print(f"Error unlocking target: {str(e)}")

    def hide_target(self, target):
        subprocess.run([r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe', 
                       '-Command', 
                       f"Set-ItemProperty -Path \"{target}\" -Name Attributes -Value ([System.IO.FileAttributes]::Hidden)"], 
                       check=True)

    def unhide_target(self, target):
        subprocess.run([r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe', 
                       '-Command', 
                       f"Set-ItemProperty -Path \"{target}\" -Name Attributes -Value 0"], 
                       check=True)

    def backup_target(self, target):
        backup_folder = target + '_backup'
        try:
            subprocess.run(['robocopy', target, backup_folder, '/MIR'], check=True)
        except Exception as e:
            print(f"Backup failed: {str(e)}")

    def set_folder_icon(self, folder_path, icon_path):
        desktop_ini_path = os.path.join(folder_path, "desktop.ini")
        with open(desktop_ini_path, 'w') as f:
            f.write(f"[.ShellClassInfo]\nIconResource={os.path.abspath(icon_path)},0\n")
        os.system(f'attrib +s +h "{desktop_ini_path}"')
        os.system(f'attrib +s +r "{folder_path}"')

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

if __name__ == "__main__":
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
