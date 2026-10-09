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
          and "summary" (one-line teaser).
          Section option "header_nav": true also puts the archive links at the TOP: inside the <header> of the
          section page, and inside the first <header> of each detail/listen page that gets the strip (between
          <!-- ph-archive-nav-top:start --> / <!-- ph-archive-nav-top:end -->; right after <body> if a page has no
          <header>). The footer strip stays.
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
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
function d(iso) { const [y, m, dd] = iso.slice(0, 10).split('-').map(Number); return new Date(Date.UTC(y, m - 1, dd)); }
const longDate = (iso) => { const x = d(iso); return `${DAYS[x.getUTCDay()]}, ${MONTHS[x.getUTCMonth()]} ${x.getUTCDate()}, ${x.getUTCFullYear()}`; };
const midDate = (iso) => { const x = d(iso); return `${MONTHS[x.getUTCMonth()]} ${x.getUTCDate()}, ${x.getUTCFullYear()}`; };
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

function shell({ title, issuedate, body, canonical, headerNav }) {
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
  <p class="ph-tagline">A look at upcoming events, meetings, maintenance notices, useful resources and helpful links</p>
  <p class="ph-address"><a href="https://www.google.com/maps/search/1800+Seminole+Blvd,+Largo,+FL+33778">1800 Seminole Blvd, Largo, FL 33778</a></p>
${headerNav ? headerNav + '\n' : ''}</header>
<main class="ph-body">
${body}
</main>
<footer class="ph-footer">
  <div class="ph-urgent">
    <p class="ph-urgent-line">NON-URGENT SERVICE REQUESTS – Submit through the <a href="https://home.resourcepropertymgmt.com/community/requests">VANTACA Service Request System</a></p>
    <p class="ph-urgent-line">URGENT SERVICE REQUESTS – Business Hours: <a href="tel:+17275818729">(727) 581-8729</a> / After Hours: <a href="tel:+17272698236">(727) 269-8236</a></p>
  </div>
  <p class="ph-fineprint">For the latest details, always confirm event times and updates on the <a href="https://www.palmhillcountryclub.net/calendar-1/">official Palm Hill calendar</a>.</p>
</footer>
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
const crumbs = (title) => `<p class="ph-crumbs"><a href="index.html">Newsletter Archive</a> › ${esc(title)}</p>`;

// ---------- section pages ----------
function sectionPage(k) {
  const sec = S[k];
  let out = `${crumbs(sec.title)}\n<h1 class="ph-section">${esc(sec.title)}</h1>\n<p class="ph-lead">${esc(sec.lead)}</p>\n`;
  let month = null; let n = 0;
  let rows = sorted(k);
  // "feature_latest": the newest item leads the page as the current one; the rest list below as previous items.
  if (sec.feature_latest && rows.length) {
    const top = rows[0]; rows = rows.slice(1);
    const when = top.date_label ? esc(top.date_label) : longDate(top.date);
    const links = [top.page ? `<a href="${pageUrl(top.page)}">${esc(sec.feature_read || 'Read →')}</a>` : null, top.listen ? `<a href="${pageUrl(top.listen)}">Listen →</a>` : null].filter(Boolean).join('<span class="ph-dot"> · </span>');
    out += `<section class="ph-feature" aria-label="${esc(sec.feature_label || 'Latest')}">\n<p class="ph-feature-kicker">${esc(sec.feature_label || 'Latest')}</p>\n`;
    out += `<h2 class="ph-feature-title">${top.page ? `<a href="${pageUrl(top.page)}">${esc(top.title)}</a>` : esc(top.title)}</h2>\n`;
    out += `<div class="ph-row-meta">${[top.byline ? esc(top.byline) : null, when].filter(Boolean).join(' · ')}</div>\n`;
    if (top.summary) out += `<p class="ph-detail">${esc(top.summary)}</p>\n`;
    if (links) out += `<nav class="ph-links">${links}</nav>\n`;
    if (top.source) out += `<div class="ph-row-meta">Source: ${esc(top.source)}</div>\n`;
    if (top.issues && top.issues.length) out += `<div class="ph-row-meta">In the newsletter: ${top.issues.slice().sort().map(issueLink).join(', ')}</div>\n`;
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
    const meta = [it.date_label ? esc(it.date_label) : longDate(it.date), it.byline ? esc(it.byline) : null, it.listen ? `<a href="${pageUrl(it.listen)}">Listen →</a>` : null, ...(it.also || []).map((a) => `<a href="${pageUrl(a.page)}">${esc(a.label)}</a>`)].filter(Boolean).join(' · ');
    out += `<div class="ph-row${n % 2 ? ' ph-alt' : ''}"${id}>${head}\n<div class="ph-row-meta">${meta}</div>\n`;
    if (it.text) out += `<div class="ph-detail">${esc(it.text)}</div>\n`;
    if (it.summary) out += `<div class="ph-detail">${esc(it.summary)}</div>\n`;
    if (it.external) out += `<nav class="ph-links"><a href="${esc(it.external)}">${esc(it.external_label || 'Open →')}</a></nav>\n`;
    if (it.source) out += `<div class="ph-row-meta">Source: ${esc(it.source)}</div>\n`;
    if (it.issues && it.issues.length) out += `<div class="ph-row-meta">In the newsletter: ${it.issues.slice().sort().map(issueLink).join(', ')}</div>\n`;
    out += `</div>\n`;
    n++;
  }
  out += `<nav class="ph-archive-nav" aria-label="More from the newsletter"><a href="index.html">Newsletter Archive →</a></nav>\n`;
  return shell({ title: `${sec.title} — Newsletter Archive`, issuedate: 'Newsletter Archive', body: out, canonical: archUrl(`${k}.html`), headerNav: sec.header_nav ? sectionHeaderNav(k, sec.feature_latest && sorted(k).length > 1) : null });
}
// Archive links at the top of a section page ("header_nav"), inside the banner. Same wording as the strips.
function sectionHeaderNav(k, hasPrev) {
  const sec = S[k];
  const A = 'color:#3a6b1a;font-weight:bold;text-decoration:underline';
  const links = [hasPrev ? `<a href="#previous" style="${A}">${esc(sec.prev.replace(/\s*→$/, ''))} ↓</a>` : null, `<a href="index.html" style="${A}">Newsletter Archive →</a>`].filter(Boolean);
  return `<nav class="ph-header-nav" aria-label="Newsletter archive" style="margin:10px auto 0;max-width:600px;padding:8px 12px;background:#eaf4e4;border-top:3px solid #2d5016;border-radius:0 0 4px 4px;font:15px/1.8 Arial,sans-serif;color:#333333;text-align:center">${links.join('<span style="font-weight:normal"> · </span>')}</nav>`;
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
  out += `<nav class="ph-archive-nav" aria-label="More from the newsletter"><a href="${pageUrl('2026-10-04-committee-video-guide.html')}">How to find videos on the Palm Hill website →</a><span class="ph-dot"> · </span><a href="index.html">Newsletter Archive →</a></nav>\n`;
  return shell({ title: 'Meeting Videos — Newsletter Archive', issuedate: 'Newsletter Archive', body: out, canonical: archUrl('videos.html') });
}

function homePage() {
  const tiles = SECTION_ORDER.map((k) => {
    const items = S[k].items; const newest = items.map((x) => x.date).sort().pop();
    const noun = k === 'videos' ? 'recording' : 'item';
    return `<a class="ph-tile" href="${k}.html"><b>${esc(S[k].title)} →</b><span>${items.length} ${noun}${items.length === 1 ? '' : 's'} · newest ${shortDate(newest)}</span></a>`;
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
  const body = `<h1 class="ph-section">Newsletter Archive</h1>
<p class="ph-lead">Past issues of the Palm Hill weekly newsletter, plus a page for each regular section so you can catch up on anything you missed.</p>
<h2 class="ph-subhead">Browse by Section</h2>
<div class="ph-grid">
${tiles}
</div>
<h2 class="ph-subhead">Past Issues</h2>
${rows}<p class="ph-source">The archive starts with the first resident issue, sent July 21, 2026. Issues before October 4 were sent as a PDF from palmhillcountryclub.net; their archive pages are made from the exact HTML build of that PDF. Private meeting links, download links and unsubscribe links are removed.</p>
`;
  return shell({ title: 'Newsletter Archive', issuedate: 'Newsletter Archive', body, canonical: archUrl('index.html') });
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
function stripFor(k) {
  const sec = S[k];
  // A <div role="navigation"> with fully inline styles, so each page's own nav/a rules cannot restyle it.
  const A = 'display:inline;background:none;border:0;border-radius:0;box-shadow:none;padding:0;margin:0;color:#3a6b1a;font:bold 15px/1.8 Arial,sans-serif;text-decoration:underline';
  return `<!-- ph-archive-nav:start -->
<div role="navigation" aria-label="More from the newsletter" style="display:block;max-width:660px;margin:24px auto 16px;padding:10px 14px;box-sizing:border-box;background:#eaf4e4;border:0;border-top:3px solid #2d5016;border-radius:0 0 4px 4px;font:15px/1.8 Arial,sans-serif;color:#333333;text-align:left"><a href="${archUrl(`${k}.html`)}" style="${A}">${esc(sec.prev)}</a><span style="color:#333333;font-weight:normal"> · </span><a href="${archUrl('index.html')}" style="${A}">Newsletter Archive →</a></div>
<!-- ph-archive-nav:end -->`;
}
// Top-of-page version for "header_nav" sections: sits inside the page's dark green <header>, so gold links on green.
function topStripFor(k) {
  const sec = S[k];
  const A = 'display:inline;background:none;border:0;border-radius:0;box-shadow:none;padding:0;margin:0;color:#f3dfa2;font:bold 15px/1.8 Arial,sans-serif;text-decoration:underline;letter-spacing:0;text-transform:none';
  return `<!-- ph-archive-nav-top:start -->
<div role="navigation" aria-label="Newsletter archive" style="display:block;max-width:780px;margin:10px auto 0;padding:6px 0 0;box-sizing:border-box;background:none;border:0;border-top:1px solid rgba(243,223,162,.45);font:15px/1.8 Arial,sans-serif;color:#ffffff;text-align:inherit;letter-spacing:0;text-transform:none"><a href="${archUrl(`${k}.html`)}" style="${A}">${esc(sec.prev)}</a><span style="color:#ffffff;font-weight:normal"> · </span><a href="${archUrl('index.html')}" style="${A}">Newsletter Archive →</a></div>
<!-- ph-archive-nav-top:end -->`;
}
function addStrip(page, k) {
  const file = path.join(PAGES, page);
  const src = fs.readFileSync(file, 'utf8');
  const strip = stripFor(k);
  let next;
  if (src.includes('<!-- ph-archive-nav:start -->')) next = src.replace(/<!-- ph-archive-nav:start -->[\s\S]*?<!-- ph-archive-nav:end -->/, strip);
  else {
    const i = src.toLowerCase().lastIndexOf('</body>');
    if (i < 0) throw new Error(`${page}: no </body>`);
    next = src.slice(0, i) + strip + '\n' + src.slice(i);
  }
  const top = S[k].header_nav ? topStripFor(k) : null;
  const TOP_RE = /<!-- ph-archive-nav-top:start -->[\s\S]*?<!-- ph-archive-nav-top:end -->\n?/;
  if (top) {
    if (TOP_RE.test(next)) next = next.replace(TOP_RE, top + '\n');
    else {
      const lower = next.toLowerCase();
      const h = lower.indexOf('</header>');
      if (h >= 0) next = next.slice(0, h) + top + '\n' + next.slice(h);
      else {
        const b = lower.indexOf('<body');
        const e = b >= 0 ? next.indexOf('>', b) : -1;
        if (e < 0) throw new Error(`${page}: no <body>`);
        next = next.slice(0, e + 1) + '\n' + top + '\n' + next.slice(e + 1);
      }
    }
  } else next = next.replace(TOP_RE, '');
  write(file, next);
}

// ---------- run ----------
for (const k of SECTION_ORDER) write(path.join(OUT, `${k}.html`), k === 'videos' ? videosPage() : sectionPage(k));
write(path.join(OUT, 'index.html'), homePage());

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
