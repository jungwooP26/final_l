# main.py: 애플리케이션 실행 진입점. QMainWindow와 QStackedWidget을 초기화하고 전체 화면 전환을 관리함.

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from mode_select import ModeSelectWindow  # 모드 선택 화면 불러오기

# 이 블록 안의 코드는 '직접 실행'될 때만 실행됨
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QMainWindow()

    # 스택 위젯으로 여러 화면 관리
    stacked_widget = QStackedWidget()
    main_window.setCentralWidget(stacked_widget)

    # 첫 번째 화면: 모드 선택
    mode_ui = ModeSelectWindow(stacked_widget)
    stacked_widget.addWidget(mode_ui)
    stacked_widget.setCurrentWidget(mode_ui)

    # 메인 윈도우 설정
    main_window.setWindowTitle("Shuffle")
    main_window.resize(960, 640)
    main_window.show()

    # 이벤트 루프 시작
    sys.exit(app.exec_())