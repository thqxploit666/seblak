from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QScrollArea, QMessageBox, QProgressBar, 
                           QGroupBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QPixmap, QMovie 
import requests
import json
import os
import time 
from pathlib import Path

class UpdateCheckerThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    result = pyqtSignal(dict)
    finished = pyqtSignal()
    
    def __init__(self, local_path):
        super().__init__()
        self.local_path = local_path
        self.repo_api = "https://api.github.com/repos/thqxploit666/seblak/contents"
        self.headers = {'Accept': 'application/vnd.github.v3+json'}
        
    def get_file_sha(self, path):
        """Get SHA of file from GitHub"""
        try:
            response = requests.get(f"{self.repo_api}/{path}", headers=self.headers)
            if response.status_code == 200:
                return response.json()['sha']
        except:
            return None
        return None

    def get_local_files(self):
        """Get list of local files recursively, excluding certain folders"""
        files = []
        excluded_folders = ['imej', 'result']  # Folder yang tidak perlu diperiksa
        try:
            for root, _, filenames in os.walk(self.local_path):
                # Abaikan folder yang tidak perlu
                if any(excluded in root for excluded in excluded_folders):
                    continue
                
                for filename in filenames:
                    if not filename.endswith(('.pyc', '.pyo', '.pyd', '.git')):  # Ekstensi yang diabaikan
                        rel_path = os.path.relpath(os.path.join(root, filename), self.local_path)
                        files.append(rel_path)
            print("Local files found:", files)  # Debugging log
        except Exception as e:
            print(f"Error reading local files: {e}")
        return files

    def run(self):
        try:
            print("Starting update check...")
            self.status.emit("Memeriksa pembaruan...")
            self.progress.emit(0)

            # Path folder lokal
            local_folder = os.path.join(self.local_path)

            # Validasi apakah folder lokal ada
            if not os.path.exists(local_folder):
                raise FileNotFoundError(f"Folder lokal tidak ditemukan: {local_folder}")

            # Ambil file lokal
            local_files = {os.path.relpath(os.path.join(root, file), local_folder): file
                           for root, _, files in os.walk(local_folder)
                           for file in files}
            print("Local Files Detected:", local_files)  # Debugging local files
            print(f"Number of local files detected: {len(local_files)}")
            self.progress.emit(20)

            # Ambil file dari GitHub
            response = requests.get(f"{self.repo_api}", headers=self.headers)
            print("GitHub API Response Code:", response.status_code)  # Debugging response status

            if response.status_code != 200:
                raise Exception(f"Gagal mengambil data dari repository: {response.text}")

            repo_files = {item['name']: item for item in response.json() if item['type'] == 'file'}
            print("Repo Files Extracted:", repo_files)  # Debugging repository files
            print(f"Number of repo files detected: {len(repo_files)}")
            self.progress.emit(50)

            updates = {
                'has_updates': False,
                'files': []
            }

            # Bandingkan file GitHub dengan file lokal
            for repo_name, repo_file in repo_files.items():
                if repo_name in local_files:
                    # Jika file ada di lokal, bandingkan ukuran
                    local_file_path = os.path.join(local_folder, repo_name)
                    if os.path.getsize(local_file_path) != int(repo_file['size']):
                        updates['has_updates'] = True
                        updates['files'].append({'name': repo_name, 'status': 'update'})
                    else:
                        updates['files'].append({'name': repo_name, 'status': 'current'})
                else:
                    # File baru di GitHub
                    updates['has_updates'] = True
                    updates['files'].append({'name': repo_name, 'status': 'new'})

            # Cari file yang perlu dihapus dari lokal
            for local_file in local_files:
                # Gunakan local_file langsung tanpa relpath tambahan
                if local_file not in repo_files:
                    updates['has_updates'] = True
                    updates['files'].append({'name': local_file, 'status': 'delete'})

            print(f"Updates found: {updates['has_updates']}")
            print(f"Files to update: {updates['files']}")

            self.progress.emit(100)
            self.result.emit(updates)

        except Exception as e:
            self.status.emit(f"Error: {str(e)}")
            print(f"Error during update check: {e}")
        finally:
            self.finished.emit()


