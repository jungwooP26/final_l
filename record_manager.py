import json
import os

RECORD_FILE = "records.json"

def load_records():
    """기록 파일을 불러옵니다. 없으면 초기값 생성."""
    if not os.path.exists(RECORD_FILE):
        return {
            "high_turn": 0,
            "history": []
        }
    with open(RECORD_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_record(turn, round_, total_score, target_score):
    """새 기록을 추가하고 최고 턴을 갱신합니다."""
    records = load_records()

    new_record = {
        "turn": turn,
        "round": round_,
        "total_score": total_score,
        "target_score": target_score
    }

    records["history"].append(new_record)

    if turn > records.get("high_turn", 0):
        records["high_turn"] = turn

    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def get_high_turn():
    """현재 최고 기록(턴 수)을 반환합니다."""
    records = load_records()
    return records.get("high_turn", 0)

def get_all_history():
    """전체 플레이 기록 리스트를 반환합니다."""
    records = load_records()
    return records.get("history", [])
