#!/usr/bin/env node
'use strict';
/*
  Newsletter Archive builder (v1, draft).

  node scripts/build_archive.js                      section pages, archive home, videos, archive-index.json,
                                                     and the "Previous … → · Newsletter Archive →" strip on detail pages
  node scripts/build_archive.js --issues-from DIR    also writes pages/archive/issues/<date>.html from the sent
                                                     newsletter HTML at DIR/<issues[].nas minus "02-Issues/">
                                                     (NAS layout <YYYY-MM>/<send date>/sent-final/<file>), falling back
                                                     to DIR/<date>/<basename>.
                                                     Issue pages are written ONCE; existing ones are never overwritten
                                                     (Handbook 17) unless --force-issues is given.
  node scripts/build_archive.js --check              exits 1 if anything would change (CI use)

  Input:  archive/archive-items.json (hand-curated; not published)
  Rules:  item pages keep their permanent URLs (Handbook 8). The detail-page strip is appended between
          <!-- ph-archive-nav:start --> / <!-- ph-archive-nav:end --> markers just before </body>;
          nothing else in those pages changes. Hidden pages stay live and are simply not listed.
          A section with "strip_listen": true also gets the strip on its items' listen pages.
          Item options: "also": [{page,label}] extra pages listed on the row (e.g. Original notice) and given the
          strip; "strip_extra": [page] pages that get the strip but are not listed (e.g. Zoom pages);
          "strip_as": "<section>" gives the item's page that section's strip instead (video guide -> Previous Videos).
          Section option "feature_latest": true leads the section page with the newest item (feature_label / feature_read /
          feature_rest set the wording). Item options "date_label" (shown instead of the weekday date, e.g. a Link month)
          and "summary" (one-line teaser). Section option "plain_rows": true hides the
          grey "Source: …" and "In the newsletter: …" lines on that section page (Community Stories).
          Archive nav (v2, one bar for every section): a single light bar at the TOP of the page only, right under
          the page's first <header> (right after <body> if it has none), dark text, 18px:
          "Previous <Section> → · Newsletter Archive →". Detail/listen pages carry it between
          <!-- ph-archive-nav:start --> / <!-- ph-archive-nav:end -->; older footer strips and
          <!-- ph-archive-nav-top --> header strips are removed on rebuild. Section pages get the same bar under
          the banner (feature_latest sections: "Previous … ↓" jumps to the list). "header_nav" is no longer used.
*/
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const PAGES = path.join(ROOT, 'pages');
const OUT = path.join(PAGES, 'archive');
const ITEMS = JSON.parse(fs.readFileSync(path.join(ROOT, 'archive', 'archive-items.json'), 'utf8'));
const BASE = ITEMS.base_url.replace(/\/$/, '');
const args = process.argv.slice(2);
const argVal = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const CHECK = args.includes('--check');
if (args.includes('--help') || args.includes('-h')) {
  console.log(`Usage: node scripts/build_archive.js [--issues-from DIR] [--force-issues] [--check]

Inputs:   archive/archive-items.json        curated issues, section items, hidden pages, video list
          pages/*.html                      existing detail pages (must exist; never renamed)
          DIR/<issues[].nas minus 02-Issues/>  (--issues-from) sent newsletter HTML, NAS 02-Issues layout
                                            (<YYYY-MM>/<send date>/sent-final/<file>); fallback DIR/<date>/<basename>
Outputs:  pages/archive/index.html (PHNL issues only), pages/archive/main.html (Main Archive Page), pages/archive/<section>.html (10), pages/archive/archive-index.json,
          pages/archive/issues/<date>.html (only with --issues-from; written once),
          marked nav strip in each listed detail page
Exit:     0 ok; 1 with --check if anything is out of date; non-zero on any missing page/source
See archive/RUNBOOK-archive.md.`);
  process.exit(0);
}
const changed = [];

const SECTION_ORDER = ['community-stories', 'presidents-message', 'meetings', 'committee-reports', 'manager-reports', 'weekly-manager-updates', 'events', 'community-notices', 'did-you-know', 'videos'];
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
// L21 code policy (Steven, Oct 9, 2026): every user-visible month is three letters (Jan … Dec), phones especially.
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
function d(iso) { const [y, m, dd] = iso.slice(0, 10).split('-').map(Number); return new Date(Date.UTC(y, m - 1, dd)); }
const longDate = (iso) => { const x = d(iso); return `${DAYS[x.getUTCDay()]}, ${MONTHS[x.getUTCMonth()]} ${x.getUTCDate()}, ${x.getUTCFullYear()}`; };
const midDate = (iso) => { const x = d(iso); return `${MONTHS[x.getUTCMonth()]} ${x.getUTCDate()}, ${x.getUTCFullYear()}`; };
// Every listed item shows a full date. Link items (date_label, month-only issues) show "Mon D, YYYY" from their
// date field (1st of the issue month unless a real day is known) without a weekday.
const fullDate = (it) => (it.date_label ? midDate(it.date) : longDate(it.date));
const shortDate = (iso) => { const x = d(iso); return `${MONTHS[x.getUTCMonth()].slice(0, 3)} ${x.getUTCDate()}`; };
const etParts = (iso) => Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }).formatToParts(new Date(iso)).map((p) => [p.type, p.value]));
const fileDated = (iso) => { const p = etParts(iso); return `${p.month} ${p.day}, ${p.year} ${p.hour}:${p.minute} ${p.dayPeriod}`; };
const sentTimeET = (iso) => new Date(iso).toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour: 'numeric', minute: '2-digit' });
const issueLabel = (iss) => iss.label || `Week of ${midDate(iss.date)}`;
// ---------- issue numbering: "Vol. V, No. N" ----------
// Vol. 1, No. 1 = first resident issue (numbering.first_issue). Each sent issue is the next No.; the volume goes up on
// every numbering.volume_anniversary (MM-DD) and No. restarts at 1. Stored issues[].volume/number are checked against
// this rule (missing values are filled in). Same rule as phnews pipeline/scripts/issue_number.py.
const NUMBERING = ITEMS.numbering || { first_issue: '2026-07-21', volume_anniversary: '07-21' };
const volYear = (iso) => Number(iso.slice(0, 4)) + (iso.slice(5, 10) >= NUMBERING.volume_anniversary ? 1 : 0);
const volumeOf = (iso) => {
  const v = volYear(iso) - volYear(NUMBERING.first_issue) + 1;
  if (v < 1) throw new Error(`${iso}: before the first issue ${NUMBERING.first_issue}`);
  return v;
};
{
  const asc = [...ITEMS.issues].sort((a, b) => a.date.localeCompare(b.date));
  if (asc.length && asc[0].date !== NUMBERING.first_issue) throw new Error(`first issue is ${asc[0].date}, numbering.first_issue is ${NUMBERING.first_issue}`);
  let vol = 0; let no = 0;
  for (const iss of asc) {
    const v = volumeOf(iss.date);
    if (v !== vol) { vol = v; no = 0; }
    no++;
    if (iss.volume == null) iss.volume = v;
    if (iss.number == null) iss.number = no;
    if (iss.volume !== v || iss.number !== no) throw new Error(`${iss.date}: archive-items.json says Vol. ${iss.volume}, No. ${iss.number}; the numbering rule gives Vol. ${v}, No. ${no}`);
  }
}
const volNo = (iss) => `Vol. ${iss.volume}, No. ${iss.number}`;
const monthKey = (iso) => { const x = d(iso); return `${MONTHS[x.getUTCMonth()]} ${x.getUTCFullYear()}`; };
const pageUrl = (p) => `${BASE}/pages/${p}`;
const archUrl = (p) => `${BASE}/pages/archive/${p}`;
const pageExists = (p) => fs.existsSync(path.join(PAGES, p));

