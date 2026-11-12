"""Step 1 of the weekly Pipeline refresh: consensus board -> ESPN ids -> early-season stats + archetype basis.
Usage: python3 pipeline/board_refresh.py <ubb_nba_2027_*.txt from Downloads>
Reads ~/dm/mbb_pb_2025/2026/2027.parquet. Writes pipeline/work/board_2027.csv.
Prints any prospect with no ESPN height/class in pipeline/work/bio27.txt (fetch those in Chrome, see WEEKLY_UPDATE.md)."""
import re, os, sys, unicodedata, pathlib, numpy as np, pandas as pd
W = pathlib.Path(__file__).resolve().parent / "work"; DM = os.path.expanduser("~/dm")
def norm(s): s = unicodedata.normalize("NFKD", str(s)).encode("ascii","ignore").decode().lower(); s = re.sub(r"\b(jr|sr|ii|iii|iv)\b\.?", "", s); return re.sub(r"[^a-z]", "", s)
# hand-checked fixes (Nov 2026): same-name players at other schools, and the board's own duplicate entries
ID_FIX = {"cameron-williams": "5210407", "matthew-able": "5196877"}
NAME_KEY_FIX = {"matthew-able": "mattable"}
u = pd.read_csv(sys.argv[1], sep="|", dtype=str)
# Ultimate Big Board sometimes lists one player twice (name spelled two ways); the extra copy has a single source and "NO TEAM SUPPLIED". Keep the real one.
u["single"] = u.text.str.contains("NO TEAM SUPPLIED", na=False)
u = u[~(u.single & u.duplicated(subset=None, keep=False) | (u.single & u.slug.isin(["pat-ngongba", "hugo-yigma-moukouri"])))].copy()
pool = []
for y in (2027, 2026, 2025):
    b = pd.read_parquet(f"{DM}/mbb_pb_{y}.parquet", columns=["athlete_id","athlete_display_name","team_location","minutes"]).dropna(subset=["athlete_id"])
    b["minutes"] = pd.to_numeric(b.minutes, errors="coerce").fillna(0); b["aid"] = [str(int(float(i))) for i in b.athlete_id]
    g = b.groupby(["aid","athlete_display_name"]).agg(team=("team_location","last"), mins=("minutes","sum")).reset_index(); g["season"] = y; pool.append(g)
P = pd.concat(pool); P["key"] = P.athlete_display_name.map(norm)
rows = []
for i, r in enumerate(u.itertuples(), 1):
    key = NAME_KEY_FIX.get(r.slug, r.slug.replace("-", "")); key = norm(key)
    m = P[P.key == key].sort_values(["season","mins"], ascending=False)
    aid = ID_FIX.get(r.slug, m.aid.iloc[0] if len(m) else "")
    team = P[P.aid == aid].sort_values("season").team.iloc[-1] if aid and (P.aid == aid).any() else ""
    rows.append({"cons_rank": i, "slug": r.slug, "avg": r.avg_pick, "athlete_id": aid, "team": team, "ambiguous": m.aid.nunique() > 1 and r.slug not in ID_FIX})
B = pd.DataFrame(rows)
bio = {x.split(":")[0]: x.split(":") for x in (W / "bio27.txt").read_text().strip().split(",")}
need = B[(B.athlete_id != "") & ~B.athlete_id.isin(bio)]
if len(need): print("NEED BIO (ESPN height/class/position) for:", ",".join(need.athlete_id))
amb = B[B.ambiguous]
if len(amb): print("CHECK same-name matches:", amb[["slug","athlete_id","team"]].values.tolist())
ST = ["minutes","points","field_goals_made","field_goals_attempted","three_point_field_goals_made","three_point_field_goals_attempted","free_throws_made","free_throws_attempted","offensive_rebounds","defensive_rebounds","assists","steals","blocks","turnovers","fouls"]
def season(y):
    b = pd.read_parquet(f"{DM}/mbb_pb_{y}.parquet"); b = b[b.season_type.isin([2,3])].dropna(subset=["athlete_id"]).copy()
    for c in ST: b[c] = pd.to_numeric(b[c], errors="coerce").fillna(0)
    b = b[b.minutes > 0]; g = b.groupby("athlete_id").agg(games=("game_id","nunique"), **{c:(c,"sum") for c in ST}); g.index = [str(int(float(i))) for i in g.index]; return g
cur, prev = season(2027), season(2026)
out = []
for r in B.itertuples():
    d = {"cons_rank": r.cons_rank, "player": r.slug.replace("-", " ").title(), "avg_pick": float(r.avg), "team": r.team, "athlete_id": r.athlete_id}
    if not r.athlete_id: d["status"] = "International (no college data)"; out.append(d); continue
    b = bio.get(r.athlete_id, [r.athlete_id, "", "", "", ""]); h = float(b[1]) if b[1] else np.nan; d.update(cls=b[3], height_in=h)
    c = cur.loc[r.athlete_id] if r.athlete_id in cur.index else None; p = prev.loc[r.athlete_id] if r.athlete_id in prev.index else None
    if c is None and p is None: d["status"] = "No games yet"; out.append(d); continue
    if c is not None and c.minutes >= 450: s, note = c[ST], "this season"
    elif c is not None and p is not None: w = (450 - c.minutes)/450; s, note = c[ST] + w*p[ST], f"this season + {round(100*w)}% of last season"
    elif c is not None: s, note = c[ST], "this season only (freshman, small sample)"
    else: s, note = p[ST], "last season only"
    m_ = max(s["minutes"], 1); fga = max(s["field_goals_attempted"], 1)
    d.update(games_now=int(c.games) if c is not None else 0, min_now=float(c.minutes) if c is not None else 0.0, basis=note,
             pts40=40*s["points"]/m_, orb40=40*s["offensive_rebounds"]/m_, drb40=40*s["defensive_rebounds"]/m_, ast40=40*s["assists"]/m_, tov40=40*s["turnovers"]/m_,
             stl40=40*s["steals"]/m_, blk40=40*s["blocks"]/m_, tpa_rate=s["three_point_field_goals_attempted"]/fga, ftr=s["free_throws_attempted"]/fga,
             ft_pct=(s["free_throws_made"] + 0.72*20)/(s["free_throws_attempted"] + 20), ppg_now=round(float(c.points/c.games), 1) if c is not None else None,
             archetype="pending", status="college")
    out.append(d)
O = pd.DataFrame(out); O.to_csv(W / "board_2027.csv", index=False)
print("board rows", len(O), "| college with stats", int((O.status == "college").sum()), "| international", int(O.status.str.startswith("International", na=False).sum()))
