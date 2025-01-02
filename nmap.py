from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
                           QLabel, QScrollArea, QCheckBox, QMessageBox, QSpacerItem, 
                           QSizePolicy, QProgressBar, QComboBox, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import nmap
import threading
import time

class NmapScannerThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, target, arguments):
        super().__init__()
        self.target = target
        self.arguments = arguments
        
    def run(self):
        scanner = nmap.PortScanner()
        try:
            # Mulai scanning
            self.progress.emit(0)  # Awal scanning
            scanner.scan(hosts=self.target, arguments=self.arguments)

            # Total host yang akan discan
            total_hosts = len(scanner.all_hosts())
            if total_hosts == 0:
                raise Exception("No hosts found.")
            
            # Iterasi setiap host untuk memperbarui progres
            for idx, host in enumerate(scanner.all_hosts(), start=1):
                # Emit progres berdasarkan persentase host yang selesai
                self.progress.emit(int((idx / total_hosts) * 100))
                time.sleep(0.1)  # Simulasi delay untuk memastikan UI update

            # Parsing hasil scan
            results = self.parse_scan_results(scanner)
            self.result.emit(results)
        except Exception as e:
            self.result.emit(f"Error during scan: {str(e)}")
        finally:
            self.progress.emit(100)  # Scanning selesai
            self.finished.emit()

            
    def parse_scan_results(self, scanner):
        results = "Scan Results:\n\n"
        
        for host in scanner.all_hosts():
            results += f"Host: {host} ({scanner[host].hostname()})\n"
            results += f"State: {scanner[host].state()}\n\n"
            
            if 'osmatch' in scanner[host]:
                results += "Operating System Detection:\n"
                for os in scanner[host]['osmatch']:
                    results += f"• {os['name']} (Accuracy: {os['accuracy']}%)\n"
                results += "\n"
            
            for proto in scanner[host].all_protocols():
                results += f"Protocol: {proto.upper()}\n"
                ports = scanner[host][proto].keys()
                
                for port in sorted(ports):
                    port_info = scanner[host][proto][port]
                    state = port_info['state']
                    service = port_info.get('name', 'unknown')
                    version = port_info.get('version', '')
                    
                    results += f"• Port {port}/{proto}: {state}\n"
                    results += f"  Service: {service} {version}\n"
                    
                    if 'script' in port_info:
                        results += "  Scripts:\n"
                        for script_name, output in port_info['script'].items():
                            results += f"    - {script_name}: {output}\n"
                
                results += "\n"
                
        return results or "No results found."

