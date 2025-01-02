from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, QPlainTextEdit, QLabel, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import requests
import socket
import json
import time

class ReverseIPWorker(QThread):
    resultReady = pyqtSignal(list)
    updateStatus = pyqtSignal(str)
    
    def __init__(self, target):
        super().__init__()
        self.target = target
        
    def get_ip(self, domain):
        try:
            return socket.gethostbyname(domain)
        except:
            return domain
            
    def run(self):
        all_domains = set()
        target_input = self.target

        # WhoisXMLAPI Section
        whoisxml_api_keys = [
            'at_6A2gsGrYqAn9nKJJCV3kuiuVSRo8L',
            'at_AlAyrUj8C9Ux4tjrLwhzmx7IpHmKh',
            'at_NSf3vTq3dPlgzoPdirFBeUBcLFydd'
        ]
        
        # Check if input is a domain or IP
        try:
            # If it's a domain, this will work
            socket.inet_aton(target_input)
            ip_for_whois = target_input
            self.updateStatus.emit(f"Input is an IP address: {target_input}")
        except socket.error:
            # If it's a domain, convert to IP
            try:
                ip_for_whois = socket.gethostbyname(target_input)
                self.updateStatus.emit(f"Resolved domain {target_input} to IP: {ip_for_whois}")
            except socket.gaierror as e:
                self.updateStatus.emit(f"Could not resolve domain {target_input} to IP: {str(e)}")
                ip_for_whois = target_input

        # Now use the resolved IP with WhoisXMLAPI
        for api_key in whoisxml_api_keys:
            try:
                self.updateStatus.emit(f"Querying with IP: {ip_for_whois}")
                response = requests.get(f"https://reverse-ip.whoisxmlapi.com/api/v1?apiKey={api_key}&ip={ip_for_whois}")
                
                if response.status_code == 200:
                    data = response.json()
                    if 'result' in data:
                        domains = [record.get('name', '').strip() for record in data['result']]
                        added_domains = set(filter(None, domains))
                        all_domains.update(added_domains)
                        self.updateStatus.emit(f"Found {len(added_domains)} domains")
                    break
                else:
                    self.updateStatus.emit(f"returned status code: {response.status_code}")
            except Exception as e:
                self.updateStatus.emit(f"Error fetching : {str(e)}")

        # Continue with other APIs using the original target input
        ip_address = self.get_ip(target_input)

        # HackerTarget API
        try:
            response = requests.get(f"https://api.hackertarget.com/reverseiplookup/?q={ip_address}")
            if response.status_code == 200 and not "error" in response.text.lower():
                domains = response.text.split('\n')
                new_domains = set(domain.strip() for domain in domains if domain.strip())
                all_domains.update(new_domains)
                self.updateStatus.emit(f"Found {len(new_domains)} domains part2")
        except Exception as e:
            self.updateStatus.emit(f"Error fetching  {str(e)}")

        # YouGetSignal API
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            data = {
                "remoteAddress": self.target,
                "key": "WEBgui",
                "cmd": "IP_DOMAIN"
            }
            response = requests.post("https://domains.yougetsignal.com/domains.php", headers=headers, data=data)
            json_data = response.json()
            if json_data.get('status') == 'Success' and 'domainArray' in json_data:
                domains = [domain[0] for domain in json_data['domainArray']]
                all_domains.update(domains)
        except Exception as e:
            self.updateStatus.emit(f"Error fetching : {str(e)}")

        # ViewDNS API
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(f"https://viewdns.info/reverseip/?host={ip_address}&t=1", headers=headers)
            if response.status_code == 200:
                # Extract domains from HTML response (simplified)
                for line in response.text.split('\n'):
                    if 'Domain:</td><td>' in line:
                        domain = line.split('Domain:</td><td>')[1].split('</td>')[0].strip()
                        if domain:
                            all_domains.add(domain)
        except Exception as e:
            self.updateStatus.emit(f"Error fetching : {str(e)}")

        # Shodan API
        shodan_api_keys = [
            'OefcMxcunkm72Po71vVtX8zUN57vQtAC',
            'PSKINdQe1GyxGgecYz2191H2JoS9qvgD',
            'EBeU0lGqtIO6yCxVFCWC4nUVbvovtjo5',
            'XYdjHDeJM36AjDfU1feBsyMJIj8XxGzD',
            'pHHlgpFt8Ka3Stb5UlTxcaEwciOeF2QM',
            '61TvA2dNwxNxmWziZxKzR5aO9tFD00Nj',
            'xTbXXOSBr0R65OcClImSwzadExoXU4tc',
            'EJV3A4Mka2wPs7P8VBCO6xcpRe27iNJu',
            'mEuInz8UH1ixLGJq4oQhEiJORERVG5xc',
            'lkY0ng0XMo29zEhzyw3ibQfeEBxghwPF',
            'syeCnFndQ8TE4qAGvhm9nZLBZOBgoLKd',
            '7TeyFZ8oyLulHwYUOcSPzZ5w3cLYib61',
            'v4YpsPUJ3wjDxEqywwu6aF5OZKWj8kik',
            'dTNGRiwYNozXIDRf5DWyGNbkdiS5m3JK',
            'kdnzf4fsYWQmGajRDn3hB0RElbUlIaqu',
            'boYedPn8iDWi6GDSO6h2kz72VLt6bZ3S',
            'FQNAMUdkeqXqVOdXsTLYeatFSpZSktdb',
            'OygcaGSSq46Lg5fZiADAuFxl4OBbn7zm',
            'XAbsu1Ruj5uhTNcxGdbGNgrh9WuMS1B6',
            'nkGd8uVE4oryfUVvioprswdKGmA5InzZ',
            'XYdjHDeJM36AjDfU1feBsyMJIj8XxGzD',
            'EBeU0lGqtIO6yCxVFCWC4nUVbvovtjo5'
        ]
        
        for api_key in shodan_api_keys:
            try:
                # Search by IP
                response = requests.get(f"https://api.shodan.io/shodan/host/{ip_address}?key={api_key}")
                if response.status_code == 200:
                    data = response.json()
                    if 'hostnames' in data:
                        all_domains.update(data['hostnames'])
                    if 'domains' in data:
                        all_domains.update(data['domains'])
                        
                # Search by domain
                response = requests.get(f"https://api.shodan.io/dns/domain/{self.target}?key={api_key}")
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data:
                        for entry in data['data']:
                            if 'subdomain' in entry:
                                all_domains.add(f"{entry['subdomain']}.{self.target}")
                    break
            except Exception as e:
                self.updateStatus.emit(f"Error fetching from Shodan: {str(e)}")

        # SecurityTrails API
        securitytrails_api_keys = [
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
            "D23egmnLJ5vk8CZgcH21ks_ckdxbdmOy"
        ]
        
        for api_key in securitytrails_api_keys:
            try:
                # Get associated domains
                headers = {"APIKEY": api_key}
                
                # Search by IP
                response = requests.get(f"https://api.securitytrails.com/v1/ips/nearby/{ip_address}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if 'blocks' in data:
                        for block in data['blocks']:
                            if 'hostnames' in block:
                                all_domains.update(block['hostnames'])
                
                # Search by domain
                response = requests.get(f"https://api.securitytrails.com/v1/domain/{self.target}/subdomains", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if 'subdomains' in data:
                        for subdomain in data['subdomains']:
                            all_domains.add(f"{subdomain}.{self.target}")
                    break
            except Exception as e:
                self.updateStatus.emit(f"Error fetching from SecurityTrails: {str(e)}")

        # Remove empty strings and sort results
        unique_domains = sorted(list(filter(None, all_domains)))
        self.resultReady.emit(unique_domains)

class ReverseIP(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.worker = None
        self.init_ui()

    def init_ui(self):
        # Main layout
        revip_layout = QVBoxLayout(self)

        # Input field for domain/IP
        self.revip_input = QLineEdit(self)
        self.revip_input.setPlaceholderText("Enter Domain or IP Address")
        self.revip_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 8px;
                color: {self.theme['text']};
            }}
        """)
        revip_layout.addWidget(self.revip_input)

        # Find button
        self.find_button = QPushButton("Find Domains", self)
        self.find_button.clicked.connect(self.start_reverse_ip_lookup)
        self.find_button.setStyleSheet(f"""
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
        revip_layout.addWidget(self.find_button)

        # Output field for results
        self.revip_output = QPlainTextEdit(self)
        self.revip_output.setReadOnly(True)
        self.revip_output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 8px;
                color: {self.theme['text']};
            }}
        """)
        revip_layout.addWidget(self.revip_output)

    def start_reverse_ip_lookup(self):
        target = self.revip_input.text().strip()
        
        if not target:
            QMessageBox.warning(self, "Input Error", "Please enter a valid Domain or IP address.")
            return
            
        # Disable button while processing
        self.find_button.setEnabled(False)
        self.revip_output.setPlainText("Searching for domains...")
        
        # Create and start worker thread
        self.worker = ReverseIPWorker(target)
        self.worker.resultReady.connect(self.handle_results)
        self.worker.updateStatus.connect(self.update_status)
        self.worker.finished.connect(lambda: self.find_button.setEnabled(True))
        self.worker.start()

    @pyqtSlot(list)
    def handle_results(self, unique_domains):
        if unique_domains:
            self.revip_output.setPlainText(f"Total Unique Domains Found: {len(unique_domains)}\n")
            for domain in unique_domains:
                self.revip_output.appendPlainText(domain)
        else:
            self.revip_output.setPlainText("No domains found.")

    @pyqtSlot(str)
    def update_status(self, status):
        self.revip_output.appendPlainText(status)