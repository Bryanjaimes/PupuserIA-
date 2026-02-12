"""Final diagnostic: detailed card extraction from realtor.com."""
import asyncio
from playwright.async_api import async_playwright


async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    ctx = await browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    )
    page = await ctx.new_page()
    
    url = "https://www.realtor.com/international/sv/"
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_timeout(6000)
    
    # Get ALL cards with their complete ancestor chain to find the <a> wrap
    data = await page.evaluate("""() => {
        const results = [];
        
        // Get all links that go to /international/sv/ listing pages
        const allLinks = document.querySelectorAll('a[href*="/international/sv/"]');
        for (const link of allLinks) {
            const href = link.href;
            // Filter: must have long URL (listing detail pages)
            if (href.length < 60) continue;
            
            // Get the card container (walk up to find listing card class)
            let container = link;
            while (container && !container.className?.includes?.('listing-card')) {
                container = container.parentElement;
            }
            
            // Get all text within this link/card
            const fullText = (container || link).innerText.trim();
            
            // Get images
            const imgs = (container || link).querySelectorAll('img[src]');
            const images = Array.from(imgs)
                .map(i => i.src)
                .filter(s => s && !s.startsWith('data:'));
            
            // Get alt text (contains URL slug)
            const imgAlts = Array.from(imgs).map(i => i.alt).filter(Boolean);
            
            // Get price
            const priceEl = (container || link).querySelector('.displayListingPrice');
            const price = priceEl?.innerText?.trim() || '';
            
            // Get features
            const featureEls = (container || link).querySelectorAll('.feature-item');
            const features = Array.from(featureEls).map(f => f.innerText.trim());
            
            // Get the listing tag (LATEST, etc.)
            const tagEl = (container || link).querySelector('.standard-listing-card-new-tag');
            const tag = tagEl?.innerText?.trim() || '';
            
            results.push({
                href: href.substring(0, 250),
                fullText: fullText.substring(0, 500),
                price,
                images,
                imgAlts,
                features,
                tag,
                containerClass: container?.className?.substring(0, 100) || 'none',
            });
        }
        
        return results;
    }""")
    
    print(f"Found {len(data)} listing links")
    
    for i, item in enumerate(data[:8]):
        print(f"\n{'=' * 60}")
        print(f"[{i}] URL: {item['href']}")
        print(f"    Price: {item['price']}")
        print(f"    Images: {len(item['images'])} - {item['images'][:2]}")
        print(f"    Features: {item['features']}")
        print(f"    Tag: {item['tag']}")
        print(f"    Container: {item['containerClass']}")
        print(f"    Text: {item['fullText'][:200]}")
    
    # Now test detail page
    if data:
        detail_url = data[0]['href']
        print(f"\n\n{'=' * 60}")
        print(f"DETAIL PAGE: {detail_url}")
        print(f"{'=' * 60}")
        
        await page.goto(detail_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        
        detail = await page.evaluate("""() => {
            const r = {};
            
            // Title - try various
            r.title = document.querySelector('h1')?.innerText?.trim() || '';
            
            // Price
            r.price = document.querySelector('.displayListingPrice')?.innerText?.trim() || '';
            if (!r.price) {
                const allPrices = document.querySelectorAll('[class*="price"], [class*="Price"]');
                for (const p of allPrices) {
                    const t = p.innerText.trim();
                    if (t.match(/USD|\\$|\\d{3}/)) { r.price = t; break; }
                }
            }
            
            // Description
            const allPs = document.querySelectorAll('p');
            for (const p of allPs) {
                const t = p.innerText.trim();
                if (t.length > 100) {
                    r.description = t.substring(0, 1000);
                    break;
                }
            }
            
            // All images
            r.images = Array.from(document.querySelectorAll('img[src*="rea.global"]'))
                .map(i => ('https:' + i.src).replace('https:https:', 'https:'))
                .slice(0, 20);
            
            // Property details/features
            r.features = Array.from(document.querySelectorAll('.feature-item'))
                .map(f => f.innerText.trim());
            
            // Location from breadcrumbs or title
            r.breadcrumbs = Array.from(document.querySelectorAll('[class*="breadcrumb"] a, nav a'))
                .map(a => a.innerText.trim())
                .filter(t => t.length > 0);
            
            // Agent info
            const agentName = document.querySelector('[class*="agent-name"], [class*="AgentName"]');
            r.agent = agentName?.innerText?.trim() || '';
            
            // Property type from features
            r.propertyType = '';
            for (const f of r.features) {
                if (f.match(/House|Apartment|Land|Commercial|Condo|Villa|Industrial/i)) {
                    r.propertyType = f;
                }
            }
            
            // Get structured data from classes
            const allClasses = new Set();
            document.querySelectorAll('*').forEach(el => {
                for (const c of el.classList) {
                    const l = c.toLowerCase();
                    if (l.includes('detail') || l.includes('feature') || l.includes('listing') || 
                        l.includes('property') || l.includes('spec') || l.includes('info') ||
                        l.includes('agent') || l.includes('gallery') || l.includes('image') ||
                        l.includes('photo') || l.includes('bed') || l.includes('bath') ||
                        l.includes('area') || l.includes('size') || l.includes('location'))
                        allClasses.add(c);
                }
            });
            r.relevantClasses = [...allClasses].sort().slice(0, 30);
            
            // Get key sections content
            r.bodySnippet = document.body.innerText.substring(0, 3000);
            
            return r;
        }""")
        
        print(f"Title: {detail.get('title')}")
        print(f"Price: {detail.get('price')}")
        print(f"Description: {detail.get('description', '')[:200]}")
        print(f"Images: {detail.get('images', [])[:5]}")
        print(f"Features: {detail.get('features')}")
        print(f"Breadcrumbs: {detail.get('breadcrumbs')}")
        print(f"Agent: {detail.get('agent')}")
        print(f"PropertyType: {detail.get('propertyType')}")
        print(f"Relevant classes: {detail.get('relevantClasses')}")
        print(f"\nBody text (first 1000 chars):\n{detail.get('bodySnippet', '')[:1000]}")

    await browser.close()
    await pw.stop()


asyncio.run(main())
