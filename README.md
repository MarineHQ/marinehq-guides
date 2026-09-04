# Marine HQ Guides

Owner-facing guides for guides.marinehq.com.au (or the main site's blog, once Mesmerise switch it on).
Static site: Markdown in `content/` → `python3 build.py` → HTML in `site/` → Netlify.

- House style / how to write a guide: `GUIDES-STYLE.md`
- Build + check: `python3 build.py --check`
- Local preview: serve `site/` with any static server
- Deploy: push to `main`; Netlify runs `build.py` and publishes `site/`
