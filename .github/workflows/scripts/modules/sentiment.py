from datetime import date

def build(today: date) -> dict:
    return {
        "generated_at": today.isoformat(),
        "score": None,
        "tier": "数据不足（需先回填250日历史）",
        "tier_range": None,
        "dimensions": {"capital": None, "heat": None, "breadth": None, "derivative": None},
    }
