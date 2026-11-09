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

# ---------------------------------------------------------------- equipment
# id: (name, category, why)
EQUIPMENT = {
    "chefs-knife": ("8-inch chef's knife", "Knives and boards",
                    "One sharp, all-purpose knife handles nearly every cut in these recipes."),
    "cutting-board": ("Large cutting board", "Knives and boards",
                      "A big, stable board gives you room to chop and keeps the counter clean."),
    "measuring-cups": ("Measuring cups", "Measuring",
                       "Nested dry cups for oats, lentils, rice and greens."),
    "measuring-spoons": ("Measuring spoons", "Measuring",
                         "For spices, oils and the small amounts that make a dish."),
    "mason-jars": ("Pint mason jars with lids", "Storage and fermenting",
                   "Mix, chill and serve in one jar; also the starting point for home ferments."),
    "mixing-bowl": ("Mixing bowl set", "Prep",
                    "Nesting bowls for mixing, tossing and holding prepped ingredients."),
    "fine-strainer": ("Fine-mesh strainer", "Prep",
                      "Rinses lentils and beans without losing the small ones."),
    "microplane": ("Rasp grater", "Prep",
                   "Grates ginger, garlic and citrus zest in seconds."),
    "tofu-press": ("Tofu press", "Prep",
                   "Squeezes water out of tofu so it crisps instead of steaming."),
    "nonstick-skillet": ("12-inch nonstick skillet", "Pots and pans",
                         "Wide enough to crisp tofu and fry rice without crowding."),
    "small-skillet": ("8-inch skillet", "Pots and pans",
                      "Right-sized for blooming spices in oil."),
    "saucepan": ("3-quart saucepan with lid", "Pots and pans",
                 "Simmers lentils, grains and sauces."),
    "turner": ("Flexible turner", "Tools",
               "Thin edge slides under tofu and rice for a clean flip."),
    "wooden-spoon": ("Wooden spoon", "Tools",
                     "Stirs dal and sauces without scratching the pan."),
}
RETAILERS = ["Walmart", "Amazon", "Target"]

# ---------------------------------------------------------------- supplies
# category -> list of (name, note, used_in)
SUPPLIES = [
    ("Salt and pepper", [
        ("Kosher salt", "Coarse and easy to pinch; the everyday cooking salt.", "All recipes"),
        ("Fine sea salt", "Dissolves fast in dressings and baking.", "Dressings, baking"),
        ("Canning and pickling salt", "Pure salt with no iodine or anti-caking agents, for ferments.", "Sauerkraut"),
        ("Black peppercorns", "Whole peppercorns for a pepper grinder; fresher than pre-ground.", "All recipes"),
    ]),
    ("Oils and vinegars", [
        ("Canola oil", "Neutral flavor and a high smoke point for searing and stir-frying.", "Kimchi fried rice"),
        ("Extra-virgin olive oil", "For roasting, dressings and finishing.", "Lentil and beet salad, white bean soup"),
        ("Toasted sesame oil", "A finishing oil; a teaspoon adds a lot of flavor.", "Kimchi fried rice, kimchi eggs"),
        ("Apple cider vinegar", "Bright, mild acid for marinades and dressings.", "Tempeh Reuben"),
        ("Red wine vinegar", "Sharper acid for vinaigrettes.", "Lentil and beet salad"),
    ]),
    ("Spices", [
        ("Ground cumin", "Warm and earthy; a base for beans and lentils.", "Bean and lentil dishes"),
        ("Cumin seeds", "Whole seeds to sizzle in oil before adding other ingredients.", "Red lentil dal"),
        ("Ground turmeric", "Golden color and mild bitterness for dal and rice.", "Red lentil dal"),
        ("Ground coriander", "Citrusy, gentle spice that pairs with cumin.", "Red lentil dal"),
        ("Garam masala", "A warm spice blend, added near the end of cooking.", "Red lentil dal"),
        ("Smoked paprika", "Smoky depth without meat.", "Tempeh Reuben"),
        ("Red chili flakes", "Adjustable heat.", "Red lentil dal"),
        ("Ground cinnamon", "Warmth for oats and puddings.", "Overnight oats"),
        ("Caraway seeds", "The classic sauerkraut and rye-bread spice.", "Sauerkraut, rye breads"),
        ("Dried thyme", "An easy stand-in when fresh herbs aren't on hand.", "White bean soup"),
    ]),
    ("Pantry", [
        ("Low-sodium soy sauce", "Salty, savory seasoning with less sodium.", "Kimchi fried rice, tempeh Reuben"),
        ("Gochujang", "Fermented Korean chili paste.", "Kimchi fried rice"),
        ("Dijon mustard", "Emulsifies and sharpens vinaigrettes.", "Lentil and beet salad"),
        ("Pure vanilla extract", "For oats, puddings and baking.", "Overnight oats, chia pudding"),
        ("Cornstarch", "A light coating that helps tofu crisp.", "Kimchi fried rice"),
        ("Low-sodium vegetable broth", "A soup base that leaves room to season.", "White bean soup"),
    ]),
    ("Kitchen supplies", [
        ("Parchment paper", "Lines sheet pans for roasting with less sticking.", "Roasted vegetables"),
        ("Paper towels", "Blots tofu, greens and washed produce dry.", "Kimchi fried rice"),
        ("Zip-top storage bags", "Holds prepped vegetables and leftovers.", "Meal prep"),
    ]),
]

