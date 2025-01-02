from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QGridLayout
from PyQt5.QtCore import QTimer, Qt, QDateTime, QPropertyAnimation, QRect
from PyQt5.QtGui import QIcon
import subprocess
import platform
import socket

class ContentWidget(QWidget):
    def __init__(self, title, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.ping_label = None
        self.time_label = None
        self.init_ui(title)
        

    def init_ui(self, title):
        # Layout utama
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(15, 15, 15, 15)

        # Kontainer untuk konten
        content_container = QFrame()
        content_container.setObjectName("contentContainer")
        content_container.setStyleSheet(f"""
            #contentContainer {{
                background-color: {self.theme['content_background']};
                border-radius: 15px;
                border: 1px solid {self.theme['border']};
            }}
        """)
        content_layout = QVBoxLayout(content_container)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel(title)
        header_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {self.theme['text']};
            margin: 0px;
        """)
        header_layout.addWidget(header_label, alignment=Qt.AlignCenter)

        content_layout.addLayout(header_layout)

        # Tambahkan konten sesuai dengan judul
        if title.upper() == "HOME":
            self.add_home_content(content_layout)
        elif title.upper() == "REVSHELL GENERATOR":
            from seblak.r_generator import ReverseShellGenerator
            revshell_widget = ReverseShellGenerator(self.theme)
            content_layout.addWidget(revshell_widget)
        elif title.upper() == "HASH GENERATOR":
            from seblak.hash import HashGenerator
            hash_widget = HashGenerator(self.theme)
            content_layout.addWidget(hash_widget)
        elif title.upper() == "REVIP DOMAIN CHECK":
            from seblak.revip import ReverseIP
            revip_widget = ReverseIP(self.theme)
            content_layout.addWidget(revip_widget)
        elif title.upper() == "SUBDO FINDER":
            from seblak.subdofind import SubdomainFinder
            subdo_widget = SubdomainFinder(self.theme)
            content_layout.addWidget(subdo_widget)
        elif title.upper() == "DOMAIN INFO":
            from seblak.doinfo import DomainInfoWidget
            doinfo_widget = DomainInfoWidget(self.theme)
            content_layout.addWidget(doinfo_widget)
        elif title.upper() == "PORT SCANNER":
            from seblak.nmap import NmapScanner
            nmap_widget = NmapScanner(self.theme)
            content_layout.addWidget(nmap_widget)
        elif title.upper() == "DB VULNERABILITY":        
            from seblak.dbv import VulnerabilitySearchWidget
            vuln_search_widget = VulnerabilitySearchWidget(self.theme)
            content_layout.addWidget(vuln_search_widget)
        elif title.upper() == "SHODAN DORKING":
            from seblak.shdn import ShodanDorkingWidget
            shodan_widget = ShodanDorkingWidget(self.theme)
            content_layout.addWidget(shodan_widget)
        elif title.upper() == "FOLDER ENCRYPTOR":
            from seblak.fenc import FolCryptorApp
            fenc_widget = FolCryptorApp(self.theme)
            content_layout.addWidget(fenc_widget)
        elif title.upper() == "ENCODING KODE":
            from seblak.obs import ObfuscatorApp
            obs_widget = ObfuscatorApp(self.theme)
            content_layout.addWidget(obs_widget)
        elif title.upper() == "WEB SEO ANALYSIS":
            from seblak.analiseo import SeoAnalyzer
            seo_widget = SeoAnalyzer(self.theme)
            content_layout.addWidget(seo_widget)
        elif title.upper() == "SQLI SCANNER":
            from seblak.sscanql import SQLiScanner
            sql_widget = SQLiScanner(self.theme)
            content_layout.addWidget(sql_widget)
        elif title.upper() == "GABUT TOOLS":
            from seblak.gtls import GTLSTools
            gtls_widget = GTLSTools(self.theme)
            content_layout.addWidget(gtls_widget)
        elif title.upper() == "CHECK UPDATE":
            from seblak.apdetindong import UpdateChecker
            update_widget = UpdateChecker(self.theme)
            content_layout.addWidget(update_widget)

        else:
            placeholder = QLabel(f"Content for {title} is under development")
            placeholder.setStyleSheet(f"color: {self.theme['secondary_text']}; font-size: 16px;")
            placeholder.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(placeholder)

        layout.addWidget(content_container)

    def add_home_content(self, layout):
        # Informasi aplikasi
        introduction = QLabel(
                        "Selamat datang di <b>Zero-Defender App</b>, evolusi dari WslTools! Aplikasi ini memberikan kesempatan "
                        "untuk bereksperimen memahami sistem keamanan, termasuk mencoba mempenetrasi sistem server  "
                        "dengan fitur-fitur yang dirancang ramah pengguna. Aplikasi ini akan terus berkembang dengan penambahan "
                        "fitur-fitur menarik dan bermanfaat."
                        "<br><br>"
                        "Dibuat oleh <b>WSL`User</b> didukung oleh <b>TSecNetwork Hacker Community</b> dan <b>Bengkulu Anomaly Crews</b>."
                    )
        introduction.setWordWrap(True)
        introduction.setStyleSheet(f"color: {self.theme['secondary_text']}; font-size: 16px;")
        layout.addWidget(introduction)

        # Kontainer untuk info
        info_container = QFrame()
        info_container.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme['background']};
                padding: 10px;
            }}
        """)

        # Layout vertikal untuk semua baris info
        info_layout = QVBoxLayout(info_container)
        info_layout.setSpacing(5)  # Jarak antar baris lebih kecil
        info_layout.setContentsMargins(0, 0, 0, 0)

        # Tambahkan setiap baris informasi
        def add_info_row(label_text, value_text):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(5)  # Jarak kecil antara keterangan dan nilai
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {self.theme['text']}; font-weight: bold;")
            value = QLabel(value_text)
            value.setStyleSheet(f"color: {self.theme['accent']}; font-size: 16px; ")
            
            row_layout.addWidget(label, alignment=Qt.AlignRight)
            row_layout.addWidget(value, alignment=Qt.AlignLeft)
            return row_layout

        # IPv4
        ipv4_row = add_info_row("IPv4:", self.get_ipv4_address())
        info_layout.addLayout(ipv4_row)

        # OS Version
        os_row = add_info_row("OS Version:", f"{platform.system()} {platform.release()}")
        info_layout.addLayout(os_row)

        # Time
        time_row = QHBoxLayout()
        time_row.setSpacing(5)
        time_row.setContentsMargins(0, 0, 0, 0)

        time_label = QLabel("Time:")
        time_label.setStyleSheet(f"color: {self.theme['text']}; font-weight: bold;")
        self.time_label = QLabel("--:--:--")
        self.time_label.setStyleSheet(f"""
            color: {self.theme['accent']};
            font-size: 16px;
        """)

        time_row.addWidget(time_label, alignment=Qt.AlignRight)
        time_row.addWidget(self.time_label, alignment=Qt.AlignLeft)
        info_layout.addLayout(time_row)

        # Tambahkan kontainer ke layout utama
        layout.addWidget(info_container)

        # Timer untuk memperbarui waktu
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)

    def update_time(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.time_label.setText(current_time)


    def complete_time_update(self, new_time, original_geometry):
        self.time_label.setText(new_time)
        
        # Animasi fade in (scaling up)
        fade_in = QPropertyAnimation(self.time_label, b"geometry")
        fade_in.setDuration(200)
        fade_in.setStartValue(QRect(original_geometry.x(), original_geometry.y() - 10,
                                  original_geometry.width(), original_geometry.height()))
        fade_in.setEndValue(original_geometry)
        fade_in.start()

    @staticmethod
    def get_ipv4_address():
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception as e:
            return "Tidak ditemukan"