class NmapScanner(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.scan_thread = None
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Target input group (same as before)
        target_group = QGroupBox("Target Configuration")
        target_layout = QVBoxLayout()
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText('Enter IP or Domain (e.g., 192.168.1.1, example.com)')
        target_layout.addWidget(self.ip_input)
        
        port_layout = QHBoxLayout()
        self.port_start = QLineEdit()
        self.port_start.setPlaceholderText('Start Port')
        self.port_end = QLineEdit()
        self.port_end.setPlaceholderText('End Port (max 65535)')
        port_layout.addWidget(self.port_start)
        port_layout.addWidget(QLabel("-"))
        port_layout.addWidget(self.port_end)
        target_layout.addLayout(port_layout)
        
        target_group.setLayout(target_layout)
        layout.addWidget(target_group)

        # Scan options group with horizontal layout for checkboxes
        options_group = QGroupBox("Scan Options")
        options_layout = QVBoxLayout()

        # Basic options in horizontal layout
        checkbox_layout = QHBoxLayout()
        
        # Left column of checkboxes
        left_checkbox_layout = QVBoxLayout()
        self.tcp_checkbox = QCheckBox("TCP SYN Scan")
        self.udp_checkbox = QCheckBox("UDP Scan")
        self.version_checkbox = QCheckBox("Version Detection")
        left_checkbox_layout.addWidget(self.tcp_checkbox)
        left_checkbox_layout.addWidget(self.udp_checkbox)
        left_checkbox_layout.addWidget(self.version_checkbox)
        
        # Right column of checkboxes
        right_checkbox_layout = QVBoxLayout()
        self.os_detect_checkbox = QCheckBox("OS Detection")
        self.aggressive_checkbox = QCheckBox("Aggressive Scan")
        right_checkbox_layout.addWidget(self.os_detect_checkbox)
        right_checkbox_layout.addWidget(self.aggressive_checkbox)

        # Add both columns to checkbox layout
        checkbox_layout.addLayout(left_checkbox_layout)
        checkbox_layout.addLayout(right_checkbox_layout)
        options_layout.addLayout(checkbox_layout)

        # Timing and script options
        options_grid = QHBoxLayout()
        
        # Timing template
        timing_layout = QVBoxLayout()
        timing_layout.addWidget(QLabel("Timing Template:"))
        self.timing_combo = QComboBox()
        self.timing_combo.addItems(["T0 (Paranoid)", "T1 (Sneaky)", "T2 (Polite)", 
                                  "T3 (Normal)", "T4 (Aggressive)", "T5 (Insane)"])
        self.timing_combo.setCurrentIndex(3)
        timing_layout.addWidget(self.timing_combo)
        options_grid.addLayout(timing_layout)

        # Script selection
        script_layout = QVBoxLayout()
        script_layout.addWidget(QLabel("Script Selection:"))
        self.script_combo = QComboBox()
        self.script_combo.addItems(["No Scripts", "Default Scripts", "Vuln Scripts", 
                                  "Safe Scripts", "Auth Scripts", "All Scripts"])
        script_layout.addWidget(self.script_combo)
        options_grid.addLayout(script_layout)
        
        options_layout.addLayout(options_grid)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Scan button
        self.scan_button = QPushButton('Start Scan')
        self.scan_button.clicked.connect(self.start_scan)
        layout.addWidget(self.scan_button)

        # Results area with increased height
        results_group = QGroupBox("Scan Results")
        results_layout = QVBoxLayout()
        
        self.result_text = QLabel()
        self.result_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.result_text.setWordWrap(True)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.result_text)
        scroll_area.setMinimumHeight(400)  # Increased height for results
        results_layout.addWidget(scroll_area)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

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
            QScrollArea {{
                border: none;
            }}
            QLabel {{
                color: {self.theme['text']};
            }}
            QCheckBox {{
                color: {self.theme['text']};

            }}
            QComboBox {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 4px;
                padding: 5px;
                color: {self.theme['text']};
            }}
            QProgressBar {{
                border: 1px solid {self.theme['border']};
                border-radius: 4px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {self.theme['accent']};
            }}
        """)

    def get_scan_arguments(self):
        args = []
        
        # Port range
        start_port = self.port_start.text() or "1"
        end_port = self.port_end.text() or "1024"
        args.append(f"-p{start_port}-{end_port}")
        
        # Scan types
        if self.tcp_checkbox.isChecked():
            args.append("-sS")
        if self.udp_checkbox.isChecked():
            args.append("-sU")
        if self.version_checkbox.isChecked():
            args.append("-sV")
        if self.os_detect_checkbox.isChecked():
            args.append("-O")
        if self.aggressive_checkbox.isChecked():
            args.append("-A")
            
        # Timing template
        timing_index = self.timing_combo.currentIndex()
        args.append(f"-T{timing_index}")
        
        # Scripts
        script_option = self.script_combo.currentText()
        if script_option != "No Scripts":
            if script_option == "Default Scripts":
                args.append("-sC")
            elif script_option == "Vuln Scripts":
                args.append("--script vuln")
            elif script_option == "Safe Scripts":
                args.append("--script safe")
            elif script_option == "Auth Scripts":
                args.append("--script auth")
            elif script_option == "All Scripts":
                args.append("--script all")
        
        return " ".join(args)

    def start_scan(self):
        target = self.ip_input.text().strip()
        if not target:
            QMessageBox.warning(self, 'Error', 'Please enter an IP or domain.')
            return
            
        try:
            # Validate port range
            start_port = int(self.port_start.text() or "1")
            end_port = int(self.port_end.text() or "1024")
            if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
                raise ValueError("Ports must be between 1 and 65535")
            if start_port > end_port:
                raise ValueError("Start port must be less than or equal to end port")
        except ValueError as e:
            QMessageBox.warning(self, 'Error', str(e))
            return

        # Disable UI during scan
        self.scan_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.result_text.setText("Scanning in progress...")

        # Start scan in separate thread
        arguments = self.get_scan_arguments()
        self.scan_thread = NmapScannerThread(target, arguments)
        self.scan_thread.progress.connect(self.update_progress)
        self.scan_thread.result.connect(self.update_results)
        self.scan_thread.finished.connect(self.scan_completed)
        self.scan_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_results(self, results):
        self.result_text.setText(results)

    def scan_completed(self):
        self.scan_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.scan_thread = None