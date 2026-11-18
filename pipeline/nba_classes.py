"""Per-class NBA tables for The Pipeline (added Nov 17, 2026).
build_class(year, ...) returns one row per pick: college line + this season's NBA line + "vs. slot".
- 2026 class: every college pick, both rounds (unchanged behaviour).
- 2025 / 2024 classes: the whole first round (picks 1-30), including international / no-college picks
  (archetype "No college data"). "Vs. slot" is ranked within the rows shown, among players with 3+ games."""
import json, html, os
import pandas as pd
ID_FIX = {(2025, 8): "5175643"}   # Egor Demin: draft list has no ESPN id (found on the BKN roster, Nov 17 2026)
_R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "research", "pipeline_backbone")
# Page display line = his actual last college season (ESPN box scores, no blending). Added Nov 17 2026 after Steve caught Demin showing "no college data".
_CF = os.path.join(_R, "data", "college_final_season.csv")
CFS = pd.read_csv(_CF, dtype={"athlete_id": str}).set_index("athlete_id") if os.path.exists(_CF) else pd.DataFrame()
_AM = json.load(open(os.path.join(_R, "archetype_model.json")))
def _arch(c, h):   # nearest archetype center for a player the backbone missed (same features as the backbone)
    import numpy as np
    m = max(c.minutes, 1); fga = max(c.field_goals_attempted, 1)
    x = dict(pts40=40*c.points/m, orb40=40*c.offensive_rebounds/m, drb40=40*c.defensive_rebounds/m, ast40=40*c.assists/m, tov40=40*c.turnovers/m,
             stl40=40*c.steals/m, blk40=40*c.blocks/m, tpa_rate=c.three_point_field_goals_attempted/fga, ftr=c.free_throws_attempted/fga, height_in=h)
    z = (np.array([x[f] for f in _AM["features"]]) - np.array(_AM["mean"])) / np.array(_AM["sd"])
    return _AM["names"][int(np.argmin(np.linalg.norm(np.array(_AM["centers"]) - z, axis=1)))]
def _line(aid):
    c = CFS.loc[aid]; m = max(c.minutes, 1)
    return {"college": c.team, "c_gp": int(c.gp), "c_ppg": round(c.points/c.gp, 1), "c_reb40": round(40*(c.offensive_rebounds + c.defensive_rebounds)/m, 1),
            "c_ast40": round(40*c.assists/m, 1), "c_stk40": round(40*(c.steals + c.blocks)/m, 1)}
_NF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work", "nba_status_notes.txt")
NOTES = {}
if os.path.exists(_NF):
    for l in open(_NF, encoding="utf-8").read().splitlines():
        if l.strip() and not l.startswith("#"): i, t, n = l.split("|", 2); NOTES[i.strip()] = (t.strip() or None, n.strip())

def _nba_line(aid, NA_):
    n_ = NA_.loc[aid]; m_ = max(n_.minutes, 1)
    return dict(team=n_.team, gp=int(n_.gp), starts=int(n_.starts), mpg=round(n_.minutes/n_.gp, 1), ppg=round(n_.points/n_.gp, 1),
                rpg=round(n_.rebounds/n_.gp, 1), apg=round(n_.assists/n_.gp, 1),
                ts=round(n_.points/(2*(n_.field_goals_attempted + 0.44*n_.free_throws_attempted)), 3) if n_.field_goals_attempted else None,
                gs_g=round(n_.gs/n_.gp, 2), n_reb36=round(36*n_.rebounds/m_, 1), n_ast36=round(36*n_.assists/m_, 1), n_stk36=round(36*(n_.steals + n_.blocks)/m_, 1))

def build_class(year, bp, NA_, NSTAT=None, dr=None, max_pick=None):
    NSTAT = NSTAT or {}
    BPY = bp[bp.year == year].set_index("athlete_id")
    if dr is not None:   # whole draft list (incl. international picks)
        picks = dr[dr.year == year]
        if max_pick: picks = picks[picks.overall <= max_pick]
        picks = [(int(r.overall), ID_FIX.get((year, int(r.overall)), str(r.athlete_id)), html.unescape(str(r.name)), bool(r.college)) for r in picks.itertuples()]
    else:
        picks = [(int(r.overall), str(aid), r.name, True) for aid, r in BPY.iterrows() if not max_pick or r.overall <= max_pick]
    out_ = []
    for pick, aid, name, col in sorted(picks):
        if aid in BPY.index:
            r = BPY.loc[aid]
            d_ = {"pick": pick, "name": r["name"], "aid": aid, "college": r.col_team, "archetype": r.archetype,
                  "c_ppg": round(r.c_points / max(r.col_games, 1), 1), "c_reb40": round(40*(r.c_offensive_rebounds + r.c_defensive_rebounds)/max(r.c_minutes, 1), 1),
                  "c_ast40": round(40*r.c_assists/max(r.c_minutes, 1), 1), "c_stk40": round(40*(r.c_steals + r.c_blocks)/max(r.c_minutes, 1), 1)}
            if aid in CFS.index: d_.update(_line(aid))
        elif aid in CFS.index:   # in the box scores but missing from the backbone (e.g. Demin)
            h = dr[(dr.year == year) & (dr.overall == pick)].height_in.iloc[0] if dr is not None else None
            d_ = {"pick": pick, "name": " ".join(name.split()), "aid": aid, "archetype": _arch(CFS.loc[aid], float(h) if h == h and h else 79.0), **_line(aid)}
        else:
            d_ = {"pick": pick, "name": " ".join(name.split()), "aid": aid, "college": "College stats missing" if col else "Pro route", "archetype": "No college data", "c_ppg": None}   # e.g. Egor Demin (BYU): ESPN has no box scores for him
        if aid in NA_.index: d_.update(_nba_line(aid, NA_))
        else:
            stt = NSTAT.get(aid); d_.update(gp=0, team=stt[0] if stt else None, nba_status=stt[1] if stt else None)
        if aid in NOTES:
            t_, n_ = NOTES[aid]; d_["note"] = n_
            if t_ and not d_.get("team"): d_["team"] = t_
            if not t_ and not d_.get("gp"): d_["team"] = None   # free agent / waived: no current NBA team
        out_.append(d_)
    df_ = pd.DataFrame(out_); q_ = df_[df_.gp >= 3].copy()
    q_["prod_rank"] = q_.gs_g.rank(ascending=False, method="min"); q_["pick_rank"] = q_.pick.rank(method="min"); q_["vs_slot"] = (q_.pick_rank - q_.prod_rank).astype(int)
    df_ = df_.merge(q_[["aid","prod_rank","vs_slot"]], on="aid", how="left")
    return json.loads(df_.to_json(orient="records"))
