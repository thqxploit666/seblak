        self.url = url
        self.filters = filters
        self.api_keys = api_keys

    def run(self):
        headers = {}
        for i, api_key in enumerate(self.api_keys):
            headers = {
                'x-rapidapi-key': api_key,
                'x-rapidapi-host': "website-seo-analyzer.p.rapidapi.com"
            }
            response = requests.get(f"https://website-seo-analyzer.p.rapidapi.com/seo/seo-audit-basic?url={self.url}",
                                    headers=headers)

            if response.status_code == 200:
                self.result.emit(response.json())
                self.progress.emit(100)
                break
            else:
                self.progress.emit(int((i + 1) / len(self.api_keys) * 100))
        else:
            self.result.emit({"success": False, "message": "All API keys exhausted or invalid."})
        self.finished.emit()

class SeoAnalyzer(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.analysis_thread = None
        self.api_keys = self.load_api_keys()
        self.init_ui()
        self.apply_theme()

    def load_api_keys(self):
        url = "https://raw.githubusercontent.com/thqxploit666/fire/refs/heads/main/nls.json"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else []

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # URL Input Group
        url_group = QGroupBox("Input URL")
        url_layout = QVBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter website URL (e.g., https://example.com)")
        url_layout.addWidget(self.url_input)
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)

        # Filter Group
        filter_group = QGroupBox("Filter Results")
        filter_layout = QVBoxLayout()
        self.filter_http = QCheckBox("HTTP Details")
        self.filter_title = QCheckBox("Title Analysis")
        self.filter_meta = QCheckBox("Meta Description")
        self.filter_headings = QCheckBox("Headings Summary")
        self.filter_links = QCheckBox("Links Summary")
        filter_layout.addWidget(self.filter_http)
        filter_layout.addWidget(self.filter_title)
        filter_layout.addWidget(self.filter_meta)
        filter_layout.addWidget(self.filter_headings)
        filter_layout.addWidget(self.filter_links)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Analyze Button
        self.analyze_button = QPushButton("Analyze SEO")
        self.analyze_button.clicked.connect(self.start_analysis)
        layout.addWidget(self.analyze_button)

        # Results Area
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        self.results_label = QLabel()
        self.results_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.results_label.setWordWrap(True)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.results_label)
        scroll_area.setMinimumHeight(400)
        results_layout.addWidget(scroll_area)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        self.setLayout(layout)

    def apply_theme(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme['background']};
                color: {self.theme['text']};
            }}
            QPushButton {{
                background-color: {self.theme['content_background']};
                border: 1px solid {self.theme['border']};
                border-radius: 4px;
                padding: 8px;
                color: {self.theme['text']};
            }}
            QPushButton:hover {{
                background-color: {self.theme['button_hover']};
            }}
        """)

    def start_analysis(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL.")
            return

        filters = {
            "http": self.filter_http.isChecked(),
            "title": self.filter_title.isChecked(),
            "meta_description": self.filter_meta.isChecked(),
            "headings": self.filter_headings.isChecked(),
            "links": self.filter_links.isChecked(),
        }

        if not any(filters.values()):
            QMessageBox.warning(self, "Error", "Please select at least one filter.")
            return

        if not self.api_keys:
            QMessageBox.critical(self, "Error", "No API keys available.")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_label.setText("Analyzing SEO...")
        self.analyze_button.setEnabled(False)

        self.analysis_thread = SeoAnalyzerThread(url, filters, self.api_keys)
        self.analysis_thread.progress.connect(self.update_progress)
        self.analysis_thread.result.connect(self.display_results)
        self.analysis_thread.finished.connect(self.analysis_complete)
        self.analysis_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_results(self, results):
        if results.get("success"):
            self.results_label.setText(json.dumps(results.get("result"), indent=4))
        else:
            self.results_label.setText(results.get("message", "An error occurred."))

    def analysis_complete(self):
        self.analyze_button.setEnabled(True)
        self.progress_bar.setVisible(False)
