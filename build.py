#!/usr/bin/env python3
"""Marine HQ Guides — static site builder.

    python3 build.py            # builds ./site from ./content/*.md
    python3 build.py --check    # build + report anything missing (no quote, no FAQ, no sources…)

Each guide is a Markdown file in content/ with a JSON front-matter block:

    ---json
    { "title": "...", "slug": "...", "description": "...", "category": "Costs",
      "date": "2026-09-05", "updated": "2026-09-05", "hero": "assets/login-bg.jpg",
      "quote": "One sentence in Trish's voice.", "quote_by": "Trish Perez, Marine HQ",
      "faq": [ {"q": "...", "a": "..."} ],
      "related": ["other-slug", "another-slug"],
      "sources": [ {"t": "Source title", "u": "https://..."} ],
      "cta": "Optional custom CTA line" }
    ---
    Markdown body. Use {{quote}} and {{cta}} where the quote block and mid-article CTA should sit.
    Wrap key-facts / callouts in HTML with markdown="1" (see GUIDES-STYLE.md).

Outputs: site/index.html, site/guides/<slug>.html, site/<category>.html hubs, site/sitemap.xml, site/robots.txt.
House rules live in GUIDES-STYLE.md — read it before writing a guide.
"""
import os, re, json, sys, html, datetime, glob
import markdown

ROOT    = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
SITE    = os.path.join(ROOT, "site")
BASE    = "https://guides.marinehq.com.au"          # change if the guides end up under another host
PREFIX  = ""                                         # e.g. "/marinehq-guides" for a GitHub Pages review build (--prefix)
NOINDEX = False                                      # review builds: --noindex adds a robots noindex tag
GA4     = "G-657FQN68L7"                                         # Google Analytics 4 measurement id, e.g. "G-XXXXXXXXXX" (--ga). Never added to --noindex review builds.
MAIN    = "https://www.marinehq.com.au"
PHONE   = "0439 748 387"
PHONE_H = "+61439748387"
EMAIL   = "yachtsupport@marinehq.com.au"
JOBS_EMAIL = "crew@marinehq.com.au"
JOBS_LIVE = False                                      # --jobs-live: jobs.marinehq.com.au is live; /jobs/ and /apply/ here become redirects
JOBSITE = False                                        # --jobs-site: build the standalone jobs.marinehq.com.au site
JOBS_DOMAIN = "https://jobsboard.marinehq.com.au"
GUIDES_DOMAIN = "https://guides.marinehq.com.au"
APPLY_API = "https://script.google.com/macros/s/AKfycbxHJfMaCMMxG1k1a1I5WlM5dBeq4nD1q4jr-ad5cw8MTM8_5QuDi4qFpf3SjN9MyBEB/exec"   # Apps Script web app /exec URL for the applicants backend (set after deploy)
ABN     = "ABN 38 661 097 221"
ORG     = "Marine HQ"

CATEGORIES = [   # slug, label, one-liner (hub page intro)
  ("costs",       "Costs",       "What owning and running a yacht on the Gold Coast really costs, with the numbers shown."),
  ("maintenance", "Maintenance", "What each job involves, how often it is due, and what to check before you pay for it."),
  ("marinas",     "Marinas",     "Where to keep her: every Gold Coast marina, compared on the things that matter."),
  ("buying",      "Buying & selling", "Surveys, sea trials, pre-purchase checks and getting a yacht ready for sale."),
  ("cruising",    "Cruising & passages", "Taking her further: the Whitsundays, Sydney, and what to plan before you clear the Seaway."),
  ("ownership",   "Ownership",   "Crew, compliance, insurance, registration and the admin of owning a yacht."),
]
CAT_LABEL = {s: l for s, l, _ in CATEGORIES}

MD = markdown.Markdown(extensions=["tables", "attr_list", "md_in_html", "toc", "sane_lists", "smarty"],
                       extension_configs={"toc": {"toc_depth": "2"}})

def read_guide(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"^---json\s*\n(.*?)\n---\s*\n(.*)$", raw, re.S)
    if not m:
        sys.exit("No ---json front matter in %s" % path)
    meta = json.loads(m.group(1))
    body = m.group(2)
    meta.setdefault("slug", os.path.splitext(os.path.basename(path))[0])
    meta.setdefault("updated", meta.get("date"))
    meta.setdefault("hero", "assets/login-bg.jpg")
    meta.setdefault("category", "ownership")
    meta["words"] = len(re.findall(r"\w+", body))
    meta["mins"]  = max(2, round(meta["words"] / 220))
    meta["_body"] = body
    meta["_path"] = path
    return meta

def nice_date(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%-d %B %Y")

def esc(s):
    return html.escape(s or "", quote=True)

# ---------------------------------------------------------------- templates
HEAD = '''<!DOCTYPE html><html lang="en-AU"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<link rel="canonical" href="__CANON__">
<meta property="og:type" content="__OGTYPE__"><meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__"><meta property="og:url" content="__CANON__">
<meta property="og:image" content="__BASE__/assets/top_banner_optimized.jpg">
<meta property="og:site_name" content="Marine HQ Guides"><meta property="og:locale" content="en_AU">
<link rel="icon" href="/assets/white_favicon-64.png"><link rel="apple-touch-icon" href="/assets/white_icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;0,6..96,500;0,6..96,600;1,6..96,400&family=Inter:wght@300;400;500;600&family=Montserrat:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v=__V__">
__JSONLD__
</head><body>
<header class="mh">
  <div class="wrap mh-bar">
    <a class="mh-logo" href="__MAIN__/" aria-label="Marine HQ home"><img src="/assets/logo_navy.png" alt="Marine HQ"></a>
    <nav class="mh-nav" aria-label="Marine HQ">__MAINNAV__</nav>
    <div class="mh-cta"><a class="mh-phone" href="tel:__PHONE_H__">0439 748 387</a><a class="mh-contact" href="__MAIN__/contact">Contact us</a></div>
    <details class="mh-menu"><summary aria-label="Menu"><i></i><i></i><i></i></summary>
      <div class="mh-drawer">__MAINNAV__<div class="mh-drawer-sub"><span>Guides by topic</span>__NAV__<a href="/crew/">Crew placement</a><a href="/jobs/">Jobs Board</a><a href="/owners-kit/">Owner&rsquo;s Kit</a></div><a class="mh-phone" href="tel:__PHONE_H__">Call 0439 748 387</a></div>
    </details>
  </div>
</header>
<nav class="sub" aria-label="Guide sections"><div class="wrap sub-bar"><a class="sub-home" href="/">All guides</a>__NAV__<a class="sub-kit" href="/crew/">Crew placement</a><a class="sub-kit" href="/jobs/">Jobs Board</a><a class="sub-kit" href="/owners-kit/">Owner&rsquo;s Kit</a></div></nav>
'''

FOOT = '''
<footer class="foot">
  <div class="wrap">
    <div class="foot-cta">
      <div>
        <div class="eyebrow">Marine HQ &middot; Coomera, Gold Coast</div>
        <h2>Own the yacht. Leave the running of her to us.</h2>
        <p>Full vessel management for motor yachts on the Gold Coast &mdash; maintenance, shipyard periods, crew, compliance and the paperwork &mdash; with a private owner app so you can see it all being done.</p>
      </div>
      <div class="foot-actions">
        <a class="btn" href="tel:__PHONE_H__">Call __PHONE__</a>
        <a class="btn ghost" href="mailto:__EMAIL__">__EMAIL__</a>
        <a class="btn ghost" href="__MAIN__/services">What we do &rarr;</a>
      </div>
    </div>
    <img class="banner" src="/assets/bottom_banner_v2.png" alt="Marine HQ — Freedom to enjoy. m: __PHONE__ · e: __EMAIL__ · w: www.marinehq.com.au">
    <div class="foot-links">__FOOTNAV__</div>
    <p class="fine">&copy; __YEAR__ Marine HQ Pty Ltd &middot; __ABN__ &middot; 76 - 84 Waterway Dr, Coomera QLD 4209.
      Prices and figures in these guides are indicative, drawn from published sources on the date shown, and change without notice &mdash; always confirm with the provider. Nothing here is financial or legal advice.</p>
  </div>
</footer>
<script src="/assets/whatsapp-widget.js" defer></script>
<script src="/assets/video.js" defer></script>
</body></html>'''

GUIDE = '''
<section class="hero__HEROCLS__" style="--photo:url('/__HERO__');--pos:__HEROPOS__">
  <div class="wrap">
    <div class="crumbs"><a href="/">Guides</a> <span>&rsaquo;</span> <a href="/__CATSLUG__/">__CAT__</a></div>
    <h1>__H1__</h1>
    <p class="stand">__DESC__</p>
    <div class="meta"><span>Updated __UPDATED__</span><span>&middot;</span><span>__MINS__ min read</span><span>&middot;</span><span>Gold Coast, Queensland</span></div>
  </div>__HEROVID__
</section>
<main class="wrap article">
  <article class="body">
__BODY__
  </article>
  <aside class="side">
    <div class="card toc"><div class="eyebrow">In this guide</div>__TOC__</div>
    <div class="side-stick">__SIDEPROD__<div class="card cta side-cta">
      <div class="eyebrow">Talk to Marine HQ</div>
      <h3>Want this handled, not just explained?</h3>
      <p>We manage motor yachts on the Gold Coast end to end. One call and it is on our list, not yours.</p>
      <a class="btn" href="tel:__PHONE_H__">Call __PHONE__</a>
      <a class="btn ghost" href="mailto:__EMAIL__?subject=__SUBJ__">Email us</a>
    </div></div>
  </aside>
</main>
<section class="wrap tail">
__FAQ__
__CTA_END__
__RELATED__
__SOURCES__
</section>
'''

QUOTE = '''<blockquote class="pull"><p>&ldquo;__Q__&rdquo;</p><footer>&mdash; __BY__</footer></blockquote>'''

CTA_MID = '''<div class="cta mid"><div><div class="eyebrow">Marine HQ</div><strong>__LINE__</strong></div>
<a class="btn" href="tel:__PHONE_H__">Call __PHONE__</a></div>'''

CTA_END = '''<div class="cta end">
  <div><div class="eyebrow">Next step</div><h2>Rather have someone do this for you?</h2>
  <p>Marine HQ looks after motor yachts across the Gold Coast &mdash; the maintenance schedule, the yard, the trades, the crew and the compliance &mdash; and shows you every job and every dollar in your own MyYacht app. Tell us about your yacht and we will tell you what she needs.</p></div>
  <div class="foot-actions"><a class="btn" href="tel:__PHONE_H__">Call __PHONE__</a><a class="btn ghost" href="mailto:__EMAIL__?subject=__SUBJ__">Email __EMAIL__</a></div>
</div>'''

def render_faq(faq):
    if not faq: return ""
    items = "".join('<details><summary>%s</summary><div class="ans">%s</div></details>'
                    % (esc(f["q"]), MD.reset().convert(f["a"])) for f in faq)
    return '<section class="faq"><h2>Questions owners ask</h2>%s</section>' % items

def render_related(meta, guides):
    rel = [g for g in guides if g["slug"] in meta.get("related", [])]
    if not rel:
        rel = [g for g in guides if g["slug"] != meta["slug"] and g["category"] == meta["category"]][:3]
    if not rel: return ""
    cards = "".join(card(g) for g in rel)
    return '<section class="related"><h2>Read next</h2><div class="grid">%s</div></section>' % cards

def render_sources(meta):
    src = meta.get("sources") or []
    if not src: return ""
    li = "".join('<li><a href="%s" rel="nofollow noopener" target="_blank">%s</a></li>' % (esc(s["u"]), esc(s["t"])) for s in src)
    return ('<section class="sources"><h2>Where the figures come from</h2><p>Published rates and sources checked on %s. '
            'They change &mdash; confirm with the provider before you rely on them.</p><ol>%s</ol></section>'
            % (nice_date(meta["updated"]), li))

# card photo per guide, so a row of cards never repeats one picture; falls back to the guide's hero
THUMBS = {}

def hero_video(name, poster):
    """A silent looping clip in the hero, from site/assets/video/<name>.mp4. The hero photo is its still frame."""
    if not name: return ""
    return ('\n  <video class="hero-vid" data-auto autoplay muted loop playsinline preload="metadata" poster="/%s">'
            '<source src="/assets/video/%s.mp4" type="video/mp4"></video>' % (poster, name))

def card(g):
    ph = THUMBS.get(g["slug"]) or g.get("hero") or "assets/photos/shoot-underway.jpg"
    pos = "center" if g["slug"] in THUMBS else g.get("hero_pos", "center")
    return ('<a class="gcard" href="/guides/%s/"><span class="ph"><img src="/%s" alt="" loading="lazy" style="object-position:%s"></span>'
            '<span class="eyebrow">%s</span><strong>%s</strong><p>%s</p>'
            '<span class="more">%s min read &rarr;</span></a>'
            % (g["slug"], ph, pos, esc(CAT_LABEL.get(g["category"], g["category"])), esc(g["title"]), esc(g["description"]), g["mins"]))

def jsonld_guide(meta):
    url = "%s/guides/%s/" % (BASE, meta["slug"])
    art = {"@context": "https://schema.org", "@type": "Article", "headline": meta["title"],
           "description": meta["description"], "datePublished": meta["date"], "dateModified": meta["updated"],
           "inLanguage": "en-AU", "mainEntityOfPage": url, "image": BASE + "/" + meta["hero"],
           "author": {"@type": "Organization", "name": ORG, "url": MAIN},
           "publisher": {"@type": "Organization", "name": ORG, "url": MAIN,
                         "logo": {"@type": "ImageObject", "url": BASE + "/assets/logo_navy.png"}},
           "about": {"@type": "Place", "name": "Gold Coast, Queensland, Australia"}}
    out = ['<script type="application/ld+json">%s</script>' % json.dumps(art)]
    if meta.get("faq"):
        faq = {"@context": "https://schema.org", "@type": "FAQPage",
               "mainEntity": [{"@type": "Question", "name": f["q"],
                               "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", MD.reset().convert(f["a"]))}}
                              for f in meta["faq"]]}
        out.append('<script type="application/ld+json">%s</script>' % json.dumps(faq))
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Guides", "item": BASE + "/"},
        {"@type": "ListItem", "position": 2, "name": CAT_LABEL.get(meta["category"], meta["category"]), "item": "%s/%s/" % (BASE, meta["category"])},
        {"@type": "ListItem", "position": 3, "name": meta["title"], "item": url}]}
    out.append('<script type="application/ld+json">%s</script>' % json.dumps(crumbs))
    return "\n".join(out)

