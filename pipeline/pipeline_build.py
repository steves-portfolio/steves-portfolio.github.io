"""Builds pipeline.json for The Pipeline page (preview v1, Nov 12 2026)."""
import json, os, html, datetime, numpy as np, pandas as pd
DM = os.path.expanduser("~/dm"); WS = os.path.expanduser("~/mnt/Project Portfolio/website source"); R = f"{WS}/research/pipeline_backbone"
TODAY = datetime.date.today().isoformat()
AM = json.load(open(f"{R}/archetype_model.json")); NAMES = AM["names"]
BASE = json.load(open(f"{WS}/brainstorm_only/draft_model_baseline.json"))
ST = ["minutes","points","field_goals_made","field_goals_attempted","three_point_field_goals_made","three_point_field_goals_attempted","free_throws_made","free_throws_attempted","offensive_rebounds","defensive_rebounds","rebounds","assists","steals","blocks","turnovers","fouls"]
def load(y):
    b = pd.read_parquet(f"{DM}/mbb_pb_{y}.parquet"); b = b[b.season_type.isin([2,3])].copy()
    for c in ST: b[c] = pd.to_numeric(b[c], errors="coerce").fillna(0)
    b = b[b.minutes > 0]; b["aid"] = [str(int(float(i))) for i in b.athlete_id]; return b
cur_b, prev_b = load(2027), load(2026)
def agg(b):
    tm = b.drop_duplicates(["game_id","team_id"]).assign(m=lambda d: pd.to_numeric(d.team_score) - pd.to_numeric(d.opponent_team_score)).groupby("team_id").m.mean()
    g = b.groupby("aid").agg(name=("athlete_display_name","last"), team=("team_location","last"), team_id=("team_id","last"), games=("game_id","nunique"), **{c:(c,"sum") for c in ST})
    g["margin"] = g.team_id.map(tm); return g
cur, prev = agg(cur_b), agg(prev_b)
# ---------------- 2027 board ----------------
board = pd.read_csv(f"{WS}/pipeline/work/board_2027.csv")
AGE = {"Freshman": 19.2, "Sophomore": 20.2, "Junior": 21.2, "Senior": 22.2}
def v2score(s, margin, cls, h, pos):
    m = max(s["minutes"], 1); fga = s["field_goals_attempted"]
    st = dict(pts40=40*s["points"]/m, reb40=40*s["rebounds"]/m, ast40=40*s["assists"]/m, stocks40=40*(s["steals"]+s["blocks"])/m, tov40=40*s["turnovers"]/m,
              ts=s["points"]/(2*(fga+0.44*s["free_throws_attempted"])) if fga else 0, usg=(fga+0.44*s["free_throws_attempted"]+s["turnovers"])/m, margin=margin)
    blk40, tpa40 = 40*s["blocks"]/m, 40*s["three_point_field_goals_attempted"]/m
    hh = h if h == h else 79
    grp = "Big" if (pos == "C" or hh >= 84 or ((st["reb40"] >= 11 or blk40 >= 2.0) and tpa40 < 4.5)) else ("Guard" if pos == "G" and (hh <= 77 or st["ast40"] >= 4.5) else "Wing")
    t = sum(w * (st[k] - BASE["groups"][grp][k][0]) / BASE["groups"][grp][k][1] * (-1 if k == "tov40" else 1) for k, w in BASE["weights"].items())
    age = AGE.get(cls, 20.2); raw = (t + BASE["age_w"] * (-(age - BASE["age_mean"]) / BASE["age_sd"])) / (sum(BASE["weights"].values()) + BASE["age_w"])
    return grp, raw, 100 * np.searchsorted(BASE["raw_pool"], raw) / len(BASE["raw_pool"])
