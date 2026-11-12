# The Pipeline: backbone study (Nov 11, 2026)
Question: which college player types become NBA players, and which college skills carry over?

## Data (all free, all ESPN IDs so college and NBA records link exactly)
- Every NBA draft pick 2015-2026: ESPN draft API (713 picks), saved in data/espn_nba_drafts_2015_2026.txt. Birth dates from ESPN athlete pages (data/dob.raw, same row order; SHA-256 checked on transfer).
- College stats: sportsdataverse ESPN men's college player box scores 2014-2026, last college season before the draft (under 450 minutes: prior season blended in, same rule as draft model v2).
- NBA outcomes: sportsdataverse ESPN NBA player box scores 2016-2027, regular season only, first 3 seasons after the draft.
- 583 drafted college players; 570 matched to college box scores (13 missing: did not play, e.g. Shaedon Sharpe, Mitchell Robinson). 428 have 3 complete NBA seasons (classes 2015-2023).
- NBA role in a season: Starter (30+ games, started at least half), Rotation (15+ min/game), Bench, Out/G League (under 10 games). "Hit" = Starter or Rotation in year 3.

## Findings
1. Glue skills carry over; scoring does not (college per-40 vs NBA per-36, 357 players with 500+ NBA minutes):
   blocks 0.83, offensive rebounding 0.82, assists 0.77, defensive rebounding 0.76, 3-point attempt rate 0.73, steals 0.66, free-throw rate 0.59, turnovers 0.43, scoring 0.32 (Spearman).
2. Shooting: college FT% predicts NBA 3P% (0.35) better than college 3P% (0.29), matching the Harvard Sports Analysis finding.
3. NBA teams already price college stats in: no single college stat predicts beating your draft slot (all |rho| < 0.10). Pick + age (rank corr 0.573 with 3-year value, leave-one-class-out) beats pick + age + stats (0.551). Stats alone, without the pick: 0.395.
4. Archetypes (k-means on style, k=5 by silhouette; silhouette is low, 0.14, so types are a spectrum, not boxes):
   - Volume Shooter: hit rate 13.9 pts BELOW what their draft slot predicts (95% CI -22.7 to -4.7), beat their slot in only 2 of 9 classes; it holds in round 1, round 2 and the lottery. The market overpays for college scoring guards.
   - Movement Shooter: +8.2 pts above slot (CI -0.9 to +17.0; +13.8 in round 1), above in 6 of 9 classes. Lean: undervalued.
   - Swiss Army Forward +2.3, Connector +1.2, Paint Anchor -3.3: about what their slot predicts.
   Names chosen by Steve (archetype_names.json).

## Archetype v1.1 (Nov 12): fixes for early-season reads
- Steve flagged Tyran Stokes (a guard) reading as a Paint Anchor after 2 games. Two fixes:
  1. Position rule: a prospect can only get archetypes his ESPN position has produced among 2015-2026 draftees (5%+ of that position).
     Guards: Movement Shooter, Connector, Volume Shooter, Swiss Army Forward. Forwards: Swiss Army Forward, Paint Anchor, Movement Shooter. Centers: Paint Anchor, Swiss Army Forward.
     (0 of 300 drafted guards were Paint Anchors.)
  2. Small samples are blended with the typical drafted player at his position (120-minute prior), so 2 games can't swing a read.
     Under 150 minutes the badge says "lean". Faded badge = under 8 games.
- Sleeper/caution flags now come from these reads. Official calls still wait for 8 games.
