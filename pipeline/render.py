"""The Pipeline page renderer. Usage: python3 pipeline/render.py data/pipeline.json src/style.css docs/index.html"""
import json, sys, pathlib
d = json.loads(pathlib.Path(sys.argv[1]).read_text())
css = pathlib.Path(sys.argv[2]).read_text()
extra = r"""
.pv{background:#fff6dd;border-bottom:1px solid #ecd9a4;font:500 13.5px/1.5 var(--f-ui);color:#6b5413;padding:10px 0}
.sec{padding:34px 0 8px}.sec h3.sh{font:700 26px/1.25 var(--f-serif);margin:0 0 4px}.sec .sd{font:400 15px/1.55 var(--f-ui);color:var(--ink2);margin:0 0 16px;max-width:760px}
.kick{font:700 12px var(--f-ui);letter-spacing:.1em;text-transform:uppercase;color:var(--p)}
.charts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}@media (max-width:900px){.charts{grid-template-columns:1fr}}
.cbox{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:18px 20px;min-width:0}
.cbox h4{font:700 18px/1.3 var(--f-serif);margin:0 0 2px}.cbox .cap{font:400 13px/1.5 var(--f-ui);color:var(--ink3);margin:0 0 10px}
.cbox svg{width:100%;height:auto;display:block}svg text{font-family:var(--f-ui)}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 12px}.chip{font:600 12.5px var(--f-ui);border:1px solid var(--line2);background:var(--paper);border-radius:999px;padding:5px 11px;cursor:pointer;color:var(--ink2)}
.chip[aria-pressed=true]{background:var(--ink);color:#fff;border-color:var(--ink)}
.tw{overflow:auto;max-height:640px;border:1px solid var(--line);border-radius:10px;background:var(--paper)}
table.bd{width:100%;border-collapse:collapse;font:500 13.5px var(--f-ui)}table.bd th{font:700 11.5px var(--f-ui);letter-spacing:.06em;text-transform:uppercase;color:var(--ink3);text-align:left;padding:10px 10px;border-bottom:1px solid var(--line2);position:sticky;top:0;background:var(--paper);cursor:pointer;white-space:nowrap}
table.bd td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:middle}table.bd tr:hover td{background:#faf6ec}
.pn{font-weight:700;color:var(--ink)}.pn small{display:block;font-weight:400;color:var(--ink3);font-size:12px}
.ab{display:inline-block;font:700 11.5px var(--f-ui);padding:3px 8px;border-radius:6px;color:#fff;white-space:nowrap}.ab.e{opacity:.55}
.gl{display:inline-flex;align-items:center;gap:6px}.gl i{display:inline-block;height:8px;border-radius:4px;background:#a8791c}
.gp{font-weight:700}.gp.up{color:var(--good)}.gp.dn{color:var(--bad)}
.fl{font:700 11px var(--f-ui);padding:3px 7px;border-radius:6px;white-space:nowrap}.fl.s{background:#e3f1e8;color:var(--good)}.fl.c{background:#f7e3e3;color:var(--bad)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
.card{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:14px 16px;border-top:4px solid var(--good)}.card.c{border-top-color:var(--bad)}
.card b{font:700 17px var(--f-serif)}.card .m{font:500 12.5px/1.5 var(--f-ui);color:var(--ink3)}.card p{font:400 14px/1.5 var(--f-ui);margin:8px 0 0;color:var(--ink2)}
.note{border:1px dashed var(--line2);border-radius:10px;padding:12px 16px;font:500 13.5px/1.5 var(--f-ui);color:var(--ink3);margin-top:12px}
.lg-k{display:flex;gap:12px;flex-wrap:wrap;font:500 12px var(--f-ui);color:var(--ink2);margin-top:8px}.lg-k i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.aw{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}@media (max-width:900px){.aw{grid-template-columns:1fr}}
.aw ol{margin:0;padding:0;list-style:none}.aw li{display:flex;gap:10px;align-items:baseline;padding:7px 0;border-top:1px solid var(--line);font:500 13.5px var(--f-ui)}.aw li .r{font:700 13px var(--f-ui);color:var(--ink3);width:20px}.aw li small{color:var(--ink3);display:block;font-weight:400}
.lean{display:inline-block;margin-left:6px;font:600 11px var(--f-ui);color:var(--ink3);font-style:italic}@media (max-width:700px){.glc{display:none}table.bd td,table.bd th{padding:7px 6px}}
.rk{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}@media (max-width:900px){.rk{grid-template-columns:1fr}}
.rc{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:14px 16px;border-top:4px solid var(--good)}.rc.dn{border-top-color:var(--bad)}
.rc .top{display:flex;gap:10px;align-items:center}.hs{width:54px;height:40px;object-fit:cover;object-position:top;border-radius:6px;background:#f1ece1}
.rc .ln{display:grid;grid-template-columns:auto 1fr;gap:2px 10px;font:500 12.5px/1.45 var(--f-ui);margin-top:10px}.rc .ln span:nth-child(odd){color:var(--ink3);font-weight:700;letter-spacing:.04em;text-transform:uppercase;font-size:11px}
.pw{display:flex;gap:10px;align-items:center}.pw .hs,.pn .hs{width:44px;height:32px}.hs.ini{display:inline-flex;align-items:center;justify-content:center;font:700 12px var(--f-ui);color:var(--ink3);background:#f1ece1;border-radius:6px;flex:none}
.hero h1{font:700 clamp(30px,4.2vw,44px)/1.15 var(--f-serif);margin:6px 0 10px;max-width:900px}.hero .take{font:600 19px/1.45 var(--f-serif);color:var(--ink2);max-width:820px;margin:0}
"""
html = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>The Pipeline · Steve Trombetta</title><meta name="description" content="Steve Trombetta follows every NBA draft prospect from his first college game to his third NBA season, and grades his own model along the way."><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='10' fill='%231f4e8c'/%3E%3Ctext x='32' y='44' font-family='Impact,sans-serif' font-size='34' fill='white' text-anchor='middle'%3EST%3C/text%3E%3C/svg%3E">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap" rel="stylesheet">
<style>""" + css + extra + """</style></head><body>
<header class="mast"><div class="wrap mast-in"><a class="brand" href="#"><b>Steve Trombetta</b><span>Steve's portfolio</span></a><nav class="nav" style="margin-left:auto;display:flex;gap:18px;font:600 14px var(--f-ui)"><a href="#board27" style="text-decoration:none;color:var(--ink2)">2027 Board</a><a href="#nba" style="text-decoration:none;color:var(--ink2)">NBA Rookies</a><a href="#backbone" style="text-decoration:none;color:var(--ink2)">The Study</a><a href="#about" style="text-decoration:none;color:var(--ink2)">About</a></nav></div></header>
<div class="pv"><div class="wrap" id="upd"></div></div>
<div class="wrap">
<section class="sec hero"><span class="kick">The Pipeline · College → Draft → NBA</span>
<h1>I follow every draft prospect from his first college game to his third NBA season, and grade my own model along the way.</h1>
<p class="take" id="take"></p></section>
<section class="sec" style="padding-top:8px"><div id="flow"></div></section>

