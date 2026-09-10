#!/usr/bin/env python3
"""Why each guide exists — the question it answers and where that question was found.
Landscape A4, compact branded header (house exception for wide grids), Chrome → PDF.
Re-run after adding guides: edit ROWS."""
import subprocess, os, base64
OUT   = os.path.expanduser("~/Documents/Marine HQ/MHQ-Guides-Why-Each-Guide-Exists.pdf")
HTML  = os.path.expanduser("~/Documents/Marine HQ/marinehq-guides/docs/demand_table.html")
LOGO  = os.path.expanduser("~/Documents/Marine HQ/marinehq-app/brand/logo_navy.png")
CHROME= "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
logo = "data:image/png;base64," + base64.b64encode(open(LOGO,"rb").read()).decode()

ROWS = [  # guide, question(s) people ask, where found, signal
 ("Cost of owning a yacht on the Gold Coast",
  "&ldquo;How much does it cost to moor a boat on the Gold Coast?&rdquo; &middot; &ldquo;How much does boat rego cost in QLD?&rdquo; &middot; &ldquo;I&rsquo;ve been trying to ascertain the real cost of yacht ownership&hellip;&rdquo;",
  "Google AU <b>People also ask</b> for <i>how much does it cost to own a boat gold coast</i>; Seabreeze forum thread <i>The REAL cost of ownership</i>; Neptune Oceanic FAQ (competitor, 23 May 2026)",
  "Competitor page ranks #4 but uses Geelong figures and no Gold Coast numbers. Nobody publishes a Gold Coast worked example."),
 ("Antifouling on the Gold Coast",
  "&ldquo;How much does antifouling cost?&rdquo; &middot; &ldquo;How often should you antifoul a boat in Australia?&rdquo; &middot; &ldquo;Is Propspeed included in a standard antifouling quote?&rdquo;",
  "Google AU People also ask for <i>antifouling cost gold coast</i>; Cruisers Forum <i>Gold Coast anti-fouling locations</i>; YBW poll (97 votes, 53% every 12 months); Neptune Oceanic and Antifoul Solutions cost guides (Apr&ndash;May 2026)",
  "GCCM&rsquo;s $89.50/ft package is the featured result. No page builds the full 60 ft bill line by line."),
 ("Gold Coast marinas compared",
  "&ldquo;What are the best marinas on the Gold Coast?&rdquo; &middot; &ldquo;How much does it cost to moor a boat on the Gold Coast?&rdquo; &middot; &ldquo;Can you live on a boat in a marina in Queensland?&rdquo;",
  "Google AU People also ask for <i>best marina gold coast</i> and <i>gold coast marina fees</i>; Trawler Forum <i>Gold Coast Berth</i>; Cruisers Forum; Reddit r/GoldCoast (14 comments); Facebook <i>Gold Coast Boating Scene</i>",
  "Related searches: <i>cheap marina berths for rent</i>, <i>liveaboard marinas</i>, <i>berths for sale</i>. The existing listicle covers 9 marinas with no prices."),
 ("The annual haul-out checklist",
  "&ldquo;How often should a boat be hauled out?&rdquo; &middot; &ldquo;What should be on a yacht haul-out checklist?&rdquo; &middot; &ldquo;Planning our first haul out in 7 years&hellip; stabiliser service, bottom paint, a new thru-hull&rdquo;",
  "Google AU People also ask for <i>boat haul out checklist</i>; Yacht Maintenance Hub FAQ (Jul 2026); Nautilus Insurance guide quoting The Boat Works (Apr 2026); Cruisers Forum and Sam&rsquo;s Marine (Hatteras) threads",
  "Evergreen topic; page 1 is all US/UK pages. No Australian yard or manager has a checklist page."),
 ("Sanctuary Cove boat show 2027",
  "&ldquo;Can you buy Sanctuary Cove boat show tickets at the gate?&rdquo; &middot; &ldquo;How much are the tickets?&rdquo; &middot; &ldquo;What is the biggest boat show in Australia?&rdquo;",
  "Google AU People also ask for <i>sanctuary cove boat show 2027</i>; official SCIBS ticketing FAQ (&ldquo;2027 prices yet to be announced&rdquo;); Marine Business News, 19 Aug 2026",
  "Related searches: <i>2027 tickets</i>, <i>schedule</i>, <i>dates</i>, <i>exhibitors</i>. Early-mover window before the official pages fill in."),
 ("Gold Coast to Sydney by motor yacht",
  "&ldquo;How long does it take to go from Gold Coast to Sydney?&rdquo; &middot; &ldquo;How far is the Gold Coast from Sydney in nautical miles?&rdquo; &middot; &ldquo;&hellip;knowledge on entering bars along the way&rdquo;",
  "Google AU People also ask for <i>gold coast to sydney by boat</i>; Seabreeze <i>Passage Planning Sydney to Brisbane</i> (multi-page); MV Pikorua motor-boat blog (Feb 2025); Trawler Forum",
  "The #1 result is a private blog. Almost all community content is sailing; the motor-yacht version does not exist."),
 ("Gold Coast to the Whitsundays by motor yacht",
  "&ldquo;How far is Whitsunday from the Gold Coast?&rdquo; &middot; &ldquo;When to avoid Whitsundays?&rdquo; &middot; &ldquo;Wide Bay Bar &mdash; anyone entered between Inskip Point and South Spit?&rdquo;",
  "Google AU People also ask for <i>gold coast to whitsundays by boat</i>; Seabreeze Wide Bay Bar thread (QLD owners, same-day replies); Riviera and Maritimo convoy pages and video (4.7K views); Facebook <i>Whitsunday Sailing Crew Finder</i>",
  "Rome2Rio (ferry and train) ranks #1, so nobody owns the boating intent. Builders&rsquo; marketing is the only motor-yacht voice."),
 ("Detailing and ceramic coating",
  "&ldquo;What is the typical cost range for ceramic coating on the Gold Coast?&rdquo; &middot; &ldquo;What is the downside of ceramic coating?&rdquo; &middot; &ldquo;Is it worth it, would you do it again?&rdquo;",
  "Google AU People also ask for <i>boat ceramic coating cost gold coast</i>; Tugnuts (19 replies); The Hull Truth ceramic threads (2022&ndash;2025); Neptune Oceanic detailing guide (Jul 2026, no numbers)",
  "Gold Coast results are car detailers. Only marine result is The Boat Butler with no price. No Australian page states $/ft or a wash-down cadence."),
 ("Do you need full-time crew? Can I drive her myself?",
  "&ldquo;Can I captain my own yacht?&rdquo; &middot; &ldquo;What is the largest yacht you can drive alone?&rdquo; &middot; &ldquo;At what point do I need to have a captain on my boat? I&rsquo;ve heard 24 metres is a threshold&hellip;&rdquo; &middot; &ldquo;Just purchased a 60&rsquo; motor yacht and lack experience&hellip; need training and to hire a captain for a while&rdquo;",
  "Google AU People also ask for <i>do i need a captain for my yacht</i> and <i>can i drive my own yacht australia</i>; Trawler Forum <i>At what point do I need a captain</i> (3 pages, ~60 posts); YachtForums; Quora (40+ answers); Reddit r/boating (26 answers); boatsales <i>How big a boat can I drive in Australia?</i>",
  "The universal answer online is &ldquo;no law, but your insurer will want a captain&rdquo;. Nobody covers the Queensland rules, the real crew costs, or what happens when a captain leaves."),
 ("MyYacht: the owner app, screen by screen",
  "&ldquo;What is yacht management and why is it important?&rdquo; &middot; &ldquo;What does a yacht manager do on a day-to-day basis?&rdquo; &middot; &ldquo;Who looks after your boat when you&rsquo;re not on board?&rdquo;",
  "Competitor pages Chapman Yachting (Oct 2024, Apr 2026), Neptune Oceanic (May 2026), Southern Right Yachting; our own Dock Talk interviews at SCIBS 2026",
  "Every competitor describes management in words; none shows the owner what they will actually see. This guide is the app, screen by screen, on the demo yacht."),
 ("What size boat should I get?",
  "&ldquo;What size boat should I buy?&rdquo; &middot; &ldquo;What size boat do I need for a family of 4?&rdquo; &middot; &ldquo;What is the largest boat one can single-hand?&rdquo; &middot; &ldquo;How big is too big for a first boat?&rdquo;",
  "YachtBuyer buying guide (Aug 2026); Intermarine (Jul 2025); YBW forum (Jan 2018, 3 pages); Trawler Forum <i>Too big or too small?</i> (Feb 2023, 30 posts) and <i>Biggest boat for 1&frac12; persons</i> (Oct 2022, ~40 replies); YachtForums (3 pages); Boat Gold Coast and Club Marine buyer guides",
  "Australian forums are trailer-boat and sail; no Australian page sizes a 40&ndash;90 ft motor yacht against Gold Coast berths, depth, fuel burn and the insurers&rsquo; ten-foot rule."),
]

