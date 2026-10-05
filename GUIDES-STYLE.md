# Marine HQ Guides — house style (the "skill")

Read this before writing or editing any guide. It is the one place the rules live. When Trish
corrects something, change it HERE so the next guide follows it automatically.

## What a guide is for
A guide is a lead engine that happens to look like an article. Every guide answers a question a
Gold Coast yacht owner actually types into Google, answers it properly with real numbers and sources,
and ends with a way to call Marine HQ. It is not a diary post and it is not an advert.

## Before writing
1. **Search first.** Check what people actually search (Google autocomplete, "People also ask",
   competitor pages: Chapman Yachting, Pacific Yacht Management, AusCoast, GCCM, The Boat Works).
   The title should match the way an owner phrases the question.
2. **Research with sources.** Every figure comes from a named, current source (official site first).
   No invented prices. If a number cannot be sourced, say "ask for a quote" rather than guess.
3. **No client data.** Never use a managed vessel's name, owner, figures or photographs. The hero
   image is the stock yacht (`assets/login-bg.jpg`) unless a licensed/own photo is added.

## Structure (the template `build.py` expects)
- **Title**: the question or promise, in the owner's words. Under 65 characters where possible.
  Include "Gold Coast" or the suburb/marina when it is a local query.
- **Description**: one sentence, 140–160 characters, the answer in miniature.
- **Opening paragraph**: give the answer straight away (a number, a range, a yes/no). No throat-clearing.
- **Key facts box** right after the opening (see components).
- **H2 sections** that follow the reader's questions in order. Short paragraphs. Tables for numbers.
- No attributed quotes. Trish asked (5 Sep 2026) for the "said by Trish" quote blocks to be removed; do not add `{{quote}}` or any quote in her name.
- `{{cta}}` roughly two-thirds through — the mid-article call.
- **A worked example** with the arithmetic shown, whenever the topic is a cost.
- **"What we do"** or **"What to check"** section near the end — practical, first person plural.
- **FAQ**: 4–7 real questions (the "People also ask" ones), 1–3 sentence answers.
- **Related**: 2–3 slugs. **Sources**: every URL used.
- Length: 1,200–2,200 words. A marina/brand hub page can be longer.

## Components (HTML in the markdown, `markdown="1"` on the wrapper)
```html
<div class="keyfacts" markdown="1"><span class="eyebrow">Key facts</span>
- **Berth, 60 ft** — $2,400–$3,600 a month, depending on the marina
- **Antifoul** — every 12–18 months, about $8,000–$12,000 all in
</div>

<div class="callout" markdown="1"><span class="eyebrow">Worth knowing</span>
Text…</div>                      <!-- .callout.orange = warning/cost trap, .callout.green = good news -->

<div class="stat-row"><div class="stat"><b>$85/ft</b><span>GCCM antifoul package</span></div>…</div>

<ol class="steps"><li><b>Step name.</b> What happens.</li></ol>
```
Tables: Markdown pipe tables. First column is the label (rendered bold). Right-align money with
`{: .num}` is not supported — keep numbers in their own column and let the table handle it.

## Voice
- Australian English (colour, organise, licence, metres, litres, A$ written as $).
- Plain, direct, warm. Short sentences. The reader is busy and probably on a phone.
- "You" for the owner, "we" for Marine HQ. "Your yacht", "she/her" for the vessel is fine.
- No hype words (world-class, bespoke, seamless, unparalleled). No exclamation marks.
- Honest about cost and hassle. Owners trust the guide that tells them the antifoul will be $10k.
- Mention Marine HQ where it is genuinely relevant (we do this, here is what we check), never every paragraph.

## Local specifics to get right
- Gold Coast marinas: Sanctuary Cove, Southport Yacht Club (Main Beach + Hollywell), The Boat Works,
  Gold Coast City Marina & Shipyard (GCCM), Hope Harbour, Marina Mirage, Runaway Bay, Horizon Shores.
- Coomera River is tidal with 6-knot zones; the Gold Coast Seaway is the way to open water.
- Queensland: TMR registration, Maritime Safety Queensland rules, warm water = faster fouling.
- Marine HQ is at 76 - 84 Waterway Dr, Coomera QLD 4209 (bases: The Boat Works and GCCM) · 0439 748 387 · yachtsupport@marinehq.com.au.

## Adding a guide (the routine)
1. `content/<slug>.md` with the JSON front matter (copy an existing guide).
2. `python3 build.py --check` — fix anything it flags (no quote, no FAQ, no sources, US spelling).
3. Open `site/guides/<slug>/index.html` locally and read it on a phone-width window.
4. Commit and push — Netlify publishes it. Add the new guide to related lists of its neighbours.
5. Every guide has an `updated` date. Refresh prices at least every 6 months (scheduled task).

## Don'ts
- Don't publish a number without a source. Don't round a sourced number into something that sounds nicer.
- Don't use client vessels, owners, crew names or Marine HQ internal pricing.
- Don't write "in this article we will…" — just write it.
- Don't put more than one CTA block in the body (the sidebar and footer already carry it).

## Photos (added 6 Sep 2026 — Trish: "what about adding some pics")
- Photos live in `site/assets/photos/` (re-encoded JPEG, max 1800px, EXIF/GPS stripped). Source = the
  `Marine HQ Website pics` library (already public on marinehq.com.au) — **never** a photo that shows a
  managed vessel's name, hull number, owner or crew face without checking with Trish first.
