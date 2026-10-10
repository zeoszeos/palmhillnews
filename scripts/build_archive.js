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
Outputs:  pages/archive/index.html, pages/archive/<section>.html (9), pages/archive/archive-index.json,
          pages/archive/issues/<date>.html (only with --issues-from; written once),
          marked nav strip in each listed detail page
Exit:     0 ok; 1 with --check if anything is out of date; non-zero on any missing page/source
See archive/RUNBOOK-archive.md.`);
  process.exit(0);
}
const changed = [];

const SECTION_ORDER = ['community-stories', 'presidents-message', 'meetings', 'committee-reports', 'manager-reports', 'events', 'community-notices', 'did-you-know', 'videos'];
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
const sorted = (k) => [...S[k].items].sort((a, b) => (b.date || '').localeCompare(a.date || ''));
const issueDates = ITEMS.issues.map((i) => i.date).sort().reverse();
const issueLink = (date) => ITEMS.issues.some((i) => i.date === date) ? `<a href="issues/${date}.html">${shortDate(date)}</a>` : shortDate(date);
const crumbs = (title) => `<p class="ph-crumbs"><a href="index.html">Newsletter Archives</a> › ${esc(title)}</p>`;

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
  const topNav = navBar([hasPrev ? ['#previous', `${sec.prev.replace(/\s*→$/, '')} ↓`] : null, ['index.html', 'Newsletter Archive →']].filter(Boolean));
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
  const topNav = navBar([[pageUrl('2026-10-04-committee-video-guide.html'), 'How to Find Videos →'], ['index.html', 'Newsletter Archive →']]);
  return shell({ title: 'Meeting Videos — Newsletter Archive', issuedate: 'Newsletter Archives', body: out, canonical: archUrl('videos.html'), topNav });
}

function homePage() {
  const tiles = SECTION_ORDER.map((k) => {
    const items = S[k].items; const newest = items.map((x) => x.date).sort().pop();
    const noun = k === 'videos' ? 'recording' : 'item';
    return `<a class="ph-tile" href="${k}.html"><b>${esc(S[k].hub_label || S[k].title)} →</b><span>${esc(S[k].title)} · ${items.length} ${noun}${items.length === 1 ? '' : 's'} · newest ${shortDate(newest)}</span></a>`;
  }).join('\n');
  let rows = ''; let n = 0;
  for (const iss of [...ITEMS.issues].sort((a, b) => b.date.localeCompare(a.date))) {
    const parts = [];
    for (const k of SECTION_ORDER) {
      const c = S[k].items.filter((x) => (x.issues || []).includes(iss.date)).length;
      if (c) parts.push(`${c} ${S[k].title.replace('?', '')}`);
    }
    rows += `<div class="ph-row${n++ % 2 ? ' ph-alt' : ''}"><a class="ph-row-title" href="issues/${iss.date}.html">${esc(issueLabel(iss))} →</a>\n<div class="ph-row-meta"><b>${volNo(iss)}</b> · Sent ${longDate(iss.date)} at ${sentTimeET(iss.sent)} ET${iss.file_dated ? ` · file dated ${fileDated(iss.file_dated)}` : ''} · ${esc(iss.format)}</div>\n<div class="ph-row-meta">${esc(parts.join(' · '))}</div></div>\n`;
  }
  const body = `<h1 class="ph-section">Palm Hill Newsletter Archives</h1>
<p class="ph-lead">Everything the Palm Hill weekly newsletter has carried, in one place: an archive for each section, and every back issue as it was sent.</p>
<h2 class="ph-subhead" id="sections">Section Archives</h2>
<div class="ph-grid">
${tiles}
</div>
<h2 class="ph-subhead" id="issues">Newsletter Back Issues</h2>
${rows}<p class="ph-source">The archive starts with the first resident issue, sent Jul 21, 2026. Issues before Oct 4 were sent as a PDF from palmhillcountryclub.net; their archive pages are made from the exact HTML build of that PDF. Private meeting links, download links and unsubscribe links are removed.</p>
`;
  const topNav = navBar([['#sections', 'Section Archives ↓'], ['#issues', 'Back Issues ↓']]);
  return shell({ title: 'Palm Hill Newsletter Archives', issuedate: 'Newsletter Archives', body, canonical: archUrl('index.html'), topNav });
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
const DATED = new Set(['community-stories', 'presidents-message', 'committee-reports', 'manager-reports']);
const pageItem = new Map();
for (const k of DATED) for (const it of S[k].items) for (const pg of [it.page, it.listen]) if (pg && !pageItem.has(pg)) pageItem.set(pg, it);
// No dateline when the page's own <header> already shows that full date (e.g. chair-report pages).
function stripFor(k, page, headerText = '') {
  const sec = S[k];
  const it = DATED.has(k) ? pageItem.get(page) : null;
  const dateline = it && it.date && !headerText.includes(midDate(it.date)) ? `\n<p class="ph-dateline" style="display:block;margin:0;padding:10px 14px 0;box-sizing:border-box;background:none;border:0;color:#1a1a1a;font:18px/1.5 Arial,Helvetica,sans-serif;text-align:center;letter-spacing:0;text-transform:none">${fullDate(it)}</p>` : '';
  if (sec.story_nav && it) return `<!-- ph-archive-nav:start -->\n${storyNav(k, page, it, !headerText.includes(midDate(it.date)))}\n<!-- ph-archive-nav:end -->`;
  return `<!-- ph-archive-nav:start -->\n${navBar([[archUrl(`${k}.html`), sec.prev], [archUrl('index.html'), 'Newsletter Archive →']])}${dateline}\n<!-- ph-archive-nav:end -->`;
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
  const long = (sec.prev.length + 'Newsletter Archive →'.length) > 36;
  const L = `${A};font-size:min(17px,4.3vw)`;
  const css = long ? '<style>@media (max-width:480px){.ph-story-links-long .ph-sep{display:none!important}.ph-story-links-long a{display:block!important;width:max-content}}</style>' : '';
  // "story_nav_back" (Community Stories, Steven Oct 9 — archive-structure pattern): no Story Archives · Newsletter
  // Archive pair on the detail page; ONE "← Back" link instead. It goes back in browser history when the reader came
  // from another page, and falls back to the section archive (href) when opened fresh (e.g. from the email).
  if (sec.story_nav_back) {
    const back = `<div class="ph-story-back" style="margin:6px 0 0"><a href="${archUrl(`${k}.html`)}" onclick="if(document.referrer&&history.length>1){history.back();return false}" style="${A}">← Back</a></div>`;
    return `<div class="ph-story-nav" role="navigation" aria-label="Story date and back" style="display:block;max-width:790px;margin:0 auto;padding:12px 20px 10px;box-sizing:border-box;background:none;border:0;border-bottom:2px solid #2d5016;text-align:left;letter-spacing:0;text-transform:none">${row1}${back}</div>`;
  }
  const row2 = `${css}<div class="${long ? 'ph-story-links-long' : 'ph-story-links'}" style="margin:6px 0 0;white-space:nowrap;overflow-wrap:normal;color:#1a1a1a;font:bold min(17px,4.3vw)/1.5 ${F}"><a href="${archUrl(`${k}.html`)}" style="${L}">${esc(sec.prev)}</a><span class="ph-sep" aria-hidden="true" style="padding:0 6px"> · </span><a href="${archUrl('index.html')}" style="${L}">Newsletter Archive →</a></div>`;
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
writeHub(path.join(OUT, 'index.html'), homePage());

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
