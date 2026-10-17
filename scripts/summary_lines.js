// Shared by visual_regression.py (R18): every item summary block in the main newsletter, with its line count.
// A summary block = leaf-ish div/p with >=40 chars of text that is not a title (bold), not a Source line, not mostly links,
// inside a green-bar section (not masthead/footer/Helpful Webpages/Residents Reference).
() => {
  const SKIP = /Residents Reference|Helpful Webpages|Palm Hill Country Club$/i;
  const bars = [...document.querySelectorAll('div,td,table,h2')].filter(e => getComputedStyle(e).backgroundColor === 'rgb(45, 80, 22)' && e.innerText.trim().length > 2 && e.getBoundingClientRect().height < 140);
  const ys = bars.map(e => ({y: e.getBoundingClientRect().top + scrollY, t: e.innerText.split('\n')[0].trim()})).sort((a, b) => a.y - b.y);
  const secOf = (y) => { let s = null; for (const b of ys) if (b.y <= y) s = b.t; return s; };
  const out = [];
  for (const el of document.querySelectorAll('div,p')) {
    if ([...el.children].some(c => /^(DIV|P|TABLE)$/.test(c.tagName))) continue;
    const txt = el.innerText.trim(); if (txt.length < 40 || /^Source:/i.test(txt)) continue;
    const cs = getComputedStyle(el); if (parseInt(cs.fontWeight) >= 600) continue;
    const linkTxt = [...el.querySelectorAll('a')].map(a => a.innerText).join('').length; if (linkTxt > txt.length * 0.6) continue;
    const r = el.getBoundingClientRect(); if (!r.height) continue;
    const y = r.top + scrollY; const sec = secOf(y); if (!sec || SKIP.test(sec)) continue;
    const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2;
    // title = nearest preceding bold text in the same row
    const row = el.closest('tr') || el.parentElement; const tb = row && [...row.querySelectorAll('td,div,b,strong,a')].find(x => parseInt(getComputedStyle(x).fontWeight) >= 600 && x.innerText.trim());
    out.push({sec, title: tb ? tb.innerText.trim().slice(0, 60) : '', lines: Math.round(r.height / lh), text: txt.slice(0, 80)});
  }
  return out;
}
