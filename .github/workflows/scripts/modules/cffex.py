import akshare as ak
from datetime import date, timedelta

PRODUCTS = {"IH": "上证50", "IF": "沪深300", "IC": "中证500", "IM": "中证1000"}

def _prev_trading(today: date) -> date:
    d = today - timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d

def build(today: date) -> dict:
    prev = _prev_trading(today)
    try:
        df = ak.get_cffex_rank_table(date=prev.strftime("%Y%m%d"))
    except Exception:
        return {}

    # 标准化列名
    rename = {"品种": "variety", "合约": "contract", "会员简称": "member",
              "持买单量": "long_hold", "持卖单量": "short_hold", "持仓量": "open_interest"}
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    if not {"variety", "contract", "member", "long_hold", "short_hold"}.issubset(df.columns):
        return {}

    for c in ("long_hold", "short_hold"):
        df[c] = df[c].astype(float)

    citic, sent, top5 = {}, {}, {}
    for prod in PRODUCTS:
        sub = df[df["variety"] == prod]
        if sub.empty:
            continue
        # 主力合约：持仓量最大
        if "open_interest" in sub.columns:
            main = sub.loc[sub["open_interest"].astype(float).idxmax(), "contract"]
        else:
            main = sub["contract"].mode().iloc[0]
        m = sub[sub["contract"] == main].copy()
        m["net"] = m["long_hold"] - m["short_hold"]

        # 口径 A：前 5 个多头席位各自净持仓求和
        top5[prod] = round(float(m.nlargest(5, "long_hold")["net"].sum()), 1)

        c = m[m["member"].astype(str).str.contains("中信", na=False)]
        citic[prod] = round(float(c["net"].sum()), 1) if not c.empty else None

        net_sum = float(m["net"].sum())
        tot_sum = float((m["long_hold"] + m["short_hold"]).sum())
        sent[prod] = round(net_sum / tot_sum * 100, 1) if tot_sum else None

    net_total = round(sum(v for v in top5.values() if v is not None), 1)
    return {prev.isoformat(): {
        "top5": {"net": net_total},
        "citic": citic,
        "sentiment": sent,
    }}
