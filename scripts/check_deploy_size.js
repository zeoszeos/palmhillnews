#!/usr/bin/env node
// STYLE-RULES.md R29 (Steven, Oct 17 2026): keep the Vercel deployment small (Hobby Deployment Storage is 10 GB and
// every deployment stores a full copy of the output). Runs at the end of the Vercel buildCommand on the output
// directory, and can be run by hand: `node scripts/check_deploy_size.js public` (or with no argument after a build).
// FAILS (exit 1, so the deployment fails and the live site stays on the last good deployment) when:
//   - any PDF in the deploy tree is over 2 MiB  -> host it like the Link PDFs (scripts/link_store.py) instead;
//   - any other single file is over 5 MiB;
//   - the whole deploy tree is over 40 MiB.
// Prints the total and the five largest files either way.
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(process.argv[2] || 'public');
const MiB = 1024 * 1024, PDF_MAX = 2 * MiB, FILE_MAX = 5 * MiB, TOTAL_MAX = 40 * MiB;
const files = [];
(function walk(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) walk(p); else if (e.isFile()) files.push([fs.statSync(p).size, path.relative(ROOT, p)]);
  }
})(ROOT);
const total = files.reduce((s, f) => s + f[0], 0), fails = [];
for (const [sz, rel] of files) {
  if (/\.pdf$/i.test(rel) && sz > PDF_MAX) fails.push(`PDF over 2 MiB in deploy tree: ${rel} (${(sz / MiB).toFixed(1)} MiB)`);
  else if (sz > FILE_MAX) fails.push(`file over 5 MiB in deploy tree: ${rel} (${(sz / MiB).toFixed(1)} MiB)`);
}
if (total > TOTAL_MAX) fails.push(`deploy tree is ${(total / MiB).toFixed(1)} MiB (limit 40 MiB)`);
files.sort((a, b) => b[0] - a[0]);
console.log(`R29 deploy size: ${files.length} files, ${(total / MiB).toFixed(1)} MiB in ${ROOT}`);
for (const [sz, rel] of files.slice(0, 5)) console.log(`  ${(sz / MiB).toFixed(2)} MiB  ${rel}`);
if (fails.length) { console.error('R29 FAIL (STYLE-RULES.md R29):\n  ' + fails.join('\n  ')); process.exit(1); }
console.log('R29 OK');