class UpdateInstallThread(QThread):
    progress = pyqtSignal(int)
    file_status = pyqtSignal(str, bool)
    status = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, files_to_update, local_path):
        super().__init__()
        self.files_to_update = files_to_update
        self.local_path = local_path
        self.repo_raw = "https://raw.githubusercontent.com/thqxploit666/seblak/main"
        
    def run(self):
        total_files = len(self.files_to_update)
        updated_count = 0
        
        for idx, file_info in enumerate(self.files_to_update, 1):
            try:
                print(f"Processing file: {file_info['name']} with status {file_info['status']}")
                self.status.emit(f"Memperbarui {file_info['name']}...")
                
                if file_info['status'] == 'delete':
                    # Delete file
                    try:
                        os.remove(os.path.join(self.local_path, file_info['name']))
                        success = True
                        print(f"Deleted file: {file_info['name']}")
                    except Exception as e:
                        success = False
                        print(f"Failed to delete file {file_info['name']}: {e}")
                else:
                    # Download/update file
                    response = requests.get(f"{self.repo_raw}/{file_info['name']}")
                    if response.status_code == 200:
                        # Ensure directory exists
                        file_path = os.path.join(self.local_path, file_info['name'])
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        
                        # Write file
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        success = True
                        updated_count += 1
                        print(f"Updated file: {file_info['name']}")
                    else:
                        success = False
                        print(f"Failed to download file {file_info['name']}: Status code {response.status_code}")
                
                progress = int((idx / total_files) * 100)
                self.progress.emit(progress)
                self.file_status.emit(file_info['name'], success)
                
            except Exception as e:
                self.file_status.emit(file_info['name'], False)
                print(f"Error updating file {file_info['name']}: {e}")
                
        if updated_count == total_files:
            self.status.emit("Pembaruan selesai!")
            print("All files updated successfully.")
        else:
            self.status.emit(f"Pembaruan selesai dengan {total_files - updated_count} kesalahan")
            print(f"Update completed with {total_files - updated_count} errors.")
            
        self.finished.emit()


