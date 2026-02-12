"""Test alternative property listing sources in El Salvador."""
import asyncio
from playwright.async_api import async_playwright


async def test_source(ctx, name, url, timeout=20000):
    """Test a single source and return results."""
    print(f"\n{'=' * 60}")
    print(f"=== {name} ===")
    print(f"{'=' * 60}")
    
    page = await ctx.new_page()
    try:
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        print(f"Status: {resp.status}, Final URL: {page.url}")
        await page.wait_for_timeout(5000)
        
        # Save screenshot
        fname = name.lower().replace(" ", "_")
        await page.screenshot(path=f"debug_{fname}.png", full_page=False)
        
        # Get page title
        title = await page.title()
        print(f"Title: {title}")
        
        # Get relevant classes
        classes = await page.evaluate("""() => {
            const all = document.querySelectorAll('*');
            const matches = new Set();
            for (const el of all) {
                for (const cls of el.classList) {
                    const l = cls.toLowerCase();
                    if (l.includes('listing') || l.includes('card') || l.includes('result') || 
                        l.includes('property') || l.includes('item') || l.includes('product') ||
                        l.includes('anuncio') || l.includes('ad-') || l.includes('classified') ||
                        l.includes('tile') || l.includes('grid') || l.includes('catalog'))
                        matches.add(cls);
                }
            }
            return [...matches].sort();
        }""")
        print(f"CSS classes ({len(classes)}): {classes[:30]}")
        
        # Get all property-looking links
        links = await page.evaluate("""() => {
            const all = document.querySelectorAll('a[href]');
            const matches = [];
            const seen = new Set();
            for (const a of all) {
                const href = a.href || '';
                const text = a.innerText.trim().substring(0, 100);
                if (href.length > 30 && text.length > 5 && !seen.has(href) && 
                    !href.includes('javascript:') && !href.includes('#')) {
                    seen.add(href);
                    matches.push({href: href.substring(0, 200), text: text});
                }
            }
            return matches.slice(0, 15);
        }""")
        print(f"Links ({len(links)}):")
        for l in links[:10]:
            print(f"  {l['text'][:60]}")
            print(f"    -> {l['href'][:120]}")
        
        # Count images
        img_count = await page.evaluate("() => document.querySelectorAll('img').length")
        print(f"Images: {img_count}")
        
        # Get headings
        headings = await page.evaluate("""() => {
            const result = [];
            for (const tag of ['h1', 'h2', 'h3']) {
                document.querySelectorAll(tag).forEach(el => {
                    const t = el.innerText.trim();
                    if (t.length > 2) result.push(tag + ': ' + t.substring(0, 80));
                });
            }
            return result;
        }""")
        print(f"Headings:")
        for h in headings[:10]:
            print(f"  {h}")
            
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        await page.close()


async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
    )
    ctx = await browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        locale="es-SV",
    )
    
    sources = [
        ("LaVitrina SV", "https://www.lavitrina.com.sv/inmuebles/casas-en-venta"),
        ("Segundamano SV", "https://www.segundamano.com.sv/inmuebles/"),
        ("OLX SV", "https://www.olx.com.sv/inmuebles/"),
        ("realtor.com intl", "https://www.realtor.com/international/sv/"),
        ("Century21 SV", "https://www.century21.com.sv/propiedades/"),
        ("Properstar SV", "https://www.properstar.com/el-salvador/buy"),
        ("Lamudi SV", "https://www.lamudi.com.sv/venta/"),
        ("Point2 SV", "https://www.point2homes.com/SV/Real-Estate-Listings.html"),
        ("CompraVenta SV", "https://www.compraventasv.com/inmuebles"),
    ]
    
    working = []
    for name, url in sources:
        success = await test_source(ctx, name, url)
        if success:
            working.append(name)
    
    print(f"\n\n{'=' * 60}")
    print(f"SUMMARY: Sources that loaded: {working}")
    print(f"{'=' * 60}")
    
    await browser.close()
    await pw.stop()


asyncio.run(main())
