import json, os, datetime, traceback
from zoneinfo import ZoneInfo
from modules import macro, repo, cffex, unlock_change, trend, sentiment

BJ = ZoneInfo("Asia/Shanghai")
TODAY = datetime.datetime.now(BJ).date()
OUT = "data/processed"
os.makedirs(OUT, exist_ok=True)

errors, results = {}, {}

def run(name, fn):
    try:
        results[name] = fn(TODAY)
    except Exception as e:
        errors[name] = f"{type(e).__name__}: {e}"
        traceback.print_exc()
        results[name] = None

run("macro",         macro.build)
run("repo",          repo.build)
run("cffex",         cffex.build)
run("unlock_change", unlock_change.build)
run("trend",         trend.build)
run("sentiment",     sentiment.build)

calendar = {"generated_at": datetime.datetime.now(BJ).isoformat(), "days": {}}
for key in ("repo", "cffex", "unlock_change"):
    if results.get(key):
        for d, payload in results[key].items():
            calendar["days"].setdefault(d, {}).update(payload)

for name, obj in [("macro", results.get("macro")), ("calendar", calendar),
                  ("trend", results.get("trend")), ("sentiment", results.get("sentiment"))]:
    if obj is not None:
        with open(f"{OUT}/{name}.json", "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)

with open(f"{OUT}/_errors.json", "w", encoding="utf-8") as f:
    json.dump(errors, f, ensure_ascii=False, indent=2)
print("done. errors:", errors)
