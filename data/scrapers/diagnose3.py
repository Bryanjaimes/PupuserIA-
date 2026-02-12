"""Diagnostic v3: Intercept API calls and try stealth approach."""
import asyncio
import json
from playwright.async_api import async_playwright


async def diagnose():
    pw = await async_playwright().start()
    
    # Try with stealth settings
    browser = await pw.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ]
    )
    ctx = await browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        locale="es-SV",
        java_script_enabled=True,
    )
    
    # Remove webdriver flag
    page = await ctx.new_page()
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['es-SV', 'es', 'en'] });
        window.chrome = { runtime: {} };
    """)
    
    # Capture network requests - look for API calls
    api_calls = []
    async def on_response(response):
        url = response.url
        ct = response.headers.get("content-type", "")
        if "json" in ct or "api" in url or "ajax" in url or "graphql" in url:
            try:
                body = await response.text()
                api_calls.append({
                    "url": url[:200],
                    "status": response.status,
                    "content_type": ct,
                    "body_preview": body[:500],
                })
            except:
                api_calls.append({"url": url[:200], "status": response.status, "error": "couldn't read body"})
    
    page.on("response", on_response)
    
    # Navigate
    url = "https://www.encuentra24.com/el-salvador-es/bienes-raices-venta-de-casas"
    print(f"Loading {url} with stealth settings...")
    resp = await page.goto(url, wait_until="networkidle")
    print(f"Response: {resp.status} -> {page.url}")
    await page.wait_for_timeout(5000)
    
    # Save screenshot
    await page.screenshot(path="debug_v3_stealth.png", full_page=True)
    
    print(f"\nAPI/JSON responses captured: {len(api_calls)}")
    for call in api_calls[:20]:
        print(f"\n  URL: {call['url']}")
        print(f"  Status: {call['status']}")
        if 'body_preview' in call:
            print(f"  Body: {call['body_preview'][:200]}")
    
    # -- Now try other sources --
    print("\n\n" + "=" * 60)
    print("=== Testing LaVitrina.com.sv ===")
    print("=" * 60)
    
    page2 = await ctx.new_page()
    try:
        resp2 = await page2.goto("https://www.lavitrina.com.sv/inmuebles/casas-en-venta", wait_until="networkidle", timeout=20000)
        print(f"LaVitrina status: {resp2.status}, URL: {page2.url}")
        await page2.wait_for_timeout(3000)
        
        classes = await page2.evaluate("""() => {
            const all = document.querySelectorAll('*');
            const matches = new Set();
            for (const el of all) {
                for (const cls of el.classList) {
                    const l = cls.toLowerCase();
                    if (l.includes('listing') || l.includes('card') || l.includes('result') || 
                        l.includes('property') || l.includes('item') || l.includes('product') ||
                        l.includes('anuncio'))
                        matches.add(cls);
                }
            }
            return [...matches].sort();
        }""")
        print(f"CSS classes: {classes}")
        
        links = await page2.evaluate("""() => {
            const all = document.querySelectorAll('a[href]');
            const matches = [];
            for (const a of all) {
                const href = a.href || '';
                if ((href.includes('casa') || href.includes('inmueble') || href.includes('propiedad')) 
                    && href !== window.location.href && href.length > 40) {
                    matches.push({href: href.substring(0, 150), text: a.innerText.substring(0, 80).trim()});
                }
            }
            return matches.slice(0, 10);
        }""")
        print(f"Property links: {len(links)}")
        for l in links[:5]:
            print(f"  {l['text'][:50]} -> {l['href'][:100]}")
        
        await page2.screenshot(path="debug_lavitrina.png", full_page=True)
    except Exception as e:
        print(f"LaVitrina error: {e}")
    finally:
        await page2.close()
    
    
    print("\n\n" + "=" * 60)
    print("=== Testing Corotos.com.sv ===")
    print("=" * 60)
    
    page3 = await ctx.new_page()
    try:
        resp3 = await page3.goto("https://www.corotos.com.sv/inmuebles/", wait_until="networkidle", timeout=20000)
        print(f"Corotos status: {resp3.status}, URL: {page3.url}")
        await page3.wait_for_timeout(3000)
        
        classes = await page3.evaluate("""() => {
            const all = document.querySelectorAll('*');
            const matches = new Set();
            for (const el of all) {
                for (const cls of el.classList) {
                    const l = cls.toLowerCase();
                    if (l.includes('listing') || l.includes('card') || l.includes('result') || 
                        l.includes('property') || l.includes('item') || l.includes('product') ||
                        l.includes('anuncio'))
                        matches.add(cls);
                }
            }
            return [...matches].sort();
        }""")
        print(f"CSS classes: {classes}")
    except Exception as e:
        print(f"Corotos error: {e}")
    finally:
        await page3.close()

    print("\n\n" + "=" * 60)
    print("=== Testing OLX El Salvador ===")
    print("=" * 60)
    
    page4 = await ctx.new_page()
    try:
        resp4 = await page4.goto("https://www.olx.com.sv/inmuebles/", wait_until="networkidle", timeout=20000)
        print(f"OLX status: {resp4.status}, URL: {page4.url}")
        await page4.wait_for_timeout(3000)
        await page4.screenshot(path="debug_olx.png", full_page=True)
    except Exception as e:
        print(f"OLX error: {e}")
    finally:
        await page4.close()

    print("\n\n" + "=" * 60)
    print("=== Testing Clasitag.com (SV) ===")
    print("=" * 60)
    
    page5 = await ctx.new_page()
    try:
        resp5 = await page5.goto("https://www.clasitag.com/el-salvador/inmuebles", wait_until="networkidle", timeout=20000)
        print(f"Clasitag status: {resp5.status}, URL: {page5.url}")
        await page5.wait_for_timeout(3000)
        
        links = await page5.evaluate("""() => {
            const all = document.querySelectorAll('a[href]');
            const matches = [];
            for (const a of all) {
                const href = a.href || '';
                if (href.length > 40 && a.innerText.trim().length > 5) {
                    matches.push({href: href.substring(0, 150), text: a.innerText.substring(0, 80).trim()});
                }
            }
            return matches.slice(0, 10);
        }""")
        print(f"Links: {len(links)}")
        for l in links[:5]:
            print(f"  {l['text'][:50]} -> {l['href'][:100]}")
    except Exception as e:
        print(f"Clasitag error: {e}")
    finally:
        await page5.close()

    await browser.close()
    await pw.stop()


asyncio.run(diagnose())
