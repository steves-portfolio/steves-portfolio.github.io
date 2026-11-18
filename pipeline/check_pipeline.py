"""Pre-publish check for The Pipeline page. Run in an environment with Playwright:
    python3 check_pipeline.py <docs/index.html> [--max-nba-age-days 10]
Exit 0 = OK to publish, 1 = DO NOT publish. Prints one JSON line."""
import json, sys, pathlib, datetime
from playwright.sync_api import sync_playwright
target = sys.argv[1]; maxage = int(sys.argv[sys.argv.index("--max-nba-age-days") + 1]) if "--max-nba-age-days" in sys.argv else 10
url = target if target.startswith("http") else pathlib.Path(target).resolve().as_uri()
JS = r"""() => ({
  take: (document.querySelector('#take')||{}).innerText || '',
  boardRows: document.querySelectorAll('#board tbody tr').length,
  archBadges: document.querySelectorAll('#board .ab').length,
  rookieRows: document.querySelectorAll('#rtab tbody tr').length,
  classTabs: document.querySelectorAll('#ctabs .chip').length,
  c25: (typeof D !== 'undefined') ? (D.sophomores||[]).length : 0, c24: (typeof D !== 'undefined') ? (D.class2024||[]).length : 0,
  rookieCards: document.querySelectorAll('#rkcards .rc').length,
  svgs: document.querySelectorAll('svg').length,
  poy: document.querySelectorAll('#poy li').length, fy: document.querySelectorAll('#fy li').length,
  guardPaintAnchors: (typeof D !== 'undefined') ? D.board.filter(r => r.pos === 'G' && r.archetype === 'Paint Anchor').map(r => r.player) : ['D missing'],
  nbaThrough: (typeof D !== 'undefined') ? D.nba_through : null, updated: (typeof D !== 'undefined') ? D.updated : null,
  noTeam: (typeof D !== 'undefined') ? D.rookies.filter(r => !r.team && !r.note).map(r => r.name) : [],
  unexplained: (typeof D !== 'undefined') ? [...D.rookies, ...(D.sophomores||[]), ...(D.class2024||[])].filter(r => !r.gp && !r.note).map(r => r.name) : [],
  nan: /\bNaN\b|undefined/.test(document.body.innerText)
})"""
errors, problems = [], []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(url, wait_until="domcontentloaded", timeout=60000); pg.wait_for_timeout(2500)
    r = pg.evaluate(JS); b.close()
if errors: problems.append("JavaScript errors: " + " | ".join(errors[:3]))
if len(r["take"]) < 40: problems.append("take headline empty")
if r["boardRows"] < 40: problems.append(f"2027 board has only {r['boardRows']} rows")
if r["archBadges"] < 30: problems.append(f"only {r['archBadges']} archetype badges on the board")
if r["rookieRows"] < 40: problems.append(f"rookie table has only {r['rookieRows']} rows")
if r["classTabs"] != 3: problems.append(f"{r['classTabs']} NBA class tabs (need 3)")
if r["c25"] < 28 or r["c24"] < 28: problems.append(f"2025/2024 first-round tables short ({r['c25']}/{r['c24']} rows, need 28+)")
if r["rookieCards"] != 6: problems.append(f"{r['rookieCards']} rookie cards (need 6)")
if r["svgs"] < 8: problems.append(f"only {r['svgs']} charts rendered")
if r["poy"] < 5 or r["fy"] < 5: problems.append("award race lists empty")
if r["guardPaintAnchors"]: problems.append("guards labeled Paint Anchor: " + ", ".join(r["guardPaintAnchors"]))
if r["nan"]: problems.append("NaN or undefined printed on the page")
if r["unexplained"]: problems.append("players with 0 NBA games and no status note (add them to pipeline/work/nba_status_notes.txt): " + ", ".join(r["unexplained"]))
if r["noTeam"]: problems.append("rookies with no NBA team or status (refresh pipeline/work/nba_status.txt): " + ", ".join(r["noTeam"]))
if r["nbaThrough"]:
    age = (datetime.date.today() - datetime.date.fromisoformat(r["nbaThrough"])).days
    if age > maxage: problems.append(f"NBA data is {age} days old (through {r['nbaThrough']})")
else: problems.append("no NBA data date")
print(json.dumps({"ok": not problems, "problems": problems, **{k: r[k] for k in ["updated","nbaThrough","boardRows","rookieRows","svgs"]}}))
sys.exit(0 if not problems else 1)
