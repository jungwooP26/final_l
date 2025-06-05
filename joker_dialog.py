from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

class JokerCardDialog(QDialog):
    def __init__(self, parent=None, joker_cards=None):
        super().__init__(parent)

        self.setWindowTitle("조커 카드 선택")
        self.setFixedSize(500, 250)

        self.layout = QHBoxLayout()
        self.button_group = []
        self.selected_joker = None

        # 전달된 조커 카드 목록 사용
        self.joker_cards = joker_cards if joker_cards else []

        for name, tooltip in self.joker_cards:
            btn = QPushButton(name)
            btn.setFixedSize(120, 180)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(self.default_style())
            btn.clicked.connect(lambda _, b=btn, n=name: self.select_joker(b, n))
            self.layout.addWidget(btn)
            self.button_group.append(btn)

        # 확인 버튼
        close_btn = QPushButton("확인")
        close_btn.clicked.connect(self.confirm_selection)

        vbox = QVBoxLayout()
        vbox.addLayout(self.layout)
        vbox.addWidget(close_btn, alignment=Qt.AlignCenter)
        self.setLayout(vbox)

    def default_style(self):
        return """
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                color: black;
                border: 2px solid black;
                border-radius: 8px;
                background-color: white;
            }
            QPushButton:hover {
                border: 3px solid blue;
                background-color: #f0f8ff;
            }
        """

    def selected_style(self):
        return """
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                color: white;
                border: 3px solid darkblue;
                border-radius: 8px;
                background-color: #4169e1;
            }
        """

    def select_joker(self, button, name):
        for btn in self.button_group:
            btn.setStyleSheet(self.default_style())

        button.setStyleSheet(self.selected_style())
        self.selected_joker = name

    def confirm_selection(self):
        if self.selected_joker is None:
            QMessageBox.warning(self, "선택 안 됨", "조커 카드를 하나 선택해주세요.")
        else:
            self.accept()
