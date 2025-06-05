from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QMessageBox, QGraphicsOpacityEffect
)
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtCore import Qt, QTimer
import random
from joker_dialog import JokerCardDialog
from utils import calculate_score
from show_my_deck import MyDeckDialog
from record_manager import get_high_turn, save_record


class BasicGameWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.current_joker_group = None
        self.turn = 1
        self.round = 1
        self.total_score = 0.0
        self.target_score = 100

        self.phase = 1
        self.selected_cards = []
        self.upper_buttons = []
        self.lower_buttons = []
        self.selected_joker = None
        self.broken_jokers = set()
        self.stored_multiplier = 0.0
        self.previous_hand_type = None
        self.friend_suit = random.choice(['♥', '♠', '♦', '♣'])

        self.all_jokers = [
            ("피보나치의 축복", "A,2,3,5,8 포함 카드마다 +13점"),
            ("왕국의 위엄", "K 카드 1장당 ×1.5 배수"),
            ("마지노선", "제한의 2/3 넘으면 자동 통과, 사용 후 폐기"),
            ("응축된 분노", "버릴 때마다 +0.5배 저장, 사용 시 리셋"),
            ("삼위일체", "트리플 또는 3카드 족보 시 ×3.33"),
            ("막장드라마", "Q 포함, K 제외 족보 시 ×2.5"),
            ("동그라미의 꿈", "6, 8, 9 포함 카드마다 +6.89점"),
            ("친구", "특정 무늬 1장당 +12점 (매 라운드 무늬 고정)"),
            ("관성", "이전과 같은 족보라면 ×1.5")
        ]
        self.jokers_this_turn = random.sample(self.all_jokers, 9)
        self.used_joker_count = 0

        # UI 설정
        self.turn_label = QLabel("턴: 1")
        self.round_label = QLabel("라운드: 1")
        self.total_score_label = QLabel("누적 점수: 0.0")
        self.target_label = QLabel("목표 점수: 100")

        info_layout = QVBoxLayout()
        for lbl in [self.turn_label, self.round_label, self.total_score_label, self.target_label]:
            lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
            info_layout.addWidget(lbl)

        self.confirm_btn = QPushButton("🔒 선택 완료")
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.clicked.connect(self.confirm_selection)

        self.joker_btn = QPushButton("🃏 조커 카드 보기")
        self.joker_btn.clicked.connect(self.show_joker_cards)

        self.deck_btn = QPushButton("🎯 나의 덱")
        self.deck_btn.clicked.connect(self.show_my_deck)

        self.back_btn = QPushButton("🔙 메인으로")
        self.back_btn.clicked.connect(self.go_back)

        self.upper_layout = QHBoxLayout()
        self.lower_layout = QHBoxLayout()
        self.generate_cards(self.upper_layout, self.upper_buttons, 4)

        top = QHBoxLayout()
        top.addLayout(info_layout)
        top.addStretch()
        top.addWidget(self.back_btn)

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addLayout(self.upper_layout)
        layout.addSpacing(20)
        layout.addLayout(self.lower_layout)
        layout.addWidget(self.confirm_btn)
        layout.addWidget(self.joker_btn)
        layout.addWidget(self.deck_btn)
        self.setLayout(layout)

        # 중앙 상단 라벨 및 버튼
        self.high_score_label = QLabel(f"📈 최고 기록 : {get_high_turn()}턴")
        self.high_score_label.setAlignment(Qt.AlignCenter)
        self.high_score_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.save_btn = QPushButton("💾 저장하기")
        self.save_btn.clicked.connect(self.save_current_record)

        center_layout = QVBoxLayout()
        center_layout.addWidget(self.high_score_label)
        center_layout.addWidget(self.save_btn)

        layout.insertLayout(1, center_layout)  # 기존 layout에 삽입

    def generate_cards(self, layout, buttons, count):
        suits = ['♥', '♠', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        for _ in range(count):
            suit = random.choice(suits)
            rank = random.choice(ranks)
            card_text = f"{suit} {rank}"
            color = "red" if suit in ['♥', '♦'] else "black"
            btn = QPushButton(card_text)
            btn.setFixedSize(100, 150)
            btn.setCheckable(True)
            btn.clicked.connect(self.update_selection)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 22px; font-weight: bold;
                    color: {color};
                    border: 3px solid #0000ff;
                    border-radius: 10px;
                    background-color: #f0f8ff;
                }}
                QPushButton:checked {{
                    border: 3px solid red;
                    background-color: #cceeff;
                }}
            """)
            layout.addWidget(btn)
            buttons.append(btn)

    def update_selection(self):
        if self.phase == 1:
            selected = [b for b in self.upper_buttons if b.isChecked()]
            self.confirm_btn.setEnabled(len(selected) > 0)

            max_select = 4
            for btn in self.upper_buttons:
                if not btn.isChecked():
                    btn.setCheckable(len(selected) < max_select)

        else:
            selected = self.selected_cards + [b for b in self.lower_buttons if b.isChecked()]
            self.confirm_btn.setEnabled(len(selected) == 5)

            remaining = 5 - len(self.selected_cards)
            for btn in self.lower_buttons:
                if not btn.isChecked():
                    btn.setCheckable(len([b for b in self.lower_buttons if b.isChecked()]) < remaining)

        # 버튼 활성화 조건
        self.confirm_btn.setEnabled(len(selected) > 0 if self.phase == 1 else len(selected) == 5)

    def animate_card_disappearance(self, buttons, callback):
        self.animations = []  # 애니메이션을 보관할 리스트

        for btn in buttons:
            effect = QGraphicsOpacityEffect()
            btn.setGraphicsEffect(effect)

            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(500)
            anim.setStartValue(1.0)
            anim.setEndValue(0.0)
            anim.start()

            self.animations.append(anim)  # 리스트에 저장

            QTimer.singleShot(600, lambda b=btn: b.hide())  # btn 바인딩 명시적 처리

        QTimer.singleShot(700, callback)


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
        if self.round > 3:
            if self.total_score >= self.target_score:
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

    def show_joker_cards(self):
        if self.selected_joker:  # 이미 선택한 조커가 있다면 다시 열지 않음
            QMessageBox.information(self, "조커 카드", f"이미 선택한 조커: {self.selected_joker}")
            return

        if self.used_joker_count >= 9:
            QMessageBox.warning(self, "조커 카드", "이번 턴의 조커 카드를 모두 사용했습니다.")
            return

        if not self.current_joker_group:
            start = self.used_joker_count
            self.current_joker_group = self.jokers_this_turn[start:start+3]

        dialog = JokerCardDialog(self, self.current_joker_group)
        if dialog.exec_() == QMessageBox.Accepted:
            self.selected_joker = dialog.selected_joker
            self.used_joker_count += 3
            self.current_joker_group = None
            self.update_selection()

    def show_my_deck(self):
        cards = list(self.selected_cards)
        if self.phase == 1:
            cards += [b for b in self.upper_buttons if b.isChecked()]
        elif self.phase == 2:
            cards += [b for b in self.lower_buttons if b.isChecked()]
        if not cards:
            QMessageBox.information(self, "나의 덱", "아직 선택된 카드가 없습니다.")
            return
        info = calculate_score(cards, self.selected_joker, self.previous_hand_type, self.friend_suit, self.broken_jokers, self.stored_multiplier)
        dialog = MyDeckDialog(cards, info, self.selected_joker, self)
        dialog.exec_()

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
                self.target_score += 50
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

    def reset_game(self):
        self.selected_cards.clear()
        self.upper_buttons.clear()
        self.lower_buttons.clear()
        self.confirm_btn.setEnabled(False)
        for layout in [self.upper_layout, self.lower_layout]:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        self.generate_cards(self.upper_layout, self.upper_buttons, 4)
        self.phase = 1

    def go_back(self):
        if QMessageBox.question(self, "메인 화면", "정말 돌아가시겠습니까?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.stacked_widget.setCurrentIndex(0)

    def save_current_record(self):
        save_record(self.turn, self.round, self.total_score, self.target_score)
        self.high_score_label.setText(f"📈 최고 기록 : {get_high_turn()}턴")
        QMessageBox.information(self, "저장 완료", "현재 기록이 저장되었습니다.")
