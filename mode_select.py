from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QDialog, QTextEdit
from PyQt5.QtCore import Qt, QTimer
from basic_game import BasicGameWindow
from custom_game import CustomGameWindow
from custom_setting_dialog import CustomSettingDialog
from record_manager import get_high_turn, get_all_history

class ModeSelectWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        self.view_record_button = QPushButton("📜 기록 보기")
        self.view_record_button.setStyleSheet("font-size: 14px;")
        self.view_record_button.clicked.connect(self.show_records)
        layout.addWidget(self.view_record_button)

        icon_layout = QHBoxLayout()
        self.left_icons = QLabel('♥ ♠')
        self.right_icons = QLabel('♣ ♦')
        self.left_icons.setStyleSheet("color: red; font-size: 18px; padding-right: 8px;")
        self.right_icons.setStyleSheet("color: black; font-size: 18px; padding-left: 8px;")
        self.title = QLabel("SHUFFLE")
        self.title.setStyleSheet("font-size: 22px; font-weight: bold; color: black;")
        self.title.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(self.left_icons)
        icon_layout.addWidget(self.title)
        icon_layout.addWidget(self.right_icons)

        self.basic_button = QPushButton("🎯 Basic 모드")
        self.basic_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.basic_button.clicked.connect(self.start_basic_mode)

        self.custom_mode_button = QPushButton("🎯 Custom 모드")
        self.custom_mode_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.custom_mode_button.clicked.connect(self.open_custom_game)

        layout.addLayout(icon_layout)
        layout.addWidget(self.basic_button)
        layout.addWidget(self.custom_mode_button)

        self.loading_label = QLabel("🃏 카드를 준비 중입니다...", self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("""
            background-color: white;
            border: 2px solid #666;
            padding: 15px;
            font-size: 14pt;
            font-weight: bold;
        """)
        self.loading_label.setFixedSize(300, 80)
        self.loading_label.setGeometry((960 - 300) // 2, (640 - 80) // 2, 300, 80)
        self.loading_label.hide()

    def hide_all_ui(self):
        self.title.hide()
        self.left_icons.hide()
        self.right_icons.hide()
        self.basic_button.hide()
        self.custom_mode_button.hide()
        self.view_record_button.hide()

    def show_all_ui(self):
        self.title.show()
        self.left_icons.show()
        self.right_icons.show()
        self.basic_button.show()
        self.custom_mode_button.show()
        self.view_record_button.show()

    def start_basic_mode(self):
        self.hide_all_ui()
        self.loading_label.setText("🃏 카드를 준비 중입니다...")
        self.loading_label.show()
        self.loading_label.raise_()
        QTimer.singleShot(800, self.open_basic_game)

    def open_basic_game(self):
        for i in range(self.stacked_widget.count()):
            widget = self.stacked_widget.widget(i)
            if isinstance(widget, BasicGameWindow):
                self.stacked_widget.removeWidget(widget)
                widget.deleteLater()

        basic_ui = BasicGameWindow(self.stacked_widget)
        basic_ui.reset_game()
        self.stacked_widget.addWidget(basic_ui)
        self.stacked_widget.setCurrentWidget(basic_ui)

    def open_custom_game(self):
        dialog = CustomSettingDialog(self)
        if dialog.exec_():
            turns, rounds, target, increase = dialog.get_settings()
            self.hide_all_ui()
            self.loading_label.setText("🃏 카드를 준비 중입니다...")
            self.loading_label.show()

            def proceed():
                custom_ui = CustomGameWindow(self.stacked_widget, turns, rounds, target, increase)
                self.stacked_widget.addWidget(custom_ui)
                self.stacked_widget.setCurrentWidget(custom_ui)

            QTimer.singleShot(800, proceed)

    def showEvent(self, event):
        self.show_all_ui()
        self.loading_label.hide()

    def show_records(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("📜 개인 기록")
        text = QTextEdit()
        text.setReadOnly(True)

        history = get_all_history()
        if not history:
            text.setText("저장된 기록이 없습니다.")
        else:
            lines = [f"{i+1}. 턴: {r['turn']}, 라운드: {r['round']}, 점수: {r['total_score']}, 목표: {r['target_score']}" for i, r in enumerate(history)]
            text.setText("\n".join(lines))

        layout = QVBoxLayout()
        layout.addWidget(text)
        dialog.setLayout(layout)
        dialog.resize(400, 300)
        dialog.exec_()