bio = {x.split(":")[0]: x.split(":") for x in open(f"{WS}/pipeline/work/bio27.txt").read().strip().split(",")}
rows = []
for r in board.itertuples():
    d = {k: (None if (isinstance(v, float) and v != v) else v) for k, v in r._asdict().items() if k != "Index"}
    aid = str(int(r.athlete_id)) if r.athlete_id == r.athlete_id else ""
    if aid and r.status == "college":
        c = cur.loc[aid] if aid in cur.index else None; p = prev.loc[aid] if aid in prev.index else None
        if c is not None and c.minutes >= 450: s, mg = c[ST], c.margin
        elif c is not None and p is not None: w = (450 - c.minutes)/450; s, mg = c[ST] + w*p[ST], c.margin
        elif c is not None: s, mg = c[ST], c.margin
        else: s, mg = p[ST], p.margin
        b = bio.get(aid, ["", "", "", "", ""]); h = float(b[1]) if b[1] else float("nan")
        grp, raw, pct = v2score(s, mg if mg == mg else 0, b[3], h, b[4])
        d.update(grp=grp, raw=round(float(raw), 3), model_pct=round(float(pct), 0), min_now=float(c.minutes) if c is not None else 0.0,
                 ts=round(float(s["points"]/(2*(s["field_goals_attempted"]+0.44*s["free_throws_attempted"]))), 3) if s["field_goals_attempted"] else None)
    rows.append(d)
B = pd.DataFrame(rows)
# ---- archetype v1.1: shrink small samples toward his position's typical drafted player (300-minute prior), and only allow
# archetypes his ESPN position has actually produced among 2015-2026 draftees (5%+ of that position). No guard has ever been a Paint Anchor.
BP = pd.read_parquet(f"{R}/data/backbone_players.parquet").merge(pd.read_csv(f"{R}/data/backbone_pos.csv", dtype=str), on="athlete_id")
BP["archetype"] = BP.arch.map(lambda i: NAMES[int(i)])
STY = AM["features"]; MU, SDV, CEN = np.array(AM["mean"]), np.array(AM["sd"]), np.array(AM["centers"])
FEATS = STY + ["ft_pct"]
PRIOR = {p_: BP[BP.pos == p_][FEATS].mean() for p_ in ["G","F","C"]}
ALLOW = {p_: [a for a, sh in (BP[BP.pos == p_].archetype.value_counts(normalize=True)).items() if sh >= 0.05] for p_ in ["G","F","C"]}
GLUE = ["orb40","drb40","ast40","stl40","blk40"]; K = 120
arch_rows = []
for i, r in B.iterrows():
    if r.get("archetype") is None or (isinstance(r.get("archetype"), float)): continue
    pos_ = (bio.get(str(int(board.loc[i, "athlete_id"])), ["","","","","F"])[4] or "F") if board.loc[i, "athlete_id"] == board.loc[i, "athlete_id"] else "F"
    pos_ = pos_ if pos_ in PRIOR else "F"
    mins = float(r["min_now"] or 0) if (r.get("basis") or "").startswith("this season only") else 450.0
    x = {f: (mins * float(r[f]) + K * PRIOR[pos_][f]) / (mins + K) for f in FEATS}
    if r.get("height_in") == r.get("height_in") and r.get("height_in") is not None: x["height_in"] = float(r["height_in"])
    z = (np.array([x[f] for f in STY]) - MU) / SDV; d_ = np.linalg.norm(CEN - z, axis=1)
    ok = [j for j in np.argsort(d_) if NAMES[j] in ALLOW[pos_]]
    a1, a2 = NAMES[ok[0]], NAMES[ok[1]]
    g = BP[BP.archetype == a1]
    glue = float(np.mean([(g[k] < x[k]).mean() for k in GLUE]) * 100)
    B.loc[i, ["archetype","second","fit","glue_pct","pos"]] = [a1, a2, round(float(1 - d_[ok[0]] / d_[ok[1]]), 2), round(glue), pos_]
    B.loc[i, "read"] = "lean" if mins < 150 else ("early" if mins < 450 else "solid")