<section class="sec" id="board27"><span class="kick">2027 Board</span><h3 class="sh">The experts' top 58, run through my model</h3>
<p class="sd">Experts = the <a href="https://ultimatebigboard.com/nba/2027/">Ultimate Big Board</a> consensus (14 sources). Model = my draft model v2 (position group + age). Archetype and glue score come from the backbone study. Faded badges = early read (under 8 games).</p>
<div class="charts" style="margin-bottom:18px"><div class="cbox"><h4>Experts vs. my model</h4><p class="cap">Above the line: my model likes him more than the experts do. Color = archetype.</p><div id="c_sc"></div></div>
<div class="cbox"><h4>What kind of players are on the board</h4><p class="cap">Archetype mix of the 51 college prospects with games.</p><div id="c_pie"></div></div></div>
<div class="chips" id="chips"></div>
<div class="tw"><table class="bd" id="board"></table></div><p class="sd" style="font-size:13px;margin-top:8px"><b>Reading the archetype:</b> a <i>lean</i> means under 150 minutes this season, so his read leans on what players at his position usually look like. It firms up with every game. Faded = under 8 games. Model (gap) = my model's rank, and how many spots above (+) or below (−) the experts.</p></section>

<section class="sec"><span class="kick">Receipts</span><h3 class="sh">Watch list, then official calls</h3>
<p class="sd">Rules: a <b>sleeper</b> is a Movement Shooter, Connector or Swiss Army Forward with a glue score of 60+ whom my model ranks 8+ spots above the experts. A <b>caution</b> is a Volume Shooter in the experts' top 20. Calls become official, dated and graded once a player reaches 8 games.</p>
<div class="cards" id="watch"></div><div class="note" id="calls"></div></section>

<section class="sec" id="nba"><span class="kick">Now in the NBA</span><h3 class="sh">The 2026 class: from college to the league</h3>
<p class="sd" id="rkd"></p>
<div class="rk" id="rkcards"></div>
<div class="charts" style="margin-top:20px"><div class="cbox"><h4>Does the glue carry over already?</h4><p class="cap">Each dot is a rookie (3+ games, 10+ min a game): his college rate (per 40) against his NBA rate (per 36). r = how tightly they line up.</p><div id="c_tr"></div></div>
<div class="cbox"><h4>2026 class: production vs. draft slot by archetype</h4><p class="cap" id="c26cap"></p><div id="c_26"></div><p class="cap" id="c26n"></p></div></div>
<div class="chips" id="rchips" style="margin-top:18px"></div>
<div class="tw"><table class="bd" id="rtab"></table></div>
<h4 style="font:700 20px var(--f-serif);margin:26px 0 4px">Year 2: the 2025 class</h4><p class="sd" style="font-size:14px">Second-year players, same lens. Top 10 by Game Score per game this season.</p>
<div class="tw"><table class="bd" id="stab"></table></div></section>

