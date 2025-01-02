from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QPlainTextEdit, QPushButton, QMessageBox)
import hashlib
import zlib
import base64

class HashGenerator(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme  # Store the theme for styling
        self.init_ui()

    def init_ui(self):
        # Main layout
        hash_layout = QVBoxLayout(self)

        # Input field for text to hash
        self.hash_input = QLineEdit(self)
        self.hash_input.setPlaceholderText("Enter text to hash or unhash")
        self.hash_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 8px;
                color: {self.theme['text']};
            }}
        """)
        hash_layout.addWidget(self.hash_input)

        # Dropdown for hash algorithms
        hash_algorithms = [
            "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
            "blake2b", "blake2s", "sha3_224", "sha3_256", "sha3_384",
            "sha3_512", "adler32", "crc32", "base64"
        ]
        self.hash_algorithm_combo = QComboBox(self)
        self.hash_algorithm_combo.addItems(hash_algorithms)
        self.hash_algorithm_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 5px;
                color: {self.theme['text']};
            }}
        """)
        self.hash_algorithm_combo.currentTextChanged.connect(self.update_buttons_visibility)
        hash_layout.addWidget(self.hash_algorithm_combo)

        # Output field for generated hash
        self.hash_output = QPlainTextEdit(self)
        self.hash_output.setReadOnly(True)
        self.hash_output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 8px;
                color: {self.theme['text']};
            }}
        """)
        hash_layout.addWidget(self.hash_output)

        # Buttons for hash and unhash
        self.button_layout = QHBoxLayout()

        self.generate_button = QPushButton("Generate Hash", self)
        self.generate_button.clicked.connect(self.generate_hash)
        self.generate_button.setStyleSheet(f"""
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
        self.button_layout.addWidget(self.generate_button)

        self.unhash_button = QPushButton("Unhash", self)
        self.unhash_button.clicked.connect(self.unhash_text)
        self.unhash_button.setStyleSheet(f"""
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
        self.button_layout.addWidget(self.unhash_button)

        hash_layout.addLayout(self.button_layout)
        self.update_buttons_visibility()  # Set initial visibility

    def generate_hash(self):
        input_text = self.hash_input.text().encode('utf-8')
        selected_algorithm = self.hash_algorithm_combo.currentText()

        try:
            if selected_algorithm in hashlib.algorithms_available:
                hasher = hashlib.new(selected_algorithm)
                hasher.update(input_text)
                self.hash_output.setPlainText(hasher.hexdigest())
            elif selected_algorithm == "adler32":
                result = zlib.adler32(input_text)
                self.hash_output.setPlainText(format(result, '08x'))
            elif selected_algorithm == "crc32":
                result = zlib.crc32(input_text)
                self.hash_output.setPlainText(format(result, '08x'))
            elif selected_algorithm == "base64":
                encoded = base64.b64encode(input_text).decode('utf-8')
                self.hash_output.setPlainText(encoded)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error hashing text: {str(e)}")

    def unhash_text(self):
        input_text = self.hash_input.text()
        selected_algorithm = self.hash_algorithm_combo.currentText()

        try:
            if selected_algorithm == "base64":
                decoded = base64.b64decode(input_text.encode('utf-8')).decode('utf-8')
                self.hash_output.setPlainText(decoded)
            else:
                raise ValueError(f"Unhashing not supported for: {selected_algorithm}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error unhashing text: {str(e)}")

    def update_buttons_visibility(self):
        selected_algorithm = self.hash_algorithm_combo.currentText()
        if selected_algorithm == "base64":
            self.unhash_button.setVisible(True)
        else:
            self.unhash_button.setVisible(False)
