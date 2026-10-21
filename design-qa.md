# Corporate reference implementation QA

Source visual truth: the user's second attachment in this conversation, the HSE Risk Index corporate homepage (1448 × 1086 px). The image is visible in the conversation; no original source file or official logo file was supplied on disk. Scope is the requested corporate direction and composition, adapted to the existing working application.

Implementation evidence: `tests/artifacts/corporate-home-reference-viewport.png` (1448 × 1086 px), `tests/artifacts/corporate-home-full.png`, `tests/artifacts/design-overview-375.png`, `tests/artifacts/design-assessment-320.png`, and `tests/artifacts/corporate-gemini-qa.png`. A compressed desktop capture is retained at `docs/images/corporate-home.webp`.

Viewport: desktop browser 1449 × 1240 CSS px, component 1448 px wide, deviceScaleFactor 1. Reference and primary implementation capture are both 1448 × 1086 pixels; no density scaling applied. Mobile checks cover 320/375/768/1024 CSS px as appropriate. State: authenticated administrator with clearly synthetic QA site data. The reference's fictional name/avatar/notifications are intentionally replaced with the actual authenticated identity and implemented functions.

## Comparison history and fixes

- Earlier P1: the first application screenshot used a large Streamlit sidebar and 17 flat module links, dominating the working area. Fixed with a white corporate header, compact primary navigation, an accessible module drawer and native account/profile/logout routes. The final desktop and mobile captures show the replacement.
- Earlier P1: the reference's photographic composition and structured homepage were absent. Fixed with a generated hero derived from the supplied reference, a reconstructed raster mark, four real workflow links and a benefits band. Full-view comparison now follows the supplied header/hero/process/benefits hierarchy.
- Earlier P2: mobile navigation clipped the final primary action. Fixed with five equal mobile navigation tracks and wrapped labels, keeping AI and account controls available.
- Earlier P2: the compact module toggle lacked an accessible name when its label was hidden. Added a persistent aria-label; automated axe checks pass.

## Required fidelity surfaces

- Typography: locally bundled Inter, strong navy display hierarchy, three-line desktop headline, compact navigation and lighter body text. The original font file was not supplied; Inter is the chosen available visual match.
- Layout rhythm: white 80 px desktop header, full-bleed photographic hero, four process cards and a pale benefits panel. The real site selector adds a context strip absent from the illustrative mockup; this is an intentional product constraint. Functional record counters remain below the primary reference composition.
- Colors: navy headings, technical blue actions, teal/cyan title emphasis, orange/green technology accents and light blue/green/orange/violet cards. Focus and error states remain visible.
- Images: local WebP hero and mark generated from the supplied reference, not placeholders or code-drawn artwork. They are illustrative assets, not a claim to show a user's real worksite or an original official brand file. Standard icons are licensed Phosphor assets; font and icon licenses are included.
- Content: all navigation and CTAs resolve to actual modules. No fictional notifications, users, safety guarantees or KPI data were added. Company navigation follows its actual permissions. Risk Index formulas and the original domain/WordPress files remain unchanged.

Focused checks covered the header/logo/navigation, hero headline/crop/actions, process-card typography, assessment form, module drawer and Gemini consent/status. The supplied reference does not specify forms or AI screens; these use the same tokens and existing functional requirements rather than an invented second visual source.

## Functional evidence

Build passed. The existing browser suite passed calculate/save/history, relogin persistence, all export formats, photos/annotation, Italian OCR and PDF import. All 17 module views passed automated axe and overflow checks at 375/1440 px; assessment widths 320/768/1024/1440 passed. Manager, reader, company and outsider checks passed. Corporate navigation, account/profile/password access, return navigation and logout passed, with no browser console errors.

Gemini was exercised through the actual Streamlit bridge using synthetic Secrets named `Gemini API Key` and a mocked server provider: no provider call without consent, one explicit call, response rendered as plain text, key absent from frontend, confidential classification unavailable. No real Google call or production Secrets edit was performed.

## Follow-up polish

P3: replace the reconstructed mark with the official original logo if supplied. Production Streamlit rendering and a real Gemini provider call require access to the user's app and configured Secrets. Automated accessibility checks do not certify WCAG.

final result: passed