<section class="sec" id="backbone"><span class="kick">The backbone</span><h3 class="sh">What 570 drafted players taught me</h3>
<p class="sd" id="bbd"></p>
<div class="charts"><div class="cbox"><h4>The dirty work translates. Scoring doesn't.</h4><p class="cap">How closely a player's college rate matches his NBA rate (first 3 seasons, 357 players with 500+ NBA minutes). 1.0 = identical.</p><div id="c_pers"></div></div>
<div class="cbox"><h4>The draft overpays for Volume Shooters</h4><p class="cap">How often each archetype became an NBA starter or rotation player by year 3, compared with what its draft slots predicted. Dot = average, line = 95% range.</p><div id="c_arch"></div></div></div></section>

<section class="sec"><span class="kick">Award race</span><h3 class="sh">Who's winning by the numbers</h3>
<p class="sd" id="awd"></p><div class="aw"><div class="cbox"><h4>Player of the Year</h4><ol id="poy"></ol></div><div class="cbox"><h4>Freshman of the Year <small style="font:500 12px var(--f-ui);color:var(--ink3)">(first year in D1)</small></h4><ol id="fy"></ol></div></div></section>

<section class="sec"><span class="kick">Steve's Guys</span><h3 class="sh">The players I'm following</h3>
<div class="note">This section fills in from <b>Steves Notes.xlsx</b>: mark a player "Y" under My guy, add your archetype call and notes, and each one gets a card here with your take next to what the numbers say.</div></section>

<section class="sec"><span class="kick">The NBA chapter</span><h3 class="sh">Did it hold up in the league?</h3>
<div class="charts"><div class="cbox"><h4>Where a draft class ends up</h4><p class="cap">Role in the 2025-26 season. Starter = started most of 30+ games; Rotation = 15+ min/game; Bench = less; Out = under 10 NBA games.</p><div id="c_flow"></div><div class="lg-k" id="flk"></div></div></div>
<div class="note">Graded every June: did the sleepers rise, did the caution calls fall, and did college glue scores predict rookie production? The model gets a new version only if the grade says it should.</div></section>
<section class="sec" id="about"><span class="kick">About</span><h3 class="sh">About me</h3><p class="sd">I'm Steve Trombetta, a senior in Information Systems &amp; Analytics at Rowan University (May 2027) and a former college soccer player. The Pipeline is built end to end by me: ESPN and sportsdataverse box scores, the Ultimate Big Board consensus, Python models, and a weekly automated refresh with validation checks before anything publishes.</p>
<p class="sd" style="font-size:13px">Data: ESPN box scores via sportsdataverse (hoopR / hoopR-py), ESPN draft and roster data, Ultimate Big Board consensus. Headshots from ESPN. For information and entertainment.</p></section>
<div style="height:40px"></div></div>
<script>
const D = """ + json.dumps(d) + """;
const IMG = (lg, id) => `https://a.espncdn.com/combiner/i?img=/i/headshots/${lg}/players/full/${id}.png&w=110&h=80`;
const initials = n => String(n||'').split(' ').filter(Boolean).slice(0,2).map(w => w[0]).join('');
window.__hsFail = img => { const sp = document.createElement('span'); sp.className = img.className + ' ini'; sp.textContent = img.dataset.ini || ''; img.replaceWith(sp); };
const face = (lg, id, name) => id ? `<img class="hs" src="${IMG(lg, id)}" alt="" loading="lazy" data-ini="${initials(name)}" onerror="__hsFail(this)">` : `<span class="hs ini">${initials(name)}</span>`;
document.getElementById('upd').textContent = `Updated ${D.updated} · NBA data through ${D.nba_through} · College reads firm up as games are played (lean = under 150 minutes, faded = under 8 games).`;
const $ = s => document.querySelector(s), esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const AC = {"Movement Shooter":"#1f4e8c","Swiss Army Forward":"#2e7d4f","Connector":"#a8791c","Paint Anchor":"#6b4fa0","Volume Shooter":"#b23a3a"};
const B = D.board, scored = B.filter(r => r.archetype);
const sl = B.filter(r => r.flag === 'sleeper').sort((a,b) => b.glue_pct - a.glue_pct || b.gap - a.gap)[0];
const rk1 = [...D.rookies.filter(r => r.gp >= 3)].sort((a,b) => b.vs_slot - a.vs_slot)[0];
$('#take').innerHTML = `This week: <b>${esc(sl.player)}</b> is the college name to watch (experts No. ${sl.cons_rank}, my model No. ${sl.model_rank}). In the NBA, <b>${esc(rk1.name)}</b> (pick ${rk1.pick}) is outplaying his draft slot by ${rk1.vs_slot} spots.`;
// flow diagram
(() => { const st = [["College","Every game, every prospect"],["Draft","Experts vs. my model"],["NBA","Rookie production, 3 seasons"],["Grade","Model graded, then updated"]], w = 230, g = 40;
  let s = `<svg viewBox="0 0 1060 140" role="img" aria-label="College, draft, NBA, grade, then back to college"><defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#767b84"/></marker></defs>`;
  st.forEach(([a,b],i) => { const x = i*(w+g)+10, L = i === 3; s += `<rect x="${x}" y="10" width="${w}" height="70" rx="10" fill="${L?'#e7edf6':'#fffdf8'}" stroke="${L?'#1f4e8c':'#d2c9b8'}" stroke-width="${L?2:1.25}"/><text x="${x+18}" y="40" font-size="19" font-weight="700" fill="#1d1f23">${a}</text><text x="${x+18}" y="63" font-size="13.5" fill="#43474f">${b}</text>`; if (i < 3) s += `<line x1="${x+w+4}" y1="45" x2="${x+w+g-6}" y2="45" stroke="#767b84" stroke-width="1.5" marker-end="url(#ar)"/>`; });
  s += `<path d="M${3*(w+g)+10+w/2} 82 V118 H${10+w/2} V86" fill="none" stroke="#1f4e8c" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#ar)"/><text x="530" y="132" text-anchor="middle" font-size="12.5" fill="#1f4e8c">every June, the grade feeds next year's board</text>`;
  $('#flow').innerHTML = s + '</svg>'; })();
