#!/usr/bin/env python3
"""Automated QA for index.html across all required viewport widths."""
import asyncio, json, os
from playwright.async_api import async_playwright

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html')
WIDTHS = [1440, 1280, 1024, 834, 768, 430, 414, 390, 375]
HEIGHT = 900

JS_CHECKS = """
() => {
  const issues = [];
  const vw = document.documentElement.clientWidth;
  // 1. horizontal overflow
  if (document.documentElement.scrollWidth > vw + 1) {
    issues.push('PAGE overflow: scrollWidth=' + document.documentElement.scrollWidth + ' > vw=' + vw);
    // find offenders
    document.querySelectorAll('*').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.right > vw + 6 && r.width > 40 && getComputedStyle(el).position !== 'fixed') {
        const id = el.id ? '#'+el.id : '';
        const cls = typeof el.className === 'string' && el.className ? '.'+el.className.trim().split(/\\s+/).slice(0,2).join('.') : '';
        issues.push('  offender: <' + el.tagName.toLowerCase() + id + cls + '> right=' + Math.round(r.right));
      }
    });
  }
  // 2. broken images
  document.querySelectorAll('img').forEach(img => {
    if (!img.complete || img.naturalWidth === 0) issues.push('BROKEN IMG: ' + (img.alt || 'no-alt').slice(0, 50));
  });
  // 3. font applied
  const h1 = document.querySelector('h1');
  const h1Font = h1 ? getComputedStyle(h1).fontFamily : '';
  if (!/Cormorant/i.test(h1Font)) issues.push('FONT not applied on h1: ' + h1Font);
  // 4. wa button in viewport bottom-right
  const wa = document.querySelector('.wa-float');
  if (wa) {
    const r = wa.getBoundingClientRect();
    if (r.width < 40 || r.height < 40) issues.push('WA button too small: ' + r.width + 'x' + r.height);
  } else issues.push('WA button missing');
  // 5. tap targets on mobile
  const vwSmall = vw < 480;
  if (vwSmall) {
    document.querySelectorAll('a.btn, button.tab, .nav-toggle').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.height > 0 && r.height < 38) issues.push('TAP TARGET small (<38px): ' + (el.textContent||'').trim().slice(0,24) + ' h=' + Math.round(r.height));
    });
  }
  // 6. tiny text
  document.querySelectorAll('p, li, td, a').forEach(el => {
    if (!el.children.length || el.tagName === 'TD') {
      const fs = parseFloat(getComputedStyle(el).fontSize);
      const txt = (el.textContent || '').trim();
      if (fs < 11.5 && txt.length > 12) issues.push('TINY TEXT ' + fs + 'px: ' + txt.slice(0, 40));
    }
  });
  return issues;
}
"""

async def main():
    results = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for w in WIDTHS:
            page = await browser.new_page(viewport={'width': w, 'height': HEIGHT})
            errors = []
            page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
            page.on('pageerror', lambda e: errors.append(str(e)))
            await page.goto('file://' + PATH)
            await page.wait_for_timeout(700)
            # force reveal all for measurement
            await page.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('is-in'))")
            await page.wait_for_timeout(200)
            issues = await page.evaluate(JS_CHECKS)
            # header height
            hdr = await page.evaluate("document.querySelector('.header-inner').getBoundingClientRect().height")
            # hero title size
            h1size = await page.evaluate("getComputedStyle(document.querySelector('h1')).fontSize")
            results[w] = {'issues': issues, 'console_errors': errors, 'header_h': round(hdr), 'h1_px': h1size}
            await page.close()

        # ---- interaction tests at 390px ----
        page = await browser.new_page(viewport={'width': 390, 'height': 844})
        await page.goto('file://' + PATH)
        await page.wait_for_timeout(500)
        inter = {}
        # drawer
        await page.click('#navToggle')
        await page.wait_for_timeout(500)
        inter['drawer_opens'] = await page.evaluate("document.getElementById('drawer').classList.contains('is-open')")
        inter['drawer_link_visible'] = await page.evaluate("!!Array.from(document.querySelectorAll('#drawer nav a')).find(a => a.offsetParent !== null)")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(400)
        inter['drawer_esc_closes'] = await page.evaluate("!document.getElementById('drawer').classList.contains('is-open')")
        # tabs
        await page.click('#tab-chinese')
        await page.wait_for_timeout(300)
        inter['tab_switch'] = await page.evaluate("document.getElementById('panel-chinese').classList.contains('is-active') && !document.getElementById('panel-starters').classList.contains('is-active')")
        # lightbox
        await page.click('[data-lb="g1"]')
        await page.wait_for_timeout(400)
        inter['lightbox_opens'] = await page.evaluate("document.getElementById('lightbox').classList.contains('is-open')")
        inter['lightbox_img'] = await page.evaluate("document.getElementById('lbImg').naturalWidth > 0")
        await page.keyboard.press('ArrowRight')
        await page.wait_for_timeout(150)
        inter['lightbox_nav'] = await page.evaluate("document.getElementById('lbCount').textContent")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(300)
        inter['lightbox_esc'] = await page.evaluate("!document.getElementById('lightbox').classList.contains('is-open')")
        # open-now badge computed
        inter['live_badge'] = await page.evaluate("document.getElementById('liveText').textContent")
        # anchor scroll (use footer link — visible on all sizes)
        await page.click('.footer-links a[href="#menu"]')
        await page.wait_for_timeout(3000)
        inter['anchor_scroll'] = await page.evaluate("Math.abs(document.getElementById('menu').getBoundingClientRect().top) < 120")
        # map iframe presence
        inter['map_iframe'] = await page.evaluate("!!document.querySelector('.map-card iframe')")
        results['interactions@390'] = inter

        # desktop interaction check at 1280
        page2 = await browser.new_page(viewport={'width': 1280, 'height': 900})
        await page2.goto('file://' + PATH)
        await page2.wait_for_timeout(500)
        d = {}
        d['nav_visible'] = await page2.evaluate("document.querySelector('.primary-nav').offsetParent !== null")
        d['header_solid_after_scroll'] = await page2.evaluate("""async () => {
            window.scrollTo(0, 400); await new Promise(r => setTimeout(r, 400));
            return document.getElementById('siteHeader').classList.contains('is-solid');
        }""")
        d['h1_width_ok'] = await page2.evaluate("document.querySelector('h1').getBoundingClientRect().width < 700")
        results['desktop@1280'] = d
        await browser.close()

    print(json.dumps(results, indent=1, ensure_ascii=False))
    total_issues = sum(len(r['issues']) for r in results.values() if isinstance(r, dict) and 'issues' in r)
    print(f"\n=== TOTAL LAYOUT ISSUES: {total_issues} ===")

asyncio.run(main())