rows = "".join("<tr><td class='g'>%s</td><td>%s</td><td>%s</td><td class='s'>%s</td></tr>" % r for r in ROWS)
html = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@page {{ size: A4 landscape; margin: 11mm 12mm 10mm; }}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:"Helvetica Neue",Arial,sans-serif;color:#33415c;font-size:8.4pt;line-height:1.42;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.hdr{{display:flex;align-items:center;justify-content:space-between;border-bottom:2px solid #E87722;padding-bottom:7px;margin-bottom:9px}}
.hdr img{{height:34px}}
.hdr h1{{font-size:15.5pt;color:#16223f;font-weight:800;line-height:1.1}}
.hdr .k{{color:#E87722;font-size:7pt;font-weight:800;letter-spacing:2.5px;text-transform:uppercase;margin-bottom:3px}}
.hdr .r{{text-align:right;font-size:7.4pt;color:#7a8699;line-height:1.4}}
p.lede{{font-size:8.8pt;color:#33415c;margin-bottom:8px;max-width:1000px}}
table{{width:100%;border-collapse:collapse}}
th{{background:#16223f;color:#fff;text-align:left;padding:6px 8px;font-size:6.6pt;letter-spacing:1.3px;text-transform:uppercase;border-bottom:2px solid #E87722}}
td{{padding:6px 8px;border-bottom:1px solid #E6EDF6;vertical-align:top}}
tr:nth-child(even) td{{background:#F7F9FC}}
td.g{{font-weight:700;color:#16223f;width:19%;background:#EEF2F8}}
tr:nth-child(even) td.g{{background:#E9EEF6}}
td.s{{color:#4a5670;width:24%}}
td:nth-child(2){{width:29%}}
td i{{color:#16223f}} td b{{color:#16223f}}
.new{{display:inline-block;background:#E87722;color:#fff;font-size:6pt;letter-spacing:1px;text-transform:uppercase;padding:1px 5px;border-radius:3px;margin-left:4px;vertical-align:middle}}
.foot{{margin-top:8px;display:flex;justify-content:space-between;font-size:7pt;color:#7a8699;border-top:1px solid #DCE5F1;padding-top:5px}}
.note{{font-size:7.4pt;color:#4a5670;margin-top:7px;background:#FFF6EF;border-left:3px solid #E87722;padding:6px 9px}}
</style></head><body>
<div class="hdr"><div><div class="k">Marine HQ Guides &middot; internal</div><h1>Why each guide exists</h1></div>
<div class="r">The question it answers, and where that question was found<br>Compiled 10 September 2026 &middot; guides.marinehq.com.au</div><img src="{logo}" alt="Marine HQ"></div>
<p class="lede">Every guide was written to answer a question owners are already asking. This is the evidence: the wording people use, where it appears, and what is missing from the pages that currently rank. The gap column is the reason the guide can win.</p>
<table><tr><th>Guide</th><th>The question, as people ask it</th><th>Where the question was found</th><th>What is missing online (our opening)</th></tr>{rows}</table>
<div class="note"><b>Honest note on volumes.</b> No keyword-tool numbers are in this table: the Ahrefs connector is not authorised and Google&rsquo;s Keyword Planner was not accessible. Every signal is a real Google &ldquo;People also ask&rdquo; box, a related-search suggestion, or a forum thread with its reply count and date. Full source links are in the research file in the Guides project (docs/demand-research.md).</div>
<div class="foot"><span>Marine HQ Pty Ltd &middot; ABN 38 661 097 221 &middot; 76/84 Waterway Dr, Coomera QLD 4209</span><span>0439 748 387 &middot; yachtsupport@marinehq.com.au &middot; www.marinehq.com.au</span></div>
</body></html>'''
open(HTML,"w",encoding="utf-8").write(html)
subprocess.run([CHROME,"--headless=new","--disable-gpu","--no-pdf-header-footer","--print-to-pdf="+OUT,"file://"+HTML],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
subprocess.run(["xattr","-c",OUT]); print("PDF:",OUT)