$('#bbd').innerHTML = `Every NBA pick from 2015 to 2026 (${D.study.picks} picks), linked by ESPN player ID to his last college season and his NBA box scores. ${D.study.three_seasons} college players from the ${D.study.classes} classes have three full NBA seasons to grade. Two findings drive everything below.`;
// persistence bars
(() => { const P = D.persistence, W = 520, rh = 30, H = P.length*rh + 10; let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="College to NBA skill persistence">`;
  P.forEach(([k,v],i) => { const y = i*rh + 4, w = v/1*300, sc = k === 'Scoring' || k === 'Turnovers'; s += `<text x="0" y="${y+17}" font-size="13" fill="#1d1f23" font-weight="${sc?700:500}">${k}</text><rect x="170" y="${y+5}" width="${w}" height="16" rx="4" fill="${sc?'#b23a3a':'#a8791c'}"/><text x="${176+w}" y="${y+18}" font-size="12.5" font-weight="700" fill="#1d1f23">${v.toFixed(2)}</text>`; });
  $('#c_pers').innerHTML = s + '</svg>'; })();
// archetype dot + whisker
(() => { const A = D.archetypes, W = 560, rh = 46, H = A.length*rh + 46, X = v => 395 + v/0.25*140; let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Archetype hit rate versus draft slot">`;
  s += `<rect x='265' y='0' width='${W-265}' height='${H-36}' fill='#faf7f0'/>`; for (const t of [-0.2,-0.1,0,0.1,0.2]) s += `<line x1="${X(t)}" x2="${X(t)}" y1="0" y2="${H-36}" stroke="${t===0?'#767b84':'#e6e0d4'}"/><text x="${X(t)}" y="${H-22}" text-anchor="middle" font-size="11" fill="#767b84">${t>0?'+':''}${Math.round(t*100)}</text>`;
  A.forEach((a,i) => { const y = i*rh + 18, c = AC[a.name]; s += `<text x="0" y="${y+4}" font-size="13.5" font-weight="700" fill="#1d1f23">${a.name}</text><text x="0" y="${y+19}" font-size="11" fill="#767b84">${a.like}</text><line x1="${X(a.lo)}" x2="${X(a.hi)}" y1="${y}" y2="${y}" stroke="${c}" stroke-width="2.5"/><circle cx="${X(a.over)}" cy="${y}" r="6" fill="${c}"/><text x="${X(a.hi)+6}" y="${y+4}" font-size="12" font-weight="700" fill="${c}">${a.over>0?'+':''}${Math.round(a.over*1000)/10}</text>`; });
  s += `<text x="${X(0)}" y="${H-1}" text-anchor="middle" font-size="10.5" fill="#767b84">points above / below what the draft slot predicted</text>`;
  $('#c_arch').innerHTML = s + '</svg>'; })();
