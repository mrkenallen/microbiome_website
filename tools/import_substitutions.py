#!/usr/bin/env python3
"""Import the substitutions spreadsheet into content/substitutions/*.json.

Usage (from the repo root):
    python3 tools/import_substitutions.py path/to/Microbiome_Recipes_Substitutions.xlsx [--dry-run]

Reads the "Substitutions" sheet (header row + one row per entry), validates it, then REPLACES all
files in content/substitutions/ with the spreadsheet's rows. New categories from the "Lists" sheet
(or found in rows) are appended to substitution_categories in content/settings/taxonomy.json.
Section intros and page text in content/settings/substitutions.json are not touched.
"""
import glob
import json
import os
import re
import sys

from openpyxl import load_workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content", "substitutions")
TAX = os.path.join(ROOT, "content", "settings", "taxonomy.json")

COLUMNS = {
    "category": "Category",
    "title": "Ingredient (or group name)",
    "kind": "Type",
    "amount": "Amount",
    "swaps": "Use instead (one per line)",
    "note": "Notes",
    "origin": "Where it comes from",
    "source_title": "Source title",
    "source_url": "Source link",
    "order": "Order",
}


def text(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).strip()


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("'", "").replace("’", "")).strip("-")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if not args:
        sys.exit(__doc__)
    wb = load_workbook(args[0], data_only=True)
    if "Substitutions" not in wb.sheetnames:
        sys.exit('No sheet named "Substitutions" in the workbook.')
    ws = wb["Substitutions"]
    header = [text(c.value) for c in ws[1]]
    idx = {}
    for key, name in COLUMNS.items():
        if name not in header:
            sys.exit(f'Missing column "{name}". Found: {header}')
        idx[key] = header.index(name)

    entries, problems, slugs = [], [], {}
    for rnum, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        vals = {k: text(row[i]) if i < len(row) else "" for k, i in idx.items()}
        if not any(vals.values()):
            continue
        if not vals["title"]:
            problems.append(f"Row {rnum}: Ingredient is empty."); continue
        if not vals["category"]:
            problems.append(f"Row {rnum} ({vals['title']}): Category is empty."); continue
        swaps = [s.strip(" •-\t") for s in re.split(r"\r?\n", vals["swaps"]) if s.strip(" •-\t")]
        if not swaps:
            problems.append(f"Row {rnum} ({vals['title']}): 'Use instead' is empty."); continue
        kind = "family" if vals["kind"].lower().startswith("fam") else "swap"
        origin = "ours" if vals["origin"].lower().startswith("our") else "extension"
        if origin == "extension" and not vals["source_url"]:
            problems.append(f"Row {rnum} ({vals['title']}): marked Published source but has no Source link.")
        if vals["source_url"] and not vals["source_url"].startswith(("http://", "https://")):
            problems.append(f"Row {rnum} ({vals['title']}): Source link should start with https://")
        try:
            order = int(float(vals["order"])) if vals["order"] else 999
        except ValueError:
            order = 999
        slug = slugify(vals["title"] if kind == "swap" else vals["category"] + " " + vals["title"]) or f"row-{rnum}"
        if slug in slugs:
            slug = f"{slug}-{slugify(vals['category'])}"
        if slug in slugs:
            slug = f"{slug}-{rnum}"
        slugs[slug] = rnum
        entries.append((slug, {
            "title": vals["title"], "category": vals["category"], "kind": kind, "amount": vals["amount"],
            "swaps": swaps, "note": vals["note"], "origin": origin, "order": order,
            "source_title": vals["source_title"], "source_url": vals["source_url"],
        }))

    # categories: keep existing order, then any new ones from the Lists sheet, then any new ones in rows
    tax = json.load(open(TAX, encoding="utf-8"))
    cats = list(tax.get("substitution_categories", []))
    extra = []
    if "Lists" in wb.sheetnames:
        extra += [text(c.value) for c in wb["Lists"]["A"][1:] if text(c.value) and len(text(c.value)) < 60]
    extra += [d["category"] for _, d in entries]
    for c in extra:
        if c and c not in cats:
            cats.append(c)

    print(f"{len(entries)} entries read; {len(problems)} problem(s).")
    for p in problems:
        print("  -", p)
    new_cats = [c for c in cats if c not in tax.get("substitution_categories", [])]
    if new_cats:
        print("New categories:", ", ".join(new_cats))
    if dry:
        print("Dry run: nothing written.")
        return
    if not entries:
        sys.exit("No entries to write; leaving content unchanged.")
    for f in glob.glob(os.path.join(OUT, "*.json")):
        os.remove(f)
    os.makedirs(OUT, exist_ok=True)
    for slug, d in entries:
        with open(os.path.join(OUT, slug + ".json"), "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    tax["substitution_categories"] = cats
    with open(TAX, "w", encoding="utf-8") as fh:
        json.dump(tax, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"Wrote {len(entries)} files to content/substitutions/.")


if __name__ == "__main__":
    main()
