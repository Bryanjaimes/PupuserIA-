"""Deep diagnostic on realtor.com/international/sv to map DOM structure."""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    ctx = await browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    )
    page = await ctx.new_page()
    
    url = "https://www.realtor.com/international/sv/"
    print(f"Loading {url}")
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_timeout(6000)
    
    # Get the listing card HTML structure
    card_html = await page.evaluate("""() => {
        // Try different selectors
        const selectors = [
            '.standard-listing-card-non-desktop',
            '.boost-listing-card-non-desktop',
            '[class*="listing-card"]',
            '[class*="listing"]',
        ];
        for (const sel of selectors) {
            const cards = document.querySelectorAll(sel);
            if (cards.length > 0) {
                return {
                    selector: sel,
                    count: cards.length,
                    html: cards[0].outerHTML.substring(0, 3000),
                    secondHtml: cards.length > 1 ? cards[1].outerHTML.substring(0, 3000) : '',
                };
            }
        }
        return null;
    }""")
    
    if card_html:
        print(f"\nFound {card_html['count']} cards with selector: {card_html['selector']}")
        print(f"\nCard 1 HTML:\n{card_html['html']}")
        print(f"\nCard 2 HTML:\n{card_html['secondHtml']}")
    else:
        print("No listing cards found!")
    
    # Check pagination
    pagination = await page.evaluate("""() => {
        const items = document.querySelectorAll('.ant-pagination-item');
        return {
            count: items.length,
            pages: Array.from(items).map(el => ({
                text: el.innerText.trim(),
                href: el.querySelector('a')?.href || '',
                active: el.classList.contains('ant-pagination-item-active'),
            })),
        };
    }""")
    print(f"\nPagination: {pagination['count']} pages")
    for p in pagination['pages']:
        print(f"  Page {p['text']}: {p['href'][:80]} {'[ACTIVE]' if p['active'] else ''}")
    
    # Extract all property data from visible cards
    properties = await page.evaluate("""() => {
        const cards = document.querySelectorAll('.standard-listing-card-non-desktop, .boost-listing-card-non-desktop');
        return Array.from(cards).map(card => {
            const link = card.querySelector('a[href*="/international/sv/"]');
            const priceEl = card.querySelector('.displayListingPrice') || card.querySelector('[class*="price"]');
            const imgs = card.querySelectorAll('img[src]');
            const features = card.querySelectorAll('.feature-item');
            
            return {
                href: link?.href || '',
                title: link?.innerText?.trim()?.substring(0, 200) || '',
                price: priceEl?.innerText?.trim() || '',
                images: Array.from(imgs).map(img => img.src).filter(s => s && !s.startsWith('data:')),
                features: Array.from(features).map(f => f.innerText.trim()),
                fullText: card.innerText.trim().substring(0, 300),
            };
        });
    }""")
    
    print(f"\nExtracted {len(properties)} properties:")
    for i, p in enumerate(properties[:5]):
        print(f"\n  [{i}] {p.get('title', 'NO TITLE')[:80]}")
        print(f"      Price: {p.get('price', 'N/A')}")
        print(f"      URL: {p.get('href', 'N/A')[:100]}")
        print(f"      Images: {len(p.get('images', []))}")
        print(f"      Features: {p.get('features', [])}")
        print(f"      Text: {p.get('fullText', '')[:150]}")
    
    # Check for total results count
    total = await page.evaluate("""() => {
        const header = document.querySelector('.search-result-head') || 
                       document.querySelector('[class*="result-count"]') ||
                       document.querySelector('h1');
        return header?.innerText?.trim() || 'not found';
    }""")
    print(f"\nResults header: {total}")
    
    # Try page 2
    print(f"\n\n=== Testing Page 2 ===")
    await page.goto("https://www.realtor.com/international/sv/?page=2", wait_until="domcontentloaded")
    await page.wait_for_timeout(5000)
    
    p2_count = await page.evaluate("""() => {
        return document.querySelectorAll('.standard-listing-card-non-desktop, .boost-listing-card-non-desktop').length;
    }""")
    print(f"Page 2 cards: {p2_count}")
    
    p2_data = await page.evaluate("""() => {
        const cards = document.querySelectorAll('.standard-listing-card-non-desktop, .boost-listing-card-non-desktop');
        return Array.from(cards).slice(0, 3).map(card => {
            const link = card.querySelector('a[href*="/international/sv/"]');
            const priceEl = card.querySelector('.displayListingPrice') || card.querySelector('[class*="price"]');
            return {
                href: link?.href?.substring(0, 150) || '',
                price: priceEl?.innerText?.trim() || '',
            };
        });
    }""")
    for p in p2_data:
        print(f"  {p['price']} -> {p['href'][:80]}")
    
    # Now test a detail page
    if properties and properties[0].get("href"):
        detail_url = properties[0]["href"]
        print(f"\n\n=== Testing Detail Page ===")
        print(f"URL: {detail_url}")
        
        await page.goto(detail_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        
        detail = await page.evaluate("""() => {
            const result = {};
            
            // Title
            const h1 = document.querySelector('h1');
            result.title = h1?.innerText?.trim() || '';
            
            // Price
            const price = document.querySelector('.displayListingPrice') || document.querySelector('[class*="price"]');
            result.price = price?.innerText?.trim() || '';
            
            // Description
            const desc = document.querySelector('[class*="description"]') || document.querySelector('[class*="Description"]');
            result.description = desc?.innerText?.trim()?.substring(0, 500) || '';
            
            // Images
            const imgs = document.querySelectorAll('img[src]');
            result.images = Array.from(imgs)
                .map(img => img.src)
                .filter(s => s && !s.startsWith('data:') && s.includes('http'))
                .slice(0, 10);
            
            // Features/details
            const features = document.querySelectorAll('.feature-item, [class*="detail"] li, [class*="feature"]');
            result.features = Array.from(features).map(f => f.innerText.trim()).filter(t => t.length > 0);
            
            // Location breadcrumbs
            const breadcrumbs = document.querySelectorAll('[class*="breadcrumb"] a, [class*="Breadcrumb"] a');
            result.breadcrumbs = Array.from(breadcrumbs).map(a => a.innerText.trim());
            
            // All text for debugging
            result.bodyText = document.body.innerText.substring(0, 2000);
            
            // All classes containing 'detail', 'feature', 'info'
            const allEls = document.querySelectorAll('*');
            const cls = new Set();
            for (const el of allEls) {
                for (const c of el.classList) {
                    const l = c.toLowerCase();
                    if (l.includes('detail') || l.includes('feature') || l.includes('info') || 
                        l.includes('spec') || l.includes('attribute') || l.includes('meta'))
                        cls.add(c);
                }
            }
            result.detailClasses = [...cls].sort();
            
            return result;
        }""")
        
        print(f"Title: {detail.get('title')}")
        print(f"Price: {detail.get('price')}")
        print(f"Description: {detail.get('description', '')[:200]}")
        print(f"Images: {len(detail.get('images', []))}")
        for img in detail.get('images', [])[:5]:
            print(f"  {img[:100]}")
        print(f"Features: {detail.get('features', [])[:10]}")
        print(f"Breadcrumbs: {detail.get('breadcrumbs')}")
        print(f"Detail classes: {detail.get('detailClasses', [])[:20]}")

    await browser.close()
    await pw.stop()


asyncio.run(main())
