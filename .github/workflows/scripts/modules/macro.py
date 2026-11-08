import akshare as ak
from datetime import date

def _pick(df, value_col, period_col, label, unit=""):
    """取最新一行；period 是数据所属月份，不是采集日。"""
    try:
        row = df.iloc[0]
        return {"label": label, "value": round(float(row[value_col]), 1),
                "period": str(row[period_col])[:7], "unit": unit}
    except Exception:
        return {"label": label, "value": None, "period": None, "unit": unit}

def build(today: date) -> dict:
    out = {"generated_at": today.isoformat(), "china": {}, "usa": {}}

    # 中国
    try:
        df = ak.macro_china_cpi_yearly()
        out["china"]["cpi"] = _pick(df, "今值", "日期", "CPI 同比", "%")
    except Exception:
        out["china"]["cpi"] = _pick(None.__class__, "", "", "CPI 同比", "%") \
            if False else {"label":"CPI 同比","value":None,"period":None,"unit":"%"}

    try:
        df = ak.macro_china_ppi_yearly()
        out["china"]["ppi"] = _pick(df, "今值", "日期", "PPI 同比", "%")
    except Exception:
        out["china"]["ppi"] = {"label":"PPI 同比","value":None,"period":None,"unit":"%"}

    try:
        df = ak.macro_china_pmi()
        out["china"]["pmi"] = _pick(df, "制造业-指数", "月份", "制造业 PMI")
    except Exception:
        out["china"]["pmi"] = {"label":"制造业 PMI","value":None,"period":None,"unit":""}

    try:
        df = ak.macro_china_money_supply()
        out["china"]["m1"] = _pick(df, "货币(M1)-同比增长", "月份", "M1 同比", "%")
        out["china"]["m2"] = _pick(df, "货币和准货币(M2)-同比增长", "月份", "M2 同比", "%")
    except Exception:
        out["china"]["m1"] = {"label":"M1 同比","value":None,"period":None,"unit":"%"}
        out["china"]["m2"] = {"label":"M2 同比","value":None,"period":None,"unit":"%"}

    try:
        df = ak.macro_china_urban_unemployment()
        out["china"]["job"] = _pick(df, "今值", "日期", "城镇调查失业率", "%")
    except Exception:
        out["china"]["job"] = {"label":"城镇调查失业率","value":None,"period":None,"unit":"%"}

    # 美国
    try:
        df = ak.macro_usa_cpi_monthly()
        out["usa"]["cpi"] = _pick(df, "今值", "日期", "CPI 同比", "%")
    except Exception:
        out["usa"]["cpi"] = {"label":"CPI 同比","value":None,"period":None,"unit":"%"}

    try:
        df = ak.macro_usa_core_cpi_monthly()
        out["usa"]["core"] = _pick(df, "今值", "日期", "核心 CPI 同比", "%")
    except Exception:
        out["usa"]["core"] = {"label":"核心 CPI 同比","value":None,"period":None,"unit":"%"}

    try:
        df = ak.macro_usa_ppi_monthly()
        out["usa"]["ppi"] = _pick(df, "今值", "日期", "PPI 同比", "%")
    except Exception:
        out["usa"]["ppi"] = {"label":"PPI 同比","value":None,"period":None,"unit":"%"}

    try:
        df = ak.macro_usa_ism_pmi()
        out["usa"]["pmi"] = _pick(df, "今值", "日期", "ISM 制造业 PMI")
    except Exception:
        out["usa"]["pmi"] = {"label":"ISM 制造业 PMI","value":None,"period":None,"unit":""}

    try:
        df = ak.macro_usa_unemployment_rate()
        out["usa"]["job"] = _pick(df, "今值", "日期", "失业率", "%")
    except Exception:
        out["usa"]["job"] = {"label":"失业率","value":None,"period":None,"unit":"%"}

    return out
