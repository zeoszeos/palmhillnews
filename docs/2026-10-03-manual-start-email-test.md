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