function write(file, content) {
  const prev = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : null;
  if (prev === content) return;
  changed.push(path.relative(ROOT, file));
  if (!CHECK) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, content); }
}

function shell({ title, issuedate, body, canonical, topNav }) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>${esc(title)} — Palm Hill Country Club</title>
${canonical ? `<link rel="canonical" href="${canonical}">\n` : ''}<link rel="stylesheet" href="/pages/assets/ph-newsletter.css">
</head>
<body>
<!-- Generated by scripts/build_archive.js from archive/archive-items.json. Edit the data, not this file. -->
<div class="ph-page">
<header class="ph-banner">
  <div class="ph-masthead">
    <img class="ph-palm" src="/pages/assets/masthead-palm.png" alt="" width="74" height="77">
    <div class="ph-masthead-text">
      <div class="ph-wordmark">Palm Hill Country Club</div>
      <div class="ph-issuedate">${esc(issuedate)}</div>
    </div>
    <img class="ph-palm" src="/pages/assets/masthead-palm.png" alt="" width="74" height="77">
  </div>
  <p class="ph-tagline ph-address-strip" style="padding:8px 12px;font:15px/1.4 Arial,Helvetica,sans-serif;font-style:normal"><a href="https://www.google.com/maps/search/1800+Seminole+Blvd,+Largo,+FL+33778" style="color:#ffffff;text-decoration:underline">1800 Seminole Blvd, Largo, FL 33778</a></p>