MAIN_NAV = [("Yacht Management", "/yacht-management-coomera"), ("Yacht Maintenance", "/yacht-maintenance-coomera"),
            ("Services", "/services"), ("Guides", None), ("Contact", "/contact"), ("About", "/about-us")]   # same order as marinehq.com.au

def main_nav_html():
    if JOBSITE:
        out = []
        for l, u in MAIN_NAV:
            if u is None:
                out.append('<a href="%s/">Guides</a><a class="on" href="/">Jobs Board</a>' % GUIDES_DOMAIN)
            else:
                out.append('<a href="%s%s">%s</a>' % (MAIN, u, l))
        return "".join(out)
    return "".join('<a class="on" href="/">%s</a>' % l if u is None else '<a href="%s%s">%s</a>' % (MAIN, u, l) for l, u in MAIN_NAV)

def nav_html():
    return "".join('<a href="/%s/">%s</a>' % (s, l) for s, l, _ in CATEGORIES)

def shell(title, desc, canon, ogtype, jsonld, inner):
    v = datetime.date.today().strftime("%Y%m%d%H%M")
    page = (HEAD.replace("__TITLE__", esc(title)).replace("__DESC__", esc(desc)).replace("__CANON__", canon)
                .replace("__OGTYPE__", ogtype).replace("__BASE__", BASE).replace("__V__", v)
                .replace("__JSONLD__", jsonld).replace("__MAINNAV__", main_nav_html()).replace("__NAV__", nav_html()).replace("__MAIN__", MAIN)
                .replace("__PHONE_H__", PHONE_H))
    foot = (FOOT.replace("__FOOTNAV__", nav_html() + '<a href="/crew/">Crew placement</a><a href="/jobs/">Jobs Board</a><a href="/owners-kit/">Owner&rsquo;s Kit</a><a href="%s">Marine HQ home</a><a href="%s/contact">Contact</a>' % (MAIN, MAIN))
                .replace("__YEAR__", str(datetime.date.today().year)).replace("__ABN__", ABN)
                .replace("__PHONE_H__", PHONE_H).replace("__PHONE__", PHONE).replace("__EMAIL__", EMAIL).replace("__MAIN__", MAIN))
    return page + inner + foot

PRODUCTS = json.load(open(os.path.join(CONTENT, "_products.json"), encoding="utf-8"))
PROD = {p["id"]: p for p in PRODUCTS["products"]}

def plabel(p):
    """Eyebrow label: the Owner's Kit, or 'Marine HQ crew documents' for the crew line."""
    return "Marine HQ crew documents" if p.get("line") == "crew" else PRODUCTS["kit_name"]

def order_link(p):
    if p.get("buy"): return p["buy"]
    ready = p["status"] == "ready"
    subj = ("Order: %s ($%d)" if ready else "Tell me when it is ready: %s ($%d)") % (p["name"], p["price"])
    body = ("Hi Marine HQ, I would like to order the %s ($%d). Please send the payment link." if ready
            else "Hi Marine HQ, please let me know when the %s ($%d) is available.") % (p["name"], p["price"])
    from urllib.parse import quote
    return "mailto:%s?subject=%s&amp;body=%s" % (EMAIL, quote(subj), quote(body))

def price_html(p, cls="price", note=False):
    """$49, or <s>$65</s> $49 when a genuine 'was' price is set. A product with "launch" set is on a dated launch price
    (the struck figure is the price it really goes up to); note=True adds the 'until' line on the full product cards."""
    if p.get("was"):
        out = '<span class="%s"><s>$%d</s> $%d</span>' % (cls, p["was"], p["price"])
        if note and p.get("launch"):
            out += '<span class="launch">Launch price until %s</span>' % esc(PRODUCTS["launch_until"])
        return out
    return '<span class="%s">$%d</span>' % (cls, p["price"])

def order_label(p):
    """Button text. With a pay page it is the product's own call to action; until then the email fallback says so."""
    if p.get("buy"): return "%s &middot; $%d" % (esc(p.get("cta", "Buy now")), p["price"])
    return ("Order by email &middot; $%d" % p["price"]) if p["status"] == "ready" else "Tell me when it is ready"

