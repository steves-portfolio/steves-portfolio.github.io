"""Display line for each drafted player's LAST college season (2024-2026 classes), straight from ESPN box scores, no blending.
The archetype model still uses the blended line (short final season + prior season); this file is only what the page shows.
Writes research/pipeline_backbone/data/college_final_season.csv. Re-run only if the draft list changes."""
import os, pandas as pd
DM = os.path.expanduser("~/dm"); R = os.path.dirname(os.path.abspath(__file__))
dr = pd.read_parquet(f"{R}/data/pipeline_backbone.parquet")
FIX = {(2025, 8): "5175643"}   # Egor Demin (BYU): draft list had no ESPN id
ST = ["minutes","points","offensive_rebounds","defensive_rebounds","assists","steals","blocks","three_point_field_goals_attempted","field_goals_attempted","free_throws_attempted","turnovers"]
out = []
for yr in (2024, 2025, 2026):
    b = pd.read_parquet(f"{DM}/mbb_pb_{yr}.parquet"); b = b[b.season_type.isin([2,3])].copy()
    for c in ST: b[c] = pd.to_numeric(b[c], errors="coerce").fillna(0)
    b = b[b.minutes > 0]; b["aid"] = [str(int(float(i))) for i in b.athlete_id]
    g = b.sort_values("game_date").groupby("aid").agg(team=("team_location","last"), gp=("game_id","nunique"), **{c:(c,"sum") for c in ST})
    for r in dr[dr.year == yr].itertuples():
        aid = FIX.get((yr, int(r.overall)), str(r.athlete_id))
        if aid in g.index: out.append({"year": yr, "overall": int(r.overall), "athlete_id": aid, **g.loc[aid].to_dict()})
pd.DataFrame(out).to_csv(f"{R}/data/college_final_season.csv", index=False); print(len(out), "rows")
