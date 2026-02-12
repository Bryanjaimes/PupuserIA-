"""Diagnostic script to understand Encuentra24's DOM structure."""
import asyncio
from playwright.async_api import async_playwright


async def diagnose():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    ctx = await browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        locale="es-SV",
    )
    page = await ctx.new_page()
    url = "https://www.encuentra24.com/el-salvador-es/bienes-raices-venta-de-casas"
    print(f"Loading {url}...")
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_timeout(8000)

    # Save screenshot
    await page.screenshot(path="debug_screenshot.png", full_page=True)
    print("Screenshot saved to debug_screenshot.png")

    # Get all class names that contain relevant keywords
    classes = await page.evaluate("""() => {
        const all = document.querySelectorAll('*');
        const matches = new Set();
        for (const el of all) {
            for (const cls of el.classList) {
                const l = cls.toLowerCase();
                if (l.includes('listing') || l.includes('card') || l.includes('result') || 
                    l.includes('ann') || l.includes('item') || l.includes('ad-') ||
                    l.includes('property') || l.includes('lc-') || l.includes('classified'))
                    matches.add(cls);
            }
        }
        return [...matches].sort();
    }""")
    print(f"\nRelevant CSS classes ({len(classes)}):")
    for c in classes[:50]:
        print(f"  .{c}")

    # Count links to detail pages
    links = await page.evaluate("""() => {
        const all = document.querySelectorAll('a[href]');
        const matches = [];
        for (const a of all) {
            const href = a.href || '';
            if (href.includes('bienes-raices') && /\\d{5,}/.test(href)) {
                matches.push({href: href, text: a.innerText.substring(0, 100).trim()});
            }
        }
        return matches;
    }""")
    print(f"\nDetail page links: {len(links)}")
    for l in links[:10]:
        print(f"  {l['text'][:60]} -> {l['href']}")

    # Try to find any embedded data
    data_check = await page.evaluate("""() => {
        const checks = {};
        checks.has__NEXT_DATA__ = !!window.__NEXT_DATA__;
        checks.has__data = !!window.__data;
        checks.has__INITIAL_STATE__ = !!window.__INITIAL_STATE__;
        checks.hasSearchResults = !!window.searchResults;
        checks.hasPageData = !!window.pageData;
        
        const jsonLd = document.querySelectorAll('script[type="application/ld+json"]');
        checks.jsonLdScripts = jsonLd.length;
        if (jsonLd.length > 0) {
            try { checks.jsonLdSample = jsonLd[0].textContent.substring(0, 200); } catch(e) {}
        }
        
        checks.title = document.title;
        checks.h1Count = document.querySelectorAll('h1').length;
        checks.h2Count = document.querySelectorAll('h2').length;
        checks.imgCount = document.querySelectorAll('img').length;
        checks.anchorCount = document.querySelectorAll('a').length;
        
        return checks;
    }""")
    print(f"\nPage diagnostics:")
    for k, v in data_check.items():
        print(f"  {k}: {v}")

    # Get body structure
    structure = await page.evaluate("""() => {
        const body = document.body;
        const result = [];
        for (const child of body.children) {
            const tag = child.tagName.toLowerCase();
            const cls = child.className ? '.' + child.className.toString().split(' ').slice(0, 3).join('.') : '';
            const id_attr = child.id ? '#' + child.id : '';
            const childCount = child.children.length;
            result.push(tag + id_attr + cls + ' (' + childCount + ' children)');
        }
        return result;
    }""")
    print(f"\nBody structure:")
    for s in structure[:20]:
        print(f"  {s}")

    # Get the main content area inner HTML (truncated)
    main_html = await page.evaluate("""() => {
        // Try to find the main content container
        const main = document.querySelector('main') || 
                     document.querySelector('#content') ||
                     document.querySelector('[class*="content"]') ||
                     document.querySelector('[class*="main"]');
        if (main) {
            return {selector: main.tagName + '.' + (main.className || ''), html: main.innerHTML.substring(0, 3000)};
        }
        // Fallback: get body inner HTML
        return {selector: 'body', html: document.body.innerHTML.substring(0, 3000)};
    }""")
    print(f"\nMain content ({main_html['selector']}):")
    print(main_html["html"][:2000])

    await browser.close()
    await pw.stop()


asyncio.run(diagnose())
