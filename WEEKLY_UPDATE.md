# Weekly portfolio update (every Wednesday)

Live site: https://stevetrombetta-analytics-portfolio.netlify.app/
Netlify project: https://app.netlify.com/projects/stevetrombetta-analytics-portfolio/overview

## What updates
| Project | Source | Script | Notes |
| --- | --- | --- | --- |
| 01 College basketball | sportsdataverse team_box_2027.parquet | cbb_refresh.py | Waits until the median team has 5 games (mid-Nov); until then the 2025-26 final ratings stay up |
| 02 NBA draft board + Rookie Report | sportsdataverse player_box_2027.parquet | rookie_refresh.py | Season tips off Oct 20, 2026; before that the page shows a countdown |
| 03 NFL receivers | nflverse ngs_receiving.csv.gz | refresh.py --ngs | |
| 04 NHL defensemen | MoneyPuck skaters CSV (Chrome download) | refresh.py --mp | |

The "answer" text and Unsung Hero cards are computed on the page from the data, so they update on their own.

## Folder layout (Desktop > Project Portfolio > website source)
- src/        page pieces: body.html, style.css, app.js, quad.js
- data/       teams.txt + cbb.json (college), draft.txt (draft), rookies.json (rookie report), quad.json (NFL + NHL)
- data/teams_2025-26_final.txt  backup of last season's final college ratings
- build.py    stitches everything into dist/index.html (the file that gets published)

