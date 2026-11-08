import akshare as ak
from datetime import date, timedelta

def build(today: date) -> dict:
    out = {}
    start = today - timedelta(days=7)
    end = today + timedelta(days=14)

    # 解禁
    try:
        df = ak.stock_restricted_release_detail_em(
            start_date=start.strftime("%Y%m%d"), end_date=end.strftime("%Y%m%d"))
        df["解禁日期"] = df["解禁日期"].astype(str).str[:10]
        for d, g in df.groupby("解禁日期"):
            out.setdefault(d, {})["unlock"] = [
                {"code": str(r["股票代码"]), "name": r["股票简称"],
                 "shares": round(float(r["解禁数量"]) / 1e8, 1),
                 "value": round(float(r["解禁市值"]) / 1e8, 1)}
                for _, r in g.iterrows()]
    except Exception:
        pass

    # 增减持
    try:
        df = ak.stock_hold_management_detail_em()
        date_col = "变动日期" if "变动日期" in df.columns else "公告日期"
        df[date_col] = df[date_col].astype(str).str[:10]
        df = df[(df[date_col] >= start.isoformat()) & (df[date_col] <= end.isoformat())]
        for d, g in df.groupby(date_col):
            out.setdefault(d, {})["change"] = [
                {"code": str(r["股票代码"]), "name": r["股票简称"],
                 "type": "增持" if float(r["变动股数"]) > 0 else "减持",
                 "shares": round(abs(float(r["变动股数"])) / 1e4, 1),
                 "value": round(abs(float(r["变动金额"])) / 1e8, 1)}
                for _, r in g.iterrows()]
    except Exception:
        pass

    # 保证每个工作日都有键
    cur = start
    while cur <= end:
        if cur.weekday() < 5:
            out.setdefault(cur.isoformat(), {})
        cur += timedelta(days=1)
    return out
