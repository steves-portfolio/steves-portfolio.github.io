import sys, json, html, numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.linear_model import LogisticRegression, Ridge
from scipy.stats import spearmanr
df = pd.read_parquet(sys.argv[1]); OUT = sys.argv[2]
df["name"] = df.name.map(html.unescape).str.replace(r"\s+", " ", regex=True)
c = df[df.col_found.fillna(False).astype(bool)].copy()
m = c.c_minutes.clip(lower=1)
for k, col in [("pts","c_points"),("orb","c_offensive_rebounds"),("drb","c_defensive_rebounds"),("ast","c_assists"),("tov","c_turnovers"),("stl","c_steals"),("blk","c_blocks"),("pf","c_fouls")]: c[k + "40"] = 40 * c[col] / m
c["tpa_rate"] = c.c_three_point_field_goals_attempted / c.c_field_goals_attempted.clip(lower=1)
c["ftr"] = c.c_free_throws_attempted / c.c_field_goals_attempted.clip(lower=1)
c["ft_pct"] = (c.c_free_throws_made + 0.72*20) / (c.c_free_throws_attempted + 20)          # shrunk toward 72% (small samples)
c["tp_pct"] = (c.c_three_point_field_goals_made + 0.34*30) / (c.c_three_point_field_goals_attempted + 30)
c["ts"] = c.c_points / (2 * (c.c_field_goals_attempted + 0.44*c.c_free_throws_attempted)).clip(lower=1)
c["mpg"] = c.c_minutes / c.col_games.clip(lower=1)
c["height_in"] = c.height_in.fillna(c.height_in.median()); c["age"] = c.age_draft.fillna(c.age_draft.median())
# ---------- archetypes: style only (what he does on the floor + size), not how good he is ----------
STY = ["pts40","orb40","drb40","ast40","tov40","stl40","blk40","tpa_rate","ftr","height_in"]
Xs = c[STY].values; mu, sd = Xs.mean(0), Xs.std(0); Z = (Xs - mu) / sd
sil = {}
for k in range(5, 11): lab = KMeans(k, n_init=50, random_state=7).fit_predict(Z); sil[k] = round(float(silhouette_score(Z, lab)), 3)
K = int(sys.argv[3]) if len(sys.argv) > 3 else max(sil, key=sil.get)
km = KMeans(K, n_init=100, random_state=7).fit(Z); c["arch"] = km.labels_
cent = pd.DataFrame(km.cluster_centers_, columns=STY)
# ---------- outcomes ----------
done = c[c.n3_complete].copy()   # classes with 3 full NBA seasons (2015-2023)
done["hit"] = done.role3.isin(["Starter","Rotation"]).astype(int); done["stuck"] = (done.role3 != "Out / G League").astype(int)
done["lp"] = np.log(done.overall)
lr = LogisticRegression().fit(done[["lp"]], done.hit); done["exp_hit"] = lr.predict_proba(done[["lp"]])[:,1]
rg = np.polyfit(done.lp, done.gmsc3, 2); done["exp_g"] = np.polyval(rg, done.lp); done["res_g"] = done.gmsc3 - done.exp_g
arch = []
for a, g in done.groupby("arch"):
    yrs = g.groupby("year").apply(lambda x: (x.hit - x.exp_hit).mean())
    arch.append({"arch": int(a), "n": len(g), "avg_pick": round(g.overall.mean(),1), "hit": round(g.hit.mean(),3), "exp_hit": round(g.exp_hit.mean(),3),
                 "over": round((g.hit - g.exp_hit).mean(),3), "res_gmsc3": round(g.res_g.mean(),1), "classes_over": int((yrs > 0).sum()), "classes": int(len(yrs)),
                 "examples_hit": g[g.hit == 1].sort_values("gmsc3", ascending=False).name.head(4).tolist(), "examples_all": g.sort_values("overall").name.head(4).tolist()})
A = pd.DataFrame(arch).merge(cent.round(2).reset_index().rename(columns={"index":"arch"}), on="arch").sort_values("over", ascending=False)
# ---------- translation: which college stats predict NBA value beyond pick + age ----------
FEAT = ["pts40","orb40","drb40","ast40","tov40","stl40","blk40","pf40","tpa_rate","ftr","ft_pct","tp_pct","ts","height_in","age","team_margin","col_seasons","mpg"]
tr = []
for f in FEAT:
    r1, p1 = spearmanr(done[f], done.res_g); tr.append([f, round(float(r1),3), round(float(p1),4)])
tr.sort(key=lambda r: -abs(r[1]))
# leave-one-class-out: pick+age only vs pick+age+college stats (ridge) -> rank correlation with 3-year NBA value
def loco(cols):
    pred = pd.Series(index=done.index, dtype=float)
    for y in sorted(done.year.unique()):
        trn, tst = done[done.year != y], done[done.year == y]
        X = trn[cols].values; xm, xs = X.mean(0), X.std(0)
        mdl = Ridge(alpha=5).fit((X - xm)/xs, trn.gmsc3); pred[tst.index] = mdl.predict((tst[cols].values - xm)/xs)
    per = [spearmanr(pred[done.year == y], done.gmsc3[done.year == y])[0] for y in sorted(done.year.unique())]
    return round(float(spearmanr(pred, done.gmsc3)[0]),3), round(float(np.mean(per)),3)
base = ["lp","age"]
glue = ["orb40","drb40","ast40","stl40","blk40","tpa_rate","ft_pct"]
res = {"pick_only": loco(["lp"]), "pick_age": loco(base), "pick_age_glue": loco(base + glue), "pick_age_all": loco(base + [f for f in FEAT if f != "age"])}
# stats-only model (no draft pick): can college numbers alone find NBA value? (useful before the draft)
res["stats_only_all"] = loco(["age"] + [f for f in FEAT if f != "age"]); res["stats_only_glue"] = loco(["age"] + glue)
out = {"k_silhouette": sil, "K": K, "n_college_found": int(len(c)), "n_with_3yrs": int(len(done)), "classes_3yrs": sorted(int(x) for x in done.year.unique()),
       "hit_rate_all": round(float(done.hit.mean()),3), "archetypes": A.to_dict("records"), "translation_spearman_vs_value_beyond_pick": tr, "loco": res}
json.dump(out, open(f"{OUT}/backbone_results.json","w"), indent=1, default=str)
c.to_parquet(f"{OUT}/backbone_players.parquet")
print(json.dumps({k: out[k] for k in ["k_silhouette","K","n_college_found","n_with_3yrs","hit_rate_all","loco"]}))
pd.set_option("display.width", 250)
print(A[["arch","n","avg_pick","hit","exp_hit","over","res_gmsc3","classes_over","classes"] + STY].to_string(index=False))
for r in A.itertuples(): print(r.arch, "hits:", r.examples_hit, "| top picks:", r.examples_all)
print(tr)
