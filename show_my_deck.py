from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QScrollArea, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class MyDeckDialog(QDialog):
    def __init__(self, cards, score_info, joker_effect, parent=None):
        super().__init__(parent)
        self.setWindowTitle("나의 덱 보기")
        self.setFixedSize(650, 380)

        layout = QVBoxLayout()

        # 조커 설명 딕셔너리
        joker_descriptions = {
            "피보나치의 축복": "A,2,3,5,8 포함 카드마다 +13점",
            "왕국의 위엄": "K 카드 1장당 ×1.5 배수",
            "마지노선": "제한의 2/3 넘으면 자동 통과, 사용 후 폐기",
            "응축된 분노": "버릴 때마다 +0.5배 저장, 사용 시 리셋",
            "삼위일체": "트리플 또는 3카드 족보 시 ×3.33",
            "막장드라마": "Q 포함, K 제외 족보 시 ×2.5",
            "동그라미의 꿈": "6, 8, 9 포함 카드마다 +6.89점",
            "친구": "특정 무늬 1장당 +12점",
            "관성": "이전과 같은 족보라면 ×1.5",
            "무너진 마지노선": "(사용 완료된 조커)"
        }

        # --- 스크롤 가능한 점수 정보 영역 ---
        score_widget = QWidget()
        score_layout = QVBoxLayout(score_widget)

        effect_description = joker_descriptions.get(joker_effect, "없음")
        joker_line = f"- 조커 효과: {joker_effect} - {effect_description}" if joker_effect else "- 조커 효과: 없음"

        detail_text = f"""
현재 점수: {score_info['total_score']:.2f}

- 카드 가치 합: {score_info['value_sum']}
- 족보: {score_info['combo_name']} (기본 점수: {score_info['combo_score']})
- 무늬 배수: x{score_info['suit_multiplier']} ({score_info['top_suit']})
{joker_line}
"""
        score_label = QLabel(detail_text)
        score_label.setFont(QFont("Arial", 13))
        score_label.setAlignment(Qt.AlignLeft)
        score_label.setStyleSheet("padding: 10px;")
        score_layout.addWidget(score_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(score_widget)
        scroll_area.setFixedHeight(140)

        layout.addWidget(scroll_area)

        # --- 카드 표시 영역 ---
        card_layout = QHBoxLayout()
        for i in range(5):
            if i < len(cards):
                text = cards[i].text()
                suit = text.split()[0]
                color = "red" if suit in ['♥', '♦'] else "black"
            else:
                text = " "
                color = "black"

            card_label = QLabel(text)
            card_label.setFixedSize(100, 150)
            card_label.setAlignment(Qt.AlignCenter)
            card_label.setStyleSheet(f"""
                QLabel {{
                    border: 3px solid #0000ff;
                    border-radius: 10px;
                    background-color: #f0f8ff;
                    font-size: 20px;
                    font-weight: bold;
                    color: {color};
                }}
            """)
            card_layout.addWidget(card_label)

        layout.addLayout(card_layout)

        # --- 확인 버튼 ---
        ok_btn = QPushButton("확인")
        ok_btn.setFixedSize(100, 40)
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