// scatter experts vs model
(() => { const W = 520, H = 360, m = 40, N = 58, X = v => m + (v-1)/(N-1)*(W-m-14), Y = v => 14 + (v-1)/(N-1)*(H-m-14); let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Experts rank vs model rank">`;
  s += `<line x1="${X(1)}" y1="${Y(1)}" x2="${X(N)}" y2="${Y(N)}" stroke="#d2c9b8" stroke-dasharray="4 4"/>`;
  for (const t of [1,10,20,30,40,50]) s += `<text x="${X(t)}" y="${H-22}" text-anchor="middle" font-size="11" fill="#767b84">${t}</text><text x="${m-8}" y="${Y(t)+4}" text-anchor="end" font-size="11" fill="#767b84">${t}</text>`;
  s += `<text x="${(W+m)/2}" y="${H-4}" text-anchor="middle" font-size="11.5" fill="#43474f">experts' rank</text><text x="12" y="${H/2-20}" font-size="11.5" fill="#43474f" transform="rotate(-90 12 ${H/2-20})" dy="4" text-anchor="middle">my model's rank</text>`;
  scored.forEach(r => { s += `<circle cx="${X(r.cons_rank)}" cy="${Y(r.model_rank)}" r="5.5" fill="${AC[r.archetype]}" fill-opacity="${r.sample==='solid'?0.95:0.7}"><title>${esc(r.player)}: experts ${r.cons_rank}, model ${r.model_rank}</title></circle>`; if (r.flag) { const right = X(r.cons_rank) > W - 120; s += `<text x="${X(r.cons_rank) + (right ? -8 : 8)}" y="${Y(r.model_rank)+4}" text-anchor="${right ? 'end' : 'start'}" font-size="11" font-weight="600" fill="#1d1f23">${esc(r.player)}</text>`; } });
  $('#c_sc').innerHTML = s + '</svg>'; })();
// donut archetype mix
(() => { const cnt = {}; scored.forEach(r => cnt[r.archetype] = (cnt[r.archetype]||0)+1); const tot = scored.length, K = Object.keys(AC); let a0 = -Math.PI/2, s = `<svg viewBox="0 0 520 240" role="img" aria-label="Archetype mix">`, cx = 130, cy = 120, R = 95, r = 58;
  K.forEach(k => { const v = cnt[k]||0, a1 = a0 + v/tot*2*Math.PI, big = a1-a0 > Math.PI ? 1 : 0, p = (rr,a) => `${cx+rr*Math.cos(a)},${cy+rr*Math.sin(a)}`; s += `<path d="M${p(R,a0)} A${R} ${R} 0 ${big} 1 ${p(R,a1)} L${p(r,a1)} A${r} ${r} 0 ${big} 0 ${p(r,a0)}Z" fill="${AC[k]}"/>`; a0 = a1; });
  s += `<text x="${cx}" y="${cy-2}" text-anchor="middle" font-size="26" font-weight="700" fill="#1d1f23">${tot}</text><text x="${cx}" y="${cy+18}" text-anchor="middle" font-size="11.5" fill="#767b84">prospects</text>`;
  K.forEach((k,i) => { const y = 50 + i*34; s += `<rect x="270" y="${y}" width="14" height="14" rx="3" fill="${AC[k]}"/><text x="292" y="${y+12}" font-size="14" font-weight="600" fill="#1d1f23">${k}</text><text x="500" y="${y+12}" text-anchor="end" font-size="14" font-weight="700" fill="#1d1f23">${cnt[k]||0}</text>`; });
  $('#c_pie').innerHTML = s + '</svg>'; })();
// board table with filter + sort
let filt = 'All', sortK = 'cons_rank', sortD = 1;
$('#chips').innerHTML = ['All', ...Object.keys(AC), 'Flags only'].map(k => `<button class="chip" data-k="${k}" aria-pressed="${k==='All'}">${k}</button>`).join('');
document.querySelectorAll('.chip').forEach(b => b.onclick = () => { filt = b.dataset.k; document.querySelectorAll('.chip').forEach(x => x.setAttribute('aria-pressed', x === b)); drawBoard(); });
function drawBoard(){ const cols = [['cons_rank','Experts'],['player','Player'],['archetype','Archetype'],['model_rank','Model (gap)'],['glue_pct','Glue'],['flag','Flag']];
  let rows = B.filter(r => filt === 'All' || (filt === 'Flags only' ? r.flag : r.archetype === filt)); rows = [...rows].sort((a,b) => { const x = a[sortK], y = b[sortK]; if (x == null) return 1; if (y == null) return -1; return (typeof x === 'string' ? x.localeCompare(y) : x - y) * sortD; });
  $('#board').innerHTML = '<thead><tr>' + cols.map(([k,h]) => `<th data-k="${k}" class="${k==='glue_pct'?'glc':''}">${h}${sortK===k?(sortD>0?' ↑':' ↓'):''}</th>`).join('') + '</tr></thead><tbody>' + rows.map(r => `<tr><td><b>${r.cons_rank}</b></td><td class="pn"><span class="pw">${face('mens-college-basketball', r.athlete_id ? String(Math.trunc(r.athlete_id)) : '', r.player)}<span>${esc(r.player)}<small>${esc(r.team||'International')}${r.cls?' · '+esc(r.cls):''}</small></span></span></td>
   <td>${r.archetype ? `<span class="ab ${r.sample==='solid'?'':'e'}" style="background:${AC[r.archetype]}">${r.archetype}</span>${r.read==='lean'?'<small class="lean">lean</small>':''}` : `<small style="color:var(--ink3)">${esc(r.status === 'college' ? '' : r.status || '')}</small>`}</td>
   <td>${r.model_rank??''} ${r.gap!=null?`<span class="gp ${r.gap>=5?'up':r.gap<=-5?'dn':''}">(${r.gap>0?'+':''}${r.gap})</span>`:''}</td>
   <td class="glc">${r.glue_pct!=null?`<span class="gl"><i style="width:${r.glue_pct*0.5}px"></i>${r.glue_pct}</span>`:''}</td>
   <td>${r.flag==='sleeper'?'<span class="fl s">Sleeper watch</span>':r.flag==='caution'?'<span class="fl c">Caution</span>':''}</td></tr>`).join('') + '</tbody>';
  document.querySelectorAll('#board th').forEach(th => th.onclick = () => { const k = th.dataset.k; sortD = sortK === k ? -sortD : 1; sortK = k; drawBoard(); }); }
