"""Pipeline backbone dataset: every NBA draft pick 2015-2026 (ESPN), his last college season, and his first 3 NBA seasons."""
import sys, numpy as np, pandas as pd
D = sys.argv[1]; OUT = sys.argv[2]
dr = pd.read_csv(f"{D}/espn_nba_drafts_2015_2026.txt", sep="|", dtype=str)
dob = open(f"{D}/dob.raw").read().strip().split(","); assert len(dob) == len(dr); dr["dob"] = pd.to_datetime(pd.Series(dob).replace("", None), format="%Y%m%d", errors="coerce")
for c in ["year","overall","round"]: dr[c] = dr[c].astype(int)
dr["college"] = dr.ath_league.eq("mens-college-basketball") | dr.team_league.eq("mens-college-basketball")
dr["age_draft"] = (pd.to_datetime(dr.year.astype(str) + "-06-25") - dr.dob).dt.days / 365.25
dr["height_in"] = pd.to_numeric(dr.height_in, errors="coerce")
ST = ["minutes","points","field_goals_made","field_goals_attempted","three_point_field_goals_made","three_point_field_goals_attempted","free_throws_made","free_throws_attempted","offensive_rebounds","defensive_rebounds","assists","steals","blocks","turnovers","fouls"]
def col_season(y):
    b = pd.read_parquet(f"{D}/mbb_pb_{y}.parquet")
    b = b[b.season_type.isin([2, 3])].copy()
    for c in ST: b[c] = pd.to_numeric(b[c], errors="coerce").fillna(0)
    b = b[b.minutes > 0]
    g = b.groupby("athlete_id").agg(games=("game_id","nunique"), team_id=("team_id","last"), team=("team_location","last"), **{c: (c, "sum") for c in ST})
    tm = b.drop_duplicates(["game_id","team_id"]).assign(m=lambda d: pd.to_numeric(d.team_score) - pd.to_numeric(d.opponent_team_score)).groupby("team_id").m.mean()
    g["team_margin"] = g.team_id.map(tm); g.index = [str(int(float(i))) for i in g.index]; return g
cache = {}
def cs(y):
    if y not in cache: cache[y] = col_season(y)
    return cache[y]
rows = []
for r in dr[dr.college].itertuples():
    aid = str(r.athlete_id); y = r.year
    cur = cs(y).loc[aid] if aid in cs(y).index else None
    prev = cs(y - 1).loc[aid] if (y - 1 >= 2014 and aid in cs(y - 1).index) else None
    seasons = sum(aid in cs(k).index for k in range(max(2014, y - 4), y + 1))
    base = cur if cur is not None else prev; blend = 0.0
    if base is None: rows.append({"athlete_id": aid, "col_found": False}); continue
    s = base[ST].astype(float).copy(); games = base.games; tmarg = base.team_margin; team = base.team
    if cur is not None and cur.minutes < 450 and prev is not None:   # short/injured final season: blend in prior season (same rule as draft model v2)
        w = (450 - cur.minutes) / 450; s = cur[ST].astype(float) + w * prev[ST].astype(float); blend = w; games = cur.games + w * prev.games
    rows.append({"athlete_id": aid, "col_found": True, "col_team": team, "col_games": games, "col_seasons": seasons, "blend": blend, "team_margin": tmarg, **{"c_" + k: v for k, v in s.items()}})
C = pd.DataFrame(rows)
df = dr.merge(C, on="athlete_id", how="left")
# NBA outcomes: regular season only, seasons Y+1..Y+3 (ESPN season label = year the season ends)
nb = []
for y in range(2016, 2028):
    b = pd.read_parquet(f"{D}/nba_pb_{y}.parquet"); b = b[b.season_type == 2].copy()
    for c in ["minutes","points","field_goals_made","field_goals_attempted","free_throws_made","free_throws_attempted","offensive_rebounds","defensive_rebounds","assists","steals","blocks","turnovers","fouls"]: b[c] = pd.to_numeric(b[c], errors="coerce").fillna(0)
    b = b[b.minutes > 0]
    b["gmsc"] = b.points + 0.4*b.field_goals_made - 0.7*b.field_goals_attempted - 0.4*(b.free_throws_attempted - b.free_throws_made) + 0.7*b.offensive_rebounds + 0.3*b.defensive_rebounds + b.steals + 0.7*b.assists + 0.7*b.blocks - 0.4*b.fouls - b.turnovers
    b["st"] = b.starter.fillna(False).astype(bool)
    g = b.groupby("athlete_id").agg(gp=("game_id","nunique"), mins=("minutes","sum"), starts=("st","sum"), gmsc=("gmsc","sum")).reset_index(); g["season"] = y; g["athlete_id"] = [str(int(float(i))) for i in g.athlete_id]; nb.append(g)
NB = pd.concat(nb)
last_season = int(NB.season.max())
for k in (1, 2, 3):
    m = NB.rename(columns={c: f"n{k}_{c}" for c in ["gp","mins","starts","gmsc"]})
    df = df.merge(m.drop(columns="season").assign(year=m.season - k), on=["athlete_id","year"], how="left")
for k in (1, 2, 3):
    for c in ["gp","mins","starts","gmsc"]: df[f"n{k}_{c}"] = df[f"n{k}_{c}"].fillna(0)
    df[f"n{k}_complete"] = (df.year + k) < last_season   # season fully in the data (current season 2027 is in progress)
def role(gp, mins, starts):
    if gp < 10: return "Out / G League"
    if gp >= 30 and starts >= gp / 2: return "Starter"
    if mins / gp >= 15: return "Rotation"
    return "Bench"
for k in (1, 2, 3): df[f"role{k}"] = [role(a, b, c) for a, b, c in zip(df[f"n{k}_gp"], df[f"n{k}_mins"], df[f"n{k}_starts"])]
df["gmsc3"] = df.n1_gmsc + df.n2_gmsc + df.n3_gmsc
df["mins3"] = df.n1_mins + df.n2_mins + df.n3_mins
df.to_parquet(f"{OUT}/pipeline_backbone.parquet")
print("picks", len(df), "college", int(df.college.sum()), "college found in box", int(df.col_found.fillna(False).sum()), "| dob", int(df.dob.notna().sum()), "| last NBA season", last_season)
print(df[df.college & ~df.col_found.fillna(False).astype(bool)][["year","overall","name","team_id"]].head(15).to_string())
print(df.groupby("year").agg(picks=("overall","size"), college=("college","sum"), found=("col_found", lambda s: s.fillna(False).astype(bool).sum()), yr3_complete=("n3_complete","sum")).to_string())
