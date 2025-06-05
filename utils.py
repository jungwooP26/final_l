from collections import Counter

# 카드 숫자별 점수 정의
def get_card_value(rank: str) -> int:
    rank_value = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
        '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 15, 'Q': 20, 'K': 25, 'A': 30
    }
    return rank_value.get(rank, 0)

def extract_suit_and_rank(card_text: str):
    suit, rank = card_text.split()
    return suit, rank

def detect_hand(ranks, suits):
    if len(ranks) < 5:
        return "노페어"  # 카드 수 부족 시 기본 족보로 처리
        
    rank_order = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    rank_indices = [rank_order.index(r) for r in ranks]
    rank_indices.sort()
    rank_count = Counter(ranks)
    suit_count = Counter(suits)
    is_flush = len(suit_count) == 1
    is_straight = all(rank_indices[i]+1 == rank_indices[i+1] for i in range(4))
    is_back_straight = sorted(ranks) == ['2','3','4','5','A']
    is_mountain = sorted(ranks) == ['10','J','K','Q','A']
    if is_flush and is_mountain:
        return "로열스트레이트플러쉬"
    elif is_flush and is_back_straight:
        return "백스트레이트플러쉬"
    elif is_flush and is_straight:
        return "스트레이트플러쉬"
    elif 4 in rank_count.values():
        return "포카드"
    elif sorted(rank_count.values()) == [2, 3]:
        return "풀하우스"
    elif is_flush:
        return "플러쉬"
    elif is_mountain:
        return "마운틴"
    elif is_back_straight:
        return "백스트레이트"
    elif is_straight:
        return "스트레이트"
    elif 3 in rank_count.values():
        return "트리플"
    elif list(rank_count.values()).count(2) == 2:
        return "투페어"
    elif 2 in rank_count.values():
        return "원페어"
    else:
        return "노페어"

def calculate_score(cards, joker=None, prev_hand=None, friend_suit=None, broken_jokers=None, stored_multiplier=0.0):
    suits, ranks = [], []
    for c in cards:
        text = c.text() if hasattr(c, 'text') else c
        suit, rank = extract_suit_and_rank(text)
        suits.append(suit)
        ranks.append(rank)

    values = [get_card_value(r) for r in ranks]
    card_sum = sum(values)
    hand_type = detect_hand(ranks, suits)

    base_score = {
        "로열스트레이트플러쉬": 300, "백스트레이트플러쉬": 280, "스트레이트플러쉬": 250,
        "포카드": 200, "풀하우스": 180, "플러쉬": 150, "마운틴": 130,
        "백스트레이트": 120, "스트레이트": 100, "트리플": 90,
        "투페어": 60, "원페어": 40, "노페어": 0
    }.get(hand_type, 0)

    bonus = 0.0
    multiplier = 1.0
    auto_pass = False
    joker_name = joker or ""

    if joker_name == "피보나치의 축복":
        bonus += sum(13 for r in ranks if r in ['A', '2', '3', '5', '8'])
    elif joker_name == "왕국의 위엄":
        multiplier *= 1.5 ** ranks.count('K')
    elif joker_name == "마지노선":
        if broken_jokers is not None and "마지노선" not in broken_jokers:
            if (base_score + card_sum) >= (2/3) * 100:
                broken_jokers.add("마지노선")
                return {
                    "total_score": 0,
                    "hand_type": hand_type,
                    "base_score": 0,
                    "card_sum": 0,
                    "bonus": 0,
                    "multiplier": 0,
                    "auto_pass": True,
                    "value_sum": 0,
                    "combo_name": hand_type,
                    "combo_score": 0,
                    "suit_multiplier": 0,
                    "top_suit": ''
                }
    elif joker_name == "응축된 분노":
        multiplier *= (1 + stored_multiplier)
    elif joker_name == "삼위일체":
        if hand_type == "트리플" or len(set(ranks)) == 3:
            multiplier *= 3.33
    elif joker_name == "막장드라마":
        if 'Q' in ranks and 'K' not in ranks:
            multiplier *= 2.5
    elif joker_name == "동그라미의 꿈":
        bonus += sum(6.89 for r in ranks if r in ['6', '8', '9'])
    elif joker_name == "친구" and friend_suit:
        bonus += suits.count(friend_suit) * 12
    elif joker_name == "관성":
        if prev_hand and prev_hand == hand_type:
            multiplier *= 1.5

    total = (base_score + card_sum + bonus) * multiplier
    max_suit = max(set(suits), key=suits.count)

    return {
        "total_score": total,
        "hand_type": hand_type,
        "base_score": base_score,
        "card_sum": card_sum,
        "bonus": bonus,
        "multiplier": multiplier,
        "auto_pass": auto_pass,
        "value_sum": card_sum,
        "combo_name": hand_type,
        "combo_score": base_score,
        "suit_multiplier": multiplier,
        "top_suit": max_suit
    }
