#!/usr/bin/env python3
"""Builds the hidden preview pages under /home-preview/.

Run from the repo root:  python3 tools/build_preview.py
Writes: home-preview/recipes/<slug>/index.html, home-preview/equipment/index.html,
home-preview/supplies/index.html. The tools/ folder is not published (see .assetsignore).
"""
import html
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = "/home-preview"  # unlisted preview area; nothing public links here

e = html.escape

# ---------------------------------------------------------------- ingredient amounts (CMS: quantity + unit + item)
UNITS = ["", "tsp", "tbsp", "cup", "oz", "lb", "g", "kg", "ml", "l", "pint", "quart", "can", "clove",
         "bunch", "head", "each", "pinch", "to taste", "to serve"]
_PLURAL = {"cup": "cups", "clove": "cloves", "can": "cans", "bunch": "bunches", "head": "heads",
           "pint": "pints", "quart": "quarts"}
# Instacart's accepted unit names (docs.instacart.com/developer_platform_api/api/units_of_measurement).
# Units Instacart doesn't support (clove, pinch, to taste, to serve) are sent without a measurement.
INSTACART_UNIT = {"tsp": "teaspoon", "tbsp": "tablespoon", "cup": "cup", "oz": "ounce", "lb": "pound",
                  "g": "gram", "kg": "kilogram", "ml": "milliliter", "l": "liter", "pint": "pint",
                  "quart": "quart", "can": "can", "bunch": "bunch", "head": "head", "each": "each", "": "each"}
_FRACTIONS = {"½": 0.5, "⅓": 1 / 3, "⅔": 2 / 3, "¼": 0.25, "¾": 0.75, "⅛": 0.125}


def amount_text(i):
    """Display amount, e.g. '2 cloves', '½ tsp', 'Pinch', 'To serve'."""
    if "amount" in i and "quantity" not in i:  # older entries
        return i.get("amount", "")
    q, u = (i.get("quantity") or "").strip(), (i.get("unit") or "").strip()
    if u in ("pinch", "to taste", "to serve"):
        return (q + " " + u).strip().capitalize() if q else u.capitalize()
    if u in _PLURAL and parse_qty(q) not in (None, 1.0) and parse_qty(q) > 1:
        u = _PLURAL[u]
    return (q + " " + u).strip()


def parse_qty(q):
    """'1 ½' -> 1.5, '½' -> 0.5, '14.5' -> 14.5; None if empty or unreadable."""
    total, found = 0.0, False
    for part in (q or "").replace("-", " ").split():
        if part in _FRACTIONS:
            total += _FRACTIONS[part]; found = True
        elif "/" in part:
            try:
                a, b = part.split("/"); total += float(a) / float(b); found = True
            except ValueError:
                return None
        else:
            try:
                total += float(part); found = True
            except ValueError:
                return None
    return round(total, 3) if found and total > 0 else None


def instacart_line(i):
    """One Instacart LineItem, or None if the ingredient isn't shopped (e.g. water)."""
    if i.get("shop") is False:
        return None
    item = i.get("item", "")
    name = (i.get("shop_as") or item.split(",")[0].split("(")[0]).strip().lower()
    li = {"name": name, "display_text": (amount_text(i) + " " + item).strip()}
    q, unit = parse_qty(i.get("quantity")), INSTACART_UNIT.get((i.get("unit") or "").strip())
    if q and unit:
        li["measurements"] = [{"quantity": q, "unit": unit}]
    return li

# ---------------------------------------------------------------- content (edited in Decap CMS at /admin)
import json
import glob

CONTENT = os.path.join(ROOT, "content")