sc = B[B.raw.notna()].sort_values("raw", ascending=False); B.loc[sc.index, "model_rank"] = range(1, len(sc) + 1)
B["cons_rank_scored"] = B.cons_rank.rank()  # rank within the board
B["gap"] = B.cons_rank - B.model_rank   # + = model likes him more than the experts
B["sample"] = np.where(B.games_now.fillna(0) >= 8, "solid", "early")
B.loc[B.read.isna() & B.archetype.notna(), "read"] = "early"
GOOD = {"Movement Shooter", "Connector", "Swiss Army Forward"}
B["flag"] = None
B.loc[(B.archetype == "Volume Shooter") & (B.cons_rank <= 20), "flag"] = "caution"
B.loc[B.archetype.isin(GOOD) & (B.glue_pct >= 60) & (B.cons_rank >= 8) & (B.gap >= 8), "flag"] = "sleeper"
# ---------------- sleeper / caution calls: dated receipts ----------------
CALLS = f"{WS}/data/pipeline_calls.csv"
calls = pd.read_csv(CALLS) if os.path.exists(CALLS) else pd.DataFrame(columns=["date","player","call","archetype","cons_rank_at_call","model_rank_at_call","reason"])
# Official calls are only logged once the read is stable (8+ games this season); before that, flags show as a watch list.
for r in B[B.flag.notna() & (B["sample"] == "solid")].itertuples():
    if ((calls.player == r.player) & (calls.call == r.flag)).any(): continue
    why = f"{r.archetype}, glue {int(r.glue_pct)}, model No. {int(r.model_rank)} vs. experts No. {int(r.cons_rank)}" if r.flag == "sleeper" else f"Volume Shooter ranked No. {int(r.cons_rank)} by the experts; the type has beaten its draft slot in only 2 of 9 classes"
    calls.loc[len(calls)] = [TODAY, r.player, r.flag, r.archetype, int(r.cons_rank), int(r.model_rank) if r.model_rank == r.model_rank else None, why]
calls.to_csv(CALLS, index=False)
# snapshot for the stock ticker
os.makedirs(f"{WS}/data/history/pipeline", exist_ok=True)
B[["player","cons_rank","model_rank","model_pct","glue_pct","archetype"]].to_csv(f"{WS}/data/history/pipeline/board_{TODAY}.csv", index=False)
hist = []
for f in sorted(os.listdir(f"{WS}/data/history/pipeline")):
    if f.startswith("board_"): h = pd.read_csv(f"{WS}/data/history/pipeline/{f}"); h["date"] = f[6:16]; hist.append(h)
