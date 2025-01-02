from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QPlainTextEdit, QLabel, QMessageBox
from PyQt5.QtCore import Qt
import requests

class DomainInfoWidget(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme  # Store the theme for styling
        self.api_keys = [
            "NQ-vg7MN217qK2Fuvpb7zm66Do_F_HrB",
            "E-L46Rm6RQZr9nNVQQTTCchh8kiazSO8",
            "lAs8ypgC_6bo7VZrkFfdxycHBYGMD_2M",
            "5UvkY64Wpo2KUVxc15BpCUJHOg54Slw4",
            "QzPWxVs6ZpwxLL8xGBbX1mGXG5Rm1cvZ",
            "D2TVBa7nc00V4l1gqXUnVl5zLKTvl4qO",
            "HZ7fHtww1-RypH-kvqbCjLxBM_xilh3p",
            "NQzRlDy4oCmOzOviLoLYvkxGkeS6EDJU",
            "ymQrMpVmtcdc1WA08luxgFFSfEFRVzbl",
            "2TLu_qiwpDlJimP96LwULQUtGXQtFsbH",
            "0IE8aT4fH6jPWBM8jgYvcJmFYXK58ESw",
            "M17bkWbXbYAALYlFqzRE4hakjDxnTUCO",
            "qY1mOPL3SnaHQmym1d2KznKFyQWElyCI",
            "JSkUrMFTvUYcK9To7T1hDkaMpv179ZGQ",
            "h53znMgPSEKSTVd6pZezreprBRG-FKYf",
            "D23egmnLJ5vk8CZgcH21ks_ckdxbdmOy",
        ]
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Input field
        self.domain_input = QLineEdit(self)
        self.domain_input.setPlaceholderText("Enter domain")
        self.domain_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 8px;
                color: {self.theme['text']};
            }}
        """)
        layout.addWidget(self.domain_input)

        # Check button
        check_button = QPushButton("Check Info", self)
        check_button.clicked.connect(self.check_domain_info)
        check_button.setStyleSheet(f"""
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
        layout.addWidget(check_button)

        # Output field
        self.domain_output = QPlainTextEdit(self)
        self.domain_output.setReadOnly(True)
        self.domain_output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 8px;
                color: {self.theme['text']};
            }}
        """)
        layout.addWidget(self.domain_output)

    def check_domain_info(self):
        domain = self.domain_input.text().strip()

        if not domain:
            QMessageBox.warning(self, "Input Error", "Please enter a valid domain.")
            return

        result_found = False

        for api_key in self.api_keys:
            try:
                url = f"https://api.securitytrails.com/v1/domain/{domain}"
                headers = {"APIKEY": api_key}
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    domain_info = response.json()
                    formatted_info = f"""
                    Apex Domain: {domain_info.get('apex_domain', 'N/A')}
                    Alexa Rank: {domain_info.get('alexa_rank', 'N/A')}
                    Subdomain Count: {domain_info.get('subdomain_count', 'N/A')}

                    Current DNS:
                    A Records:
                        First Seen: {domain_info.get('current_dns', {}).get('a', {}).get('first_seen', 'N/A')}
                        IP: {domain_info.get('current_dns', {}).get('a', {}).get('values', [{}])[0].get('ip', 'N/A')}
                        Organization: {domain_info.get('current_dns', {}).get('a', {}).get('values', [{}])[0].get('ip_organization', 'N/A')}

                    MX Records:
                        First Seen: {domain_info.get('current_dns', {}).get('mx', {}).get('first_seen', 'N/A')}
                        Hostname: {domain_info.get('current_dns', {}).get('mx', {}).get('values', [{}])[0].get('hostname', 'N/A')}
                        Priority: {domain_info.get('current_dns', {}).get('mx', {}).get('values', [{}])[0].get('priority', 'N/A')}

                    NS Records:
                        First Seen: {domain_info.get('current_dns', {}).get('ns', {}).get('first_seen', 'N/A')}
                        Nameserver: {domain_info.get('current_dns', {}).get('ns', {}).get('values', [{}])[0].get('nameserver', 'N/A')}

                    SOA Records:
                        First Seen: {domain_info.get('current_dns', {}).get('soa', {}).get('first_seen', 'N/A')}
                        Email: {domain_info.get('current_dns', {}).get('soa', {}).get('values', [{}])[0].get('email', 'N/A')}
                        TTL: {domain_info.get('current_dns', {}).get('soa', {}).get('values', [{}])[0].get('ttl', 'N/A')}

                    TXT Records:
                        First Seen: {domain_info.get('current_dns', {}).get('txt', {}).get('first_seen', 'N/A')}
                        Value: {domain_info.get('current_dns', {}).get('txt', {}).get('values', [{}])[0].get('value', 'N/A')}
                    """
                    self.domain_output.setPlainText(formatted_info)
                    result_found = True
                    break
                else:
                    self.domain_output.setPlainText(f"Error: {response.status_code} - {response.reason}")
                    continue
            except requests.exceptions.RequestException as e:
                self.domain_output.setPlainText(f"Error: {e}")
                continue

        if not result_found:
            self.domain_output.setPlainText("No valid domain info found with the available API keys.")