WORKS_ICONS = {
 "Excel": '<svg viewBox="0 0 22 22" aria-hidden="true"><rect x="1" y="1" width="20" height="20" rx="4" fill="#1D6F42"/><text x="11" y="16" text-anchor="middle" font-family="Arial" font-weight="800" font-size="13" fill="#fff">X</text></svg>',
 "Google Sheets": '<svg viewBox="0 0 22 22" aria-hidden="true"><rect x="1" y="1" width="20" height="20" rx="4" fill="#21A464"/><rect x="5" y="6" width="12" height="10" rx="1" fill="none" stroke="#fff" stroke-width="1.4"/><line x1="5" y1="11" x2="17" y2="11" stroke="#fff" stroke-width="1.4"/><line x1="11" y1="6" x2="11" y2="16" stroke="#fff" stroke-width="1.4"/></svg>',
 "Apple Numbers": '<svg viewBox="0 0 22 22" aria-hidden="true"><rect x="1" y="1" width="20" height="20" rx="4" fill="#fff" stroke="#CBD3E0"/><rect x="5" y="11" width="3" height="6" fill="#34C759"/><rect x="9.5" y="6" width="3" height="11" fill="#FFCC00"/><rect x="14" y="8.5" width="3" height="8.5" fill="#007AFF"/></svg>',
}
def works_html(p):
    """'Works in' badges under the format line, for products that open in several apps (the calculator)."""
    if not p.get("works_in"): return ""
    return '<p class="works"><span class="eyebrow">Works in</span>%s</p>' % "".join('<span>%s%s</span>' % (WORKS_ICONS.get(w, ""), esc(w)) for w in p["works_in"])

def render_product(pid):
    p = PROD[pid]
    img = ('<img src="/%s" alt="%s, first page" loading="lazy">' % (p["img"], esc(p["name"]))) if p.get("img") else '<div class="prod-ph">%s</div>' % esc(p["short"])
    soon = "" if p["status"] == "ready" else '<span class="soon">Coming soon</span>'
    return ('<aside class="prod"><a class="prod-img" href="/owners-kit/#%s">%s</a><div class="prod-txt"><span class="eyebrow">From %s %s</span>'
            '<strong>%s</strong><p>%s</p>%s<div class="prod-act">%s<a class="btn" href="%s">%s</a>'
            '<a class="prod-more" href="/owners-kit/#%s">What is inside</a></div></div></aside>'
            % (p["id"], img, esc(plabel(p)), soon, esc(p["name"]), esc(p["blurb"]), works_html(p), price_html(p), order_link(p), order_label(p), p["id"]))

def product_strip(pid):
    """One slim line early in a guide, so the product is seen before the reader is most of the way down."""
    p = PROD[pid]
    img = ('<img src="/%s" alt="" loading="lazy">' % p["img"]) if p.get("img") else ""
    return ('<a class="pstrip" href="/owners-kit/#%s">%s<span class="t"><span class="eyebrow">From %s</span><strong>%s</strong></span>'
            '%s<span class="go">See it &rarr;</span></a>' % (p["id"], img, esc(plabel(p)), esc(p["name"]), price_html(p)))

def product_side(pid):
    """The same product as a card in the side column (desktop), which stays in view while the guide scrolls."""
    p = PROD[pid]
    img = ('<img src="/%s" alt="%s, first page" loading="lazy">' % (p["img"], esc(p["name"]))) if p.get("img") else ""
    return ('<a class="side-prod" href="/owners-kit/#%s"><span class="eyebrow">From %s</span>%s<strong>%s</strong>'
            '<span class="sp-row">%s<span class="go">See what is inside &rarr;</span></span></a>'
            % (p["id"], esc(plabel(p)), img, esc(p["short"]), price_html(p)))

def kit_row():
    """Home page: the five products in one row, above the guides."""
    cards = "".join('<a class="kitcard" href="/owners-kit/#%s"><span class="ph"><img src="/%s" alt="%s" loading="lazy"></span>'
                    '<strong>%s</strong>%s</a>' % (p["id"], p["img"], esc(p["name"]), esc(p["short"]), price_html(p))
                    for p in PRODUCTS["products"] if p.get("img") and p["status"] == "ready" and p.get("line") != "crew")
    return ('<section class="cat kitrow"><div class="cat-head"><h2><a href="/owners-kit/">%s</a></h2>'
            '<p>The checklists, schedule and cost calculator our crews work to, written for owners who run their own yacht. From $7.</p></div>'
            '<div class="kitgrid">%s</div><a class="kit-all" href="/owners-kit/">See everything in the kit &rarr;</a></section>'
            % (esc(PRODUCTS["kit_name"]), cards))

def build_shop():
    cards = []
    crew_head = False
    for p in PRODUCTS["products"]:
        if p.get("line") == "crew" and not crew_head:
            crew_head = True
            cards.append('<div class="shop-sub"><span class="eyebrow">Crew documents</span><h2>Hiring crew, and starting out in yachting</h2><p>Two documents written from the same crew guides as this site, for owners who hire and for people who want to work on yachts in Australia.</p></div>')
        img = ('<img src="/%s" alt="%s, first page" loading="lazy">' % (p["img"], esc(p["name"]))) if p.get("img") else '<div class="prod-ph">%s</div>' % esc(p["short"])
        soon = "" if p["status"] == "ready" else '<span class="soon">Coming soon</span>'
        inc = "".join("<li>%s</li>" % esc(i) for i in p["includes"])
        cards.append('<article class="shopcard%s" id="%s"><div class="shop-img">%s</div><div class="shop-txt"><h2>%s %s</h2><p class="blurb">%s</p><ul>%s</ul>'
                     '<p class="fmt">%s</p>%s<div class="prod-act">%s<a class="btn" href="%s">%s</a></div></div></article>'
                     % (" is-kit" if p["id"] == "kit" else "", p["id"], img, esc(p["name"]), soon, esc(p["blurb"]), inc, esc(p["format"]), works_html(p), price_html(p), order_link(p), order_label(p)))
    inner = ('<section class="hero small"><div class="wrap"><div class="crumbs"><a href="/">Guides</a> <span>&rsaquo;</span> Owner&rsquo;s Kit</div>'
             '<h1>%s</h1><p class="stand">The checklists and schedules our crews work to, written for owners who run their own yacht. Download, print, keep aboard.</p></div></section>'
             '<main class="wrap shop"><p class="shop-note">%s Questions: <a href="tel:%s">%s</a>.</p><p class="launch-note">Launch prices until %s</p>%s'
             '<section class="shop-done"><div class="eyebrow">Rather have it written for your yacht?</div><h2>SOPs and the Vessel Dossier</h2>'
             '<p>These are general documents for any motor yacht. Marine HQ also writes vessel-specific Standard Operating Procedures and a bound Vessel Dossier for individual yachts: her particulars, emergency response card, safety checklist, maintenance schedule and the procedures her crew work to.</p>'
             '<div class="foot-actions"><a class="btn" href="/guides/yacht-sops-standard-operating-procedures/">Read the SOP guide</a><a class="btn ghost" href="mailto:%s?subject=SOPs%%20and%%20Vessel%%20Dossier%%20enquiry">Ask about SOPs for your yacht</a></div></section></main>'
             % (esc(PRODUCTS["kit_name"]), esc(PRODUCTS["order_note"]), PHONE_H, PHONE, esc(PRODUCTS["launch_until"]), "".join(cards), EMAIL))
    jl = "".join('<script type="application/ld+json">%s</script>' % json.dumps({"@context": "https://schema.org", "@type": "Product", "name": p["name"],
          "description": p["blurb"], "brand": {"@type": "Organization", "name": ORG}, "image": (BASE + "/" + p["img"]) if p.get("img") else BASE + "/assets/top_banner_optimized.jpg",
          "offers": {"@type": "Offer", "price": str(p["price"]), "priceCurrency": "AUD", "url": BASE + "/owners-kit/#" + p["id"],
                     "availability": "https://schema.org/" + ("InStock" if p["status"] == "ready" else "PreOrder")}}) for p in PRODUCTS["products"])
    page = shell("%s — checklists and schedules for yacht owners | Marine HQ" % PRODUCTS["kit_name"],
                 "Pre-departure, stand-down and wash-down checklists, the annual haul-out checklist, a running cost calculator and a scheduled maintenance programme for motor yacht owners. From $7.",
                 BASE + "/owners-kit/", "website", jl, inner)
    os.makedirs(os.path.join(SITE, "owners-kit"), exist_ok=True)
    write_page(os.path.join(SITE, "owners-kit", "index.html"), page)

CREW_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSe_rfRTPSsm-Xd5MFaZYx9pCNVsvkIeXZveDmQXO5ZgIG_pRw/viewform"