H = pd.concat(hist)
# ---------------- award race: impact on a winner ----------------
cb = cur_b.copy()
cb["gmsc"] = cb.points + 0.4*cb.field_goals_made - 0.7*cb.field_goals_attempted - 0.4*(cb.free_throws_attempted - cb.free_throws_made) + 0.7*cb.offensive_rebounds + 0.3*cb.defensive_rebounds + cb.steals + 0.7*cb.assists + 0.7*cb.blocks - 0.4*cb.fouls - cb.turnovers
cb["won"] = cb.team_winner.astype(str).str.lower().isin(["true","1"])
pl = cb.groupby("aid").agg(name=("athlete_display_name","last"), team=("team_location","last"), team_id=("team_id","last"), gp=("game_id","nunique"), mins=("minutes","sum"), pts=("points","sum"), gs=("gmsc","sum"), reb=("rebounds","sum"), ast=("assists","sum"))
tm = cur_b.drop_duplicates(["game_id","team_id"]).assign(m=lambda d: pd.to_numeric(d.team_score) - pd.to_numeric(d.opponent_team_score), w=lambda d: d.team_winner.astype(str).str.lower().isin(["true","1"]))
tmm = tm.groupby("team_id").agg(margin=("m","mean"), w=("w","sum"), g=("game_id","nunique"))
pl = pl.join(tmm, on="team_id"); pl["mpg"] = pl.mins/pl.gp; pl["gs_g"] = pl.gs/pl.gp
el = pl[(pl.gp >= 2) & (pl.mpg >= 20)].copy()
z = lambda s: (s - s.mean())/s.std()
el["impact"] = z(el.gs_g) + 0.5*z(el.margin.clip(-30, 30))
el["first_year"] = ~el.index.isin(prev.index) & ~el.index.isin(load(2025).aid.unique())
def top(df, n=10): return [{"name": r.name, "team": r.team, "gp": int(r.gp), "ppg": round(r.pts/r.gp,1), "rpg": round(r.reb/r.gp,1), "apg": round(r.ast/r.gp,1), "gs_g": round(r.gs_g,1), "record": f"{int(r.w)}-{int(r.g - r.w)}", "margin": round(r.margin,1), "impact": round(r.impact,2)} for r in df.sort_values("impact", ascending=False).head(n).itertuples()]
awards = {"poy": top(el), "fy": top(el[el.first_year]), "players": int(len(el)), "median_games": float(pl.gp.median())}
# ---------------- NBA chapter ----------------
bp = pd.read_parquet(f"{R}/data/backbone_players.parquet"); bp["archetype"] = bp.arch.map(lambda i: NAMES[int(i)]); bp["name"] = bp.name.map(html.unescape).str.replace(r"\s+", " ", regex=True)
c26 = pd.read_csv(f"{R}/data/class2026_archetypes.csv")
# role in the latest complete season (2025-26) for the 2024 class (year 2) and 2025 class (year 1)
dr = pd.read_parquet(f"{R}/data/pipeline_backbone.parquet")
tr = []
for yr, k in [(2025, 1), (2024, 2), (2023, 3)]:
    d = dr[(dr.year == yr) & dr.college]
    for r in d.itertuples(): tr.append({"class": yr, "season_no": k, "round": int(r.round), "role": getattr(r, f"role{k}")})
TR = pd.DataFrame(tr)
flows = TR.groupby(["class","round","role"]).size().reset_index(name="n").to_dict("records")
nb = pd.read_parquet(f"{DM}/nba_pb_2027.parquet"); nb = nb[nb.season_type == 2].copy()
NS = ["minutes","points","field_goals_made","field_goals_attempted","three_point_field_goals_made","three_point_field_goals_attempted","free_throws_made","free_throws_attempted","offensive_rebounds","defensive_rebounds","rebounds","assists","steals","blocks","turnovers","fouls"]
for k_ in NS: nb[k_] = pd.to_numeric(nb[k_], errors="coerce").fillna(0)
nb = nb[nb.minutes > 0]; nb["aid"] = [str(int(float(i))) for i in nb.athlete_id]
nb["gmsc"] = nb.points + 0.4*nb.field_goals_made - 0.7*nb.field_goals_attempted - 0.4*(nb.free_throws_attempted-nb.free_throws_made) + 0.7*nb.offensive_rebounds + 0.3*nb.defensive_rebounds + nb.steals + 0.7*nb.assists + 0.7*nb.blocks - 0.4*nb.fouls - nb.turnovers
nb["st"] = nb.starter.fillna(False).astype(bool)
NA_ = nb.sort_values("game_date").groupby("aid").agg(team=("team_abbreviation","last"), gp=("game_id","nunique"), starts=("st","sum"), **{k_:(k_,"sum") for k_ in NS}, gs=("gmsc","sum"))
NBA_THROUGH = str(nb.game_date.max())[:10]
bpp = bp.copy()
def rook(year):
    out_ = []
    for r in bpp[bpp.year == year].itertuples():
        d_ = {"pick": int(r.overall), "name": r.name, "aid": r.athlete_id, "college": r.col_team, "archetype": r.archetype,
              "c_ppg": round(r.c_points / max(r.col_games, 1), 1), "c_reb40": round(40*(r.c_offensive_rebounds + r.c_defensive_rebounds)/max(r.c_minutes,1), 1),
              "c_ast40": round(40*r.c_assists/max(r.c_minutes,1), 1), "c_stk40": round(40*(r.c_steals + r.c_blocks)/max(r.c_minutes,1), 1)}
        if r.athlete_id in NA_.index:
            n_ = NA_.loc[r.athlete_id]; m_ = max(n_.minutes, 1)
            d_.update(team=n_.team, gp=int(n_.gp), starts=int(n_.starts), mpg=round(n_.minutes/n_.gp, 1), ppg=round(n_.points/n_.gp, 1), rpg=round(n_.rebounds/n_.gp, 1), apg=round(n_.assists/n_.gp, 1),
                      ts=round(n_.points/(2*(n_.field_goals_attempted + 0.44*n_.free_throws_attempted)), 3) if n_.field_goals_attempted else None, gs_g=round(n_.gs/n_.gp, 2),
                      n_reb36=round(36*n_.rebounds/m_, 1), n_ast36=round(36*n_.assists/m_, 1), n_stk36=round(36*(n_.steals + n_.blocks)/m_, 1))
        else: d_.update(gp=0)
        out_.append(d_)
    df_ = pd.DataFrame(out_); q_ = df_[df_.gp >= 3].copy()
    q_["prod_rank"] = q_.gs_g.rank(ascending=False, method="min"); q_["pick_rank"] = q_.pick.rank(method="min"); q_["vs_slot"] = (q_.pick_rank - q_.prod_rank).astype(int)
    df_ = df_.merge(q_[["aid","prod_rank","vs_slot"]], on="aid", how="left"); return json.loads(df_.to_json(orient="records"))
