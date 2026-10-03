# October 4 email source: manual-start audio test

Recovered from the direct MyNetWire "PH News v9" message sent October 3, 2026 at 01:14 EDT. The local workspace runner and file writer were unavailable.

- Newsletter text, graphics, and October 2 calendar data are retained from v9. This does not constitute a new calendar pull.
- Seven audio links point to the revised draft readers; autoplay query parameters are removed. Two recurring-calendar links use the same current draft preview.
- Recipient-specific mail-service unsubscribe footer is removed from this reusable source. MyNetWire should generate its own unsubscribe links when sending.
- All nine preview destinations returned HTTP 200. Seven audio page sources contain manual click handlers and no load-triggered speech.
- Clipboard and download buttons are provided in the copy screen; their browser behavior still needs a user click test.
- Preview bypass access expires October 4, 2026 at approximately 05:00 EDT. These links are for testing; permanent public links are required before a resident mailing.
- No source or preview was written to the Windows storage folder; those writes failed. Use the copy screen's Download source button to save it there manually.

Files:
- pages/2026-10-04-manual-start-email-source.txt
- pages/2026-10-04-manual-start-email-copy.html
- pages/2026-10-04-manual-start-email-preview.html

## Sentence-based reading update

All seven draft readers now split reports and stories at complete sentence boundaries, using Intl.Segmenter where available and a punctuation-based fallback for older browsers. This replaces the 65-character chunks that restarted speech in the middle of sentences.

Pause/resume and setting changes repeat the current sentence. Manual start remains required. Newsletter content, source HTML links, and the October 2 calendar snapshot are unchanged.

Verification: all article words are preserved with both segmentation methods; simulated speech callbacks confirm manual start, completion, pause/resume, speed and volume changes, Stop, and rejection of stale callbacks after cancellation. Henry's message drops from 63 speech requests to 37, and Mary's story from 47 to 28. The browser's actual audible smoothness still requires listening on PC and phone; these checks do not emulate a real voice engine.

## Video guide wording

The October 4 guide now uses the heading and browser title “Latest Committee and Board Meeting Videos.” All eight recording links use singular “Video,” including “Board Meeting Video.” Recording URLs, dates, and the link to all past committee videos are unchanged. This wording-only change was also applied to the existing public October 4 guide on main; the draft copy matches it.

The video guide has a decorative green-and-gold SVG camera before each of its eight recording links. The link to the original committee webpage has a webpage icon instead of a camera. Date labels use three-letter months (for example, Sep 30, 2026). Icons are hidden from screen readers; link text, dates, and recording URLs remain accessible. Both the public and draft guides use these changes.

The archive line is one continuous hyperlink: “See all videos at the Palm Hill committees webpage.” It retains https://www.palmhillcountryclub.net/committees/ as its destination.
