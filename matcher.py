import re

def _tokenise(text: str) -> set:
    stop = {'a', 'an', 'the', 'is', 'it', 'in', 'on', 'at', 'i', 'my', 'was', 'and', 'or', 'of'}
    words = re.findall(r'[a-z]+', text.lower())
    return {w for w in words if len(w) > 2 and w not in stop}


def score_pair(new_item: dict, db_row: tuple) -> int:
    score = 0

    new_words = _tokenise(new_item.get('title', '') + ' ' + new_item.get('description', ''))
    db_words  = _tokenise(str(db_row[1]) + ' ' + str(db_row[2]))

    if new_words and db_words:
        overlap = len(new_words & db_words)
        union   = len(new_words | db_words)
        jaccard = overlap / union if union else 0
        score  += int(jaccard * 40)          # max 40 pts

    if new_item.get('category', '').lower() == str(db_row[4]).lower():
        score += 30

    if new_item.get('location', '').lower() == str(db_row[5]).lower():
        score += 30

    return score


def find_matches(new_item: dict, db_rows: list, threshold: int = 30) -> list:
   
    results = []
    for row in db_rows:
        s = score_pair(new_item, row)
        if s >= threshold:
            results.append({'item': row, 'score': s})

    results.sort(key=lambda x: x['score'], reverse=True)
    return results