bp["archetype"] = bp.arch.map(lambda i: NAMES[int(i)]); bpp = bp
rookies26, soph25 = rook(2026), rook(2025)
out = {"updated": TODAY, "nba_through": NBA_THROUGH, "rookies": rookies26, "sophomores": soph25,
       "board": json.loads(B.assign(athlete_id=B.athlete_id.map(lambda v: str(int(float(v))) if v == v and v not in (None, "") else "")).to_json(orient="records")),
       "calls": json.loads(calls.to_json(orient="records")),
       "history": json.loads(H.to_json(orient="records")),
       "awards": awards,
       "class2026": json.loads(c26.to_json(orient="records")),
       "flows": flows,
       "persistence": [["Blocks", .83], ["Offensive rebounding", .82], ["Assists", .77], ["Defensive rebounding", .76], ["3-point attempt rate", .73], ["Steals", .66], ["Free-throw rate", .59], ["Turnovers", .43], ["Scoring", .32]],
       "archetypes": [{"name": "Movement Shooter", "over": .082, "lo": -.009, "hi": .170, "n": 99, "like": "Booker, Jamal Murray, Franz Wagner"},
                      {"name": "Swiss Army Forward", "over": .023, "lo": -.064, "hi": .109, "n": 102, "like": "Tatum, Banchero, Zion"},
                      {"name": "Connector", "over": .012, "lo": -.084, "hi": .103, "n": 84, "like": "Haliburton, Scottie Barnes, Jalen Williams"},
                      {"name": "Paint Anchor", "over": -.033, "lo": -.120, "hi": .052, "n": 80, "like": "Karl-Anthony Towns, Evan Mobley, Ayton"},
                      {"name": "Volume Shooter", "over": -.139, "lo": -.227, "hi": -.047, "n": 63, "like": "Trae Young, Anthony Edwards, Ja Morant"}],
       "study": {"picks": 713, "college": 583, "matched": 570, "three_seasons": 428, "classes": "2015-2023"}}
json.dump(out, open(f"{WS}/data/pipeline.json", "w"))
pd.set_option("display.width", 230)
print(B[["cons_rank","player","archetype","glue_pct","model_rank","gap","flag","sample"]].head(60).to_string(index=False))
print(calls.to_string(index=False)); print("POY", [(a["name"], a["team"], a["ppg"], a["record"]) for a in awards["poy"][:5]]); print("FY", [(a["name"], a["team"], a["ppg"]) for a in awards["fy"][:5]])
print(pd.DataFrame(flows).pivot_table(index=["class","round"], columns="role", values="n", fill_value=0))
