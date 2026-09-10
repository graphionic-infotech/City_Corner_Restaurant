# City Corner Restaurant — Website

A premium, single-file website for **City Corner Restaurant**, pure-veg restaurant
at Parikrama Appartment, opposite Lunsikui Ground, Lunsikui Ring Road, Navsari 396445, Gujarat.

Design direction: luxury fine-dining language (deep emerald + antique gold, Cormorant
Garamond serif with Jost, arched image frames) adapted to a beloved local casual eatery.

---

## Files

| Path | What it is |
|---|---|
| `index.html` | **Option A — single-file website.** Fully self-contained (fonts & images embedded). Works anywhere, zero setup. |
| `mobile-fast/` | **Option B — fast hosting build.** ~100 KB HTML + optimised assets with lazy loading. Initial page weight ~0.4 MB instead of ~2.8 MB — best for real hosting & mobile data. |
| `og-cover.jpg` | Social-share cover image (for Open Graph). Upload next to `index.html`. |
| `img/` | Optimised real business photos (same images as embedded in `index.html`). |
| `fonts/` | Self-hosted web fonts (Cormorant Garamond 500/600/500i, Jost 400/500/600). |
| `src/` | Maintainable source: 4 HTML template parts + `build.py` + `qa_test.py`. |
| `raw-photos/` | Original downloaded source photos. |

## Hosting — pick ONE of the two options

**Option A (simplest):** upload `index.html` + `og-cover.jpg` to any host.
One file does everything.

**Option B (fastest on mobile — recommended):** upload the whole `mobile-fast/` folder
(`index.html`, `og-cover.jpg` and the `assets/` directory, keeping the structure).
The page loads ~7× lighter on phones because images below the screen lazy-load on demand.

## Editing & rebuilding

Edit the files in `src/` (CSS lives in `src/part1-head.html`, content in parts 2–4),
then run:

```bash
python3 src/build.py     # → regenerates index.html
python3 src/qa_test.py   # optional: automated responsive QA (needs playwright + chromium)
```

Placeholders like `{{IMG_HERO}}` are replaced with base64 data URIs at build time.

## Hosting

Upload `index.html` (and `og-cover.jpg`) to any static host — Netlify, Vercel,
cPanel/shared hosting, GitHub Pages. No build step, no dependencies, no database.

After hosting, update two things in `src/part1-head.html` and rebuild:
1. `<link rel="canonical">` → your real domain
2. `og:image` → the absolute URL of `og-cover.jpg` on your domain
   (social scrapers need a full URL, e.g. `https://yourdomain/og-cover.jpg`)

## After publishing (recommended)

- Add the website URL to the Google Business Profile ("Add website" is currently empty) —
  it significantly helps local SEO.
- Verify the Restaurant structured data at search.google.com/test/rich-results

## Verified data sources (nothing invented)

Every fact, price, review and photo on the site is real, drawn from public listings:

- **Google Business Profile** — name, category (sandwich shop / veg, Punjabi & Indian casual
  eatery), address, phone +91 99980 61609, hours (daily 11 AM–10 PM), 3.8★/472 reviews,
  ₹200–400 per person, WhatsApp-enabled number.
- **Justdial listing** (verified badge) — 26 years in business, pure veg, ₹410 for two,
  full address (1st Floor, Parikrama Appartment), full menu with prices (148 dishes),
  Zomato order link, catalogue photos & logo.
- **Zomato** — 3.9★ from 6,253 ratings; cuisines: sandwich, pizza, soups & salads, continental.
- **Restaurant Guru** — outdoor seating, delivery, takeaway, booking, cards accepted;
  coordinates 20.9471296, 72.9363381; photo catalogue & menu-card scans.
- **Google reviews** — quoted verbatim: Konrad Brus, Hardik Prajapati, Darshan Shakya,
  Vaishali Jadhav, Parth Rana, Jimmy Patel, Anjali Shah (Gujarati quote).
- **Instagram** — @citycorner.restaurant ("book your tables at…").

Menu prices are from the Justdial menu page (updated 2026, user-contributed) and are
labelled as such on the site. The sandwich & pizza card is intentionally shown without
prices because no verified price list for it exists online.

## Design notes

- Palette: `#0c2016` emerald base · `#c8a45d` antique gold · `#f4efe2` cream — all text
  pairs pass WCAG AA (most exceed 7:1).
- Typography: Cormorant Garamond (display) + Jost (body/UI), embedded latin subsets (~176 KB).
- Interactions: sticky header, mobile drawer, menu tabs, lightbox (gallery + menu cards,
  keyboard navigable), live open/closed badge computed in IST, reveal-on-scroll respecting
  `prefers-reduced-motion`, floating WhatsApp button.
- Tested at 1440 / 1280 / 1024 / 834 / 768 / 430 / 414 / 390 / 375 px — zero overflow,
  zero console errors, all tap targets ≥ 40 px on mobile.
