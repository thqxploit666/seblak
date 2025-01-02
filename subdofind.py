from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, QPlainTextEdit, QLabel, QMessageBox)
import requests

class SubdomainFinder(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme  # Store the theme for styling
        self.api_keys = [
            "M17bkWbXbYAALYlFqzRE4hakjDxnTUCO",
            "0IE8aT4fH6jPWBM8jgYvcJmFYXK58ESw",
            "2TLu_qiwpDlJimP96LwULQUtGXQtFsbH",
            "ymQrMpVmtcdc1WA08luxgFFSfEFRVzbl",
            "NQzRlDy4oCmOzOviLoLYvkxGkeS6EDJU",
            "HZ7fHtww1-RypH-kvqbCjLxBM_xilh3p",
            "D2TVBa7nc00V4l1gqXUnVl5zLKTvl4qO",
            "QzPWxVs6ZpwxLL8xGBbX1mGXG5Rm1cvZ",
            "5UvkY64Wpo2KUVxc15BpCUJHOg54Slw4",
            "lAs8ypgC_6bo7VZrkFfdxycHBYGMD_2M",
            "E-L46Rm6RQZr9nNVQQTTCchh8kiazSO8",
            "NQ-vg7MN217qK2Fuvpb7zm66Do_F_HrB",
            "qY1mOPL3SnaHQmym1d2KznKFyQWElyCI",
            "JSkUrMFTvUYcK9To7T1hDkaMpv179ZGQ",
            "h53znMgPSEKSTVd6pZezreprBRG-FKYf",
            "D23egmnLJ5vk8CZgcH21ks_ckdxbdmOy",
        ]
        self.init_ui()

    def init_ui(self):
        # Main layout
        subdo_layout = QVBoxLayout(self)

        # Input field for domain
        self.subdo_input = QLineEdit(self)
        self.subdo_input.setPlaceholderText("Enter Domain or IP Address")
        self.subdo_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 8px;
                color: {self.theme['text']};
            }}
        """)
        subdo_layout.addWidget(self.subdo_input)

        # Find button
        find_button = QPushButton("Find Subdomains", self)
        find_button.clicked.connect(self.perform_subdo_finder)
        find_button.setStyleSheet(f"""
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
        subdo_layout.addWidget(find_button)

        # Output field for subdomains
        self.subdo_output = QPlainTextEdit(self)
        self.subdo_output.setReadOnly(True)
        self.subdo_output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 8px;
                color: {self.theme['text']};
            }}
        """)
        subdo_layout.addWidget(self.subdo_output)

    def perform_subdo_finder(self):
        domain = self.subdo_input.text().strip()

        if not domain:
            QMessageBox.warning(self, "Input Error", "Please enter a valid domain or IP address.")
            return

        result_found = False

        for api_key in self.api_keys:
            try:
                api_url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
                headers = {
                    "Content-Type": "application/json",
                    "APIKEY": api_key
                }
                response = requests.get(api_url, headers=headers)
                data = response.json()

                if response.status_code != 200 or 'error' in data:
                    continue
                
                subdomains = data.get('subdomains', [])
                if subdomains:
                    result_text = "\n".join([f"{subdomain}.{domain}" for subdomain in subdomains])
                    result_text += f"\n\nTotal subdomains found: {len(subdomains)}"
                    self.subdo_output.setPlainText(result_text)
                else:
                    self.subdo_output.setPlainText("No subdomains found.")

                result_found = True
                break
            except Exception as e:
                self.subdo_output.setPlainText(f"Error: {str(e)}")
                continue

        if not result_found:
            self.subdo_output.setPlainText("No valid subdomains found with the available API keys.")
