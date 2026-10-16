/* Marine HQ Guides: search panel on the home page.
   Reads assets/search.json (built by build.py) and searches it in the browser. No tracking, no server. */
(function () {
  var panel = document.getElementById("sp");
  if (!panel) return;
  var q = document.getElementById("sp-q"), out = document.getElementById("sp-out"),
      form = document.getElementById("sp-form"), tabs = [].slice.call(panel.querySelectorAll(".sp-tab"));
  var cat = "all", data = null, loading = false;
  var src = (document.currentScript && document.currentScript.src) || "";
  var jsonUrl = src ? src.replace(/search\.js(\?.*)?$/, "search.json") : "/assets/search.json";

  function load(cb) {
    if (data) return cb();
    if (loading) return;
    loading = true;
    fetch(jsonUrl).then(function (r) { return r.json(); })
      .then(function (d) { data = d; loading = false; cb(); })
      .catch(function () { loading = false; out.innerHTML = '<p class="sp-none">Search could not load. Browse the sections below.</p>'; });
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); }
  function words(s) { return s.toLowerCase().replace(/[^a-z0-9$ ]+/g, " ").split(/\s+/).filter(function (w) { return w.length > 1; }); }
  function stem(w) { return w.replace(/(ing|ed|es|s)$/, ""); }

  function score(item, terms, any) {
    var t = item.t.toLowerCase(), d = item.d.toLowerCase(), x = (item.x || "").toLowerCase(), n = 0;
    for (var i = 0; i < terms.length; i++) {
      var w = terms[i], s = stem(w), hit = 0;
      if (t.indexOf(w) >= 0 || t.indexOf(s) >= 0) hit = i === 0 ? 9 : 7;   // the first word is usually the subject
      else if (d.indexOf(w) >= 0 || d.indexOf(s) >= 0) hit = 3;
      else if (x.indexOf(w) >= 0 || x.indexOf(s) >= 0) hit = 1;
      if (!hit) { if (any) continue; return 0; }   // by default every word has to appear somewhere
      n += hit;
    }
    return n;
  }
  function row(i) {
    return '<a class="sp-item" href="' + esc(i.u) + '"><span class="sp-k">' + esc(i.k) + (i.m ? ' &middot; ' + esc(i.m) : '') + '</span>' +
           '<strong>' + esc(i.t) + '</strong><span class="sp-d">' + esc(i.d) + '</span></a>';
  }
  function render() {
    var text = q.value.trim(), terms = words(text), pool = data.filter(function (i) { return cat === "all" || i.c === cat; }), list;
    if (!terms.length) {
      // nothing typed: show the section's items, newest guides first as built
      list = pool.slice(0, cat === "all" ? 0 : 8);
      out.innerHTML = list.length ? list.map(row).join("") : "";
      out.classList.toggle("on", !!list.length);
      return;
    }
    function rank(any) {
      return pool.map(function (i) { return [score(i, terms, any), i]; }).filter(function (p) { return p[0] > 0; })
                 .sort(function (a, b) { return b[0] - a[0]; }).slice(0, 8).map(function (p) { return p[1]; });
    }
    list = rank(false);
    if (!list.length && terms.length > 1) list = rank(true);   // no page has every word: show pages with any of them
    out.classList.add("on");
    out.innerHTML = list.length ? list.map(row).join("")
      : '<p class="sp-none">Nothing matches &ldquo;' + esc(text) + '&rdquo;. Try fewer words, or call us on 0439 748 387 and ask.</p>';
  }
  function go() { load(render); }

  tabs.forEach(function (b) {
    b.addEventListener("click", function () {
      cat = b.getAttribute("data-cat");
      tabs.forEach(function (x) { var on = x === b; x.classList.toggle("on", on); x.setAttribute("aria-selected", on ? "true" : "false"); });
      go();
    });
  });
  q.addEventListener("input", go);
  q.addEventListener("focus", function () { load(function () {}); });
  form.addEventListener("submit", function (e) { e.preventDefault(); go(); });
})();