def build_crew():
    """/crew/ : Marine HQ crew placement. Owners who need crew, and crew who want work (the register form)."""
    from urllib.parse import quote
    need_mail = "mailto:%s?subject=%s&amp;body=%s" % (EMAIL, quote("Crew enquiry"), quote("Hi Marine HQ, I am looking for crew.\n\nRole:\nBoat (make, length, home port):\nPermanent, seasonal, relief or delivery:\nStart date:\n\nMy name and number:\n"))
    inner = ('<section class="hero small"><div class="wrap"><div class="crumbs"><a href="/">Guides</a> <span>&rsaquo;</span> Crew placement</div>'
             '<h1>Yacht crew placement across Australia</h1>'
             '<p class="stand">Captains, engineers, mates, deckhands, stewards and chefs for motor yachts, for permanent roles, seasons, deliveries and day work. For owners who need crew, and for crew who want a boat.</p></div></section>'
             '<main class="wrap shop"><div class="crew-two">'
             '<section class="crew-card"><span class="eyebrow">Owners, captains and managers</span><h2>I need crew</h2>'
             '<p>Tell us the boat, the role and the dates. We find and check the people, introduce you to a shortlist and help with the start. We are a yacht management company first, so we place people who will work on boats like yours.</p>'
             '<ul><li>Permanent roles, seasons, relief cover and deliveries</li><li>Certificates, medical, sea time and references checked before a CV reaches you</li><li>A written agreement, a handover list and a check-in once they are aboard</li></ul>'
             '<div class="foot-actions"><a class="btn" href="%s">Tell us what you need</a><a class="btn ghost" href="/guides/how-to-hire-yacht-crew-australia/">Read the hiring guide</a></div>'
             '<p class="crew-note">Or call <a href="tel:%s">%s</a>. Hiring yourself? The <a href="/owners-kit/#crew-hiring-pack">Crew Hiring Pack</a> has the interview questions, reference checks and paperwork.</p></section>'
             '<section class="crew-card"><span class="eyebrow">Captains, engineers, deck and interior crew</span><h2>I am looking for yacht work</h2>'
             '<p>Join the Marine HQ crew register. Tell us your certificates, your experience and when you are free, and we will call when a role or a few days of work comes up that fits.</p>'
             '<ul><li>Takes about five minutes</li><li>Your details stay with us and are only passed on when we are considering you for a role</li><li>Starting out? Read how to get your first yacht job</li></ul>'
             '<div class="foot-actions"><a class="btn" href="%s">Join the crew register</a><a class="btn ghost" href="/guides/how-to-get-into-the-yachting-industry-australia/">How to get into yachting</a></div>'
             '<p class="crew-note">Not ready? The <a href="/owners-kit/#crew-starter-kit">Yacht Crew Starter Kit</a> has the CV guide, messages and a job tracker.</p></section>'
             '</div></main>' % (need_mail, PHONE_H, PHONE, CREW_FORM))
    page = shell("Yacht crew placement in Australia | Marine HQ",
                 "Marine HQ places captains, engineers, mates, deckhands, stewards and chefs on motor yachts across Australia. Owners: tell us what you need. Crew: join the register.",
                 BASE + "/crew/", "website", "", inner)
    os.makedirs(os.path.join(SITE, "crew"), exist_ok=True)
    write_page(os.path.join(SITE, "crew", "index.html"), page)

def build_jobs():
    """/jobs/ : Marine HQ Jobs Board. Roles live in content/_jobs.json. Each role has a code (MHQ-JB-nnn) that goes in the application email subject."""
    from urllib.parse import quote
    jobs = json.load(open(os.path.join(CONTENT, "_jobs.json"), encoding="utf-8"))["jobs"]
    live = [j for j in jobs if j.get("status") == "open"]
    def mail(j):
        return "mailto:%s?subject=%s&amp;body=%s" % (JOBS_EMAIL, quote("%s - %s - Application" % (j["code"], j["position"])),
            quote("Hi Marine HQ, I would like to apply for %s (%s), %s.\n\nName:\nMobile:\nTickets and certificates held:\nSea time / commercial experience:\nAvailability:\n\nCV attached.\n" % (j["position"], j["code"], j["location"])))
    details = "".join('<section class="crew-card job" id="%s" data-loc="%s" data-pos="%s"><div class="job-head"><span class="job-code">%s</span><h2>%s</h2></div>'
                      '<dl class="job-facts"><div><dt>Location</dt><dd>%s</dd></div><div><dt>Position</dt><dd>%s</dd></div><div><dt>Type</dt><dd>%s</dd></div><div><dt>Start</dt><dd>%s</dd></div></dl>'
                      '<p>%s</p><p><strong>What we are looking for</strong></p><ul>%s</ul>'
                      '<div class="foot-actions"><a class="btn" href="%s">Apply for %s</a></div></section>'
                      % (j["id"], esc(j["location"]), esc(j.get("family", j["position"])), j["code"], esc(j["title"]), esc(j["location"]), esc(j["position"]), esc(j["type"]), esc(j["start"]), esc(j["summary"]),
                         "".join("<li>%s</li>" % esc(n) for n in j["needs"]), "/apply/?job=" + j["code"], j["code"]) for j in live)
    locs = sorted({j["location"] for j in live}); poss = sorted({j.get("family", j["position"]) for j in live})
    opt = lambda xs: "".join('<option value="%s">%s</option>' % (esc(x), esc(x)) for x in xs)
    filt = ('<div class="jobs-filter" id="jobsFilter" hidden><label>Location<select id="fLoc"><option value="">All locations</option>%s</select></label>'
            '<label>Position<select id="fPos"><option value="">All positions</option>%s</select></label>'
            '<span class="jobs-count" id="fCount" aria-live="polite"></span></div>'
            '<p class="jobs-none" id="fNone" hidden>No jobs match that selection. <a href="/crew/">Join the crew register</a> and we will call when one comes up.</p>'
            '<script>document.addEventListener("DOMContentLoaded",function(){var f=document.getElementById("jobsFilter");if(!f)return;f.hidden=false;var L=document.getElementById("fLoc"),P=document.getElementById("fPos"),C=document.getElementById("fCount"),N=document.getElementById("fNone"),J=[].slice.call(document.querySelectorAll(".job"));'
            'function go(){var n=0;J.forEach(function(e){var ok=(!L.value||e.dataset.loc===L.value)&&(!P.value||e.dataset.pos===P.value);e.hidden=!ok;if(ok)n++});C.textContent=n+(n===1?" job":" jobs");N.hidden=n>0}'
            'L.onchange=P.onchange=go;go()});</script>' % (opt(locs), opt(poss)))
    how = ('<section class="crew-card"><h2>How to apply</h2><ol><li>Email <a href="mailto:%s">%s</a> with your CV attached.</li>'
           '<li>If you email instead, <strong>put the job code in the subject line</strong>, for example <em>MHQ-JB-001 - Commercial Skipper - Your Name</em>.</li>'
           '<li>We will confirm by email and call if there is a fit.</li></ol>'
           '<p class="crew-note">Applying for more than one role? Send one email per code. Not seeing the right role? <a href="/crew/">Join the Marine HQ crew register</a> and we will call when something fits.</p></section>' % (JOBS_EMAIL, JOBS_EMAIL))
    about = ('<section class="crew-card"><span class="eyebrow">About Marine HQ</span><h2>Who you would be working for</h2>'
             '<p>Marine HQ looks after motor yachts for their owners. We are based at The Boat Works in Coomera on the Gold Coast and work across the Gold Coast, Sydney and the Whitsundays. We manage and maintain yachts from 40 to 120 ft, supply crew and relief skippers, run deliveries, and give owners the MyYacht app so every job, photo and document is in one place.</p>'
             '<p>We are a small, hands-on team. When work lands we need good people we can call on, so register your interest even if the timing is not right yet and we will keep you on the list.</p>'
             '<p class="crew-note"><a href="%s/about-us">More about Marine HQ</a> &middot; <a href="/crew/">Join the crew register</a></p></section>' % MAIN)
    inner = ('<section class="hero small"><div class="wrap"><div class="crumbs"><a href="/">Guides</a> <span>&rsaquo;</span> Jobs Board</div>'
             '<h1>Marine HQ Crew Jobs Board</h1>'
             '<p class="stand">Yacht crewing work that has come to us: skippers, deckhands and day work, casual and ongoing, so you can be called on when a job lands.</p></div></section>'
             '<main class="wrap shop">%s<div class="jobs-list">%s%s</div></main>' % (filt, details, how + about))
    page = shell("Crew Jobs Board: yacht crew jobs | Marine HQ",
                 "Marine HQ Crew Jobs Board. Commercial skippers and deckhands wanted in Sydney, casual and ongoing. Apply with your CV to crew@marinehq.com.au quoting the job code.",
                 BASE + "/jobs/", "website", "", inner)
    os.makedirs(os.path.join(SITE, "jobs"), exist_ok=True)
    write_page(os.path.join(SITE, "jobs", "index.html"), page)

