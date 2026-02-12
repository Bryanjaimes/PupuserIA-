"""Diagnostic v2: Handle cookie consent and check actual page state."""
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
    
    # Don't block images this time — we want to see the full page
    url = "https://www.encuentra24.com/el-salvador-es/bienes-raices-venta-de-casas"
    print(f"Loading {url}...")
    
    resp = await page.goto(url, wait_until="networkidle")
    print(f"Response status: {resp.status}")
    print(f"Response URL: {resp.url}")
    
    # Check if we were redirected
    print(f"Current URL: {page.url}")
    
    await page.wait_for_timeout(5000)
    
    # Screenshot
    await page.screenshot(path="debug_v2.png", full_page=True)
    print("Screenshot saved to debug_v2.png")
    
    # Check for cookie consent dialogs
    cookie_selectors = [
        "[class*='cookie']", "[class*='consent']", "[class*='gdpr']",
        "[class*='privacy']", "[id*='cookie']", "[id*='consent']",
        "[class*='accept']", "button[class*='accept']",
        "[class*='modal']", "[class*='dialog']", "[class*='overlay']",
        "[class*='banner']",
    ]
    print("\nChecking for overlays/dialogs:")
    for sel in cookie_selectors:
        els = await page.query_selector_all(sel)
        if els:
            for el in els:
                visible = await el.is_visible()
                tag = await el.evaluate("e => e.tagName")
                cls = await el.evaluate("e => e.className")
                text = (await el.inner_text())[:60] if visible else ""
                print(f"  {sel}: {tag}.{cls} visible={visible} text='{text}'")
    
    # Try clicking any accept/OK buttons
    accept_selectors = [
        "button:has-text('Aceptar')", "button:has-text('Accept')",
        "button:has-text('OK')", "button:has-text('Entendido')",
        "button:has-text('Continuar')", "a:has-text('Accept')",
        "[class*='accept']", ".cookie-accept",
    ]
    print("\nTrying to click accept buttons:")
    for sel in accept_selectors:
        try:
            btn = await page.query_selector(sel)
            if btn and await btn.is_visible():
                print(f"  Found and clicking: {sel}")
                await btn.click()
                await page.wait_for_timeout(2000)
                break
        except Exception as e:
            continue
    
    # Check current URL after any redirects
    print(f"\nCurrent URL after consent: {page.url}")
    
    # Get the page HTML container content
    container_html = await page.evaluate("""() => {
        const container = document.querySelector('.container.container-narrow');
        if (container) return container.innerHTML.substring(0, 3000);
        return document.body.innerHTML.substring(0, 3000);
    }""")
    print(f"\nContainer HTML ({len(container_html)} chars):")
    print(container_html[:2000])
    
    # Check for iframes that might contain content
    iframes = await page.query_selector_all("iframe")
    print(f"\nIframes on page: {len(iframes)}")
    for i, iframe in enumerate(iframes):
        src = await iframe.get_attribute("src") or "no-src"
        print(f"  iframe[{i}]: {src[:100]}")
    
    # Try a different URL format
    print("\n\n=== Trying alternative URL ===")
    url2 = "https://www.encuentra24.com/el-salvador-es/bienes-raices-casas-en-venta"
    resp2 = await page.goto(url2, wait_until="networkidle")
    print(f"URL2 status: {resp2.status}, final URL: {page.url}")
    await page.wait_for_timeout(5000)
    
    classes2 = await page.evaluate("""() => {
        const all = document.querySelectorAll('*');
        const matches = new Set();
        for (const el of all) {
            for (const cls of el.classList) {
                const l = cls.toLowerCase();
                if (l.includes('listing') || l.includes('card') || l.includes('result') || 
                    l.includes('ann') || l.includes('item') || l.includes('classified') ||
                    l.includes('property') || l.includes('lc-') || l.includes('tile') ||
                    l.includes('grid') || l.includes('search'))
                    matches.add(cls);
            }
        }
        return [...matches].sort();
    }""")
    print(f"Classes found: {classes2}")
    
    # Get all h-tags to understand page structure
    headings = await page.evaluate("""() => {
        const result = [];
        for (const tag of ['h1', 'h2', 'h3']) {
            document.querySelectorAll(tag).forEach(el => {
                result.push({tag, text: el.innerText.trim().substring(0, 80)});
            });
        }
        return result;
    }""")
    print(f"\nHeadings:")
    for h in headings:
        print(f"  <{h['tag']}> {h['text']}")
    
    await page.screenshot(path="debug_v2b.png", full_page=True)
    print("\nScreenshot 2 saved to debug_v2b.png")

    await browser.close()
    await pw.stop()


asyncio.run(diagnose())
