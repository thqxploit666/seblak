from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QPlainTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
import requests
import json
import subprocess
import shlex

class VulDBSearchThread(QThread):
    search_complete = pyqtSignal(dict)

    def __init__(self, search_term, api_key):
        super().__init__()
        self.search_term = search_term
        self.api_key = api_key

    def run(self):
        api_url = "https://vuldb.com/?api"
        command = f"curl -X POST {api_url} -H 'X-VulDB-ApiKey: {self.api_key}' -d 'search={self.search_term}'"

        try:
            process = subprocess.run(shlex.split(command), capture_output=True, text=True, timeout=30)
            if process.returncode == 0:
                response = json.loads(process.stdout)
                self.search_complete.emit(response)
            else:
                self.search_complete.emit({"error": process.stderr.strip()})
        except Exception as e:
            self.search_complete.emit({"error": str(e)})

class VulnerabilitySearchWidget(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.api_keys = []
        self.current_api_key_index = 0
        self.load_api_keys()  # Load API keys from the JSON file
        self.init_ui()

    def load_api_keys(self):
        """Load API keys from the specified JSON URL."""
        url = "https://raw.githubusercontent.com/thqxploit666/fire/refs/heads/main/vln.json"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.api_keys = data.get("api_keys", [])
        except requests.exceptions.RequestException as e:
            print(f"Failed to load API keys: {str(e)}")
            self.api_keys = []  # Reset to empty if there's an error
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {str(e)}")
            self.api_keys = []

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Input field
        self.vuln_input = QLineEdit(self)
        self.vuln_input.setPlaceholderText("Enter search term")
        self.vuln_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 8px;
                color: {self.theme['text']};
            }}
        """)
        layout.addWidget(self.vuln_input)

        # Search button
        search_button = QPushButton("Search Vulnerabilities", self)
        search_button.clicked.connect(self.perform_vuln_search)
        search_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['button']};
                color: {self.theme['text']};
                border-radius: 8px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['button_hover']};
            }}
        """)
        layout.addWidget(search_button)

        # Output field
        self.vuln_output = QPlainTextEdit(self)
        self.vuln_output.setReadOnly(True)
        self.vuln_output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 8px;
                color: {self.theme['text']};
            }}
        """)
        layout.addWidget(self.vuln_output)

    def perform_vuln_search(self):
        search_term = self.vuln_input.text().strip()
        if not search_term:
            self.vuln_output.setPlainText("Please enter a search term.")
            return

        if not self.api_keys:
            self.vuln_output.setPlainText("No API keys available.")
            return

        api_key = self.api_keys[self.current_api_key_index]
        self.current_api_key_index = (self.current_api_key_index + 1) % len(self.api_keys)

        self.vuln_output.setPlainText("Searching vulnerabilities... Please wait.")

        self.search_thread = VulDBSearchThread(search_term, api_key)
        self.search_thread.search_complete.connect(self.update_vuln_output)
        self.search_thread.start()

    def update_vuln_output(self, data):
        if 'result' in data:
            vulnerabilities = data['result']
            result_text = f"Total vulnerabilities found: {len(vulnerabilities)}\n\n"
            for vuln in vulnerabilities:
                result_text += f"ID: {vuln.get('entry', {}).get('id')}\n"
                result_text += f"Title: {vuln.get('entry', {}).get('title')}\n"
                result_text += f"Risk Level: {vuln.get('vulnerability', {}).get('risk', {}).get('name')}\n"
                result_text += f"CVSS Score: {vuln.get('cvss_score')}\n"
                result_text += f"Advisory Date: {vuln.get('advisory', {}).get('date')}\n"
                result_text += f"CVE ID: {vuln.get('source', {}).get('cve', {}).get('id')}\n"
                result_text += "--------------------------\n"

            self.vuln_output.setPlainText(result_text)
        else:
            error_message = data.get('error', 'Unknown error')
            self.vuln_output.setPlainText(f"Error: {error_message}")