# ---------------------------------------------------------------- recipes
RECIPES = [
    {
        "slug": "overnight-oats-kefir-chia-raspberries",
        "title": "Overnight oats with kefir, chia and raspberries",
        "meal": "Breakfast", "pillar": "Fermented", "tags": ["No cooking", "Make ahead"],
        "intro": "Five minutes the night before gets you a creamy, tangy breakfast that's ready when you are. Kefir does the soaking, so there's no cooking.",
        "quick_look": "Stir 1c oats, 1c kefir, ½c milk, 2T chia, ½t vanilla, pinch cinnamon; + ½c raspberries. Chill 6hr+. Top w ½c raspberries + 2T walnuts.",
        "prep_time": "5 minutes",
        "wait_time": "At least 6 hours, or overnight, in the refrigerator",
        "total": "6 hours 5 minutes (overnight)",
        "serves": 2,
        "equipment": ["measuring-cups", "measuring-spoons", "mason-jars"],
        "ingredients": [
            ("1 cup", "Old-fashioned rolled oats"),
            ("1 cup", "Plain unsweetened kefir"),
            ("½ cup", "Milk of choice"),
            ("2 T", "Chia seeds"),
            ("½ t", "Vanilla extract"),
            ("Pinch", "Cinnamon"),
            ("1 cup", "Raspberries, fresh or frozen (half in, half on top)"),
            ("2 T", "Walnuts, chopped, to serve"),
        ],
        "prep": [
            "Divide the oats between two pint jars, or use one bowl.",
            "Chop the walnuts and set them aside for the morning.",
        ],
        "steps": [
            "Stir the oats, kefir, milk, chia, vanilla and cinnamon together.",
            "Fold in half the raspberries.",
            "Cover and refrigerate at least 6 hours or overnight.",
            "Stir, then top with the remaining raspberries and the walnuts.",
        ],
        "note": ('Kefir is a fermented food, and oats, chia and raspberries bring fiber. An early Stanford study found that adults who ate more fermented foods for 10 weeks had more diverse gut microbes, though experts say the benefits aren\'t yet established. '
                 '<a href="https://med.stanford.edu/news/all-news/2021/07/fermented-food-diet-increases-microbiome-diversity-lowers-inflammation.html">Source</a>'),
        "care": "Kefir contains live cultures. If you're immunocompromised, check with your doctor before eating live-culture foods. New to fiber? Start with a half portion.",
    },
    {
        "slug": "kimchi-fried-brown-rice-tofu",
        "title": "Kimchi fried brown rice with tofu",
        "meal": "Dinner", "pillar": "Fermented", "tags": ["30 minutes or less"],
        "intro": "Day-old brown rice, crisp tofu and kimchi two ways: half cooked into the rice for depth, half folded in at the end so it stays crunchy.",
        "quick_look": "Crisp 14oz cubed tofu (+1T cornstarch) in 1T oil 8–10min; set aside. 1T oil + garlic, scallion whites, ½ kimchi 2min; + 1c peas/carrots, 3c cold rice 4–5min. + 1T soy, 1t gochujang, 2T kimchi juice, tofu. Off heat: rest of kimchi, 1t sesame oil, scallion greens.",
        "prep_time": "[TBD — time on test cook]",
        "total": "25 minutes",
        "serves": 3,
        "equipment": ["tofu-press", "chefs-knife", "cutting-board", "measuring-cups", "measuring-spoons", "nonstick-skillet", "turner"],
        "ingredients": [
            ("14 oz", "Extra-firm tofu, pressed and cubed"),
            ("1 T", "Cornstarch"),
            ("2 T", "Neutral oil, divided"),
            ("2 cloves", "Garlic, minced"),
            ("3", "Scallions, whites and greens separated"),
            ("1 cup + 2 T", "Kimchi, chopped, plus kimchi juice"),
            ("1 cup", "Frozen peas and carrots"),
            ("3 cups", "Cooked brown rice, chilled"),
            ("1 T", "Low-sodium soy sauce"),
            ("1 t", "Gochujang (optional)"),
            ("1 t", "Toasted sesame oil"),
            ("To serve", "3 fried eggs and sesame seeds (optional)"),
        ],
        "prep": [
            "Press the tofu, then cut it into bite-size cubes.",
            "Mince the garlic. Slice the scallions, keeping the whites and greens apart.",
            "Chop the kimchi and save 2 tablespoons of its juice.",
        ],
        "steps": [
            "Toss the tofu with the cornstarch.",
            "Heat 1 tablespoon oil over medium-high heat and crisp the tofu, 8–10 minutes. Set aside.",
            "Add the remaining oil, the garlic, scallion whites and half the kimchi; cook 2 minutes.",
            "Add the peas and carrots, then the rice. Press it into the pan and cook 4–5 minutes until crisp in spots.",
            "Stir in the soy sauce, gochujang and kimchi juice. Return the tofu.",
            "Off the heat, fold in the remaining kimchi, sesame oil and scallion greens.",
            "Top with fried eggs and sesame seeds, if using.",
        ],
        "care": "Cooking kimchi kills its live cultures, which is why half goes in at the end.",
    },
    {
        "slug": "red-lentil-dal-spinach",
        "title": "Red lentil dal with spinach",
        "meal": "Dinner", "pillar": "Fiber", "tags": ["One pot"],
        "intro": "Red lentils cook down to a creamy base in about 20 minutes. A quick pan of cumin, onion, ginger and tomato does the rest.",
        "quick_look": "Simmer 1c red lentils, 3c water, ½t turmeric 15–20min. Sizzle 1t cumin seeds in 1T oil 30sec; + onion 6–8min; + garlic, ginger, 1t coriander, ½t garam masala, chili 1min; + 14.5oz tomatoes 5min. Combine; + 4c spinach. Lemon, salt.",
        "prep_time": "[TBD — time on test cook]",
        "total": "35 minutes",
        "serves": 4,
        "equipment": ["fine-strainer", "chefs-knife", "cutting-board", "microplane", "measuring-cups", "measuring-spoons", "saucepan", "small-skillet", "wooden-spoon"],
        "ingredients": [
            ("1 cup", "Red lentils, rinsed"),
            ("3 cups", "Water"),
            ("½ t", "Ground turmeric"),
            ("1 T", "Oil or ghee"),
            ("1 t", "Cumin seeds"),
            ("1", "Onion, diced"),
            ("3 cloves", "Garlic, minced"),
            ("1 T", "Fresh ginger, grated"),
            ("1 t", "Ground coriander"),
            ("½ t", "Garam masala"),
            ("Pinch", "Chili flakes"),
            ("14.5 oz can", "Diced tomatoes"),
            ("4 cups", "Baby spinach"),
            ("1 T", "Lemon juice"),
            ("To serve", "Salt, cilantro, plain yogurt and brown rice"),
        ],
        "prep": [
            "Rinse the lentils in a strainer until the water runs mostly clear.",
            "Dice the onion, mince the garlic and grate the ginger.",
        ],
        "steps": [
            "Simmer the lentils, water and turmeric 15–20 minutes, stirring now and then, until soft.",
            "Meanwhile, heat the oil and sizzle the cumin seeds 30 seconds.",
            "Add the onion and cook 6–8 minutes.",
            "Add the garlic, ginger, coriander, garam masala and chili; cook 1 minute.",
            "Add the tomatoes and simmer 5 minutes.",
            "Stir the tomato mixture into the lentils. Add the spinach and stir until wilted.",
            "Season with lemon juice and salt. Serve with cilantro, a spoon of yogurt and brown rice.",
        ],
        "care": "New to beans and lentils? Start with a smaller portion and drink plenty of water.",
    },
]