def _load_folder(name):
    items = []
    for f in sorted(glob.glob(os.path.join(CONTENT, name, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        d["slug"] = os.path.splitext(os.path.basename(f))[0]
        items.append(d)
    return items


def _load(name):
    return json.load(open(os.path.join(CONTENT, "settings", name + ".json"), encoding="utf-8"))


TAX = _load("taxonomy")
MEAL_ORDER = TAX["meals"]
RETAILERS = ["Walmart", "Amazon", "Target"]

_equip = sorted(_load_folder("equipment"), key=lambda d: (TAX["equipment_categories"].index(d["category"]) if d["category"] in TAX["equipment_categories"] else 99, d.get("order", 999), d["title"]))
EQUIPMENT = {d["slug"]: (d["title"], d["category"], d.get("why", "")) for d in _equip}
EQUIP_DATA = {d["slug"]: d for d in _equip}

_sup = _load_folder("supplies")
SUPPLIES = []
for _c in TAX["supply_categories"] + sorted({d["category"] for d in _sup} - set(TAX["supply_categories"])):
    _items = sorted([d for d in _sup if d["category"] == _c], key=lambda d: (d.get("order", 999), d["title"]))
    if _items:
        SUPPLIES.append((_c, [(d["title"], d.get("note", ""), d.get("used_in", "")) for d in _items]))

ALL_RECIPES = sorted(_load_folder("recipes"), key=lambda d: (d.get("number") or 9999, d["title"]))
# A recipe gets its own page once it has steps.
RECIPES = []
for _r in ALL_RECIPES:
    if _r.get("steps"):
        r = dict(_r)
        r["ingredients_raw"] = r.get("ingredients", [])
        r["ingredients"] = [(amount_text(i), i.get("item", "")) for i in r["ingredients_raw"]]
        r.setdefault("serves", "")
        r["tags"] = r.get("tags") or []
        r["equipment"] = [x for x in (r.get("equipment") or []) if x in EQUIPMENT]
        RECIPES.append(r)

ARTICLES = []
for _a in sorted(_load_folder("articles"), key=lambda d: (d.get("order", 999), d["title"])):
    ARTICLES.append({"slug": _a["slug"], "title": _a["title"], "status": _a.get("status", "mockup"),
                     "covers": _a.get("covers", ""), "summary": _a.get("summary", ""),
                     "recipes": _a.get("in_our_recipes", ""),
                     "sources": [(x["title"], x["url"]) for x in _a.get("sources", [])]})

_b = _load("book")
BOOK = {"title": _b["title"], "subtitle": _b["subtitle"], "authors": _b["authors"], "blurb": _b["blurb"],
        "inside": _b["inside"], "editions": [(x["name"], x["description"], x["price"], x["stores"]) for x in _b["editions"]]}
HOME = _load("home")
INTEGRATIONS = _load("integrations")
SUPPLY_IMG = {d["title"]: d.get("image") for d in _sup}


def _rows():
    """Recipe index rows: (number, title, meal, pillar, key ingredients, status)."""
    return [(r.get("number", ""), r["title"], r["meal"], r["pillar"], r.get("key_ingredients", ""), r.get("status", "")) for r in ALL_RECIPES]

# ---------------------------------------------------------------- shared chrome
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">')


def head(title, desc, extra=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{e(title)} — Microbiome Recipes</title>
<meta name="description" content="{e(desc)}">
{FONTS}
<link rel="stylesheet" href="/assets/styles.css">
<link rel="stylesheet" href="/assets/preview.css">
<!-- Google AdSense: paste the account loader script here (adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX) -->
{extra}</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
"""


def header(current=None):
    links = [("Recipes", f"{P}/recipes/"), ("Learn", f"{P}/learn/"), ("Fermenting", f"{P}/fermenting/"),
             ("Cookbook", f"{P}/cookbook/"), ("About", f"{P}/about/"), ("Equipment", f"{P}/equipment/"),
             ("Supplies", f"{P}/supplies/")]
    nav = "\n".join(
        f'      <a href="{h}"{" aria-current=\"page\"" if n == current else ""}>{n}</a>' for n, h in links)
    return f"""<div class="preview-bar" role="note">Preview — not public. This page is only reachable by its address.</div>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{P}/">
      <svg width="32" height="32" viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="15" fill="#1E6B4E"/><path d="M10 19c2-6 8-9 13-9-1 6-5 11-11 11" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>
      Microbiome Recipes
    </a>
    <nav class="main-nav" aria-label="Main">
{nav}
    </nav>
  </div>
</header>
"""


FOOTER = """<footer class="site-footer">
  <div class="wrap">
    <div>
      <span class="brand" style="font-size:18px">Microbiome Recipes</span>
      <p>Recipes and general information, not medical advice. Talk with your doctor before big changes to your diet. Some links earn us a commission at no cost to you.</p>
    </div>
  </div>
</footer>
</body>
</html>
"""


def ad(slot, size="in-content"):
    """Google AdSense placeholder. Replace the inner div with the AdSense <ins> unit for this slot."""
    return (f'<aside class="ad-slot ad-{size}" aria-label="Advertisement">'
            f'<!-- AdSense unit: {slot} ({size}) — paste the <ins class="adsbygoogle"> code here -->'
            f'<span class="ad-label">Advertisement</span><div class="ad-box">Google AdSense · {e(slot)}</div></aside>')


def placeholder(label, cls="ph"):
    return f'<div class="{cls}" role="img" aria-label="Image placeholder: {e(label)}"><span>{e(label)}</span></div>'


def soon_button(label, uid):
    return (f'<div class="soon-btn">'
            f'<button type="button" class="btn-store" aria-disabled="true" aria-describedby="{uid}">{e(label)}</button>'
            f'<span class="soon" id="{uid}">Coming soon</span></div>')


def retailer_buttons(item_id, prefix):
    """Store buttons for a piece of equipment. A store with a URL becomes a live link; otherwise "Coming soon"."""
    stores = {x.get("store"): x for x in EQUIP_DATA.get(item_id, {}).get("stores", [])}
    out = []
    for r in RETAILERS:
        st = stores.get(r, {})
        price = st.get("price") or "$XX.XX"
        if st.get("url"):
            out.append(f'<div class="soon-btn"><a class="btn-store" rel="sponsored noopener" target="_blank" href="{e(st["url"])}">{e(r)} · {e(price)}</a></div>')
        else:
            out.append(soon_button(f"{r} · {price}", f"{prefix}-{item_id}-{r.lower()}"))
    return '<div class="store-row">' + "".join(out) + "</div>"


def media(src, label, cls="ph"):
    """An uploaded image if one is set in the CMS, otherwise a gray placeholder."""
    if src:
        return f'<img class="{cls.replace("ph ", "img ")}" src="{e(src)}" alt="{e(label)}" loading="lazy">'
    return placeholder(label, cls)


def grocery_buttons(prefix):
    """Supplies page: single Instacart button (coming soon until single-item shopping is built)."""
    return '<div class="store-row">' + soon_button("Instacart", f"{prefix}-instacart") + "</div>"


def instacart_recipe_button(r):
    """Recipe page shop button. Live once Instacart is enabled in Site settings → Integrations."""
    if INTEGRATIONS.get("instacart_enabled"):
        return (f'<a class="btn btn-primary btn-instacart" rel="nofollow sponsored" href="/api/instacart/{e(r["slug"])}">'
                f'Get recipe ingredients on Instacart</a>'
                '<p class="fine">Service fees apply.* Instacart may not be available in all zip codes.</p>')
    return '<div class="store-row">' + soon_button("Instacart", f'{r["slug"]}-groceries-instacart') + "</div>"


def instacart_payload(r):
    """Request body for Instacart's Create Recipe Page API, written to /data/instacart/<slug>.json at build time."""
    lines = [x for x in (instacart_line(i) for i in r.get("ingredients_raw", [])) if x]
    body = {
        "title": r["title"],
        "author": BOOK["authors"],
        "link_type": "recipe",
        "external_reference_id": r["slug"],
        "expires_in": 365,
        "instructions": list(r.get("prep") or []) + list(r.get("steps") or []),
        "ingredients": lines,
        "landing_page_configuration": {
            "partner_linkback_url": f"{SITE}{P}/recipes/{r['slug']}/",
            "enable_pantry_items": True,
        },
    }
    if r.get("serves"):
        body["servings"] = int(r["serves"])
    mins = iso_duration(r.get("total"))
    if mins:
        import re as _re
        h = _re.search(r"(\d+)H", mins); m = _re.search(r"(\d+)M", mins)
        body["cooking_time"] = (int(h.group(1)) * 60 if h else 0) + (int(m.group(1)) if m else 0)
    if r.get("image"):
        body["image_url"] = r["image"] if r["image"].startswith("http") else SITE + r["image"]
    return body


def write(path, content):
    full = os.path.join(ROOT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)



# ---------------------------------------------------------------- recipe structured data (schema.org/Recipe)
SITE = "https://microbiomerecipes.com"


def iso_duration(text):
    """'35 minutes' -> PT35M, '6 hours 5 minutes (overnight)' -> PT6H5M. Returns None if no time is given."""
    import re as _re
    t = (text or "").lower()
    if not t or "tbd" in t:
        return None
    h = _re.search(r"(\d+)\s*(?:hours?|hrs?|hr)\b", t)
    m = _re.search(r"(\d+)\s*(?:minutes?|mins?|min)\b", t)
    if not h and not m:
        return None
    return "PT" + (f"{h.group(1)}H" if h else "") + (f"{m.group(1)}M" if m else "")


def recipe_jsonld(r):
    """Recipe markup read by Google search and by Chicory. Built from the recipe's CMS fields."""
    authors = [a.strip() for a in BOOK["authors"].replace(" and ", ",").split(",") if a.strip()]
    d = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": r["title"],
        "description": r.get("intro", ""),
        "author": [{"@type": "Person", "name": a} for a in authors],
        "url": f"{SITE}{P}/recipes/{r['slug']}/",
        "recipeCategory": r["meal"],
        "keywords": ", ".join([r["pillar"]] + list(r.get("tags") or [])),
        "recipeIngredient": [f"{q} {i}".strip() for q, i in r["ingredients"]],
        "recipeInstructions": [],
    }
    if r.get("image"):
        d["image"] = [r["image"] if r["image"].startswith("http") else SITE + r["image"]]
    if r.get("serves"):
        d["recipeYield"] = f'{r["serves"]} servings'
    for key, field in (("prepTime", "prep_time"), ("totalTime", "total")):
        v = iso_duration(r.get(field))
        if v:
            d[key] = v
    for name, items in (("Prep", r.get("prep") or []), ("Steps", r.get("steps") or [])):
        if items:
            d["recipeInstructions"].append({"@type": "HowToSection", "name": name,
                                            "itemListElement": [{"@type": "HowToStep", "text": t} for t in items]})
    js = json.dumps(d, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return f'<script type="application/ld+json">\n{js}\n</script>\n'


# ---------------------------------------------------------------- recipe page
def numbered(items, start=1):
    return "\n".join(
        f'        <li><span class="num" aria-hidden="true">{i:02d}</span><p>{e(t)}</p></li>'
        for i, t in enumerate(items, start))


def recipe_page(r):
    tags = (f'<span class="tag tag-pillar">{e(r["pillar"])}</span><span class="tag tag-plain">{e(r["meal"])}</span>'
            + "".join(f'<span class="tag tag-plain">{e(t)}</span>' for t in r["tags"]))
    equip = "\n".join(
        f'          <li class="equip-item"><span class="equip-name">{e(EQUIPMENT[i][0])}</span>'
        f'{retailer_buttons(i, r["slug"])}</li>' for i in r["equipment"])
    rows = "\n".join(f'          <tr><th scope="row">{e(q)}</th><td>{e(n)}</td></tr>' for q, n in r["ingredients"])
    note = (f'<section class="note" aria-labelledby="gut-title"><h2 id="gut-title">Gut-health note</h2><p>{r["note"]}</p></section>'
            if r.get("note") else "")
    care = (f'<section class="care" aria-labelledby="care-title"><h2 id="care-title">Good to know</h2><p>{e(r["care"])}</p></section>'
            if r.get("care") else "")
    s = r["slug"]
    body = f"""{head(r["title"], r["intro"], recipe_jsonld(r))}{header()}
<main id="main">
  <div class="wrap">
    <p class="breadcrumb"><a href="{P}/">Home</a> / <a href="{P}/recipes/">Recipes</a> / {e(r["title"])}</p>
    <section class="recipe-hero" aria-labelledby="title">
      <div>
        <div class="tags">{tags}</div>
        <h1 id="title">{e(r["title"])}</h1>
        <p class="lede">{e(r["intro"])}</p>
        <div class="shop-box" aria-labelledby="shop-title">
          <h2 id="shop-title">Shop the ingredients</h2>
          {instacart_recipe_button(r)}
        </div>
      </div>
      {media(r.get("image"), r["title"], "ph ph-hero")}
    </section>
    {ad("recipe-top", "leaderboard")}
  </div>

  <div class="narrow recipe-card-panel">
    <section class="panel" aria-label="Recipe at a glance">
      <h2 class="label">Quick Look</h2>
      <p class="shorthand">{e(r["quick_look"])}</p>
      <h2 class="label">Prep Time</h2>
      <p>{e(r["prep_time"])}</p>
      {f'<h2 class="label">Waiting Time</h2>{chr(10)}      <p>{e(r["wait_time"])}</p>' if r.get("wait_time") else ""}
      <h2 class="label">Start To Finish</h2>
      <p>{e(r["total"])}</p>
      <h2 class="label">Equipment</h2>
      <ul class="equip-list">
{equip}
      </ul>
      <p class="fine">Prices are placeholders. <a href="{P}/equipment/">See all equipment</a></p>
    </section>

    {ad("recipe-after-equipment")}

    {placeholder("Ingredients laid out side by side", "ph ph-wide")}

    <table class="ing-table">
      <caption class="visually-hidden">Ingredients for {e(r["title"])}</caption>
      <thead><tr><th scope="col">To serve {r["serves"]}</th><th scope="col">Ingredients</th></tr></thead>
      <tbody>
{rows}
      </tbody>
    </table>
    <p class="fine">Missing an ingredient? See <a href="{P}/substitutions/">ingredient substitutions</a>.</p>

    <section aria-labelledby="prep-title" class="method-block">
      <h2 id="prep-title" class="method-head">Prep</h2>
      <ol class="num-steps">
{numbered(r["prep"])}
      </ol>
      <div class="ph-row">{placeholder("Prep step photo")}{placeholder("Prep step photo")}{placeholder("Prep step photo")}</div>
    </section>

    <section aria-labelledby="steps-title" class="method-block">
      <h2 id="steps-title" class="method-head">Steps</h2>
      <ol class="num-steps">
{numbered(r["steps"])}
      </ol>
      {placeholder("Step photo", "ph ph-step")}
    </section>

    {ad("recipe-after-steps")}

    {note}
    {care}
    <p class="disclaimer">Recipes and general information, not medical advice.</p>
  </div>
</main>
{FOOTER}"""
    write(f"{P}/recipes/{s}/index.html", body)


# ---------------------------------------------------------------- equipment page
def equipment_page():
    used = {}
    for r in RECIPES:
        for i in r["equipment"]:
            used.setdefault(i, []).append(r)
    cats = []
    for k, (n, c, w) in EQUIPMENT.items():
        if c not in cats:
            cats.append(c)
    toc = " · ".join(f'<a href="#{c.lower().replace(" ", "-")}">{e(c)}</a>' for c in cats)
    sections = []
    for c in cats:
        cards = []
        for k, (n, cat, w) in EQUIPMENT.items():
            if cat != c:
                continue
            uses = ", ".join(f'<a href="{P}/recipes/{r["slug"]}/">{e(r["title"])}</a>' for r in used.get(k, []))
            cards.append(f"""      <article class="pick" id="{k}">
        {media(EQUIP_DATA[k].get("image"), n, "ph ph-pick")}
        <div class="pick-body">
          <p class="pick-label">Our pick</p>
          <h3>{e(n)}</h3>
          <p class="pick-model">{e(EQUIP_DATA[k].get("model") or "[Brand and model — to be chosen]")}</p>
          <p>{e(w)}</p>
          {retailer_buttons(k, "eq")}
          {f'<p class="fine">Used in: {uses}</p>' if uses else ''}
        </div>
      </article>""")
        cid = c.lower().replace(" ", "-")
        sections.append(f'    <section aria-labelledby="{cid}-h" id="{cid}"><h2 id="{cid}-h" class="cat-head">{e(c)}</h2>\n' + "\n".join(cards) + "\n    </section>")
    body = f"""{head("Equipment", "The kitchen equipment used in our recipes.")}{header("Equipment")}
<main id="main">
  <div class="narrow" style="padding-top:40px; padding-bottom:72px">
    <p class="eyebrow">Kitchen guide</p>
    <h1 class="page-title">The equipment we use</h1>
    <p class="lede">Every tool that appears in our recipes, in one place. You don't need all of it: start with a knife, a board and one good skillet.</p>
    <p class="byline">By Ken Allen · Updated [DATE]</p>
    <div class="callout"><strong>How we pick.</strong> [Explain the testing and selection approach.] Prices and store links are placeholders until our retail partnerships are live. Some links will earn us a commission at no cost to you.</div>
    {ad("equipment-top", "leaderboard")}
    <nav class="toc" aria-label="Categories">{toc}</nav>
{chr(10).join(x + (chr(10) + "    " + ad(f"equipment-mid-{i // 2 + 1}") if i % 2 == 1 and i < len(sections) - 1 else "") for i, x in enumerate(sections))}
    {ad("equipment-bottom")}
  </div>
</main>
{FOOTER}"""
    write(f"{P}/equipment/index.html", body)


# ---------------------------------------------------------------- supplies page
def supplies_page():
    sections = []
    for cat, items in SUPPLIES:
        cid = cat.lower().replace(" ", "-")
        rows = []
        for n, note, used in items:
            iid = cid + "-" + n.lower().replace(" ", "-").replace("'", "")
            rows.append(f"""      <li class="supply">
        {media(SUPPLY_IMG.get(n), n, "ph ph-thumb")}
        <div class="supply-text"><h3>{e(n)}</h3><p>{e(note)}</p><p class="fine">Used in: {e(used)}</p></div>
        {grocery_buttons(iid)}
      </li>""")
        sections.append(f'    <section aria-labelledby="{cid}-h"><h2 id="{cid}-h" class="cat-head">{e(cat)}</h2>\n    <ul class="supply-list">\n' + "\n".join(rows) + "\n    </ul>\n    </section>")
    body = f"""{head("Supplies We Love", "Pantry staples, spices and kitchen supplies for our recipes.")}{header("Supplies")}
<main id="main">
  <div class="narrow" style="padding-top:40px; padding-bottom:72px">
    <p class="eyebrow">Pantry guide</p>
    <h1 class="page-title">Supplies We Love</h1>
    <p class="lede">The salt, oils, spices and staples our recipes lean on. Keep these stocked and most recipes only need a short fresh-food list.</p>
    {ad("supplies-top", "leaderboard")}
{chr(10).join(x + (chr(10) + "    " + ad(f"supplies-mid-{i // 2 + 1}") if i % 2 == 1 and i < len(sections) - 1 else "") for i, x in enumerate(sections))}
    {ad("supplies-bottom")}
  </div>
</main>
{FOOTER}"""
    write(f"{P}/supplies/index.html", body)


def sources_list(srcs):
    return "<ol>" + "".join(f'<li><a href="{e(u)}">{e(t)}</a></li>' for t, u in srcs) + "</ol>"


def learn_index():
    cards = []
    for a in ARTICLES:
        badge = "Draft" if a["status"] == "draft" else "Mockup"
        cards.append(f"""      <article class="article-card">
        {placeholder(a["title"], "ph ph-thumb-lg")}
        <div class="article-card-body">
          <p class="pick-label">{badge}</p>
          <h2><a href="{P}/learn/{a["slug"]}/">{e(a["title"])}</a></h2>
          <p>{e(a["summary"])}</p>
          <p class="in-recipes"><strong>In our recipes:</strong> {e(a["recipes"])}</p>
          <p class="fine">Sources: {", ".join(f'<a href="{e(u)}">{e(t)}</a>' for t, u in a["sources"])}</p>
        </div>
      </article>""")
    body = f"""{head("Learn: the science behind our recipes", "Short, cited explainers on fiber, fermented foods, plant variety and eating patterns, and how they shape our recipes.")}{header("Learn")}
<main id="main">
  <div class="narrow" style="padding-top:40px; padding-bottom:72px">
    <p class="eyebrow">Learn</p>
    <h1 class="page-title">The science behind our recipes</h1>
    <p class="lede">Why we cook the way we do, in plain language and with sources. Where the research is early, we say so.</p>
    <div class="callout"><strong>Kitchen guide:</strong> <a href="{P}/substitutions/">Ingredient substitutions</a> — what to use when you're missing something.</div>
    {ad("learn-top", "leaderboard")}
    <div class="article-list">
{chr(10).join(c + (chr(10) + "      " + ad("learn-mid") if i == 2 else "") for i, c in enumerate(cards))}
    </div>
    <p class="disclaimer">General information, not medical advice. Talk with your doctor before big changes to your diet.</p>
  </div>
</main>
{FOOTER}"""
    write(f"{P}/learn/index.html", body)


def article_stub(a):
    body = f"""{head(a["title"], a["summary"])}{header("Learn")}
<main id="main">
  <div class="narrow">
    <p class="breadcrumb"><a href="{P}/">Home</a> / <a href="{P}/learn/">Learn</a> / {e(a["title"])}</p>
    <article class="article">
      <h1>{e(a["title"])}</h1>
      <p class="byline">By Ken Allen · [DATE] · Article in progress</p>
      <section class="summary" aria-labelledby="sum-title">
        <h2 id="sum-title">The short version</h2>
        <ul><li>{e(a["summary"])}</li><li><strong>In our recipes:</strong> {e(a["recipes"])}</li></ul>
      </section>
      {ad("article-after-summary")}
      {placeholder("Article image", "ph ph-wide")}
      <div class="prose">
        <p><em>Full article coming soon. It will cover: {e(a["covers"][0].lower() + a["covers"][1:])}</em></p>
      </div>
      {ad("article-before-sources")}
      <section class="sources" aria-labelledby="src-title"><h2 id="src-title" style="font-size:20px">Sources</h2>{sources_list(a["sources"])}</section>
      <p class="disclaimer">General information, not medical advice.</p>
    </article>
  </div>
</main>
{FOOTER}"""
    write(f"{P}/learn/{a['slug']}/index.html", body)


# ---------------------------------------------------------------- recipe index (table of contents)
MEAL_HEAD = {"Side": "Sides", "Bread": "Breads", "Snack": "Snacks", "Dessert": "Desserts",
             "Condiment": "Condiments", "Ferment": "Ferments", "Drink": "Fermented drinks"}


def recipes_index():
    rows = _rows()
    built = {r["title"]: r["slug"] for r in RECIPES}
    groups = {}
    for num, title, meal, pillar, ing, status in rows:
        groups.setdefault(meal, []).append((title, pillar))
    toc = " · ".join(f'<a href="#{m.lower()}">{e(MEAL_HEAD.get(m, m))}</a>' for m in MEAL_ORDER if m in groups)
    secs = []
    for m in MEAL_ORDER:
        if m not in groups:
            continue
        items = []
        for title, pillar in groups[m]:
            if title in built:
                name = f'<a href="{P}/recipes/{built[title]}/">{e(title)}</a>'
                state = '<span class="tag tag-pillar">Ready to view</span>'
            else:
                name = f'<span>{e(title)}</span>'
                state = '<span class="soon">Coming soon</span>'
            items.append(f'        <li class="toc-item"><span class="toc-name">{name}</span>'
                         f'<span class="toc-meta"><span class="tag tag-plain">{e(pillar)}</span>{state}</span></li>')
        secs.append(f'    <section aria-labelledby="{m.lower()}-h" id="{m.lower()}"><h2 id="{m.lower()}-h" class="cat-head">'
                    f'{e(MEAL_HEAD.get(m, m))} <span class="count">({len(groups[m])})</span></h2>\n      <ul class="toc-list">\n'
                    + "\n".join(items) + "\n      </ul>\n    </section>")
    body = f"""{head("All recipes", "Every recipe on Microbiome Recipes, by meal.")}{header("Recipes")}
<main id="main">
  <div class="narrow" style="padding-top:40px; padding-bottom:72px">
    <p class="eyebrow">Recipes</p>
    <h1 class="page-title">All recipes</h1>
    <p class="lede">Recipes built around fiber, fermented foods and plant variety, listed by meal. Linked titles are ready to view; the rest are coming soon.</p>
    <nav class="toc" aria-label="Meals">{toc}</nav>
    {ad("recipes-index-top", "leaderboard")}
{chr(10).join(x + (chr(10) + "    " + ad(f"recipes-index-mid-{i // 3 + 1}") if i % 3 == 2 and i < len(secs) - 1 else "") for i, x in enumerate(secs))}
  </div>
</main>
{FOOTER}"""
    write(f"{P}/recipes/index.html", body)


def cookbook_page():
    b = BOOK
    eds = []
    for i, (name, desc, price, stores) in enumerate(b["editions"]):
        btns = "".join(soon_button(st, f"book-{i}-{st.lower().replace(' ', '-').replace('&', 'and').replace('.', '')}") for st in stores)
        eds.append(f"""      <section class="edition" aria-labelledby="ed{i}">
        <div class="edition-head"><h3 id="ed{i}">{e(name)}</h3><span class="edition-price">{e(price)}</span></div>
        <p>{e(desc)}</p>
        <div class="store-row">{btns}</div>
      </section>""")
    body = f"""{head(b["title"], b["subtitle"] + " — by " + b["authors"])}{header("Cookbook")}
<main id="main">
  <div class="wrap">
    <section class="book-hero" aria-labelledby="book-h">
      {media(_b.get("cover"), "Book cover: " + b["title"], "ph ph-cover")}
      <div class="book-info">
        <p class="eyebrow">The cookbook</p>
        <h1 id="book-h" class="page-title" style="margin:0">{e(b["title"])}</h1>
        <p class="lede">{e(b["subtitle"])}</p>
        <p class="authors">By {e(b["authors"])}</p>
        {"".join(f"<p class='blurb'>{para}</p>" for para in b["blurb"])}
      </div>
    </section>
  </div>
  <div class="narrow" style="padding-bottom:72px">
    <section aria-labelledby="inside-h" class="callout">
      <h2 id="inside-h" style="font-size:20px; margin-bottom:10px">What's inside</h2>
      <ul class="inside-list">{"".join(f"<li>{e(x)}</li>" for x in b["inside"])}</ul>
    </section>
    <h2 class="cat-head">Order the book</h2>
{chr(10).join(eds)}
    {ad("cookbook-bottom")}
    <p class="fine">Store links and prices will appear here at launch. Some links may earn us a commission at no cost to you.</p>
    <p class="disclaimer">Recipes and general information, not medical advice.</p>
  </div>
</main>
{FOOTER}"""
    write(f"{P}/cookbook/index.html", body)


# ---------------------------------------------------------------- Fermenting landing page
FERMENT_SAFETY = [
    ("Keep it under the brine.", "Vegetables must stay completely submerged so the right bacteria grow and air stays out.",
     ("Clemson Extension (HGIC)", "https://hgic.clemson.edu/want-to-ferment-vegetables/")),
    ("Mind the temperature.", "At 70–75°F, sauerkraut is fully fermented in about three to four weeks; at 60–65°F it may take six weeks.",
     ("Penn State Extension", "https://extension.psu.edu/lets-preserve-fermentation-sauerkraut-and-pickles")),
    ("Know when to toss it.", "Don't taste a ferment that has mold on the surface, a slimy texture or a bad smell. Discard the batch if there's a lot of visible mold.",
     ("Penn State Extension", "https://extension.psu.edu/lets-preserve-fermentation-sauerkraut-and-pickles")),
    ("Refrigerate when it's done.", "Once fermenting is finished, store the food in the refrigerator or can it properly.",
     ("UC Agriculture and Natural Resources", "https://ccfruitandnuts.ucanr.edu/sites/default/files/2020-12/340665.pdf")),
    ("Fermented drinks can contain alcohol.", "When sugar and yeast ferment, a drink like kombucha can reach 0.5% alcohol or more. If you avoid alcohol, keep that in mind with home-brewed drinks.",
     ("U.S. Alcohol and Tobacco Tax and Trade Bureau", "https://www.ttb.gov/kombucha/kombucha-general/print")),
]


def fermenting_page():
    rows = _rows()
    built = {r["title"]: r["slug"] for r in RECIPES}

    def cards(meal):
        out = []
        for num, title, m, pillar, ing, status in rows:
            if m != meal:
                continue
            if title in built:
                link = f'<a href="{P}/recipes/{built[title]}/">{e(title)}</a>'
                state = '<span class="tag tag-pillar">Ready to view</span>'
            else:
                link, state = e(title), '<span class="soon">Coming soon</span>'
            out.append(f'        <li class="method-card">{placeholder(title, "ph ph-method")}<h3>{link}</h3>'
                       f'<p>{e(ing)}</p>{state}</li>')
        return "\n".join(out)

    safety = "\n".join(
        f'        <li><strong>{e(h)}</strong> {e(t)} <span class="fine">(<a href="{e(u)}">{e(src)}</a>)</span></li>'
        for h, t, (src, u) in FERMENT_SAFETY)
    body = f"""{head("Fermenting at home", "Start fermenting at home: sauerkraut, kimchi, kefir, yogurt and fermented drinks, with the safety basics.")}{header("Fermenting")}
<main id="main">
  <div class="wrap">
    <section class="recipe-hero" aria-labelledby="ferm-h">
      <div>
        <p class="eyebrow">Fermenting</p>
        <h1 id="ferm-h" class="page-title" style="margin:0">Fermenting at home</h1>
        <p class="lede">Cabbage, salt and a jar are all it takes to start. Learn the base methods our recipes build on, from sauerkraut and kimchi to kefir and fizzy fermented drinks.</p>
        <div class="actions">
          <a class="btn btn-primary" href="#methods">Start with the basics</a>
          <a class="btn btn-secondary" href="{P}/learn/fermented-foods/">What the science says</a>
        </div>
      </div>
      {placeholder("Jars of fermenting vegetables", "ph ph-hero")}
    </section>
    {ad("fermenting-top", "leaderboard")}
  </div>

  <div class="narrow" style="padding-bottom:72px">
    <section id="methods" aria-labelledby="methods-h">
      <h2 id="methods-h" class="cat-head">Base methods</h2>
      <p class="fine" style="font-size:16px">The starting points for many of our recipes. Begin with sauerkraut: it's the simplest.</p>
      <ul class="method-grid">
{cards("Ferment")}
      </ul>
    </section>

    <section aria-labelledby="safety-h" class="callout safety">
      <h2 id="safety-h" style="font-size:22px; margin-bottom:12px">Safety basics</h2>
      <ul class="safety-list">
{safety}
      </ul>
      <p class="fine">For tested recipes and full guidance, see the <a href="https://nchfp.uga.edu/how/ferment/sauerkraut/">National Center for Home Food Preservation</a>.</p>
    </section>

    {ad("fermenting-mid")}

    <section aria-labelledby="drinks-h">
      <h2 id="drinks-h" class="cat-head">Fermented drinks</h2>
      <ul class="method-grid">
{cards("Drink")}
      </ul>
    </section>

    <section aria-labelledby="gear-h" class="callout">
      <h2 id="gear-h" style="font-size:20px; margin-bottom:8px">What you'll need</h2>
      <p style="margin:0">Most ferments need only a knife, a cutting board, clean jars and salt. See <a href="{P}/equipment/#storage-and-fermenting">equipment</a> and <a href="{P}/supplies/#salt-and-pepper-h">supplies</a>.</p>
    </section>
    {ad("fermenting-bottom")}
    <p class="disclaimer">General information, not medical or food-safety certification. Follow tested recipes and current guidance.</p>
  </div>
</main>
{FOOTER}"""
    write(f"{P}/fermenting/index.html", body)


# ---------------------------------------------------------------- About page
def about_page():
    people = [("Crystal Allen", "[Short bio for Crystal Allen: background, role on the site and the book, and what got her interested in gut-friendly cooking.]"),
              ("Ken Allen", "[Short bio for Ken Allen: background, role on the site and the book, and what got him interested in gut-friendly cooking.]")]
    ppl = "\n".join(f"""      <article class="person">
        {placeholder(n + " portrait", "ph ph-portrait")}
        <div><h3>{e(n)}</h3><p>{e(b)}</p></div>
      </article>""" for n, b in people)
    pillars = [("We show our sources.", f'Every science claim links to the research behind it, and we say plainly when the evidence is early. <a href="{P}/learn/">See the science</a>.'),
               ("We cook it first.", "Every recipe is made in our own kitchen and adjusted before it's published."),
               ("Food first, not supplements.", "We focus on everyday food: fiber, fermented foods and plenty of plants. We don't sell supplements or gut tests."),
               ("It's not medical advice.", "We share recipes and general information. Talk with your doctor before big changes to your diet, especially if you have a digestive condition."),
               ("How we keep the lights on.", "The site is supported by ads, by some store links that earn a commission at no cost to you, and by our cookbook.")]
    pl = "\n".join(f"        <li><strong>{h}</strong> {t}</li>" for h, t in pillars)
    body = f"""{head("About us", "Who we are and how we make Microbiome Recipes.")}{header("About")}
<main id="main">
  <div class="narrow" style="padding-top:40px; padding-bottom:72px">
    <p class="eyebrow">About</p>
    <h1 class="page-title">Good food, good gut, good health</h1>
    <p class="lede">Microbiome Recipes is a home for everyday cooking built around what the research on gut health actually supports: fiber, fermented foods and lots of different plants. No miracle cures, no supplements, just good food.</p>
    {placeholder("Crystal and Ken in the kitchen", "ph ph-wide")}

    <section aria-labelledby="who-h">
      <h2 id="who-h" class="cat-head">Who we are</h2>
{ppl}
    </section>

    {ad("about-mid")}

    <section aria-labelledby="how-h">
      <h2 id="how-h" class="cat-head">How we work</h2>
      <ul class="safety-list">
{pl}
      </ul>
    </section>

    <section aria-labelledby="book-h2" class="callout">
      <h2 id="book-h2" style="font-size:20px; margin-bottom:8px">The cookbook</h2>
      <p style="margin:0"><em>The Microbiome Cookbook — Good Food, Good Gut, Good Health</em> has 150 recipes you won't find on the site. <a href="{P}/cookbook/">Learn more</a>.</p>
    </section>

    <section aria-labelledby="contact-h">
      <h2 id="contact-h" class="cat-head">Get in touch</h2>
      <p style="font-size:17px">Questions, corrections or a recipe that didn't work? Email us at [CONTACT EMAIL]. If you spot an error in our science, tell us and we'll fix it.</p>
    </section>
  </div>
</main>
{FOOTER}"""
    write(f"{P}/about/index.html", body)



# ---------------------------------------------------------------- Ingredient substitutions (CMS: Substitutions)
def substitutions_page():
    subs = _load_folder("substitutions")
    cfg = _load("substitutions")
    intros = {x["category"]: x["intro"] for x in cfg.get("intros", [])}
    cats = TAX.get("substitution_categories", []) + sorted({x["category"] for x in subs} - set(TAX.get("substitution_categories", [])))
    toc = " · ".join(f'<a href="#{c.lower().replace(" ", "-")}">{e(c)}</a>' for c in cats if any(x["category"] == c for x in subs))
    secs = []
    for c in cats:
        items = sorted([x for x in subs if x["category"] == c], key=lambda x: (x.get("order", 999), x["title"]))
        if not items:
            continue
        rows = []
        for x in items:
            ours = x.get("origin") == "ours"
            family = x.get("kind") == "family"
            if family:
                use = ('<span class="sub-label">Interchangeable</span><ul class="sub-swaps sub-family">'
                       + "".join(f"<li>{e(w)}</li>" for w in x.get("swaps", [])) + "</ul>")
            else:
                use = '<ul class="sub-swaps">' + "".join(f"<li>{e(w)}</li>" for w in x.get("swaps", [])) + "</ul>"
            if ours:
                src = '<span class="tag tag-plain">Our suggestion · not yet tested</span>'
                if x.get("source_url"):
                    src += f'<br><a class="fine" href="{e(x["source_url"])}">Note source</a>'
            elif x.get("source_url"):
                src = f'<a href="{e(x["source_url"])}">{e(x.get("source_title") or "Source")}</a>'
            else:
                src = e(x.get("source_title", ""))
            search = " ".join([x["title"], c, x.get("note", "")] + list(x.get("swaps", []))).lower()
            rows.append(f"""          <tr data-search="{e(search)}">
            <th scope="row" data-label="Ingredient">{e(x["title"])}</th>
            <td data-label="Amount">{e(x.get("amount", "")) or "—"}</td>
            <td data-label="Use instead">{use}</td>
            <td data-label="Notes">{e(x.get("note", ""))}</td>
            <td data-label="Source" class="sub-src">{src}</td>
          </tr>""")
        cards = [f"""      <div class="sub-table-wrap">
      <table class="sub-table">
        <caption class="visually-hidden">Substitutions: {e(c)}</caption>
        <thead><tr><th scope="col">Ingredient</th><th scope="col">Amount</th><th scope="col">Use instead</th><th scope="col">Notes</th><th scope="col">Source</th></tr></thead>
        <tbody>
""" + "\n".join(rows) + """
        </tbody>
      </table>
      </div>"""]
        cid = c.lower().replace(" ", "-")
        intro = f'<p class="sub-intro">{e(intros[c])}</p>' if intros.get(c) else ""
        secs.append(f'    <section class="sub-section" aria-labelledby="{cid}-h" id="{cid}"><h2 id="{cid}-h" class="cat-head">{e(c)}</h2>\n'
                    + f'      {placeholder(c + " photo", "ph ph-wide ph-section")}\n      {intro}\n'
                    + "\n".join(cards) + "\n    </section>")
    body = f"""{head("Ingredient substitutions", "What to use when you're missing an ingredient, with notes on keeping live cultures and fiber in your cooking.")}{header("Learn")}
<main id="main">
  <div class="sub-page" style="padding-top:40px; padding-bottom:72px">
    <p class="eyebrow">Kitchen guide</p>
    <h1 class="page-title">Ingredient substitutions</h1>
    <p class="byline">{e(cfg.get("byline", ""))} · Updated {e(cfg.get("updated", ""))}</p>
    <p class="lede">Missing something? Here's what to use instead. Some swaps are one-for-one; others are families of ingredients you can trade freely. Either way, think about flavor, texture and cooking time, and taste as you go.</p>
    <div class="callout"><strong>Live cultures and heat.</strong> Heat can kill the live cultures in fermented foods like yogurt, kefir, sauerkraut and kimchi. To keep them, stir these in after cooking. <span class="fine">(<a href="https://www.health.harvard.edu/staying-healthy/do-fermented-foods-live-up-to-the-hype">Harvard Health</a>)</span></div>
    <div class="sub-search">
      <label for="sub-q">Find an ingredient</label>
      <input id="sub-q" type="search" placeholder="e.g. buttermilk, garlic, cornstarch" autocomplete="off">
      <p id="sub-count" class="fine" aria-live="polite"></p>
    </div>
    <nav class="toc" aria-label="Categories">{toc}</nav>
    {ad("substitutions-top", "leaderboard")}
{chr(10).join(secs)}
    {ad("substitutions-bottom")}
    <p class="disclaimer">Swaps marked "Our suggestion" haven't been tested in our kitchen yet. Recipes and general information, not medical advice.</p>
  </div>
</main>
<script>
(function () {{
  var q = document.getElementById("sub-q"), out = document.getElementById("sub-count");
  var rows = [].slice.call(document.querySelectorAll(".sub-table tbody tr"));
  var secs = [].slice.call(document.querySelectorAll(".sub-section"));
  q.addEventListener("input", function () {{
    var t = q.value.trim().toLowerCase(), n = 0;
    rows.forEach(function (r) {{ var m = !t || r.dataset.search.indexOf(t) > -1; r.hidden = !m; if (m) n++; }});
    secs.forEach(function (s) {{ s.hidden = !s.querySelector(".sub-table tbody tr:not([hidden])"); }});
    out.textContent = t ? n + (n === 1 ? " match" : " matches") : "";
  }});
}})();
</script>
{FOOTER}"""
    write(f"{P}/substitutions/index.html", body)


# ---------------------------------------------------------------- home: featured recipe (chosen in CMS settings)
def home_featured():
    path = os.path.join(ROOT, P.lstrip("/"), "index.html")
    html_ = open(path, encoding="utf-8").read()
    start, end = "<!-- FEATURED:START -->", "<!-- FEATURED:END -->"
    if start not in html_:
        return
    r = next((x for x in RECIPES if x["slug"] == HOME.get("featured_recipe")), RECIPES[0] if RECIPES else None)
    if not r:
        return
    timing = r.get("total", "")
    if r.get("wait_time"):
        timing = (r.get("prep_time", "") + " + overnight") if "overnight" in r.get("wait_time", "").lower() else timing
    desc = HOME.get("featured_description") or r.get("intro", "")
    card = f"""{start}
      <a class="featured" href="{P}/recipes/{r["slug"]}/" aria-labelledby="featured-title">
        {media(r.get("image"), r["title"], "ph featured-img")}
        <div class="featured-body">
          <p class="featured-label">Featured recipe</p>
          <h2 id="featured-title" class="featured-title">{e(r["title"])}</h2>
          <p class="featured-desc">{e(desc)}</p>
          <div class="tags"><span class="tag tag-pillar">{e(r["pillar"])}</span><span class="tag tag-plain">{e(r["meal"])}</span><span class="tag tag-plain">{e(timing)}</span></div>
          <span class="featured-cta">Get the recipe →</span>
        </div>
      </a>
      {end}"""
    i, j = html_.index(start), html_.index(end) + len(end)
    open(path, "w", encoding="utf-8").write(html_[:i] + card + html_[j:])
    print("updated featured recipe on", P + "/")


# ---------------------------------------------------------------- keep the editor's dropdowns in sync with the taxonomy settings
def sync_admin_options():
    import re as _re
    path = os.path.join(ROOT, "admin", "config.yml")
    if not os.path.exists(path):
        return
    cfg = open(path, encoding="utf-8").read()
    pairs = {"name: meal, widget: select": TAX["meals"], "name: pillar, widget: select": TAX["pillars"]}
    for key, vals in pairs.items():
        cfg = _re.sub(_re.escape(key) + r", options: \[[^\]]*\]", key + ", options: " + json.dumps(vals, ensure_ascii=False), cfg)
    # category selects appear in the equipment, supplies and substitutions collections, in that order
    key = "name: category, widget: select, options: "
    parts = cfg.split(key)
    lists = [TAX["equipment_categories"], TAX["supply_categories"], TAX.get("substitution_categories", [])]
    if len(parts) == len(lists) + 1:
        out = parts[0]
        for chunk, vals in zip(parts[1:], lists):
            out += key + json.dumps(vals, ensure_ascii=False) + chunk[chunk.index("]") + 1:]
        cfg = out
    open(path, "w", encoding="utf-8").write(cfg)

if __name__ == "__main__":
    for r in RECIPES:
        recipe_page(r)
        write(f"/data/instacart/{r['slug']}.json", json.dumps(instacart_payload(r), ensure_ascii=False, indent=1))
    equipment_page()
    supplies_page()
    learn_index()
    recipes_index()
    cookbook_page()
    fermenting_page()
    about_page()
    substitutions_page()
    home_featured()
    sync_admin_options()
    for a in ARTICLES:
        if a["slug"] != "fiber":  # the fiber article is hand-written
            article_stub(a)