drawBoard();
// watch list cards
$('#watch').innerHTML = B.filter(r => r.flag).sort((a,b) => (a.flag > b.flag ? -1 : 1) || a.cons_rank - b.cons_rank).map(r => `<div class="card ${r.flag==='caution'?'c':''}"><span class="fl ${r.flag==='caution'?'c':'s'}">${r.flag==='caution'?'Caution':'Sleeper watch'}</span><div style="margin-top:8px;display:flex;gap:10px;align-items:center">${face('mens-college-basketball', r.athlete_id ? String(Math.trunc(r.athlete_id)) : '', r.player)}<b>${esc(r.player)}</b></div><div class="m">${esc(r.team)} · ${esc(r.cls)} · ${r.archetype} · ${r.games_now} games</div>
  <p>${r.flag==='caution' ? `Experts No. ${r.cons_rank}. Volume Shooters have beaten their draft slot in only 2 of 9 classes.` : `Experts No. ${r.cons_rank}, my model No. ${r.model_rank}. Glue score ${r.glue_pct}: the stuff that carries over to the NBA.`}</p></div>`).join('');
$('#calls').innerHTML = D.calls.length ? D.calls.map(c => `${c.date}: ${esc(c.player)} (${c.call})`).join('<br>') : `<b>Official calls: none yet.</b> The first ones lock when these players reach 8 games (early December), and each one is graded at the draft and again after his rookie year.`;
// awards
$('#awd').innerHTML = `Ranked by impact on a winner: Game Score per game plus how well his team is doing, among players with 20+ minutes a game. Very early (median team: ${D.awards.median_games} games), so expect big moves until mid-December.`;
const li = (a,i) => `<li><span class="r">${i+1}</span><span><b>${esc(a.name)}</b> <small>${esc(a.team)} (${a.record}) · ${a.ppg} ppg, ${a.rpg} reb, ${a.apg} ast</small></span></li>`;
$('#poy').innerHTML = D.awards.poy.map(li).join(''); $('#fy').innerHTML = D.awards.fy.map(li).join('');
// rookies
const RK = D.rookies, Q = RK.filter(r => r.gp >= 3), hs = id => face('nba', id, (D.rookies.find(r => r.aid === id) || {}).name);
$('#rkd').innerHTML = `Every college player from last June's draft, with his college line next to his NBA line (data through ${D.nba_through}). ${Q.length} of ${RK.length} have played 3+ games. "Vs. slot" = his production rank among rookies minus his draft rank: + means he's outplaying where he was picked.`;
const card = (r, dn) => `<div class="rc ${dn?'dn':''}"><div class="top">${hs(r.aid)}<div><b style="font:700 17px var(--f-serif)">${esc(r.name)}</b><div class="m" style="font:500 12px var(--f-ui);color:var(--ink3)">Pick ${r.pick} · ${esc(r.team||'')} · <span style="color:${AC[r.archetype]};font-weight:700">${r.archetype}</span></div></div><span class="gp ${dn?'dn':'up'}" style="margin-left:auto;font:700 18px var(--f-ui)">${r.vs_slot>0?'+':''}${r.vs_slot}</span></div>
  <div class="ln"><span>College</span><span>${esc(r.college)}: ${r.c_ppg} ppg · ${r.c_reb40} reb/40 · ${r.c_ast40} ast/40</span><span>NBA</span><span>${r.ppg} ppg · ${r.rpg} reb · ${r.apg} ast in ${r.mpg} min · TS ${r.ts!=null?(r.ts*100).toFixed(1)+'%':'—'}</span></div></div>`;