# ---------------------------------------------------------------- shared chrome
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">')


def head(title, desc):
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
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
"""


def header(current=None):
    links = [("Recipes", f"{P}/recipes/"), ("Learn", f"{P}/learn/"),
             ("Equipment", f"{P}/equipment/"), ("Supplies", f"{P}/supplies/"), ("Cookbook", f"{P}/cookbook/")]
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


def placeholder(label, cls="ph"):
    return f'<div class="{cls}" role="img" aria-label="Image placeholder: {e(label)}"><span>{e(label)}</span></div>'


def soon_button(label, uid):
    return (f'<div class="soon-btn">'
            f'<button type="button" class="btn-store" aria-disabled="true" aria-describedby="{uid}">{e(label)}</button>'
            f'<span class="soon" id="{uid}">Coming soon</span></div>')


def retailer_buttons(item_id, prefix):
    return '<div class="store-row">' + "".join(
        soon_button(f"{r} · $XX.XX", f"{prefix}-{item_id}-{r.lower()}") for r in RETAILERS) + "</div>"


def grocery_buttons(prefix):
    return ('<div class="store-row">' + soon_button("Instacart", f"{prefix}-instacart")
            + soon_button("Chicory", f"{prefix}-chicory") + "</div>")


def write(path, content):
    full = os.path.join(ROOT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)


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
    body = f"""{head(r["title"], r["intro"])}{header()}
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
          {grocery_buttons(s + "-groceries")}
        </div>
      </div>
      {placeholder("Finished dish", "ph ph-hero")}
    </section>
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

    {placeholder("Ingredients laid out side by side", "ph ph-wide")}

    <table class="ing-table">
      <caption class="visually-hidden">Ingredients for {e(r["title"])}</caption>
      <thead><tr><th scope="col">To serve {r["serves"]}</th><th scope="col">Ingredients</th></tr></thead>
      <tbody>
{rows}
      </tbody>
    </table>
    <p class="fine">T = tablespoon · t = teaspoon</p>

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
        {placeholder(n, "ph ph-pick")}
        <div class="pick-body">
          <p class="pick-label">Our pick</p>
          <h3>{e(n)}</h3>
          <p class="pick-model">[Brand and model — to be chosen]</p>
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
    <nav class="toc" aria-label="Categories">{toc}</nav>
{chr(10).join(sections)}
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
        {placeholder(n, "ph ph-thumb")}
        <div class="supply-text"><h3>{e(n)}</h3><p>{e(note)}</p><p class="fine">Used in: {e(used)}</p></div>
        {grocery_buttons(iid)}
      </li>""")
        sections.append(f'    <section aria-labelledby="{cid}-h"><h2 id="{cid}-h" class="cat-head">{e(cat)}</h2>\n    <ul class="supply-list">\n' + "\n".join(rows) + "\n    </ul>\n    </section>")
    body = f"""{head("Supplies", "Pantry staples, spices and kitchen supplies for our recipes.")}{header("Supplies")}