def build_apply():
    """/apply/?job=MHQ-JB-001 : application form. Posts to the applicants Apps Script (name, contact, location, availability, CV, notes)."""
    jobs = json.load(open(os.path.join(CONTENT, "_jobs.json"), encoding="utf-8"))["jobs"]
    jl = json.dumps({j["code"]: {"position": j["position"], "location": j["location"], "title": j["title"], "type": j["type"], "start": j["start"], "summary": j["summary"], "needs": j["needs"]} for j in jobs if j.get("status") == "open"})
    inner = ('<section class="hero small"><div class="wrap"><div class="crumbs"><a href="/">Guides</a> <span>&rsaquo;</span> <a href="/jobs/">Jobs Board</a> <span>&rsaquo;</span> Apply</div>'
      '<h1>Apply to Marine HQ</h1><p class="stand" id="aFor">Tell us a little about you and upload your CV.</p></div></section>'
      '<main class="wrap shop"><div class="crew-card apply-role" id="aRole" hidden></div><div class="crew-card apply-card" id="aCard">'
      '<form id="aForm" novalidate>'
      '<div class="a-job" id="aJob" hidden></div>'
      '<label>Job<select id="aSel" name="job"><option value="GENERAL">General interest, keep me on your crew list</option></select></label>'
      '<div class="a-grid"><label>Full name *<input name="name" required autocomplete="name"></label>'
      '<label>Mobile *<input name="mobile" required type="tel" autocomplete="tel"></label>'
      '<label>Email *<input name="email" required type="email" autocomplete="email"></label>'
      '<label>Where are you based? *<input name="based" required placeholder="Suburb or town, state"></label></div>'
      '<label>When are you available? *<input name="availability" required placeholder="e.g. from 5 November, weekends, short notice any day"></label>'
      '<label>Tickets and certificates<input name="tickets" placeholder="e.g. Master up to 24 m, Coxswain, First Aid, RSA, MSIC"></label>'
      '<label>Upload your CV (PDF or Word, up to 5 MB) *<input id="aCv" type="file" accept=".pdf,.doc,.docx,application/pdf" required></label>'
      '<label>Anything else you would like to add<textarea name="notes" rows="4" placeholder="Boats you have worked on, why you are a good fit, questions for us"></textarea></label>'
      '<input class="a-hp" name="hp" tabindex="-1" autocomplete="off" aria-hidden="true">'
      '<p class="a-note">We keep your details only to contact you about work. Ask us any time and we will remove them.</p>'
      '<div class="foot-actions"><button class="btn" type="submit" id="aBtn">Send my application</button></div>'
      '<p class="a-err" id="aErr" role="alert" hidden></p></form>'
      '<div class="a-ok" id="aOk" hidden><span class="eyebrow">Application received</span><h2>Thank you</h2>'
      '<p id="aOkMsg"></p><p class="crew-note"><a href="/jobs/">Back to the Jobs Board</a></p></div></div></main>'
      '<script>(function(){var API="%s",JOBS=%s,q=new URLSearchParams(location.search).get("job"),sel=document.getElementById("aSel");'
      'Object.keys(JOBS).forEach(function(c){var o=document.createElement("option");o.value=c;o.textContent=c+" - "+JOBS[c].title;sel.appendChild(o)});'
      'if(q&&JOBS[q.toUpperCase()]){sel.value=q.toUpperCase();var b=document.getElementById("aJob");b.hidden=false;b.innerHTML="<span>"+sel.value+"</span> "+JOBS[sel.value].title;document.getElementById("aFor").textContent="Applying for "+JOBS[sel.value].position+", "+JOBS[sel.value].location+"."}'
      'function showRole(c){var r=document.getElementById("aRole"),J=JOBS[c];if(!J){r.hidden=true;return}r.hidden=false;r.innerHTML="";var e=function(t,x,cl){var n=document.createElement(t);if(cl)n.className=cl;n.textContent=x;return n};r.appendChild(e("span",c+" \\u00b7 "+J.location,"eyebrow"));r.appendChild(e("h2",J.title));var d=document.createElement("dl");d.className="job-facts";[["Location",J.location],["Position",J.position],["Type",J.type],["Start",J.start]].forEach(function(p){var w=document.createElement("div");w.appendChild(e("dt",p[0]));w.appendChild(e("dd",p[1]));d.appendChild(w)});r.appendChild(d);r.appendChild(e("p",J.summary));var s=e("p","");s.innerHTML="<strong>What we are looking for</strong>";r.appendChild(s);var u=document.createElement("ul");(J.needs||[]).forEach(function(n){u.appendChild(e("li",n))});r.appendChild(u)}'
      'sel.onchange=function(){showRole(sel.value)};showRole(sel.value);'
      'var f=document.getElementById("aForm"),err=document.getElementById("aErr"),btn=document.getElementById("aBtn");'
      'function fail(m){err.textContent=m;err.hidden=false;btn.disabled=false;btn.textContent="Send my application"}'
      'f.addEventListener("submit",function(ev){ev.preventDefault();err.hidden=true;var fd=new FormData(f),file=document.getElementById("aCv").files[0];'
      'var need=["name","mobile","email","based","availability"];for(var i=0;i<need.length;i++){if(!String(fd.get(need[i])||"").trim())return fail("Please fill in all the fields marked *.")}'
      'if(!file)return fail("Please upload your CV.");if(!/\.(pdf|docx?)$/i.test(file.name))return fail("Please upload your CV as a PDF or Word document.");if(file.size>5*1024*1024)return fail("That CV is over 5 MB. Please upload a smaller file.");'
      'btn.disabled=true;btn.textContent="Sending...";var r=new FileReader();r.onerror=function(){fail("Could not read that file. Please try another.")};'
      'r.onload=function(){var j=sel.value,p={job:j,position:(JOBS[j]||{}).position||"",location:(JOBS[j]||{}).location||"",hp:fd.get("hp"),cvName:file.name,cvType:file.type,cvB64:String(r.result).split(",")[1]};'
      'need.concat(["tickets","notes"]).forEach(function(k){p[k]=fd.get(k)});'
      'fetch(API,{method:"POST",headers:{"Content-Type":"text/plain;charset=utf-8"},body:JSON.stringify(p)}).then(function(x){return x.json()}).then(function(x){'
      'if(!x.ok)return fail(x.error||"Something went wrong.");try{if(window.gtag)gtag("event","job_application",{job_code:j,job_position:(JOBS[j]||{}).position||"",job_location:(JOBS[j]||{}).location||""})}catch(e){}f.hidden=true;document.getElementById("aOkMsg").textContent="Your reference is "+x.id+". We have emailed you a confirmation and will be in touch if there is a fit.";document.getElementById("aOk").hidden=false;window.scrollTo(0,0)})'
      '.catch(function(){fail("We could not send that just now. Please email your CV to %s with the job code in the subject.")})};r.readAsDataURL(file)})})();</script>'
      % (APPLY_API, jl, JOBS_EMAIL))
    page = shell("Apply | Marine HQ Crew Jobs Board", "Apply for a Marine HQ job: tell us about you and upload your CV.", BASE + "/apply/", "website", "", inner)
    page = page.replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1) if "noindex" not in page else page
    os.makedirs(os.path.join(SITE, "apply"), exist_ok=True)
    write_page(os.path.join(SITE, "apply", "index.html"), page)

def build_job_pages():
    """One page per open job: /<slug>/ with Google JobPosting structured data."""
    jobs = [j for j in json.load(open(os.path.join(CONTENT, "_jobs.json"), encoding="utf-8"))["jobs"] if j.get("status") == "open"]
    for j in jobs:
        slug = job_slug(j); city, _, state = [x.strip() for x in (j["location"] + ",").split(",")][:3]
        posted = datetime.date.fromisoformat(j["posted"]); valid = (posted + datetime.timedelta(days=120)).isoformat()
        desc = "<p>%s</p><p>What we are looking for:</p><ul>%s</ul>" % (esc(j["summary"]), "".join("<li>%s</li>" % esc(n) for n in j["needs"]))
        ld = {"@context": "https://schema.org/", "@type": "JobPosting", "title": j["title"], "description": desc,
              "identifier": {"@type": "PropertyValue", "name": "Marine HQ", "value": j["code"]},
              "datePosted": j["posted"], "validThrough": valid, "employmentType": ["CONTRACTOR", "PART_TIME"],
              "hiringOrganization": {"@type": "Organization", "name": "Marine HQ", "sameAs": MAIN, "logo": BASE + "/assets/logo_navy.png"},
              "jobLocation": {"@type": "Place", "address": {"@type": "PostalAddress", "addressLocality": city, "addressRegion": state, "addressCountry": "AU"}},
              "directApply": True}
        jsonld = '<script type="application/ld+json">%s</script>' % json.dumps(ld)
        inner = ('<section class="hero small"><div class="wrap"><div class="crumbs"><a href="/">Guides</a> <span>&rsaquo;</span> <a href="/jobs/">Jobs Board</a> <span>&rsaquo;</span> %s</div>'
                 '<h1>%s</h1><p class="stand">%s &middot; %s &middot; Start: %s</p></div></section>'
                 '<main class="wrap shop"><div class="jobs-list"><section class="crew-card job"><div class="job-head"><span class="job-code">%s</span><h2>About the role</h2></div>'
                 '<dl class="job-facts"><div><dt>Location</dt><dd>%s</dd></div><div><dt>Position</dt><dd>%s</dd></div><div><dt>Type</dt><dd>%s</dd></div><div><dt>Start</dt><dd>%s</dd></div></dl>'
                 '<p>%s</p><p><strong>What we are looking for</strong></p><ul>%s</ul>'
                 '<div class="foot-actions"><a class="btn" href="/apply/?job=%s">Apply for %s</a></div>'
                 '<p class="crew-note"><a href="/jobs/">&larr; All jobs</a></p></section>'
                 '<section class="crew-card"><span class="eyebrow">About Marine HQ</span><h2>Who you would be working for</h2>'
                 '<p>Marine HQ looks after motor yachts for their owners. We are based at The Boat Works in Coomera on the Gold Coast and work across the Gold Coast, Sydney and the Whitsundays, managing and maintaining yachts from 40 to 120 ft, supplying crew and relief skippers, and running deliveries.</p></section></div></main>'
                 % (esc(j["title"]), esc(j["title"]), esc(j["location"]), esc(j["type"]), esc(j["start"]), j["code"], esc(j["location"]), esc(j["position"]), esc(j["type"]), esc(j["start"]),
                    esc(j["summary"]), "".join("<li>%s</li>" % esc(n) for n in j["needs"]), j["code"], j["code"]))
        page = shell("%s | Marine HQ" % j["title"], "%s: %s, %s. %s Apply online with your CV." % (j["code"], j["position"], j["location"], j["type"]), "%s/%s/" % (BASE, slug), "website", jsonld, inner)
        os.makedirs(os.path.join(SITE, slug), exist_ok=True)
        write_page(os.path.join(SITE, slug, "index.html"), page)
    return [job_slug(j) for j in jobs]

