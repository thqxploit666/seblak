from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, 
    QFrame, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QTextCursor, QColor

import os
import re
from urllib.parse import urlparse
import socket

#qthreads nya
class PortScannerThread(QThread):
    update_signal = pyqtSignal(str, str)  # Emit text and color

    def __init__(self, hosts_and_ports):
        super().__init__()
        self.hosts_and_ports = hosts_and_ports

    def run(self):
        for line in self.hosts_and_ports:
            line = line.strip()
            if not line:
                continue

            try:
                host, port = line.split(":")
                port = int(port)
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))

                if result == 0:
                    self.update_signal.emit(f"{host}:{port} - Open", "green")
                else:
                    self.update_signal.emit(f"{host}:{port} - Closed", "red")
                
                sock.close()
            except Exception as e:
                self.update_signal.emit(f"{line} - Error: {str(e)}", "black")


class GTLSTools(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Content frame
        self.content_frame = QFrame(self)
        self.content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme['content_background']};
                border-radius: 15px;
                padding: 10px;
                color: {self.theme['text']};
            }}
        """)
        self.content_layout = QVBoxLayout(self.content_frame)
        
        
        # First row of buttons
        first_row_layout = QHBoxLayout()
        self.buttons_row1 = [
            ("Anti Duplicate", self.show_anti_duplicate),
            ("URL Cleaner", self.show_url_cleaner),
            ("Base64 En/Decoder", self.show_base64_tool),
            ("IP Calculator", self.show_ip_calculator),
            ("Add Port in Domain", self.show_adport)
        ]
        
        # Second row of buttons
        second_row_layout = QHBoxLayout()
        self.buttons_row2 = [
            ("Port Scanner", self.show_port_scanner),
            ("Domain To Ip", self.show_dotoip),
            ("Word Counter", self.show_word_counter),
            ("Email Extractor", self.show_email_extractor),
            ("String Reverser", self.show_string_reverser)
        ]
        
        # Create and add buttons for both rows
        for button_text, callback in self.buttons_row1:
            button = self.create_styled_button(button_text)
            button.clicked.connect(callback)
            first_row_layout.addWidget(button)
            
        for button_text, callback in self.buttons_row2:
            button = self.create_styled_button(button_text)
            button.clicked.connect(callback)
            second_row_layout.addWidget(button)
        
        self.content_layout.addLayout(first_row_layout)
        self.content_layout.addLayout(second_row_layout)
        
        # Add content frame to main layout
        self.main_layout.addWidget(self.content_frame)
        
        # Content area for tools
        self.tool_content = QWidget()
        self.tool_layout = QVBoxLayout(self.tool_content)
        self.content_layout.addWidget(self.tool_content)

    def create_styled_button(self, text):
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['button']};
                color: {self.theme['text']};
                border-radius: 10px;
                padding: 8px;
                font-size: 12px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['button_hover']};
            }}
        """)
        return button

    def clear_tool_content(self):
        while self.tool_layout.count():
            widget = self.tool_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

    def create_text_area(self):
        text_area = QTextEdit()
        text_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.theme['content_background']};
                border: 2px solid {self.theme['accent']};
                border-radius: 10px;
                padding: 5px;
                color: {self.theme['text']};
                font-family: monospace;
            }}
        """)
        return text_area

    def create_process_button(self, text="Process"):
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['accent']};
                color: white;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['button_hover']};
            }}
        """)
        return button

    def show_anti_duplicate(self):
        self.clear_tool_content()
        
        # Create input and output areas
        input_area = self.create_text_area()
        input_area.setPlaceholderText("Enter URLs (one per line)")
        output_area = self.create_text_area()
        output_area.setReadOnly(True)
        
        process_button = self.create_process_button("Remove Duplicates")
        
        def process_duplicates():
            urls = set(input_area.toPlainText().strip().split('\n'))
            unique_urls = '\n'.join(sorted(urls))
            output_area.setText(unique_urls)
            
        process_button.clicked.connect(process_duplicates)
        
        self.tool_layout.addWidget(QLabel("Input URLs:"))
        self.tool_layout.addWidget(input_area)
        self.tool_layout.addWidget(process_button)
        self.tool_layout.addWidget(QLabel("Unique URLs:"))
        self.tool_layout.addWidget(output_area)

    def show_url_cleaner(self):
        self.clear_tool_content()
        
        input_area = self.create_text_area()
        input_area.setPlaceholderText("Enter URLs (one per line)")
        output_area = self.create_text_area()
        output_area.setReadOnly(True)
        
        process_button = self.create_process_button("Clean URLs")
        
        def clean_urls():
            urls = input_area.toPlainText().strip().split('\n')
            cleaned_urls = []
            for url in urls:
                try:
                    parsed = urlparse(url)
                    cleaned_url = parsed.netloc
                    if cleaned_url:
                        cleaned_urls.append(cleaned_url)
                except:
                    continue
            output_area.setText('\n'.join(cleaned_urls))
            
        process_button.clicked.connect(clean_urls)
        
        self.tool_layout.addWidget(QLabel("Input URLs:"))
        self.tool_layout.addWidget(input_area)
        self.tool_layout.addWidget(process_button)
        self.tool_layout.addWidget(QLabel("Cleaned URLs:"))
        self.tool_layout.addWidget(output_area)

    def show_base64_tool(self):
        self.clear_tool_content()
        
        input_area = self.create_text_area()
        input_area.setPlaceholderText("Enter text to encode/decode")
        output_area = self.create_text_area()
        output_area.setReadOnly(True)
        
        encode_button = self.create_process_button("Encode")
        decode_button = self.create_process_button("Decode")
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(encode_button)
        button_layout.addWidget(decode_button)
        
        import base64
        
        def encode_text():
            text = input_area.toPlainText()
            try:
                encoded = base64.b64encode(text.encode()).decode()
                output_area.setText(encoded)
            except:
                QMessageBox.warning(self, "Error", "Invalid input for encoding")
                
        def decode_text():
            text = input_area.toPlainText()
            try:
                decoded = base64.b64decode(text.encode()).decode()
                output_area.setText(decoded)
            except:
                QMessageBox.warning(self, "Error", "Invalid input for decoding")
                
        encode_button.clicked.connect(encode_text)
        decode_button.clicked.connect(decode_text)
        
        self.tool_layout.addWidget(QLabel("Input Text:"))
        self.tool_layout.addWidget(input_area)
        self.tool_layout.addLayout(button_layout)
        self.tool_layout.addWidget(QLabel("Output:"))
        self.tool_layout.addWidget(output_area)

    def show_ip_calculator(self):
        self.clear_tool_content()
        
        input_area = self.create_text_area()
        input_area.setPlaceholderText("Enter IP/CIDR (e.g., 192.168.1.0/24)")
        output_area = self.create_text_area()
        output_area.setReadOnly(True)
        
        process_button = self.create_process_button("Calculate")
        
        def calculate_ip():
            import ipaddress
            try:
                network = ipaddress.ip_network(input_area.toPlainText().strip(), strict=False)
                result = f"Network: {network.network_address}\n"
                result += f"Broadcast: {network.broadcast_address}\n"
                result += f"Netmask: {network.netmask}\n"
                result += f"Total hosts: {network.num_addresses}\n"
                result += f"First host: {next(network.hosts())}\n"
                result += f"Last host: {list(network.hosts())[-1]}"
                output_area.setText(result)
            except:
                QMessageBox.warning(self, "Error", "Invalid IP/CIDR format")
                
        process_button.clicked.connect(calculate_ip)
        
        self.tool_layout.addWidget(QLabel("Input IP/CIDR:"))
        self.tool_layout.addWidget(input_area)
        self.tool_layout.addWidget(process_button)
        self.tool_layout.addWidget(QLabel("Network Information:"))
        self.tool_layout.addWidget(output_area)

    def show_adport(self):
        self.clear_tool_content()
        
        input_area = self.create_text_area()
        input_area.setPlaceholderText("Enter domains (one per line)")
        output_area = self.create_text_area()
        output_area.setReadOnly(True)
        
        process_button = self.create_process_button("Add Ports")
        
        def add_ports():
            domains = input_area.toPlainText().strip().split('\n')
            ports = [20, 21, 22, 23, 25, 53, 67, 69, 80, 110, 
                    143, 443, 445, 3389, 5900, 8080, 3306, 
                    5432, 6379, 27017]
            
            results = []
            for domain in domains:
                domain = domain.strip()
                if not domain:
                    continue
                    
                domain_results = []
                for port in ports:
                    domain_results.append(f"{domain}:{port}")
                    
                results.extend(domain_results)
                results.append("")  # Add blank line between domains
                
            # Remove last blank line if exists
            if results and not results[-1]:
                results.pop()
                
            output_area.setText('\n'.join(results))
            
        process_button.clicked.connect(add_ports)
        
        self.tool_layout.addWidget(QLabel("Input Domains:"))
        self.tool_layout.addWidget(input_area)
        self.tool_layout.addWidget(process_button)
        self.tool_layout.addWidget(QLabel("Domains with Ports:"))
        self.tool_layout.addWidget(output_area)

    def show_port_scanner(self):
        self.clear_tool_content()

        input_area = self.create_text_area()
        input_area.setPlaceholderText("Enter hostnames/IPs with ports (e.g., itg.ac.id:80) one per line")
        output_area = self.create_text_area()
        output_area.setReadOnly(True)

        process_button = self.create_process_button("Scan Ports")

        def scan_ports():
            # Clear previous results
            output_area.clear()
            
            hosts_and_ports = input_area.toPlainText().strip().split("\n")

            self.thread = PortScannerThread(hosts_and_ports)
            
            def update_output(result, color):
                cursor = output_area.textCursor()
                cursor.movePosition(QTextCursor.End)
                output_area.setTextCursor(cursor)

                # Convert string color to QColor
                color_map = {
                    "green": QColor(0, 255, 0),
                    "red": QColor(255, 0, 0),
                    "black": QColor(0, 0, 0)
                }
                output_area.setTextColor(color_map.get(color, QColor(0, 0, 0)))  # Default to black if color not found
                output_area.append(result)

            self.thread.update_signal.connect(lambda result, color: update_output(result, color))
            self.thread.start()

        process_button.clicked.connect(scan_ports)

        self.tool_layout.addWidget(QLabel("Input Hosts:"))
        self.tool_layout.addWidget(input_area)
        self.tool_layout.addWidget(process_button)
        self.tool_layout.addWidget(QLabel("Scan Results:"))
        self.tool_layout.addWidget(output_area)


    def show_dotoip(self):
        self.clear_tool_content()
        
        input_area = self.create_text_area()
        input_area.setPlaceholderText("Enter domains (one per line)")
        output_area = self.create_text_area()
        output_area.setReadOnly(True)
        
        process_button = self.create_process_button("Convert to IP")
        
        def lookup_dns():
            import socket
            domains = input_area.toPlainText().strip().split('\n')
            results = []
            for domain in domains:
                try:
                    domain = domain.strip()
                    if domain:
                        ip = socket.gethostbyname(domain)
                        results.append(f"{domain} -> {ip}")
                except:
                    results.append(f"{domain} -> Resolution failed")
            output_area.setText('\n'.join(results))
                
        process_button.clicked.connect(lookup_dns)
        
        self.tool_layout.addWidget(QLabel("Input Domains:"))
        self.tool_layout.addWidget(input_area)
        self.tool_layout.addWidget(process_button)
        self.tool_layout.addWidget(QLabel("IP Addresses:"))
        self.tool_layout.addWidget(output_area)

    def show_word_counter(self):
        self.clear_tool_content()
        
        input_area = self.create_text_area()
        input_area.setPlaceholderText("Enter text to count words and characters")
        output_area = self.create_text_area()
        output_area.setReadOnly(True)
        
        process_button = self.create_process_button("Count")
        
        def count_text():
            text = input_area.toPlainText()
            words = len(text.split())
            chars = len(text)
            chars_no_space = len(text.replace(" ", ""))
            lines = len(text.splitlines())
            output = f"Words: {words}\nCharacters (with spaces): {chars}\n"
            output += f"Characters (no spaces): {chars_no_space}\nLines: {lines}"
            output_area.setText(output)
            
        process_button.clicked.connect(count_text)
        
        self.tool_layout.addWidget(QLabel("Input Text:"))
        self.tool_layout.addWidget(input_area)
        self.tool_layout.addWidget(process_button)
        self.tool_layout.addWidget(QLabel("Statistics:"))
        self.tool_layout.addWidget(output_area)

    def show_email_extractor(self):
        self.clear_tool_content()
        
        input_area = self.create_text_area()
        input_area.setPlaceholderText("Enter text containing email addresses")
        output_area = self.create_text_area()
        output_area.setReadOnly(True)
        
        process_button = self.create_process_button("Extract Emails")
        
        def extract_emails():
            text = input_area.toPlainText()
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            if emails:
                output_area.setText('\n'.join(sorted(set(emails))))
            else:
                output_area.setText("No email addresses found")
                
        process_button.clicked.connect(extract_emails)
        
        self.tool_layout.addWidget(QLabel("Input Text:"))
        self.tool_layout.addWidget(input_area)
        self.tool_layout.addWidget(process_button)
        self.tool_layout.addWidget(QLabel("Extracted Emails:"))
        self.tool_layout.addWidget(output_area)

    def show_string_reverser(self):
        self.clear_tool_content()
        
        input_area = self.create_text_area()
        input_area.setPlaceholderText("Enter text to reverse")
        output_area = self.create_text_area()
        output_area.setReadOnly(True)
        
        process_button = self.create_process_button("Reverse")
        
        def reverse_text():
            text = input_area.toPlainText()
            reversed_text = '\n'.join(line[::-1] for line in text.splitlines())
            output_area.setText(reversed_text)
            
        process_button.clicked.connect(reverse_text)
        
        self.tool_layout.addWidget(QLabel("Input Text:"))
        self.tool_layout.addWidget(input_area)
        self.tool_layout.addWidget(process_button)
        self.tool_layout.addWidget(QLabel("Reversed Text:"))
        self.tool_layout.addWidget(output_area)