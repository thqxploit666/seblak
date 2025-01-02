from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
import shodan

class ShodanWorker(QThread):
    search_complete = pyqtSignal(object)

    def __init__(self, shodan_api_key, query):
        super().__init__()
        self.shodan_api_key = shodan_api_key
        self.query = query
        self._is_running = True

    def run(self):
        try:
            api = shodan.Shodan(self.shodan_api_key)
            if self._is_running:
                results = api.search(self.query)
                if self._is_running:
                    self.search_complete.emit(results)
        except shodan.APIError as e:
            if self._is_running:
                self.search_complete.emit({"error": str(e)})

    def stop(self):
        self._is_running = False

class ShodanDorkingWidget(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.shodan_api_keys = [
            "OefcMxcunkm72Po71vVtX8zUN57vQtAC",
            "PSKINdQe1GyxGgecYz2191H2JoS9qvgD",
            "EBeU0lGqtIO6yCxVFCWC4nUVbvovtjo5",
            "XYdjHDeJM36AjDfU1feBsyMJIj8XxGzD",
            "pHHlgpFt8Ka3Stb5UlTxcaEwciOeF2QM",
            "61TvA2dNwxNxmWziZxKzR5aO9tFD00Nj",
            "xTbXXOSBr0R65OcClImSwzadExoXU4tc",
            "EJV3A4Mka2wPs7P8VBCO6xcpRe27iNJu",
            "mEuInz8UH1ixLGJq4oQhEiJORERVG5xc",
            "lkY0ng0XMo29zEhzyw3ibQfeEBxghwPF",
            "syeCnFndQ8TE4qAGvhm9nZLBZOBgoLKd",
            "7TeyFZ8oyLulHwYUOcSPzZ5w3cLYib61",
            "v4YpsPUJ3wjDxEqywwu6aF5OZKWj8kik",
            "dTNGRiwYNozXIDRf5DWyGNbkdiS5m3JK",
            "kdnzf4fsYWQmGajRDn3hB0RElbUlIaqu",
            "boYedPn8iDWi6GDSO6h2kz72VLt6bZ3S",
            "FQNAMUdkeqXqVOdXsTLYeatFSpZSktdb",
            "OygcaGSSq46Lg5fZiADAuFxl4OBbn7zm",
            "XAbsu1Ruj5uhTNcxGdbGNgrh9WuMS1B6",
            "nkGd8uVE4oryfUVvioprswdKGmA5InzZ",
            "XYdjHDeJM36AjDfU1feBsyMJIj8XxGzD",
            "EBeU0lGqtIO6yCxVFCWC4nUVbvovtjo5",
        ]
        self.current_shodan_api_index = 0
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.dork_input = QLineEdit(self)
        self.dork_input.setPlaceholderText("Enter dork query")
        self.dork_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 8px;
                color: {self.theme['text']};
            }}
        """)
        layout.addWidget(self.dork_input)

        search_button = QPushButton("Search", self)
        search_button.clicked.connect(self.start_shodan_search)
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

        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 8px;
                color: {self.theme['text']};
            }}
        """)
        layout.addWidget(self.result_text)

    def start_shodan_search(self):
        dork_query = self.dork_input.text().strip()
        if not dork_query:
            self.result_text.setPlainText("Please enter a dork query.")
            return

        shodan_api_key = self.shodan_api_keys[self.current_shodan_api_index]

        if self.worker is not None:
            self.worker.stop()
            self.worker.wait()

        self.worker = ShodanWorker(shodan_api_key, dork_query)
        self.worker.search_complete.connect(self.on_search_complete)
        self.worker.start()
        self.result_text.setPlainText("Searching...")

    def on_search_complete(self, results):
        if "error" in results:
            self.result_text.setPlainText(f"Error: {results['error']}")

            error_message = results['error']
            if "403" in error_message or "429" in error_message:
                self.current_shodan_api_index = (self.current_shodan_api_index + 1) % len(self.shodan_api_keys)
                shodan_api_key = self.shodan_api_keys[self.current_shodan_api_index]

                self.worker = ShodanWorker(shodan_api_key, self.dork_input.text().strip())
                self.worker.search_complete.connect(self.on_search_complete)
                self.worker.start()
                self.result_text.append("waitttt.... retryyy :)")
        else:
            if results.get('matches'):
                ip_list = [host['ip_str'] for host in results['matches']]
                total_results = len(ip_list)
                self.result_text.setPlainText(f"Total results: {total_results}\n" + '\n'.join(ip_list))
            else:
                self.result_text.setPlainText("No results found.")