def build_jobs_site(out):
    """Standalone site for jobs.marinehq.com.au: board at /, /apply/, one page per job, sitemap, CNAME."""
    global JOBSITE, BASE, SITE
    import shutil
    old_site = SITE
    tmp = os.path.join(ROOT, "_jobs_tmp"); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    JOBSITE, BASE, SITE = True, JOBS_DOMAIN, tmp
    shutil.copytree(os.path.join(old_site, "assets"), os.path.join(tmp, "assets"), ignore=shutil.ignore_patterns("photos", "*.mp4", "*.mov"))
    build_jobs(); build_apply(); slugs = build_job_pages()
    os.makedirs(out, exist_ok=True)
    for item in os.listdir(out):
        if item == ".git": continue
        p = os.path.join(out, item); shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    shutil.copytree(os.path.join(tmp, "assets"), os.path.join(out, "assets"))
    shutil.copy(os.path.join(tmp, "jobs", "index.html"), os.path.join(out, "index.html"))
    shutil.copytree(os.path.join(tmp, "apply"), os.path.join(out, "apply"))
    for sl in slugs: shutil.copytree(os.path.join(tmp, sl), os.path.join(out, sl))
    today = datetime.date.today().isoformat()
    urls = ["/"] + ["/%s/" % sl for sl in slugs]
    open(os.path.join(out, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join("<url><loc>%s%s</loc><lastmod>%s</lastmod></url>" % (JOBS_DOMAIN, u, today) for u in urls) + "\n</urlset>")
    open(os.path.join(out, "robots.txt"), "w").write("User-agent: *\nAllow: /\nDisallow: /apply/\nSitemap: %s/sitemap.xml\n" % JOBS_DOMAIN)
    open(os.path.join(out, "CNAME"), "w").write("jobsboard.marinehq.com.au\n"); open(os.path.join(out, ".nojekyll"), "w").write("")
    shutil.rmtree(tmp, ignore_errors=True)
    print("jobs site built -> %s (%d job pages)" % (out, len(slugs)))

def build_thanks():
    """After-payment pages for the Stripe Payment Links (crew products): /thanks/<id>/ with the download. noindex, not in the sitemap."""
    for pid, fname in (("crew-hiring-pack", "MHQ-Crew-Hiring-Pack.pdf"), ("crew-starter-kit", "MHQ-Yacht-Crew-Starter-Kit.pdf")):
        p = PROD[pid]
        inner = ('<section class="hero small"><div class="wrap"><h1>Thank you. Your %s is ready.</h1>'
                 '<p class="stand">Download it below, print it and keep it. A receipt is on its way to your email.</p></div></section>'
                 '<main class="wrap shop"><div class="foot-actions"><a class="btn" href="/dl/472187/%s" download>Download the PDF</a></div>'
                 '<p class="shop-note">Save the file somewhere you can find it again. If anything does not open, email <a href="mailto:%s">%s</a> or call <a href="tel:%s">%s</a> and we will sort it the same day.</p>'
                 '<p class="shop-note">Looking for crew, or for your next yacht? <a href="mailto:%s?subject=Crew%%20enquiry">Tell us the role, the boat and the dates.</a></p></main>'
                 % (esc(p["name"]), fname, EMAIL, EMAIL, PHONE_H, PHONE, EMAIL))
        page = shell("Thank you | Marine HQ", "Your download.", BASE + "/thanks/%s/" % pid, "website", "", inner)
        page = page.replace("<head>", '<head>\n<meta name="robots" content="noindex,nofollow">', 1)
        os.makedirs(os.path.join(SITE, "thanks", pid), exist_ok=True)
        write_page(os.path.join(SITE, "thanks", pid, "index.html"), page)

FREE_PDF = "/dl/MHQ-10-Haul-Out-Checks-FREE.pdf"
FREE_FORM = '<script id="form-script-tag-25708478" src="https://yachtsupport.systeme.io/public/remote/page/45334936e30b683521b509541ddb327b3ab87629.js"></script>'
WA_BIO = "https://wa.me/61439748387?text=Hi%20Marine%20HQ%2C%20I%20found%20you%20on%20Instagram"

def build_free():
    inc = "".join("<li>%s</li>" % i for i in [
        "Before she lifts: the sea-trial readings to take, and why",
        "On the hardstand: hull, anodes, running gear and every seacock",
        "Machinery and safety gear: what to renew and what to check the dates on",
        "What to get in writing before you sign the yard quote",
        "One page, A4, tick-box, print-ready"])
    inner = ('<section class="hero small"><div class="wrap"><div class="crumbs"><a href="/">Guides</a> <span>&rsaquo;</span> Free checklist</div>'
             '<h1>FREE Annual Haul&#8209;Out Checklist</h1><p class="stand">The ten checks our crews make sure happen every time a yacht comes out of the water. Free, and yours to print.</p></div></section>'
             '<main class="wrap freegrid"><a class="freeimg" href="/guides/annual-haul-out-checklist/"><img src="/assets/products/free-haul-out.jpg" alt="Marine HQ Annual Haul-Out Checklist, first page" loading="eager"></a>'
             '<div class="freetxt"><h2>What is in it</h2><ul class="freeinc">%s</ul>'
             '<div class="formbox"><div class="eyebrow">Where should we send it?</div><p>Put your email in and the download opens straight away.</p>%s'
             '<p class="fine">We will only use your email to send useful yacht-owner guides. Unsubscribe any time.</p></div></div></main>'
             % (inc, FREE_FORM))
    page = shell("FREE Annual Haul-Out Checklist for yacht owners | Marine HQ",
                 "A free one-page haul-out checklist from Marine HQ: the ten checks that matter when your yacht comes out of the water. Free download.",
                 BASE + "/free-haul-out-checklist/", "website", "", inner)
    os.makedirs(os.path.join(SITE, "free-haul-out-checklist", "thanks"), exist_ok=True)
    write_page(os.path.join(SITE, "free-haul-out-checklist", "index.html"), page)
    inner2 = ('<section class="hero small"><div class="wrap"><div class="crumbs"><a href="/">Guides</a> <span>&rsaquo;</span> Free checklist</div>'
              '<h1>Your checklist is ready</h1><p class="stand">Thanks. Download it, print it, and take it to the yard.</p></div></section>'
              '<main class="wrap freegrid"><a class="freeimg" href="%s"><img src="/assets/products/free-haul-out.jpg" alt="Marine HQ Annual Haul-Out Checklist, first page"></a>'
              '<div class="freetxt"><div class="foot-actions"><a class="btn" href="%s" download>Download the checklist (PDF)</a></div>'
              '<h2>Next</h2><ul class="freeinc"><li><a href="/guides/annual-haul-out-checklist/">Read the full haul-out guide</a>: what a yard period should include and cost</li>'
              '<li><a href="/guides/antifouling-gold-coast-cost/">What antifoul costs on the Gold Coast</a></li>'
              '<li><a href="/owners-kit/">The Yacht Owner&rsquo;s Kit</a>: the fuller haul-out checklist and more, from $7</li></ul>'
              '<p class="alt">Questions about your own yacht? <a href="%s">Message us on WhatsApp</a> or call <a href="tel:%s">%s</a>.</p></div></main>'
              % (FREE_PDF, FREE_PDF, WA_BIO, PHONE_H, PHONE))
    page2 = shell("Your checklist is ready | Marine HQ", "Download your free Annual Haul-Out Checklist.", BASE + "/free-haul-out-checklist/thanks/", "website", "", inner2)
    page2 = page2.replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1)
    # GA4 lead event: fires once the thank-you page loads (gtag is only present on production builds)
    page2 = page2.replace("</body>", "<script>if(window.gtag){gtag('event','generate_lead',{lead_source:'free_haul_out_checklist'});}</script>\n</body>", 1)
    write_page(os.path.join(SITE, "free-haul-out-checklist", "thanks", "index.html"), page2)

LINKS = [("FREE Annual Haul-Out Checklist", "/free-haul-out-checklist/", "Free two-page PDF"),
         ("Read the free yacht owner guides", "/", "Costs, marinas, maintenance, passages"),
         ("Let&rsquo;s chat on WhatsApp", WA_BIO, "Usually within the hour"),
         ("Yacht crew: hire or get hired", "/crew/", "Crew placement across Australia"),
         ("The Yacht Owner&rsquo;s Kit", "/owners-kit/", "Checklists and schedules from $7"),
         ("Marine HQ website", MAIN + "/", "Yacht management and maintenance"),
         ("Call %s" % PHONE, "tel:" + PHONE_H, "")]

GO = {"haul-out": "/guides/annual-haul-out-checklist/", "antifoul": "/guides/antifouling-gold-coast-cost/",
      "cost": "/guides/cost-of-owning-a-yacht-gold-coast/", "kit": "/owners-kit/", "free": "/free-haul-out-checklist/"}

def build_go():
    """Short links (under ~50 characters) for emails: systeme.io's plain email editor cuts typed links at about 52 characters."""
    for slug, dest in GO.items():
        url = BASE + dest
        os.makedirs(os.path.join(SITE, "go", slug), exist_ok=True)
        doc = ('<!DOCTYPE html><html lang="en-AU"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
               '<meta http-equiv="refresh" content="0; url=%s"><link rel="canonical" href="%s"><title>Marine HQ</title></head>'
               '<body><p>Taking you to <a href="%s">%s</a></p><script>location.replace(%s)</script></body></html>' % (url, url, url, url, json.dumps(url)))
        open(os.path.join(SITE, "go", slug, "index.html"), "w", encoding="utf-8").write(doc)
    # short file link for the free checklist PDF
    import shutil
    shutil.copyfile(os.path.join(SITE, "dl", "MHQ-10-Haul-Out-Checks-FREE.pdf"), os.path.join(SITE, "dl", "haul-out-10.pdf"))

