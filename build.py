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
MAIN    = "https://www.marinehq.com.au"
PHONE   = "0439 748 387"
PHONE_H = "+61439748387"
EMAIL   = "yachtsupport@marinehq.com.au"
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
<header class="top">
  <div class="wrap bar">
    <a class="logo" href="/" aria-label="Marine HQ Guides"><img src="/assets/logo_navy.png" alt="Marine HQ"><span>Guides</span></a>
    <nav class="nav" aria-label="Sections">__NAV__<a class="ext" href="__MAIN__">marinehq.com.au</a></nav>
    <a class="btn call" href="tel:__PHONE_H__">Speak to us</a>
  </div>
</header>
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
    <p class="fine">&copy; __YEAR__ Marine HQ Pty Ltd &middot; __ABN__ &middot; 76/84 Waterway Dr, Coomera QLD 4209.
      Prices and figures in these guides are indicative, drawn from published sources on the date shown, and change without notice &mdash; always confirm with the provider. Nothing here is financial or legal advice.</p>
  </div>
</footer>
</body></html>'''

GUIDE = '''
<section class="hero" style="background-image:linear-gradient(180deg,rgba(22,34,63,.35) 0%,rgba(22,34,63,.55) 40%,rgba(22,34,63,.92) 100%),url('/__HERO__')">
  <div class="wrap">
    <div class="crumbs"><a href="/">Guides</a> <span>&rsaquo;</span> <a href="/__CATSLUG__/">__CAT__</a></div>
    <h1>__H1__</h1>
    <p class="stand">__DESC__</p>
    <div class="meta"><span>Updated __UPDATED__</span><span>&middot;</span><span>__MINS__ min read</span><span>&middot;</span><span>Gold Coast, Queensland</span></div>
  </div>
</section>
<main class="wrap article">
  <article class="body">
__BODY__
  </article>
  <aside class="side">
    <div class="card toc"><div class="eyebrow">In this guide</div>__TOC__</div>
    <div class="card cta side-cta">
      <div class="eyebrow">Talk to Marine HQ</div>
      <h3>Want this handled, not just explained?</h3>
      <p>We manage motor yachts on the Gold Coast end to end. One call and it is on our list, not yours.</p>
      <a class="btn" href="tel:__PHONE_H__">Call __PHONE__</a>
      <a class="btn ghost" href="mailto:__EMAIL__?subject=__SUBJ__">Email us</a>
    </div>
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

def card(g):
    return ('<a class="gcard" href="/guides/%s/"><span class="eyebrow">%s</span><strong>%s</strong><p>%s</p>'
            '<span class="more">%s min read &rarr;</span></a>'
            % (g["slug"], esc(CAT_LABEL.get(g["category"], g["category"])), esc(g["title"]), esc(g["description"]), g["mins"]))

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

def nav_html():
    return "".join('<a href="/%s/">%s</a>' % (s, l) for s, l, _ in CATEGORIES)

def shell(title, desc, canon, ogtype, jsonld, inner):
    v = datetime.date.today().strftime("%Y%m%d")
    page = (HEAD.replace("__TITLE__", esc(title)).replace("__DESC__", esc(desc)).replace("__CANON__", canon)
                .replace("__OGTYPE__", ogtype).replace("__BASE__", BASE).replace("__V__", v)
                .replace("__JSONLD__", jsonld).replace("__NAV__", nav_html()).replace("__MAIN__", MAIN)
                .replace("__PHONE_H__", PHONE_H))
    foot = (FOOT.replace("__FOOTNAV__", nav_html() + '<a href="%s">Marine HQ home</a><a href="%s/contact">Contact</a>' % (MAIN, MAIN))
                .replace("__YEAR__", str(datetime.date.today().year)).replace("__ABN__", ABN)
                .replace("__PHONE_H__", PHONE_H).replace("__PHONE__", PHONE).replace("__EMAIL__", EMAIL).replace("__MAIN__", MAIN))
    return page + inner + foot

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
    subj = "Enquiry from the guide: " + meta["title"]
    inner = (GUIDE.replace("__HERO__", meta["hero"]).replace("__CATSLUG__", meta["category"])
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
    out = os.path.join(SITE, "guides", meta["slug"])
    os.makedirs(out, exist_ok=True)
    write_page(os.path.join(out, "index.html"), page)

INDEX = '''
<section class="hero home" style="background-image:linear-gradient(180deg,rgba(22,34,63,.30) 0%,rgba(22,34,63,.55) 45%,rgba(22,34,63,.92) 100%),url('/assets/login-bg.jpg')">
  <div class="wrap">
    <div class="eyebrow">Marine HQ Guides &middot; Gold Coast</div>
    <h1>Straight answers on owning a yacht on the Gold Coast.</h1>
    <p class="stand">Costs, marinas, maintenance and the paperwork &mdash; written by the team that runs motor yachts here every day, with the numbers shown and the sources named.</p>
  </div>
</section>
<main class="wrap">
__SECTIONS__
</main>
'''

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
                 BASE + "/", "website", jl, INDEX.replace("__SECTIONS__", "\n".join(secs)))
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
    urls = ["%s/" % BASE] + ["%s/%s/" % (BASE, s) for s, _, _ in CATEGORIES] + ["%s/guides/%s/" % (BASE, g["slug"]) for g in guides]
    lm = {("%s/guides/%s/" % (BASE, g["slug"])): g["updated"] for g in guides}
    today = datetime.date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += ["<url><loc>%s</loc><lastmod>%s</lastmod></url>" % (u, lm.get(u, today)) for u in urls]
    sm.append("</urlset>")
    open(os.path.join(SITE, "sitemap.xml"), "w").write("\n".join(sm))
    open(os.path.join(SITE, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % BASE)
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

_write_orig = None
def write_page(path, html):
    if PREFIX:
        html = re.sub(r'(href|src)="/(?!/)', lambda m: '%s="%s/' % (m.group(1), PREFIX), html)
        html = html.replace("url('/", "url('%s/" % PREFIX)
    if NOINDEX:
        html = html.replace("<head>", '<head>\n<meta name="robots" content="noindex,nofollow">', 1)
    open(path, "w", encoding="utf-8").write(html)

def main():
    global PREFIX, NOINDEX, BASE
    for i, a in enumerate(sys.argv):
        if a == "--prefix" and i + 1 < len(sys.argv): PREFIX = sys.argv[i + 1].rstrip("/")
        if a == "--base" and i + 1 < len(sys.argv):   BASE = sys.argv[i + 1].rstrip("/")
        if a == "--noindex": NOINDEX = True
    paths = sorted(glob.glob(os.path.join(CONTENT, "*.md")))
    guides = [read_guide(p) for p in paths]
    guides.sort(key=lambda g: g["updated"], reverse=True)
    os.makedirs(os.path.join(SITE, "guides"), exist_ok=True)
    for g in guides: build_guide(g, guides)
    build_index(guides); build_hubs(guides); build_meta(guides)
    print("built %d guide(s) → %s" % (len(guides), SITE))
    for g in guides: print("  /guides/%s/  (%d words, %s)" % (g["slug"], g["words"], CAT_LABEL.get(g["category"], g["category"])))
    if "--check" in sys.argv: check(guides)

if __name__ == "__main__":
    main()