const up = [...Q].sort((a,b) => b.vs_slot - a.vs_slot || b.gs_g - a.gs_g).slice(0,3), dn = [...Q].sort((a,b) => a.vs_slot - b.vs_slot).slice(0,3);
$('#rkcards').innerHTML = up.map(r => card(r,false)).join('') + dn.map(r => card(r,true)).join('');
// translation small multiples
(() => { const T = Q.filter(r => r.mpg >= 10), pairs = [['Rebounds','c_reb40','n_reb36'],['Assists','c_ast40','n_ast36'],['Steals + blocks','c_stk40','n_stk36']], W = 560, pw = 170, ph = 150;
  const corr = (a,b) => { const n = a.length, ma = a.reduce((x,y)=>x+y,0)/n, mb = b.reduce((x,y)=>x+y,0)/n; let sab=0,sa=0,sb=0; for (let i=0;i<n;i++){sab+=(a[i]-ma)*(b[i]-mb);sa+=(a[i]-ma)**2;sb+=(b[i]-mb)**2;} return sab/Math.sqrt(sa*sb); };
  let s = `<svg viewBox="0 0 ${W} ${ph+46}" role="img" aria-label="College vs NBA rates for rookies">`;
  pairs.forEach(([lab,cx,nx],k) => { const ox = k*(pw+18)+6, xs = T.map(r => r[cx]), ys = T.map(r => r[nx]), mx = Math.max(...xs,...ys)*1.05, X = v => ox + v/mx*pw, Y = v => 20 + ph - v/mx*ph, r_ = corr(xs,ys);
    s += `<rect x="${ox}" y="20" width="${pw}" height="${ph}" fill="#faf7f0" stroke="#e6e0d4"/><line x1="${X(0)}" y1="${Y(0)}" x2="${X(mx)}" y2="${Y(mx)}" stroke="#d2c9b8" stroke-dasharray="4 4"/><text x="${ox}" y="13" font-size="13" font-weight="700" fill="#1d1f23">${lab}</text><text x="${ox+pw}" y="13" text-anchor="end" font-size="12.5" font-weight="700" fill="#a8791c">r = ${r_.toFixed(2)}</text>`;
    T.forEach(r => s += `<circle cx="${X(r[cx])}" cy="${Y(r[nx])}" r="4" fill="${AC[r.archetype]}" fill-opacity=".8"><title>${esc(r.name)}: college ${r[cx]}, NBA ${r[nx]}</title></circle>`);
    s += `<text x="${ox+pw/2}" y="${ph+36}" text-anchor="middle" font-size="11" fill="#767b84">college per 40 → NBA per 36</text>`; });
  $('#c_tr').innerHTML = s + '</svg>'; })();
