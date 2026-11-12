import sys, numpy as np, pandas as pd
from scipy.stats import spearmanr, pearsonr
D = sys.argv[1]; c = pd.read_parquet(sys.argv[2])
done = c[c.n3_complete].copy(); done["hit"] = done.role3.isin(["Starter","Rotation"]).astype(int)
from sklearn.linear_model import LogisticRegression
done["lp"] = np.log(done.overall); lr = LogisticRegression().fit(done[["lp"]], done.hit); done["exp_hit"] = lr.predict_proba(done[["lp"]])[:,1]
rng = np.random.default_rng(1)
print("archetype over-expected hit rate, 95% bootstrap CI, and by round:")
for a, g in done.groupby("arch"):
    d = (g.hit - g.exp_hit).values; bs = [rng.choice(d, len(d)).mean() for _ in range(4000)]
    r1 = g[g["round"] == 1]; r2 = g[g["round"] == 2]
    print(a, len(g), round(d.mean(),3), np.round(np.percentile(bs,[2.5,97.5]),3), "| R1", len(r1), round((r1.hit-r1.exp_hit).mean(),3), "| R2", len(r2), round((r2.hit-r2.exp_hit).mean(),3), "| lottery(<=14)", int((g.overall<=14).sum()), round((g[g.overall<=14].hit-g[g.overall<=14].exp_hit).mean(),3))
# skill persistence: college per-40 rates vs NBA per-36 rates over first 3 seasons (players with 500+ NBA minutes)
ST = ["minutes","offensive_rebounds","defensive_rebounds","assists","steals","blocks","turnovers","points","three_point_field_goals_attempted","field_goals_attempted","free_throws_made","free_throws_attempted","three_point_field_goals_made"]
nb = []
for y in range(2016, 2027):
    b = pd.read_parquet(f"{D}/nba_pb_{y}.parquet"); b = b[b.season_type == 2]
    for k in ST: b[k] = pd.to_numeric(b[k], errors="coerce").fillna(0)
    g = b.groupby("athlete_id")[ST].sum().reset_index(); g["season"] = y; g["athlete_id"] = [str(int(float(i))) for i in g.athlete_id]; nb.append(g)
NB = pd.concat(nb)
rows = []
for r in c.itertuples():
    s = NB[(NB.athlete_id == r.athlete_id) & (NB.season > r.year) & (NB.season <= r.year + 3)][ST].sum()
    if s.minutes >= 500: rows.append({"athlete_id": r.athlete_id, **{"n_" + k: v for k, v in s.items()}})
N = c.merge(pd.DataFrame(rows), on="athlete_id")
m = N.n_minutes
pairs = {"Offensive rebounding": ("orb40", 36*N.n_offensive_rebounds/m), "Defensive rebounding": ("drb40", 36*N.n_defensive_rebounds/m), "Assists": ("ast40", 36*N.n_assists/m),
         "Steals": ("stl40", 36*N.n_steals/m), "Blocks": ("blk40", 36*N.n_blocks/m), "Turnovers": ("tov40", 36*N.n_turnovers/m), "Scoring": ("pts40", 36*N.n_points/m),
         "3-point attempt rate": ("tpa_rate", N.n_three_point_field_goals_attempted/N.n_field_goals_attempted.clip(lower=1)),
         "Free-throw rate": ("ftr", N.n_free_throws_attempted/N.n_field_goals_attempted.clip(lower=1))}
print("\nskill persistence college -> NBA (first 3 seasons, 500+ min), n =", len(N))
for k, (cc, nbv) in sorted(pairs.items(), key=lambda kv: -spearmanr(N[kv[1][0]], kv[1][1])[0]): print(f"{k:22s} rho={spearmanr(N[cc], nbv)[0]:.2f}")
ok = N.n_three_point_field_goals_attempted >= 150
nb3 = N.n_three_point_field_goals_made[ok] / N.n_three_point_field_goals_attempted[ok]
print(f"NBA 3P pct (150+ att, n={int(ok.sum())}): college FT pct rho={spearmanr(N.ft_pct[ok], nb3)[0]:.2f}, college 3P pct rho={spearmanr(N.tp_pct[ok], nb3)[0]:.2f}, college 3PA rate rho={spearmanr(N.tpa_rate[ok], nb3)[0]:.2f}")