class UpdateChecker(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.check_thread = None
        self.install_thread = None
        self.local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'seblak')
        self.current_files = []  # Inisialisasi self.current_files
        
        # Initialize spinner here
        self.spinner = QMovie("imej/spinner.gif")
        self.spinner.setScaledSize(QSize(32, 32))
        
        self.init_ui()
        self.apply_theme()
        
        # Load spinner animation
        self.spinner = QMovie("imej/spinner.gif")
        self.spinner.setScaledSize(QSize(32, 32))

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Header
        header_label = QLabel("Pemeriksa Pembaruan")
        header_label.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)

        # Status icon and message
        self.status_icon = QLabel()
        self.status_icon.setAlignment(Qt.AlignCenter)
        self.status_icon.setMinimumHeight(100)
        self.status_icon.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.status_icon)

        # Loading animation
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setMovie(self.spinner)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)

        self.status_label = QLabel("Klik 'Periksa Pembaruan' untuk memulai")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Files list group
        self.files_group = QGroupBox("File yang Perlu Diperbarui")
        self.files_group.setVisible(False)
        files_layout = QVBoxLayout()
        
        self.files_area = QWidget()
        self.files_list_layout = QVBoxLayout(self.files_area)
        
        scroll = QScrollArea()
        scroll.setWidget(self.files_area)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(200)
        files_layout.addWidget(scroll)
        
        self.files_group.setLayout(files_layout)
        layout.addWidget(self.files_group)

        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.check_button = QPushButton("Periksa Pembaruan")
        self.check_button.clicked.connect(self.check_updates)
        buttons_layout.addWidget(self.check_button)
        
        self.update_button = QPushButton("Ya Update")
        self.update_button.clicked.connect(self.start_update)
        self.update_button.setVisible(False)
        buttons_layout.addWidget(self.update_button)
        
        self.cancel_button = QPushButton("Batalkan")
        self.cancel_button.clicked.connect(self.cancel_update)
        self.cancel_button.setVisible(False)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

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
            }}
            QPushButton {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 4px;
                padding: 8px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['button_hover']};
            }}
            QProgressBar {{
                border: 1px solid {self.theme['border']};
                border-radius: 4px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {self.theme['accent']};
            }}
            QScrollArea {{
                border: none;
            }}
        """)

    def check_updates(self):
        self.check_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.files_group.setVisible(False)
        self.status_icon.hide()
        self.loading_label.show()
        self.spinner.start()
        
        # Mulai pemeriksaan dalam thread terpisah
        self.check_thread = UpdateCheckerThread(self.local_path)
        self.check_thread.progress.connect(self.update_progress)
        self.check_thread.status.connect(self.update_status)
        self.check_thread.result.connect(self.handle_check_result)
        self.check_thread.finished.connect(self.check_completed)
        self.check_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, message):
        self.status_label.setText(message)

    def handle_check_result(self, result):
        self.loading_label.hide()
        self.spinner.stop()
        self.status_icon.show()
        
        if result['has_updates']:
            self.status_icon.setText("⟳")  # Big retry icon
            self.status_label.setText("Pembaruan Tersedia")
            self.show_file_list(result['files'])
            self.update_button.setVisible(True)
            self.cancel_button.setVisible(True)
            
            # Menetapkan self.current_files di sini
            self.current_files = result['files']
        else:
            self.status_icon.setText("✓")  # Big checkmark
            self.status_label.setText("Aplikasi Anda Sudah Versi Terbaru")
            self.current_files = []  # Tidak ada pembaruan

    def check_completed(self):
        """Handle the completion of the update checking process."""
        self.check_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.spinner.stop()
        self.loading_label.hide()

        # Jika ada pembaruan, tampilkan tombol update dan batalkan
        if self.current_files:
            self.status_label.setText("Klik 'Ya Update' untuk memulai pembaruan.")
        else:
            self.status_label.setText("Pemeriksaan selesai. Aplikasi sudah versi terbaru.")

    def show_file_list(self, files):
        # Clear previous list
        while self.files_list_layout.count():
            item = self.files_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add files to list
        for file_info in files:
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            
            # Status icon dengan warna
            status_map = {
                'current': ('✓', '#28a745'),  # Hijau
                'update': ('⟳', '#007bff'),   # Biru
                'new': ('+', '#17a2b8'),      # Cyan
                'delete': ('×', '#dc3545')    # Merah
            }
            
            icon, color = status_map.get(file_info['status'], ('?', '#6c757d'))
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            item_layout.addWidget(icon_label)
            
            # File info
            status_text = {
                'update': 'perlu diperbarui',
                'new': 'file baru',
                'current': 'sudah terbaru',
                'delete': 'akan dihapus'
            }
            file_label = QLabel(f"{file_info['name']} ({status_text.get(file_info['status'], 'unknown')})")
            item_layout.addWidget(file_label)
            
            item_layout.addStretch()
            self.files_list_layout.addWidget(item_widget)
        
        self.files_group.setVisible(True)

    def start_update(self):
        self.update_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_icon.hide()
        self.loading_label.show()
        self.spinner.start()
        
        # Ambil files_to_update dari self.current_files
        files_to_update = [f for f in self.current_files if f['status'] in ('update', 'new', 'delete')]
        
        if not files_to_update:
            self.status_label.setText("Tidak ada file yang perlu diperbarui.")
            self.spinner.stop()
            self.loading_label.hide()
            self.update_button.setEnabled(True)
            self.cancel_button.setVisible(False)
            return
        
        # Mulai pembaruan dalam thread terpisah
        self.install_thread = UpdateInstallThread(files_to_update, self.local_path)
        self.install_thread.progress.connect(self.update_progress)
        self.install_thread.file_status.connect(self.handle_file_status)
        self.install_thread.status.connect(self.update_status)
        self.install_thread.finished.connect(self.update_completed)
        self.install_thread.start()

    def handle_file_status(self, file_name, success):
        """Handle status of individual file update."""
        print(f"Updating file: {file_name} - {'Success' if success else 'Failed'}")
        status_icon = "✓" if success else "×"
        color = "#28a745" if success else "#dc3545"
        status_message = f"{status_icon} {file_name} {'berhasil diperbarui' if success else 'gagal diperbarui'}"
        
        status_label = QLabel(status_message)
        status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.files_list_layout.addWidget(status_label)

    def update_completed(self):
        """Handle completion of update process."""
        print("Update process completed.")
        self.spinner.stop()
        self.loading_label.hide()
        self.status_icon.show()
        self.status_icon.setText("✓")  # Big checkmark icon
        self.status_label.setText("Pembaruan selesai!")

        self.check_button.setEnabled(True)
        self.update_button.setVisible(False)
        self.cancel_button.setVisible(False)

    def cancel_update(self):
        """Handle cancel update process."""
        if self.check_thread and self.check_thread.isRunning():
            self.check_thread.terminate()
        if self.install_thread and self.install_thread.isRunning():
            self.install_thread.terminate()
        
        self.spinner.stop()
        self.loading_label.hide()
        self.status_label.setText("Pembaruan dibatalkan.")
        self.check_button.setEnabled(True)
        self.update_button.setVisible(False)
        self.cancel_button.setVisible(False)
