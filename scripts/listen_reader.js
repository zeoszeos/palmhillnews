  // STYLE-RULES R49/R76: the ONE reader (what Listen speaks), shared by the v2 page-listen script and the in-place
  // Listen on archive / issue pages. phParts(doc) -> phrases in page order. Same rules as the v1 page script.
  const MON = {Jan:'January',Feb:'February',Mar:'March',Apr:'April',Jun:'June',Jul:'July',Aug:'August',Sep:'September',Oct:'October',Nov:'November',Dec:'December'};
  function chunks(text) {
    const clean = text.replace(/\b(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b\.?/g, (m, k) => MON[k]).replace(/\s+/g, ' ').trim();
    if (!clean) return [];
    const frags = typeof Intl.Segmenter === 'function'
      ? Array.from(new Intl.Segmenter('en-US', {granularity: 'sentence'}).segment(clean), (s) => s.segment.trim()).filter(Boolean)
      : [clean];
    const out = []; let p = '';
    for (const s of frags) { if (p && p.length + s.length + 1 > 260) { out.push(p); p = s; } else p += (p ? ' ' : '') + s; }
    if (p) out.push(p);
    return out;
  }
  function phParts(doc) {
    const win = doc.defaultView || window;
    const h1 = doc.querySelector('h1');
    const sel = 'main .content-card, main .ph-row, main .ph-meta, main .source, main .ph-source, main .credit, main .byline';
    const sent = (doc.querySelector('main') || doc.body).innerText;
    const all = Array.from(doc.querySelectorAll(sel))
      .filter((el) => !el.closest('nav, .ph-strip, .ph-links, .ph-tap-bar') && !el.classList.contains('attachments') && !/^\s*Subject:/.test(el.innerText))
      .filter((el) => !(el.classList.contains('ph-meta') && sent.includes('Sent: ' + el.innerText.trim())));
    let blocks = all.filter((el) => !all.some((o) => o !== el && o.contains(el))).map((el) => el.innerText.trim()).filter(Boolean);
    // R83: a story page (<main> with an <article>) is read in page order -- byline, article (h2, figures, captions), credit line
    if (!blocks.length || doc.querySelector('main article')) blocks = walkAll(doc, win);
    return [h1 ? h1.textContent : '', ...blocks].flatMap((t) => t.split(/\n+/)).flatMap(chunks);
  }
  function walkAll(doc, win) {
    const BLOCK = 'h2,h3,h4,h5,h6,p,li,blockquote,figure,figcaption,pre,table,dl,aside';
    const SKIP = 'h1,header,footer,script,style,noscript,nav,button,[role="navigation"],.ph-listen,.ph-listen-row,.ph-tap-bar,.ph-story-nav,.ph-story-links-long,.ph-archive-bar,.ph-dateline,.page-kicker,.ph-strip,.ph-links,.badge,.meta,.date,.back,.attachments,[aria-hidden="true"]';
    const vis = (el) => el.getClientRects().length > 0;
    const out = [];
    const walk = (el) => {
      let run = '';
      const flush = () => { if (run.trim()) out.push(run.trim()); run = ''; };
      for (const n of el.childNodes) {
        if (n.nodeType === 3) { run += n.textContent; continue; }
        if (n.nodeType !== 1 || n.matches(SKIP) || !vis(n)) continue;
        if (n.matches(BLOCK)) {
          flush();
          if (n.matches('table,dl')) n.querySelectorAll('caption,tr,dt,dd').forEach((r) => { const x = r.innerText.trim(); if (x) out.push(x); });
          else if (n.matches('figure,aside,blockquote') && n.querySelector('p,li,figcaption')) walk(n);
          else { const x = n.innerText.trim(); if (x) out.push(x); }
        } else if (win.getComputedStyle(n).display.startsWith('inline')) run += n.innerText;
        else { flush(); walk(n); }
      }
      flush();
    };
    walk(doc.querySelector('main') || doc.querySelector('article') || doc.body);
    return out;
  }