</header>
${topNav ? topNav + '\n' : ''}<main class="ph-body">
${body}
</main>
</div>
</body>
</html>
`;
}

const S = ITEMS.sections;
const hidden = new Set(ITEMS.hidden || []);
for (const [k, sec] of Object.entries(S)) for (const it of sec.items) {
  if (it.page && hidden.has(it.page)) throw new Error(`${k}: ${it.page} is in hidden[]`);
  if (it.page && !pageExists(it.page)) throw new Error(`${k}: missing page ${it.page}`);
  if (it.listen && !pageExists(it.listen)) throw new Error(`${k}: missing listen page ${it.listen}`);
  for (const a of it.also || []) if (!pageExists(a.page)) throw new Error(`${k}: missing page ${a.page}`);
  for (const p of it.strip_extra || []) if (!pageExists(p)) throw new Error(`${k}: missing page ${p}`);
  if (it.strip_as && !S[it.strip_as]) throw new Error(`${k}: strip_as names unknown section ${it.strip_as}`);
}
for (const k of SECTION_ORDER) if (!S[k]) throw new Error(`archive-items.json has no section ${k}`);
if (S['manager-reports'].title !== 'Monthly Shareholders Reports') throw new Error('manager-reports must be titled Monthly Shareholders Reports (Steven, Oct 9)');
for (const it of S['manager-reports'].items) if (/weekly/i.test(it.title || '')) throw new Error(`manager-reports (monthly) lists a weekly item: ${it.title}`);
for (const it of S['weekly-manager-updates'].items) if (!/weekly/i.test(it.title || '')) throw new Error(`weekly-manager-updates lists a non-weekly item: ${it.title}`);
const sorted = (k) => [...S[k].items].sort((a, b) => (b.date || '').localeCompare(a.date || ''));
const issueDates = ITEMS.issues.map((i) => i.date).sort().reverse();
const issueLink = (date) => ITEMS.issues.some((i) => i.date === date) ? `<a href="issues/${date}.html">${shortDate(date)}</a>` : shortDate(date);
// Steven, Oct 9: pages/archive/index.html is the PHNL issues page ONLY. pages/archive/main.html is the Main Archive
// Page (every archive, issues included). Section pages and detail strips go up to the Main Archive Page.
const HUB = 'main.html';
const HUB_LABEL = 'All Archives →';
const crumbs = (title) => `<p class="ph-crumbs"><a href="${HUB}">Palm Hill Archives</a> › ${esc(title)}</p>`;

// ---------- shared archive nav bar (top of page only) ----------
// Fully inline styles so each page's own nav/a rules cannot restyle it. Large, dark, high-contrast for older eyes.
function navBar(links) {
  const A = 'display:inline-block;background:none;border:0;border-radius:0;box-shadow:none;padding:4px 2px;margin:0;color:#1d4310;font:bold 18px/1.5 Arial,Helvetica,sans-serif;text-decoration:underline;text-underline-offset:3px;letter-spacing:0;text-transform:none';
  const body = links.map(([href, label]) => `<a href="${href}" style="${A}">${esc(label)}</a>`).join('<span class="ph-sep" style="color:#1a1a1a;font:bold 18px/1.5 Arial,Helvetica,sans-serif;padding:0 6px" aria-hidden="true">·</span>');
  // On phones the two links stack, one per line, and the dot drops out (no dangling "·" at a line end).
  const css = '<style>@media (max-width:480px){.ph-archive-bar .ph-sep{display:none!important}.ph-archive-bar a{display:block!important;margin:0 auto!important;width:max-content}}</style>';
  return `<div class="ph-archive-bar" role="navigation" aria-label="Newsletter archive" style="display:block;width:100%;margin:0;padding:10px 14px;box-sizing:border-box;background:#f3f8ee;border:0;border-bottom:2px solid #2d5016;color:#1a1a1a;font:18px/1.5 Arial,Helvetica,sans-serif;text-align:center;letter-spacing:0;text-transform:none">${css}${body}</div>`;
}

// ---------- section pages ----------
function sectionPage(k) {
  const sec = S[k];
  let out = `${crumbs(sec.title)}\n<h1 class="ph-section">${esc(sec.title)}</h1>\n<p class="ph-lead">${esc(sec.lead)}</p>\n`;
  let month = null; let n = 0;
  let rows = sorted(k);
  // "feature_latest": the newest item leads the page as the current one; the rest list below as previous items.
  if (sec.feature_latest && rows.length) {
    const top = rows[0]; rows = rows.slice(1);
    const when = fullDate(top);
    const links = [top.page ? `<a href="${pageUrl(top.page)}">${esc(sec.feature_read || 'Read →')}</a>` : null, top.listen ? `<a href="${pageUrl(top.listen)}">Listen →</a>` : null].filter(Boolean).join('<span class="ph-dot"> · </span>');
    out += `<section class="ph-feature" aria-label="${esc(sec.feature_label || 'Latest')}">\n<p class="ph-feature-kicker">${esc(sec.feature_label || 'Latest')}</p>\n`;
    out += `<h2 class="ph-feature-title">${top.page ? `<a href="${pageUrl(top.page)}">${esc(top.title)}</a>` : esc(top.title)}</h2>\n`;
    out += `<div class="ph-row-meta">${[top.byline ? esc(top.byline) : null, when].filter(Boolean).join(' · ')}</div>\n`;
    if (top.summary) out += `<p class="ph-detail">${esc(top.summary)}</p>\n`;
    if (links) out += `<nav class="ph-links">${links}</nav>\n`;
    if (top.source && !sec.plain_rows) out += `<div class="ph-row-meta">Source: ${esc(top.source)}</div>\n`;
    if (!sec.plain_rows && top.issues && top.issues.length) out += `<div class="ph-row-meta">In the newsletter: ${top.issues.slice().sort().map(issueLink).join(', ')}</div>\n`;
    out += `</section>\n`;
    if (rows.length) out += `<h2 class="ph-subhead ph-prev-head" id="previous">${esc(sec.feature_rest || 'Previous')}</h2>\n`;
  }
  for (const it of rows) {
    const m = monthKey(it.date);
    if (m !== month) { out += `<h2 class="ph-subhead">${m}</h2>\n`; month = m; }
    const id = it.id ? ` id="${esc(it.id)}"` : '';
    const head = it.page
      ? `<a class="ph-row-title" href="${pageUrl(it.page)}">${esc(it.title)} →</a>`
      : `<span class="ph-row-title">${esc(it.title)}</span>`;
    const meta = [fullDate(it), it.byline ? esc(it.byline) : null, it.listen ? `<a href="${pageUrl(it.listen)}">Listen →</a>` : null, ...(it.also || []).map((a) => `<a href="${pageUrl(a.page)}">${esc(a.label)}</a>`)].filter(Boolean).join(' · ');
    out += `<div class="ph-row${n % 2 ? ' ph-alt' : ''}"${id}>${head}\n<div class="ph-row-meta">${meta}</div>\n`;
    if (it.text) out += `<div class="ph-detail">${esc(it.text)}</div>\n`;
    if (it.summary) out += `<div class="ph-detail">${esc(it.summary)}</div>\n`;
    if (it.external) out += `<nav class="ph-links"><a href="${esc(it.external)}">${esc(it.external_label || 'Open →')}</a></nav>\n`;
    if (it.source && !sec.plain_rows) out += `<div class="ph-row-meta">Source: ${esc(it.source)}</div>\n`;
    if (!sec.plain_rows && it.issues && it.issues.length) out += `<div class="ph-row-meta">In the newsletter: ${it.issues.slice().sort().map(issueLink).join(', ')}</div>\n`;
    out += `</div>\n`;
    n++;
  }
  const hasPrev = sec.feature_latest && sorted(k).length > 1;
  const topNav = navBar([hasPrev ? ['#previous', `${sec.prev.replace(/\s*→$/, '')} ↓`] : null, [HUB, HUB_LABEL]].filter(Boolean));
  return shell({ title: `${sec.title} — Newsletter Archive`, issuedate: 'Newsletter Archives', body: out, canonical: archUrl(`${k}.html`), topNav });
}

function videosPage() {
  const sec = S.videos;
  const dyk = S['did-you-know'].items.filter((x) => x.external);
  let out = `${crumbs('Meeting Videos')}\n<h1 class="ph-section">Board &amp; Committee Meeting Videos</h1>\n<p class="ph-lead">${esc(sec.lead)}</p>\n<h2 class="ph-subhead">Recordings, newest first</h2>\n`;
  [...sec.items].sort((a, b) => b.date.localeCompare(a.date)).forEach((v, n) => {
    out += `<div class="ph-video${n % 2 ? ' ph-alt' : ''}"><a class="ph-play" href="${esc(v.url)}" aria-label="Play the ${esc(v.group)} recording from ${midDate(v.date)}">▶</a><div><div class="ph-row-title"><a href="${esc(v.url)}">${esc(v.group)}</a></div><div class="ph-row-meta">${longDate(v.date)}</div></div></div>\n`;
  });
  out += `<h2 class="ph-subhead">How-To Videos</h2>\n`;
  dyk.forEach((x, n) => {
    out += `<div class="ph-video${n % 2 ? ' ph-alt' : ''}"><a class="ph-play" href="${esc(x.external)}" aria-label="Play: ${esc(x.title)}">▶</a><div><div class="ph-row-title"><a href="${esc(x.external)}">${esc(x.title)}</a></div><div class="ph-row-meta">Tutorial video</div></div></div>\n`;
  });
  out += `<nav class="ph-links"><a href="https://www.palmhillcountryclub.net/committees/">All recordings on the Palm Hill website (sign-in required) →</a></nav>\n`;
  out += `<p class="ph-source">Source: ${esc(sec.snapshot)}. Recordings open in Google Drive.</p>\n`;
  const topNav = navBar([[pageUrl('2026-10-04-committee-video-guide.html'), 'How to Find Videos →'], [HUB, HUB_LABEL]]);
  return shell({ title: 'Meeting Videos — Newsletter Archive', issuedate: 'Newsletter Archives', body: out, canonical: archUrl('videos.html'), topNav });
}

// ---------- PHNL issues page + Main Archive Page (Steven, Oct 9) ----------
// No masthead, no main-PHNL footer: a quiet green title band, then the content. Three-letter months (L21).
const PA_CSS = `<style id="ph-archive-pride">
.pa-page{max-width:660px;margin:0 auto;background:#fff;color:#2b2b2b;font:17px/1.55 Arial,Helvetica,sans-serif}
.pa-hero{background:#2d5016;color:#fff;text-align:center;padding:26px 18px 22px;border-bottom:4px solid #b9913c}
.pa-hero svg{display:block;margin:0 auto 14px;width:140px;height:auto}
.pa-kicker{margin:0 0 4px;color:#e5d39c;font:bold 13px/1.4 Arial,Helvetica,sans-serif;letter-spacing:.14em;text-transform:uppercase}
.pa-hero h1{margin:0;font:700 clamp(28px,7vw,38px)/1.15 Georgia,'Times New Roman',serif;color:#fff;letter-spacing:.01em}
.pa-sub{margin:8px auto 0;max-width:30em;color:#e9f1df;font:italic 17px/1.45 Georgia,'Times New Roman',serif}
.pa-bar{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:4px 14px;padding:10px 18px;background:#f3f8ee;border-bottom:1px solid #d8dfce;color:#4a5a44;font:15px/1.5 Arial,Helvetica,sans-serif}
.pa-bar a,.pa-quiet a{color:#3a6b1a;text-decoration:underline;text-underline-offset:3px}
.pa-main{padding:18px 18px 8px}
.pa-label{margin:0 0 6px;color:#8b6914;font:bold 13px/1.4 Arial,Helvetica,sans-serif;letter-spacing:.12em;text-transform:uppercase}
.pa-latest{border:1px solid #d8dfce;border-top:4px solid #2d5016;border-radius:6px;padding:16px 18px;margin:0 0 22px;background:#fbfdf8}
.pa-latest h2{margin:2px 0 4px;font:700 26px/1.2 Georgia,'Times New Roman',serif}
.pa-latest h2 a{color:#1d4310;text-decoration:none}
.pa-volno{margin:0;color:#2d5016;font:bold 16px/1.4 Arial,Helvetica,sans-serif}
.pa-meta{margin:2px 0 0;color:#555;font:15px/1.5 Arial,Helvetica,sans-serif}
.pa-in{margin:8px 0 0;color:#555;font:15px/1.5 Arial,Helvetica,sans-serif}
.pa-read{display:inline-block;margin-top:12px;padding:10px 18px;border-radius:4px;background:#2d5016;color:#fff!important;font:bold 17px/1.3 Arial,Helvetica,sans-serif;text-decoration:none}
.pa-month{margin:20px 0 6px;padding:0 0 4px;border-bottom:2px solid #2d5016;color:#2d5016;font:700 19px/1.3 Georgia,'Times New Roman',serif}
.pa-issue{display:flex;align-items:center;gap:14px;padding:12px 4px;border-bottom:1px solid #e3e8dc;color:inherit;text-decoration:none}
.pa-issue:hover,.pa-issue:focus-visible{background:#f3f8ee}
.pa-no{flex:0 0 58px;height:58px;display:flex;flex-direction:column;align-items:center;justify-content:center;border:2px solid #2d5016;border-radius:50%;color:#2d5016;background:#fff;font:700 22px/1 Georgia,'Times New Roman',serif}
.pa-no small{display:block;margin-bottom:2px;font:bold 10px/1 Arial,Helvetica,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#8b6914}
.pa-what{flex:1;min-width:0}
.pa-what b{display:block;color:#1d4310;font:700 19px/1.3 Georgia,'Times New Roman',serif}
.pa-what span{display:block;color:#555;font:15px/1.45 Arial,Helvetica,sans-serif}
.pa-go{flex:0 0 auto;color:#3a6b1a;font:bold 20px/1 Arial,Helvetica,sans-serif}
.pa-note{margin:22px 0 8px;color:#666;font:14px/1.5 Arial,Helvetica,sans-serif}
.pa-quiet{margin:6px 0 22px;text-align:center;color:#666;font:15px/1.5 Arial,Helvetica,sans-serif}
.pa-grid{display:grid;grid-template-columns:1fr;gap:10px;margin:0 0 20px}
@media (min-width:520px){.pa-grid{grid-template-columns:1fr 1fr}}
.pa-tile{display:block;padding:12px 14px;border:1px solid #d8dfce;border-radius:6px;background:#fff;color:inherit;text-decoration:none}
a.pa-tile:hover,a.pa-tile:focus-visible{background:#f3f8ee}
.pa-tile b{display:block;color:#1d4310;font:700 18px/1.3 Georgia,'Times New Roman',serif}
.pa-tile span{display:block;color:#555;font:14px/1.45 Arial,Helvetica,sans-serif}
.pa-tile .pa-tlinks{margin-top:4px;font:bold 15px/1.5 Arial,Helvetica,sans-serif}
.pa-tile .pa-tlinks a{color:#3a6b1a}
.pa-feature{display:flex;align-items:center;gap:16px;margin:0 0 22px;padding:16px 18px;border:1px solid #d8dfce;border-top:4px solid #2d5016;border-radius:6px;background:#fbfdf8;color:inherit;text-decoration:none}
.pa-feature:hover,.pa-feature:focus-visible{background:#f3f8ee}
.pa-feature svg{flex:0 0 64px;width:64px;height:auto}
.pa-feature b{display:block;color:#1d4310;font:700 23px/1.2 Georgia,'Times New Roman',serif}
.pa-feature span{display:block;color:#555;font:15px/1.45 Arial,Helvetica,sans-serif}
@media (max-width:420px){.pa-main{padding:14px 14px 6px}.pa-no{flex-basis:50px;height:50px;font-size:19px}.pa-what b{font-size:18px}}
</style>`;

// Elegant line-art folded newspaper (gold rule work on the green band; not a cartoon).
function newspaperIcon({ stroke = '#f3dfa2', fill = 'none', paper = 'rgba(255,255,255,0.06)', w = 140, label = '' } = {}) {
  return `<svg viewBox="0 0 120 96" width="${w}" ${label ? `role="img" aria-label="${esc(label)}"` : 'aria-hidden="true" focusable="false"'} xmlns="http://www.w3.org/2000/svg">
<g fill="${fill}" stroke="${stroke}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
<path d="M22 10h80a4 4 0 0 1 4 4v66a8 8 0 0 1-8 8H18a8 8 0 0 1-8-8V30h12" fill="${paper}"/>
<path d="M22 10v70a8 8 0 0 1-8 8"/>
<path d="M10 30v50a4 4 0 0 0 8 0"/>
<path d="M32 22h64" stroke-width="3.4"/>
<path d="M32 29h64" stroke-width="1.2"/>
<rect x="32" y="37" width="28" height="22" rx="1.5" stroke-width="1.8"/>
<path d="M36 55l7-8 6 5 4-4 5 7" stroke-width="1.6"/>
<path d="M66 39h30M66 45h30M66 51h30M66 57h22M32 66h64M32 72h64M32 78h44" stroke-width="1.6"/>
</g></svg>`;
}

function prideShell({ title, canonical, hero, body }) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>${esc(title)} — Palm Hill Country Club</title>
<link rel="canonical" href="${canonical}">
<link rel="stylesheet" href="/pages/assets/ph-newsletter.css">
${PA_CSS}
</head>
<body>
<!-- Generated by scripts/build_archive.js from archive/archive-items.json. Edit the data, not this file. -->
<div class="pa-page">
${hero}
${body}
</div>
</body>
</html>
`;
}

const shortWeekday = (iso) => DAYS[d(iso).getUTCDay()];
const editionOf = (iss) => (/pdf/i.test(iss.format || '') ? 'PDF edition' : 'Email edition');
// Section nouns for an issue's "In this issue" line (singular, plural).
const NOUNS = {
  'community-stories': ['Community Story', 'Community Stories'], 'presidents-message': ["President's Message", "President's Messages"],
  meetings: ['Meeting', 'Meetings'], 'committee-reports': ['Chair Report', 'Chair Reports'], 'manager-reports': ['Shareholders Report', 'Shareholders Reports'],
  'weekly-manager-updates': ['Weekly Manager Update', 'Weekly Manager Updates'],
  events: ['Special Event', 'Special Events'], 'community-notices': ['Notice', 'Notices'], 'did-you-know': ['Did You Know?', 'Did You Know?'], videos: ['Video', 'Videos'],
};
function issueContents(iss) {
  const parts = [];
  for (const k of SECTION_ORDER) {
    const c = S[k].items.filter((x) => (x.issues || []).includes(iss.date)).length;
    if (c) parts.push(`${c} ${NOUNS[k][c === 1 ? 0 : 1]}`);
  }
  return parts.join(' · ');
}
const issuesDesc = () => [...ITEMS.issues].sort((a, b) => b.date.localeCompare(a.date));

// pages/archive/index.html — PHNL issues ONLY. Nothing else is listed here; one quiet link up to the Main Archive Page.
function issuesPage() {
  const all = issuesDesc(); const latest = all[0]; const first = all[all.length - 1];
  const hero = `<header class="pa-hero">
${newspaperIcon({ label: 'The Palm Hill Newsletter' })}
<p class="pa-kicker">Palm Hill Country Club</p>
<h1>The Palm Hill Newsletter</h1>
<p class="pa-sub">Every issue we have published for our community, as it was sent.</p>
</header>
<nav class="pa-bar" aria-label="Archive"><span>${all.length} issues · ${shortDate(first.date)} – ${midDate(latest.date)}</span><a href="${HUB}">${esc(HUB_LABEL)}</a></nav>`;
  let body = `<main class="pa-main">
<section class="pa-latest" aria-label="Latest issue">
<p class="pa-label">Latest Issue</p>
<p class="pa-volno">${volNo(latest)}</p>
<h2><a href="issues/${latest.date}.html">${esc(issueLabel(latest))}</a></h2>
<p class="pa-meta">Sent ${longDate(latest.date)} · ${editionOf(latest)}</p>
${issueContents(latest) ? `<p class="pa-in">In this issue: ${esc(issueContents(latest))}</p>\n` : ''}<a class="pa-read" href="issues/${latest.date}.html">Read this issue →</a>
</section>
`;
  let month = null;
  for (const iss of all.slice(1)) {
    const m = monthKey(iss.date);
    if (m !== month) { body += `<h2 class="pa-month">${m}</h2>\n`; month = m; }
    const what = issueContents(iss);
    body += `<a class="pa-issue" href="issues/${iss.date}.html" aria-label="${esc(`${volNo(iss)}, ${issueLabel(iss)}`)}"><span class="pa-no"><small>No.</small>${iss.number}</span><span class="pa-what"><b>${esc(issueLabel(iss))}</b><span>Vol. ${iss.volume} · Sent ${shortWeekday(iss.date)}, ${shortDate(iss.date)} · ${editionOf(iss)}</span>${what ? `<span>${esc(what)}</span>` : ''}</span><span class="pa-go" aria-hidden="true">→</span></a>\n`;
  }
  body += `<p class="pa-note">Volume 1 began ${midDate(first.date)} with our first issue for residents. Each archive copy is the issue as it was sent that week; private meeting links, download links and unsubscribe links are removed. Early issues went out as a PDF from palmhillcountryclub.net.</p>
<p class="pa-quiet">Looking for stories or reports? <a href="${HUB}">${esc(HUB_LABEL)}</a></p>
</main>`;
  return prideShell({ title: 'The Palm Hill Newsletter — Every Issue', canonical: archUrl('index.html'), hero, body });
}

// pages/archive/main.html — Main Archive Page: newsletter archives ONLY, the Newsletter issues first.
// Steven, Oct 9: no Community Notices or Did You Know? tiles, and no Meetings, Events & Activities group
// (Committee & Board Meetings, Special Events, Recurring Activities, Meeting Videos). Those section pages stay
// (detail pages still link "Previous Notices →", "Previous Meetings →" etc.); they are just not listed here.
// Steven, Oct 9: Megan's monthly report (prepared for each Board meeting) is "Monthly Shareholders Reports"
// (section key manager-reports kept so its URL and #anchors stay permanent); her weekly office updates are their own
// section, Weekly Manager Updates. Fail closed if a weekly item lands in the monthly section or vice versa.
const HUB_KEEP = ['community-stories', 'presidents-message', 'committee-reports', 'manager-reports', 'weekly-manager-updates'];
const HUB_EXCLUDE = SECTION_ORDER.filter((k) => !HUB_KEEP.includes(k));
const HUB_GROUPS = [
  ['From the Newsletter', HUB_KEEP],
];
function mainPage() {
  const all = issuesDesc(); const latest = all[0]; const first = all[all.length - 1];
  const tile = (k) => {
    const items = S[k].items; const newest = items.map((x) => x.date).sort().pop();
    return `<a class="pa-tile" href="${k}.html"><b>${esc(S[k].title)} →</b><span>${items.length} item${items.length === 1 ? '' : 's'} · newest ${shortDate(newest)}</span></a>`;
  };
  const hero = `<header class="pa-hero">
<p class="pa-kicker">Palm Hill Country Club</p>
<h1>Palm Hill Archives</h1>
<p class="pa-sub">Everything our newsletter has carried, kept in one place.</p>
</header>`;
  let body = `<main class="pa-main">
<a class="pa-feature" href="index.html">${newspaperIcon({ stroke: '#2d5016', paper: '#ffffff', w: 64 })}<span><b>The Palm Hill Newsletter →</b><span>Every issue · ${volNo(first).replace(/, No\. \d+$/, '')}, No. ${first.number}–${latest.number} · ${shortDate(first.date)} – ${midDate(latest.date)}</span></span></a>
`;
  for (const [label, keys] of HUB_GROUPS) {
    body += `<p class="pa-label">${esc(label)}</p>\n<div class="pa-grid">\n${keys.map(tile).join('\n')}\n</div>\n`;
  }
  body += `</main>`;
  return prideShell({ title: 'Palm Hill Archives', canonical: archUrl(HUB), hero, body });
}
// Fail closed: the issues page lists PHNL issues only (plus the one link up to the Main Archive Page), carries no
// masthead, and every month is three letters (L21).
const FULL_MONTH = /\b(January|February|March|April|June|July|August|September|October|November|December)\b/;
function checkPride(name, html, issuesOnly) {
  if (/ph-masthead|ph-wordmark/.test(html)) throw new Error(`${name}: masthead must not appear`);
  const vis = html.replace(/<style[\s\S]*?<\/style>/g, '').replace(/<[^>]+>/g, ' ');
  const fm = vis.match(FULL_MONTH); if (fm) throw new Error(`${name}: full month name "${fm[0]}" (L21: three letters)`);
  if (name === HUB) {
    const hit = HUB_EXCLUDE.filter((k) => html.includes(`href="${k}.html"`) || html.includes(esc(S[k].title)));
    if (hit.length) throw new Error(`${name}: Main Archive Page must not list ${hit.join(', ')}`);
    const links = [...html.matchAll(/<a\b[^>]*href="([^"]+)"/g)].map((m) => m[1]);
    const allowed = ['index.html', ...HUB_KEEP.map((k) => `${k}.html`)];
    const extra = links.filter((h) => !allowed.includes(h));
    if (extra.length) throw new Error(`${name}: Main Archive Page is newsletter archives only; unexpected links: ${extra.join(', ')}`);
    if (/Meetings, Events|Recurring Activities|Meeting Videos|Special Events/.test(html)) throw new Error(`${name}: Meetings, Events & Activities must not appear`);
  }
  if (issuesOnly) {
    const bad = [...html.matchAll(/<a\b[^>]*href="([^"]+)"/g)].map((m) => m[1]).filter((h) => !/^issues\/\d{4}-\d{2}-\d{2}\.html$/.test(h) && h !== HUB);
    if (bad.length) throw new Error(`${name}: issues-only page links to non-issue pages: ${bad.join(', ')}`);
  }
  return html;
}

// ---------- issue pages (immutable) ----------
const ISSUE_CSS = `<style id="ph-archive-issue">
html{-webkit-text-size-adjust:100%}body{margin:0;background:#f5f5f5;overflow-x:hidden}
table{max-width:100%!important}table[width="660"],table[width="640"],table[width="600"]{width:100%!important}td,th{white-space:normal!important}img{max-width:100%;height:auto}td,div,p,a,span{overflow-wrap:anywhere;word-break:break-word}
.pha-banner{max-width:660px;margin:0 auto;padding:10px 14px;background:#fff9e6;border-bottom:3px solid #8b6914;font:15px/1.45 Arial,sans-serif;color:#333;box-sizing:border-box}
.pha-banner b{color:#2d5016}.pha-banner a{color:#3a6b1a;font-weight:bold}.pha-note{display:block;margin-top:4px;font-size:13px;color:#666}
.pha-foot{max-width:660px;margin:0 auto 20px;padding:10px 14px;background:#eaf4e4;border-top:3px solid #2d5016;font:15px/1.8 Arial,sans-serif;box-sizing:border-box}.pha-foot a{color:#3a6b1a;font-weight:bold}
</style>`;
function cleanIssue(raw, iss) {
  let h = raw;
  h = h.replace(/<script[\s\S]*?<\/script>/gi, '');
  // personal unsubscribe link from the resident blast
  h = h.replace(/<hr>\s*<div>\s*If you no longer wish to receive these emails[\s\S]*?<\/div>/i, '');
  h = h.replace(/<a [^>]*unsubscribe[^>]*>[\s\S]*?<\/a>/gi, '');
  // private links: Zoom meeting links/passcodes, monthly-media download tokens (anchor text kept, link removed)
  h = h.replace(/\s*(?:&nbsp;|\s)*[·•|](?:&nbsp;|\s)*<a\b[^>]*href="[^"]*zoom\.us[^"]*"[^>]*>[\s\S]*?<\/a>/gi, '');
  h = h.replace(/<a\b[^>]*href="[^"]*zoom\.us[^"]*"[^>]*>[\s\S]*?<\/a>/gi, '');
  h = h.replace(/https?:\/\/[\w.-]*zoom\.us\/\S*/gi, '');
  h = h.replace(/(?:Passcode|Meeting ID|Password)\s*:?\s*[\w\s-]{3,20}?(?=<|$)/gi, '');
  h = h.replace(/<a\b[^>]*href="[^"]*newsletter_download\.php[^"]*"[^>]*>([\s\S]*?)<\/a>/gi, '<span>$1</span>');
  // review-only banners
  h = h.replace(/<(div|p)[^>]*>[^<]*LOCAL REVIEW[^<]*<\/\1>/gi, '');
  for (const name of iss.remove_sections || []) {
    const i = h.indexOf(name);
    if (i < 0) throw new Error(`${iss.date}: section "${name}" not found`);
    const marker = '<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 0 0;">';
    const start = h.lastIndexOf(marker, i); const end = h.indexOf(marker, i);
    if (start < 0 || end < 0) throw new Error(`${iss.date}: could not bound section "${name}"`);
    h = h.slice(0, start) + h.slice(end);
  }
  // links: map renamed pages, absolutize local copies, unlink anything that is not live
  const linkStats = { kept: 0, mapped: 0, unlinked: [] };
  h = h.replace(/<a\b([^>]*?)href="([^"]*)"([^>]*)>([\s\S]*?)<\/a>/gi, (m, pre, href, post, inner) => {
    let u = href.trim();
    if (/^(mailto:|tel:|#)/i.test(u)) { linkStats.kept++; return m; }
    let page = null;
    const pm = u.match(/^https:\/\/palmhillnews\.vercel\.app\/pages\/([^#?]+)(.*)$/i);
    if (pm) page = pm[1] + '|' + pm[2];
    else if (!/^https?:/i.test(u)) { const b = u.split('/pages/').pop().split('/').pop(); page = b + '|'; }
    if (page !== null) {
      let [p, rest] = page.split('|');
      if (ITEMS.link_map[p]) { p = ITEMS.link_map[p]; linkStats.mapped++; }
      if (pageExists(p)) { linkStats.kept++; return `<a${pre}href="${pageUrl(p)}${rest || ''}"${post}>${inner}</a>`; }
      linkStats.unlinked.push(u); return `<span>${inner}</span>`;
    }
    linkStats.kept++; return m;
  });
  const head = `<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta name="robots" content="noindex">\n<title>Palm Hill Newsletter — ${esc(issueLabel(iss))}, ${volNo(iss)} (archive copy)</title>\n<link rel="canonical" href="${archUrl(`issues/${iss.date}.html`)}">\n${ISSUE_CSS}`;
  if (/<head[^>]*>/i.test(h)) {
    h = h.replace(/<meta[^>]*name="viewport"[^>]*>/gi, '').replace(/<title>[\s\S]*?<\/title>/i, '');
    h = h.replace(/<head([^>]*)>/i, `<head$1>\n<meta charset="utf-8">\n${head}`);
  } else {
    h = `<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n${head}\n</head>\n<body>\n${h}\n</body>\n</html>\n`;
  }
  const banner = `<div class="pha-banner" role="note"><b>Archive copy · ${volNo(iss)} · Sent ${longDate(iss.date)} at ${sentTimeET(iss.sent)} ET${iss.file_dated ? ` · file dated ${fileDated(iss.file_dated)}` : ''}.</b> This is the version sent to Palm Hill residents; dates, times and links are as they were that week. <a href="${archUrl('index.html')}">Newsletter Archive →</a>${iss.caveat ? `<span class="pha-note">${esc(iss.caveat)}</span>` : ''}</div>`;
  const foot = `<nav class="pha-foot" aria-label="Newsletter archive"><a href="${archUrl('index.html')}">Newsletter Archive →</a> · <a href="${archUrl('community-notices.html')}">Previous Notices →</a> · <a href="${archUrl('committee-reports.html')}">Previous Chair Reports →</a></nav>`;
  h = h.replace(/<body([^>]*)>/i, `<body$1>\n<!-- Archive copy generated by scripts/build_archive.js from ${esc(iss.source)}. Written once; never overwritten. -->\n${banner}`);
  h = h.replace(/<\/body>(?![\s\S]*<\/body>)/i, `${foot}\n</body>`);
  const leak = h.match(/zoom\.us|pwd=|newsletter_download\.php|unsubscribe\.php|LOCAL REVIEW/i);
  if (leak) throw new Error(`${iss.date}: private content left after cleaning (${leak[0]})`);
  return { html: h, linkStats };
}

// ---------- detail-page strip ----------
// Story and report sections: each item page (and its listen page) also gets a full-date line under the bar,
// and loses its bottom <footer> (Steven, Oct 9: no footer on archive/story/report pages).
const DATED = new Set(['community-stories', 'presidents-message', 'committee-reports', 'manager-reports', 'weekly-manager-updates']);
const pageItem = new Map();
for (const k of DATED) for (const it of S[k].items) for (const pg of [it.page, it.listen]) if (pg && !pageItem.has(pg)) pageItem.set(pg, it);
// No dateline when the page's own <header> already shows that full date (e.g. chair-report pages).
function stripFor(k, page, headerText = '') {
  const sec = S[k];
  const it = DATED.has(k) ? pageItem.get(page) : null;
  const dateline = it && it.date && !headerText.includes(midDate(it.date)) ? `\n<p class="ph-dateline" style="display:block;margin:0;padding:10px 14px 0;box-sizing:border-box;background:none;border:0;color:#1a1a1a;font:18px/1.5 Arial,Helvetica,sans-serif;text-align:center;letter-spacing:0;text-transform:none">${fullDate(it)}</p>` : '';
  if (sec.story_nav && it) return `<!-- ph-archive-nav:start -->\n${storyNav(k, page, it, !headerText.includes(midDate(it.date)))}\n<!-- ph-archive-nav:end -->`;
  if (sec.dateline_listen && it && it.date && page === it.page) return `<!-- ph-archive-nav:start -->\n${navBar([[archUrl(`${k}.html`), sec.prev], [archUrl(HUB), HUB_LABEL]])}\n${listenDateline(it)}\n<!-- ph-archive-nav:end -->`;
  return `<!-- ph-archive-nav:start -->\n${navBar([[archUrl(`${k}.html`), sec.prev], [archUrl(HUB), HUB_LABEL]])}${dateline}\n<!-- ph-archive-nav:end -->`;
}
// "dateline_listen" sections (Committee Chair Reports), Steven Oct 10: the full date LEFT-justified and the
// newsletter's green/gold speaker icon + "Listen" RIGHT-justified on the same row (links to the item's listen page).
// No listen page -> date alone, still left-justified. Row is the width of the content card.
const LISTEN_ICON = 'https://palmhillnews.vercel.app/assets/images/phnews/2026-10-04/speaker-read-aloud-green-gold-512-v3.png';
function listenDateline(it) {
  const F = 'Arial,Helvetica,sans-serif';
  const link = it.listen ? `<a class="ph-listen" href="${pageUrl(it.listen)}" style="display:inline-flex;align-items:center;gap:6px;margin-left:auto;background:none;border:0;padding:0;color:#1d4310;font:bold 18px/1.5 ${F};text-decoration:underline;text-underline-offset:3px;white-space:nowrap"><img src="${LISTEN_ICON}" alt="" width="32" height="32" style="display:inline-block;width:32px;height:32px;border:0;margin:0;vertical-align:middle">Listen</a>` : '';
  return `<div class="ph-dateline" style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:4px 16px;width:min(780px,100%);margin:0 auto;padding:10px 18px 0;box-sizing:border-box;background:none;border:0;text-align:left;letter-spacing:0;text-transform:none"><span style="color:#1a1a1a;font:18px/1.5 ${F}">${fullDate(it)}</span>${link}</div>`;
}
// "story_nav" sections (Community Stories), Steven Oct 9: under the header, the full date with Listen (or, on the
// listen page, Read the Story) right-aligned on the same row; below it ONE line: Story Archives → · Newsletter Archive →
// (or, with story_nav_back, a single ← Back link).
function storyNav(k, page, it, showDate) {
  const sec = S[k];
  const F = 'Arial,Helvetica,sans-serif';
  const A = `display:inline;background:none;border:0;border-radius:0;box-shadow:none;padding:0;margin:0;color:#1d4310;font:bold 18px/1.5 ${F};text-decoration:underline;text-underline-offset:3px;letter-spacing:0;text-transform:none;white-space:nowrap`;
  const side = page === it.listen ? (it.page ? [pageUrl(it.page), sec.story_nav_read || 'Read the Story →'] : null) : (it.listen ? [pageUrl(it.listen), '🔊 Listen →'] : null);
  const row1 = `<div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:4px 16px;margin:0"><span style="color:#1a1a1a;font:18px/1.5 ${F}">${showDate ? fullDate(it) : ''}</span>${side ? `<a href="${side[0]}" style="${A};margin-left:auto">${esc(side[1])}</a>` : ''}</div>`;
  // Short labels (Story Archives) stay on one line even on phones; longer ones (President Message Archives) stack
  // one per line at <=480px with the dot hidden, so nothing runs off the screen.
  const long = (sec.prev.length + HUB_LABEL.length) > 36;
  const L = `${A};font-size:min(17px,4.3vw)`;
  const css = long ? '<style>@media (max-width:480px){.ph-story-links-long .ph-sep{display:none!important}.ph-story-links-long a{display:block!important;width:max-content}}</style>' : '';
  // "story_nav_back" (Community Stories, Steven Oct 9 — archive-structure pattern): no Story Archives · Newsletter
  // Archive pair on the detail page; ONE "← Back" link instead. It goes back in browser history when the reader came
  // from another page, and falls back to the section archive (href) when opened fresh (e.g. from the email).
  if (sec.story_nav_back) {
    const back = `<div class="ph-story-back" style="margin:6px 0 0"><a href="${archUrl(`${k}.html`)}" onclick="if(document.referrer&&history.length>1){history.back();return false}" style="${A}">← Back</a></div>`;
    return `<div class="ph-story-nav" role="navigation" aria-label="Story date and back" style="display:block;max-width:790px;margin:0 auto;padding:12px 20px 10px;box-sizing:border-box;background:none;border:0;border-bottom:2px solid #2d5016;text-align:left;letter-spacing:0;text-transform:none">${row1}${back}</div>`;
  }
  const row2 = `${css}<div class="${long ? 'ph-story-links-long' : 'ph-story-links'}" style="margin:6px 0 0;white-space:nowrap;overflow-wrap:normal;color:#1a1a1a;font:bold min(17px,4.3vw)/1.5 ${F}"><a href="${archUrl(`${k}.html`)}" style="${L}">${esc(sec.prev)}</a><span class="ph-sep" aria-hidden="true" style="padding:0 6px"> · </span><a href="${archUrl(HUB)}" style="${L}">${esc(HUB_LABEL)}</a></div>`;
  return `<div class="ph-story-nav" role="navigation" aria-label="Story date and newsletter archive" style="display:block;max-width:790px;margin:0 auto;padding:12px 20px 10px;box-sizing:border-box;background:none;border:0;border-bottom:2px solid #2d5016;text-align:left;letter-spacing:0;text-transform:none">${row1}${row2}</div>`;
}
function addStrip(page, k) {
  const file = path.join(PAGES, page);
  const src = fs.readFileSync(file, 'utf8');
  // Pages marked <!-- ph-archive-nav:none --> (original-notice pages, Steven Oct 9) get no bar: title only.
  if (src.includes('<!-- ph-archive-nav:none')) return;
  // Drop any earlier strip (footer v1 or header-top), then put the one bar at the top.
  let next = src.replace(/\n?<!-- ph-archive-nav-top:start -->[\s\S]*?<!-- ph-archive-nav-top:end -->\n?/g, '')
    .replace(/\n?<!-- ph-archive-nav:start -->[\s\S]*?<!-- ph-archive-nav:end -->\n?/g, (m0, off, all) => (/\n$/.test(m0) && all[off + m0.length] !== undefined ? '\n' : ''));
  const lower = next.toLowerCase();
  const h = lower.indexOf('</header>');
  let at;
  if (h >= 0) at = h + '</header>'.length;
  else {
    const b = lower.indexOf('<body');
    at = b >= 0 ? next.indexOf('>', b) + 1 : 0;
    if (!at) throw new Error(`${page}: no <body>`);
  }
  const hs = lower.indexOf('<header');
  const headerText = h >= 0 && hs >= 0 && hs < h ? next.slice(hs, h).replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ') : '';
  next = next.slice(0, at) + '\n' + stripFor(k, page, headerText) + '\n' + next.slice(at).replace(/^\n/, '');
  if (DATED.has(k)) next = next.replace(/<footer\b[\s\S]*?<\/footer>/gi, '');
  write(file, next);
}

// ---------- run ----------
// Hub + section archive pages never carry the main PHNL footer (Vantaca box, calendar disclaimer, bottom <footer>).
// Steven, Oct 9: "page does not need the footer from the main phnl page." Fail closed if one sneaks back in.
const NO_FOOTER = /<footer\b|class="ph-footer|class="ph-urgent-line|class="ph-fineprint|VANTACA Service Request System|always confirm event times and updates on the/i;
function writeHub(file, html) {
  const m = html.match(NO_FOOTER);
  if (m) throw new Error(`${path.relative(ROOT, file)}: main-newsletter footer must not appear on archive hub/section pages (found ${m[0]})`);
  write(file, html);
}
for (const k of SECTION_ORDER) writeHub(path.join(OUT, `${k}.html`), k === 'videos' ? videosPage() : sectionPage(k));
writeHub(path.join(OUT, 'index.html'), checkPride('index.html', issuesPage(), true));
writeHub(path.join(OUT, HUB), checkPride(HUB, mainPage(), false));

const stripped = new Map();
for (const k of SECTION_ORDER) for (const it of S[k].items) if (it.page && !stripped.has(it.page)) stripped.set(it.page, it.strip_as || k);
// "also" pages (e.g. Original notice) and "strip_extra" pages (e.g. Zoom) get their item's section strip.
for (const k of SECTION_ORDER) for (const it of S[k].items) for (const p of [...(it.also || []).map((a) => a.page), ...(it.strip_extra || [])]) if (!stripped.has(p)) stripped.set(p, k);
// Sections with "strip_listen": true also get the strip on each item's read-aloud (listen) page.
for (const k of SECTION_ORDER) if (S[k].strip_listen) for (const it of S[k].items) if (it.listen && !stripped.has(it.listen)) stripped.set(it.listen, k);
for (const [p, k] of stripped) addStrip(p, k);

const issuesFrom = argVal('--issues-from');
const report = {};
if (issuesFrom) {
  for (const iss of ITEMS.issues) {
    const target = path.join(OUT, 'issues', `${iss.date}.html`);
    if (fs.existsSync(target) && !args.includes('--force-issues')) { report[iss.date] = 'exists (kept)'; continue; }
    const cands = [path.join(issuesFrom, iss.nas.replace(/^02-Issues\//, '')), path.join(issuesFrom, iss.date, path.basename(iss.nas))];
    const src = cands.find((c) => fs.existsSync(c));
    if (!src) throw new Error(`${iss.date}: source not found (tried ${cands.join(', ')})`);
    const { html, linkStats } = cleanIssue(fs.readFileSync(src, 'utf8'), iss);
    write(target, html);
    report[iss.date] = linkStats;
  }
}

const index = {
  schema: 'phnews-archive-index/1',
  generated_by: 'scripts/build_archive.js',
  base_url: BASE,
  archive_home: archUrl('index.html'),
  archive_main: archUrl(HUB),
  issues: [...ITEMS.issues].sort((a, b) => b.date.localeCompare(a.date)).map((i) => ({ date: i.date, volume: i.volume, number: i.number, issue_number: volNo(i), label: issueLabel(i), sent: i.sent, file_dated: i.file_dated, format: i.format, url: archUrl(`issues/${i.date}.html`) })),
  sections: Object.fromEntries(SECTION_ORDER.map((k) => [k, {
    title: S[k].title, url: archUrl(`${k}.html`), email_link_label: S[k].past, page_link_label: S[k].prev,
    items: sorted(k).map((it) => ({ date: it.date, title: it.title || it.group, url: it.page ? pageUrl(it.page) : (it.url || (it.id ? `${archUrl(`${k}.html`)}#${it.id}` : null)), listen_url: it.listen ? pageUrl(it.listen) : undefined, also: it.also ? it.also.map((a) => ({ label: a.label, url: pageUrl(a.page) })) : undefined, issues: it.issues })),
  }])),
  hidden: [...hidden].map(pageUrl),
};
write(path.join(OUT, 'archive-index.json'), JSON.stringify(index, null, 2) + '\n');

if (Object.keys(report).length) console.log(JSON.stringify(report, null, 2));
console.log(`${CHECK ? 'would change' : 'changed'} ${changed.length} file(s)`);
changed.forEach((f) => console.log('  ' + f));
if (CHECK && changed.length) process.exit(1);
