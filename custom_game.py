from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QTimer
import random
from basic_game import BasicGameWindow
from PyQt5.QtWidgets import QMessageBox
from utils import calculate_score

class CustomGameWindow(BasicGameWindow):
    def __init__(self, stacked_widget, total_turns, rounds_per_turn, initial_target, increase_per_turn):
        super().__init__(stacked_widget)
        self.total_turns = total_turns
        self.rounds_per_turn = rounds_per_turn
        self.increase_per_turn = increase_per_turn
        self.target_score = initial_target
        self.target_label.setText(f"목표 점수: {self.target_score}")

    def confirm_selection(self):
        if self.phase == 1:
            self.selected_cards = [b for b in self.upper_buttons if b.isChecked()]
            for b in self.selected_cards:
                b.setEnabled(False)
            self.phase = 2
            self.confirm_btn.setEnabled(False)
            self.animate_card_disappearance(
                [b for b in self.upper_buttons if not b.isChecked()],
                lambda: self.generate_cards(self.lower_layout, self.lower_buttons, 4)
            )
            return

        selected = [b for b in self.lower_buttons if b.isChecked()]
        if len(self.selected_cards) + len(selected) != 5:
            return

        all_selected = self.selected_cards + selected
        if self.selected_joker == "응축된 분노":
            self.stored_multiplier += 0.5 * len([b for b in self.upper_buttons if not b.isChecked()])

        info = calculate_score(all_selected, self.selected_joker, self.previous_hand_type, self.friend_suit, self.broken_jokers, self.stored_multiplier)

        if info.get("auto_pass"):
            self.selected_joker = "무너진 마지노선"

        round_score = info['total_score']
        self.total_score += round_score
        self.previous_hand_type = info['hand_type']

        self.round += 1
        if self.round > self.rounds_per_turn:  # 🔁 사용자 설정 반영
            if self.turn >= self.total_turns:
                QMessageBox.information(self, "게임 종료", "모든 턴이 종료되었습니다.")
                self.stacked_widget.setCurrentIndex(0)
                return
            elif self.total_score >= self.target_score:
                self.show_loading_message("🎉 목표 점수 달성! 다음 턴으로 넘어갑니다...", next_turn=True)
            else:
                QMessageBox.information(self, "게임 종료", "목표 점수를 달성하지 못했습니다.")
                self.stacked_widget.setCurrentIndex(0)
            return

        self.total_score_label.setText(f"누적 점수: {self.total_score:.2f}")
        self.round_label.setText(f"라운드: {self.round}")
        self.friend_suit = random.choice(['♥', '♠', '♦', '♣'])
        self.selected_cards.clear()
        self.upper_buttons.clear()
        self.lower_buttons.clear()
        self.confirm_btn.setEnabled(False)
        self.selected_joker = None
        self.phase = 1
        self.current_joker_group = None
        for layout in [self.upper_layout, self.lower_layout]:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        self.generate_cards(self.upper_layout, self.upper_buttons, 4)

    def show_loading_message(self, message, next_turn=False):
        self.loading_label = QLabel(message, self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("""
            background-color: white; border: 2px solid #666;
            padding: 15px; font-size: 14pt; font-weight: bold;
        """)
        self.loading_label.setFixedSize(400, 80)
        self.loading_label.setGeometry((960 - 400) // 2, (640 - 80) // 2, 400, 80)
        self.loading_label.show()

        def proceed():
            self.used_joker_count = 0
            self.loading_label.hide()
            if next_turn:
                self.turn += 1
                self.round = 1
                previous_target = self.target_score
                self.target_score += self.increase_per_turn  # 사용자 설정 적용
                self.turn_label.setText(f"턴: {self.turn}")
                self.round_label.setText("라운드: 1")
                self.target_label.setText(f"목표 점수: {self.target_score}")
                surplus = self.total_score - previous_target
                self.total_score = max(0, surplus)
                self.total_score_label.setText(f"누적 점수: {self.total_score:.2f}")
                self.jokers_this_turn = random.sample(self.all_jokers, 9)
                self.used_joker_count = 0
                self.selected_joker = None
                self.broken_jokers = set()
                self.stored_multiplier = 0.0
                self.friend_suit = random.choice(['♥', '♠', '♦', '♣'])
                self.reset_game()

        QTimer.singleShot(1500, proceed)