def build_links():
    rows = "".join('<a class="lk" href="%s"><b>%s</b>%s</a>' % (u, t, ("<span>%s</span>" % d) if d else "") for t, u, d in LINKS)
    doc = ('<!DOCTYPE html><html lang="en-AU"><head>\n<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           '<title>Marine HQ — links</title><meta name="description" content="Marine HQ: yacht management on the Gold Coast. Guides, the Yacht Owner&rsquo;s Kit, and how to reach us.">'
           '<link rel="canonical" href="%s/links/"><link rel="icon" href="/assets/white_favicon-64.png">'
           '<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,500&family=Inter:wght@400;600&family=Montserrat:wght@700&display=swap" rel="stylesheet">'
           '<link rel="stylesheet" href="/assets/style.css?v=%s">\n</head><body class="lkpage"><main class="lkwrap"><img class="lklogo" src="/assets/logo_navy.png" alt="Marine HQ">'
           '<h1>Marine HQ</h1><p>Yacht management and maintenance. Gold Coast, Sydney, Whitsundays.</p>%s<p class="lkfoot">Freedom to enjoy.</p></main>\n</body></html>'
           % (BASE, datetime.date.today().strftime("%Y%m%d%H%M"), rows))
    os.makedirs(os.path.join(SITE, "links"), exist_ok=True)
    write_page(os.path.join(SITE, "links", "index.html"), doc)

MAPS = json.load(open(os.path.join(CONTENT, "_maps.json"), encoding="utf-8"))
LEAFLET = ('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">\n'
           '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>\n'
           '<script src="/assets/maps.js" defer></script>\n')

def render_map(mid):
    m = MAPS[mid]
    data = html.escape(json.dumps({"points": m["points"], "line": m.get("line", False)}), quote=True)
    items = "".join('<li class="k-%s"><span class="pin k-%s">%s</span><span><b>%s</b>%s</span></li>'
                    % (p.get("kind", "std"), p.get("kind", "std"), esc(p["n"]), esc(p["name"]),
                       (" <i>%s</i>" % esc(p["note"])) if p.get("note") else "") for p in m["points"])
    return ('<figure class="mapfig"><div class="map" role="img" aria-label="Map: %s" style="height:%dpx" data-map="%s"></div>'
            '<ol class="maplist">%s</ol><figcaption><b>%s</b> — %s Map data &copy; OpenStreetMap contributors.</figcaption></figure>'
            % (esc(m["title"]), m.get("height", 520), data, items, esc(m["title"]), esc(m["caption"])))

def build_guide(meta, guides):
    body_md = meta["_body"]
    quote = QUOTE.replace("__Q__", esc(meta.get("quote", ""))).replace("__BY__", esc(meta.get("quote_by", "Trish Perez, Marine HQ")))
    cta_line = meta.get("cta") or "Want a straight answer for your yacht? One call, no obligation."
    cta_mid = CTA_MID.replace("__LINE__", esc(cta_line)).replace("__PHONE_H__", PHONE_H).replace("__PHONE__", PHONE)
    body_md = body_md.replace("{{quote}}", quote if meta.get("quote") else "").replace("{{cta}}", cta_mid)
    # an eyebrow span inside a markdown="1" block must be followed by a blank line or the list after it won't parse
    body_md = re.sub(r'(<span class="eyebrow">[^<]*</span>)[ \t]*\n(?!\n)', r'\1\n\n', body_md)
    MD.reset()
    body_html = MD.convert(body_md)
    toc = MD.toc
    pids = re.findall(r"\{\{product:([a-z0-9-]+)\}\}", body_html)
    for pid in pids:
        body_html = body_html.replace("<p>{{product:%s}}</p>" % pid, render_product(pid)).replace("{{product:%s}}" % pid, render_product(pid))
    lead_pid = meta.get("product") or (pids[0] if pids else None)
    if lead_pid:                                  # slim strip before the second section, unless the full block is already that high
        h2s = [m.start() for m in re.finditer(r"<h2", body_html)]
        if len(h2s) >= 2 and not (0 <= body_html.find('class="prod"') < h2s[1]):
            at = h2s[1] if h2s[1] <= 0.25 * len(body_html) else h2s[0]      # a long first section (map, big table) would bury it
            body_html = body_html[:at] + product_strip(lead_pid) + "\n" + body_html[at:]
    has_map = False
    for mid in re.findall(r"\{\{map:([a-z0-9-]+)\}\}", body_html):
        body_html = body_html.replace("<p>{{map:%s}}</p>" % mid, render_map(mid)).replace("{{map:%s}}" % mid, render_map(mid))
        has_map = True
    subj = "Enquiry from the guide: " + meta["title"]
    inner = (GUIDE.replace("__HERO__", meta["hero"]).replace("__HEROPOS__", meta.get("hero_pos", "center"))
                  .replace("__HEROCLS__", " has-vid" if meta.get("hero_video") else "")
                  .replace("__SIDEPROD__", product_side(lead_pid) if lead_pid else "")
                  .replace("__HEROVID__", hero_video(meta.get("hero_video"), meta["hero"]))
                  .replace("__CATSLUG__", meta["category"])
                  .replace("__CAT__", esc(CAT_LABEL.get(meta["category"], meta["category"])))
                  .replace("__H1__", esc(meta["title"])).replace("__DESC__", esc(meta["description"]))
                  .replace("__UPDATED__", nice_date(meta["updated"])).replace("__MINS__", str(meta["mins"]))
                  .replace("__BODY__", body_html).replace("__TOC__", toc)
                  .replace("__FAQ__", render_faq(meta.get("faq")))
                  .replace("__CTA_END__", CTA_END).replace("__RELATED__", render_related(meta, guides))
                  .replace("__SOURCES__", render_sources(meta))
                  .replace("__PHONE_H__", PHONE_H).replace("__PHONE__", PHONE).replace("__EMAIL__", EMAIL)
                  .replace("__SUBJ__", html.escape(subj.replace(" ", "%20"))))
    canon = "%s/guides/%s/" % (BASE, meta["slug"])
    page = shell(meta["title"] + " | Marine HQ Guides", meta["description"], canon, "article", jsonld_guide(meta), inner)
    if has_map:
        page = page.replace("</body>", LEAFLET + "</body>")
    out = os.path.join(SITE, "guides", meta["slug"])
    os.makedirs(out, exist_ok=True)
    write_page(os.path.join(out, "index.html"), page)

INDEX = '''
<section class="hero home has-vid" style="--photo:url('/assets/photos/shoot-marina-aerial-2.jpg')">
  <div class="wrap">
    <div class="eyebrow">Marine HQ Guides &middot; Gold Coast</div>
    <h1>Straight answers on owning a yacht on the Gold Coast.</h1>
    <p class="stand">Costs, marinas, maintenance and the paperwork &mdash; written by the team that runs motor yachts here every day, with the numbers shown and the sources named.</p>
    <div class="sp" id="sp" role="search">
      <div class="sp-tabs" id="sp-tabs" role="tablist" aria-label="Narrow the search">__SPTABS__</div>
      <form class="sp-form" id="sp-form" action="#" autocomplete="off">
        <label class="sp-lab" for="sp-q">What do you want to know?</label>
        <div class="sp-row"><input id="sp-q" type="search" placeholder="e.g. antifoul cost, sea trial, crew, marina fees" aria-controls="sp-out"><button type="submit">Search</button></div>
      </form>
      <div class="sp-out" id="sp-out" aria-live="polite"></div>
      <noscript><p class="sp-ns">Search needs JavaScript. Browse the sections below instead.</p></noscript>
    </div>
  </div>
  <video class="hero-vid" data-auto autoplay muted loop playsinline preload="metadata" poster="/assets/photos/shoot-marina-aerial-2.jpg"><source src="/assets/video/marina-aerial.mp4" type="video/mp4"></video>
</section>
<main class="wrap">
__KIT__
__SECTIONS__
</main>
<script src="/assets/search.js" defer></script>
'''

def search_tabs():
    """Quick-pick chips above the search box: All, one per guide section, and the Owner's Kit."""
    tabs = [("all", "All")] + [(sl, l) for sl, l, _ in CATEGORIES if True] + [("kit", "Owner\u2019s Kit")]
    return "".join('<button type="button" role="tab" class="sp-tab%s" data-cat="%s" aria-selected="%s">%s</button>'
                   % (" on" if i == 0 else "", c, "true" if i == 0 else "false", esc(l)) for i, (c, l) in enumerate(tabs))

def strip_html(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t or "")).strip()

def build_search_index(guides):
    """site/assets/search.json: one entry per guide and per product, searched in the browser (search.js).
    Links carry PREFIX so the GitHub Pages review build still works."""
    items = []
    for g in guides:
        heads = " ".join(re.findall(r"^##+\s+(.+)$", g["_body"], re.M))
        faqs = " ".join(f["q"] for f in g.get("faq", []))
        items.append({"t": g["title"], "d": g["description"], "u": "%s/guides/%s/" % (PREFIX, g["slug"]),
                      "c": g["category"], "k": CAT_LABEL.get(g["category"], g["category"]),
                      "m": "%d min read" % g["mins"], "x": strip_html(heads + " " + faqs + " " + MD.reset().convert(g["_body"]))[:14000]})
    for p in PRODUCTS["products"]:
        soon = p.get("status") == "soon"
        items.append({"t": p["name"], "d": p["blurb"], "u": "%s/owners-kit/#%s" % (PREFIX, p["id"]), "c": "kit",
                      "k": "Owner\u2019s Kit", "m": "Coming soon" if soon else "$%s" % p["price"],
                      "x": strip_html(" ".join(p.get("includes", [])))[:600]})
    items.append({"t": "Free Annual Haul-Out Checklist", "d": "A free two-page PDF of what should happen while she is out of the water.",
                  "u": PREFIX + "/free-haul-out-checklist/", "c": "kit", "k": "Owner\u2019s Kit", "m": "Free", "x": "haul out hardstand shipyard checklist free pdf"})
    items.append({"t": "Crew placement", "d": "Owners who need crew, and crew who want work.", "u": PREFIX + "/crew/",
                  "c": "ownership", "k": "Ownership", "m": "", "x": "captain deckhand engineer stewardess relief skipper hire crew register"})
    os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)
    open(os.path.join(SITE, "assets", "search.json"), "w", encoding="utf-8").write(json.dumps(items, ensure_ascii=False, separators=(",", ":")))

