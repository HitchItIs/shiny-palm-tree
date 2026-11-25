def exam_grade(percent: float) -> str:
    if percent >= 92:
        return "1 – sehr gut"
    if percent >= 81:
        return "2 – gut"
    if percent >= 67:
        return "3 – befriedigend"
    if percent >= 50:
        return "4 – ausreichend"
    if percent >= 30:
        return "5 – mangelhaft"
    return "6 – ungenügend"
