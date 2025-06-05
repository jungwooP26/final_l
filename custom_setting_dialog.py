from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QDialogButtonBox, QMessageBox

class CustomSettingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom 모드 설정")

        # 1. 총 턴 수 입력
        self.total_turns_input = QLineEdit()
        self.total_turns_input.setPlaceholderText("총 턴 수 (예: 3)")

        # 2. 라운드 수 입력
        self.rounds_per_turn_input = QLineEdit()
        self.rounds_per_turn_input.setPlaceholderText("턴당 라운드 수 (3 이하로 설정)")

        # 3. 초기 목표 점수 입력
        self.initial_target_input = QLineEdit()
        self.initial_target_input.setPlaceholderText("초기 목표 점수 (예: 100)")

        # 4. 턴당 증가 점수 입력
        self.increase_per_turn_input = QLineEdit()
        self.increase_per_turn_input.setPlaceholderText("턴마다 증가할 점수 (예: 50)")

        # 확인 / 취소 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)

        # 레이아웃 구성
        layout = QVBoxLayout()
        layout.addWidget(QLabel("총 턴 수:"))
        layout.addWidget(self.total_turns_input)
        layout.addWidget(QLabel("턴당 라운드 수:"))
        layout.addWidget(self.rounds_per_turn_input)
        layout.addWidget(QLabel("초기 목표 점수:"))
        layout.addWidget(self.initial_target_input)
        layout.addWidget(QLabel("턴당 증가 점수:"))
        layout.addWidget(self.increase_per_turn_input)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def validate_and_accept(self):
        try:
            self.total_turns = int(self.total_turns_input.text())
            self.rounds_per_turn = int(self.rounds_per_turn_input.text())
            self.initial_target = int(self.initial_target_input.text())
            self.increase_per_turn = int(self.increase_per_turn_input.text())

            if (
                self.total_turns <= 0
                or self.rounds_per_turn <= 0
                or self.rounds_per_turn > 3  # 🔒 여기에서 최대값 제한
            ):
                raise ValueError("양의 정수를 입력하고, 턴당 라운드는 3 이하로 설정하세요.")

            self.accept()
        except ValueError:
            QMessageBox.warning(self, "입력 오류", "모든 값을 양의 정수로 입력하고,\n턴당 라운드는 3 이하로 설정하세요.")



    def get_settings(self):
        return (
            self.total_turns,
            self.rounds_per_turn,
            self.initial_target,
            self.increase_per_turn
        )