<main id="main">
  <div class="narrow" style="padding-top:40px; padding-bottom:72px">
    <p class="eyebrow">Pantry guide</p>
    <h1 class="page-title">Supplies</h1>
    <p class="lede">The salt, oils, spices and staples our recipes lean on. Keep these stocked and most recipes only need a short fresh-food list.</p>
{chr(10).join(sections)}
  </div>
</main>
{FOOTER}"""
    write(f"{P}/supplies/index.html", body)


# ---------------------------------------------------------------- articles (Learn)
# Summaries come from the book outline's Part 1 research table; sources are the ones cited there.
ARTICLES = [
    {"slug": "microbiome-basics", "title": "Meet your gut microbiome", "status": "mockup",
     "covers": "What the microbiome is and how quickly diet shifts it.",
     "summary": "Diet can change gut microbes within about a day. Most findings so far come from small or short studies, so we treat them as early signals, not proof.",
     "recipes": "Why we focus on everyday eating patterns instead of quick fixes.",
     "sources": [("Harvard T.H. Chan School of Public Health: The Microbiome", "https://nutritionsource.hsph.harvard.edu/microbiome/"),
                 ("NIH News in Health: Your Body's Bugs", "https://newsinhealth.nih.gov/2021/08/your-body-s-bugs"),
                 ("David et al., Nature 2014", "https://doi.org/10.1038/nature12820")]},
    {"slug": "fiber", "title": "Fiber: the strongest evidence", "status": "draft",
     "covers": "Fiber types, food sources and how much to eat.",
     "summary": "Higher fiber intake is linked to lower risk of heart disease, type 2 diabetes and colorectal cancer. Fiber alone hasn't been shown to raise microbial diversity in the short term.",
     "recipes": "Why most of our recipes are built on beans, lentils, whole grains and vegetables.",
     "sources": [("Reynolds et al., The Lancet 2019", "https://doi.org/10.1016/S0140-6736(18)31809-9"),
                 ("King's College London, 2018", "https://www.kcl.ac.uk/news/some-types-of-fibre-more-beneficial-for-gut-health-than-others"),
                 ("Harvard T.H. Chan School of Public Health: Fiber", "https://nutritionsource.hsph.harvard.edu/carbohydrates/fiber/")]},
    {"slug": "fermented-foods", "title": "Fermented foods: promising, early", "status": "mockup",
     "covers": "Yogurt, kefir, kimchi, sauerkraut, miso and tempeh.",
     "summary": "An early Stanford study found a fermented-food diet raised gut microbial diversity. Experts say the health benefits aren't yet established.",
     "recipes": "Why kefir, kimchi and sauerkraut show up often, and why we add kimchi at the end of cooking to keep its live cultures.",
     "sources": [("Wastyk et al., Cell 2021", "https://doi.org/10.1016/j.cell.2021.06.019"),
                 ("Marco et al., Nature Reviews Gastroenterology & Hepatology 2021 (ISAPP)", "https://doi.org/10.1038/s41575-020-00390-5"),
                 ("American Gastroenterological Association: The gut microbiome", "https://patient.gastro.org/the-gut-microbiome-what-it-is/")]},
    {"slug": "plant-variety", "title": "Plant variety and \"30 plants a week\"", "status": "mockup",
     "covers": "Counting plant types and easy ways to add variety.",
     "summary": "Researchers are testing whether eating 30 or more plant types a week helps the gut. For now it's an association, not a proven cause.",
     "recipes": "Why our recipes mix several vegetables, grains, nuts, seeds and herbs in one dish.",
     "sources": [("McDonald et al., mSystems 2018", "https://doi.org/10.1128/mSystems.00031-18"),
                 ("King's College London, 2021", "https://www.kcl.ac.uk/news/landmark-study-link-gut-microbes-diet-illnesses")]},
    {"slug": "eating-patterns", "title": "Patterns beat single foods", "status": "mockup",
     "covers": "Mediterranean-style eating and why habits matter more than superfoods.",
     "summary": "Mediterranean-style eating has been linked to gut-microbe changes in older adults, and the benefits faded when people stopped.",
     "recipes": "Why we offer a full week of meals rather than a single \"gut-health\" food.",
     "sources": [("Ghosh et al., Gut 2020", "https://doi.org/10.1136/gutjnl-2019-319654"),
                 ("Ross et al., Nature Reviews Microbiology 2024", "https://doi.org/10.1038/s41579-024-01068-4"),
                 ("MD Anderson: beans and gut health trial", "https://www.mdanderson.org/newsroom/eating-beans-improves-gut-health-regulates-immune-inflammatory-processes-colorectal-cancer-survivors.h00-159623379.html")]},
    {"slug": "start-slow", "title": "Start slow, stay safe", "status": "mockup",
     "covers": "Ramping up fiber, drinking water, and who should check with a doctor first.",
     "summary": "Add fiber gradually and drink water with it. People with IBS, IBD or strictures, those taking MAOIs, anyone watching sodium, and people who are immunocompromised should take extra care with high-fiber and fermented foods.",
     "recipes": "Why our recipes carry \"Good to know\" notes and suggest half portions for beginners.",
     "sources": [("Ascension, 2026", "https://healthcare.ascension.org/blog/2026/08/flpen-fibermaxxing-too-much-fiber"),
                 ("UF/IFAS: Sauerkraut", "https://ask.ifas.ufl.edu/publication/FS474/pdf"),
                 ("Mayo Clinic: Probiotics", "https://mayoclinic.org/healthy-lifestyle/consumer-health/expert-answers/probiotics/faq-20058065")]},
]


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
    <div class="article-list">
{chr(10).join(cards)}
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
      {placeholder("Article image", "ph ph-wide")}
      <div class="prose">
        <p><em>Full article coming soon. It will cover: {e(a["covers"][0].lower() + a["covers"][1:])}</em></p>
      </div>
      <section class="sources" aria-labelledby="src-title"><h2 id="src-title" style="font-size:20px">Sources</h2>{sources_list(a["sources"])}</section>
      <p class="disclaimer">General information, not medical advice.</p>
    </article>
  </div>
</main>
{FOOTER}"""
    write(f"{P}/learn/{a['slug']}/index.html", body)


