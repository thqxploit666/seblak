import base64
import zlib
import random
import string
import marshal
import hashlib
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ObfuscatorThread(QThread):
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, code, language, level):
        super().__init__()
        self.code = code
        self.language = language
        self.level = level

    def run(self):
        try:
            # Remove PHP tags if the language is PHP
            if self.language == "php":
                self.code = self.remove_php_tags(self.code)

            if self.language == "php":
                result = self.obfuscate_php()
            elif self.language == "python":
                result = self.obfuscate_python()
            elif self.language == "javascript":
                result = self.obfuscate_javascript()
            else:
                raise ValueError("Unsupported language selected.")
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def remove_php_tags(self, code):
        """Remove PHP tags <?php and ?> from the code."""
        code = code.strip()
        if code.startswith("<?php"):
            code = code[5:]  # Remove <?php
        if code.endswith("?>"):
            code = code[:-2]  # Remove ?>
        return code.strip()

    def generate_key(self, length=16):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def obfuscate_php(self):
        self.progress.emit(25)
        if self.level == "slowly":
            encoded = base64.b64encode(self.code.encode()).decode()
            result = f"<?php eval(base64_decode('{encoded}')); ?>"

        elif self.level == "medium":
            key = self.generate_key()
            encoded = base64.b64encode(zlib.compress(self.code.encode())).decode()
            result = f"""<?php
$k='{key}';
eval(gzuncompress(base64_decode('{encoded}')));
?>"""

        else:  # hard
            key1 = self.generate_key()
            key2 = self.generate_key()
            encoded = base64.b64encode(zlib.compress(self.code.encode())).decode()
            result = f"""lagi ngebug cokkk"""

        self.progress.emit(100)
        return result

    def obfuscate_python(self):
        self.progress.emit(25)
        if self.level == "slowly":
            encoded = base64.b64encode(marshal.dumps(compile(self.code, '<string>', 'exec'))).decode()
            result = f"import marshal,base64\nexec(marshal.loads(base64.b64decode('{encoded}')))"

        elif self.level == "medium":
            key = self.generate_key()
            compressed = base64.b64encode(zlib.compress(self.code.encode())).decode()
            key_hash = hashlib.sha256(key.encode()).hexdigest()
            result = f"""import base64,zlib,hashlib
k='{key}'
if hashlib.sha256(k.encode()).hexdigest() == '{key_hash}':
    exec(zlib.decompress(base64.b64decode('{compressed}')).decode())"""

        else:  # hard
            encoded = base64.b64encode(zlib.compress(marshal.dumps(
                compile(self.code, '<string>', 'exec')))).decode()
            key = self.generate_key()
            key_hash = hashlib.sha256(key.encode()).hexdigest()
            result = f"""lagi ngebug cokkk"""

        self.progress.emit(100)
        return result

    def obfuscate_javascript(self):
        self.progress.emit(25)
        if self.level == "slowly":
            encoded = base64.b64encode(self.code.encode()).decode()
            result = f"eval(atob('{encoded}'));"

        elif self.level == "medium":
            encoded = ''.join(f"\\u{ord(c):04x}" for c in self.code)
            key = self.generate_key()
            result = f"""
(function(k){{
    if(k==='{key}'){{
        eval('{encoded}');
    }}
}})('{key}');"""

        else:  # hard
            encoded = base64.b64encode(self.code.encode()).decode()
            key1 = self.generate_key()
            key2 = self.generate_key()
            result = f"""
(lagi ngebug cokkk"""

        self.progress.emit(100)
        return result

class ObfuscatorApp(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.input_code = QTextEdit(self)
        self.language_group = QGroupBox("Select Language", self)
        self.php_radio = QRadioButton("PHP", self)
        self.python_radio = QRadioButton("Python", self)
        self.js_radio = QRadioButton("JavaScript", self)
        self.php_radio.setChecked(True)
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(self.php_radio)
        lang_layout.addWidget(self.python_radio)
        lang_layout.addWidget(self.js_radio)
        self.language_group.setLayout(lang_layout)
        self.level_group = QGroupBox("Select Obfuscation Level", self)
        self.slowly_radio = QRadioButton("Slowly", self)
        self.medium_radio = QRadioButton("Medium", self)
        self.hard_radio = QRadioButton("Hard")
        self.slowly_radio.setChecked(True)
        level_layout = QHBoxLayout()
        level_layout.addWidget(self.slowly_radio)
        level_layout.addWidget(self.medium_radio)
        level_layout.addWidget(self.hard_radio)
        self.level_group.setLayout(level_layout)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        self.gas_button = QPushButton("Obfuscate", self)
        self.gas_button.clicked.connect(self.execute_obfuscation)
        layout.addWidget(self.input_code)
        layout.addWidget(self.language_group)
        layout.addWidget(self.level_group)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.gas_button)
        self.setLayout(layout)

    def execute_obfuscation(self):
        code = self.input_code.toPlainText()
        if not code.strip():
            QMessageBox.critical(self, "Error", "Please input some code to obfuscate.")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.gas_button.setEnabled(False)

        language = "php" if self.php_radio.isChecked() else "python" if self.python_radio.isChecked() else "javascript"
        level = "slowly" if self.slowly_radio.isChecked() else "medium" if self.medium_radio.isChecked() else "hard"

        self.obfuscator_thread = ObfuscatorThread(code, language, level)
        self.obfuscator_thread.finished.connect(self.on_obfuscation_finished)
        self.obfuscator_thread.progress.connect(self.update_progress)
        self.obfuscator_thread.error.connect(self.on_error)
        self.obfuscator_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_obfuscation_finished(self, result):
        self.progress_bar.setVisible(False)
        self.gas_button.setEnabled(True)
        QMessageBox.information(self, "Success", "Code obfuscation completed!")
        self.input_code.setText(result)

    def on_error(self, message):
        self.progress_bar.setVisible(False)
        self.gas_button.setEnabled(True)
        QMessageBox.critical(self, "Error", f"An error occurred: {message}")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    theme = "dark"
    window = ObfuscatorApp(theme)
    window.setWindowTitle("Code Obfuscator")
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec_())
