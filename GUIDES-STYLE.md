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
- `{{quote}}` after the first or second H2 — one sentence in Trish's voice (see Voice).
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
- The **quote** is Trish speaking from experience: one sentence, an opinion or a rule of thumb,
  never a sales line. e.g. "Berthing is the bill people budget for; the yard is the one that surprises them."
- Mention Marine HQ where it is genuinely relevant (we do this, here is what we check), never every paragraph.

## Local specifics to get right
- Gold Coast marinas: Sanctuary Cove, Southport Yacht Club (Main Beach + Hollywell), The Boat Works,
  Gold Coast City Marina & Shipyard (GCCM), Hope Harbour, Marina Mirage, Runaway Bay, Horizon Shores.
- Coomera River is tidal with 6-knot zones; the Gold Coast Seaway is the way to open water.
- Queensland: TMR registration, Maritime Safety Queensland rules, warm water = faster fouling.
- Marine HQ is at 76/84 Waterway Dr, Coomera QLD 4209 · 0439 748 387 · yachtsupport@marinehq.com.au.

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