# ---------------------------------------------------------------- recipe index (table of contents)
import json
MEAL_ORDER = ["Breakfast", "Lunch", "Dinner", "Side", "Bread", "Snack", "Dessert", "Condiment", "Ferment", "Drink"]
MEAL_HEAD = {"Side": "Sides", "Bread": "Breads", "Snack": "Snacks", "Dessert": "Desserts",
             "Condiment": "Condiments", "Ferment": "Ferments", "Drink": "Fermented drinks"}


def recipes_index():
    rows = json.load(open(os.path.join(ROOT, "tools", "recipe_list.json"), encoding="utf-8"))["site"]
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
    <p class="lede">{len(rows)} recipes built around fiber, fermented foods and plant variety, listed by meal. Linked titles are ready to view; the rest are coming soon.</p>
    <nav class="toc" aria-label="Meals">{toc}</nav>
{chr(10).join(secs)}
  </div>
</main>
{FOOTER}"""
    write(f"{P}/recipes/index.html", body)


# ---------------------------------------------------------------- cookbook (book) page
BOOK = {
    "title": "The Microbiome Cookbook",
    "subtitle": "Good Food, Good Gut, Good Health",
    "authors": "Crystal Allen and Ken Allen",
    "blurb": [
        "Eating for your gut doesn't take supplements, special tests or a pantry full of powders. It takes good food: beans and whole grains, vegetables in every color, and the tangy, living flavors of yogurt, kefir, kimchi and sauerkraut.",
        "In <em>The Microbiome Cookbook</em>, Crystal Allen and Ken Allen bring together 150 recipes you won't find on the website, from weekday breakfasts to slow-simmered dinners, fresh breads and homemade fermented drinks. Every recipe carries a short gut-health note that tells you what the research shows, and where it's still early.",
        "Six plain-language science chapters explain the why: what your gut microbiome is, why fiber has the strongest evidence, what we know (and don't) about fermented foods, and how to add more fiber comfortably. A hands-on fermenting guide walks you through the base methods step by step, with the safety rules that matter.",
    ],
    "inside": ["150 book-only recipes, from breakfast to fermented drinks",
               "Six short science chapters, with sources",
               "A step-by-step guide to fermenting at home",
               "A cited gut-health note on every recipe"],
    "editions": [
        ("Print edition", "Lay-flat, so it stays open on the counter while you cook.", "[PRICE]",
         ["Amazon", "Barnes & Noble", "Bookshop.org", "Books-A-Million"]),
        ("Ebook", "Read on your phone, tablet or e-reader.", "[PRICE]",
         ["Kindle", "Nook", "Apple Books", "Kobo", "Google Play Books"]),
    ],
}


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
      {placeholder("Book cover", "ph ph-cover")}
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
    <p class="fine">Store links and prices will appear here at launch. Some links may earn us a commission at no cost to you.</p>
    <p class="disclaimer">Recipes and general information, not medical advice.</p>
  </div>
</main>
{FOOTER}"""
    write(f"{P}/cookbook/index.html", body)


if __name__ == "__main__":
    for r in RECIPES:
        recipe_page(r)
    equipment_page()
    supplies_page()
    learn_index()
    recipes_index()
    cookbook_page()
    for a in ARTICLES:
        if a["slug"] != "fiber":  # the fiber article is hand-written
            article_stub(a)
