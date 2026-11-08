import akshare as ak
import json, os
from datetime import date, datetime, timedelta

HOLIDAYS_PATH = os.path.join(os.path.dirname(__file__), "..", "holidays_2026.json")

def _load_holidays():
    with open(HOLIDAYS_PATH, encoding="utf-8") as f:
        return set(json.load(f)["holidays"])

def _next_trading(d: date, holidays: set) -> date:
    while d.weekday() >= 5 or d.isoformat() in holidays:
        d += timedelta(days=1)
    return d

def build(today: date) -> dict:
    holidays = _load_holidays()
    df = ak.macro_china_gksccz()
    df["操作日期"] = df["操作日期"].astype(str).str[:10]
    df["到期日"] = df.apply(
        lambda r: _next_trading(
            datetime.strptime(r["操作日期"], "%Y-%m-%d").date() + timedelta(days=int(r["期限"])),
            holidays).isoformat(), axis=1)

    op_by_day, mat_by_day = {}, {}
    for _, r in df.iterrows():
        d, mat, amt = r["操作日期"], r["到期日"], float(r["交易量"])
        op_by_day[d] = op_by_day.get(d, 0) + amt
        if r["正/逆回购"] == "逆回购":
            mat_by_day[mat] = mat_by_day.get(mat, 0) + amt

    out = {}
    cur = today - timedelta(days=30)
    end = today + timedelta(days=14)
    while cur <= end:
        if cur.weekday() < 5:
            key = cur.isoformat()
            future = cur > today
            out[key] = {"repo": {
                "operation": None if future else round(op_by_day.get(key, 0), 1),
                "maturity": round(mat_by_day.get(key, 0), 1),
                "detail": [] if future else [
                    f'{int(r["期限"])}天逆回购 {float(r["交易量"]):.1f}亿'
                    for _, r in df[df["操作日期"] == key].iterrows()],
            }}
        cur += timedelta(days=1)
    return out