// archetype vs slot (2026 class)
(() => { const g = {}; Q.forEach(r => (g[r.archetype] = g[r.archetype] || []).push(r.vs_slot));
  $('#c26cap').innerHTML = `Average "vs. slot" for the ${Q.length} rookies with 3+ games. Early, but it lines up with the backbone so far.`;
  const A = Object.keys(AC).map(k => [k, g[k] ? g[k].reduce((a,b)=>a+b,0)/g[k].length : 0, (g[k]||[]).length]).sort((a,b) => b[1]-a[1]);
  const W = 520, rh = 40, H = A.length*rh + 10, c = 300, mx = Math.max(...A.map(a => Math.abs(a[1])), 1), sc = v => v/mx*150; let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="2026 rookies vs slot by archetype"><line x1="${c}" x2="${c}" y1="0" y2="${H}" stroke="#d2c9b8"/>`;
  A.forEach(([k,v,n],i) => { const y = i*rh + 6, upv = v >= 0, w = Math.abs(sc(v)), x0 = upv ? c : c - w; s += `<text x="0" y="${y+18}" font-size="13.5" font-weight="600" fill="#1d1f23">${k}</text><text x="0" y="${y+32}" font-size="11" fill="#767b84">${n} rookies</text><rect x="${x0}" y="${y+6}" width="${w}" height="18" rx="4" fill="${AC[k]}"/><text x="${upv?x0+w+6:x0-6}" y="${y+20}" text-anchor="${upv?'start':'end'}" font-size="12.5" font-weight="700" fill="${AC[k]}">${v>0?'+':''}${v.toFixed(1)}</text>`; });
  $('#c_26').innerHTML = s + '</svg>'; })();
// rookie table
let rf = 'All', rsk = 'pick', rsd = 1;
$('#rchips').innerHTML = ['All', ...Object.keys(AC)].map(k => `<button class="chip" data-k="${k}" aria-pressed="${k==='All'}">${k}</button>`).join('');
document.querySelectorAll('#rchips .chip').forEach(b => b.onclick = () => { rf = b.dataset.k; document.querySelectorAll('#rchips .chip').forEach(x => x.setAttribute('aria-pressed', x === b)); drawRk(); });
function drawRk(){ const cols = [['pick','Pick'],['name','Rookie'],['archetype','Archetype'],['c_ppg','College ppg'],['gp','GP'],['mpg','MPG'],['ppg','PPG'],['gs_g','GmSc/g'],['vs_slot','Vs. slot']];
  let rows = RK.filter(r => rf === 'All' || r.archetype === rf); rows = [...rows].sort((a,b) => { const x = a[rsk], y = b[rsk]; if (x == null) return 1; if (y == null) return -1; return (typeof x === 'string' ? x.localeCompare(y) : x - y) * rsd; });
  $('#rtab').innerHTML = '<thead><tr>' + cols.map(([k,h]) => `<th data-k="${k}">${h}${rsk===k?(rsd>0?' ↑':' ↓'):''}</th>`).join('') + '</tr></thead><tbody>' + rows.map(r => `<tr><td><b>${r.pick}</b></td><td class="pn"><span class="pw">${face('nba', r.aid, r.name)}<span>${esc(r.name)}<small>${esc(r.college)} → ${esc(r.team||'not in NBA yet')}</small></span></span></td><td><span class="ab" style="background:${AC[r.archetype]}">${r.archetype}</span></td><td>${r.c_ppg}</td><td>${r.gp||0}</td><td>${r.mpg??''}</td><td>${r.ppg??''}</td><td><b>${r.gs_g??''}</b></td><td>${r.vs_slot!=null?`<span class="gp ${r.vs_slot>=3?'up':r.vs_slot<=-3?'dn':''}">${r.vs_slot>0?'+':''}${r.vs_slot}</span>`:''}</td></tr>`).join('') + '</tbody>';
  document.querySelectorAll('#rtab th').forEach(th => th.onclick = () => { const k = th.dataset.k; rsd = rsk === k ? -rsd : (['pick','name','archetype'].includes(k) ? 1 : -1); rsk = k; drawRk(); }); }
drawRk();
// sophomores
(() => { const S2 = D.sophomores.filter(r => r.gp >= 3).sort((a,b) => b.gs_g - a.gs_g).slice(0,10);
  $('#stab').innerHTML = '<thead><tr><th>Pick</th><th>Player</th><th>Archetype</th><th>GP</th><th>MPG</th><th>PPG</th><th>RPG</th><th>APG</th><th>GmSc/g</th><th>Vs. slot</th></tr></thead><tbody>' + S2.map(r => `<tr><td><b>${r.pick}</b></td><td class="pn"><span class="pw">${face('nba', r.aid, r.name)}<span>${esc(r.name)}<small>${esc(r.college)} → ${esc(r.team)}</small></span></span></td><td><span class="ab" style="background:${AC[r.archetype]}">${r.archetype}</span></td><td>${r.gp}</td><td>${r.mpg}</td><td>${r.ppg}</td><td>${r.rpg}</td><td>${r.apg}</td><td><b>${r.gs_g}</b></td><td><span class="gp ${r.vs_slot>=3?'up':r.vs_slot<=-3?'dn':''}">${r.vs_slot>0?'+':''}${r.vs_slot}</span></td></tr>`).join('') + '</tbody>'; })();
// stacked bars: class x round -> role
(() => { const roles = ['Starter','Rotation','Bench','Out / G League'], col = {'Starter':'#1f4e8c','Rotation':'#5b84bf','Bench':'#c9bfa8','Out / G League':'#b23a3a'};
  const keys = []; [2023,2024,2025].forEach(c => [1,2].forEach(r => keys.push([c,r]))); const W = 520, rh = 38, H = keys.length*rh + 6; let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Role by draft class and round">`;
  keys.forEach(([c,r],i) => { const rs = roles.map(ro => (D.flows.find(f => f.class===c && f.round===r && f.role===ro)||{n:0}).n), tot = rs.reduce((a,b)=>a+b,0); let x = 150; const y = i*rh + 4;
    s += `<text x="0" y="${y+16}" font-size="13" font-weight="700" fill="#1d1f23">${c} class</text><text x="0" y="${y+30}" font-size="11" fill="#767b84">Round ${r} · year ${2026-c}</text>`;
    rs.forEach((n,j) => { const w = n/tot*360; if (w > 0) { s += `<rect x="${x}" y="${y+6}" width="${w}" height="22" fill="${col[roles[j]]}"/>`; if (w > 18) s += `<text x="${x+w/2}" y="${y+21}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${j===2?'#1d1f23':'#fff'}">${n}</text>`; } x += w; }); });
  $('#c_flow').innerHTML = s + '</svg>'; $('#flk').innerHTML = roles.map(r => `<span><i style="background:${col[r]}"></i>${r}</span>`).join(''); })();
</script></body></html>"""
pathlib.Path(sys.argv[3]).write_text(html); print(len(html))
