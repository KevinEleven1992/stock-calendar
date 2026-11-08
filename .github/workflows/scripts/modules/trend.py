import akshare as ak
from datetime import date, timedelta

ETFS = {
    "etf_510300": ("510300", "华泰柏瑞300ETF"),
    "etf_510330": ("510330", "华夏300ETF"),
    "etf_510310": ("510310", "易方达300ETF"),
    "etf_510050": ("510050", "华夏50ETF"),
}

def _mk(name, unit, color, symbol, data):
    return {"name": name, "unit": unit, "color": color, "symbol": symbol, "data": data}

def build(today: date) -> dict:
    start = today - timedelta(days=45)
    end = today
    out = {"generated_at": today.isoformat(), "dates": [], "series": {}}

    # 上证指数
    sse = ak.stock_zh_index_daily(symbol="sh000001")
    sse["date"] = sse["date"].astype(str).str[:10]
    sse = sse[(sse["date"] >= start.isoformat()) & (sse["date"] <= end.isoformat())]
    out["dates"] = sse["date"].tolist()
    out["series"]["sse_index"] = _mk("上证指数", "点", "#9aa0a6", "none",
                                     sse["close"].round(1).tolist())

    # 两市成交额
    try:
        szse = ak.stock_zh_index_daily(symbol="sz399001")
        szse["date"] = szse["date"].astype(str).str[:10]
        szse = szse[(szse["date"] >= start.isoformat()) & (szse["date"] <= end.isoformat())]
        merged = sse[["date", "amount"]].merge(
            szse[["date", "amount"]], on="date", suffixes=("_sh", "_sz"))
        turnover = (merged["amount_sh"].astype(float) + merged["amount_sz"].astype(float)) / 1e8
        out["series"]["turnover"] = _mk("两市成交额", "亿元", "#8b5cf6", "triangle",
                                        turnover.round(1).tolist())
    except Exception:
        pass

    # 两融余额：沪市单位是元，必须 /1e8
    try:
        m_sh = ak.stock_margin_sse()
        m_sz = ak.stock_margin_szse()
        m_sh["信用交易日期"] = m_sh["信用交易日期"].astype(str).str[:10]
        m_sz["信用交易日期"] = m_sz["信用交易日期"].astype(str).str[:10]
        ms = m_sh[["信用交易日期", "融资融券余额"]].merge(
            m_sz[["信用交易日期", "融资融券余额"]], on="信用交易日期", suffixes=("_sh", "_sz"))
        ms["total"] = ms["融资融券余额_sh"].astype(float) / 1e8 + ms["融资融券余额_sz"].astype(float)
        ms = ms[ms["信用交易日期"].isin(out["dates"])].sort_values("信用交易日期")
        out["series"]["margin"] = _mk("两融余额", "亿元", "#f59e0b", "circle",
                                      ms["total"].round(1).tolist())
    except Exception:
        pass

    # ETF：口径 A（份额变动 × 成交均价），分别计算不加总
    for key, (code, name) in ETFS.items():
        try:
            hist = ak.fund_etf_hist_em(symbol=code, period="daily", adjust="")
            hist["日期"] = hist["日期"].astype(str).str[:10]
            hist = hist[(hist["日期"] >= start.isoformat()) & (hist["日期"] <= end.isoformat())]
            hist = hist.sort_values("日期")
            avg = hist["成交额"].astype(float) / hist["成交量"].astype(float)
            out["series"][key + "_amount"] = _mk(
                f"{name} 总成交额", "亿元", "#93c5fd", "rect",
                (hist["成交额"].astype(float) / 1e8).round(1).tolist())
            if "份额" in hist.columns:
                delta = hist["份额"].astype(float).diff().fillna(0)
                out["series"][key] = _mk(f"{name} 净申购", "亿元", "#2563eb", "circle",
                                         (delta * avg).round(1).tolist())
        except Exception:
            pass

    # 金 / 油 08:15 快照
    try:
        gold = ak.futures_foreign_commodity_realtime(subscribe_list="黄金")
        out["series"]["gold_9am"] = _mk("纽约金 08:15", "美元/盎司", "#d4a017", "diamond",
                                        [round(float(gold.iloc[0]["最新价"]), 1)])
    except Exception:
        pass
    try:
        oil = ak.futures_foreign_commodity_realtime(subscribe_list="布伦特原油")
        out["series"]["brent_9am"] = _mk("布伦特原油 08:15", "美元/桶", "#0f766e", "rect",
                                         [round(float(oil.iloc[0]["最新价"]), 1)])
    except Exception:
        pass

    # 中美 5 年期国债收益率（日频收盘值，不是 9:00 盘中值）
    try:
        rate = ak.bond_zh_us_rate()
        rate["日期"] = rate["日期"].astype(str).str[:10]
        rate = rate[rate["日期"].isin(out["dates"])].sort_values("日期")
        out["series"]["cn_5y"] = _mk("中国5年期国债收益率（收盘）", "%", "#dc2626", "circle",
                                     rate["中国国债收益率5年"].round(1).tolist())
        out["series"]["us_5y"] = _mk("美国5年期国债收益率（收盘）", "%", "#2563eb", "triangle",
                                     rate["美国国债收益率5年"].round(1).tolist())
    except Exception:
        pass

    return out