## Steps
1. Downloads (device shell has GitHub access):
   B=https://github.com/sportsdataverse/sportsdataverse-data/releases/download
   curl -sSL -o ~/team_box_2027.parquet $B/espn_mens_college_basketball_team_boxscores/team_box_2027.parquet
   curl -sSL -o ~/player_box_2027.parquet $B/espn_nba_player_boxscores/player_box_2027.parquet
   curl -sSL -o ~/ngs_receiving.csv.gz https://github.com/nflverse/nflverse-data/releases/download/nextgen_stats/ngs_receiving.csv.gz
   (A 404 / 9-byte file means that season hasn't started; skip that step.)
2. NHL: on moneypuck.com/data.htm in Chrome, fetch('/moneypuck/playerData/seasonSummary/2026/regular/skaters.csv') and save to Downloads.
3. pip install --user pyarrow   (if parquet reading fails)
4. python3 cbb_refresh.py --box ~/team_box_2027.parquet --season 2026-27
   python3 rookie_refresh.py --box ~/player_box_2027.parquet
   python3 refresh.py --ngs ~/ngs_receiving.csv.gz --mp <newest moneypuck_skaters_2026*.csv in Downloads>
   python3 build.py
5. Publish dist/index.html on Netlify ("Drop a folder, .zip, or HTML file"), then check the live site.

## Consistency rules (added Oct 15, 2026)
- refresh.py checks the new data before saving it (no duplicate players, values in sane ranges, row counts didn't collapse, weeks/games never go backwards). If it prints VALIDATION FAILED it exits without changing anything: DO NOT publish that week; report the reason.
- Every successful refresh saves a full copy of the data to data/history/YYYY-MM-DD/, so past weeks are never overwritten.
- "What I found" and the Unsung Hero cards are computed once from the official weekly cut (the default view: WRs 4+ targets per game, TEs 3+, defensemen 18+ min per game in half their team's games). Moving sliders or switching seasons only changes the chart, so the answer only changes when the weekly data changes.
- Hero log: data/history/heroes.csv (date,sport,candidate,hero). After publishing, append 4 lines (cbb, nba, nfl, nhl) using each '.verdict' box's data-candidate and data-hero attributes on the live page (#vCBB, #vDraft, #vNFL, #vNHL). The page uses this log for the 2-week hold rule (a new hero must lead two refreshes in a row) and the "Previous heroes" line.
- NFL target share and EPA per target come from nflverse's official season stats (stats_player_reg_2025/2026.parquet), passed to refresh.py with --stats. Yards per route run is NOT used: nflverse has no 2026 route (participation) data.
- NHL hits, blocks, takeaways and giveaways come from the same MoneyPuck file (current season only; 2025-26 shows a dash).
- The NHL hover trend line is built from the weekly snapshots in data/history, so it fills in one point per week.
- Build only from this folder. It is the single source of truth.

## Draft model v2 (Oct 17, 2026)
- The 2026 draft board is scored offline by draft_model/draft_model.py (position groups guards/wings/bigs, prior-season blend under 450 minutes, age = ~29% of score). It does not change weekly; rerun only if the method changes: python3 draft_model/draft_model.py --box-dir <folder with mbb_pb_2023-2026 + nba_pb_2025-2026 parquet>.
- Backtest on the 2024 + 2025 classes is saved to data/draft_backtest.json and shown on the site (v2 0.22 vs. v1 -0.02 vs. draft order 0.49).
- The old v1 board is kept at data/history/draft_v1_before_model_v2.txt. The NBA hero log was reset when the model changed.

## Pre-publish check + NBA early-season fix (Oct 22, 2026)
- NBA card: until 5 college draftees have 3+ NBA games, the card keeps the draft-board view (model steals/reaches) and the model's late-round hero, with that player's NBA games so far. After that it switches to the model-vs-scouts scoreboard. If no late pick (20+) has 3+ games yet, the hero falls back to the draft-board pick, so the card is never empty. Old version saved at data/history/app_before_2026-10-22.js.
- check_build.py renders dist/index.html in headless Chromium (run in the cloud container, which has Playwright) and fails if any chart is missing, any Unsung Hero card is empty, any list is empty, any card lacks data-candidate/data-hero, there are JS errors, or the page's NFL weeks / NHL games don't match data/quad.json. Never publish when it fails.
  python3 check_build.py dist/index.html --expect-nfl-weeks <N> --expect-nhl-gp <N>
- The weekly run always sends Steve a notification with the result.

## Self-hosted logos + image fallbacks (Oct 22, 2026)
- Why: on Oct 22 the Canucks logos showed as broken images because ESPN's logo CDN briefly failed in the visitor's browser.
- All team logos (365 college, 30 NBA, 32 NFL, 32 NHL, Arsenal) are now embedded in the page from data/logos.json (built in by build.py as LOGOS). The page no longer loads team logos from ESPN at all.
- src/logos.js: if any image still fails (headshots, or a team not in the pack), it retries once, then shows a neat team-code badge (logos) or falls back to the team logo / hides it (headshots). The browser's broken-image icon never shows.
- check_build.py now also fails if any team logo the page uses is missing from data/logos.json (e.g. a new team code), and lists the missing "league/id" keys.
  Fix: set KEYS in logo_pack_snippet.js to those keys, run it in Chrome on the live site (saves Downloads/portfolio_logos_add.json), then
  python3 add_logos.py "$HOME/mnt/Downloads/portfolio_logos_add.json" && python3 build.py, and re-run the check.
- Files before this change: data/history/before_logo_pack_2026-10-22/.

## NBA current teams (Oct 22, 2026)
- Why: the draft board used draft-night teams only, so players traded later showed the wrong team (Koa Peat showed Mavericks, he's on the Suns; 7 draftees in all).
- Each draftee's team is now: team in his latest NBA game (rookies.json) > ESPN current roster (data/nba_teams.json) > draft-night team (NBA_PICK in src/app.js). Traded players show "(drafted by X)".
- Weekly step (before build.py): in Chrome open https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams, run nba_rosters_snippet.js, then
  python3 nba_teams.py "<newest nba_rosters*.json in Downloads>"   (prints any team changes; exits 1 if the roster file looks broken)
- check_build.py fails if any draftee shows a team different from his latest game/roster, or if data/nba_teams.json is missing or more than 9 days old.

## Oct 29, 2026: back to the published version + moved to GitHub
- The Oct 25 brainstorm changes (college v2 + predictions, 2027 prospects, project index) were never published and are NOT part of the site. Steve decided to stay with the published (Oct 22) version and only update data.
- The source folder was rebuilt from the live page, so build.py reproduces the published site exactly. Brainstorm files are kept in "older site versions/brainstorm version 2026-10-25 (source)" and website source/brainstorm_only/ (not in the repo).
- College: cbb_refresh.py is the v1 script again: python3 cbb_refresh.py --box <team_box_2027.parquet> --season 2026-27 (keeps 2025-26 final until the median team has 5 games). No --sched, no prospects step.
- Hosting moved from Netlify (15 credits per publish) to GitHub Pages (free):
  Repo: https://github.com/steves-portfolio/steves-portfolio.github.io
  Site: https://steves-portfolio.github.io/
  build.py now also writes docs/index.html; GitHub Pages serves main branch /docs.
- Publishing = uploading the changed files to the repo (main branch) and committing; Pages republishes in about a minute. Try bigger changes on a separate branch first.
- The old Netlify site stays up with the Oct 22 data until Steve decides what to do with it.

## Nov 7, 2026: renamed to Steve's Portfolio
- GitHub account renamed steves-sports-analytics -> steves-portfolio; repo renamed to steves-portfolio.github.io.
- New site: https://steves-portfolio.github.io/  (the old steves-sports-analytics.github.io link no longer works; GitHub doesn't redirect Pages sites)
- Page title is now "Steve's Portfolio · Steve Trombetta"; header still shows Steve Trombetta. Data and layout unchanged.
- Files before the rename: data/history/before_rename_2026-11-07/.

## Nov 10, 2026: take headlines, Called It, college deep-dive lists
- Removed: every "coming next" placeholder (Premier League) and the college Matchup projector.
- Headlines are takes, auto-written from the data each build (question stays as the small line underneath):
  NBA: "The scouts are cooking my model." / "My model is cooking the scouts." / coin flip if the two rank correlations are within 0.03.
  College: "<top fraud> is a fraud. <top sleeper> is better than you think." ONLY on current-season ratings. While data/cbb.json has final=true (last season), the plain question stays and the lists use neutral labels. Steve's rule: no takes until the median team has 5 games.
- College card lists (3 each): Frauds, Sleepers (well-known programs), Mid-majors that can hang (best-rated teams outside that list), Paper tigers (mid-majors with a top-50 record, bottom-half schedule, rated 25+ spots below their record).
- cbb_refresh.py now writes "tracking" (games, median games, need) into data/cbb.json while it waits for 5 games; the page shows it as progress. Upload data/cbb.json each week.
- NBA "Called it: struggling" (v1), in src/app.js draftVerdict. Sample = college draftees with 3+ NBA games, full college seasons only. Ranks inside that sample:
  modelGap = model rank - draft rank (need >= 4), miss = Game Score rank - draft rank (need >= 3). Sort by min(modelGap, miss), ties to the higher pick, top 3.
  The names are in #vDraft data-called. Only tune the thresholds with Steve's OK, and note any change here.
- Files before this change: data/history/before_takes_2026-11-10/ and data/history/before_remove_coming_2026-11-10/. Preview copy: ../preview work 2026-11-10 (safe to ignore).
- College hoops END GOAL (Steve, Nov 10): help as much as possible for March Madness. Track every team through the whole regular season, plus the signals that say how a team will do down the stretch. Build new college features toward that.

## Nov 11, 2026: The Pipeline (Steve's flagship project, planned, not built yet)
- Pitch: "I follow every draft prospect from his first college game to his third NBA season, and grade my own model along the way."
- Lenses: glue guy (skills that translate: rebounding, steals/blocks, assists, FT%, 3-pt rate) + market (rising / overhyped vs. consensus + Vegas). No Philly angle. No card content on the page.
- One page: take headline, Board (top ~60 from Ultimate Big Board consensus, credited) with model rank, translation score, archetype badge, stock-ticker sparkline; sleeper receipts (dated calls, graded); award race (POY + Freshman, "impact on a winner"); Steve's Guys (from Steves Notes.xlsx); NBA chapter (Rookie Report + 2024-26 class tracker, roles by minutes AND starts).
- Archetypes: data clusters, Steve names them and can override per player.
- Backbone study: which college archetypes become NBA players, drafted college players since ~2015.
- Steve's notes live in ../Steves Notes.xlsx (Prospects sheet). The refresh only reads it, never writes it.
- June 2027 = success if sleepers were called before their breakout, and rookie data proves which college skills translate.
- Odds key (odds_key.txt) still needed for the Vegas line.

## Nov 12, 2026: SITE REWORK. The Pipeline is now the only project on the site
- Steve is reworking the portfolio. The live site (docs/index.html) is now ONLY The Pipeline page. The old multi-sport site (college ratings, NBA draft board, NFL/NHL quadrants) is archived locally:
  ../older site versions/2026-11-12 multi-sport site (before The Pipeline).html and "...multi-sport site src". Its scripts (build.py, refresh.py, cbb_refresh.py, rookie_refresh.py, check_build.py) are NOT part of the weekly run any more. NEVER run build.py: it would overwrite docs/index.html with the old site.
- Page source: pipeline/render.py (HTML/CSS/JS template) + data/pipeline.json. Style: src/style.css.

### Weekly Pipeline refresh (every Wednesday)
1. Downloads (device_bash; a file under 1 KB is a 404, stop and report):
   B=https://github.com/sportsdataverse/sportsdataverse-data/releases/download; mkdir -p $HOME/dm && cd $HOME/dm
   for y in 2025 2026 2027; do curl -sSL -m 150 -o mbb_pb_$y.parquet $B/espn_mens_college_basketball_player_boxscores/player_box_$y.parquet; done
   curl -sSL -m 150 -o nba_pb_2027.parquet $B/espn_nba_player_boxscores/player_box_2027.parquet
2. Consensus board (Chrome): open https://ultimatebigboard.com/nba/2027/, collect the 60 player links (rank|slug|avg pick|row text) and save Downloads/ubb_nba_2027_<YYYY-MM-DD>.txt (see the Nov 11 session; header rank|slug|avg_pick|text). Copy it into pipeline/work/. If it fails, reuse the newest file in pipeline/work/ and say so.
3. python3 pipeline/board_refresh.py pipeline/work/<newest ubb file>
   - "NEED BIO" ids: in Chrome on https://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball fetch /v2/sports/basketball/leagues/mens-college-basketball/athletes/<id> for each and append id:height:dob:class:position to pipeline/work/bio27.txt (comma separated), then rerun step 3.
   - "CHECK same-name matches": confirm the school matches the board; fix in ID_FIX if not.
4. python3 pipeline/pipeline_build.py   (writes data/pipeline.json, logs official calls in data/pipeline_calls.csv once a player has 8+ games, snapshots data/history/pipeline/board_<date>.csv)
5. python3 pipeline/render.py data/pipeline.json src/style.css docs/index.html
6. Check (cloud container, Playwright): stage docs/index.html + pipeline/check_pipeline.py; python3 check_pipeline.py <staged index.html>. If it fails: publish nothing, notify Steve.
7. Publish (GitHub web upload, main branch): data (pipeline.json, pipeline_calls.csv), data/history/pipeline (new snapshot), pipeline/work (new ubb file, bio27.txt if changed), docs/index.html LAST. Confirm the live site shows the new "Updated" date.
8. Notify Steve: board movers (biggest model/expert gaps, any archetype that changed), new official calls, rookie leaders/laggards vs. slot, award race top 3.

### How the model evolves during the season (Steve's standing instruction: handle it as the data says)
- Archetype reads: position rule (only archetypes his position has produced) + 120-minute position prior. Lean < 150 min, faded < 8 games. Revisit the prior size in mid-December once most players pass 8 games; document any change here with the date.
- Official sleeper/caution calls lock at 8 games and are never edited afterwards; grade them at the draft and after the rookie year.
- Once college team ratings are live (median team 5+ games), weight the award race by opponent quality.
- Any model change = new version note here + the README in research/pipeline_backbone, and a short "what changed" line on the page.