- Each guide sets its own `"hero": "assets/photos/<file>.jpg"` in the front matter. Pick the photo that
  matches the subject (yard shots for maintenance, open water for passages, marina for berthing).
- In the body, one or two figures per guide at most, where a picture explains something words cannot:
  ```html
  <figure><img src="/assets/photos/running-gear.jpg" alt="Props, shafts and rudders on the hardstand" loading="lazy"><figcaption><b>Running gear</b> — what Propspeed and new anodes protect.</figcaption></figure>
  <div class="figrow"><figure>…</figure><figure>…</figure></div>   <!-- two side by side -->
  ```
- Always write a real `alt` and a caption that adds a fact. No stock-photo filler; if there is no honest
  photo, use none.

## Audience size range (3 Oct 2026 — Trish: "make it 40 – 120 ft boats")
The guides are written for owners of **40 to 120 ft** motor yachts (was 40–90). Say "40 to 120 ft" wherever a range is given. Above about 82 ft most rates are quote-only, so give the sourced figures that exist (GCCM 2022 schedule 91–110 ft, Crew Pacific 100–120 ft crew pay) and say plainly where a price is on application.

## Where Marine HQ is based (4 Oct 2026 — Trish: "put Gold Coast City Marina as base also… so both")
Marine HQ has **two bases in the Coomera marine precinct: The Boat Works and Gold Coast City Marina & Shipyard (GCCM)**. Say both, never one alone. On maps both carry the orange `hq` pin. Address is written **76 - 84 Waterway Dr, Coomera QLD 4209** (not 76/84).

## Products in guides (4 Oct 2026)
- The catalogue is `content/_products.json` (id, name, price, status ready|soon, img, blurb, includes, format, buy). Prices are Trish's, locked 22 Sep 2026: checklists $7, haul-out $12, calculator $17, programme $29, kit $49.
- Put `{{product:<id>}}` on its own line where the product genuinely helps the reader (one per guide, never next to `{{cta}}`). It renders a product block linking to `/owners-kit/#<id>`.
- `status: soon` shows "Coming soon" and a "Tell me when it is ready" button. Never mark a product `ready` until its PDF exists in `~/Documents/Marine HQ/Products/`.
- When a checkout link exists, paste it into the product's `buy` field; the button becomes "Buy now".
- SOP and Vessel Dossier prices are NOT published on the guides; they are "quoted per yacht".
- `/links/` is the Instagram bio page; edit `LINKS` in build.py.

## Colour (4 Oct 2026)

- No filled dark-blue blocks and no filled orange blocks, on pages or in the product PDFs.
- Navy is for type and hairlines. Orange is a note only: a thin rule, a small label, a bullet, a number.
- Panels sit on white or the pale wash with a 2px orange top line. Buttons are outlined, never filled.
- Hero = light ground, navy headline, then the photo shown clean (no navy wash over it).
- Table headers are a pale tint with navy type and an orange underline.
- The top menu bar is white too (navy logo, navy tracked small caps, hairline under). It no longer copies the navy bar on www.marinehq.com.au.

## The luxury look (4 Oct 2026)

- White everywhere. Big, clean photography. Thin 1px lines. Square corners. Tracked small-cap labels. Plenty of air.
- Guide cards lead with a photo (`THUMBS` in build.py picks one per guide so a row never repeats a picture).
- Headlines are light-weight Bodoni, large. Buttons are 1px outlined, square.
- The product PDFs follow the same rule: no filled bands, outlined pills, orange as a hairline.

## The professional shoot: photos and video (5 Oct 2026)

- Source: 114 photos + 10 clips (Canon R6, May 2025) in
  `~/Documents/Marine HQ/Marketing/Pics/2026100465467754161cc9a3bb806d05722e1d1eae5eb68f6ee029d19fd32c05d6819b46/`.
  Web copies are made by `docs/process_shoot_photos.py` into `site/assets/photos/shoot-*.jpg`; never edit the originals.
- Rules used when choosing: no vessel name or hull lettering (painted out in the script, or the frame is skipped:
  frames 95-104 show a client yacht's name), no crew face as the subject (backs, hands, tools only, until Trish
  says who may be shown), no other company's branding (frames 41-53, and the interior-detailing clip).
- `"hero_pos": "center 60%"` in a guide's front matter sets which part of the hero photo shows in the wide band
  and on its card. `"hero_video": "<name>"` plays `site/assets/video/<name>.mp4` in the hero instead; the hero photo
  is its still frame.
- Video: silent, looping, H.264 MP4, 720p (hero 900p), under about 7 MB, cut so no face or boat name is in frame.
  In a guide body:
  ```html
  <figure class="vid"><video data-auto muted loop playsinline preload="none" poster="/assets/video/x.jpg"><source src="/assets/video/x.mp4" type="video/mp4"></video><figcaption><b>Label</b> — a caption that adds a fact.</figcaption></figure>
  ```
  `assets/video.js` plays clips only while on screen and not at all for reduced-motion visitors.
- Not used: `Sunseeker 68 Tour Reel` (one specific yacht, whose footage it is not confirmed), the `dashboard` and
  `logo` stings, and any clip section with a face or a name.