def build_index(guides):
    secs = []
    for s, l, intro in CATEGORIES:
        gs = [g for g in guides if g["category"] == s]
        if not gs: continue
        secs.append('<section class="cat"><div class="cat-head"><h2><a href="/%s/">%s</a></h2><p>%s</p></div><div class="grid">%s</div></section>'
                    % (s, l, esc(intro), "".join(card(g) for g in gs)))
    jl = '<script type="application/ld+json">%s</script>' % json.dumps(
        {"@context": "https://schema.org", "@type": "WebSite", "name": "Marine HQ Guides", "url": BASE + "/",
         "publisher": {"@type": "Organization", "name": ORG, "url": MAIN}})
    page = shell("Marine HQ Guides — owning a yacht on the Gold Coast",
                 "Costs, marinas, maintenance and the paperwork of owning a motor yacht on the Gold Coast. Plain answers with the numbers shown.",
                 BASE + "/", "website", jl, INDEX.replace("__KIT__", kit_row()).replace("__SPTABS__", search_tabs()).replace("__SECTIONS__", "\n".join(secs)))
    write_page(os.path.join(SITE, "index.html"), page)

def build_hubs(guides):
    for s, l, intro in CATEGORIES:
        gs = [g for g in guides if g["category"] == s]
        inner = ('<section class="hero small"><div class="wrap"><div class="crumbs"><a href="/">Guides</a> <span>&rsaquo;</span> %s</div>'
                 '<h1>%s</h1><p class="stand">%s</p></div></section><main class="wrap"><div class="grid">%s</div>%s</main>'
                 % (esc(l), esc(l), esc(intro), "".join(card(g) for g in gs),
                    "" if gs else '<p class="empty">Guides for this section are being written. Call us in the meantime.</p>'))
        page = shell("%s — Marine HQ Guides" % l, intro, "%s/%s/" % (BASE, s), "website", "", inner)
        os.makedirs(os.path.join(SITE, s), exist_ok=True)
        write_page(os.path.join(SITE, s, "index.html"), page)

def build_meta(guides):
    urls = ["%s/" % BASE] + ["%s/%s/" % (BASE, s) for s, _, _ in CATEGORIES] + [BASE + "/owners-kit/", BASE + "/crew/", BASE + "/jobs/", BASE + "/free-haul-out-checklist/"] + ["%s/guides/%s/" % (BASE, g["slug"]) for g in guides]
    lm = {("%s/guides/%s/" % (BASE, g["slug"])): g["updated"] for g in guides}
    today = datetime.date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += ["<url><loc>%s</loc><lastmod>%s</lastmod></url>" % (u, lm.get(u, today)) for u in urls]
    sm.append("</urlset>")
    open(os.path.join(SITE, "sitemap.xml"), "w").write("\n".join(sm))
    open(os.path.join(SITE, "robots.txt"), "w").write("User-agent: *\nAllow: /\nDisallow: /dl/\nDisallow: /thanks/\nDisallow: /go/\nSitemap: %s/sitemap.xml\n" % BASE)
    open(os.path.join(SITE, "_redirects"), "w").write("/guides/:slug /guides/:slug/ 301\n")

def check(guides):
    bad = 0
    for g in guides:
        probs = []
        if not g.get("faq"):     probs.append("no FAQ")
        if not g.get("sources"): probs.append("no sources")
        if "{{cta}}" not in g["_body"]: probs.append("no {{cta}} placement")
        if g["words"] < 900:     probs.append("short (%d words)" % g["words"])
        if re.search(r"\b(color|organize|optimize|recognize|center|license[sd]?\b)", g["_body"]): probs.append("US spelling?")
        if probs:
            bad += 1; print("  ! %s: %s" % (g["slug"], ", ".join(probs)))
    print("check: %d guide(s) with issues" % bad)

GA_SNIPPET = """<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','%s');</script>
</head>"""

_write_orig = None
def job_slug(j):
    return re.sub(r"[^a-z0-9]+", "-", ("%s %s %s" % (j["position"], j["location"].split(",")[0], j["code"])).lower()).strip("-")

def jobsite_fix(h):
    h = re.sub(r'<nav class="sub".*?</nav>\n?', '', h, flags=re.S)                       # no guides sub-bar
    h = h.replace('<a href="/">Guides</a> <span>&rsaquo;</span>', '<a href="%s/">Marine HQ</a> <span>&rsaquo;</span>' % MAIN)
    h = h.replace('href="/crew/"', 'href="%s/crew/"' % GUIDES_DOMAIN).replace('href="/jobs/"', 'href="/"')
    h = h.replace(JOBS_DOMAIN + '/jobs/', JOBS_DOMAIN + '/')
    h = h.replace('content="Marine HQ Guides"', 'content="Marine HQ Jobs"')
    h = re.sub(r'<p class="fine">.*?</p>', '<p class="fine">&copy; %s Marine HQ Pty Ltd &middot; %s &middot; 76 - 84 Waterway Dr, Coomera QLD 4209.</p>' % (datetime.date.today().year, ABN), h, flags=re.S)
    h = re.sub(r'<div class="foot-links">.*?</div>', '<div class="foot-links"><a href="/">Jobs Board</a><a href="%s/crew/">Crew register</a><a href="%s/">Guides</a><a href="%s">Marine HQ home</a><a href="%s/contact">Contact</a></div>' % (GUIDES_DOMAIN, GUIDES_DOMAIN, MAIN, MAIN), h, flags=re.S)
    for j in json.load(open(os.path.join(CONTENT, "_jobs.json"), encoding="utf-8"))["jobs"]:
        h = h.replace('<h2>%s</h2>' % esc(j["title"]), '<h2><a href="/%s/" style="color:inherit;text-decoration:none">%s</a></h2>' % (job_slug(j), esc(j["title"])))
    return h

def write_page(path, html):
    if JOBSITE: html = jobsite_fix(html)
    elif JOBS_LIVE: html = html.replace('href="/jobs/"', 'href="%s/"' % JOBS_DOMAIN)
    if PREFIX:
        html = re.sub(r'(href|src|poster)="/(?!/)', lambda m: '%s="%s/' % (m.group(1), PREFIX), html)
        html = html.replace("url('/", "url('%s/" % PREFIX)
    if NOINDEX:
        html = html.replace("<head>", '<head>\n<meta name="robots" content="noindex,nofollow">', 1)
    elif GA4:
        html = html.replace("</head>", GA_SNIPPET % (GA4, GA4), 1)
    open(path, "w", encoding="utf-8").write(html)

def main():
    global PREFIX, NOINDEX, BASE, GA4, JOBS_LIVE
    JOBS_LIVE = "--jobs-live" in sys.argv
    if "--jobs-site" in sys.argv:
        build_jobs_site(os.path.expanduser("~/Documents/Marine HQ/marinehq-jobs")); return
    for i, a in enumerate(sys.argv):
        if a == "--prefix" and i + 1 < len(sys.argv): PREFIX = sys.argv[i + 1].rstrip("/")
        if a == "--base" and i + 1 < len(sys.argv):   BASE = sys.argv[i + 1].rstrip("/")
        if a == "--noindex": NOINDEX = True
        if a == "--ga" and i + 1 < len(sys.argv):     GA4 = sys.argv[i + 1].strip()
    paths = sorted(glob.glob(os.path.join(CONTENT, "*.md")))
    guides = [read_guide(p) for p in paths]
    guides.sort(key=lambda g: g["updated"], reverse=True)
    os.makedirs(os.path.join(SITE, "guides"), exist_ok=True)
    for g in guides: build_guide(g, guides)
    build_search_index(guides); build_index(guides); build_hubs(guides); build_shop(); build_crew(); build_jobs(); build_apply(); build_thanks(); build_free(); build_go(); build_links(); build_meta(guides)
    if JOBS_LIVE:
        redir = lambda to, js: ('<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><title>Marine HQ Jobs Board</title>'
                                '<meta name="robots" content="noindex"><link rel="canonical" href="%s/"><meta http-equiv="refresh" content="0;url=%s/">'
                                '<script>%s</script></head><body style="font-family:Arial,sans-serif;padding:40px"><p>The Marine HQ Jobs Board has moved to <a href="%s/">%s</a>.</p></body></html>' % (JOBS_DOMAIN, to, js, to, to))
        open(os.path.join(SITE, "jobs", "index.html"), "w", encoding="utf-8").write(redir(JOBS_DOMAIN, 'location.replace("%s/")' % JOBS_DOMAIN))
        open(os.path.join(SITE, "apply", "index.html"), "w", encoding="utf-8").write(redir(JOBS_DOMAIN + "/apply", 'location.replace("%s/apply/"+location.search)' % JOBS_DOMAIN))
        sm = os.path.join(SITE, "sitemap.xml"); t = open(sm).read(); open(sm, "w").write(re.sub(r"<url><loc>[^<]*/jobs/</loc>.*?</url>\n?", "", t))
    print("built %d guide(s) → %s" % (len(guides), SITE))
    for g in guides: print("  /guides/%s/  (%d words, %s)" % (g["slug"], g["words"], CAT_LABEL.get(g["category"], g["category"])))
    if "--check" in sys.argv: check(guides)

if __name__ == "__main__":
    main()
