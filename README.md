# microbiomerecipes.com

Static site for **Microbiome Recipes**: original recipes built around fiber, fermented foods and plant variety, with one-click grocery carts. Hosted on Cloudflare.

## What's here

| Path | Page |
| --- | --- |
| `/index.html` | Landing page |
| `/learn/fiber/index.html` | Learn article: "Fiber: the strongest evidence" |
| `/recipes/overnight-oats-kefir-chia-raspberries/index.html` | Recipe page template (with schema.org Recipe markup) |
| `/assets/styles.css` | Shared styles and color tokens |
| `/assets/recipe.js` | Servings stepper on recipe pages |

These three pages come from the approved design. Other links point to the planned URLs in the site map (`/recipes/`, `/learn/`, `/fermenting/`, `/cookbook/`, legal pages and so on) and will 404 until those pages exist.

## Placeholders to fill

- Photos: every `figure.photo` is a labeled placeholder for the shot it needs.
- `[COUNT]`, `[PRICE]`, `[g]` (fiber per serving), `[DIETITIAN NAME, RD]`, `[DATE]`, storage times.
- Shop buttons: Instacart's official button (after demo approval and production keys) and the Chicory SDK (after publisher sign-up).

## Requirements

- **Accessibility:** WCAG 2.1 Level AA. Text contrast ≥ 4.5:1, keyboard access for every control, visible focus, alt text on every photo, labels on every form field, color never the only signal.
- **Recipe pages:** schema.org `Recipe` JSON-LD on every recipe (needed for Google and for Chicory). Add `image` in 16:9, 4:3 and 1:1 crops.
- **Instacart wording:** "Service fees apply.*", "Instacart may not be available in all zip codes"; no "partner", "Free Delivery" or health claims in Instacart messaging.
- **Health claims:** describe foods, not outcomes; cite a source for every gut-health note; "not medical advice" on every page.

## Deploy

Cloudflare Pages (or Workers static assets): no build step, output directory is the repository root.

`microbiomecookbook.com` and `microbiomedietcookbook.com` 301-redirect to `microbiomerecipes.com` (set in Cloudflare, not in this repo).
